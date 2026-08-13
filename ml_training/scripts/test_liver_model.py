import joblib
import pandas as pd

model = joblib.load("../trained_models/liver_model.pkl")
scaler = joblib.load("../trained_models/liver_scaler.pkl")
columns = joblib.load("../trained_models/liver_columns.pkl")

patient = pd.DataFrame([{
    "age":45,
    "gender":1,
    "tot_bilirubin":1.2,
    "direct_bilirubin":0.3,
    "tot_proteins":7.0,
    "albumin":4.0,
    "ag_ratio":1.3,
    "sgpt":35,
    "sgot":30,
    "alkphos":180
}])

patient = patient.reindex(columns=columns, fill_value=0)
patient = scaler.transform(patient)

prediction = model.predict(patient)[0]
probability = model.predict_proba(patient)[0].max()

print("=" * 50)
print("Liver Disease Prediction")
print("=" * 50)

if prediction == 1:
    print("Prediction : Liver Disease")
else:
    print("Prediction : Healthy Liver")

print(f"Confidence : {probability * 100:.2f}%")
print("=" * 50)