"""
Evaluation des 3 modeles ML — resultats dans le terminal.

  - Dataset synthétique (662 lignes) — split 75/25 — test sur 25%
  - Dataset réel (50 lignes optima540) — test externe

Usage:
    python evaluate_models.py
"""
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

# ── Config ────────────────────────────────────────────────────────────────────
ML_DIR     = Path("backend/ml_models")
SYNTH_PATH = "CT_Scanner_Dataset_Engineered_T2S_with_Affected_Module.csv"
REAL_PATH  = "optima540_interventions_real_serials.csv"
RISK_LEVELS = ["Low", "Medium", "High"]

COMPONENT_MAP = {
    "DAS / cartes acquisition":     "DAS / Data Acquisition",
    "Console / informatique":       "Console / Software",
    "Gantry / positionnement":      "Mechanical / Gantry",
    "Tube RX / haute tension":      "Cooling / Tube",
    "Generateur HT / alimentation": "Power / Electronics",
    "Collimateur":                  "Detector / Sensors",
    "Table patient":                "Mechanical / Gantry",
    "Scanner CT - general":         "General Maintenance",
    "Scanner CT - général": "General Maintenance",
    "Générateur HT / alimentation": "Power / Electronics",
}

AGE_MEDIAN  = 7.0
COST_MEDIAN = 7515.19

# ── Load preprocessors & models ───────────────────────────────────────────────
scaler       = joblib.load(ML_DIR / "scaler.pkl")
le_module    = joblib.load(ML_DIR / "le_module.pkl")
feature_cols = joblib.load(ML_DIR / "feature_cols.pkl")

models = {
    "Logistic Regression": joblib.load(ML_DIR / "logistic_regression.pkl"),
    "Random Forest":       joblib.load(ML_DIR / "random_forest.pkl"),
    "XGBoost":             joblib.load(ML_DIR / "xgboost.pkl"),
}

le_target = LabelEncoder()
le_target.classes_ = np.array(RISK_LEVELS)

# ── Helper ────────────────────────────────────────────────────────────────────
def encode_module(val):
    try:    return le_module.transform([val])[0]
    except: return 0

def print_results(title, y_true, y_pred):
    acc  = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    rec  = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    f1   = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    cm   = confusion_matrix(y_true, y_pred, labels=RISK_LEVELS)

    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")
    print(f"  Accuracy  : {acc:.4f}  ({int(acc*len(y_true))}/{len(y_true)} correct)")
    print(f"  Precision : {prec:.4f}")
    print(f"  Recall    : {rec:.4f}")
    print(f"  F1 Score  : {f1:.4f}")
    print(f"\n  Confusion Matrix (rows=Actual, cols=Predicted):")
    print(f"           Low    Medium   High")
    labels = ["Low   ", "Medium", "High  "]
    for i, row in enumerate(cm):
        print(f"  {labels[i]}  {row[0]:5}  {row[1]:6}  {row[2]:6}")
    print(f"\n  Classification Report:")
    report = classification_report(y_true, y_pred, labels=RISK_LEVELS,
                                   target_names=RISK_LEVELS, zero_division=0)
    print("\n".join("  " + line for line in report.splitlines()))
    return f1

# ═══════════════════════════════════════════════════════════════════════════════
# DATASET 1 — Synthétique 662 lignes — split 75/25
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*55)
print("  DATASET SYNTHETIQUE -- 662 lignes -- Split 75/25")
print("="*55)

df_synth = pd.read_csv(SYNTH_PATH)
df_synth["Affected_Module_Encoded"] = df_synth["Affected_Module"].apply(encode_module)
df_synth["Target"] = le_target.transform(df_synth["Failure_Risk"])

X = scaler.transform(df_synth[feature_cols].values)
y = df_synth["Target"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)
print(f"  Train: {len(X_train)} lignes | Test: {len(X_test)} lignes")

best_model_name = None
best_f1 = -1
f1_scores = {}

for name, model in models.items():
    y_pred = model.predict(X_test)
    y_pred_labels = [RISK_LEVELS[p] for p in y_pred]
    y_test_labels = [RISK_LEVELS[p] for p in y_test]
    f1 = print_results(f"{name} -- Test synthetique (25%)", y_test_labels, y_pred_labels)
    f1_scores[name] = f1
    if f1 > best_f1:
        best_f1 = f1
        best_model_name = name

print(f"\n{'='*55}")
print(f"  MEILLEUR MODELE (synthétique): {best_model_name}")
print(f"  F1 Score: {best_f1:.4f}")
print(f"{'='*55}")

# ═══════════════════════════════════════════════════════════════════════════════
# DATASET 2 — Réel 50 lignes (GE Optima 540)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n\n" + "="*55)
print("  DATASET REEL -- 50 lignes (GE Optima 540)")
print("="*55)

df_real = pd.read_csv(REAL_PATH, sep=";")
df_real["Component"] = df_real["Component"].str.strip()
df_real["Affected_Module"] = df_real["Component"].map(COMPONENT_MAP).fillna("General Maintenance")
df_real["First_Date"] = pd.to_datetime(df_real["First_Date"], errors="coerce")
df_real["Last_Date"]  = pd.to_datetime(df_real["Last_Date"],  errors="coerce")

rows = []
for serial, group in df_real.groupby("Serial_Number"):
    n_total    = len(group)
    n_curative = (group["Maintenance_Type"] == "Curative").sum()
    total_dt   = group["Estimated_Downtime_Days"].sum()
    span_days  = max(1, (group["Last_Date"].max() - group["First_Date"].min()).days)
    span_months = max(1, span_days / 30.44)

    for _, row in group.iterrows():
        rows.append({
            "Age":                   AGE_MEDIAN,
            "Maintenance_Cost":      COST_MEDIAN,
            "Downtime":              row["Estimated_Downtime_Days"],
            "Maintenance_Frequency": n_total,
            "Failure_Event_Count":   int(n_curative),
            "MTBF":                  round(span_days / max(1, n_curative), 4),
            "Failure_Rate":          round(n_curative / span_months, 4),
            "Downtime_Per_Failure":  round(total_dt / max(1, n_curative), 4),
            "Maintenance_Intensity": round(n_total * (total_dt / max(1, n_total)), 4),
            "Affected_Module_Encoded": encode_module(row["Affected_Module"]),
            "Actual": row["Severity_Level"],
        })

df_eng = pd.DataFrame(rows)
df_eng[feature_cols] = df_eng[feature_cols].fillna(df_eng[feature_cols].median())
X_real = scaler.transform(df_eng[feature_cols].values)
y_real = df_eng["Actual"].values

print(f"  Lignes: {len(df_eng)}")

best_real_name = None
best_real_f1 = -1

for name, model in models.items():
    y_pred = [RISK_LEVELS[p] for p in model.predict(X_real)]
    f1 = print_results(f"{name} -- Test reel (50 lignes)", y_real, y_pred)
    if f1 > best_real_f1:
        best_real_f1 = f1
        best_real_name = name

print(f"\n{'='*55}")
print(f"  MEILLEUR MODELE (données réelles): {best_real_name}")
print(f"  F1 Score: {best_real_f1:.4f}")
print(f"{'='*55}")

# ── Tableau récapitulatif ─────────────────────────────────────────────────────
print("\n\n" + "="*55)
print("  RECAPITULATIF -- F1 Score par modele")
print("="*55)
print(f"  {'Modele':<22} {'Synthetique (25%)':>18} {'Reel (50 lignes)':>17}")
print(f"  {'-'*22} {'-'*18} {'-'*17}")
for name in models:
    f1_s = f1_scores.get(name, 0)
    y_pred_r = [RISK_LEVELS[p] for p in models[name].predict(X_real)]
    f1_r = f1_score(y_real, y_pred_r, average="weighted", zero_division=0)
    best_s = " <-- BEST" if name == best_model_name else ""
    best_r = " <-- BEST" if name == best_real_name else ""
    print(f"  {name:<22} {f1_s:>17.4f}{best_s}")
    print(f"  {'':22} {f1_r:>17.4f}{best_r}  (reel)")
    print()
