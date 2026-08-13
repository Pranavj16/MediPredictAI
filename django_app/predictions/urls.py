from django.urls import path
from . import views

urlpatterns = [

    path(
        "diabetes/",
        views.diabetes_prediction,
        name="diabetes_prediction"
    ),

    path(
        "heart/",
        views.heart_prediction,
        name="heart_prediction"
    ),

    path(
        "kidney/",
        views.kidney_prediction,
        name="kidney_prediction"
    ),

    path(
    "liver/",
    views.liver_prediction,
    name="liver_prediction"
),
    path(
    "parkinson/",
    views.parkinson_prediction,
    name="parkinson_prediction"
),
path(
    "stroke/",
    views.stroke_prediction,
    name="stroke_prediction"
),

]