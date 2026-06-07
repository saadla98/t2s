"""Data pipeline API router."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models.scanner import Scanner
from services.data_pipeline import run_full_pipeline, load_csv, validate_data
from config import DATA_DIR, DATASET_FILENAME
from pathlib import Path
import shutil

router = APIRouter(prefix="/api/data", tags=["Data Pipeline"])


@router.post("/import")
def import_dataset(db: Session = Depends(get_db)):
    """Import and process the CSV dataset."""
    filepath = DATA_DIR / DATASET_FILENAME
    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"Dataset non trouvé: {DATASET_FILENAME}")

    result = run_full_pipeline(db, filepath)
    return result


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a CSV file and process it."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers CSV sont acceptés.")

    filepath = DATA_DIR / file.filename
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    result = run_full_pipeline(db, filepath)
    return result


@router.get("/status")
def data_status(db: Session = Depends(get_db)):
    """Get current data status."""
    count = db.query(Scanner).count()
    filepath = DATA_DIR / DATASET_FILENAME
    return {
        "dataset_exists": filepath.exists(),
        "dataset_filename": DATASET_FILENAME,
        "records_in_db": count,
        "status": "ready" if count > 0 else "empty"
    }


@router.get("/scanners")
def list_scanners(
    skip: int = 0, limit: int = 50,
    risk: str = None, module: str = None,
    search: str = None,
    db: Session = Depends(get_db)
):
    """List all scanners with optional filtering."""
    query = db.query(Scanner)

    if risk:
        query = query.filter(Scanner.failure_risk == risk)
    if module:
        query = query.filter(Scanner.affected_module == module)
    if search:
        query = query.filter(
            Scanner.device_id.contains(search) |
            Scanner.manufacturer.contains(search) |
            Scanner.model.contains(search)
        )

    total = query.count()
    scanners = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "scanners": [
            {
                "id": s.id,
                "device_id": s.device_id,
                "device_type": s.device_type,
                "age": s.age,
                "manufacturer": s.manufacturer,
                "model": s.model,
                "country": s.country,
                "maintenance_cost": s.maintenance_cost,
                "downtime": s.downtime,
                "maintenance_frequency": s.maintenance_frequency,
                "failure_event_count": s.failure_event_count,
                "maintenance_class": s.maintenance_class,
                "mtbf": s.mtbf,
                "failure_rate": s.failure_rate,
                "downtime_per_failure": s.downtime_per_failure,
                "maintenance_intensity": s.maintenance_intensity,
                "historical_risk_index": s.historical_risk_index,
                "failure_risk": s.failure_risk,
                "affected_module": s.affected_module,
                "scanner_age_group": s.scanner_age_group,
                "failure_frequency_level": s.failure_frequency_level,
                "maintenance_efficiency_score": s.maintenance_efficiency_score,
                "downtime_severity": s.downtime_severity,
                "risk_indicator_composite": s.risk_indicator_composite,
            }
            for s in scanners
        ],
    }


@router.get("/scanners/{device_id}")
def get_scanner(device_id: str, db: Session = Depends(get_db)):
    """Get a specific scanner by device ID."""
    scanner = db.query(Scanner).filter(Scanner.device_id == device_id).first()
    if not scanner:
        raise HTTPException(status_code=404, detail=f"Scanner {device_id} non trouvé.")

    return {
        "id": scanner.id,
        "device_id": scanner.device_id,
        "device_type": scanner.device_type,
        "purchase_date": scanner.purchase_date,
        "age": scanner.age,
        "manufacturer": scanner.manufacturer,
        "model": scanner.model,
        "country": scanner.country,
        "maintenance_cost": scanner.maintenance_cost,
        "downtime": scanner.downtime,
        "maintenance_frequency": scanner.maintenance_frequency,
        "failure_event_count": scanner.failure_event_count,
        "maintenance_class": scanner.maintenance_class,
        "maintenance_report": scanner.maintenance_report,
        "mtbf": scanner.mtbf,
        "failure_rate": scanner.failure_rate,
        "downtime_per_failure": scanner.downtime_per_failure,
        "maintenance_intensity": scanner.maintenance_intensity,
        "historical_risk_index": scanner.historical_risk_index,
        "failure_risk": scanner.failure_risk,
        "affected_module": scanner.affected_module,
        "scanner_age_group": scanner.scanner_age_group,
        "failure_frequency_level": scanner.failure_frequency_level,
        "maintenance_efficiency_score": scanner.maintenance_efficiency_score,
        "downtime_severity": scanner.downtime_severity,
        "risk_indicator_composite": scanner.risk_indicator_composite,
    }
