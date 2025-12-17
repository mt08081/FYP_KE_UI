"""
K-Electric Fault Prediction API Server
======================================
Predictive maintenance system using ML models for fault type and restoration time prediction.
Includes: Live Weather (Meteostat), Real Routing (ORS API), Isochrone Coverage

Run: python server.py
API Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
import joblib
import pandas as pd
import numpy as np
import math
import datetime
import os
import warnings
import requests
import asyncio
from functools import lru_cache

warnings.filterwarnings('ignore')

# ============================================
# API KEYS - Configure these!
# ============================================
# Get free ORS key at: https://openrouteservice.org/dev/#/signup
# ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjhjMDgzMjgzMmVjZDRhYmU4ZGE3ZTA1ZGE0OWZlYmY3IiwiaCI6Im11cm11cjY0In0="
ORS_API_KEY = os.environ.get('ORS_API_KEY', 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjhjMDgzMjgzMmVjZDRhYmU4ZGE3ZTA1ZGE0OWZlYmY3IiwiaCI6Im11cm11cjY0In0=')

# ============================================
# APP SETUP
# ============================================
app = FastAPI(
    title="K-Electric Predictive Maintenance API",
    description="Fault prediction, restoration time estimation, live weather, and routing for KE grid stations",
    version="2.0.0"
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
# Serve data files (for cached isochrones)
app.mount("/data", StaticFiles(directory="data"), name="data")

# ============================================
# PATHS (Clean structure)
# ============================================
BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")

# ============================================
# KARACHI COORDINATES (for Meteostat)
# ============================================
KARACHI_LAT = 24.8607
KARACHI_LNG = 67.0011

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

# Default weather (fallback if Meteostat fails)
AVG_TEMP = 32.5
AVG_WIND = 15.0

# ============================================
# REQUEST/RESPONSE MODELS
# ============================================
class FaultLocation(BaseModel):
    lat: float
    lng: float
    description: Optional[str] = None

class WeatherData(BaseModel):
    temperature: float
    wind_speed: float
    humidity: Optional[float] = None
    source: str = "meteostat"
    timestamp: Optional[str] = None

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
    print("🚀 K-Electric Predictive Maintenance API v2.0")
    print("=" * 50)
    load_models()
    load_data()
    print("=" * 50)
    print("📍 Dashboard:    http://localhost:8000/static/index.html")
    print("🗺️ Interactive:  http://localhost:8000/static/interactive.html")
    print("📊 Coverage:     http://localhost:8000/static/coverage.html")
    print("📚 API Docs:     http://localhost:8000/docs")
    print("=" * 50 + "\n")


# ============================================
# WEATHER API (Meteostat)
# ============================================
def get_live_weather():
    """
    Fetch current weather for Karachi using Meteostat via Open-Meteo API
    Falls back to averages if API fails
    """
    try:
        # Using Open-Meteo API (free, no key required) as Meteostat alternative
        url = f"https://api.open-meteo.com/v1/forecast?latitude={KARACHI_LAT}&longitude={KARACHI_LNG}&current=temperature_2m,wind_speed_10m,relative_humidity_2m"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            current = data.get('current', {})
            return {
                'temperature': current.get('temperature_2m', AVG_TEMP),
                'wind_speed': current.get('wind_speed_10m', AVG_WIND),
                'humidity': current.get('relative_humidity_2m', 60),
                'source': 'open-meteo',
                'timestamp': current.get('time', datetime.datetime.now().isoformat())
            }
    except Exception as e:
        print(f"⚠️ Weather API error: {e}")
    
    # Fallback
    return {
        'temperature': AVG_TEMP,
        'wind_speed': AVG_WIND,
        'humidity': 60,
        'source': 'fallback',
        'timestamp': datetime.datetime.now().isoformat()
    }


# ============================================
# ROUTING API (OpenRouteService)
# ============================================
def get_ors_route(origin_lat, origin_lng, dest_lat, dest_lng):
    """
    Get actual driving route using OpenRouteService API
    Returns: (travel_time_minutes, distance_km) or (None, None) on failure
    """
    if ORS_API_KEY == 'YOUR_ORS_API_KEY_HERE':
        return None, None  # No API key configured
    
    try:
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        headers = {
            'Authorization': ORS_API_KEY,
            'Content-Type': 'application/json'
        }
        body = {
            "coordinates": [[origin_lng, origin_lat], [dest_lng, dest_lat]],
            "instructions": False
        }
        
        response = requests.post(url, json=body, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'routes' in data and len(data['routes']) > 0:
                route = data['routes'][0]['summary']
                duration_min = route['duration'] / 60
                distance_km = route['distance'] / 1000
                return round(duration_min, 1), round(distance_km, 2)
    except Exception as e:
        print(f"⚠️ ORS routing error: {e}")
    
    return None, None


def get_ors_isochrone(lat, lng, time_minutes):
    """
    Get isochrone polygon (reachable area within X minutes) from ORS
    Returns: List of [lat, lng] coordinates or None
    """
    if ORS_API_KEY == 'YOUR_ORS_API_KEY_HERE':
        return None
    
    try:
        url = "https://api.openrouteservice.org/v2/isochrones/driving-car"
        headers = {
            'Authorization': ORS_API_KEY,
            'Content-Type': 'application/json'
        }
        body = {
            "locations": [[lng, lat]],
            "range": [time_minutes * 60],
            "range_type": "time"
        }
        
        response = requests.post(url, json=body, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if 'features' in data and len(data['features']) > 0:
                coords = data['features'][0]['geometry']['coordinates'][0]
                # Convert from [lng, lat] to [lat, lng] for Leaflet
                return [[c[1], c[0]] for c in coords]
    except Exception as e:
        print(f"⚠️ ORS isochrone error: {e}")
    
    return None


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
    if 7 <= hour < 10: return 1.5 # morning
    elif 16 <= hour < 20: return 1.6 # evening
    elif 10 <= hour < 16: return 1.2 # afternoon
    return 1.0 # night


def find_nearest_center(lat, lng, use_ors=False):
    """
    Find nearest service center to a fault location.
    If use_ors=True and ORS API is configured, uses real routing.
    """
    if centers_df is None or centers_df.empty:
        return {'name': 'Unknown Center', 'distance_km': 5, 'travel_time_min': 15, 'center_type': 'Unknown', 'routing_source': 'fallback'}
    
    best, best_dist = None, float('inf')
    for _, c in centers_df.iterrows():
        d = haversine(lat, lng, c['Latitude'], c['Longitude'])
        if d < best_dist:
            best_dist, best = d, c
    
    # Try ORS for actual routing if requested
    if use_ors and best is not None:
        ors_time, ors_dist = get_ors_route(best['Latitude'], best['Longitude'], lat, lng)
        if ors_time is not None:
            return {
                'name': best['Center Name'],
                'center_type': best.get('Type', 'Unknown'),
                'center_lat': best['Latitude'],
                'center_lng': best['Longitude'],
                'distance_km': ors_dist,
                'travel_time_min': round(ors_time * get_traffic_factor(), 1),
                'base_travel_min': ors_time,
                'traffic_factor': get_traffic_factor(),
                'routing_source': 'ors'
            }
    
    # Fallback to Haversine estimate
    travel_min = (best_dist / 30) * 60 * get_traffic_factor()
    return {
        'name': best['Center Name'],
        'center_type': best.get('Type', 'Unknown'),
        'center_lat': best['Latitude'],
        'center_lng': best['Longitude'],
        'distance_km': round(best_dist, 2),
        'travel_time_min': round(travel_min, 1),
        'base_travel_min': round((best_dist / 30) * 60, 1),
        'traffic_factor': get_traffic_factor(),
        'routing_source': 'haversine'
    }


def get_area_risk_for_location(lat, lng):
    """
    Determine kunda risk based on proximity to known risk areas
    """
    # Calculate distance to each plant and use nearest plant's risk
    min_dist = float('inf')
    nearest_risk = {'penalty': 0, 'label': 'Medium', 'area': 'Unknown'}
    
    for plant_id, info in PLANT_CONFIG.items():
        d = haversine(lat, lng, info['lat'], info['lng'])
        if d < min_dist:
            min_dist = d
            nearest_risk = {
                'penalty': info['risk_penalty'],
                'label': info['risk_label'],
                'area': info['area']
            }
    
    return nearest_risk


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
# NEW API ENDPOINTS - Weather, Routing, Interactive
# ============================================

@app.get("/weather/current", tags=["Weather"])
async def get_current_weather():
    """Get current weather conditions for Karachi using Open-Meteo API"""
    weather = get_live_weather()
    return {
        'location': 'Karachi, Pakistan',
        'coordinates': {'lat': KARACHI_LAT, 'lng': KARACHI_LNG},
        'current': weather,
        'traffic_factor': get_traffic_factor(),
        'time_period': _get_time_period_label()
    }


def _get_time_period_label():
    hour = datetime.datetime.now().hour
    if 7 <= hour < 10: return 'Morning Rush (1.5x)'
    elif 16 <= hour < 20: return 'Evening Rush (1.6x)'
    elif 10 <= hour < 16: return 'Midday (1.2x)'
    return 'Night (1.0x)'


@app.get("/centers/all", tags=["Service Centers"])
async def get_all_centers():
    """Get all 49 service centers with their details"""
    if centers_df is None:
        raise HTTPException(500, "Centers data not loaded")
    
    centers = []
    for _, row in centers_df.iterrows():
        centers.append({
            'name': row['Center Name'],
            'type': row.get('Type', 'CFC'),
            'area': row.get('Town/Area', 'Unknown'),
            'lat': row['Latitude'],
            'lng': row['Longitude']
        })
    
    # Summary
    cfc_count = len([c for c in centers if c['type'] == 'CFC'])
    cec_count = len([c for c in centers if c['type'] == 'CEC'])
    
    return {
        'total': len(centers),
        'cfc_count': cfc_count,
        'cec_count': cec_count,
        'centers': centers
    }


@app.get("/routing/travel-time", tags=["Routing"])
async def get_travel_time(
    origin_lat: float = Query(..., description="Origin latitude"),
    origin_lng: float = Query(..., description="Origin longitude"),
    dest_lat: float = Query(..., description="Destination latitude"),
    dest_lng: float = Query(..., description="Destination longitude")
):
    """Get travel time between two points using ORS or Haversine fallback"""
    
    # Try ORS first
    ors_time, ors_dist = get_ors_route(origin_lat, origin_lng, dest_lat, dest_lng)
    
    if ors_time is not None:
        return {
            'source': 'openrouteservice',
            'distance_km': ors_dist,
            'base_travel_min': ors_time,
            'traffic_factor': get_traffic_factor(),
            'adjusted_travel_min': round(ors_time * get_traffic_factor(), 1)
        }
    
    # Fallback to Haversine
    distance = haversine(origin_lat, origin_lng, dest_lat, dest_lng)
    base_time = (distance / 30) * 60  # 30 km/h average
    
    return {
        'source': 'haversine_estimate',
        'distance_km': round(distance, 2),
        'base_travel_min': round(base_time, 1),
        'traffic_factor': get_traffic_factor(),
        'adjusted_travel_min': round(base_time * get_traffic_factor(), 1),
        'note': 'Configure ORS_API_KEY for accurate routing'
    }


@app.get("/routing/isochrone", tags=["Routing"])
async def get_isochrone(
    lat: float = Query(..., description="Center latitude"),
    lng: float = Query(..., description="Center longitude"),
    time_minutes: int = Query(default=15, description="Travel time in minutes (10, 15, 20, 30)")
):
    """Get isochrone polygon showing area reachable within specified time"""
    
    polygon = get_ors_isochrone(lat, lng, time_minutes)
    
    if polygon:
        return {
            'source': 'openrouteservice',
            'center': {'lat': lat, 'lng': lng},
            'time_minutes': time_minutes,
            'polygon': polygon
        }
    
    # Generate approximate circle if ORS unavailable
    # Estimate radius based on speed and time
    radius_km = (30 / 60) * time_minutes  # 30 km/h
    
    return {
        'source': 'estimated_circle',
        'center': {'lat': lat, 'lng': lng},
        'time_minutes': time_minutes,
        'radius_km': round(radius_km, 2),
        'polygon': None,
        'note': 'Configure ORS_API_KEY for accurate isochrones'
    }


@app.post("/predict/interactive", tags=["Interactive Prediction"])
async def predict_interactive(location: FaultLocation):
    """
    Interactive fault prediction for any map location.
    Fetches live weather, calculates routing, and returns comprehensive prediction.
    """
    lat, lng = location.lat, location.lng
    
    # 1. Get live weather
    weather = get_live_weather()
    
    # 2. Determine area risk based on location
    area_risk = get_area_risk_for_location(lat, lng)
    
    # 3. Find nearest service center (with ORS if available)
    nearest = find_nearest_center(lat, lng, use_ors=True)
    
    # 4. Determine nearest plant for model prediction
    min_plant_dist = float('inf')
    nearest_plant_id = 'PLANT_01'
    for plant_id, info in PLANT_CONFIG.items():
        d = haversine(lat, lng, info['lat'], info['lng'])
        if d < min_plant_dist:
            min_plant_dist = d
            nearest_plant_id = plant_id
    
    # 5. Predict fault type and restoration time
    predicted_fault = predict_fault_for_plant(
        nearest_plant_id, 
        weather['temperature'], 
        weather['wind_speed']
    )
    
    restoration_hours = predict_restoration_time(
        nearest_plant_id,
        predicted_fault,
        weather['temperature'],
        weather['wind_speed']
    )
    
    # 6. Calculate total ETA
    total_hours = restoration_hours + (nearest['travel_time_min'] / 60)
    
    return {
        'location': {
            'lat': lat,
            'lng': lng,
            'description': location.description,
            'nearest_area': area_risk['area'],
            'risk_level': area_risk['label'],
            'risk_penalty': area_risk['penalty']
        },
        'weather': {
            'temperature': weather['temperature'],
            'wind_speed': weather['wind_speed'],
            'humidity': weather.get('humidity'),
            'source': weather['source'],
            'timestamp': weather.get('timestamp')
        },
        'traffic': {
            'factor': get_traffic_factor(),
            'period': _get_time_period_label()
        },
        'predictions': {
            'fault_type': predicted_fault,
            'fault_icon': FAULT_ICONS.get(predicted_fault, 'exclamation-triangle'),
            'restoration_hours': restoration_hours,
            'restoration_formatted': format_duration(restoration_hours)
        },
        'response': {
            'nearest_center': nearest['name'],
            'center_type': nearest.get('center_type', 'Unknown'),
            'center_coordinates': {
                'lat': nearest.get('center_lat'),
                'lng': nearest.get('center_lng')
            },
            'distance_km': nearest['distance_km'],
            'travel_time_min': nearest['travel_time_min'],
            'routing_source': nearest.get('routing_source', 'haversine')
        },
        'total_eta': {
            'hours': round(total_hours, 2),
            'formatted': format_duration(total_hours)
        }
    }


@app.get("/centers/isochrones", tags=["Coverage Analysis"])
async def get_center_isochrones(
    center_name: Optional[str] = Query(default=None, description="Specific center name"),
    time_minutes: int = Query(default=15, description="Travel time in minutes")
):
    """Get isochrone coverage for service centers"""
    if centers_df is None:
        raise HTTPException(500, "Centers data not loaded")
    
    results = []
    
    if center_name:
        # Single center
        center = centers_df[centers_df['Center Name'] == center_name]
        if center.empty:
            raise HTTPException(404, f"Center '{center_name}' not found")
        row = center.iloc[0]
        polygon = get_ors_isochrone(row['Latitude'], row['Longitude'], time_minutes)
        results.append({
            'name': row['Center Name'],
            'type': row.get('Type', 'CFC'),
            'lat': row['Latitude'],
            'lng': row['Longitude'],
            'time_minutes': time_minutes,
            'polygon': polygon
        })
    else:
        # First 5 centers (to avoid API rate limits)
        for _, row in centers_df.head(5).iterrows():
            polygon = get_ors_isochrone(row['Latitude'], row['Longitude'], time_minutes)
            results.append({
                'name': row['Center Name'],
                'type': row.get('Type', 'CFC'),
                'lat': row['Latitude'],
                'lng': row['Longitude'],
                'time_minutes': time_minutes,
                'polygon': polygon
            })
    
    return {
        'time_minutes': time_minutes,
        'centers': results,
        'note': 'ORS API has rate limits. Request individual centers for best results.'
    }


# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
