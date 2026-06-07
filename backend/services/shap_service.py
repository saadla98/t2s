"""SHAP explainability service."""
import numpy as np
import joblib
import shap
from config import ML_MODELS_DIR, FEATURE_COLUMNS


def get_shap_summary(model_name: str = "random_forest") -> dict:
    """Get SHAP feature importance summary for a model."""
    model_path = ML_MODELS_DIR / f"{model_name}.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Modèle {model_name} non trouvé.")

    model = joblib.load(model_path)
    scaler = joblib.load(ML_MODELS_DIR / "scaler.pkl")
    feature_cols = joblib.load(ML_MODELS_DIR / "feature_cols.pkl")

    # We need some background data — use the model's training data
    # For efficiency, we generate synthetic representative data
    np.random.seed(42)
    n_samples = 100
    background = np.random.randn(n_samples, len(feature_cols))

    try:
        if model_name in ["random_forest", "xgboost"]:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(background)
        else:
            explainer = shap.LinearExplainer(model, background)
            shap_values = explainer.shap_values(background)

        # Calculate mean absolute SHAP values per feature
        if isinstance(shap_values, list):
            # Multi-class: average across classes
            mean_shap = np.mean([np.mean(np.abs(sv), axis=0) for sv in shap_values], axis=0)
        else:
            if len(shap_values.shape) == 3:
                # Shape (n_samples, n_features, n_classes) - Average over samples and classes
                mean_shap = np.mean(np.abs(shap_values), axis=(0, 2))
            else:
                mean_shap = np.mean(np.abs(shap_values), axis=0)

        importance = dict(zip(feature_cols, mean_shap.tolist()))
        sorted_importance = dict(sorted(importance.items(), key=lambda x: -x[1]))

        return {
            "status": "success",
            "model_name": model_name,
            "feature_importance": sorted_importance,
            "features": feature_cols,
        }

    except Exception as e:
        # Fallback to model's built-in feature importance
        if hasattr(model, "feature_importances_"):
            importance = dict(zip(feature_cols, model.feature_importances_.tolist()))
            sorted_importance = dict(sorted(importance.items(), key=lambda x: -x[1]))
            return {
                "status": "fallback",
                "model_name": model_name,
                "feature_importance": sorted_importance,
                "features": feature_cols,
                "note": f"SHAP indisponible, utilisation de l'importance intégrée. Erreur: {str(e)}"
            }
        return {"status": "error", "message": str(e)}


def get_shap_for_prediction(scanner_data: dict, model_name: str = "random_forest") -> dict:
    """Get SHAP explanation for a single prediction."""
    model_path = ML_MODELS_DIR / f"{model_name}.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Modèle {model_name} non trouvé.")

    model = joblib.load(model_path)
    scaler = joblib.load(ML_MODELS_DIR / "scaler.pkl")
    le_module = joblib.load(ML_MODELS_DIR / "le_module.pkl")
    feature_cols = joblib.load(ML_MODELS_DIR / "feature_cols.pkl")

    # Prepare features
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
            features.append(float(scanner_data.get(col, 0)))

    X = np.array([features])
    X_scaled = scaler.transform(X)

    try:
        if model_name in ["random_forest", "xgboost"]:
            explainer = shap.TreeExplainer(model)
        else:
            np.random.seed(42)
            background = np.random.randn(50, len(feature_cols))
            explainer = shap.LinearExplainer(model, background)

        shap_values = explainer.shap_values(X_scaled)

        # For multi-class, pick the predicted class
        prediction = model.predict(X_scaled)[0]

        if isinstance(shap_values, list):
            sv = shap_values[prediction][0]
        else:
            if len(shap_values.shape) == 3:
                sv = shap_values[0, :, prediction]
            else:
                sv = shap_values[0]

        contributions = dict(zip(feature_cols, sv.tolist()))
        sorted_contributions = dict(sorted(contributions.items(), key=lambda x: -abs(x[1])))

        return {
            "status": "success",
            "contributions": sorted_contributions,
            "features": feature_cols,
            "predicted_class": int(prediction),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
