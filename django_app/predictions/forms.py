from django import forms

class DiabetesPredictionForm(forms.Form):
    gender = forms.ChoiceField(
        choices=[("Male", "Male"), ("Female", "Female")]
    )

    age = forms.FloatField()

    hypertension = forms.ChoiceField(
        choices=[(0, "No"), (1, "Yes")]
    )

    heart_disease = forms.ChoiceField(
        choices=[(0, "No"), (1, "Yes")]
    )

    smoking_history = forms.ChoiceField(
        choices=[
            ("never", "Never"),
            ("former", "Former"),
            ("current", "Current"),
            ("No Info", "No Info"),
            ("ever", "Ever"),
            ("not current", "Not Current")
        ]
    )

    bmi = forms.FloatField()

    HbA1c_level = forms.FloatField()

    blood_glucose_level = forms.FloatField()

class HeartPredictionForm(forms.Form):

    Age = forms.IntegerField(
        label="Age"
    )

    Sex = forms.ChoiceField(
        choices=[
            ("M", "Male"),
            ("F", "Female")
        ]
    )

    ChestPainType = forms.ChoiceField(
        choices=[
            ("ATA", "Atypical Angina"),
            ("NAP", "Non-Anginal Pain"),
            ("ASY", "Asymptomatic"),
            ("TA", "Typical Angina")
        ]
    )

    RestingBP = forms.IntegerField(
        label="Resting Blood Pressure"
    )

    Cholesterol = forms.IntegerField()

    FastingBS = forms.ChoiceField(
        choices=[
            (0, "No"),
            (1, "Yes")
        ]
    )

    RestingECG = forms.ChoiceField(
        choices=[
            ("Normal", "Normal"),
            ("ST", "ST"),
            ("LVH", "LVH")
        ]
    )

    MaxHR = forms.IntegerField(
        label="Maximum Heart Rate"
    )

    ExerciseAngina = forms.ChoiceField(
        choices=[
            ("N", "No"),
            ("Y", "Yes")
        ]
    )

    Oldpeak = forms.FloatField()

    ST_Slope = forms.ChoiceField(
        choices=[
            ("Up", "Up"),
            ("Flat", "Flat"),
            ("Down", "Down")
        ]
    )
    
class KidneyPredictionForm(forms.Form):

    age = forms.FloatField(label="Age")

    bp = forms.FloatField(label="Blood Pressure")

    sg = forms.FloatField(label="Specific Gravity")

    al = forms.FloatField(label="Albumin")

    su = forms.FloatField(label="Sugar")

    rbc = forms.ChoiceField(
        choices=[
            ("normal", "Normal"),
            ("abnormal", "Abnormal")
        ]
    )

    pc = forms.ChoiceField(
        choices=[
            ("normal", "Normal"),
            ("abnormal", "Abnormal")
        ]
    )

    pcc = forms.ChoiceField(
        choices=[
            ("present", "Present"),
            ("notpresent", "Not Present")
        ]
    )

    ba = forms.ChoiceField(
        choices=[
            ("present", "Present"),
            ("notpresent", "Not Present")
        ]
    )

    bgr = forms.FloatField(label="Blood Glucose Random")

    bu = forms.FloatField(label="Blood Urea")

    sc = forms.FloatField(label="Serum Creatinine")

    sod = forms.FloatField(label="Sodium")

    pot = forms.FloatField(label="Potassium")

    hemo = forms.FloatField(label="Hemoglobin")

    pcv = forms.FloatField(label="Packed Cell Volume")

    wc = forms.FloatField(label="White Blood Cell Count")

    rc = forms.FloatField(label="Red Blood Cell Count")

    htn = forms.ChoiceField(
        choices=[
            ("yes", "Yes"),
            ("no", "No")
        ]
    )

    dm = forms.ChoiceField(
        choices=[
            ("yes", "Yes"),
            ("no", "No")
        ]
    )

    cad = forms.ChoiceField(
        choices=[
            ("yes", "Yes"),
            ("no", "No")
        ]
    )

    appet = forms.ChoiceField(
        choices=[
            ("good", "Good"),
            ("poor", "Poor")
        ]
    )

    pe = forms.ChoiceField(
        choices=[
            ("yes", "Yes"),
            ("no", "No")
        ]
    )

    ane = forms.ChoiceField(
        choices=[
            ("yes", "Yes"),
            ("no", "No")
        ]
    )

class LiverPredictionForm(forms.Form):

    age = forms.IntegerField(label="Age")

    gender = forms.ChoiceField(
        choices=[
            (1, "Male"),
            (0, "Female")
        ]
    )

    tot_bilirubin = forms.FloatField(label="Total Bilirubin")

    direct_bilirubin = forms.FloatField(label="Direct Bilirubin")

    tot_proteins = forms.FloatField(label="Total Proteins")

    albumin = forms.FloatField(label="Albumin")

    ag_ratio = forms.FloatField(label="Albumin/Globulin Ratio")

    sgpt = forms.FloatField(label="SGPT (ALT)")

    sgot = forms.FloatField(label="SGOT (AST)")

    alkphos = forms.FloatField(label="Alkaline Phosphotase")

class ParkinsonPredictionForm(forms.Form):

    MDVP_Fo_Hz = forms.FloatField(label="Average Vocal Frequency (Fo)")
    MDVP_Fhi_Hz = forms.FloatField(label="Maximum Vocal Frequency (Fhi)")
    MDVP_Flo_Hz = forms.FloatField(label="Minimum Vocal Frequency (Flo)")

    MDVP_Jitter_percent = forms.FloatField(label="Jitter (%)")
    MDVP_Jitter_Abs = forms.FloatField(label="Jitter (Absolute)")
    MDVP_RAP = forms.FloatField(label="RAP")
    MDVP_PPQ = forms.FloatField(label="PPQ")
    Jitter_DDP = forms.FloatField(label="DDP")

    MDVP_Shimmer = forms.FloatField(label="Shimmer")
    MDVP_Shimmer_dB = forms.FloatField(label="Shimmer (dB)")
    Shimmer_APQ3 = forms.FloatField(label="APQ3")
    Shimmer_APQ5 = forms.FloatField(label="APQ5")
    MDVP_APQ = forms.FloatField(label="APQ")
    Shimmer_DDA = forms.FloatField(label="DDA")

    NHR = forms.FloatField(label="NHR")
    HNR = forms.FloatField(label="HNR")

    RPDE = forms.FloatField(label="RPDE")
    DFA = forms.FloatField(label="DFA")
    spread1 = forms.FloatField(label="Spread 1")
    spread2 = forms.FloatField(label="Spread 2")
    D2 = forms.FloatField(label="D2")
    PPE = forms.FloatField(label="PPE")

class StrokePredictionForm(forms.Form):

    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    YES_NO = [
        (0, "No"),
        (1, "Yes"),
    ]

    MARRIED = [
        ("Yes", "Yes"),
        ("No", "No"),
    ]

    WORK = [
        ("Private", "Private"),
        ("Self-employed", "Self-employed"),
        ("Govt_job", "Government Job"),
        ("children", "Children"),
        ("Never_worked", "Never Worked"),
    ]

    RESIDENCE = [
        ("Urban", "Urban"),
        ("Rural", "Rural"),
    ]

    SMOKING = [
        ("never smoked", "Never Smoked"),
        ("formerly smoked", "Formerly Smoked"),
        ("smokes", "Smokes"),
        ("Unknown", "Unknown"),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES)

    age = forms.FloatField()

    hypertension = forms.TypedChoiceField(
        choices=YES_NO,
        coerce=int
    )

    heart_disease = forms.TypedChoiceField(
        choices=YES_NO,
        coerce=int
    )

    ever_married = forms.ChoiceField(choices=MARRIED)

    work_type = forms.ChoiceField(choices=WORK)

    Residence_type = forms.ChoiceField(choices=RESIDENCE)

    avg_glucose_level = forms.FloatField()

    bmi = forms.FloatField()

    smoking_status = forms.ChoiceField(choices=SMOKING)