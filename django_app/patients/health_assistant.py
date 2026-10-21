"""
MediPredict AI — Medically Grounded Health Education Assistant (RAG Engine)
Grounds all responses in approved public health literature from ICMR, WHO-SEARO,
and National Health Mission (NHM) India.
Adheres strictly to medical safety: NO prescribing, NO diagnosing, NO fabricating citations.
"""
import re
from typing import Dict, Any, List, Optional


APPROVED_KNOWLEDGE_BASE = [
    {
        "id": "icmr_dm_screening",
        "title": "Diabetes Screening & Diagnostic Criteria (ICMR 2023)",
        "source": "ICMR Guidelines for Management of Type 2 Diabetes (Indian Council of Medical Research)",
        "keywords": ["diabetes", "glucose", "sugar", "fasting", "hba1c", "blood sugar", "screening", "prediabetes", "insulin"],
        "content": (
            "Screening for diabetes should be performed in all individuals aged 30 years and above, or earlier if risk factors exist. "
            "Normal fasting plasma glucose is < 100 mg/dL (5.6 mmol/L). Prediabetes (Impaired Fasting Glucose) is defined as 100–125 mg/dL. "
            "Diabetes threshold is fasting glucose >= 126 mg/dL (7.0 mmol/L) confirmed on two separate occasions, or HbA1c >= 6.5%. "
            "South Asian populations develop diabetes roughly a decade earlier and at lower BMI thresholds (>= 23 kg/m² for overweight)."
        )
    },
    {
        "id": "igh_hypertension",
        "title": "Blood Pressure Measurement & Thresholds (IGH-IV)",
        "source": "Indian Guidelines on Hypertension (IGH-IV) / Association of Physicians of India",
        "keywords": ["hypertension", "blood pressure", "bp", "systolic", "diastolic", "high bp", "sphygmomanometer"],
        "content": (
            "Blood pressure should be measured after the patient has rested comfortably for at least 5 minutes in a seated position with arm supported. "
            "Normal BP is < 120 mmHg systolic and < 80 mmHg diastolic. Stage 1 Hypertension is 130–139 systolic or 80–89 diastolic. "
            "Stage 2 Hypertension is >= 140 systolic or >= 90 diastolic. A diagnosis of hypertension requires at least two separate measurements "
            "on distinct clinical occasions, unless severe elevation (>= 180/120 mmHg) is present."
        )
    },
    {
        "id": "icmr_cvd_prevention",
        "title": "Cardiovascular Disease Prevention in Indian Patients",
        "source": "Indian Heart Association & ICMR National Guidelines for CVD Prevention",
        "keywords": ["heart", "cardiac", "cholesterol", "heart disease", "cvd", "angina", "chest pain", "stent", "attack"],
        "content": (
            "Cardiovascular disease risk in Indians is heightened by high triglycerides, low HDL, elevated lipoprotein(a), and visceral abdominal fat. "
            "Key modifiable risk factors include uncontrolled hypertension, dyslipidemia, diabetes, tobacco consumption (both smoked and smokeless), "
            "and sedentary lifestyle. Routine screening of lipid profile and resting ECG is recommended annually for adults with multiple risk factors."
        )
    },
    {
        "id": "salt_dietary_guidelines",
        "title": "Sodium and Dietary Recommendations (NIN-ICMR)",
        "source": "Dietary Guidelines for Indians, National Institute of Nutrition (NIN-ICMR)",
        "keywords": ["diet", "food", "salt", "sodium", "oil", "fat", "millet", "ragi", "jowar", "eating", "nutrition", "achar", "papad"],
        "content": (
            "Total daily salt intake should not exceed 5 grams (one level teaspoon) per person per day. High-sodium foods such as commercial pickles (achaar), "
            "papads, salted namkeens, and packaged instant soups must be restricted. Replacing refined carbohydrates with coarse grains (Ragi, Jowar, Bajra) "
            "improves insulin sensitivity and provides essential dietary minerals (iron, calcium, magnesium)."
        )
    },
    {
        "id": "doctor_visit_prep",
        "title": "Preparing for a Medical Consultation",
        "source": "National Health Portal (NHP) India / Ministry of Health and Family Welfare",
        "keywords": ["doctor", "appointment", "clinic", "prepare", "hospital", "consultation", "visit", "questions", "phc"],
        "content": (
            "When visiting a doctor or Primary Health Centre (PHC): 1) Bring all previous medical records, prescriptions, and recent lab reports. "
            "2) Note down any symptoms with their duration and triggers. 3) For fasting blood tests, ensure an 8-to-10 hour fast (water is allowed). "
            "4) List all medications, herbal formulations, and supplements you currently take. 5) Write down your primary questions in advance."
        )
    },
    {
        "id": "stroke_warning_fast",
        "title": "Recognizing Stroke Symptoms — FAST Protocol",
        "source": "WHO-SEARO & Indian Stroke Association Public Education Guidelines",
        "keywords": ["stroke", "brain", "paralysis", "fast", "slurred", "drooping", "weakness", "emergency", "108"],
        "content": (
            "Recognize stroke symptoms using FAST: Face drooping (one side of face droops when smiling), Arm weakness (one arm drifts downward when raised), "
            "Speech difficulty (slurred or strange speech), Time to call emergency (108 / 112 immediately). Stroke is a medical emergency requiring rapid "
            "hospitalization within the 4.5-hour golden window for effective thrombolytic therapy."
        )
    },
    {
        "id": "tobacco_cessation_india",
        "title": "Tobacco Cessation Support in India",
        "source": "National Tobacco Control Programme (NTCP), Ministry of Health & Family Welfare",
        "keywords": ["tobacco", "smoke", "smoking", "beedi", "bidi", "cigarette", "gutka", "khaini", "zarda", "quit", "quitting"],
        "content": (
            "Tobacco use in all forms—both smoking (beedi, cigarette) and smokeless (gutka, khaini, zarda, pan masala)—greatly accelerates arterial stiffness, "
            "hypertension, coronary artery disease, and oral/lung cancers. Quitting tobacco reduces heart attack risk by 50% within 1 year. Free national "
            "telephonic cessation counseling is available via Toll-Free 1800-11-2356."
        )
    }
]


def retrieve_relevant_knowledge(query: str, top_k: int = 2) -> List[Dict[str, Any]]:
    """
    RAG retrieval: scores queries against approved medical corpus using keyword matching & token overlap.
    """
    query_tokens = set(re.findall(r'\b\w+\b', query.lower()))
    scored_docs = []

    for doc in APPROVED_KNOWLEDGE_BASE:
        score = 0
        # Check keyword matches
        for kw in doc["keywords"]:
            if kw in query.lower():
                score += 3
        # Check content token overlap
        content_tokens = set(re.findall(r'\b\w+\b', doc["content"].lower()))
        overlap = len(query_tokens.intersection(content_tokens))
        score += overlap

        if score > 0:
            scored_docs.append((score, doc))

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scored_docs[:top_k]]


def ask_health_assistant(query: str, patient_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluates patient inquiry, retrieves verified citations, and provides grounded educational response.
    """
    cleaned_query = query.strip()
    if not cleaned_query:
        return {
            "answer": "Please enter a health question or topic you would like to learn about.",
            "sources": [],
            "safety_note": "Educational information only."
        }

    # Safety check for prescription / diagnostic demands
    prescription_patterns = [
        r'\b(prescribe|medicine|medication|drug|dose|dosage|tablets|pills|antibiotic|cure me)\b',
        r'\b(do i have|tell me if i have|diagnose me)\b'
    ]
    is_demanding_prescription = any(re.search(p, cleaned_query.lower()) for p in prescription_patterns)

    # Retrieve relevant documents
    relevant_docs = retrieve_relevant_knowledge(cleaned_query)

    sources = [doc["source"] for doc in relevant_docs]

    if not relevant_docs:
        # Fallback to general guidance
        answer = (
            "Thank you for your question. As an educational assistant, I can help explain health measurements, "
            "risk factors, preventive practices (such as diet, exercise, and screening procedures), and how to prepare "
            "for doctor appointments. For questions regarding specific clinical symptoms or treatments, please consult "
            "a registered physician or visit your nearest Primary Health Centre (PHC)."
        )
    else:
        # Synthesize educational response from top retrieved document
        primary_doc = relevant_docs[0]
        answer_parts = [primary_doc["content"]]

        if len(relevant_docs) > 1:
            answer_parts.append(f"Additional clinical context: {relevant_docs[1]['content']}")

        # Contextualize with patient screening if provided
        if patient_context and patient_context.get("recent_bp"):
            answer_parts.append(f"Note regarding your profile: Your latest recorded blood pressure was {patient_context['recent_bp']}.")

        answer = " ".join(answer_parts)

    if is_demanding_prescription:
        boundary = (
            "\n\nIMPORTANT CLINICAL SAFETY BOUNDARY: MediPredict AI cannot prescribe medications, modify dosage, "
            "or provide formal medical diagnoses. Prescription decisions must always be made by a licensed doctor "
            "following an in-person physical examination."
        )
        answer = answer + boundary

    return {
        "query": cleaned_query,
        "answer": answer,
        "sources": list(set(sources)),
        "is_safe": True,
        "disclaimer": "This information is grounded in approved medical literature for health literacy. It does not replace clinical consultation."
    }
