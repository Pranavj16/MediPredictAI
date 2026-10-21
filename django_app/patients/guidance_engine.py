"""
MediPredict AI — Evidence-Based Preventive Health Guidance Engine
Tailored for Indian populations according to ICMR-NIN (National Institute of Nutrition)
guidelines, Indian Heart Association recommendations, and WHO-SEARO public health protocols.
"""
from typing import Dict, Any, List


INDIAN_DIET_RECOMMENDATIONS = {
    "title": "Nutrition & Dietary Recommendations (ICMR-NIN Guidelines)",
    "millets_whole_grains": [
        "Incorporate regional Indian millets (Ragi/Nachni, Jowar, Bajra, Foxtail millet) to replace refined polished white rice and maida.",
        "Combine cereals with pulses in a 3:1 ratio (e.g. Khichdi, Missi Roti, Idli-Sambar) to optimize protein quality and glycemic control."
    ],
    "pulses_proteins": [
        "Consume whole sprouted pulses (Moong, Kala Chana, Matki, Rajma) and legumes daily.",
        "For non-vegetarians, prioritize skinless country chicken and freshwater fish rich in Omega-3, avoiding red meat and deep-fried preparations."
    ],
    "vegetables_fruits": [
        "Consume at least 400–500 grams of seasonal vegetables and fresh fruits daily.",
        "Emphasize locally available indigenous greens: Palak (spinach), Methi (fenugreek leaves), Bathua, Chaulai (amaranth), and Moringa (drumstick leaves).",
        "Choose low-glycemic Indian fruits: Guava (Amrood), Jamun (Indian blackberry), Apple, Papaya, and Pomegranate (Anaar) in measured portions."
    ],
    "salt_sodium_control": [
        "Restrict total dietary salt intake to LESS THAN 5 grams per day (approximately one level teaspoon per person per day).",
        "Avoid high-sodium Indian condiments: commercial pickles (achaar), papads, salted farsan, namkeens, and packaged instant noodles.",
        "Use herbs and spices (jeera, dhania, haldi, ginger, garlic, lemon juice) for flavoring instead of excess table salt."
    ],
    "healthy_fats_cooking_oils": [
        "Strictly avoid trans-fats found in Vanaspati, Dalda, commercially fried street snacks (samosas, pakodas), and bakery shortenings.",
        "Use traditional cold-pressed cooking oils in rotation or blend: Mustard oil, Groundnut (peanut) oil, or Til (sesame) oil, limited to 20–25 ml per person daily.",
        "Never reuse cooking oil that has been heated to smoking point, as it generates inflammatory trans-fats and free radicals."
    ]
}

PHYSICAL_ACTIVITY_YOGA = {
    "title": "Physical Activity & Yogic Practices (ICMR / AYUSH Protocols)",
    "aerobic_exercise": [
        "Perform at least 150 to 300 minutes of moderate-intensity aerobic exercise weekly (such as brisk walking at 100 steps/minute, cycling, or swimming).",
        "Break up sedentary desk hours: take a 3-to-5 minute walking break every 45–60 minutes of seated posture."
    ],
    "yoga_asanas": [
        "Practice daily Surya Namaskar (Sun Salutations) at a gentle, rhythmic pace matching your fitness level.",
        "Asanas beneficial for metabolic and cardiovascular conditioning: Tadasana, Vrikshasana, Bhujangasana, and Mandukasana.",
        "Consult your physician before performing inverted postures if you have unmanaged high blood pressure or retinopathy."
    ],
    "pranayama_stress": [
        "Practice 10–15 minutes of Anulom-Vilom (Alternate Nostril Breathing) and Bhramari Pranayama daily to reduce sympathetic autonomic stress.",
        "Engage in Shavasana or guided Yoga Nidra to improve heart-rate variability and sleep architecture."
    ]
}

TOBACCO_CESSATION_SUPPORT = {
    "title": "Tobacco & Smokeless Areca Nut Cessation Guidance",
    "cessation_steps": [
        "Identify specific daily triggers (post-meal cravings, tea breaks, stress, peer pressure) and substitute them with healthy oral alternatives like roasted saunf (fennel), elaichi (cardamom), or roasted ajwain.",
        "Gradual tapering or cold-turkey cessation: Set a firm quit date within the next two weeks and notify family members for accountability.",
        "National Tobacco Quitline (Government of India): Call Toll-Free 1800-11-2356 or SMS 'QUIT' to 56349 for free professional cessation counseling.",
        "Regular dental and oral cavity screening at your local Primary Health Centre (PHC) to check for oral submucous fibrosis or leukoplakia."
    ]
}

RED_FLAGS_EMERGENCY = {
    "title": "Emergency Warning Signs (Seek Immediate Hospital Care)",
    "signs": [
        "Sudden crushing chest pressure, tightness, or pain radiating to the left arm, neck, jaw, or upper back.",
        "Severe shortness of breath, sudden sweating, or unexplained dizziness.",
        "FAST Stroke Warning Signs: Facial drooping, Arm weakness, Slurred speech, Time to call emergency (108 / 112).",
        "Severe throbbing headache accompanied by blurred vision or blood pressure >= 180/120 mmHg.",
        "Loss of consciousness or sudden confusion."
    ]
}


def generate_personalized_guidance(patient, measurements=None) -> Dict[str, Any]:
    """
    Generates personalized preventive health recommendations
    based on the patient's recorded clinical parameters and risk profile.
    """
    flags = []
    tailored_tips = []

    # Check recent measurements
    latest_bp = None
    latest_glucose = None
    latest_bmi = None

    if measurements:
        for m in measurements:
            if m.measurement_type == 'blood_pressure' and not latest_bp:
                latest_bp = (m.value_numeric, m.secondary_numeric)
            elif m.measurement_type in ['blood_glucose', 'fasting_glucose'] and not latest_glucose:
                latest_glucose = m.value_numeric
            elif m.measurement_type == 'bmi' and not latest_bmi:
                latest_bmi = m.value_numeric

    # BP tailoring
    if latest_bp:
        sbp, dbp = latest_bp
        if sbp >= 140 or (dbp and dbp >= 90):
            flags.append("Elevated Blood Pressure Recorded")
            tailored_tips.append(
                "Blood Pressure Priority: Strict sodium reduction (< 3-4g salt/day). "
                "Emphasize potassium-rich foods (drumsticks, spinach, coconut water in moderation, bananas). "
                "Schedule a clinical evaluation for potential antihypertensive management."
            )
        elif sbp >= 130 or (dbp and dbp >= 80):
            flags.append("Pre-hypertension / Stage 1 BP")
            tailored_tips.append(
                "Early Vascular Care: Daily 30-minute brisk walk and daily 10-minute Pranayama. "
                "Cut out packaged namkeens and papads to normalize resting vascular resistance."
            )

    # Glucose tailoring
    if latest_glucose:
        if latest_glucose >= 126:
            flags.append("Elevated Glycemic Marker Recorded")
            tailored_tips.append(
                "Glycemic Management: Replace polished white rice with Jowar or Ragi rotis. "
                "Add 1-2 teaspoons of soaked Methi (fenugreek) seeds before morning breakfast. "
                "Schedule confirmatory HbA1c lab testing."
            )
        elif latest_glucose >= 100:
            flags.append("Prediabetes Range Glucose")
            tailored_tips.append(
                "Prediabetes Window: Diabetes is largely preventable through weight reduction (5-7% of body weight) "
                "and daily physical activity. Eliminate sweetened chai, commercial juices, and sweets."
            )

    # BMI tailoring
    if latest_bmi:
        if latest_bmi >= 25.0:
            flags.append(f"Elevated Asian-Indian BMI ({latest_bmi} kg/m²)")
            tailored_tips.append(
                "Weight Optimization: Target a gradual reduction of 500 kcal/day through portion control. "
                "Fill half your thali with raw salads and cooked vegetables before taking roti or rice."
            )
        elif latest_bmi >= 23.0:
            flags.append(f"Overweight Threshold for South Asians ({latest_bmi} kg/m²)")
            tailored_tips.append(
                "Weight Awareness: Asian Indians accumulate visceral abdominal fat at lower BMI values. "
                "Incorporate core-strengthening asanas and daily walking."
            )

    return {
        "flags": flags,
        "tailored_tips": tailored_tips,
        "diet": INDIAN_DIET_RECOMMENDATIONS,
        "exercise": PHYSICAL_ACTIVITY_YOGA,
        "tobacco": TOBACCO_CESSATION_SUPPORT,
        "emergency": RED_FLAGS_EMERGENCY,
        "disclaimer": (
            "Preventive guidance is educational and evidence-grounded. "
            "It does NOT prescribe medical therapy. Never discontinue or adjust prescription medicines "
            "without consulting your registered healthcare physician."
        )
    }
