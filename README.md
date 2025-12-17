# K-Electric Predictive Maintenance System

A machine learning-powered dashboard for predicting electrical faults and estimating restoration times across K-Electric's grid infrastructure in Karachi.

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Git (optional, for cloning)

### Installation

```bash
# 1. Clone or download the repository
git clone <repository-url>
cd FYP_KE

# 2. Create a virtual environment (recommended)
python -m venv .venv

# 3. Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start the server
python server.py
```

### Access the Application
Once the server is running, open your browser:

| Page | URL | Description |
|------|-----|-------------|
| **Dashboard** | http://localhost:8000/static/index.html | Main fault prediction dashboard |
| **Interactive Map** | http://localhost:8000/static/interactive.html | Interactive plant/fault visualization |
| **Coverage Map** | http://localhost:8000/static/coverage.html | Service center coverage zones |
| **API Docs** | http://localhost:8000/docs | FastAPI auto-generated documentation |

## 📁 Project Structure

```
FYP_KE/
├── server.py              # FastAPI backend server
├── train_models.py        # ML model training script
├── requirements.txt       # Python dependencies
├── README.md              # This file
│
├── data/
│   ├── synthetic_faults.csv    # Fault records with weather data
│   ├── service_centers.csv     # 49 KE service center locations
│   └── cached_isochrones.json  # Pre-computed coverage zones
│
├── models/
│   ├── fault_classifier.pkl    # Predicts fault type
│   ├── restoration_model.pkl   # Predicts repair duration
│   ├── plant_encoder.pkl       # Encodes plant IDs
│   └── fault_encoder.pkl       # Encodes fault types
│
├── frontend/
│   ├── index.html         # Main dashboard
│   ├── interactive.html   # Interactive map
│   ├── coverage.html      # Coverage analysis
│   ├── css/styles.css     # Styling
│   └── js/dashboard.js    # Frontend logic
│
└── notebooks/
    ├── model_development.ipynb   # ML model development
    └── traffic_analysis.ipynb    # Service center analysis
```

## 🔧 Features

### ML Predictions
- **Fault Type Prediction**: Predicts fault type (Motor Failure, Short Circuit, Leak, Sensor Fault) based on plant location, weather conditions, and kunda risk
- **Restoration Time**: Estimates repair duration considering fault type, time of day, and environmental factors

### Dashboard Features
- Interactive map showing plant locations and risk zones
- Real-time fault records with filtering by status, risk level, and fault type
- ML prediction panel for any selected plant
- Charts showing fault distribution by type and area

### Coverage Analysis
- Service center coverage zones (10/20/30 minute drive times)
- 23 centers with pre-computed isochrones
- 26 centers with fallback circular coverage
- Real-time routing via OpenRouteService API

### Weather Integration
- Live weather data from Meteostat API
- Temperature and wind speed affect predictions
- No API key required for weather data

### Routing
- Real-time driving directions via OpenRouteService
- Route optimization for service teams
- Requires ORS API key (free tier available)

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/dashboard` | GET | All dashboard data |
| `/plants` | GET | Plant information |
| `/predict` | GET | ML predictions |
| `/stats` | GET | Aggregate statistics |
| `/weather` | GET | Current Karachi weather |
| `/service-centers` | GET | All service centers |
| `/nearest-service-center` | GET | Find nearest center |
| `/route` | GET | Get driving route |

### Example Prediction Request
```
GET /predict?plant=PLANT_01&temp=35&wind=20
```

## 📊 Model Details

### Fault Classifier (RandomForest)
- **Features**: Plant, Month, Temperature, Wind, Kunda Risk Penalty
- **Predicts**: Motor Failure, Short Circuit, Leak, Sensor Fault

### Restoration Time Regressor (RandomForest)
- **Features**: Plant, Fault Type, Hour, Temperature, Wind, Risk, Wind×Risk Interaction
- **Output**: Estimated repair hours (1-48h range)

## ⚙️ Configuration

### Environment Variables (Optional)
```bash
# OpenRouteService API Key (for routing features)
# Get free key at: https://openrouteservice.org/dev/#/signup
export ORS_API_KEY=your_api_key_here
```

### Service Centers Data
The `data/service_centers.csv` contains 49 KE service centers across Karachi with:
- Center Name and Type (CEC/CFC)
- Geographic coordinates (Lat/Lng)
- Town/Area information

### Cached Isochrones
Pre-computed coverage zones in `data/cached_isochrones.json`:
- 23 centers with polygon-based coverage zones
- 10, 20, 30 minute drive time zones
- Remaining centers use circular fallback coverage

## 🔄 Retraining Models

If you need to retrain the ML models:

```bash
python train_models.py
```

This will regenerate all `.pkl` files in the `models/` directory.

## 🐛 Troubleshooting

### Server won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is available
- Verify Python version: `python --version` (needs 3.10+)

### Models not loading
- Ensure `models/` directory contains all `.pkl` files
- Run `python train_models.py` to regenerate models

### Coverage page shows "Loading failed"
- Check if `data/cached_isochrones.json` exists
- Verify JSON format is valid

### Routing not working
- ORS API key may be rate-limited or expired
- Get a new free key at https://openrouteservice.org

## 👥 Team

Final Year Project - K-Electric Predictive Maintenance System
