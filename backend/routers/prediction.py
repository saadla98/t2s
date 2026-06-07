"""Prediction API router."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from database import get_db
from services.prediction_service import (
    predict_risk, predict_module, get_prediction_history, get_prediction_by_id
)
from services.shap_service import get_shap_for_prediction
from services.pdf_service import generate_prediction_report


router = APIRouter(prefix="/api/predict", tags=["Prediction"])


class PredictionRequest(BaseModel):
    scanner_data: Dict[str, Any]
    technician_name: Optional[str] = None
    technician_role: Optional[str] = "technician"
    notes: Optional[str] = None


class ExpertPredictionRequest(BaseModel):
    scanner_data: Dict[str, Any]


@router.post("/risk")
def calculate_risk(request: PredictionRequest, db: Session = Depends(get_db)):
    """Predict failure risk for a scanner."""
    try:
        result = predict_risk(
            db,
            scanner_data=request.scanner_data,
            technician_name=request.technician_name,
            technician_role=request.technician_role,
            notes=request.notes
        )
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/module")
def predict_affected_module(request: ExpertPredictionRequest):
    """Predict the likely affected module (Expert Mode)."""
    try:
        return predict_module(request.scanner_data)
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
def prediction_history(limit: int = 50, db: Session = Depends(get_db)):
    """Get the history of predictions."""
    return get_prediction_history(db, limit)


@router.get("/{prediction_id}/shap")
def prediction_explanation(prediction_id: int, model_name: str = "random_forest", db: Session = Depends(get_db)):
    """Get SHAP explanation for a specific prediction."""
    pred = get_prediction_by_id(db, prediction_id)
    if not pred:
        raise HTTPException(status_code=404, detail="Prédiction non trouvée")
    
    try:
        return get_shap_for_prediction(pred["scanner_data"], model_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{prediction_id}/report.pdf")
def download_prediction_report(prediction_id: int, db: Session = Depends(get_db)):
    """Generate and download a PDF report for a prediction."""
    pred = get_prediction_by_id(db, prediction_id)
    if not pred:
        raise HTTPException(status_code=404, detail="Prédiction non trouvée")
    
    try:
        pdf_bytes = generate_prediction_report(pred)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=rapport_analyse_{prediction_id}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de génération PDF: {str(e)}")
