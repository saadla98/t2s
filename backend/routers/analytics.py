"""Analytics / EDA API router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.eda_service import (
    get_dashboard_summary, get_risk_distribution, get_module_distribution,
    get_correlations, get_age_distribution, get_manufacturer_distribution,
    get_risk_by_age_group, get_downtime_by_module, get_cost_by_risk
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard summary statistics."""
    return get_dashboard_summary(db)


@router.get("/risk-distribution")
def risk_distribution(db: Session = Depends(get_db)):
    """Get failure risk distribution."""
    return get_risk_distribution(db)


@router.get("/modules")
def module_distribution(db: Session = Depends(get_db)):
    """Get affected module distribution."""
    return get_module_distribution(db)


@router.get("/correlations")
def correlations(db: Session = Depends(get_db)):
    """Get feature correlation matrix."""
    return get_correlations(db)


@router.get("/age-distribution")
def age_distribution(db: Session = Depends(get_db)):
    """Get scanner age group distribution."""
    return get_age_distribution(db)


@router.get("/manufacturers")
def manufacturer_distribution(db: Session = Depends(get_db)):
    """Get manufacturer distribution."""
    return get_manufacturer_distribution(db)


@router.get("/risk-by-age")
def risk_by_age(db: Session = Depends(get_db)):
    """Get risk distribution by age group."""
    return get_risk_by_age_group(db)


@router.get("/downtime-by-module")
def downtime_by_module(db: Session = Depends(get_db)):
    """Get average downtime by affected module."""
    return get_downtime_by_module(db)


@router.get("/cost-by-risk")
def cost_by_risk(db: Session = Depends(get_db)):
    """Get average maintenance cost by risk level."""
    return get_cost_by_risk(db)
