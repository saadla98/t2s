"""
Evaluate the trained model on real GE Optima 540 intervention data.
Compares model predictions (Failure_Risk) vs actual (Severity_Level).
"""
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ML_MODELS_DIR = Path("backend/ml_models")
REAL_DATA_PATH = "optima540_interventions_real_serials.csv"
RISK_LEVELS = ["Low", "Medium", "High"]

# Component → Affected_Module mapping
COMPONENT_MAP = {
    "DAS / cartes acquisition":         "DAS / Data Acquisition",
    "Console / informatique":           "Console / Software",
    "Gantry / positionnement":          "Mechanical / Gantry",
    "Tube RX / haute tension":          "Cooling / Tube",
    "Générateur HT / alimentation":     "Power / Electronics",
    "Gé­né­rateur HT / alimentation":    "Power / Electronics",
    "Collimateur":                      "Detector / Sensors",
    "Table patient":                    "Mechanical / Gantry",
    "Scanner CT - général":             "General Maintenance",
    "Scanner CT - général":   "General Maintenance",
}

# Medians from training data (fallback for unavailable features)
AGE_MEDIAN = 7.0
COST_MEDIAN = 7515.19

# ── Load real data ────────────────────────────────────────────────────────────
df = pd.read_csv(REAL_DATA_PATH, sep=";")

# Fix encoding issues in Component column
df["Component"] = df["Component"].str.strip()
df["Affected_Module"] = df["Component"].map(COMPONENT_MAP).fillna("General Maintenance")

# Parse dates
df["First_Date"] = pd.to_datetime(df["First_Date"], errors="coerce")
df["Last_Date"]  = pd.to_datetime(df["Last_Date"],  errors="coerce")

# ── Feature engineering per Serial_Number ────────────────────────────────────
def engineer_features(group):
    n_total     = len(group)
    n_curative  = (group["Maintenance_Type"] == "Curative").sum()

    total_downtime = group["Estimated_Downtime_Days"].sum()
    min_date = group["First_Date"].min()
    max_date = group["Last_Date"].max()
    span_days = max(1, (max_date - min_date).days)
    span_months = max(1, span_days / 30.44)

    mtbf = span_days / max(1, n_curative)
    failure_rate = n_curative / span_months
    downtime_per_failure = total_downtime / max(1, n_curative)
    maintenance_intensity = n_total * (total_downtime / max(1, n_total))

    rows = []
    for _, row in group.iterrows():
        rows.append({
            "Serial_Number":         row["Serial_Number"],
            "Intervention_ID":       row["Intervention_ID"],
            "Affected_Module":       row["Affected_Module"],
            "Actual_Severity":       row["Severity_Level"],
            "Maintenance_Type":      row["Maintenance_Type"],
            # Features
            "Age":                   AGE_MEDIAN,
            "Maintenance_Cost":      COST_MEDIAN,
            "Downtime":              row["Estimated_Downtime_Days"],
            "Maintenance_Frequency": n_total,
            "Failure_Event_Count":   n_curative,
            "MTBF":                  round(mtbf, 4),
            "Failure_Rate":          round(failure_rate, 4),
            "Downtime_Per_Failure":  round(downtime_per_failure, 4),
            "Maintenance_Intensity": round(maintenance_intensity, 4),
        })
    return pd.DataFrame(rows)

engineered = df.groupby("Serial_Number", group_keys=False).apply(engineer_features)
engineered = engineered.reset_index(drop=True)

print(f"Rows engineered: {len(engineered)}")
print(f"Affected_Module distribution:\n{engineered['Affected_Module'].value_counts()}\n")

# ── Load model & preprocessors ────────────────────────────────────────────────
model       = joblib.load(ML_MODELS_DIR / "xgboost.pkl")
scaler      = joblib.load(ML_MODELS_DIR / "scaler.pkl")
le_module   = joblib.load(ML_MODELS_DIR / "le_module.pkl")
feature_cols = joblib.load(ML_MODELS_DIR / "feature_cols.pkl")

print(f"Model feature_cols: {feature_cols}\n")

# ── Encode & predict ──────────────────────────────────────────────────────────
def encode_module(val):
    try:
        return le_module.transform([val])[0]
    except ValueError:
        return 0

engineered["Affected_Module_Encoded"] = engineered["Affected_Module"].apply(encode_module)

X = engineered[feature_cols].values
X_scaled = scaler.transform(X)

predictions = model.predict(X_scaled)
engineered["Predicted_Risk"] = [RISK_LEVELS[p] for p in predictions]

proba = model.predict_proba(X_scaled)
for i, level in enumerate(RISK_LEVELS):
    engineered[f"Proba_{level}"] = (proba[:, i] * 100).round(2)

# ── Results ───────────────────────────────────────────────────────────────────
correct = (engineered["Predicted_Risk"] == engineered["Actual_Severity"]).sum()
total   = len(engineered)
accuracy = correct / total * 100

print("=" * 60)
print(f"ACCURACY vs Severity_Level: {correct}/{total} = {accuracy:.1f}%")
print("=" * 60)

print("\nPrediction vs Actual per row:")
cols = ["Serial_Number", "Intervention_ID", "Affected_Module",
        "Actual_Severity", "Predicted_Risk", "Proba_Low", "Proba_Medium", "Proba_High"]
print(engineered[cols].to_string(index=False))

print("\nConfusion matrix (rows=Actual, cols=Predicted):")
from sklearn.metrics import confusion_matrix, classification_report
cm = confusion_matrix(engineered["Actual_Severity"], engineered["Predicted_Risk"], labels=RISK_LEVELS)
cm_df = pd.DataFrame(cm, index=[f"Actual_{r}" for r in RISK_LEVELS],
                         columns=[f"Pred_{r}" for r in RISK_LEVELS])
print(cm_df)

print("\nClassification Report:")
print(classification_report(engineered["Actual_Severity"], engineered["Predicted_Risk"],
                             labels=RISK_LEVELS, zero_division=0))

# Save results
out_path = "real_data_evaluation_results.csv"
engineered.to_csv(out_path, index=False)
print(f"\nResults saved -> {out_path}")
