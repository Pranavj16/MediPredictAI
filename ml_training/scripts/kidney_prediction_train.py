
# ========================================
# Cell
# ========================================
import pandas as pd
import numpy as np
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
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score

# ========================================
# Cell
# ========================================
df=pd.read_csv('../datasets/kidney/kidney_disease.csv')
df.head()
# ========================================
# Cell
# ========================================
print(df.shape)
print(df.info())
print(df.isnull().sum())
print(df['classification'].value_counts())
# ========================================
# Cell
# ========================================
df=df.replace('?',np.nan)
df=df.replace('\t?',np.nan)
df=df.replace('\tyes','yes')
df=df.replace('\tno','no')
df=df.replace('ckd\t','ckd')

if 'id' in df.columns:
    df=df.drop('id',axis=1)

# ========================================
# Cell
# ========================================
df['classification']=df['classification'].replace({'ckd':1,'notckd':0}).astype(int)
# ========================================
# Cell
# ========================================
X=df.drop('classification',axis=1)
y=df['classification']
# ========================================
# Cell
# ========================================
num_cols=X.select_dtypes(include=['int64','float64']).columns
cat_cols=X.select_dtypes(include=['object']).columns

num_imputer=SimpleImputer(strategy='median')
cat_imputer=SimpleImputer(strategy='most_frequent')

X[num_cols]=num_imputer.fit_transform(X[num_cols])
X[cat_cols]=cat_imputer.fit_transform(X[cat_cols])

# ========================================
# Cell
# ========================================
X=pd.get_dummies(X,columns=cat_cols,drop_first=False)
feature_columns=X.columns.tolist()
# ========================================
# Cell
# ========================================
X_train,X_test,y_train,y_test=train_test_split(
X,y,test_size=0.2,random_state=42,stratify=y)
# ========================================
# Cell
# ========================================
scaler=StandardScaler()

X_train_scaled=scaler.fit_transform(X_train)
X_test_scaled=scaler.transform(X_test)

# ========================================
# Cell
# ========================================
models={
'Logistic Regression':LogisticRegression(max_iter=1000),
'Decision Tree':DecisionTreeClassifier(random_state=42),
'Random Forest':RandomForestClassifier(random_state=42),
'KNN':KNeighborsClassifier(),
'SVM':SVC(probability=True),
'Naive Bayes':GaussianNB()
}

results=[]

for name,model in models.items():
    model.fit(X_train_scaled,y_train)
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
best_model_name=results_df.iloc[0]['Model']
best_model=models[best_model_name]
print(best_model_name)

MODEL_DIR=Path('../trained_models')
MODEL_DIR.mkdir(exist_ok=True)

joblib.dump(best_model,MODEL_DIR/'kidney_model.pkl')
joblib.dump(scaler,MODEL_DIR/'kidney_scaler.pkl')
joblib.dump(feature_columns,MODEL_DIR/'kidney_columns.pkl')

print('Saved Successfully')

# ========================================
# Cell
# ========================================
model=joblib.load('../trained_models/kidney_model.pkl')
scaler=joblib.load('../trained_models/kidney_scaler.pkl')
columns=joblib.load('../trained_models/kidney_columns.pkl')

sample=X.iloc[[0]].copy()
sample=sample.reindex(columns=columns,fill_value=0)
sample=scaler.transform(sample)

print(model.predict(sample))
print(model.predict_proba(sample))
