from django.urls import path
from . import views

urlpatterns = [
    # Unified NCD & Hypertension Screening
    path("screening/unified/", views.unified_screening, name="unified_screening"),
    path("screening/hypertension/", views.hypertension_screening, name="hypertension_screening"),

    # Health Records & Trends
    path("profile/", views.patient_profile, name="patient_profile"),
    path("profile/<str:patient_id>/", views.patient_profile, name="patient_profile_detail"),
    path("trends/", views.health_trends, name="health_trends"),
    path("trends/<str:patient_id>/", views.health_trends, name="health_trends_detail"),

    # Preventive Guidance & AI Assistant
    path("guidance/", views.preventive_guidance_view, name="preventive_guidance"),
    path("guidance/<str:patient_id>/", views.preventive_guidance_view, name="preventive_guidance_detail"),
    path("assistant/", views.ai_assistant_view, name="ai_assistant"),

    # Referrals, CHW Frontline Portal & Printables
    path("referrals/", views.referrals_and_followup, name="referrals_and_followup"),
    path("chw/", views.chw_portal, name="chw_portal"),
    path("summary/<int:session_id>/print/", views.printable_summary, name="printable_summary"),
]
