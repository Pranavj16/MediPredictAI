"""
MediPredict AI — Multilingual Localization System
Supports English ('en'), Hindi ('hi'), and Marathi ('mr').
Medically reviewed terminology aligned with ICMR & National Health Mission (NHM) Maharashtra/India.
"""
from typing import Dict

TRANSLATIONS = {
    "en": {
        # Brand & Nav
        "app_title": "MediPredict AI",
        "app_subtitle": "NCD Risk Screening & Follow-up Platform",
        "dashboard": "Dashboard",
        "unified_screening": "Unified NCD Screening",
        "bp_screening": "Hypertension Screening",
        "patient_profile": "My Health Profile",
        "health_trends": "Health Trends & History",
        "preventive_guidance": "Preventive Health Guidance",
        "ai_assistant": "AI Health Education Assistant",
        "chw_portal": "Health Worker (CHW) Portal",
        "referral_management": "Referrals & Follow-ups",
        "aggregated_dashboard": "Operational Health Metrics",
        "disease_diagnostics": "AI Disease Diagnostic Suite",
        "telemetry": "System Telemetry",
        "logout": "Logout",
        "login": "Login",
        "register": "Register",
        "active_session": "Session Active",
        "models_online": "6 AI Models Online",

        # Common Actions
        "submit": "Submit",
        "save": "Save Record",
        "execute_diagnosis": "Run AI Assessment",
        "start_screening": "Begin Screening",
        "record_measurement": "Record Measurement",
        "create_referral": "Create Referral",
        "schedule_followup": "Schedule Follow-up",
        "reset_form": "Reset Form",
        "view_details": "View Details",
        "print_summary": "Print Screening Summary",
        "back_to_dashboard": "Back to Dashboard",
        "learn_more": "Learn More",

        # Form Fields
        "full_name": "Full Name",
        "age": "Age (Years)",
        "gender": "Gender",
        "male": "Male",
        "female": "Female",
        "other": "Other",
        "phone_number": "Phone Number",
        "height_cm": "Height (cm)",
        "weight_kg": "Weight (kg)",
        "bmi": "Body Mass Index (BMI)",
        "systolic_bp": "Systolic Blood Pressure (mmHg)",
        "diastolic_bp": "Diastolic Blood Pressure (mmHg)",
        "fasting_glucose": "Fasting Blood Glucose (mg/dL)",
        "random_glucose": "Random Blood Glucose (mg/dL)",
        "hba1c": "Glycated Hemoglobin HbA1c (%)",
        "tobacco_use": "Tobacco / Smoking Status",
        "physical_activity": "Weekly Physical Activity",
        "family_history": "Family History of Diabetes / Heart Disease",
        "measurement_context": "Measurement Context",
        "measurement_source": "Source of Reading",
        "was_repeated": "Repeated after 5 minutes of rest?",

        # Clinical Statuses & Badges
        "normal": "Normal / Optimal",
        "low_risk": "Low Risk / Within Expected Range",
        "elevated_risk": "Elevated Risk Identified",
        "prehypertension": "Elevated Blood Pressure",
        "stage1_htn": "Stage 1 Hypertension (Screening Threshold)",
        "stage2_htn": "Stage 2 Hypertension (Screening Threshold)",
        "crisis_htn": "Hypertensive Crisis (Urgent Review Required)",
        "screening_incomplete": "Screening Incomplete",
        "assessment_recommended": "Clinical Assessment Recommended",
        "referral_pending": "Referral Pending",
        "followup_scheduled": "Follow-up Scheduled",
        "followup_completed": "Follow-up Completed",

        # Disclaimers
        "medical_disclaimer": "Medical Disclaimer: MediPredict AI provides preliminary risk screening. It is NOT a confirmed diagnostic tool. Always consult a qualified medical professional for diagnosis and treatment decisions.",
        "confirmatory_note": "A single blood pressure reading does not constitute a chronic hypertension diagnosis. Confirmatory measurements are required.",

        # Roles
        "role_patient": "Patient",
        "role_chw": "Community Health Worker (ASHA / ANM)",
        "role_clinician": "Clinician / Reviewer",
        "role_admin": "Administrator",
    },

    "hi": {
        # Brand & Nav
        "app_title": "मेडीप्रेडिक्ट एआई",
        "app_subtitle": "एनसीडी जोखिम जांच एवं निरंतर देखभाल मंच",
        "dashboard": "डैशबोर्ड",
        "unified_screening": "एकीकृत एनसीडी जांच",
        "bp_screening": "रक्तचाप (हाइपरटेंशन) जांच",
        "patient_profile": "मेरा स्वास्थ्य प्रोफाइल",
        "health_trends": "स्वास्थ्य रुझान एवं इतिहास",
        "preventive_guidance": "निवारक स्वास्थ्य मार्गदर्शन",
        "ai_assistant": "एआई स्वास्थ्य शिक्षा सहायक",
        "chw_portal": "स्वास्थ्य कार्यकर्ता (आशा/एएनएम) पोर्टल",
        "referral_management": "रेफरल एवं फॉलो-अप प्रबंधन",
        "aggregated_dashboard": "सामुदायिक स्वास्थ्य आंकड़े",
        "disease_diagnostics": "रोग जोखिम मूल्यांकन सूट",
        "telemetry": "सिस्टम स्थिति",
        "logout": "लॉगआउट",
        "login": "लॉगिन करें",
        "register": "पंजीकरण करें",
        "active_session": "सत्र सक्रिय",
        "models_online": "6 एआई मॉडल सक्रिय",

        # Common Actions
        "submit": "जमा करें",
        "save": "रिकॉर्ड सुरक्षित करें",
        "execute_diagnosis": "एआई जांच शुरू करें",
        "start_screening": "जांच शुरू करें",
        "record_measurement": "माप दर्ज करें",
        "create_referral": "रेफरल बनाएं",
        "schedule_followup": "फॉलो-अप तय करें",
        "reset_form": "फॉर्म रीसेट करें",
        "view_details": "विवरण देखें",
        "print_summary": "जांच सारांश प्रिंट करें",
        "back_to_dashboard": "डैशबोर्ड पर लौटें",
        "learn_more": "और जानें",

        # Form Fields
        "full_name": "पूरा नाम",
        "age": "आयु (वर्ष)",
        "gender": "लिंग",
        "male": "पुरुष",
        "female": "महिला",
        "other": "अन्य",
        "phone_number": "मोबाइल नंबर",
        "height_cm": "ऊंचाई (सेमी)",
        "weight_kg": "वजन (किलो)",
        "bmi": "बॉडी मास इंडेक्स (बीएमआई)",
        "systolic_bp": "सिस्टोलिक रक्तचाप (ऊपरी बीपी - mmHg)",
        "diastolic_bp": "डायस्टोलिक रक्तचाप (निचला बीपी - mmHg)",
        "fasting_glucose": "खाली पेट रक्त शर्करा (Fasting Glucose - mg/dL)",
        "random_glucose": "रैंडम रक्त शर्करा (Random Glucose - mg/dL)",
        "hba1c": "ग्लाइकेटेड हीमोग्लोबिन HbA1c (%)",
        "tobacco_use": "तंबाकू / बीड़ी / सिगरेट का उपयोग",
        "physical_activity": "साप्ताहिक शारीरिक गतिविधि",
        "family_history": "परिवार में मधुमेह या हृदय रोग का इतिहास",
        "measurement_context": "माप की स्थिति",
        "measurement_source": "माप का स्रोत",
        "was_repeated": "क्या 5 मिनट विश्राम के बाद दोबारा मापा गया?",

        # Clinical Statuses & Badges
        "normal": "सामान्य / उत्तम",
        "low_risk": "कम जोखिम / सामान्य सीमा में",
        "elevated_risk": "जोखिम संकेत पहचाने गए",
        "prehypertension": "बढ़ा हुआ रक्तचाप (प्री-हाइपरटेंशन)",
        "stage1_htn": "स्टेज 1 हाइपरटेंशन (जांच स्तर)",
        "stage2_htn": "स्टेज 2 हाइपरटेंशन (जांच स्तर)",
        "crisis_htn": "अत्यधिक उच्च रक्तचाप (तत्काल चिकित्सा आवश्यक)",
        "screening_incomplete": "जांच अधूरी",
        "assessment_recommended": "चिकित्सकीय परामर्श अनुशंसित",
        "referral_pending": "रेफरल प्रतीक्षित",
        "followup_scheduled": "फॉलो-अप निर्धारित",
        "followup_completed": "फॉलो-अप पूर्ण",

        # Disclaimers
        "medical_disclaimer": "चिकित्सा अस्वीकरण: मेडीप्रेडिक्ट एआई केवल प्रारंभिक स्वास्थ्य स्क्रीनिंग प्रदान करता है। यह कोई अंतिम चिकित्सीय निदान नहीं है। किसी भी उपचार या दवा के लिए हमेशा योग्य चिकित्सक से परामर्श लें।",
        "confirmatory_note": "एक बार के रक्तचाप माप से स्थायी हाइपरटेंशन का निदान नहीं होता। पुष्टि के लिए अलग-अलग दिनों में माप आवश्यक है।",

        # Roles
        "role_patient": "मरीज (नागरिक)",
        "role_chw": "सामुदायिक स्वास्थ्य कार्यकर्ता (आशा / एएनएम)",
        "role_clinician": "चिकित्सक / समीक्षक",
        "role_admin": "व्यवस्थापक (एडमिन)",
    },

    "mr": {
        # Brand & Nav
        "app_title": "मेडीप्रेडिक्ट एआय",
        "app_subtitle": "अंसंसर्गजन्य रोग तपासणी व पाठपुरावा प्रणाली",
        "dashboard": "डॅशबोर्ड",
        "unified_screening": "एकात्मिक एनसीडी तपासणी",
        "bp_screening": "रक्तदाब (उच्च रक्तदाब) तपासणी",
        "patient_profile": "माझी आरोग्य माहिती",
        "health_trends": "आरोग्य नोंदी व आलेख",
        "preventive_guidance": "प्रतिबंधात्मक आरोग्य सल्ला",
        "ai_assistant": "एआय आरोग्य शिक्षण सहाय्यक",
        "chw_portal": "आरोग्य सेविका (आशा/एएनएम) पोर्टल",
        "referral_management": "रेफरल व पाठपुरावा व्यवस्थापन",
        "aggregated_dashboard": "आरोग्य आकडेवारी व अहवाल",
        "disease_diagnostics": "रोग जोखीम मूल्यांकन संच",
        "telemetry": "सिस्टम कार्यस्थिती",
        "logout": "लॉगआउट",
        "login": "लॉगिन करा",
        "register": "नोंदणी करा",
        "active_session": "सत्र सुरू",
        "models_online": "6 एआय मॉडेल्स सक्रिय",

        # Common Actions
        "submit": "सादर करा",
        "save": "नोंद साठवा",
        "execute_diagnosis": "एआय तपासणी सुरू करा",
        "start_screening": "तपासणी सुरू करा",
        "record_measurement": "मापन नोंदवा",
        "create_referral": "रेफरल तयार करा",
        "schedule_followup": "पुढील भेट नियोजित करा",
        "reset_form": "फॉर्म रीसेट करा",
        "view_details": "सविस्तर पहा",
        "print_summary": "तपासणी सारांश प्रिंट करा",
        "back_to_dashboard": "डॅशबोर्डवर परत जा",
        "learn_more": "अधिक माहिती",

        # Form Fields
        "full_name": "पूर्ण नाव",
        "age": "वय (वर्षे)",
        "gender": "लिंग",
        "male": "पुरुष",
        "female": "स्त्री",
        "other": "इतर",
        "phone_number": "मोबाईल नंबर",
        "height_cm": "उंची (सेंटीमीटर)",
        "weight_kg": "वजन (किलोग्रॅम)",
        "bmi": "बॉडी मास इंडेक्स (बीएमआय)",
        "systolic_bp": "सिस्टॉलिक रक्तदाब (वरचा बीपी - mmHg)",
        "diastolic_bp": "डायस्टॉलिक रक्तदाब (खालचा बीपी - mmHg)",
        "fasting_glucose": "उपाशीपोटी साखर (Fasting Glucose - mg/dL)",
        "random_glucose": "रँडम साखर (Random Glucose - mg/dL)",
        "hba1c": "ग्लायकेटेड हिमोग्लोबिन HbA1c (%)",
        "tobacco_use": "तंबाखू / विडी / सिगारेटचे सेवन",
        "physical_activity": "साप्ताहिक शारीरिक हालचाल",
        "family_history": "कुटुंबात मधुमेह किंवा हृदयविकाराचा इतिहास",
        "measurement_context": "मापनाची स्थिती",
        "measurement_source": "मापनाचे साधन",
        "was_repeated": "५ मिनिटे विश्रांतीनंतर पुन्हा मोजले का?",

        # Clinical Statuses & Badges
        "normal": "सामान्य / उत्तम",
        "low_risk": "कमी जोखीम / अपेक्षित मर्यादेत",
        "elevated_risk": "जोखिम घटक आढळले",
        "prehypertension": "वाढलेला रक्तदाब (प्री-हायपरटेन्शन)",
        "stage1_htn": "स्टेज १ उच्च रक्तदाब (तपासणी स्तर)",
        "stage2_htn": "स्टेज २ उच्च रक्तदाब (तपासणी स्तर)",
        "crisis_htn": "अत्यंत उच्च रक्तदाब (तातडीची वैद्यकीय गरज)",
        "screening_incomplete": "तपासणी अपूर्ण",
        "assessment_recommended": "वैद्यकीय तपासणीची शिफारस",
        "referral_pending": "रेफरल प्रलंबित",
        "followup_scheduled": "पाठपुरावा नियोजित",
        "followup_completed": "पाठपुरावा पूर्ण",

        # Disclaimers
        "medical_disclaimer": "वैद्यकीय अस्वीकरण: मेडीप्रेडिक्ट एआय केवळ प्राथमिक जोखीम तपासणी प्रदान करते. हा अंतिम वैद्यकीय निष्कर्ष नाही. योग्य उपचारांसाठी नेहमी नोंदणीकृत डॉक्टरांचा सल्ला घ्या.",
        "confirmatory_note": "एका तपासणीतील रक्तदाबावरून कायमस्वरूपी उच्च रक्तदाबाचे निदान होत नाही. पुष्टीसाठी वेगवेगळ्या दिवशी मापन आवश्यक आहे.",

        # Roles
        "role_patient": "रुग्ण (नागरिक)",
        "role_chw": "आरोग्य कार्यकर्ता (आशा / एएनएम)",
        "role_clinician": "डॉक्टर / वैद्यकीय अधिकारी",
        "role_admin": "प्रशासक (अॅडमिन)",
    }
}


def get_translation(key: str, lang: str = "en") -> str:
    """Retrieves localized string with fallback to English."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))


def get_all_translations(lang: str = "en") -> Dict[str, str]:
    """Returns complete dictionary for template rendering."""
    base = TRANSLATIONS["en"].copy()
    if lang in TRANSLATIONS and lang != "en":
        base.update(TRANSLATIONS[lang])
    return base
