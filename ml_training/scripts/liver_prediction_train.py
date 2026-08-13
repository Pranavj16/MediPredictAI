
# ========================================
# Cell
# ========================================
# ==========================================
# Liver Disease Prediction using ILPD Dataset
# ==========================================

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split

from sklearn.preprocessing import StandardScaler

from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression

from sklearn.tree import DecisionTreeClassifier

from sklearn.ensemble import RandomForestClassifier

from sklearn.neighbors import KNeighborsClassifier

from sklearn.svm import SVC

from sklearn.naive_bayes import GaussianNB

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    roc_auc_score,
    roc_curve
)

print("All libraries imported successfully.")
# ========================================
# Cell
# ========================================
# ==========================================
# Load Dataset
# ==========================================

df = pd.read_csv("../datasets/liver/Indian Liver Patient Dataset (ILPD).csv")

# Correct the mismatched columns from the CSV header to match the actual feature values
df.columns = [
    "age",
    "gender",
    "tot_bilirubin",
    "direct_bilirubin",
    "alkphos",
    "sgpt",
    "sgot",
    "tot_proteins",
    "albumin",
    "ag_ratio",
    "is_patient"
]

print("Dataset Loaded Successfully")

print("\nDataset Shape:", df.shape)

df.head()
# ========================================
# Cell
# ========================================
# ==========================================
# Dataset Information
# ==========================================

print("Dataset Information")
print("=" * 50)

df.info()

print("\n")

print("Missing Values")
print("=" * 50)

print(df.isnull().sum())
# ========================================
# Cell
# ========================================
# ==========================================
# Statistical Summary
# ==========================================

df.describe(include="all").T
# ========================================
# Cell
# ========================================
# ==========================================
# Target Distribution
# ==========================================

print(df["is_patient"].value_counts())

plt.figure(figsize=(6,4))

sns.countplot(
    x="is_patient",
    data=df
)

plt.title("Target Distribution")

# plt.show()
# ========================================
# Cell
# ========================================
# ==========================================
# Data Cleaning
# ==========================================

# Remove extra spaces
df["gender"] = df["gender"].astype(str).str.strip()

# Convert Gender to numeric
df["gender"] = df["gender"].map({
    "Male": 1,
    "Female": 0
})

# Convert target
# 1 = Liver Disease
# 2 = Healthy

df["is_patient"] = df["is_patient"].replace({
    1: 1,
    2: 0
})

print(df.head())
# ========================================
# Cell
# ========================================
# ==========================================
# Missing Value Handling
# ==========================================

from sklearn.impute import SimpleImputer

features = [
    "age",
    "gender",
    "tot_bilirubin",
    "direct_bilirubin",
    "tot_proteins",
    "albumin",
    "ag_ratio",
    "sgpt",
    "sgot",
    "alkphos"
]

imputer = SimpleImputer(strategy="median")

df[features] = imputer.fit_transform(df[features])

print(df.isnull().sum())
# ========================================
# Cell
# ========================================
# ==========================================
# Verify Dataset
# ==========================================

print(df.info())

print()

print(df.head())

print()

print(df.describe())
# ========================================
# Cell
# ========================================
# ==========================================
# Features & Target
# ==========================================

X = df.drop("is_patient", axis=1)

y = df["is_patient"]

print("X Shape :", X.shape)

print("y Shape :", y.shape)
# ========================================
# Cell
# ========================================
# ==========================================
# Final NaN Check
# ==========================================

print(X.isnull().sum())

print()

print("Total NaN :", X.isnull().sum().sum())
# ========================================
# Cell
# ========================================
# ==========================================
# Train Test Split
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training Data :", X_train.shape)
print("Testing Data :", X_test.shape)
# ========================================
# Cell
# ========================================
# ==========================================
# Feature Scaling
# ==========================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)

X_test_scaled = scaler.transform(X_test)

print("Feature Scaling Completed")
# ========================================
# Cell
# ========================================
# ==========================================
# Verify No NaN After Scaling
# ==========================================

import numpy as np

print("NaN in X_train_scaled :", np.isnan(X_train_scaled).sum())

print("NaN in X_test_scaled :", np.isnan(X_test_scaled).sum())
# ========================================
# Cell
# ========================================
# ==========================================
# Machine Learning Models
# ==========================================

models = {

    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    ),

    "Decision Tree": DecisionTreeClassifier(
        random_state=42,
        class_weight="balanced"
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced"
    ),

    "KNN": KNeighborsClassifier(n_neighbors=5),

    "SVM": SVC(
        probability=True,
        class_weight="balanced",
        random_state=42
    ),

    "Naive Bayes": GaussianNB()

}

print("Models Created Successfully")
# ========================================
# Cell
# ========================================
# ==========================================
# Train Models
# ==========================================

results = []

for name, model in models.items():

    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)

    results.append({

        "Model": name,

        "Accuracy": accuracy_score(y_test, y_pred),

        "Precision": precision_score(y_test, y_pred),

        "Recall": recall_score(y_test, y_pred),

        "F1 Score": f1_score(y_test, y_pred)

    })

print("Training Completed Successfully")
# ========================================
# Cell
# ========================================
# ==========================================
# Compare All Models
# ==========================================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="F1 Score",
    ascending=False
)

results_df.reset_index(drop=True, inplace=True)

results_df
# ========================================
# Cell
# ========================================
# ==========================================
# Select Best Model
# ==========================================

best_model_name = results_df.iloc[0]["Model"]

best_model = models[best_model_name]

print("Best Model :", best_model_name)
# ========================================
# Cell
# ========================================
# ==========================================
# Classification Report
# ==========================================

y_pred = best_model.predict(X_test_scaled)

print(classification_report(
    y_test,
    y_pred
))
# ========================================
# Cell
# ========================================
# ==========================================
# Confusion Matrix
# ==========================================

cm = confusion_matrix(
    y_test,
    y_pred
)

ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["Healthy", "Liver Disease"]
).plot(cmap="Blues")

plt.title(best_model_name)

# plt.show()

print(cm)
# ========================================
# Cell
# ========================================
# ==========================================
# ROC-AUC Score
# ==========================================

y_prob = best_model.predict_proba(
    X_test_scaled
)[:, 1]

roc = roc_auc_score(
    y_test,
    y_prob
)

print("ROC-AUC Score :", round(roc, 4))
# ========================================
# Cell
# ========================================
# ==========================================
# ROC Curve
# ==========================================

fpr, tpr, thresholds = roc_curve(
    y_test,
    y_prob
)

plt.figure(figsize=(6,6))

plt.plot(
    fpr,
    tpr,
    label=f"AUC = {roc:.3f}",
    linewidth=2
)

plt.plot(
    [0,1],
    [0,1],
    "--",
    color="red"
)

plt.xlabel("False Positive Rate")

plt.ylabel("True Positive Rate")

plt.title("ROC Curve")

plt.legend()

plt.grid(True)

# plt.show()
# ========================================
# Cell
# ========================================
# ==========================================
# Save Model
# ==========================================

feature_columns = X.columns.tolist()

MODEL_DIR = Path("../trained_models")

MODEL_DIR.mkdir(exist_ok=True)

joblib.dump(
    best_model,
    MODEL_DIR / "liver_model.pkl"
)

joblib.dump(
    scaler,
    MODEL_DIR / "liver_scaler.pkl"
)

joblib.dump(
    feature_columns,
    MODEL_DIR / "liver_columns.pkl"
)

print("Model Saved Successfully")