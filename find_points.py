import joblib
import pandas as pd
import numpy as np
import os

base_dir = r"d:\Predicitive Maintainence for Electrical Machines Using Machine Learning"
scaler_path = os.path.join(base_dir, "Data Preprocessing", "scaler.pkl")
model_path = os.path.join(base_dir, "Model Training", "motor_rf_model.pkl")

scaler = joblib.load(scaler_path)
rf_model = joblib.load(model_path)

features_ordered = [
    "Frequency(Hz)", "Current(A)", "RPM", "Voltage(V)", "VFD_Temp(C)", 
    "ApparentPower(VA)", "LoadFriction(A/Hz)", "CoolingEfficiency(C/VA)", "TorqueEst"
]

# Create some random values in specific ranges
import random
random.seed(42)

results = {}
classes_found = set()
attempts = 0

while len(classes_found) < 4 and attempts < 100000:
    freq = round(random.uniform(4.0, 60.0), 2)
    volts = round(random.uniform(200.0, 400.0), 2)
    # create some relations
    rpm = round((freq * 120 / 4) * random.uniform(0.9, 1.0), 0)
    current = round(random.uniform(1.0, 15.0), 1)
    temp = round(random.uniform(30.0, 90.0), 1)
    power = round(current * volts, 2)
    friction = round(current / freq if freq > 0 else 0, 4)
    cooling = round(temp / power if power > 0 else 0, 4)
    torque = round((power * 0.8) / (rpm * 0.1047) if rpm > 0 else 0, 2)
    
    vals = [freq, current, rpm, volts, temp, power, friction, cooling, torque]
    
    df = pd.DataFrame([vals], columns=features_ordered)
    scaled = scaler.transform(df)
    pred = rf_model.predict(scaled)[0]
    
    if pred not in classes_found:
        classes_found.add(pred)
        results[pred] = vals
    attempts += 1

state_map = {0: "Healthy", 1: "Phase Unbalance", 2: "Overheat", 3: "Bearing Fault"}

for p_val, data in results.items():
    print(f"--- {state_map.get(p_val, 'Unknown')} ---")
    for i, f in enumerate(features_ordered):
        print(f"  {f}: {data[i]}")

if len(classes_found) < 4:
    print(f"Warning: Only found {len(classes_found)} classes. Could not find others.")
