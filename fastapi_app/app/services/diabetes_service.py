from pathlib import Path
import joblib
import pandas as pd
from app.services.explainability import (
    compute_feature_contributions,
    build_explanation_response
)

BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_DIR = BASE_DIR / "ml_training" / "trained_models"

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

    patient_scaled = scaler.transform(patient)

    prediction = int(model.predict(patient_scaled)[0])

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(patient_scaled)[0]
        risk_score = float(proba[1] * 100.0)
        confidence = float(proba[prediction] * 100.0)
    else:
        risk_score = 100.0 if prediction == 1 else 0.0
        confidence = 85.0

    contributions = compute_feature_contributions(
        model, scaler, columns, patient_scaled, "diabetes"
    )

    return build_explanation_response(
        "diabetes", prediction, risk_score, confidence, contributions
    )