# K-Electric Predictive Maintenance System

A machine learning-powered dashboard for predicting electrical faults and estimating restoration times across K-Electric's grid infrastructure in Karachi.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python server.py

# Open dashboard
# http://localhost:8000/static/index.html
```

## 📁 Project Structure

```
FYP_KE/
├── server.py              # FastAPI backend server
├── train_models.py        # ML model training script
├── requirements.txt       # Python dependencies
│
├── data/
│   ├── synthetic_faults.csv    # 997 fault records with weather data
│   └── service_centers.csv     # 49 KE service center locations
│
├── models/
│   ├── fault_classifier.pkl    # Predicts fault type
│   ├── restoration_model.pkl   # Predicts repair duration
│   ├── plant_encoder.pkl       # Encodes plant IDs
│   └── fault_encoder.pkl       # Encodes fault types
│
├── frontend/
│   ├── index.html         # Main dashboard
│   ├── css/styles.css     # Styling
│   └── js/dashboard.js    # Frontend logic
│
└── notebooks/
    ├── model_development.ipynb   # ML model development
    └── traffic_analysis.ipynb    # Service center analysis
```

## 🔧 Features

### ML Predictions
- **Fault Type Prediction**: Predicts likely fault type (Motor Failure, Short Circuit, Leak, Sensor Fault) based on plant location, weather, and kunda risk
- **Restoration Time**: Estimates repair duration considering fault type, time of day, and environmental factors

### Dashboard
- Interactive map showing plant locations and risk zones
- Real-time fault records with filtering by status, risk level, and fault type
- ML prediction panel for any selected plant
- Charts showing fault distribution by type and area

### Areas Covered
| Plant | Area | Risk Level |
|-------|------|------------|
| PLANT_01 | Korangi | Extreme |
| PLANT_02 | Surjani | High |
| PLANT_03 | Nazimabad | Medium |
| MAINT_01 | Clifton | Secure |

## 🛠️ API Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `GET /dashboard` - All dashboard data
- `GET /plants` - Plant information
- `GET /predict?plant=PLANT_01&temp=35&wind=20` - ML predictions
- `GET /stats` - Aggregate statistics

## 📊 Model Details

**Fault Classifier (RandomForest)**
- Features: Plant, Month, Temperature, Wind, Kunda Risk Penalty
- Predicts: Motor Failure, Short Circuit, Leak, Sensor Fault

**Restoration Time Regressor (RandomForest)**
- Features: Plant, Fault Type, Hour, Temperature, Wind, Risk, Wind×Risk Interaction
- Output: Estimated repair hours (1-48h range)

## 👥 Team

Final Year Project - K-Electric Predictive Maintenance System
