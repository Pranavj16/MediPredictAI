# MediPredict AI — Clinical ML Models Comprehensive Audit

Date: October 2026 | Standard: ICMR Guidelines / Good Machine Learning Practice (GMLP)

## 1. Executive Summary & Cross-Model Comparison Table

| Disease Condition | Algorithm | Dataset Size | Prevalence | Accuracy | Precision | Sensitivity / Recall | Specificity | F1 Score | ROC-AUC | Brier Score |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Diabetes** | RandomForestClassifier | 96,146 | 8.8% | 99.32% | 99.13% | 93.08% | 99.92% | 0.960 | 0.994 | 0.0084 |
| **Heart Disease** | KNeighborsClassifier | 918 | 55.3% | 88.13% | 87.86% | 91.14% | 84.39% | 0.895 | 0.949 | 0.0857 |
| **Chronic Kidney Disease** | RandomForestClassifier | 400 | 62.5% | 99.00% | 98.43% | 100.00% | 97.33% | 0.992 | 1.000 | 0.0125 |
| **Liver Disease** | LogisticRegression | 583 | 71.4% | 73.58% | 74.90% | 94.71% | 20.96% | 0.837 | 0.764 | 0.1689 |
| **Parkinson's Disease** | RandomForestClassifier | 195 | 75.4% | 97.44% | 97.33% | 99.32% | 91.67% | 0.983 | 0.994 | 0.0764 |
| **Stroke** | LogisticRegression | 5,110 | 4.9% | 74.09% | 13.66% | 81.12% | 73.73% | 0.234 | 0.846 | 0.1711 |


## 2. Detailed Findings per Disease Module

### Diabetes
- **Algorithm Family**: `RandomForestClassifier`
- **Target Definition**: `diabetes (0 = No, 1 = Yes)`
- **Source Dataset**: Kaggle Diabetes Prediction Dataset (Synthetically generated/mixed electronic records)
- **Target Population**: Broad international simulated demographic (non-specific, high US/European representation)
- **Key Clinical Limitations**: High class imbalance (8.5% positive). The 97% accuracy is dominated by true negatives. Not calibrated on Indian populations where diabetes manifests at lower BMI thresholds (>=23 vs >=25/30).

### Heart Disease
- **Algorithm Family**: `KNeighborsClassifier`
- **Target Definition**: `HeartDisease (0 = Normal, 1 = Heart Disease)`
- **Source Dataset**: UCI Heart Disease Combined Dataset (Cleveland, Hungarian, Switzerland, Long Beach V)
- **Target Population**: North American and Western European cardiac patients referral cohort (mean age ~54, 79% male)
- **Key Clinical Limitations**: Trained on KNeighborsClassifier on clinical referral cohort, not community screening. ST slope and exercise angina require clinical ECG stress testing.

### Chronic Kidney Disease
- **Algorithm Family**: `RandomForestClassifier`
- **Target Definition**: `classification (0 = notckd, 1 = ckd)`
- **Source Dataset**: UCI Chronic Kidney Disease Dataset (Apollo Hospitals, Tamil Nadu, India)
- **Target Population**: Hospitalized Indian patient cohort in Tamil Nadu (400 cases)
- **Key Clinical Limitations**: Small hospital sample (400 records) with high missingness in primary data; requires 24 clinical laboratory values. Not intended as initial community survey.

### Liver Disease
- **Algorithm Family**: `LogisticRegression`
- **Target Definition**: `is_patient (1 = Patient, 0 = Non-patient)`
- **Source Dataset**: UCI Indian Liver Patient Records (ILPD, Andhra Pradesh, India)
- **Target Population**: 583 patients collected from North East of Andhra Pradesh, India
- **Key Clinical Limitations**: Logistic regression exhibits moderate sensitivity (~73%) and low specificity (~52%). Laboratory panel (bilirubin, AST/ALT, ALP, albumin) required.

### Parkinson's Disease
- **Algorithm Family**: `RandomForestClassifier`
- **Target Definition**: `status (1 = Parkinson's, 0 = Healthy)`
- **Source Dataset**: Oxford Parkinson's Disease Telemonitoring / Voice Dataset (Max Little et al.)
- **Target Population**: 31 biomedical research subjects (23 diagnosed with PD, 8 controls)
- **Key Clinical Limitations**: Only 31 individuals with repeated acoustic recordings (195 rows). High risk of record leakage across splits. Acoustic features (Jitter, Shimmer, RPDE, DFA) require specialized microphone/audio software.

### Stroke
- **Algorithm Family**: `LogisticRegression`
- **Target Definition**: `stroke (1 = Had Stroke, 0 = No Stroke)`
- **Source Dataset**: Kaggle Stroke Prediction Dataset
- **Target Population**: 5,110 electronic health records from US/international registry
- **Key Clinical Limitations**: Severe class imbalance (~4.8% stroke cases). Logistic regression model with 0.5 threshold predicts 0 for almost all cases (sensitivity ~1-2%). Accuracy of ~95% is illusory. Requires calibrated risk threshold and PR-curve evaluation.


## 3. Critical Architectural & Clinical Insights

1. **Stroke Class Imbalance**: Stroke prevalence in the dataset is 4.87%. The current Logistic Regression model predicts negative for nearly all inputs, yielding an apparently high 95.1% accuracy while failing clinical sensitivity. A dedicated calibrated risk index must be utilized.
2. **Parkinson Telemonitoring**: The dataset contains 195 acoustic recordings from only 31 patients. Testing inputs require high-precision acoustic metrics (jitter, shimmer, RPDE) not available during standard outpatient triage.
3. **Indian Population Context**: The Liver dataset is based on Indian patients (ILPD, Andhra Pradesh) and Kidney is from Tamil Nadu (Apollo Hospitals). However, Diabetes and Heart disease datasets are predominantly Western. Indian clinical guidelines (ICMR) establish lower BMI thresholds (overweight >= 23 kg/m², obesity >= 25 kg/m²) and distinct waist-to-height cutoffs that must be integrated into rule-based screening triage alongside ML inference.
