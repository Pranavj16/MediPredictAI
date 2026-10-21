"""
Explainable AI (XAI) & Clinical Interpretation Engine for MediPredict AI
Provides transparent feature contributions, calibrated risk indices,
plain-language summaries, and clinical safety disclaimers across all 6 conditions.
"""
from typing import Dict, Any, List


DISCLAIMER_TEXT = (
    "NOTICE: This AI risk assessment is a preliminary statistical screening tool, "
    "NOT a confirmed medical diagnosis. AI models evaluate pattern correlations "
    "and cannot replace a clinical evaluation, laboratory blood testing, or physical "
    "examination by a qualified medical practitioner. Do not alter prescribed medication "
    "without consulting your physician."
)

MODEL_METADATA = {
    "diabetes": {
        "model_name": "Random Forest Glycemic Classifier",
        "intended_use": "Preliminary glycemic risk triage based on blood glucose, HbA1c, and metabolic vitals.",
        "limitations": (
            "Model is calibrated on adult cohort data. Lower BMI cutoffs for South Asian populations "
            "(overweight >= 23 kg/m² per ICMR) should be clinically considered in conjunction with outputs."
        ),
        "feature_labels": {
            "HbA1c_level": "Glycated Hemoglobin (HbA1c)",
            "blood_glucose_level": "Blood Glucose Level",
            "bmi": "Body Mass Index (BMI)",
            "age": "Age",
            "hypertension": "History of Hypertension",
            "heart_disease": "History of Heart Disease",
            "smoking_history": "Smoking History",
            "gender": "Gender"
        }
    },
    "heart": {
        "model_name": "K-Nearest Neighbors Cardiovascular Classifier",
        "intended_use": "Screening of cardiovascular risk factors from resting vitals and symptom indicators.",
        "limitations": (
            "Requires clinical exercise stress testing indicators (ST slope, exercise angina). "
            "Not a substitute for 12-lead ECG or echocardiogram."
        ),
        "feature_labels": {
            "ST_Slope": "ST Slope Pattern",
            "ChestPainType": "Chest Pain Characteristics",
            "Oldpeak": "ST Depression (Oldpeak)",
            "MaxHR": "Peak Exercise Heart Rate",
            "Cholesterol": "Serum Cholesterol",
            "RestingBP": "Resting Blood Pressure",
            "Age": "Age",
            "FastingBS": "Fasting Blood Sugar",
            "Sex": "Sex"
        }
    },
    "kidney": {
        "model_name": "Random Forest Renal Filtration Classifier",
        "intended_use": "Evaluating potential chronic kidney disease indicators based on laboratory biomarkers.",
        "limitations": (
            "Trained on hospitalized patient cohort. Requires comprehensive renal panel "
            "(serum creatinine, blood urea, specific gravity, urine albumin)."
        ),
        "feature_labels": {
            "sc": "Serum Creatinine",
            "hemo": "Hemoglobin",
            "al": "Urine Albumin",
            "bgr": "Blood Glucose Random",
            "bu": "Blood Urea",
            "bp": "Blood Pressure",
            "age": "Age"
        }
    },
    "liver": {
        "model_name": "Regularized Logistic Regression Hepatic Classifier",
        "intended_use": "Evaluating liver function test (LFT) panel variations for hepatic risk.",
        "limitations": (
            "Model demonstrates moderate sensitivity and lower specificity; abnormal enzymes "
            "(ALT/AST, bilirubin) necessitate diagnostic ultrasonography and viral hepatitis screening."
        ),
        "feature_labels": {
            "tot_bilirubin": "Total Bilirubin",
            "direct_bilirubin": "Direct Bilirubin",
            "sgpt": "Alanine Aminotransferase (ALT / SGPT)",
            "sgot": "Aspartate Aminotransferase (AST / SGOT)",
            "alkphos": "Alkaline Phosphatase",
            "albumin": "Serum Albumin",
            "ag_ratio": "Albumin/Globulin Ratio",
            "age": "Age"
        }
    },
    "parkinson": {
        "model_name": "Random Forest Neuro-Vocal Classifier",
        "intended_use": "Analysis of sustained vowel phonation acoustic stability (jitter, shimmer, RPDE).",
        "limitations": (
            "Requires calibrated acoustic recording environment. Telephonic or uncalibrated microphone "
            "input can artificially elevate perturbation values."
        ),
        "feature_labels": {
            "PPE": "Pitch Period Entropy",
            "spread1": "Non-linear Fundamental Frequency Spread",
            "MDVP_Fo_Hz": "Average Vocal Fundamental Frequency",
            "MDVP_Jitter_percent": "Frequency Variation (Jitter)",
            "MDVP_Shimmer": "Amplitude Perturbation (Shimmer)",
            "HNR": "Harmonics-to-Noise Ratio"
        }
    },
    "stroke": {
        "model_name": "Calibrated Logistic Regression Cerebrovascular Classifier",
        "intended_use": "Triage of cerebrovascular risk profile based on metabolic vitals and cardiovascular history.",
        "limitations": (
            "Stroke events in the general population are rare (<5% prevalence in unselected screening). "
            "Absolute stroke risk must be evaluated in context of comprehensive vascular risk calculators."
        ),
        "feature_labels": {
            "age": "Age",
            "hypertension": "History of Hypertension",
            "avg_glucose_level": "Average Blood Glucose",
            "heart_disease": "Cardiovascular Disease History",
            "bmi": "Body Mass Index",
            "smoking_status": "Smoking Status"
        }
    }
}


def compute_feature_contributions(
    model: Any,
    scaler: Any,
    columns: List[str],
    patient_df_scaled: Any,
    condition: str
) -> List[Dict[str, Any]]:
    """
    Computes explainable feature importance/attribution for the patient instance.
    """
    contributions = []
    x_scaled = patient_df_scaled[0]
    meta = MODEL_METADATA.get(condition, {})
    label_map = meta.get("feature_labels", {})

    if hasattr(model, "feature_importances_"):
        # Tree-based model (Random Forest)
        importances = model.feature_importances_
        # Impact is directional deviation from scaled mean (scaled mean is 0.0)
        raw_impacts = x_scaled * importances
        total_mag = sum(abs(raw_impacts)) or 1.0

        for col, raw_imp, feat_val in zip(columns, raw_impacts, x_scaled):
            pct = round(float(abs(raw_imp) / total_mag * 100), 1)
            if pct >= 3.0:
                readable = label_map.get(col, col.replace('_', ' ').title())
                direction = "increases_risk" if raw_imp > 0 else "lowers_risk"
                contributions.append({
                    "feature": readable,
                    "direction": direction,
                    "relative_contribution": pct,
                    "raw_score": round(float(raw_imp), 3)
                })

    elif hasattr(model, "coef_"):
        # Linear model (Logistic Regression)
        coefs = model.coef_[0]
        raw_impacts = x_scaled * coefs
        total_mag = sum(abs(raw_impacts)) or 1.0

        for col, raw_imp, feat_val in zip(columns, raw_impacts, x_scaled):
            pct = round(float(abs(raw_imp) / total_mag * 100), 1)
            if pct >= 3.0:
                readable = label_map.get(col, col.replace('_', ' ').title())
                direction = "increases_risk" if raw_imp > 0 else "lowers_risk"
                contributions.append({
                    "feature": readable,
                    "direction": direction,
                    "relative_contribution": pct,
                    "raw_score": round(float(raw_imp), 3)
                })
    else:
        # Distance-based (KNN)
        # Identify top deviated normalized features
        deviations = abs(x_scaled)
        total_dev = sum(deviations) or 1.0
        for col, dev in zip(columns, deviations):
            pct = round(float(dev / total_dev * 100), 1)
            if pct >= 5.0:
                readable = label_map.get(col, col.replace('_', ' ').title())
                direction = "increases_risk" if dev > 1.0 else "neutral"
                contributions.append({
                    "feature": readable,
                    "direction": direction,
                    "relative_contribution": pct,
                    "raw_score": round(float(dev), 3)
                })

    # Sort descending by contribution percentage
    contributions.sort(key=lambda x: x["relative_contribution"], reverse=True)
    return contributions[:5]


def build_explanation_response(
    condition: str,
    prediction: int,
    risk_score: float,
    confidence: float,
    feature_contributions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    meta = MODEL_METADATA.get(condition, {
        "model_name": f"{condition.title()} Classifier",
        "intended_use": "Preliminary risk screening.",
        "limitations": "Screening prediction only."
    })

    if prediction == 1:
        status_label = "Elevated Risk Identified"
        interpretation = (
            f"Based on the provided measurements, the {meta['model_name']} identified "
            "elevated statistical risk markers. This suggests that further clinical review "
            "and formal diagnostic testing may be appropriate. Consider consulting a medical "
            "practitioner for confirmation and personalized guidance."
        )
        recommendations = [
            "Schedule a clinical evaluation with a qualified physician.",
            "Verify screening indicators through standard laboratory diagnostic testing.",
            "Bring your recorded measurements and medication history to the appointment.",
            "Do not begin or stop any prescription medication based solely on this assessment."
        ]
    else:
        status_label = "Low Risk / Within Expected Range"
        interpretation = (
            f"The provided metrics currently fall within expected reference patterns "
            f"for this {meta['model_name']}. Routine preventive screening, a balanced diet, "
            "and regular physical activity remain essential for long-term health."
        )
        recommendations = [
            "Maintain routine annual or bi-annual health wellness check-ups.",
            "Continue regular physical activity and balanced nutrition.",
            "Monitor vitals such as blood pressure and fasting glucose periodically."
        ]

    return {
        "condition": condition,
        "prediction": int(prediction),
        "status_label": status_label,
        "risk_score": round(float(risk_score), 1),
        "probability": round(float(risk_score), 1),
        "confidence": round(float(confidence), 1),
        "model_name": meta["model_name"],
        "intended_use": meta["intended_use"],
        "limitations": meta["limitations"],
        "disclaimer": DISCLAIMER_TEXT,
        "interpretation": interpretation,
        "recommendations": recommendations,
        "feature_contributions": feature_contributions
    }
