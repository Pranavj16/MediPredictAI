import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


def generate_patient_id():
    now = timezone.now()
    return f"MP-{now.year}{now.month:02d}-{uuid.uuid4().hex[:6].upper()}"


class Patient(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    patient_identifier = models.CharField(
        max_length=32,
        unique=True,
        default=generate_patient_id,
        db_index=True
    )
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patient_record',
        help_text="Associated auth account if user registered as patient"
    )
    registered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_patients',
        help_text="CHW, Clinician, or staff member who registered the patient"
    )
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True, help_text="Village, Ward, or Town")
    center = models.CharField(max_length=150, blank=True, null=True, help_text="Local Sub-Center, PHC, or Health Post")

    # Consent Tracking
    consent_given = models.BooleanField(
        default=True,
        help_text="Informed consent provided for digital health screening and follow-up"
    )
    consent_date = models.DateTimeField(default=timezone.now)
    consent_notes = models.TextField(blank=True, null=True, help_text="Specific patient preferences or guardian consent")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.patient_identifier})"

    def save(self, *args, **kwargs):
        if not self.patient_identifier:
            self.patient_identifier = generate_patient_id()
        super().save(*args, **kwargs)


class RecordedMeasurement(models.Model):
    MEASUREMENT_TYPES = [
        ('blood_pressure', 'Blood Pressure (Systolic / Diastolic)'),
        ('blood_glucose', 'Blood Glucose (mg/dL)'),
        ('hba1c', 'Glycated Hemoglobin HbA1c (%)'),
        ('weight', 'Weight (kg)'),
        ('height', 'Height (cm)'),
        ('bmi', 'Body Mass Index (kg/m²)'),
        ('total_cholesterol', 'Total Cholesterol (mg/dL)'),
        ('serum_creatinine', 'Serum Creatinine (mg/dL)'),
        ('bilirubin', 'Total Bilirubin (mg/dL)'),
    ]

    SOURCE_CHOICES = [
        ('self_reported', 'Self-Reported by Patient'),
        ('chw_digital_cuff', 'Community Health Worker (Digital Cuff)'),
        ('chw_manual_sphygmomanometer', 'Community Health Worker (Aneroid / Manual)'),
        ('clinic_lab', 'Primary Health Centre / Clinic Laboratory'),
        ('hospital_record', 'Hospital Discharge / Clinical Report'),
    ]

    CONTEXT_CHOICES = [
        ('resting_seated', 'Resting Seated (Standard)'),
        ('resting_supine', 'Resting Supine (Lying Down)'),
        ('standing', 'Standing'),
        ('fasting', 'Fasting (>= 8 hours)'),
        ('postprandial', 'Post-Prandial (2 hours post-meal)'),
        ('random', 'Random (Non-fasting)'),
        ('general', 'General Clinical Context'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='measurements')
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    measurement_type = models.CharField(max_length=40, choices=MEASUREMENT_TYPES, db_index=True)
    value_numeric = models.FloatField(help_text="Primary value e.g. Systolic BP, Glucose, Weight")
    secondary_numeric = models.FloatField(
        null=True,
        blank=True,
        help_text="Secondary value e.g. Diastolic BP for blood pressure"
    )
    unit = models.CharField(max_length=20)
    context = models.CharField(max_length=30, choices=CONTEXT_CHOICES, default='general')
    source = models.CharField(max_length=40, choices=SOURCE_CHOICES, default='self_reported')
    is_repeated = models.BooleanField(
        default=False,
        help_text="Indicates if this measurement was repeated after rest"
    )
    measured_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-measured_at']

    def __str__(self):
        if self.measurement_type == 'blood_pressure' and self.secondary_numeric:
            return f"BP {int(self.value_numeric)}/{int(self.secondary_numeric)} {self.unit} for {self.patient.full_name}"
        return f"{self.get_measurement_type_display()}: {self.value_numeric} {self.unit} for {self.patient.full_name}"


class ScreeningSession(models.Model):
    SCREENING_TYPES = [
        ('unified_ncd', 'Unified NCD Screening (Diabetes, CVD, HTN)'),
        ('hypertension', 'Dedicated Blood Pressure Screening'),
        ('disease_prediction', 'Specific Condition ML Diagnostic'),
    ]

    STATUS_CHOICES = [
        ('incomplete', 'Screening Incomplete'),
        ('awaiting_measurement', 'Awaiting Laboratory / Measurement'),
        ('assessment_recommended', 'Further Assessment Recommended'),
        ('referral_pending', 'Referral Pending'),
        ('followup_scheduled', 'Follow-up Scheduled'),
        ('followup_completed', 'Follow-up Completed'),
        ('further_review_required', 'Further Clinical Review Required'),
        ('routine_followup', 'Routine Annual Follow-up'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='screening_sessions')
    conducted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    screening_type = models.CharField(max_length=40, choices=SCREENING_TYPES, default='unified_ncd')
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='incomplete', db_index=True)
    summary_data = models.JSONField(default=dict, blank=True)
    missing_measurements = models.JSONField(default=list, blank=True)
    risk_flags = models.JSONField(default=list, blank=True)
    recommended_next_steps = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_screening_type_display()} - {self.patient.full_name} ({self.get_status_display()})"


class PredictionRecord(models.Model):
    CONDITION_CHOICES = [
        ('diabetes', 'Diabetes Mellitus'),
        ('heart', 'Cardiovascular Disease'),
        ('kidney', 'Chronic Kidney Disease'),
        ('liver', 'Liver Disease'),
        ('parkinson', 'Parkinson Voice Screening'),
        ('stroke', 'Cerebral Stroke Risk'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prediction_records')
    screening_session = models.ForeignKey(
        ScreeningSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='predictions'
    )
    conducted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    condition = models.CharField(max_length=30, choices=CONDITION_CHOICES, db_index=True)
    model_name = models.CharField(max_length=80)
    inputs = models.JSONField(default=dict)
    prediction = models.IntegerField(help_text="0 = Low/Normal Risk, 1 = Elevated/High Risk")
    risk_score = models.FloatField(help_text="Estimated probability of positive class (%)")
    confidence = models.FloatField(help_text="Model confidence in output classification (%)")
    feature_contributions = models.JSONField(default=list, blank=True)
    clinical_interpretation = models.TextField()
    limitations = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status_label = "Elevated Risk" if self.prediction == 1 else "Low Risk"
        return f"{self.get_condition_display()} ({status_label}) - {self.patient.full_name}"


class Referral(models.Model):
    URGENCY_CHOICES = [
        ('routine', 'Routine (Within 2-4 weeks)'),
        ('priority', 'Priority Review (Within 3-7 days)'),
        ('urgent_emergency', 'Immediate Medical Review (Urgent / Red Flag)'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Referral Pending'),
        ('scheduled', 'Appointment Scheduled'),
        ('completed', 'Referral Completed'),
        ('cancelled', 'Cancelled'),
        ('lost_to_followup', 'Lost to Follow-up'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='referrals')
    screening_session = models.ForeignKey(
        ScreeningSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    referred_to_facility = models.CharField(
        max_length=200,
        help_text="e.g. Primary Health Centre (PHC), Community Health Centre (CHC), District Hospital"
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="e.g. General Medicine, NCD Clinic, Cardiology, Nephrology"
    )
    reason = models.TextField(help_text="Clinical justification and preliminary risk summary")
    urgency = models.CharField(max_length=30, choices=URGENCY_CHOICES, default='routine')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending', db_index=True)
    appointment_date = models.DateTimeField(null=True, blank=True)
    completion_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Referral to {self.referred_to_facility} for {self.patient.full_name} ({self.get_status_display()})"


class FollowUpTask(models.Model):
    TASK_TYPES = [
        ('bp_recheck', 'Blood Pressure Re-Check (Repeat Measurement)'),
        ('glucose_recheck', 'Fasting Blood Glucose / HbA1c Lab Confirmation'),
        ('referral_followup', 'Referral Appointment Adherence Check'),
        ('lifestyle_counseling', 'Preventive Diet & Exercise Counseling'),
        ('general_review', 'General Health & Symptom Review'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='follow_up_tasks')
    referral = models.ForeignKey(
        Referral,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='follow_up_tasks'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        help_text="CHW, ASHA, or health worker responsible for the follow-up"
    )
    task_type = models.CharField(max_length=40, choices=TASK_TYPES)
    scheduled_date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', db_index=True)
    notes = models.TextField(blank=True, null=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_date']

    def __str__(self):
        return f"{self.get_task_type_display()} for {self.patient.full_name} on {self.scheduled_date}"


class AuditEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=60, db_index=True)
    details = models.TextField()
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        username = self.user.username if self.user else "System/Anonymous"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {username} - {self.action}"
