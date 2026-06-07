"""Data pipeline service — CSV import, cleaning, validation, feature engineering."""
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy.orm import Session
from models.scanner import Scanner
from config import DATA_DIR, DATASET_FILENAME, AFFECTED_MODULES


def load_csv(filepath: Path = None) -> pd.DataFrame:
    """Load the CT Scanner dataset from CSV."""
    if filepath is None:
        filepath = DATA_DIR / DATASET_FILENAME
    df = pd.read_csv(filepath)
    return df


def validate_data(df: pd.DataFrame) -> dict:
    """Validate data quality and return a report."""
    report = {
        "total_records": len(df),
        "columns": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicates": int(df.duplicated(subset=["Device_ID"]).sum()),
        "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "risk_distribution": df["Failure_Risk"].value_counts().to_dict() if "Failure_Risk" in df.columns else {},
        "module_distribution": df["Affected_Module"].value_counts().to_dict() if "Affected_Module" in df.columns else {},
        "negative_costs": int((df["Maintenance_Cost"] < 0).sum()) if "Maintenance_Cost" in df.columns else 0,
        "age_range": {
            "min": int(df["Age"].min()) if "Age" in df.columns else None,
            "max": int(df["Age"].max()) if "Age" in df.columns else None,
        },
        "issues": []
    }

    if report["duplicates"] > 0:
        report["issues"].append(f"{report['duplicates']} Device_ID en doublon détectés")
    if report["negative_costs"] > 0:
        report["issues"].append(f"{report['negative_costs']} coûts de maintenance négatifs détectés")
    if any(v > 0 for v in report["missing_values"].values()):
        report["issues"].append("Valeurs manquantes détectées")

    return report


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the dataset: handle negatives, missing values, outliers."""
    df = df.copy()

    # Clip negative maintenance costs to 0
    if "Maintenance_Cost" in df.columns:
        df["Maintenance_Cost"] = df["Maintenance_Cost"].clip(lower=0)

    # Drop duplicates by Device_ID, keep first
    df = df.drop_duplicates(subset=["Device_ID"], keep="first")

    # Fill any missing numeric columns with median
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())

    # Fill missing categorical columns with mode
    cat_cols = df.select_dtypes(include=["object"]).columns
    for col in cat_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].mode()[0])

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived features for enhanced prediction."""
    df = df.copy()

    # Scanner Age Group
    def age_group(age):
        if age <= 4:
            return "Jeune"
        elif age <= 8:
            return "Moyen"
        else:
            return "Ancien"
    df["Scanner_Age_Group"] = df["Age"].apply(age_group)

    # Failure Frequency Level
    def failure_freq(count):
        if count <= 1:
            return "Faible"
        elif count <= 3:
            return "Modéré"
        else:
            return "Élevé"
    df["Failure_Frequency_Level"] = df["Failure_Event_Count"].apply(failure_freq)

    # Maintenance Efficiency Score (higher is better)
    df["Maintenance_Efficiency_Score"] = df["MTBF"] / (df["Maintenance_Cost"].clip(lower=1) / 1000 + 1)

    # Downtime Severity
    def downtime_sev(dt):
        if dt < 5:
            return "Faible"
        elif dt <= 15:
            return "Modéré"
        else:
            return "Sévère"
    df["Downtime_Severity"] = df["Downtime"].apply(downtime_sev)

    # Risk Indicator Composite (weighted)
    df["Risk_Indicator_Composite"] = (
        0.35 * df["Failure_Rate"] +
        0.35 * df["Historical_Risk_Index"] +
        0.30 * (df["Maintenance_Intensity"] / df["Maintenance_Intensity"].max())
    )

    return df


def import_to_database(db: Session, df: pd.DataFrame) -> int:
    """Import processed DataFrame into the SQLite database."""
    # Clear existing scanner data
    db.query(Scanner).delete()
    db.commit()

    count = 0
    for _, row in df.iterrows():
        scanner = Scanner(
            device_id=row.get("Device_ID", ""),
            device_type=row.get("Device_Type", "CT Scanner"),
            purchase_date=str(row.get("Purchase_Date", "")),
            age=int(row.get("Age", 0)),
            manufacturer=row.get("Manufacturer", ""),
            model=row.get("Model", ""),
            country=row.get("Country", ""),
            maintenance_cost=float(row.get("Maintenance_Cost", 0)),
            downtime=float(row.get("Downtime", 0)),
            maintenance_frequency=int(row.get("Maintenance_Frequency", 0)),
            failure_event_count=int(row.get("Failure_Event_Count", 0)),
            maintenance_class=int(row.get("Maintenance_Class", 0)),
            maintenance_report=row.get("Maintenance_Report", ""),
            mtbf=float(row.get("MTBF", 0)),
            failure_rate=float(row.get("Failure_Rate", 0)),
            downtime_per_failure=float(row.get("Downtime_Per_Failure", 0)),
            maintenance_intensity=float(row.get("Maintenance_Intensity", 0)),
            historical_risk_index=float(row.get("Historical_Risk_Index", 0)),
            failure_risk=row.get("Failure_Risk", ""),
            affected_module=row.get("Affected_Module", ""),
            scanner_age_group=row.get("Scanner_Age_Group", ""),
            failure_frequency_level=row.get("Failure_Frequency_Level", ""),
            maintenance_efficiency_score=float(row.get("Maintenance_Efficiency_Score", 0)),
            downtime_severity=row.get("Downtime_Severity", ""),
            risk_indicator_composite=float(row.get("Risk_Indicator_Composite", 0)),
        )
        db.add(scanner)
        count += 1

    db.commit()
    return count


def run_full_pipeline(db: Session, filepath: Path = None) -> dict:
    """Run the complete data engineering pipeline."""
    # Step 1: Load
    df = load_csv(filepath)

    # Step 2: Validate
    validation_report = validate_data(df)

    # Step 3: Clean
    df_clean = clean_data(df)

    # Step 4: Feature Engineering
    df_engineered = engineer_features(df_clean)

    # Step 5: Import to DB
    record_count = import_to_database(db, df_engineered)

    return {
        "status": "success",
        "records_imported": record_count,
        "validation": validation_report,
        "features_created": [
            "Scanner_Age_Group", "Failure_Frequency_Level",
            "Maintenance_Efficiency_Score", "Downtime_Severity",
            "Risk_Indicator_Composite"
        ]
    }
