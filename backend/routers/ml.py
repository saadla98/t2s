"""Machine Learning API router (Admin Only conceptually)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.ml_service import train_all_models, get_model_comparison, train_module_classifier
from services.shap_service import get_shap_summary

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])


@router.post("/train")
def train_models(db: Session = Depends(get_db)):
    """
    Train Logistic Regression, Random Forest, and XGBoost models.
    Select the best one automatically.
    This is an Admin feature.
    """
    try:
        result = train_all_models(db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'entraînement: {str(e)}")


@router.post("/train-expert")
def train_expert_module(db: Session = Depends(get_db)):
    """
    Train the secondary classifier to predict Affected_Module.
    This is an Admin feature.
    """
    try:
        result = train_module_classifier(db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'entraînement: {str(e)}")


@router.get("/models")
def list_models(db: Session = Depends(get_db)):
    """Get comparison results of trained models."""
    return get_model_comparison(db)


@router.get("/feature-importance")
def feature_importance(model_name: str = "random_forest"):
    """Get global SHAP feature importance for a model."""
    try:
        return get_shap_summary(model_name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
