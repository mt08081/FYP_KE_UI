"""
K-Electric Fault Prediction API Server
======================================
Predictive maintenance system using ML models for fault type and restoration time prediction.

Run: python server.py
API Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional
import joblib
import pandas as pd
import numpy as np
import math
import datetime
import os
import warnings

warnings.filterwarnings('ignore')

# ============================================
# APP SETUP
# ============================================
app = FastAPI(
    title="K-Electric Predictive Maintenance API",
    description="Fault prediction and restoration time estimation for KE grid stations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# ============================================
# PATHS (Clean structure)
# ============================================
BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")

# ============================================
# CONFIGURATION
# ============================================
PLANT_CONFIG = {
    'PLANT_01': {
        'name': 'Korangi Grid Station',
        'area': 'Korangi',
        'risk_penalty': 0.21,
        'risk_label': 'Extreme',
        'lat': 24.831,
        'lng': 67.132,
        'color': '#dc3545'
    },
    'PLANT_02': {
        'name': 'Surjani Substation',
        'area': 'Surjani',
        'risk_penalty': 0.1585,
        'risk_label': 'High',
        'lat': 25.002,
        'lng': 67.062,
        'color': '#fd7e14'
    },
    'PLANT_03': {
        'name': 'Nazimabad Substation',
        'area': 'Nazimabad',
        'risk_penalty': 0.0349,
        'risk_label': 'Medium',
        'lat': 24.912,
        'lng': 67.042,
        'color': '#ffc107'
    },
    'MAINT_01': {
        'name': 'Clifton Maintenance Hub',
        'area': 'Clifton',
        'risk_penalty': -0.1087,
        'risk_label': 'Secure',
        'lat': 24.815,
        'lng': 67.028,
        'color': '#28a745'
    }
}

STATUS_DISPLAY = {
    'IN_PROGRESS': {'label': 'In Progress', 'color': 'warning', 'icon': 'hourglass-split'},
    'COMPLETED': {'label': 'Completed', 'color': 'success', 'icon': 'check-circle-fill'},
    'ON_HOLD': {'label': 'On Hold', 'color': 'secondary', 'icon': 'pause-circle-fill'},
    'NEW': {'label': 'New', 'color': 'info', 'icon': 'plus-circle-fill'}
}

FAULT_ICONS = {
    'Motor Failure': 'gear-fill',
    'Short Circuit': 'lightning-charge-fill',
    'Leak': 'droplet-fill',
    'Sensor Fault': 'cpu-fill'
}

AVG_TEMP = 32.5
AVG_WIND = 15.0

# ============================================
# GLOBAL STATE
# ============================================
clf_fault = None
reg_time = None
le_plant = None
le_fault = None
synthetic_df = None
centers_df = None


# ============================================
# STARTUP
# ============================================
def load_models():
    global clf_fault, reg_time, le_plant, le_fault
    
    try:
        clf_fault = joblib.load(os.path.join(MODEL_DIR, 'fault_classifier.pkl'))
        print("✅ Loaded: fault_classifier.pkl")
    except Exception as e:
        print(f"⚠️ Could not load fault classifier: {e}")
    
    try:
        reg_time = joblib.load(os.path.join(MODEL_DIR, 'restoration_model.pkl'))
        print("✅ Loaded: restoration_model.pkl")
    except Exception as e:
        print(f"⚠️ Could not load restoration model: {e}")
    
    try:
        le_plant = joblib.load(os.path.join(MODEL_DIR, 'plant_encoder.pkl'))
        print("✅ Loaded: plant_encoder.pkl")
    except Exception as e:
        print(f"⚠️ Could not load plant encoder: {e}")
    
    try:
        le_fault = joblib.load(os.path.join(MODEL_DIR, 'fault_encoder.pkl'))
        print("✅ Loaded: fault_encoder.pkl")
    except Exception as e:
        print(f"⚠️ Could not load fault encoder: {e}")


def load_data():
    global synthetic_df, centers_df
    
    try:
        synthetic_df = pd.read_csv(os.path.join(DATA_DIR, 'synthetic_faults.csv'))
        synthetic_df['duration_hours'] = pd.to_numeric(synthetic_df['malfunction_end'], errors='coerce').fillna(0)
        synthetic_df['kunda_risk_factor'] = synthetic_df['kunda_risk_factor'].replace('Very Secure', 'Secure')
        print(f"✅ Loaded: {len(synthetic_df)} fault records")
    except Exception as e:
        print(f"⚠️ Could not load fault data: {e}")
    
    try:
        centers_df = pd.read_csv(os.path.join(DATA_DIR, 'service_centers.csv'))
        print(f"✅ Loaded: {len(centers_df)} service centers")
    except Exception as e:
        print(f"⚠️ Could not load centers data: {e}")


@app.on_event("startup")
async def startup():
    print("\n" + "=" * 50)
    print("🚀 K-Electric Predictive Maintenance API")
    print("=" * 50)
    load_models()
    load_data()
    print("=" * 50)
    print("📍 Dashboard: http://localhost:8000/static/index.html")
    print("📚 API Docs:  http://localhost:8000/docs")
    print("=" * 50 + "\n")


# ============================================
# HELPERS
# ============================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def get_traffic_factor():
    hour = datetime.datetime.now().hour
    if 7 <= hour < 10: return 1.5
    elif 16 <= hour < 20: return 1.6
    elif 10 <= hour < 16: return 1.2
    return 1.0


def find_nearest_center(lat, lng):
    if centers_df is None or centers_df.empty:
        return {'name': 'Unknown Center', 'distance_km': 5, 'travel_time_min': 15}
    
    best, best_dist = None, float('inf')
    for _, c in centers_df.iterrows():
        d = haversine(lat, lng, c['Latitude'], c['Longitude'])
        if d < best_dist:
            best_dist, best = d, c
    
    travel_min = (best_dist / 30) * 60 * get_traffic_factor()
    return {'name': best['Center Name'], 'distance_km': round(best_dist, 2), 'travel_time_min': round(travel_min)}


def predict_fault_for_plant(plant_id: str, temp: float = None, wind: float = None):
    if clf_fault is None or le_plant is None or le_fault is None:
        return "Unknown"
    if plant_id not in PLANT_CONFIG:
        return "Unknown"
    
    plant_info = PLANT_CONFIG[plant_id]
    now = datetime.datetime.now()
    temp = temp if temp is not None else AVG_TEMP
    wind = wind if wind is not None else AVG_WIND
    
    try:
        plant_code = le_plant.transform([plant_id])[0]
        X = [[plant_code, now.month, temp, wind, plant_info['risk_penalty']]]
        pred_code = clf_fault.predict(X)[0]
        return le_fault.inverse_transform([pred_code])[0]
    except Exception as e:
        print(f"Fault prediction error: {e}")
        return "Unknown"


def predict_restoration_time(plant_id: str, fault_type: str, temp: float = None, wind: float = None):
    if reg_time is None or le_plant is None or le_fault is None:
        return 4.0
    if plant_id not in PLANT_CONFIG:
        return 4.0
    
    plant_info = PLANT_CONFIG[plant_id]
    now = datetime.datetime.now()
    temp = temp if temp is not None else AVG_TEMP
    wind = wind if wind is not None else AVG_WIND
    
    try:
        plant_code = le_plant.transform([plant_id])[0]
        fault_code = le_fault.transform([fault_type])[0]
        risk = plant_info['risk_penalty']
        interaction = wind * risk
        X = [[plant_code, fault_code, now.hour, temp, wind, risk, interaction]]
        hours = reg_time.predict(X)[0]
        return round(max(1, min(48, hours)), 1)
    except Exception as e:
        print(f"Time prediction error: {e}")
        return 4.0


def format_duration(hours):
    if hours <= 0 or pd.isna(hours):
        return "N/A"
    h = int(hours)
    m = int((hours - h) * 60)
    if h > 0 and m > 0: return f"{h}h {m}m"
    elif h > 0: return f"{h}h"
    return f"{m}m"


# ============================================
# API ENDPOINTS
# ============================================
@app.get("/", tags=["Info"])
async def root():
    return {
        "name": "K-Electric Predictive Maintenance API",
        "version": "1.0.0",
        "dashboard": "/static/index.html",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "models_loaded": {"fault_classifier": clf_fault is not None, "restoration_model": reg_time is not None},
        "data_loaded": {"fault_records": len(synthetic_df) if synthetic_df is not None else 0}
    }


@app.get("/plants", tags=["Data"])
async def get_plants():
    plants = []
    for plant_id, info in PLANT_CONFIG.items():
        fault_count = len(synthetic_df[synthetic_df['main_work_center'] == plant_id]) if synthetic_df is not None else 0
        plants.append({
            'id': plant_id,
            'name': info['name'],
            'area': info['area'],
            'risk_level': info['risk_label'],
            'coordinates': {'lat': info['lat'], 'lng': info['lng']},
            'color': info['color'],
            'total_faults': fault_count
        })
    return plants


@app.get("/dashboard", tags=["Dashboard"])
async def get_dashboard():
    if synthetic_df is None:
        raise HTTPException(500, "Data not loaded")
    
    total = len(synthetic_df)
    by_status = synthetic_df['user_status'].value_counts().to_dict()
    by_area = synthetic_df['area_name'].value_counts().to_dict()
    by_fault = synthetic_df['problem_code_text'].value_counts().to_dict()
    
    status_summary = []
    for status, count in by_status.items():
        display = STATUS_DISPLAY.get(status, {'label': status, 'color': 'secondary', 'icon': 'circle'})
        status_summary.append({'status': status, 'label': display['label'], 'count': count, 'color': display['color'], 'icon': display['icon']})
    
    recent = []
    for _, row in synthetic_df.head(25).iterrows():
        plant_id = row['main_work_center']
        plant_info = PLANT_CONFIG.get(plant_id, {})
        duration = row.get('duration_hours', 0)
        recent.append({
            'id': str(row['notification']),
            'plant_id': plant_id,
            'plant_name': plant_info.get('name', plant_id),
            'area': row['area_name'],
            'fault_type': row['problem_code_text'],
            'fault_icon': FAULT_ICONS.get(row['problem_code_text'], 'exclamation-triangle'),
            'status': row['user_status'],
            'status_info': STATUS_DISPLAY.get(row['user_status'], {}),
            'risk_level': row['kunda_risk_factor'],
            'duration': format_duration(duration),
            'duration_hours': round(duration, 1) if duration > 0 else None,
            'weather': {'temp': round(row['day_max_temp'], 1), 'wind': round(row['day_wind'], 1)},
            'color': plant_info.get('color', '#6c757d')
        })
    
    area_markers = []
    for plant_id, info in PLANT_CONFIG.items():
        plant_faults = len(synthetic_df[synthetic_df['main_work_center'] == plant_id])
        area_markers.append({
            'plant_id': plant_id,
            'plant_name': info['name'],
            'area': info['area'],
            'lat': info['lat'],
            'lng': info['lng'],
            'color': info['color'],
            'risk_level': info['risk_label'],
            'fault_count': plant_faults
        })
    
    return {
        'summary': {'total_faults': total, 'statuses': status_summary, 'by_area': by_area, 'by_fault_type': by_fault},
        'recent_faults': recent,
        'map_markers': area_markers
    }


@app.get("/predict", tags=["Prediction"])
async def predict(
    plant: str = Query(..., description="Plant ID"),
    temp: Optional[float] = Query(default=None),
    wind: Optional[float] = Query(default=None)
):
    if plant not in PLANT_CONFIG:
        raise HTTPException(400, f"Invalid plant. Valid: {list(PLANT_CONFIG.keys())}")
    
    plant_info = PLANT_CONFIG[plant]
    use_temp = temp if temp is not None else AVG_TEMP
    use_wind = wind if wind is not None else AVG_WIND
    
    predicted_fault = predict_fault_for_plant(plant, use_temp, use_wind)
    restoration_hours = predict_restoration_time(plant, predicted_fault, use_temp, use_wind)
    nearest = find_nearest_center(plant_info['lat'], plant_info['lng'])
    total_hours = restoration_hours + (nearest['travel_time_min'] / 60)
    
    return {
        'plant': {'id': plant, 'name': plant_info['name'], 'area': plant_info['area'], 'risk_level': plant_info['risk_label']},
        'conditions': {'temperature': use_temp, 'wind_speed': use_wind},
        'predictions': {
            'fault_type': predicted_fault,
            'fault_icon': FAULT_ICONS.get(predicted_fault, 'exclamation-triangle'),
            'restoration_hours': restoration_hours,
            'restoration_formatted': format_duration(restoration_hours)
        },
        'response': {
            'nearest_center': nearest['name'],
            'distance_km': nearest['distance_km'],
            'travel_time_min': nearest['travel_time_min'],
            'total_eta_formatted': format_duration(total_hours)
        }
    }


@app.get("/stats", tags=["Analytics"])
async def get_stats():
    if synthetic_df is None:
        raise HTTPException(500, "Data not loaded")
    return {
        'total_records': len(synthetic_df),
        'fault_distribution': synthetic_df['problem_code_text'].value_counts().to_dict(),
        'status_distribution': synthetic_df['user_status'].value_counts().to_dict(),
        'area_distribution': synthetic_df['area_name'].value_counts().to_dict()
    }


# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
