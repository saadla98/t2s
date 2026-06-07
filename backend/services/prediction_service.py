"""Prediction service — risk prediction, health score, recommendations."""
import numpy as np
import joblib
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime
from sklearn.preprocessing import LabelEncoder

from models.scanner import Prediction, Scanner
from config import ML_MODELS_DIR, RISK_LEVELS, HEALTH_SCORE_WEIGHTS, FEATURE_COLUMNS


def _load_model(model_name: str = None):
    """Load the best trained model and preprocessors."""
    if model_name is None:
        # Try to load best model in order of preference
        for name in ["xgboost", "random_forest", "logistic_regression"]:
            path = ML_MODELS_DIR / f"{name}.pkl"
            if path.exists():
                model = joblib.load(path)
                break
        else:
            raise FileNotFoundError("Aucun modèle entraîné trouvé. Entraînez d'abord les modèles.")
    else:
        path = ML_MODELS_DIR / f"{model_name}.pkl"
        model = joblib.load(path)

    scaler = joblib.load(ML_MODELS_DIR / "scaler.pkl")
    le_module = joblib.load(ML_MODELS_DIR / "le_module.pkl")
    feature_cols = joblib.load(ML_MODELS_DIR / "feature_cols.pkl")

    return model, scaler, le_module, feature_cols


def calculate_health_score(probabilities: dict) -> float:
    """Calculate a 0-100 health score based on risk probabilities."""
    # Weighted average: Low risk contributes positively, High negatively
    score = (
        probabilities.get("Low", 0) * 95 +
        probabilities.get("Medium", 0) * 55 +
        probabilities.get("High", 0) * 12
    )
    return round(min(max(score, 0), 100), 1)


def generate_recommendation(risk_level: str, health_score: float, probabilities: dict) -> dict:
    """Generate intelligent maintenance recommendation."""
    recommendations = {
        "Low": {
            "level": "Low",
            "level_fr": "Faible",
            "icon": "✅",
            "color": "green",
            "title": "Situation Normale",
            "message": "Le scanner fonctionne dans les paramètres normaux. Continuer la surveillance de routine.",
            "actions": [
                "Maintenir le programme de maintenance préventive actuel",
                "Prochaine inspection selon le calendrier standard",
                "Documenter les observations dans le rapport de maintenance"
            ],
            "urgency": "Aucune action immédiate requise",
            "next_review": "Selon le calendrier de maintenance standard"
        },
        "Medium": {
            "level": "Medium",
            "level_fr": "Modéré",
            "icon": "⚠️",
            "color": "amber",
            "title": "Attention Requise",
            "message": "Des indicateurs de risque modéré ont été détectés. Une maintenance préventive est recommandée.",
            "actions": [
                "Planifier une maintenance préventive dans les 2 semaines",
                "Augmenter la fréquence de surveillance",
                "Vérifier les composants identifiés comme à risque",
                "Préparer les pièces de rechange potentiellement nécessaires"
            ],
            "urgency": "Action préventive recommandée sous 14 jours",
            "next_review": "Dans 1 semaine"
        },
        "High": {
            "level": "High",
            "level_fr": "Élevé",
            "icon": "🚨",
            "color": "red",
            "title": "Intervention Immédiate Recommandée",
            "message": "Le scanner présente un risque élevé de panne. Une intervention immédiate est fortement recommandée.",
            "actions": [
                "Intervention immédiate du technicien qualifié",
                "Escalader au responsable maintenance",
                "Envisager l'arrêt préventif du scanner si possible",
                "Commander les pièces de rechange critiques",
                "Préparer un scanner de remplacement si disponible"
            ],
            "urgency": "Action immédiate requise — Priorité maximale",
            "next_review": "Suivi quotidien jusqu'à résolution"
        }
    }

    rec = recommendations.get(risk_level, recommendations["Medium"])
    rec["health_score"] = health_score
    rec["probabilities"] = probabilities
    return rec


def predict_risk(db: Session, scanner_data: dict, technician_name: str = None,
                 technician_role: str = None, notes: str = None) -> dict:
    """Predict failure risk for given scanner parameters."""
    model, scaler, le_module, feature_cols = _load_model()

    # Prepare feature vector
    features = []
    for col in feature_cols:
        if col == "Affected_Module_Encoded":
            module_val = scanner_data.get("Affected_Module", "Console / Software")
            try:
                encoded = le_module.transform([module_val])[0]
            except ValueError:
                encoded = 0
            features.append(encoded)
        else:
            val = scanner_data.get(col)
            features.append(float(val if val not in [None, ""] else 0.0))

    X = np.array([features])
    X_scaled = scaler.transform(X)

    # Predict class and probabilities
    prediction = model.predict(X_scaled)[0]
    risk_level = RISK_LEVELS[prediction]

    probabilities = {}
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_scaled)[0]
        for i, level in enumerate(RISK_LEVELS):
            probabilities[level] = round(float(proba[i]) * 100, 2)
    else:
        probabilities = {level: (100.0 if level == risk_level else 0.0) for level in RISK_LEVELS}

    # Health score
    health_score = calculate_health_score(
        {k: v / 100 for k, v in probabilities.items()}
    )

    # Recommendation
    recommendation = generate_recommendation(risk_level, health_score, probabilities)

    # Save prediction to history
    pred_record = Prediction(
        device_id=scanner_data.get("Device_ID", "MANUAL"),
        scanner_data=scanner_data,
        predicted_risk=risk_level,
        risk_probabilities=probabilities,
        health_score=health_score,
        recommendation=recommendation["message"],
        technician_name=technician_name,
        technician_role=technician_role,
        notes=notes,
    )
    db.add(pred_record)
    db.commit()
    db.refresh(pred_record)

    return {
        "prediction_id": pred_record.id,
        "risk_level": risk_level,
        "probabilities": probabilities,
        "health_score": health_score,
        "recommendation": recommendation,
        "timestamp": pred_record.created_at.isoformat() if pred_record.created_at else datetime.now().isoformat(),
    }


def predict_module(scanner_data: dict) -> dict:
    """Predict the most likely affected module."""
    try:
        model = joblib.load(ML_MODELS_DIR / "module_classifier.pkl")
        scaler = joblib.load(ML_MODELS_DIR / "module_scaler.pkl")
        le_module = joblib.load(ML_MODELS_DIR / "le_module_target.pkl")
        feature_cols = joblib.load(ML_MODELS_DIR / "module_feature_cols.pkl")
    except FileNotFoundError:
        raise FileNotFoundError("Module classifier non entraîné. Entraînez d'abord le classifieur expert.")

    # Prepare features
    le_risk = LabelEncoder()
    le_risk.classes_ = np.array(RISK_LEVELS)

    features = []
    for col in feature_cols:
        if col == "Risk_Encoded":
            risk_val = scanner_data.get("Failure_Risk", "Medium")
            try:
                encoded = le_risk.transform([risk_val])[0]
            except ValueError:
                encoded = 1
            features.append(encoded)
        else:
            val = scanner_data.get(col)
            features.append(float(val if val not in [None, ""] else 0.0))

    X = np.array([features])
    X_scaled = scaler.transform(X)

    prediction = model.predict(X_scaled)[0]
    module_name = le_module.inverse_transform([prediction])[0]

    probabilities = {}
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_scaled)[0]
        for i, cls in enumerate(le_module.classes_):
            probabilities[cls] = round(float(proba[i]) * 100, 2)

    return {
        "predicted_module": module_name,
        "module_probabilities": probabilities,
    }


def get_prediction_history(db: Session, limit: int = 50) -> list:
    """Get prediction history."""
    preds = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(limit).all()
    return [
        {
            "id": p.id,
            "device_id": p.device_id,
            "predicted_risk": p.predicted_risk,
            "risk_probabilities": p.risk_probabilities,
            "health_score": p.health_score,
            "recommendation": p.recommendation,
            "technician_name": p.technician_name,
            "technician_role": p.technician_role,
            "notes": p.notes,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in preds
    ]


def get_prediction_by_id(db: Session, prediction_id: int) -> dict:
    """Get a specific prediction by ID."""
    p = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not p:
        return None
    return {
        "id": p.id,
        "device_id": p.device_id,
        "scanner_data": p.scanner_data,
        "predicted_risk": p.predicted_risk,
        "risk_probabilities": p.risk_probabilities,
        "health_score": p.health_score,
        "predicted_module": p.predicted_module,
        "recommendation": p.recommendation,
        "technician_name": p.technician_name,
        "technician_role": p.technician_role,
        "notes": p.notes,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }
