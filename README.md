# MediPredictAI 🏥

MediPredictAI is an enterprise-grade medical diagnostic prediction platform. It leverages calibrated machine learning models to predict risk assessments across **6 clinical conditions** (Diabetes, Heart Disease, Kidney Disease, Liver Disease, Parkinson's Disease, and Stroke) based on patient metrics.

The system features a **Django web portal**, a high-performance **FastAPI inference API microservice**, and an **ML training pipeline** containing verified clinical datasets, Jupyter notebooks, and automated training scripts.

---

## 🏛️ System Architecture

MediPredictAI operates on a decoupled architecture where the clinical user interface and the ML model microservices communicate seamlessly:

```mermaid
graph TD
    Client[Web Browser] <-->|HTTPS / Bootstrap 5 / Chart.js| Django[Django Web App<br>Vercel Serverless / WSGI]
    Django <-->|Authentication & Sessions| DB[(Neon.tech Serverless PostgreSQL<br>DATABASE_URL)]
    
    subgraph FastAPI Backend Microservice
        Django -->|REST API JSON| FastAPI[FastAPI Prediction Engine]
        FastAPI -->|Inference Pipelines| Services[Disease Prediction Services]
        Services -->|Pre-Trained Artifacts| Models[trained_models/<br>.pkl files]
    end

    subgraph ML Pipeline
        Datasets[(datasets/<br>.csv files)] -->|Training & Validation| Notebooks[Jupyter Notebooks]
        Notebooks -->|Exports Best Models| Models
    end
```

### Execution Flow:
1. **Intake Screening**: The clinician or user submits patient vitals and lab biomarkers through dedicated diagnosis forms.
2. **Inference Pipeline**: 
   * The request is dispatched to the FastAPI inference engine (or evaluated locally through the built-in resilient fallback pipeline).
   * Inputs are preprocessed via one-hot categorical encoding, aligned with trained feature columns, and scaled with a `StandardScaler`.
3. **Calibrated Diagnostics**: Pre-trained Random Forest and SVM classifiers evaluate the inputs and return real-time risk predictions, probability confidence scores, and automated medical recommendations.
4. **Data Persistence**: User accounts, authentication sessions, and clinical profiles are persistently managed using **Neon Serverless PostgreSQL**.

---

## 📁 Project Directory Structure

```text
MediPredictAI/
│
├── django_app/                    # Web frontend & clinical dashboard (Django)
│   ├── config/                    # Global settings, URLs, WSGI
│   ├── accounts/                  # User registration, login, session auth
│   ├── core/                      # Landing page & platform metrics
│   ├── dashboard/                 # Clinician diagnostic portal & statistics
│   ├── patients/                  # Patient management records
│   ├── predictions/               # Web forms & result views for 6 conditions
│   ├── static/                    # Custom CSS, glassmorphism styles, JS
│   ├── templates/                 # Responsive HTML views (Bootstrap 5 & Chart.js)
│   └── manage.py                  # Django CLI management script
│
├── fastapi_app/                   # Machine learning prediction API (FastAPI)
│   └── app/
│       ├── main.py                # App initialization, CORS & router inclusion
│       ├── routes/                # 6 API routers (diabetes, heart, kidney, liver, parkinson, stroke)
│       ├── schemas/               # Pydantic request models & validation
│       ├── services/              # Inference wrappers loading joblib artifacts
│       └── utils/                 # Utilities
│
├── ml_training/                   # Machine learning training pipelines & artifacts
│   ├── datasets/                  # Source CSV datasets for all 6 conditions
│   ├── notebooks/                 # Jupyter Notebooks for model training & EDA
│   ├── scripts/                   # Model validation & training scripts
│   └── trained_models/            # Pre-trained models, scalers, and column files (.pkl)
│
├── vercel.json                    # Vercel serverless deployment configuration
├── vercel_app.py                  # Vercel Python serverless entry point
├── requirements.txt               # Project dependency package list
└── README.md                      # Project documentation
```

---

## 🚀 Deployment on Vercel (with Neon.tech Database)

### Step 1: Create a Database on Neon.tech
1. Create a free account on [Neon.tech](https://neon.tech/).
2. Create a new project named `medipredict-db`.
3. On your Neon Dashboard under **Connection Details**, select **Pooled connection** and copy your connection string:
   ```text
   postgresql://username:password@ep-xyz-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### Step 2: Deploy to Vercel
1. Go to [Vercel Dashboard](https://vercel.com/) and click **Add New** -> **Project**.
2. Import your GitHub repository `Pranavj16/MediPredictAI`.
3. In **Project Configuration**, leave the Framework Preset as **Other**.
4. Open the **Environment Variables** section and configure:
   * **`DATABASE_URL`**: *(Paste your Neon connection string from Step 1)*
   * **`DEBUG`**: `False`
   * **`SECRET_KEY`**: *(Generate a secure random string)*
   * **`ALLOWED_HOSTS`**: `*`
5. Click **Deploy**. Vercel will build and serve your application through `vercel.json`.

---

## 💻 Local Development Setup

### 1. Clone & Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/Pranavj16/MediPredictAI.git
cd MediPredictAI

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Database Migrations
```bash
cd django_app
python manage.py migrate
cd ..
```

### 3. Run Both Servers Concurrently

**Terminal 1 — FastAPI Backend (Port 8000):**
```bash
python -m uvicorn --app-dir fastapi_app app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive OpenAPI Swagger Docs available at `http://127.0.0.1:8000/docs`.

**Terminal 2 — Django Frontend (Port 8001):**
```bash
cd django_app
python manage.py runserver 8001
```
Access the web portal at `http://127.0.0.1:8001`.

---

## 🧠 Clinical AI Models & Actual Architecture (Post-Audit)

| Clinical Condition | Model Architecture | Training Records | Key Biomarkers & Features | Intended Use & Limitations |
| :--- | :--- | :--- | :--- | :--- |
| **Diabetes Risk** | `RandomForestClassifier` | 96,146 | Glucose, HbA1c, BMI, Age, Hypertension, Smoking | Screening triage based on metabolic vitals. Calibrated to 0–100% risk index. |
| **Heart Disease** | `KNeighborsClassifier` (k=5) | 918 | Resting BP, Cholesterol, Max HR, ST Slope, Chest Pain | Pattern matching against Cleveland/Hungarian clinical cohorts. Requires stress-test biometrics. |
| **Chronic Kidney Disease** | `RandomForestClassifier` | 400 | Serum Creatinine, Blood Urea, Specific Gravity, Albumin, BP | Diagnostic indicator profiling. Highly sensitive; small sample size (Apollo Hospitals). |
| **Liver Disease** | `LogisticRegression` | 583 | Total & Direct Bilirubin, SGPT (ALT), SGOT (AST), Albumin | ILPD Andhra Pradesh cohort. Linear odds model; low specificity (21%), high sensitivity (94.7%). |
| **Parkinson's Disease** | `RandomForestClassifier` | 195 | Vocal Jitter, Shimmer, Pitch Period Entropy (PPE), HNR | High sensitivity to sustained vowel phonation. Requires calibrated audio capture. |
| **Stroke Risk** | `LogisticRegression` | 5,110 | Avg Glucose Level, BMI, Hypertension, Heart Disease, Age | Low base prevalence (4.9%). Calibrated probability triage; not an absolute future event predictor. |

---

## 🇮🇳 India-Specific NCD Clinical Guidelines Implemented

1. **Asian-Indian BMI Cutoffs (ICMR / WHO-SEARO / Consensus Guidelines for Asian Indians):**
   * `< 18.5 kg/m²`: Underweight
   * `18.5 – 22.9 kg/m²`: Normal Range (standard global threshold is 24.9)
   * `23.0 – 24.9 kg/m²`: Overweight / Increased Risk
   * `≥ 25.0 kg/m²`: Generalized Obesity (standard global threshold is 30.0)

2. **Dedicated Blood Pressure Screening (Indian Guidelines on Hypertension - IGH-IV / ICMR):**
   * `Systolic < 120 AND Diastolic < 80 mmHg`: Optimal / Normal
   * `Systolic 120–129 AND Diastolic < 80 mmHg`: Prehypertension
   * `Systolic 130–139 OR Diastolic 80–89 mmHg`: Stage 1 Hypertension (requires repeat check in 1–2 weeks)
   * `Systolic 140–179 OR Diastolic 90–119 mmHg`: Stage 2 Hypertension (formal medical evaluation needed)
   * `Systolic ≥ 180 OR Diastolic ≥ 120 mmHg`: **Hypertensive Crisis** (Urgent Emergency Referral Flagged)

3. **Frontline Community Health Worker (CHW / ASHA / ANM) Portal:**
   * Simplified patient intake with informed consent recording (`consent_given`, `consent_date`, `consent_notes`).
   * Low-bandwidth optimized screening entry with automatic localStorage draft preservation.
   * Searchable patient roster, pending referral tracking, and printable bilingual screening summaries.

4. **Trilingual Localization:**
   * Full platform support in **English (`en`)**, **Hindi (`hi`)**, and **Marathi (`mr`)**.
   * Instant language toggle via navigation header with session-persisted preference.

5. **Explainable AI (XAI) & Safety Guardrails:**
   * Dynamic feature attribution (relative contribution % and direction) for all 6 disease models.
   * Clear, non-diagnostic clinical interpretations and non-alarmist language.
   * Prominent non-diagnostic disclaimers: AI predictions are screening tools, not clinical diagnoses.

6. **Medically Grounded AI Health Education Assistant:**
   * Retrieval-Augmented Generation (RAG) knowledge engine grounded in ICMR, WHO-SEARO, and NHM public health documents.
   * Hard medical safety boundaries: Rejects requests to prescribe medication, alter prescribed dosages, or claim definitive diagnoses.

