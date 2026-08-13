import joblib
import pandas as pd

# Load trained files
model = joblib.load("../trained_models/kidney_model.pkl")
scaler = joblib.load("../trained_models/kidney_scaler.pkl")
columns = joblib.load("../trained_models/kidney_columns.pkl")

# Create a sample patient using the training columns
sample = pd.DataFrame(columns=columns)
sample.loc[0] = 0

# Scale
sample = scaler.transform(sample)

# Predict
prediction = model.predict(sample)[0]
probability = model.predict_proba(sample)[0].max()

print("=" * 50)
print("Kidney Disease Prediction")
print("=" * 50)

if prediction == 1:
    print("Prediction : CKD Detected")
else:
    print("Prediction : Healthy")

print(f"Confidence : {probability * 100:.2f}%")
print("=" * 50)