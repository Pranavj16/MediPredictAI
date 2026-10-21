from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from patients.models import (
    Patient, ScreeningSession, RecordedMeasurement,
    Referral, FollowUpTask, PredictionRecord
)
from accounts.permissions import get_user_role


@login_required(login_url="login")
def dashboard(request):
    """
    Main Clinician & User Portal Dashboard:
    Computes real metrics from the database, displays active clinical classifiers,
    and provides unified screening & triage entry points.
    """
    user_role = get_user_role(request.user)

    # Real database statistics
    total_patients = Patient.objects.count()
    total_screenings = ScreeningSession.objects.count()
    total_predictions = PredictionRecord.objects.count()
    pending_referrals = Referral.objects.filter(status="pending").count()
    scheduled_tasks = FollowUpTask.objects.filter(status="scheduled").count()

    # User-specific recent activity
    user_patient = Patient.objects.filter(user=request.user).first()
    recent_screenings = []
    recent_measurements = []
    if user_patient:
        recent_screenings = user_patient.screening_sessions.all()[:5]
        recent_measurements = user_patient.measurements.all()[:5]
    elif user_role in ['chw', 'clinician', 'admin']:
        recent_screenings = ScreeningSession.objects.all()[:5]
        recent_measurements = RecordedMeasurement.objects.all()[:5]

    return render(
        request,
        "dashboard/dashboard.html",
        {
            "total_patients": total_patients,
            "total_screenings": total_screenings,
            "total_predictions": total_predictions,
            "pending_referrals": pending_referrals,
            "scheduled_tasks": scheduled_tasks,
            "recent_screenings": recent_screenings,
            "recent_measurements": recent_measurements,
            "user_role": user_role
        }
    )


@login_required(login_url="login")
def operational_dashboard(request):
    """
    Operational Public Health Metrics Dashboard:
    Displays aggregated metrics with clearly defined denominators and no PII.
    """
    total_screened = Patient.objects.count()
    sessions_total = ScreeningSession.objects.count()

    completed_screenings = ScreeningSession.objects.filter(
        status__in=["routine_followup", "followup_completed"]
    ).count()
    incomplete_screenings = ScreeningSession.objects.filter(
        status="incomplete"
    ).count()
    requiring_followup = ScreeningSession.objects.filter(
        status__in=["assessment_recommended", "referral_pending", "further_review_required"]
    ).count()

    # Referrals
    total_referrals = Referral.objects.count()
    completed_referrals = Referral.objects.filter(status="completed").count()
    referral_completion_rate = (
        round((completed_referrals / total_referrals) * 100, 1)
        if total_referrals > 0 else 0.0
    )

    # Follow-ups
    total_tasks = FollowUpTask.objects.count()
    completed_tasks = FollowUpTask.objects.filter(status="completed").count()
    followup_completion_rate = (
        round((completed_tasks / total_tasks) * 100, 1)
        if total_tasks > 0 else 0.0
    )

    # Missing measurements frequency
    patients_with_bp = RecordedMeasurement.objects.filter(
        measurement_type="blood_pressure"
    ).values("patient").distinct().count()
    patients_with_glucose = RecordedMeasurement.objects.filter(
        measurement_type__in=["blood_glucose", "fasting_glucose", "hba1c"]
    ).values("patient").distinct().count()
    patients_with_bmi = RecordedMeasurement.objects.filter(
        measurement_type="bmi"
    ).values("patient").distinct().count()

    denom = total_screened or 1
    pct_missing_bp = round(max(0, (denom - patients_with_bp) / denom * 100), 1)
    pct_missing_glucose = round(max(0, (denom - patients_with_glucose) / denom * 100), 1)
    pct_missing_bmi = round(max(0, (denom - patients_with_bmi) / denom * 100), 1)

    return render(
        request,
        "dashboard/operational_dashboard.html",
        {
            "total_screened": total_screened,
            "sessions_total": sessions_total,
            "completed_screenings": completed_screenings,
            "incomplete_screenings": incomplete_screenings,
            "requiring_followup": requiring_followup,
            "total_referrals": total_referrals,
            "completed_referrals": completed_referrals,
            "referral_completion_rate": referral_completion_rate,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "followup_completion_rate": followup_completion_rate,
            "pct_missing_bp": pct_missing_bp,
            "pct_missing_glucose": pct_missing_glucose,
            "pct_missing_bmi": pct_missing_bmi,
        }
    )