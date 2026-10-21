"""
MediPredict AI — Clinical Screening & NCD Triage Engine
Designed according to Indian Council of Medical Research (ICMR) NCD Guidelines,
Indian Guidelines on Hypertension (IGH-IV), and National Programme for Prevention
and Control of Non-Communicable Diseases (NP-NCD).
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from django.utils import timezone


def calculate_bmi(weight_kg: Optional[float], height_cm: Optional[float]) -> Optional[Dict[str, Any]]:
    """
    Calculates BMI only when valid height and weight are provided.
    Categorizes using ICMR Asian-Indian specific cut-offs:
    - Underweight: < 18.5
    - Normal: 18.5 - 22.9 kg/m²
    - Overweight: 23.0 - 24.9 kg/m²
    - Obese: >= 25.0 kg/m²
    """
    if weight_kg is None or height_cm is None:
        return None
    try:
        w = float(weight_kg)
        h = float(height_cm)
        if w <= 20.0 or w >= 300.0 or h <= 50.0 or h >= 250.0:
            return None
        height_m = h / 100.0
        bmi_val = round(w / (height_m * height_m), 1)

        if bmi_val < 18.5:
            cat = "Underweight"
            badge = "warning"
            advice = "Nutritional assessment and caloric adequacy recommended."
        elif bmi_val <= 22.9:
            cat = "Normal (Asian Indian Reference)"
            badge = "success"
            advice = "Healthy weight range. Maintain regular balanced diet and physical activity."
        elif bmi_val <= 24.9:
            cat = "Overweight (Asian Indian Threshold)"
            badge = "warning"
            advice = "Asian Indian cutoff for overweight is >= 23 kg/m² due to higher visceral adiposity. Weight management recommended."
        else:
            cat = "Obese (Asian Indian Threshold >= 25 kg/m²)"
            badge = "danger"
            advice = "Structured lifestyle modification (30 min daily activity, caloric deficit, high fiber) advised."

        return {
            "bmi": bmi_val,
            "category": cat,
            "badge": badge,
            "guideline": "ICMR Guidelines for Asian Indians",
            "advice": advice
        }
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def evaluate_hypertension(
    systolic: float,
    diastolic: float,
    context: str = "resting_seated",
    is_repeated: bool = False
) -> Dict[str, Any]:
    """
    Evaluates blood pressure according to Indian Guidelines on Hypertension (IGH-IV)
    and AHA/ACC thresholds. Distinguishes single screening from chronic diagnosis.
    """
    try:
        sbp = float(systolic)
        dbp = float(diastolic)
    except (ValueError, TypeError):
        return {
            "valid": False,
            "error": "Invalid blood pressure values provided."
        }

    # Clinical validation
    if sbp < 60 or sbp > 300 or dbp < 40 or dbp > 200:
        return {
            "valid": False,
            "error": "Blood pressure readings are outside physiological measurement ranges."
        }
    if sbp <= dbp:
        return {
            "valid": False,
            "error": "Systolic blood pressure must be greater than diastolic blood pressure."
        }

    # Classification
    if sbp >= 180 or dbp >= 120:
        category = "Hypertensive Crisis (Urgent Review Required)"
        badge = "danger"
        urgency = "urgent_emergency"
        action = "Immediate medical evaluation at the nearest emergency department or PHC."
        repeat_needed = False
        notes = (
            "CRITICAL: Blood pressure is severely elevated (>=180 systolic or >=120 diastolic). "
            "If accompanied by chest pain, shortness of breath, severe headache, vision changes, "
            "or neurological weakness, seek immediate emergency care."
        )
    elif sbp >= 140 or dbp >= 90:
        category = "Stage 2 Hypertension (Screening Threshold)"
        badge = "danger"
        urgency = "priority"
        action = "Clinical review and confirmatory measurement protocol recommended within 3 to 7 days."
        repeat_needed = not is_repeated
        notes = (
            "A single elevated reading does NOT constitute a confirmed medical diagnosis of chronic hypertension. "
            "Established clinical practice requires confirmatory re-measurement on separate days "
            "or ambulatory blood-pressure monitoring."
        )
    elif (130 <= sbp <= 139) or (80 <= dbp <= 89):
        category = "Stage 1 Hypertension (Screening Threshold)"
        badge = "warning"
        urgency = "routine"
        action = "Repeat measurement after 5 minutes of rest; schedule clinical follow-up within 2 to 4 weeks."
        repeat_needed = not is_repeated
        notes = (
            "Mildly elevated blood pressure. Recommended steps: dietary sodium reduction (<5g salt/day), "
            "brisk walking 30 min/day, stress reduction, and re-checking within 1 month."
        )
    elif (120 <= sbp <= 129) and dbp < 80:
        category = "Elevated Blood Pressure"
        badge = "info"
        urgency = "routine"
        action = "Adopt lifestyle modifications (DASH / Indian heart-healthy diet, regular exercise)."
        repeat_needed = False
        notes = "Blood pressure is mildly elevated above optimal. Re-check in 3 to 6 months."
    else:
        category = "Normal Blood Pressure"
        badge = "success"
        urgency = "routine"
        action = "Continue healthy lifestyle habits and routine annual screening."
        repeat_needed = False
        notes = "Blood pressure is within the optimal clinical reference range (<120/<80 mmHg)."

    return {
        "valid": True,
        "systolic": int(sbp),
        "diastolic": int(dbp),
        "category": category,
        "badge": badge,
        "urgency": urgency,
        "action": action,
        "repeat_needed": repeat_needed,
        "is_repeated": is_repeated,
        "context": context,
        "notes": notes,
        "disclaimer": (
            "Note: Blood pressure screening values reflect the specific measurement occasion. "
            "Diagnosis of chronic hypertension requires confirmation by a licensed medical clinician."
        )
    }


def compute_idrs(age: int, waist_cm: Optional[float], activity: str, family_history: str) -> Dict[str, Any]:
    """
    Indian Diabetes Risk Score (IDRS) developed by Dr. V. Mohan & Madras Diabetes Research Foundation (MDRF)
    Validated by ICMR for community non-invasive diabetes screening without laboratory testing.
    Score:
    - Age: <35: 0, 35-49: 20, >=50: 30
    - Waist (Asian Indian): Male: <85: 0, 85-89: 10, >=90: 20 | Female: <80: 0, 80-89: 10, >=90: 20
    - Physical Activity: Vigorous: 0, Moderate: 10, Sedentary: 30
    - Family History: No parent: 0, One parent: 10, Both parents: 20
    Score >= 60: High Risk; 30-50: Moderate Risk; <30: Low Risk
    """
    score = 0
    factors = []

    # Age points
    if age >= 50:
        score += 30
        factors.append(f"Age >= 50 years (+30 pts)")
    elif age >= 35:
        score += 20
        factors.append(f"Age 35-49 years (+20 pts)")
    else:
        factors.append(f"Age < 35 years (0 pts)")

    # Physical activity points
    act = (activity or "").lower()
    if "vigorous" in act or "heavy" in act:
        score += 0
        factors.append("Regular vigorous physical activity (0 pts)")
    elif "moderate" in act:
        score += 10
        factors.append("Moderate physical activity (+10 pts)")
    else:
        score += 30
        factors.append("Sedentary lifestyle / Minimal exercise (+30 pts)")

    # Family history
    fh = (family_history or "").lower()
    if "both" in fh:
        score += 20
        factors.append("Both biological parents have diabetes (+20 pts)")
    elif "one" in fh or "yes" in fh:
        score += 10
        factors.append("One biological parent has diabetes (+10 pts)")
    else:
        factors.append("No parental history of diabetes (0 pts)")

    # Waist if provided
    if waist_cm is not None:
        try:
            w = float(waist_cm)
            if w >= 90:
                score += 20
                factors.append(f"Waist circumference {w}cm (>=90cm: +20 pts)")
            elif w >= 85:
                score += 10
                factors.append(f"Waist circumference {w}cm (85-89cm: +10 pts)")
        except (ValueError, TypeError):
            pass

    if score >= 60:
        risk_level = "High Risk (IDRS >= 60)"
        badge = "danger"
        recommendation = "Definitive glycemic testing (Fasting Blood Glucose or HbA1c) is strongly indicated at a local health centre."
    elif score >= 30:
        risk_level = "Moderate Risk (IDRS 30-59)"
        badge = "warning"
        recommendation = "Adopt preventive physical activity (150 min/week) and annual laboratory screening."
    else:
        risk_level = "Low Risk (IDRS < 30)"
        badge = "success"
        recommendation = "Maintain healthy eating patterns, stay active, and repeat screening in 2 years."

    return {
        "score": score,
        "max_score": 100,
        "risk_level": risk_level,
        "badge": badge,
        "factors": factors,
        "recommendation": recommendation,
        "standard": "Indian Diabetes Risk Score (ICMR / MDRF Validated)"
    }
