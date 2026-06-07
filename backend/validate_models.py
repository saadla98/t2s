"""Script to investigate target leakage and produce ML validation report."""
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from xgboost import XGBClassifier
import json

df = pd.read_csv('data/CT_Scanner_Dataset_Engineered_T2S_with_Affected_Module.csv')

print("=== DATASET INFO ===")
print(f"Shape: {df.shape}")
print("Risk distribution:")
print(df['Failure_Risk'].value_counts())
print()

# Encode
le_module = LabelEncoder()
df['Affected_Module_Encoded'] = le_module.fit_transform(df['Affected_Module'])

RISK_LEVELS = ['Low', 'Medium', 'High']
le_target = LabelEncoder()
le_target.classes_ = np.array(RISK_LEVELS)
df['Target'] = le_target.transform(df['Failure_Risk'])

# Check for Maintenance_Class leakage
print("=== LEAKAGE CHECK ===")
print("Maintenance_Class value counts:")
print(df['Maintenance_Class'].value_counts())
print()
print("Cross-tab Maintenance_Class vs Failure_Risk:")
print(pd.crosstab(df['Maintenance_Class'], df['Failure_Risk']))
print()

# Feature set WITHOUT potential leakers
SAFE_FEATURES = ['Age', 'Maintenance_Cost', 'Downtime', 'Maintenance_Frequency',
                 'Failure_Event_Count', 'MTBF', 'Failure_Rate', 'Downtime_Per_Failure',
                 'Maintenance_Intensity', 'Historical_Risk_Index', 'Affected_Module_Encoded']

X = df[SAFE_FEATURES].values
y = df['Target'].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

print("=== MODEL EVALUATION (WITHOUT Maintenance_Class) ===")
models = {
    'Logistic Regression': LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=10, min_samples_split=5, random_state=42, n_jobs=-1),
    'XGBoost': XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1, subsample=0.8,
                              colsample_bytree=0.8, random_state=42, eval_metric='mlogloss')
}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    cv = cross_val_score(model, X_scaled, y, cv=skf, scoring='f1_weighted')
    cm = confusion_matrix(y_test, y_pred)
    print(f"\n--- {name} ---")
    print(f"  Test Accuracy: {acc:.4f}")
    print(f"  Test F1 (weighted): {f1:.4f}")
    print(f"  CV F1: {cv.mean():.4f} +/- {cv.std():.4f}")
    print(f"  Confusion Matrix:")
    print(cm)
    print(classification_report(y_test, y_pred, target_names=RISK_LEVELS))
    if hasattr(model, 'feature_importances_'):
        imps = sorted(zip(SAFE_FEATURES, model.feature_importances_), key=lambda x: -x[1])
        print("  Feature Importances:")
        for feat, imp in imps:
            print(f"    {feat}: {imp:.4f}")
