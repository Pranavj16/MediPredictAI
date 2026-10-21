from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from patients.models import Patient, PredictionRecord, RecordedMeasurement


class PredictionEndpointsTests(TestCase):
    """Tests for the 6 disease prediction views, form validation, and persistence"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="dr_ananya", password="Password123!")
        self.client.login(username="dr_ananya", password="Password123!")

    def test_diabetes_prediction_form_and_persistence(self):
        data = {
            "gender": "Female",
            "age": 45,
            "hypertension": 0,
            "heart_disease": 0,
            "smoking_history": "never",
            "bmi": 22.8,
            "HbA1c_level": 5.4,
            "blood_glucose_level": 92.0
        }
        res = self.client.post(reverse("diabetes_prediction"), data=data)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "XAI Calibrated")

        # Verify PredictionRecord was saved
        pred_record = PredictionRecord.objects.filter(condition="diabetes").first()
        self.assertIsNotNone(pred_record)
        self.assertEqual(pred_record.prediction, 0) # Normal risk

        # Verify biometric extraction into RecordedMeasurement
        patient = Patient.objects.filter(user=self.user).first()
        self.assertTrue(patient.measurements.filter(measurement_type="hba1c").exists())
        self.assertTrue(patient.measurements.filter(measurement_type="blood_glucose").exists())

    def test_heart_prediction_form_and_persistence(self):
        data = {
            "Age": 52,
            "Sex": "M",
            "ChestPainType": "ATA",
            "RestingBP": 125,
            "Cholesterol": 210,
            "FastingBS": 0,
            "RestingECG": "Normal",
            "MaxHR": 145,
            "ExerciseAngina": "N",
            "Oldpeak": 0.5,
            "ST_Slope": "Up"
        }
        res = self.client.post(reverse("heart_prediction"), data=data)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "XAI Calibrated")

        pred_record = PredictionRecord.objects.filter(condition="heart").first()
        self.assertIsNotNone(pred_record)
        self.assertEqual(pred_record.prediction, 0)

        patient = Patient.objects.filter(user=self.user).first()
        self.assertTrue(patient.measurements.filter(measurement_type="blood_pressure").exists())

    def test_kidney_prediction_get_and_post(self):
        res_get = self.client.get(reverse("kidney_prediction"))
        self.assertEqual(res_get.status_code, 200)

    def test_liver_prediction_get_and_post(self):
        res_get = self.client.get(reverse("liver_prediction"))
        self.assertEqual(res_get.status_code, 200)

    def test_parkinson_prediction_get_and_post(self):
        res_get = self.client.get(reverse("parkinson_prediction"))
        self.assertEqual(res_get.status_code, 200)

    def test_stroke_prediction_get_and_post(self):
        res_get = self.client.get(reverse("stroke_prediction"))
        self.assertEqual(res_get.status_code, 200)
