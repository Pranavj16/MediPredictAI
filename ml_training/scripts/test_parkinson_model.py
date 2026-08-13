import joblib
import pandas as pd
import numpy as np

# Load assets
model = joblib.load("../trained_models/parkinson_model.pkl")
scaler = joblib.load("../trained_models/parkinson_scaler.pkl")
columns = joblib.load("../trained_models/parkinson_columns.pkl")

# Load original dataset to find sample records
df = pd.read_csv("../datasets/parkinsons/parkinsons.csv")

# Find a sample with status=1 (Parkinson's)
sample_positive = df[df['status'] == 1].iloc[0].to_dict()
# Find a sample with status=0 (Healthy)
sample_negative = df[df['status'] == 0].iloc[0].to_dict()

# Print the true labels
print(f"Sample Positive True Status: {sample_positive['status']}")
print(f"Sample Negative True Status: {sample_negative['status']}")

# Convert key names to match the FastAPI input schema (replacing colon and parentheses with underscores)
def prepare_data(sample):
    # Remove metadata/target keys
    for key in ['name', 'status']:
        if key in sample:
            sample.pop(key)
            
    # Rename keys
    renamed = {}
    for k, v in sample.items():
        new_key = k.replace(':', '_').replace('(', '_').replace(')', '_').replace('%', 'percent')
        renamed[new_key] = v
    return renamed

payload_positive = prepare_data(sample_positive)
payload_negative = prepare_data(sample_negative)

# Run inference
def predict(payload, label):
    patient = pd.DataFrame([payload])
    
    # Reindex to match training columns order and name
    patient = patient.reindex(columns=columns, fill_value=0)
    
    # Scale
    patient = scaler.transform(patient)
    
    # Predict
    pred = model.predict(patient)[0]
    prob = model.predict_proba(patient)[0].max()
    
    print("=" * 50)
    print(f"Inference for {label}:")
    print(f"Prediction : {'Parkinson Disease' if pred == 1 else 'Healthy'}")
    print(f"Confidence : {prob * 100:.2f}%")
    print("=" * 50)

predict(payload_positive, "True Parkinson Patient")
predict(payload_negative, "True Healthy Subject")
