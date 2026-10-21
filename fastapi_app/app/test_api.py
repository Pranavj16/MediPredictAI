"""
Test suite for MediPredict AI FastAPI microservice endpoints and explainability engine.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to MediPredict AI API"

def test_diabetes_prediction():
    payload = {
        "gender": "Female",
        "age": 45.0,
        "hypertension": 0,
        "heart_disease": 0,
        "smoking_history": "never",
        "bmi": 26.5,
        "HbA1c_level": 5.8,
        "blood_glucose_level": 110.0
    }
    response = client.post("/predict/diabetes", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "risk_score" in data
    assert "confidence" in data
    assert "feature_contributions" in data
    assert data["condition"] == "diabetes"

def test_heart_prediction():
    payload = {
        "Age": 54,
        "Sex": "M",
        "ChestPainType": "ATA",
        "RestingBP": 128,
        "Cholesterol": 215,
        "FastingBS": 0,
        "RestingECG": "Normal",
        "MaxHR": 150,
        "ExerciseAngina": "N",
        "Oldpeak": 0.5,
        "ST_Slope": "Up"
    }
    response = client.post("/predict/heart", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "risk_score" in data
    assert data["condition"] == "heart"

def test_kidney_prediction():
    payload = {
        "age": 48.0,
        "bp": 80.0,
        "sg": 1.020,
        "al": 0.0,
        "su": 0.0,
        "rbc": "normal",
        "pc": "normal",
        "pcc": "notpresent",
        "ba": "notpresent",
        "bgr": 100.0,
        "bu": 36.0,
        "sc": 1.2,
        "sod": 137.0,
        "pot": 4.4,
        "hemo": 15.4,
        "pcv": 44.0,
        "wc": 7800.0,
        "rc": 5.2,
        "htn": "no",
        "dm": "no",
        "cad": "no",
        "appet": "good",
        "pe": "no",
        "ane": "no"
    }
    response = client.post("/predict/kidney", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert data["condition"] == "kidney"

def test_liver_prediction():
    payload = {
        "age": 45.0,
        "gender": 1,
        "tot_bilirubin": 0.9,
        "direct_bilirubin": 0.2,
        "tot_proteins": 6.8,
        "albumin": 3.4,
        "ag_ratio": 1.0,
        "sgpt": 24.0,
        "sgot": 28.0,
        "alkphos": 180.0
    }
    response = client.post("/predict/liver", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert data["condition"] == "liver"

def test_parkinson_prediction():
    payload = {
        "MDVP_Fo_Hz": 154.2,
        "MDVP_Fhi_Hz": 160.1,
        "MDVP_Flo_Hz": 140.3,
        "MDVP_Jitter_percent": 0.003,
        "MDVP_Jitter_Abs": 0.00003,
        "MDVP_RAP": 0.002,
        "MDVP_PPQ": 0.002,
        "Jitter_DDP": 0.005,
        "MDVP_Shimmer": 0.02,
        "MDVP_Shimmer_dB": 0.18,
        "Shimmer_APQ3": 0.01,
        "Shimmer_APQ5": 0.012,
        "MDVP_APQ": 0.015,
        "Shimmer_DDA": 0.03,
        "NHR": 0.008,
        "HNR": 24.5,
        "RPDE": 0.45,
        "DFA": 0.65,
        "spread1": -5.2,
        "spread2": 0.18,
        "D2": 2.1,
        "PPE": 0.15
    }
    response = client.post("/predict/parkinson", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert data["condition"] == "parkinson"

def test_stroke_prediction():
    payload = {
        "gender": "Female",
        "age": 42.0,
        "hypertension": 0,
        "heart_disease": 0,
        "ever_married": "Yes",
        "work_type": "Private",
        "Residence_type": "Urban",
        "avg_glucose_level": 92.5,
        "bmi": 24.1,
        "smoking_status": "never smoked"
    }
    response = client.post("/predict/stroke", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert data["condition"] == "stroke"
