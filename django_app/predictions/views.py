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


def get_prediction_result(endpoint_name, data, fallback_func):
    """
    Attempts to call FastAPI microservice on ports 8001 or 8000.
    Falls back to calling local ML prediction service if microservice is offline.
    """
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