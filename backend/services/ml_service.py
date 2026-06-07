"""Machine Learning service — training, evaluation, model comparison, selection."""
import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
from sqlalchemy.orm import Session

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from xgboost import XGBClassifier

from models.scanner import Scanner, ModelMetric
from config import FEATURE_COLUMNS, CATEGORICAL_FEATURES, TARGET_COLUMN, ML_MODELS_DIR, RISK_LEVELS


def _prepare_data(db: Session):
    """Prepare training data from the database."""
    scanners = db.query(Scanner).all()
    if not scanners:
        raise ValueError("Aucune donnée dans la base. Importez d'abord le dataset.")

    records = []
    for s in scanners:
        record = {
            "Age": s.age,
            "Maintenance_Cost": s.maintenance_cost,
            "Downtime": s.downtime,
            "Maintenance_Frequency": s.maintenance_frequency,
            "Failure_Event_Count": s.failure_event_count,
            "Maintenance_Class": s.maintenance_class,
            "MTBF": s.mtbf,
            "Failure_Rate": s.failure_rate,
            "Downtime_Per_Failure": s.downtime_per_failure,
            "Maintenance_Intensity": s.maintenance_intensity,
            "Historical_Risk_Index": s.historical_risk_index,
            "Affected_Module": s.affected_module,
            "Failure_Risk": s.failure_risk,
        }
        records.append(record)

    df = pd.DataFrame(records)
    return df


def train_all_models(db: Session) -> dict:
    """Train Logistic Regression, Random Forest, and XGBoost. Return comparison."""
    df = _prepare_data(db)

    # Encode categorical features
    le_module = LabelEncoder()
    df["Affected_Module_Encoded"] = le_module.fit_transform(df["Affected_Module"])

    # Encode target
    le_target = LabelEncoder()
    le_target.classes_ = np.array(RISK_LEVELS)
    df["Target"] = le_target.transform(df[TARGET_COLUMN])

    # Feature matrix
    feature_cols = FEATURE_COLUMNS + ["Affected_Module_Encoded"]
    X = df[feature_cols].values
    y = df["Target"].values

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train/Test split (80/20, stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    # Define models
    models = {
        "Logistic Regression": LogisticRegression(
            C=1.0, solver="lbfgs", max_iter=1000, multi_class="multinomial", random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=10, min_samples_split=5, random_state=42, n_jobs=-1
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8, random_state=42,
            use_label_encoder=False, eval_metric="mlogloss"
        ),
    }

    # Stratified K-Fold for cross-validation
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    results = {}
    best_f1 = -1
    best_model_name = None

    # Clear old metrics
    db.query(ModelMetric).delete()
    db.commit()

    for name, model in models.items():
        # Train
        model.fit(X_train, y_train)

        # Predict
        y_pred = model.predict(X_test)

        # Metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        # Cross-validation
        cv_scores = cross_val_score(model, X_scaled, y, cv=skf, scoring="f1_weighted")
        cv_mean = float(cv_scores.mean())
        cv_std = float(cv_scores.std())

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred).tolist()

        # Classification report
        cr = classification_report(y_test, y_pred, target_names=RISK_LEVELS, output_dict=True)

        # Feature importance
        feat_imp = None
        if hasattr(model, "feature_importances_"):
            feat_imp = dict(zip(feature_cols, model.feature_importances_.tolist()))
        elif hasattr(model, "coef_"):
            # For logistic regression, use mean absolute coefficient
            imp = np.mean(np.abs(model.coef_), axis=0)
            feat_imp = dict(zip(feature_cols, imp.tolist()))

        # Track best
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name

        results[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "cv_mean": round(cv_mean, 4),
            "cv_std": round(cv_std, 4),
            "confusion_matrix": cm,
            "classification_report": cr,
            "feature_importance": feat_imp,
        }

        # Save to DB
        metric = ModelMetric(
            model_name=name,
            accuracy=round(acc, 4),
            precision=round(prec, 4),
            recall=round(rec, 4),
            f1_score=round(f1, 4),
            cv_mean=round(cv_mean, 4),
            cv_std=round(cv_std, 4),
            confusion_matrix=cm,
            classification_report=cr,
            is_best=0,
            feature_importance=feat_imp,
        )
        db.add(metric)

        # Save model to disk
        joblib.dump(model, ML_MODELS_DIR / f"{name.lower().replace(' ', '_')}.pkl")

    # Mark best model
    db.query(ModelMetric).filter(ModelMetric.model_name == best_model_name).update({"is_best": 1})
    db.commit()

    # Save scaler and encoders
    joblib.dump(scaler, ML_MODELS_DIR / "scaler.pkl")
    joblib.dump(le_module, ML_MODELS_DIR / "le_module.pkl")
    joblib.dump(le_target, ML_MODELS_DIR / "le_target.pkl")

    # Save feature column order
    joblib.dump(feature_cols, ML_MODELS_DIR / "feature_cols.pkl")

    return {
        "status": "success",
        "best_model": best_model_name,
        "best_f1": round(best_f1, 4),
        "models": results,
    }


def get_model_comparison(db: Session) -> dict:
    """Get stored model comparison results."""
    metrics = db.query(ModelMetric).order_by(ModelMetric.f1_score.desc()).all()
    if not metrics:
        return {"status": "no_models", "models": []}

    result = []
    best_model = None
    for m in metrics:
        entry = {
            "model_name": m.model_name,
            "accuracy": m.accuracy,
            "precision": m.precision,
            "recall": m.recall,
            "f1_score": m.f1_score,
            "cv_mean": m.cv_mean,
            "cv_std": m.cv_std,
            "confusion_matrix": m.confusion_matrix,
            "classification_report": m.classification_report,
            "feature_importance": m.feature_importance,
            "is_best": bool(m.is_best),
            "training_date": m.training_date.isoformat() if m.training_date else None,
        }
        if m.is_best:
            best_model = m.model_name
        result.append(entry)

    return {
        "status": "success",
        "best_model": best_model,
        "models": result,
    }


def train_module_classifier(db: Session) -> dict:
    """Train a secondary classifier to predict Affected_Module."""
    df = _prepare_data(db)

    # Features (excluding Affected_Module)
    le_target_risk = LabelEncoder()
    le_target_risk.classes_ = np.array(RISK_LEVELS)
    df["Risk_Encoded"] = le_target_risk.transform(df["Failure_Risk"])

    feature_cols_module = FEATURE_COLUMNS + ["Risk_Encoded"]
    X = df[feature_cols_module].values

    le_module = LabelEncoder()
    y = le_module.fit_transform(df["Affected_Module"])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200, max_depth=12, random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    # Save
    joblib.dump(model, ML_MODELS_DIR / "module_classifier.pkl")
    joblib.dump(scaler, ML_MODELS_DIR / "module_scaler.pkl")
    joblib.dump(le_module, ML_MODELS_DIR / "le_module_target.pkl")
    joblib.dump(feature_cols_module, ML_MODELS_DIR / "module_feature_cols.pkl")

    return {
        "status": "success",
        "accuracy": round(acc, 4),
        "f1_score": round(f1, 4),
        "classes": le_module.classes_.tolist(),
    }
