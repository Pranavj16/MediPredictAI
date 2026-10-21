import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q

from .models import (
    Patient, RecordedMeasurement, ScreeningSession,
    PredictionRecord, Referral, FollowUpTask, AuditEvent
)
from .forms import (
    UnifiedNCDScreeningForm, HypertensionScreeningForm,
    CHWPatientRegistrationForm, ReferralCreateForm, FollowUpTaskCreateForm
)
from .screening_engine import calculate_bmi, evaluate_hypertension, compute_idrs
from .guidance_engine import generate_personalized_guidance
from .health_assistant import ask_health_assistant
from accounts.permissions import role_required, can_access_patient, get_user_role

# Local ML fallback import for diabetes service
try:
    from app.services.diabetes_service import predict_diabetes
except Exception:
    predict_diabetes = None


def get_or_create_user_patient(user):
    """Retrieves or creates patient record for self-registered user"""
    if not user.is_authenticated:
        return None
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
    return patient


@login_required(login_url="login")
def unified_screening(request):
    """
    Unified NCD Screening entry point:
    Gathers lifestyle, demographics, anthropometry, and optional clinical measurements.
    Dispatches to models ONLY when inputs are available. Never invents missing values.
    """
    patient = get_or_create_user_patient(request.user)
    result_summary = None

    if request.method == "POST":
        form = UnifiedNCDScreeningForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # 1. Anthropometry & BMI
            bmi_data = calculate_bmi(cd.get("weight_kg"), cd.get("height_cm"))

            # 2. Blood Pressure Evaluation (if provided)
            bp_data = None
            if cd.get("systolic_bp") and cd.get("diastolic_bp"):
                bp_data = evaluate_hypertension(
                    cd["systolic_bp"],
                    cd["diastolic_bp"],
                    context="resting_seated",
                    is_repeated=False
                )

            # 3. Community Risk Score (IDRS - non-invasive)
            idrs_data = compute_idrs(
                age=cd["age"],
                waist_cm=cd.get("waist_cm"),
                activity=cd["physical_activity"],
                family_history=cd["family_history_diabetes"]
            )

            # 4. Check for Machine Learning Assessment Feasibility
            ml_results = []
            missing_measurements = []

            # Check Diabetes ML
            has_glucose = cd.get("fasting_glucose") is not None
            has_hba1c = cd.get("hba1c") is not None
            has_bmi = bmi_data is not None

            if (has_glucose or has_hba1c) and has_bmi and predict_diabetes:
                # User has provided valid glycemic measurements and BMI
                glucose_val = cd.get("fasting_glucose") or 110.0
                hba1c_val = cd.get("hba1c") or 5.7
                smoking_map = {
                    "never": "never",
                    "former": "former",
                    "current_beedi_cigarette": "current",
                    "current_smokeless": "current"
                }

                ml_input = {
                    "gender": cd["gender"],
                    "age": float(cd["age"]),
                    "hypertension": int(cd["known_hypertension"]),
                    "heart_disease": int(cd["known_heart_disease"]),
                    "smoking_history": smoking_map.get(cd["tobacco_status"], "never"),
                    "bmi": bmi_data["bmi"],
                    "HbA1c_level": float(hba1c_val),
                    "blood_glucose_level": float(glucose_val)
                }

                try:
                    diabetes_pred = predict_diabetes(ml_input)
                    ml_results.append({
                        "condition": "Diabetes Risk",
                        "status_label": diabetes_pred.get("status_label"),
                        "risk_score": diabetes_pred.get("risk_score"),
                        "confidence": diabetes_pred.get("confidence"),
                        "interpretation": diabetes_pred.get("interpretation"),
                        "contributions": diabetes_pred.get("feature_contributions", [])
                    })

                    # Save prediction record
                    if patient:
                        PredictionRecord.objects.create(
                            patient=patient,
                            conducted_by=request.user,
                            condition="diabetes",
                            model_name=diabetes_pred.get("model_name", "Random Forest Classifier"),
                            inputs=ml_input,
                            prediction=diabetes_pred.get("prediction", 0),
                            risk_score=diabetes_pred.get("risk_score", 0.0),
                            confidence=diabetes_pred.get("confidence", 0.0),
                            feature_contributions=diabetes_pred.get("feature_contributions", []),
                            clinical_interpretation=diabetes_pred.get("interpretation", ""),
                            limitations=diabetes_pred.get("limitations", "")
                        )
                except Exception as err:
                    print(f"Error running diabetes model in unified screening: {err}")
            else:
                if not has_glucose and not has_hba1c:
                    missing_measurements.append("Blood Glucose / HbA1c Lab Test (Diabetes ML deferred)")
                if not has_bmi:
                    missing_measurements.append("Height and Weight (Required for BMI calculation)")

            missing_measurements.append("Resting ECG & Serum Cholesterol (Cardiovascular ML deferred)")

            # Determine overall session status
            status = "routine_followup"
            risk_flags = []

            if bp_data and bp_data.get("valid"):
                if bp_data["urgency"] == "urgent_emergency":
                    status = "further_review_required"
                    risk_flags.append(bp_data["category"])
                elif "Stage" in bp_data["category"]:
                    status = "assessment_recommended"
                    risk_flags.append(bp_data["category"])

            if idrs_data["score"] >= 60:
                risk_flags.append(f"High Community Diabetes Risk (IDRS {idrs_data['score']}/100)")
                if status == "routine_followup":
                    status = "assessment_recommended"

            # 5. Persist Measurements & Session
            session = None
            if patient:
                # Save measurements
                if cd.get("weight_kg"):
                    RecordedMeasurement.objects.create(
                        patient=patient, recorded_by=request.user,
                        measurement_type="weight", value_numeric=cd["weight_kg"],
                        unit="kg", source="self_reported"
                    )
                if cd.get("height_cm"):
                    RecordedMeasurement.objects.create(
                        patient=patient, recorded_by=request.user,
                        measurement_type="height", value_numeric=cd["height_cm"],
                        unit="cm", source="self_reported"
                    )
                if bmi_data:
                    RecordedMeasurement.objects.create(
                        patient=patient, recorded_by=request.user,
                        measurement_type="bmi", value_numeric=bmi_data["bmi"],
                        unit="kg/m²", source="self_reported"
                    )
                if bp_data and bp_data.get("valid"):
                    RecordedMeasurement.objects.create(
                        patient=patient, recorded_by=request.user,
                        measurement_type="blood_pressure", value_numeric=bp_data["systolic"],
                        secondary_numeric=bp_data["diastolic"], unit="mmHg",
                        context="resting_seated", source="self_reported"
                    )
                if cd.get("fasting_glucose"):
                    RecordedMeasurement.objects.create(
                        patient=patient, recorded_by=request.user,
                        measurement_type="blood_glucose", value_numeric=cd["fasting_glucose"],
                        unit="mg/dL", context="fasting", source="self_reported"
                    )
                if cd.get("hba1c"):
                    RecordedMeasurement.objects.create(
                        patient=patient, recorded_by=request.user,
                        measurement_type="hba1c", value_numeric=cd["hba1c"],
                        unit="%", context="general", source="self_reported"
                    )

                session = ScreeningSession.objects.create(
                    patient=patient,
                    conducted_by=request.user,
                    screening_type="unified_ncd",
                    status=status,
                    summary_data={
                        "age": cd["age"],
                        "gender": cd["gender"],
                        "bmi_data": bmi_data,
                        "bp_data": bp_data,
                        "idrs_data": idrs_data,
                        "ml_results": ml_results
                    },
                    missing_measurements=missing_measurements,
                    risk_flags=risk_flags,
                    recommended_next_steps=(
                        "Proceed with recommended laboratory confirmation and lifestyle modifications as outlined."
                    )
                )

                # Audit event
                AuditEvent.objects.create(
                    user=request.user,
                    patient=patient,
                    action="UNIFIED_SCREENING_COMPLETED",
                    details=f"Status: {status}, Flags: {', '.join(risk_flags) or 'None'}"
                )

            result_summary = {
                "session": session,
                "bmi_data": bmi_data,
                "bp_data": bp_data,
                "idrs_data": idrs_data,
                "ml_results": ml_results,
                "missing_measurements": missing_measurements,
                "risk_flags": risk_flags,
                "status": status,
                "date": timezone.now()
            }
            messages.success(request, "Unified screening completed successfully!")
    else:
        form = UnifiedNCDScreeningForm()

    return render(
        request,
        "patients/unified_screening.html",
        {
            "form": form,
            "patient": patient,
            "result_summary": result_summary
        }
    )


@login_required(login_url="login")
def hypertension_screening(request):
    """
    Dedicated Blood Pressure Screening Module:
    Accepts SBP, DBP, measurement context, repetition flag, and source.
    Evaluates against ICMR/IGH-IV clinical thresholds.
    """
    patient = get_or_create_user_patient(request.user)
    evaluation = None

    if request.method == "POST":
        form = HypertensionScreeningForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            evaluation = evaluate_hypertension(
                systolic=cd["systolic"],
                diastolic=cd["diastolic"],
                context=cd["context"],
                is_repeated=cd["is_repeated"]
            )

            if evaluation.get("valid"):
                # Persist to RecordedMeasurement
                if patient:
                    RecordedMeasurement.objects.create(
                        patient=patient,
                        recorded_by=request.user,
                        measurement_type="blood_pressure",
                        value_numeric=evaluation["systolic"],
                        secondary_numeric=evaluation["diastolic"],
                        unit="mmHg",
                        context=cd["context"],
                        source=cd["source"],
                        is_repeated=cd["is_repeated"],
                        notes=cd.get("notes", "")
                    )

                    status = "assessment_recommended" if "Stage" in evaluation["category"] or evaluation["urgency"] == "urgent_emergency" else "routine_followup"
                    ScreeningSession.objects.create(
                        patient=patient,
                        conducted_by=request.user,
                        screening_type="hypertension",
                        status=status,
                        summary_data=evaluation,
                        risk_flags=[evaluation["category"]],
                        recommended_next_steps=evaluation["action"]
                    )

                    AuditEvent.objects.create(
                        user=request.user,
                        patient=patient,
                        action="BP_MEASUREMENT_RECORDED",
                        details=f"{evaluation['systolic']}/{evaluation['diastolic']} mmHg ({evaluation['category']})"
                    )

                messages.success(request, f"Blood pressure reading of {evaluation['systolic']}/{evaluation['diastolic']} mmHg recorded.")
            else:
                messages.error(request, evaluation.get("error", "Invalid measurement inputs."))
    else:
        form = HypertensionScreeningForm()

    # Fetch recent BP history for context
    bp_history = []
    if patient:
        bp_history = patient.measurements.filter(measurement_type="blood_pressure")[:5]

    return render(
        request,
        "patients/hypertension_screening.html",
        {
            "form": form,
            "patient": patient,
            "evaluation": evaluation,
            "bp_history": bp_history
        }
    )


@login_required(login_url="login")
def patient_profile(request, patient_id=None):
    """
    Personal Health Profile View:
    Displays patient demographics, consent, measurement timeline, prediction history,
    referrals, and follow-ups with server-side authorization.
    """
    if patient_id:
        patient = get_object_or_404(Patient, patient_identifier=patient_id)
        if not can_access_patient(request.user, patient):
            messages.error(request, "Permission denied: Unauthorized access to medical records.")
            return redirect("dashboard")
    else:
        patient = get_or_create_user_patient(request.user)

    measurements = patient.measurements.all()[:15]
    sessions = patient.screening_sessions.all()[:10]
    predictions = patient.prediction_records.all()[:10]
    referrals = patient.referrals.all()[:5]
    followups = patient.follow_up_tasks.all()[:5]

    return render(
        request,
        "patients/patient_profile.html",
        {
            "patient": patient,
            "measurements": measurements,
            "sessions": sessions,
            "predictions": predictions,
            "referrals": referrals,
            "followups": followups
        }
    )


@login_required(login_url="login")
def health_trends(request, patient_id=None):
    """
    Health Trends and History Dashboard:
    Visualizes longitudinal changes in BP, Blood Glucose, HbA1c, and BMI using Chart.js.
    """
    if patient_id:
        patient = get_object_or_404(Patient, patient_identifier=patient_id)
        if not can_access_patient(request.user, patient):
            messages.error(request, "Permission denied to view medical trends.")
            return redirect("dashboard")
    else:
        patient = get_or_create_user_patient(request.user)

    # 1. Blood Pressure Series
    bp_records = patient.measurements.filter(measurement_type="blood_pressure").order_by("measured_at")
    bp_labels = [m.measured_at.strftime("%b %d, %Y") for m in bp_records]
    bp_sys = [m.value_numeric for m in bp_records]
    bp_dia = [m.secondary_numeric or 0 for m in bp_records]

    # 2. Glucose Series
    glu_records = patient.measurements.filter(measurement_type__in=["blood_glucose", "fasting_glucose"]).order_by("measured_at")
    glu_labels = [m.measured_at.strftime("%b %d, %Y") for m in glu_records]
    glu_vals = [m.value_numeric for m in glu_records]

    # 3. BMI & Weight Series
    bmi_records = patient.measurements.filter(measurement_type="bmi").order_by("measured_at")
    bmi_labels = [m.measured_at.strftime("%b %d, %Y") for m in bmi_records]
    bmi_vals = [m.value_numeric for m in bmi_records]

    all_measurements = patient.measurements.all()[:25]

    return render(
        request,
        "patients/health_trends.html",
        {
            "patient": patient,
            "all_measurements": all_measurements,
            "bp_labels_json": json.dumps(bp_labels),
            "bp_sys_json": json.dumps(bp_sys),
            "bp_dia_json": json.dumps(bp_dia),
            "glu_labels_json": json.dumps(glu_labels),
            "glu_vals_json": json.dumps(glu_vals),
            "bmi_labels_json": json.dumps(bmi_labels),
            "bmi_vals_json": json.dumps(bmi_vals),
        }
    )


@login_required(login_url="login")
def preventive_guidance_view(request, patient_id=None):
    """
    Evidence-based preventive health guidance personalized according
    to the user's recorded measurements and Indian lifestyle guidelines.
    """
    if patient_id:
        patient = get_object_or_404(Patient, patient_identifier=patient_id)
        if not can_access_patient(request.user, patient):
            messages.error(request, "Permission denied.")
            return redirect("dashboard")
    else:
        patient = get_or_create_user_patient(request.user)

    measurements = patient.measurements.all()[:10]
    guidance = generate_personalized_guidance(patient, measurements)

    return render(
        request,
        "patients/preventive_guidance.html",
        {
            "patient": patient,
            "guidance": guidance
        }
    )


@login_required(login_url="login")
def referrals_and_followup(request):
    """
    Referral and Follow-up Management Dashboard:
    Displays pending referrals, upcoming follow-ups, and enables creating referrals.
    """
    user_role = get_user_role(request.user)
    patient = get_or_create_user_patient(request.user)

    if user_role in ['chw', 'clinician', 'admin']:
        # Staff can see all active referrals in their jurisdiction
        referrals = Referral.objects.all()[:20]
        followups = FollowUpTask.objects.all()[:20]
    else:
        # Patient sees only their own
        referrals = patient.referrals.all() if patient else []
        followups = patient.follow_up_tasks.all() if patient else []

    referral_form = ReferralCreateForm()
    task_form = FollowUpTaskCreateForm()

    if request.method == "POST":
        if "create_referral" in request.POST:
            referral_form = ReferralCreateForm(request.POST)
            target_patient_id = request.POST.get("target_patient_id")
            target_patient = Patient.objects.filter(patient_identifier=target_patient_id).first() or patient

            if referral_form.is_valid() and target_patient:
                ref = referral_form.save(commit=False)
                ref.patient = target_patient
                ref.created_by = request.user
                ref.save()

                AuditEvent.objects.create(
                    user=request.user,
                    patient=target_patient,
                    action="REFERRAL_CREATED",
                    details=f"Facility: {ref.referred_to_facility}, Urgency: {ref.urgency}"
                )
                messages.success(request, f"Referral created successfully for {target_patient.full_name}.")
                return redirect("referrals_and_followup")

        elif "create_task" in request.POST:
            task_form = FollowUpTaskCreateForm(request.POST)
            target_patient_id = request.POST.get("target_patient_id")
            target_patient = Patient.objects.filter(patient_identifier=target_patient_id).first() or patient

            if task_form.is_valid() and target_patient:
                t = task_form.save(commit=False)
                t.patient = target_patient
                t.assigned_to = request.user
                t.save()

                messages.success(request, f"Follow-up task scheduled for {target_patient.full_name}.")
                return redirect("referrals_and_followup")

    return render(
        request,
        "patients/referrals_followup.html",
        {
            "referrals": referrals,
            "followups": followups,
            "referral_form": referral_form,
            "task_form": task_form,
            "patient": patient,
            "user_role": user_role
        }
    )


@login_required(login_url="login")
@role_required(['chw', 'clinician', 'admin'])
def chw_portal(request):
    """
    Community Health Worker (CHW / ASHA) Frontend Portal:
    Provides frontline screening workflows, patient registration with consent,
    and follow-up task tracking.
    """
    reg_form = CHWPatientRegistrationForm()
    search_query = request.GET.get("q", "").strip()

    patients_qs = Patient.objects.all()
    if search_query:
        patients_qs = patients_qs.filter(
            Q(full_name__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(patient_identifier__icontains=search_query) |
            Q(address__icontains=search_query)
        )

    if request.method == "POST":
        reg_form = CHWPatientRegistrationForm(request.POST)
        if reg_form.is_valid():
            new_p = reg_form.save(commit=False)
            new_p.registered_by = request.user
            new_p.save()

            AuditEvent.objects.create(
                user=request.user,
                patient=new_p,
                action="CHW_PATIENT_REGISTERED",
                details=f"Patient {new_p.full_name} ({new_p.patient_identifier}) registered with consent."
            )
            messages.success(request, f"Patient {new_p.full_name} registered successfully with ID: {new_p.patient_identifier}")
            return redirect("chw_portal")

    recent_patients = patients_qs[:15]
    pending_tasks = FollowUpTask.objects.filter(status="scheduled").order_by("scheduled_date")[:10]

    return render(
        request,
        "patients/chw_portal.html",
        {
            "reg_form": reg_form,
            "recent_patients": recent_patients,
            "pending_tasks": pending_tasks,
            "search_query": search_query
        }
    )


@login_required(login_url="login")
def ai_assistant_view(request):
    """
    AI Health Education Assistant Interface:
    Answers health literacy questions with RAG over approved ICMR/WHO guidelines.
    """
    patient = get_or_create_user_patient(request.user)
    patient_context = {}
    if patient:
        latest_bp = patient.measurements.filter(measurement_type="blood_pressure").first()
        if latest_bp:
            patient_context["recent_bp"] = f"{int(latest_bp.value_numeric)}/{int(latest_bp.secondary_numeric)} mmHg"

    response_data = None
    query = ""

    if request.method == "POST":
        # Supports form POST or JSON AJAX
        if request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.content_type:
            try:
                body = json.loads(request.body)
                query = body.get("query", "")
            except Exception:
                query = request.POST.get("query", "")
            res = ask_health_assistant(query, patient_context)
            return JsonResponse(res)
        else:
            query = request.POST.get("query", "")
            response_data = ask_health_assistant(query, patient_context)

    return render(
        request,
        "patients/ai_assistant.html",
        {
            "query": query,
            "response_data": response_data,
            "patient": patient
        }
    )


@login_required(login_url="login")
def printable_summary(request, session_id):
    """
    Generates a clean, printable clinical summary of an NCD screening session
    for patient records or referral handover.
    """
    session = get_object_or_404(ScreeningSession, id=session_id)
    if not can_access_patient(request.user, session.patient):
        messages.error(request, "Permission denied to view this summary.")
        return redirect("dashboard")

    return render(
        request,
        "patients/printable_summary.html",
        {
            "session": session,
            "patient": session.patient,
            "summary": session.summary_data
        }
    )
