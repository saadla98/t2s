"""Configuration settings for the CT Scanner Risk Prediction Platform."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ML_MODELS_DIR = BASE_DIR / "ml_models"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
ML_MODELS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{BASE_DIR / 'ct_scanner.db'}"

DATASET_FILENAME = "CT_Scanner_Dataset_Engineered_T2S_with_Affected_Module.csv"

# Feature columns used for ML training (Historical_Risk_Index removed — target leakage)
FEATURE_COLUMNS = [
    "Age", "Maintenance_Cost", "Downtime", "Maintenance_Frequency",
    "Failure_Event_Count", "MTBF", "Failure_Rate",
    "Downtime_Per_Failure", "Maintenance_Intensity"
]

CATEGORICAL_FEATURES = ["Affected_Module"]

TARGET_COLUMN = "Failure_Risk"
MODULE_TARGET = "Affected_Module"

RISK_LEVELS = ["Low", "Medium", "High"]

AFFECTED_MODULES = [
    "Console / Software",
    "Detector / Sensors",
    "Power / Electronics",
    "Mechanical / Gantry",
    "Cooling / Tube",
    "DAS / Data Acquisition",
    "General Maintenance"
]

# Health Score weights
HEALTH_SCORE_WEIGHTS = {
    "Low": 85,    # base score for low risk
    "Medium": 50, # base score for medium risk
    "High": 15    # base score for high risk
}
