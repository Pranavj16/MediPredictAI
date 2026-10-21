from django import forms
from .models import Patient, RecordedMeasurement, Referral, FollowUpTask


class UnifiedNCDScreeningForm(forms.Form):
    # Demographics & Patient Link
    full_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Patient Name (Optional if logged in)"})
    )
    age = forms.IntegerField(
        min_value=18,
        max_value=120,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Age in years (e.g. 45)"})
    )
    gender = forms.ChoiceField(
        choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
        widget=forms.Select(attrs={"class": "form-select"})
    )

    # Anthropometry (Optional - BMI computed only if both valid)
    height_cm = forms.FloatField(
        required=False,
        min_value=60.0,
        max_value=250.0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Height in cm (e.g. 165)"})
    )
    weight_kg = forms.FloatField(
        required=False,
        min_value=20.0,
        max_value=250.0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Weight in kg (e.g. 68)"})
    )
    waist_cm = forms.FloatField(
        required=False,
        min_value=40.0,
        max_value=180.0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Waist in cm (Optional)"})
    )

    # Lifestyle & Medical History
    physical_activity = forms.ChoiceField(
        choices=[
            ("sedentary", "Sedentary / Little to no exercise (< 60 min/week)"),
            ("moderate", "Moderate (Brisk walking/farming/cycling >= 150 min/week)"),
            ("vigorous", "Vigorous / Strenuous sports or manual labor")
        ],
        widget=forms.Select(attrs={"class": "form-select"})
    )
    tobacco_status = forms.ChoiceField(
        choices=[
            ("never", "Never used tobacco"),
            ("former", "Former user (Quit > 1 year ago)"),
            ("current_beedi_cigarette", "Current smoker (Beedi / Cigarette)"),
            ("current_smokeless", "Current smokeless tobacco (Gutka / Khaini / Zarda / Paan Masala)")
        ],
        widget=forms.Select(attrs={"class": "form-select"})
    )
    family_history_diabetes = forms.ChoiceField(
        choices=[
            ("none", "No biological parent with diabetes"),
            ("one", "One parent diagnosed with diabetes"),
            ("both", "Both parents diagnosed with diabetes")
        ],
        widget=forms.Select(attrs={"class": "form-select"})
    )
    known_hypertension = forms.ChoiceField(
        choices=[(0, "No previous hypertension diagnosis"), (1, "Yes, previously diagnosed with hypertension")],
        widget=forms.Select(attrs={"class": "form-select"})
    )
    known_heart_disease = forms.ChoiceField(
        choices=[(0, "No previous heart disease"), (1, "Yes, history of cardiovascular disease")],
        widget=forms.Select(attrs={"class": "form-select"})
    )

    # Optional Clinical Vitals (NOT required to screen)
    systolic_bp = forms.FloatField(
        required=False,
        min_value=60.0,
        max_value=280.0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Systolic BP mmHg (e.g. 125)"})
    )
    diastolic_bp = forms.FloatField(
        required=False,
        min_value=40.0,
        max_value=180.0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Diastolic BP mmHg (e.g. 82)"})
    )
    fasting_glucose = forms.FloatField(
        required=False,
        min_value=40.0,
        max_value=500.0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Fasting Blood Glucose mg/dL (Optional)"})
    )
    hba1c = forms.FloatField(
        required=False,
        min_value=3.5,
        max_value=18.0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "HbA1c % (Optional lab test)"})
    )


class HypertensionScreeningForm(forms.Form):
    systolic = forms.FloatField(
        min_value=60.0,
        max_value=300.0,
        label="Systolic Blood Pressure (mmHg)",
        widget=forms.NumberInput(attrs={"class": "form-control form-control-lg", "placeholder": "e.g. 128"})
    )
    diastolic = forms.FloatField(
        min_value=40.0,
        max_value=200.0,
        label="Diastolic Blood Pressure (mmHg)",
        widget=forms.NumberInput(attrs={"class": "form-control form-control-lg", "placeholder": "e.g. 84"})
    )
    context = forms.ChoiceField(
        choices=RecordedMeasurement.CONTEXT_CHOICES,
        initial="resting_seated",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    source = forms.ChoiceField(
        choices=RecordedMeasurement.SOURCE_CHOICES,
        initial="chw_digital_cuff",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    is_repeated = forms.BooleanField(
        required=False,
        initial=False,
        label="Repeated measurement after 5 minutes of quiet rest",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 2,
            "placeholder": "Clinical observations, cuff arm (Left/Right), patient symptoms, etc."
        })
    )


class CHWPatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'full_name',
            'gender',
            'age',
            'date_of_birth',
            'phone_number',
            'address',
            'center',
            'consent_given',
            'consent_notes'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Village / Ward / Street'}),
            'center': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assigned Health Sub-Centre / PHC'}),
            'consent_given': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'consent_notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Verbal / Written consent notes'}),
        }


class ReferralCreateForm(forms.ModelForm):
    class Meta:
        model = Referral
        fields = [
            'referred_to_facility',
            'department',
            'urgency',
            'reason',
            'appointment_date'
        ]
        widgets = {
            'referred_to_facility': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Primary Health Centre (PHC) Chandrapur'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. NCD Clinic / General Medicine'}),
            'urgency': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Clinical justification for referral...'}),
            'appointment_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class FollowUpTaskCreateForm(forms.ModelForm):
    class Meta:
        model = FollowUpTask
        fields = [
            'task_type',
            'scheduled_date',
            'notes'
        ]
        widgets = {
            'task_type': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Instructions for the health worker / patient...'}),
        }
