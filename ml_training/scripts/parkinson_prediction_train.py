import pandas as pd
import numpy as np
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Load dataset
df = pd.read_csv('../datasets/parkinsons/parkinsons.csv')

# Drop name column
if 'name' in df.columns:
    df = df.drop('name', axis=1)

# Rename columns to use underscores to match ParkinsonInput schema
df = df.rename(columns={
    'MDVP:Fo(Hz)': 'MDVP_Fo_Hz',
    'MDVP:Fhi(Hz)': 'MDVP_Fhi_Hz',
    'MDVP:Flo(Hz)': 'MDVP_Flo_Hz',
    'MDVP:Jitter(%)': 'MDVP_Jitter_percent',
    'MDVP:Jitter(Abs)': 'MDVP_Jitter_Abs',
    'MDVP:RAP': 'MDVP_RAP',
    'MDVP:PPQ': 'MDVP_PPQ',
    'Jitter:DDP': 'Jitter_DDP',
    'MDVP:Shimmer': 'MDVP_Shimmer',
    'MDVP:Shimmer(dB)': 'MDVP_Shimmer_dB',
    'Shimmer:APQ3': 'Shimmer_APQ3',
    'Shimmer:APQ5': 'Shimmer_APQ5',
    'MDVP:APQ': 'MDVP_APQ',
    'Shimmer:DDA': 'Shimmer_DDA'
})

# Split features and target
X = df.drop('status', axis=1)
y = df['status']

feature_columns = X.columns.tolist()

# Train test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Feature Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Models dictionary
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
    "Decision Tree": DecisionTreeClassifier(class_weight="balanced", random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=42),
    "KNN": KNeighborsClassifier(),
    "SVM": SVC(probability=True, class_weight="balanced", random_state=42),
    "Naive Bayes": GaussianNB()
}

results = []

for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    pred = model.predict(X_test_scaled)
    results.append({
        "Model": name,
        "Accuracy": accuracy_score(y_test, pred),
        "Precision": precision_score(y_test, pred),
        "Recall": recall_score(y_test, pred),
        "F1 Score": f1_score(y_test, pred)
    })

results_df = pd.DataFrame(results).sort_values("F1 Score", ascending=False).reset_index(drop=True)
print(results_df)

best_model_name = results_df.iloc[0]["Model"]
best_model = models[best_model_name]
print("Best Model Selected:", best_model_name)

MODEL_DIR = Path('../trained_models')
MODEL_DIR.mkdir(exist_ok=True)

# Save best model, scaler, and columns list
joblib.dump(best_model, MODEL_DIR / "parkinson_model.pkl")
joblib.dump(scaler, MODEL_DIR / "parkinson_scaler.pkl")
joblib.dump(feature_columns, MODEL_DIR / "parkinson_columns.pkl")

print("Model and preprocessing assets saved successfully.")
