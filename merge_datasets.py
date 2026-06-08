"""
Merge real GE Optima 540 data (interventions CSV + scanners Excel) with synthetic dataset.
Output: CT_Scanner_Dataset_Merged.csv  (722 rows)
"""
import pandas as pd
import numpy as np
from pathlib import Path

REAL_PATH    = "optima540_interventions_real_serials.csv"
SCANNER_PATH = "optima540_scanners_real_serials.xlsx"
OLD_PATH     = "CT_Scanner_Dataset_Engineered_T2S_with_Affected_Module.csv"
OUT_PATH     = "CT_Scanner_Dataset_Merged.csv"

COMPONENT_MAP = {
    "DAS / cartes acquisition":      "DAS / Data Acquisition",
    "Console / informatique":        "Console / Software",
    "Gantry / positionnement":       "Mechanical / Gantry",
    "Tube RX / haute tension":       "Cooling / Tube",
    "Générateur HT / alimentation": "Power / Electronics",
    "Collimateur":                   "Detector / Sensors",
    "Table patient":                 "Mechanical / Gantry",
    "Scanner CT - général": "General Maintenance",
}

MAINTENANCE_TYPE_TO_CLASS = {
    "Curative":    2,
    "Préventive": 1,
    "À vérifier": 2,
}

# Medians from old dataset (for fields we can't compute from real data)
df_old = pd.read_csv(OLD_PATH)
AGE_REAL        = 10           # GE Optima 540 ~2015 purchase, interventions 2025
COST_MEDIAN     = df_old["Maintenance_Cost"].median()
HRI_MEDIAN      = df_old["Historical_Risk_Index"].median()

# ── Load & prepare real data ─────────────────────────────────────────────────
df_real = pd.read_csv(REAL_PATH, sep=";")
df_real["Component"]  = df_real["Component"].str.strip()
df_real["Affected_Module"] = df_real["Component"].map(COMPONENT_MAP).fillna("General Maintenance")
df_real["First_Date"] = pd.to_datetime(df_real["First_Date"], errors="coerce")
df_real["Last_Date"]  = pd.to_datetime(df_real["Last_Date"],  errors="coerce")

# ── Engineer features per Serial_Number then keep per-intervention row ────────
rows = []
for serial, group in df_real.groupby("Serial_Number"):
    n_total    = len(group)
    n_curative = (group["Maintenance_Type"] == "Curative").sum()

    total_downtime = group["Estimated_Downtime_Days"].sum()
    min_date  = group["First_Date"].min()
    max_date  = group["Last_Date"].max()
    span_days = max(1, (max_date - min_date).days)
    span_months = max(1, span_days / 30.44)

    mtbf               = span_days / max(1, n_curative)
    failure_rate       = n_curative / span_months
    downtime_per_fail  = total_downtime / max(1, n_curative)
    maint_intensity    = n_total * (total_downtime / max(1, n_total))

    for _, row in group.iterrows():
        rows.append({
            "Device_ID":              row["Intervention_ID"],
            "Device_Type":            "CT Scanner",
            "Purchase_Date":          "2015-01-01",
            "Age":                    AGE_REAL,
            "Manufacturer":           "GE",
            "Model":                  "GE Optima 540",
            "Country":                "Morocco",
            "Maintenance_Cost":       COST_MEDIAN,
            "Downtime":               row["Estimated_Downtime_Days"],
            "Maintenance_Frequency":  n_total,
            "Failure_Event_Count":    int(n_curative),
            "Maintenance_Class":      MAINTENANCE_TYPE_TO_CLASS.get(row["Maintenance_Type"], 2),
            "Maintenance_Report":     str(row["Problem_Action_Summary"]),
            "MTBF":                   round(mtbf, 4),
            "Failure_Rate":           round(failure_rate, 4),
            "Downtime_Per_Failure":   round(downtime_per_fail, 4),
            "Maintenance_Intensity":  round(maint_intensity, 4),
            "Historical_Risk_Index":  HRI_MEDIAN,
            "Failure_Risk":           row["Severity_Level"],
            "Affected_Module":        row["Affected_Module"],
        })

df_new_rows = pd.DataFrame(rows)

# ── Scanner Excel (per-scanner aggregated data) ───────────────────────────────
df_scanners = pd.read_excel(SCANNER_PATH)

df_scanners["First_Intervention_Date"] = pd.to_datetime(df_scanners["First_Intervention_Date"], errors="coerce")
df_scanners["Last_Intervention_Date"]  = pd.to_datetime(df_scanners["Last_Intervention_Date"],  errors="coerce")

scanner_rows = []
for _, row in df_scanners.iterrows():
    span_days   = max(1, (row["Last_Intervention_Date"] - row["First_Intervention_Date"]).days)
    span_months = max(1, span_days / 30.44)
    n_failures  = max(1, row["Failure_Event_Count"])

    mtbf              = span_days / n_failures
    failure_rate      = row["Failure_Event_Count"] / span_months
    downtime_per_fail = row["Total_Downtime_Days"] / n_failures
    maint_intensity   = row["Maintenance_Frequency"] * row["Average_Downtime_Days"]

    # Maintenance_Class: mostly corrective → 2, preventive only → 1, mixed → 2
    if row["Corrective_Count"] == 0 and row["Preventive_Count"] > 0:
        maint_class = 1
    else:
        maint_class = 2

    component = str(row["Dominant_Component"]).strip()
    affected_module = COMPONENT_MAP.get(component, "General Maintenance")

    scanner_rows.append({
        "Device_ID":              f"SCAN_{row['Serial_Number']}",
        "Device_Type":            "CT Scanner",
        "Purchase_Date":          "2015-01-01",
        "Age":                    AGE_REAL,
        "Manufacturer":           "GE",
        "Model":                  "GE Optima 540",
        "Country":                "Morocco",
        "Maintenance_Cost":       COST_MEDIAN,
        "Downtime":               row["Total_Downtime_Days"],
        "Maintenance_Frequency":  row["Maintenance_Frequency"],
        "Failure_Event_Count":    int(row["Failure_Event_Count"]),
        "Maintenance_Class":      maint_class,
        "Maintenance_Report":     str(row["Latest_Problem_Action"]),
        "MTBF":                   round(mtbf, 4),
        "Failure_Rate":           round(failure_rate, 4),
        "Downtime_Per_Failure":   round(downtime_per_fail, 4),
        "Maintenance_Intensity":  round(maint_intensity, 4),
        "Historical_Risk_Index":  HRI_MEDIAN,
        "Failure_Risk":           row["Business_Risk_Level"],
        "Affected_Module":        affected_module,
    })

df_scanner_rows = pd.DataFrame(scanner_rows)

# ── Merge all three ───────────────────────────────────────────────────────────
df_merged = pd.concat([df_old, df_new_rows, df_scanner_rows], ignore_index=True)
df_merged.to_csv(OUT_PATH, index=False)

print(f"Old dataset      : {len(df_old)} rows")
print(f"Interventions CSV: {len(df_new_rows)} rows")
print(f"Scanners Excel   : {len(df_scanner_rows)} rows")
print(f"Merged total     : {len(df_merged)} rows  -> {OUT_PATH}")
print(f"\nFailure_Risk distribution:")
print(df_merged["Failure_Risk"].value_counts())
