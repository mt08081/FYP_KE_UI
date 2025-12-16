"""
K-Electric Model Training Script
================================
Trains ML models for fault type prediction and restoration time estimation.

Usage: python train_models.py
Output: Models saved to models/ folder
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import os

# Paths
DATA_PATH = "data/synthetic_faults.csv"
MODEL_DIR = "models"

# Plant risk penalties (from kunda risk analysis)
PLANT_RISK = {
    'PLANT_01': 0.21,      # Korangi - Extreme
    'PLANT_02': 0.1585,    # Surjani - High
    'PLANT_03': 0.0349,    # Nazimabad - Medium
    'MAINT_01': -0.1087    # Clifton - Secure
}


def main():
    print("=" * 50)
    print("🚀 K-Electric Model Training")
    print("=" * 50)
    
    # Load data
    print("\n📊 Loading data...")
    df = pd.read_csv(DATA_PATH)
    print(f"   Records: {len(df)}")
    
    # Add risk penalty
    df['kunda_risk_penalty'] = df['main_work_center'].map(PLANT_RISK)
    
    # Encode categorical features
    le_plant = LabelEncoder()
    le_fault = LabelEncoder()
    
    df['plant_encoded'] = le_plant.fit_transform(df['main_work_center'])
    df['fault_encoded'] = le_fault.fit_transform(df['problem_code_text'])
    
    # Extract time features
    df['malfunction_start'] = pd.to_datetime(df['malfunction_start'], errors='coerce')
    df['month'] = df['malfunction_start'].dt.month.fillna(6).astype(int)
    df['hour'] = pd.to_datetime(df['malfunction_start_time'], format='%H:%M:%S', errors='coerce').dt.hour.fillna(12).astype(int)
    
    # Duration (target for regression)
    df['duration_hours'] = pd.to_numeric(df['malfunction_end'], errors='coerce').fillna(8)
    
    # Interaction feature: wind × risk (high wind + high kunda risk = more danger)
    df['wind_risk_interaction'] = df['day_wind'] * df['kunda_risk_penalty']
    
    # ===== FAULT TYPE CLASSIFIER =====
    print("\n🔧 Training Fault Type Classifier...")
    
    # Features: [Plant, Month, Temp, Wind, Risk]
    X_clf = df[['plant_encoded', 'month', 'day_max_temp', 'day_wind', 'kunda_risk_penalty']].values
    y_clf = df['fault_encoded'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X_clf, y_clf, test_size=0.2, random_state=42)
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    clf.fit(X_train, y_train)
    
    acc = clf.score(X_test, y_test)
    print(f"   Accuracy: {acc:.2%}")
    
    # ===== RESTORATION TIME REGRESSOR =====
    print("\n⏱️  Training Restoration Time Regressor...")
    
    # Features: [Plant, Fault, Hour, Temp, Wind, Risk, Wind×Risk]
    X_reg = df[['plant_encoded', 'fault_encoded', 'hour', 'day_max_temp', 'day_wind', 
                'kunda_risk_penalty', 'wind_risk_interaction']].values
    y_reg = df['duration_hours'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)
    
    reg = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=15)
    reg.fit(X_train, y_train)
    
    r2 = reg.score(X_test, y_test)
    print(f"   R² Score: {r2:.3f}")
    
    # Sample predictions
    print("\n📈 Sample Predictions:")
    y_pred = reg.predict(X_test[:5])
    for actual, pred in zip(y_test[:5], y_pred):
        print(f"   Actual: {actual:.1f}h → Predicted: {pred:.1f}h")
    
    # ===== SAVE MODELS =====
    print("\n💾 Saving models...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    joblib.dump(clf, os.path.join(MODEL_DIR, 'fault_classifier.pkl'))
    joblib.dump(reg, os.path.join(MODEL_DIR, 'restoration_model.pkl'))
    joblib.dump(le_plant, os.path.join(MODEL_DIR, 'plant_encoder.pkl'))
    joblib.dump(le_fault, os.path.join(MODEL_DIR, 'fault_encoder.pkl'))
    
    print(f"   ✅ fault_classifier.pkl")
    print(f"   ✅ restoration_model.pkl")
    print(f"   ✅ plant_encoder.pkl")
    print(f"   ✅ fault_encoder.pkl")
    
    print("\n" + "=" * 50)
    print("✅ Training complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
