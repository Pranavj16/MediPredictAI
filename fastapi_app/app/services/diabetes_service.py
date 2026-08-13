from pathlib import Path
import joblib
import pandas as pd

# Project Root
BASE_DIR = Path(__file__).resolve().parents[3]

# Trained Models Folder
MODEL_DIR = BASE_DIR / "ml_training" / "trained_models"

# Load Files
model = joblib.load(MODEL_DIR / "diabetes_model.pkl")
scaler = joblib.load(MODEL_DIR / "diabetes_scaler.pkl")
columns = joblib.load(MODEL_DIR / "diabetes_columns.pkl")


def predict_diabetes(data):
    patient = pd.DataFrame([data])

    patient = pd.get_dummies(
        patient,
        columns=["gender", "smoking_history"]
    )

    patient = patient.reindex(
        columns=columns,
        fill_value=0
    )

    patient = scaler.transform(patient)

    prediction = model.predict(patient)[0]

    probability = model.predict_proba(patient)[0].max()

    return {
        "prediction": int(prediction),
        "probability": round(float(probability), 4)
    }