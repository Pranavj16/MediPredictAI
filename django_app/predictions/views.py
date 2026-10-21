import sys
import requests
from pathlib import Path

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .forms import (
    DiabetesPredictionForm,
    HeartPredictionForm,
    KidneyPredictionForm,
    LiverPredictionForm,
    ParkinsonPredictionForm,
    StrokePredictionForm
)
from patients.models import Patient, RecordedMeasurement, PredictionRecord, AuditEvent

# Add fastapi_app to sys.path to enable local ML prediction service fallback
BASE_DIR = Path(__file__).resolve().parents[2]
FASTAPI_DIR = BASE_DIR / "fastapi_app"
if str(FASTAPI_DIR) not in sys.path:
    sys.path.append(str(FASTAPI_DIR))

try:
    from app.services.diabetes_service import predict_diabetes
    from app.services.heart_service import predict_heart
    from app.services.kidney_service import predict_kidney
    from app.services.liver_service import predict_liver
    from app.services.parkinson_service import predict_parkinson
    from app.services.stroke_service import predict_stroke
except Exception as e:
    predict_diabetes = None
    predict_heart = None
    predict_kidney = None
    predict_liver = None
    predict_parkinson = None
    predict_stroke = None


def persist_prediction_and_measurements(user, condition, data, prediction_result):
    """
    Persists ML prediction record and extracts actual laboratory/clinical measurements
    into RecordedMeasurement table to maintain longitudinal health history.
    """
    if not user.is_authenticated or not prediction_result:
        return

    patient = Patient.objects.filter(user=user).first()
    if not patient:
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        phone = user.profile.phone_number if hasattr(user, 'profile') else ""
        center = user.profile.assigned_center if hasattr(user, 'profile') else ""
        patient = Patient.objects.create(
            user=user,
            registered_by=user,
            full_name=full_name,
            phone_number=phone,
            center=center,
            consent_given=True
        )

    # 1. Save Prediction Record
    PredictionRecord.objects.create(
        patient=patient,
        conducted_by=user,
        condition=condition,
        model_name=prediction_result.get("model_name", f"{condition.title()} Classifier"),
        inputs=data,
        prediction=prediction_result.get("prediction", 0),
        risk_score=prediction_result.get("risk_score", 0.0),
        confidence=prediction_result.get("confidence", 0.0),
        feature_contributions=prediction_result.get("feature_contributions", []),
        clinical_interpretation=prediction_result.get("interpretation", ""),
        limitations=prediction_result.get("limitations", "")
    )

    # 2. Extract and Save Relevant Clinical Measurements
    try:
        if condition == "diabetes":
            if "bmi" in data:
                RecordedMeasurement.objects.create(
                    patient=patient, recorded_by=user, measurement_type="bmi",
                    value_numeric=float(data["bmi"]), unit="kg/m²", source="self_reported"
                )
            if "HbA1c_level" in data:
                RecordedMeasurement.objects.create(
                    patient=patient, recorded_by=user, measurement_type="hba1c",
                    value_numeric=float(data["HbA1c_level"]), unit="%", source="self_reported"
                )
            if "blood_glucose_level" in data:
                RecordedMeasurement.objects.create(
                    patient=patient, recorded_by=user, measurement_type="blood_glucose",
                    value_numeric=float(data["blood_glucose_level"]), unit="mg/dL", source="self_reported"
                )

        elif condition == "heart":
            if "RestingBP" in data:
                RecordedMeasurement.objects.create(
                    patient=patient, recorded_by=user, measurement_type="blood_pressure",
                    value_numeric=float(data["RestingBP"]), secondary_numeric=80.0,
                    unit="mmHg", context="resting_seated", source="self_reported"
                )
            if "Cholesterol" in data and float(data["Cholesterol"]) > 0:
                RecordedMeasurement.objects.create(
                    patient=patient, recorded_by=user, measurement_type="total_cholesterol",
                    value_numeric=float(data["Cholesterol"]), unit="mg/dL", source="self_reported"
                )

        elif condition == "kidney":
            if "bp" in data:
                RecordedMeasurement.objects.create(
                    patient=patient, recorded_by=user, measurement_type="blood_pressure",
                    value_numeric=float(data["bp"]), secondary_numeric=80.0,
                    unit="mmHg", source="clinic_lab"
                )
            if "sc" in data and str(data["sc"]).replace('.', '', 1).isdigit():
                RecordedMeasurement.objects.create(
                    patient=patient, recorded_by=user, measurement_type="serum_creatinine",
                    value_numeric=float(data["sc"]), unit="mg/dL", source="clinic_lab"
                )

        elif condition == "liver":
            if "tot_bilirubin" in data:
                RecordedMeasurement.objects.create(
                    patient=patient, recorded_by=user, measurement_type="bilirubin",
                    value_numeric=float(data["tot_bilirubin"]), unit="mg/dL", source="clinic_lab"
                )

        elif condition == "stroke":
            if "bmi" in data:
                RecordedMeasurement.objects.create(
                    patient=patient, recorded_by=user, measurement_type="bmi",
                    value_numeric=float(data["bmi"]), unit="kg/m²", source="self_reported"
                )
            if "avg_glucose_level" in data:
                RecordedMeasurement.objects.create(
                    patient=patient, recorded_by=user, measurement_type="blood_glucose",
                    value_numeric=float(data["avg_glucose_level"]), unit="mg/dL", source="self_reported"
                )
    except Exception as err:
        print(f"Error extracting measurements in {condition}: {err}")

    # Audit event
    AuditEvent.objects.create(
        user=user,
        patient=patient,
        action=f"PREDICTION_{condition.upper()}",
        details=f"Result: {prediction_result.get('status_label')}, Risk: {prediction_result.get('risk_score')}%"
    )


def get_prediction_result(endpoint_name, data, fallback_func):
    """
    Attempts to call FastAPI microservice using FASTAPI_BACKEND_URL env var,
    falling back to local ports 8001 or 8000, and finally to local ML models.
    """
    import os
    backend_url = os.environ.get("FASTAPI_BACKEND_URL")
    if backend_url:
        try:
            url = f"{backend_url.rstrip('/')}/predict/{endpoint_name}"
            res = requests.post(url, json=data, timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception as err:
            print(f"Error calling remote FastAPI backend {url}: {err}")

    for port in [8001, 8000]:
        try:
            url = f"http://127.0.0.1:{port}/predict/{endpoint_name}"
            res = requests.post(url, json=data, timeout=2)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass

    # Direct local ML model inference fallback
    if fallback_func:
        try:
            return fallback_func(data)
        except Exception as err:
            print(f"Fallback prediction error for {endpoint_name}: {err}")
    return None


@login_required(login_url="login")
def diabetes_prediction(request):
    prediction = None

    if request.method == "POST":
        form = DiabetesPredictionForm(request.POST)

        if form.is_valid():
            data = {
                "gender": form.cleaned_data["gender"],
                "age": form.cleaned_data["age"],
                "hypertension": int(form.cleaned_data["hypertension"]),
                "heart_disease": int(form.cleaned_data["heart_disease"]),
                "smoking_history": form.cleaned_data["smoking_history"],
                "bmi": form.cleaned_data["bmi"],
                "HbA1c_level": form.cleaned_data["HbA1c_level"],
                "blood_glucose_level": form.cleaned_data["blood_glucose_level"],
            }
            prediction = get_prediction_result("diabetes", data, predict_diabetes)
            if prediction:
                persist_prediction_and_measurements(request.user, "diabetes", data, prediction)
    else:
        form = DiabetesPredictionForm()

    return render(
        request,
        "predictions/diabetes.html",
        {
            "form": form,
            "prediction": prediction
        }
    )


@login_required(login_url="login")
def heart_prediction(request):
    prediction = None

    if request.method == "POST":
        form = HeartPredictionForm(request.POST)

        if form.is_valid():
            data = {
                "Age": form.cleaned_data["Age"],
                "Sex": form.cleaned_data["Sex"],
                "ChestPainType": form.cleaned_data["ChestPainType"],
                "RestingBP": form.cleaned_data["RestingBP"],
                "Cholesterol": form.cleaned_data["Cholesterol"],
                "FastingBS": int(form.cleaned_data["FastingBS"]),
                "RestingECG": form.cleaned_data["RestingECG"],
                "MaxHR": form.cleaned_data["MaxHR"],
                "ExerciseAngina": form.cleaned_data["ExerciseAngina"],
                "Oldpeak": form.cleaned_data["Oldpeak"],
                "ST_Slope": form.cleaned_data["ST_Slope"],
            }
            prediction = get_prediction_result("heart", data, predict_heart)
            if prediction:
                persist_prediction_and_measurements(request.user, "heart", data, prediction)
    else:
        form = HeartPredictionForm()

    return render(
        request,
        "predictions/heart.html",
        {
            "form": form,
            "prediction": prediction
        }
    )


@login_required(login_url="login")
def kidney_prediction(request):
    prediction = None

    if request.method == "POST":
        form = KidneyPredictionForm(request.POST)

        if form.is_valid():
            data = {
                "age": form.cleaned_data["age"],
                "bp": form.cleaned_data["bp"],
                "sg": form.cleaned_data["sg"],
                "al": form.cleaned_data["al"],
                "su": form.cleaned_data["su"],
                "rbc": form.cleaned_data["rbc"],
                "pc": form.cleaned_data["pc"],
                "pcc": form.cleaned_data["pcc"],
                "ba": form.cleaned_data["ba"],
                "bgr": form.cleaned_data["bgr"],
                "bu": form.cleaned_data["bu"],
                "sc": form.cleaned_data["sc"],
                "sod": form.cleaned_data["sod"],
                "pot": form.cleaned_data["pot"],
                "hemo": form.cleaned_data["hemo"],
                "pcv": form.cleaned_data["pcv"],
                "wc": form.cleaned_data["wc"],
                "rc": form.cleaned_data["rc"],
                "htn": form.cleaned_data["htn"],
                "dm": form.cleaned_data["dm"],
                "cad": form.cleaned_data["cad"],
                "appet": form.cleaned_data["appet"],
                "pe": form.cleaned_data["pe"],
                "ane": form.cleaned_data["ane"],
            }
            prediction = get_prediction_result("kidney", data, predict_kidney)
            if prediction:
                persist_prediction_and_measurements(request.user, "kidney", data, prediction)
    else:
        form = KidneyPredictionForm()

    return render(
        request,
        "predictions/kidney.html",
        {
            "form": form,
            "prediction": prediction
        }
    )


@login_required(login_url="login")
def liver_prediction(request):
    prediction = None

    if request.method == "POST":
        form = LiverPredictionForm(request.POST)

        if form.is_valid():
            data = {
                "age": form.cleaned_data["age"],
                "gender": int(form.cleaned_data["gender"]),
                "tot_bilirubin": form.cleaned_data["tot_bilirubin"],
                "direct_bilirubin": form.cleaned_data["direct_bilirubin"],
                "tot_proteins": form.cleaned_data["tot_proteins"],
                "albumin": form.cleaned_data["albumin"],
                "ag_ratio": form.cleaned_data["ag_ratio"],
                "sgpt": form.cleaned_data["sgpt"],
                "sgot": form.cleaned_data["sgot"],
                "alkphos": form.cleaned_data["alkphos"],
            }
            prediction = get_prediction_result("liver", data, predict_liver)
            if prediction:
                persist_prediction_and_measurements(request.user, "liver", data, prediction)
    else:
        form = LiverPredictionForm()

    return render(
        request,
        "predictions/liver.html",
        {
            "form": form,
            "prediction": prediction
        }
    )


@login_required(login_url="login")
def parkinson_prediction(request):
    prediction = None

    if request.method == "POST":
        form = ParkinsonPredictionForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            prediction = get_prediction_result("parkinson", data, predict_parkinson)
            if prediction:
                persist_prediction_and_measurements(request.user, "parkinson", data, prediction)
    else:
        form = ParkinsonPredictionForm()

    return render(
        request,
        "predictions/parkinson.html",
        {
            "form": form,
            "prediction": prediction
        }
    )


@login_required(login_url="login")
def stroke_prediction(request):
    prediction = None

    if request.method == "POST":
        form = StrokePredictionForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            prediction = get_prediction_result("stroke", data, predict_stroke)
            if prediction:
                persist_prediction_and_measurements(request.user, "stroke", data, prediction)
    else:
        form = StrokePredictionForm()

    return render(
        request,
        "predictions/stroke.html",
        {
            "form": form,
            "prediction": prediction
        }
    )