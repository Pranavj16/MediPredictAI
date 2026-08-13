
# ========================================
# Cell
# ========================================
import pandas as pd
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

# ========================================
# Cell
# ========================================
df = pd.read_csv('../datasets/diabetes/diabetes_prediction_dataset.csv')
df.head()
# ========================================
# Cell
# ========================================
print(df.shape)
print(df.info())
print(df.isnull().sum())
print(df.duplicated().sum())
print(df['diabetes'].value_counts())
# ========================================
# Cell
# ========================================
df = df.drop_duplicates()
# ========================================
# Cell
# ========================================
X = df.drop('diabetes', axis=1)
y = df['diabetes']
# ========================================
# Cell
# ========================================
X = pd.get_dummies(
    X,
    columns=['gender','smoking_history'],
    drop_first=False
)

feature_columns = X.columns.tolist()
# ========================================
# Cell
# ========================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
# ========================================
# Cell
# ========================================
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
# ========================================
# Cell
# ========================================
models = {
    'Logistic Regression': LogisticRegression(max_iter=1000),
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Random Forest': RandomForestClassifier(random_state=42),
    'KNN': KNeighborsClassifier(),
    'SVM': SVC(probability=True),
    'Naive Bayes': GaussianNB()
}

results=[]

for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    pred=model.predict(X_test_scaled)

    results.append({
        'Model':name,
        'Accuracy':accuracy_score(y_test,pred),
        'Precision':precision_score(y_test,pred),
        'Recall':recall_score(y_test,pred),
        'F1 Score':f1_score(y_test,pred)
    })

results_df=pd.DataFrame(results).sort_values(by='Accuracy',ascending=False)
results_df
# ========================================
# Cell
# ========================================
best_model_name = results_df.iloc[0]['Model']
best_model = models[best_model_name]

print(best_model_name)
# ========================================
# Cell
# ========================================
MODEL_DIR = Path('../trained_models')
MODEL_DIR.mkdir(exist_ok=True)

joblib.dump(best_model, MODEL_DIR/'diabetes_model.pkl')
joblib.dump(scaler, MODEL_DIR/'diabetes_scaler.pkl')
joblib.dump(feature_columns, MODEL_DIR/'diabetes_columns.pkl')

print('Saved successfully')
# ========================================
# Cell
# ========================================
model = joblib.load('../trained_models/diabetes_model.pkl')
scaler = joblib.load('../trained_models/diabetes_scaler.pkl')
columns = joblib.load('../trained_models/diabetes_columns.pkl')

sample = pd.DataFrame([{
    'gender':'Male',
    'age':25,
    'hypertension':0,
    'heart_disease':0,
    'smoking_history':'never',
    'bmi':22.5,
    'HbA1c_level':5.2,
    'blood_glucose_level':95
}])

sample = pd.get_dummies(sample, columns=['gender','smoking_history'])
sample = sample.reindex(columns=columns, fill_value=0)
sample = scaler.transform(sample)

print(model.predict(sample))
print(model.predict_proba(sample))