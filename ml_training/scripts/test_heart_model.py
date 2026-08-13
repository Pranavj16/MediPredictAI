import joblib
import pandas as pd

# Load trained files
model = joblib.load("../trained_models/heart_model.pkl")
scaler = joblib.load("../trained_models/heart_scaler.pkl")
columns = joblib.load("../trained_models/heart_columns.pkl")

# Sample Patient
patient = pd.DataFrame([{
    "Age": 55,
    "Sex": "M",
    "ChestPainType": "ATA",
    "RestingBP": 130,
    "Cholesterol": 240,
    "FastingBS": 0,
    "RestingECG": "Normal",
    "MaxHR": 150,
    "ExerciseAngina": "N",
    "Oldpeak": 1.2,
    "ST_Slope": "Up"
}])

# Apply the same preprocessing used during training
patient = pd.get_dummies(
    patient,
    columns=[
        "Sex",
        "ChestPainType",
        "RestingECG",
        "ExerciseAngina",
        "ST_Slope"
    ]
)

# Match training columns
patient = patient.reindex(
    columns=columns,
    fill_value=0
)

# Scale data
patient = scaler.transform(patient)

# Predict
prediction = model.predict(patient)[0]
probability = model.predict_proba(patient)[0].max()

print("=" * 50)
print("Heart Disease Prediction")
print("=" * 50)

if prediction == 1:
    print("Prediction : Positive")
else:
    print("Prediction : Negative")

print(f"Confidence : {probability * 100:.2f}%")
print("=" * 50)