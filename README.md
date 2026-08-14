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

## 🧠 Clinical AI Models & Accuracy

| Clinical Condition | Model Architecture | Training Records | Key Biomarkers |
| :--- | :--- | :--- | :--- |
| **Diabetes Risk** | Random Forest / SVM | 100,000 | Glucose, HbA1c, BMI, Age, Hypertension |
| **Heart Disease** | Random Forest | 918 | Chest Pain Type, Resting BP, Cholesterol, EKG, Max HR |
| **Chronic Kidney Disease** | Random Forest | 400 | Specific Gravity, Albumin, Creatinine, Urea, Hemoglobin |
| **Liver Disease** | Random Forest | 583 | Total & Direct Bilirubin, SGPT (ALT), SGOT (AST), AG Ratio |
| **Parkinson's Disease** | Random Forest | 195 | Vocal Jitter, Shimmer, Fo, Fhi, Flo, Spread1, RPDE |
| **Stroke Risk** | Random Forest | 5,110 | Avg Glucose Level, BMI, Hypertension, Heart Disease, Age |
