from django.contrib import admin
from .models import (
    Patient, RecordedMeasurement, ScreeningSession,
    PredictionRecord, Referral, FollowUpTask, AuditEvent
)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_identifier', 'full_name', 'gender', 'age', 'phone_number', 'center', 'consent_given', 'created_at')
    search_fields = ('patient_identifier', 'full_name', 'phone_number', 'center')
    list_filter = ('gender', 'consent_given', 'center')


@admin.register(RecordedMeasurement)
class RecordedMeasurementAdmin(admin.ModelAdmin):
    list_display = ('patient', 'measurement_type', 'value_numeric', 'secondary_numeric', 'unit', 'context', 'source', 'measured_at')
    search_fields = ('patient__full_name', 'patient__patient_identifier')
    list_filter = ('measurement_type', 'source', 'context')


@admin.register(ScreeningSession)
class ScreeningSessionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'screening_type', 'status', 'conducted_by', 'created_at')
    search_fields = ('patient__full_name', 'patient__patient_identifier')
    list_filter = ('screening_type', 'status')


@admin.register(PredictionRecord)
class PredictionRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'condition', 'prediction', 'risk_score', 'confidence', 'created_at')
    search_fields = ('patient__full_name', 'patient__patient_identifier', 'condition')
    list_filter = ('condition', 'prediction')


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('patient', 'referred_to_facility', 'department', 'urgency', 'status', 'appointment_date', 'created_at')
    search_fields = ('patient__full_name', 'patient__patient_identifier', 'referred_to_facility')
    list_filter = ('urgency', 'status')


@admin.register(FollowUpTask)
class FollowUpTaskAdmin(admin.ModelAdmin):
    list_display = ('patient', 'task_type', 'scheduled_date', 'status', 'assigned_to', 'completed_at')
    search_fields = ('patient__full_name', 'patient__patient_identifier')
    list_filter = ('task_type', 'status', 'scheduled_date')


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'patient', 'action', 'ip_address')
    search_fields = ('user__username', 'patient__full_name', 'action', 'details')
    list_filter = ('action',)
    readonly_fields = ('timestamp', 'user', 'patient', 'action', 'details', 'ip_address')
