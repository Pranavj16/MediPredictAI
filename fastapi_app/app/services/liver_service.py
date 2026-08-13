from pathlib import Path
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_DIR = BASE_DIR / "ml_training" / "trained_models"

model = joblib.load(MODEL_DIR / "liver_model.pkl")
scaler = joblib.load(MODEL_DIR / "liver_scaler.pkl")
columns = joblib.load(MODEL_DIR / "liver_columns.pkl")


def predict_liver(data):

    patient = pd.DataFrame([data])

    patient = patient.reindex(
        columns=columns,
        fill_value=0
    )

    patient = scaler.transform(patient)

    prediction = model.predict(patient)[0]

    probability = model.predict_proba(patient)[0].max()

    return {
        "prediction": int(prediction),
        "probability": round(float(probability * 100), 2)
    }