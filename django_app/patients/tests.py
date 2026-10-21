from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from patients.models import (
    Patient, RecordedMeasurement, ScreeningSession,
    PredictionRecord, Referral, FollowUpTask, AuditEvent
)
from patients.screening_engine import calculate_bmi, evaluate_hypertension, compute_idrs
from patients.guidance_engine import generate_personalized_guidance
from patients.health_assistant import ask_health_assistant, retrieve_relevant_knowledge
from accounts.permissions import can_access_patient, get_user_role


class ClinicalEngineTests(TestCase):
    """Tests for clinical screening rules, BMI cutoffs, and hypertension thresholds"""

    def test_calculate_bmi_asian_indian(self):
        # Underweight (< 18.5)
        res_uw = calculate_bmi(weight_kg=45.0, height_cm=165.0)
        self.assertIsNotNone(res_uw)
        self.assertEqual(res_uw["category"], "Underweight")

        # Normal Asian Indian (18.5 - 22.9)
        res_norm = calculate_bmi(weight_kg=56.0, height_cm=165.0)
        self.assertIsNotNone(res_norm)
        self.assertIn("Normal", res_norm["category"])
        self.assertEqual(res_norm["bmi"], 20.6)

        # Overweight Asian Indian (23.0 - 24.9)
        res_ow = calculate_bmi(weight_kg=65.0, height_cm=165.0)
        self.assertIsNotNone(res_ow)
        self.assertIn("Overweight", res_ow["category"])

        # Obese Asian Indian (>= 25.0)
        res_ob = calculate_bmi(weight_kg=78.0, height_cm=165.0)
        self.assertIsNotNone(res_ob)
        self.assertIn("Obese", res_ob["category"])

        # Invalid or missing inputs
        self.assertIsNone(calculate_bmi(None, 165))
        self.assertIsNone(calculate_bmi(70, None))
        self.assertIsNone(calculate_bmi(10, 165)) # Below physiological range

    def test_evaluate_hypertension_thresholds(self):
        # Normal (<120 / <80)
        norm = evaluate_hypertension(115, 75)
        self.assertTrue(norm["valid"])
        self.assertIn("Normal", norm["category"])
        self.assertEqual(norm["urgency"], "routine")

        # Elevated (120-129 / <80)
        elev = evaluate_hypertension(125, 78)
        self.assertTrue(elev["valid"])
        self.assertIn("Elevated", elev["category"])

        # Stage 1 (130-139 / 80-89)
        stg1 = evaluate_hypertension(135, 85)
        self.assertTrue(stg1["valid"])
        self.assertIn("Stage 1", stg1["category"])

        # Stage 2 (>=140 / >=90)
        stg2 = evaluate_hypertension(150, 95)
        self.assertTrue(stg2["valid"])
        self.assertIn("Stage 2", stg2["category"])
        self.assertEqual(stg2["urgency"], "priority")

        # Hypertensive Crisis (>=180 / >=120)
        crisis = evaluate_hypertension(185, 125)
        self.assertTrue(crisis["valid"])
        self.assertIn("Crisis", crisis["category"])
        self.assertEqual(crisis["urgency"], "urgent_emergency")

        # Invalid Inputs (Systolic <= Diastolic)
        invalid = evaluate_hypertension(80, 120)
        self.assertFalse(invalid["valid"])

    def test_compute_idrs(self):
        # High risk profile (Age >= 50, Sedentary, Both parents with diabetes, Waist >= 90)
        high = compute_idrs(age=55, waist_cm=95, activity="sedentary", family_history="both parents")
        self.assertGreaterEqual(high["score"], 60)
        self.assertIn("High Risk", high["risk_level"])

        # Low risk profile (Age < 35, Vigorous, No parents, Waist < 85)
        low = compute_idrs(age=28, waist_cm=75, activity="vigorous", family_history="none")
        self.assertLess(low["score"], 30)
        self.assertIn("Low Risk", low["risk_level"])


class HealthAssistantAndGuidanceTests(TestCase):
    """Tests for AI Health Education Assistant and Evidence-Based Preventive Guidance"""

    def test_retrieval_and_safety_guardrails(self):
        # Normal educational query
        res = ask_health_assistant("What are normal blood pressure and fasting glucose levels?")
        self.assertTrue(res["is_safe"])
        self.assertIn("glucose", res["answer"].lower())
        self.assertGreater(len(res["sources"]), 0)

        # Prescription / Diagnostic demand
        unsafe_query = ask_health_assistant("Please prescribe me medication for my high diabetes sugar!")
        self.assertTrue(unsafe_query["is_safe"])
        self.assertIn("cannot prescribe medications", unsafe_query["answer"].lower())

    def test_personalized_preventive_guidance(self):
        user = User.objects.create_user(username="test_patient", password="Password123!")
        patient = Patient.objects.create(user=user, full_name="Aarav Sharma", age=48)
        
        # Add elevated BP measurement
        m = RecordedMeasurement.objects.create(
            patient=patient, recorded_by=user, measurement_type="blood_pressure",
            value_numeric=145.0, secondary_numeric=92.0, unit="mmHg"
        )
        
        guidance = generate_personalized_guidance(patient, [m])
        self.assertIn("diet", guidance)
        self.assertIn("exercise", guidance)
        self.assertIn("emergency", guidance)
        self.assertTrue(any("Blood Pressure" in tip for tip in guidance["tailored_tips"]))


class RoleBasedAccessControlTests(TestCase):
    """Tests for multi-role accounts, server-side permissions, and medical data isolation"""

    def setUp(self):
        self.client = Client()
        # Create standard patient
        self.patient_user = User.objects.create_user(username="patient1", password="Password123!")
        self.patient_record = Patient.objects.create(
            user=self.patient_user, full_name="Ramesh Patil", age=42, consent_given=True
        )

        # Create second patient
        self.patient2_user = User.objects.create_user(username="patient2", password="Password123!")
        self.patient2_record = Patient.objects.create(
            user=self.patient2_user, full_name="Sunita Deshmukh", age=38, consent_given=True
        )

        # Create Community Health Worker (CHW)
        self.chw_user = User.objects.create_user(username="chw_asha", password="Password123!")
        self.chw_user.profile.role = "chw"
        self.chw_user.profile.save()

    def test_server_side_patient_isolation(self):
        # Patient 1 can access Patient 1
        self.assertTrue(can_access_patient(self.patient_user, self.patient_record))
        # Patient 1 CANNOT access Patient 2
        self.assertFalse(can_access_patient(self.patient_user, self.patient2_record))
        # CHW can access authorized patient
        self.assertTrue(can_access_patient(self.chw_user, self.patient_record))

    def test_chw_portal_role_protection(self):
        # Patient attempting to view CHW portal gets redirected
        self.client.login(username="patient1", password="Password123!")
        res = self.client.get(reverse("chw_portal"))
        self.assertEqual(res.status_code, 302) # Redirect to dashboard

        # CHW user accessing CHW portal succeeds
        self.client.login(username="chw_asha", password="Password123!")
        res_chw = self.client.get(reverse("chw_portal"))
        self.assertEqual(res_chw.status_code, 200)


class ScreeningWorkflowsTests(TestCase):
    """Tests for Unified NCD screening, Dedicated BP screening, and Referral workflows"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="kavita", password="Password123!")
        self.client.login(username="kavita", password="Password123!")

    def test_unified_screening_submission(self):
        post_data = {
            "age": 46,
            "gender": "Female",
            "height_cm": 160.0,
            "weight_kg": 64.0,
            "waist_cm": 80.0,
            "physical_activity": "moderate",
            "tobacco_status": "never",
            "family_history_diabetes": "one",
            "known_hypertension": 0,
            "known_heart_disease": 0,
            "systolic_bp": 126.0,
            "diastolic_bp": 80.0,
            "fasting_glucose": 95.0,
            "hba1c": 5.4
        }
        res = self.client.post(reverse("unified_screening"), data=post_data)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Screening Triage Summary")

        # Verify session and measurements were persisted
        patient = Patient.objects.filter(user=self.user).first()
        self.assertIsNotNone(patient)
        self.assertEqual(patient.screening_sessions.count(), 1)
        self.assertGreater(patient.measurements.count(), 0)

    def test_hypertension_screening_submission(self):
        post_data = {
            "systolic": 138.0,
            "diastolic": 88.0,
            "context": "resting_seated",
            "source": "chw_digital_cuff",
            "is_repeated": True,
            "notes": "Verified resting arm measurement"
        }
        res = self.client.post(reverse("hypertension_screening"), data=post_data)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Stage 1 Hypertension")

        patient = Patient.objects.filter(user=self.user).first()
        bp = patient.measurements.filter(measurement_type="blood_pressure").first()
        self.assertIsNotNone(bp)
        self.assertEqual(bp.value_numeric, 138.0)
        self.assertEqual(bp.secondary_numeric, 88.0)

    def test_multilingual_language_switching(self):
        # Switch to Hindi
        res_hi = self.client.get(reverse("set_language", args=["hi"]))
        self.assertEqual(res_hi.status_code, 302)
        self.assertEqual(self.client.session.get("django_language"), "hi")

        # Switch to Marathi
        res_mr = self.client.get(reverse("set_language", args=["mr"]))
        self.assertEqual(res_mr.status_code, 302)
        self.assertEqual(self.client.session.get("django_language"), "mr")

    def test_operational_dashboard_view(self):
        res = self.client.get(reverse("operational_dashboard"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Operational Health Telemetry")
