import joblib
import pandas as pd

model = joblib.load("../trained_models/diabetes_model.pkl")
scaler = joblib.load("../trained_models/diabetes_scaler.pkl")
columns = joblib.load("../trained_models/diabetes_columns.pkl")

patient = pd.DataFrame([{
    "gender": "Male",
    "age": 25,
    "hypertension": 0,
    "heart_disease": 0,
    "smoking_history": "never",
    "bmi": 22.5,
    "HbA1c_level": 5.2,
    "blood_glucose_level": 95
}])

patient = pd.get_dummies(
    patient,
    columns=["gender", "smoking_history"]
)

patient = patient.reindex(columns=columns, fill_value=0)

patient = scaler.transform(patient)

print(model.predict(patient))
print(model.predict_proba(patient))