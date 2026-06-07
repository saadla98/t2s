"""EDA / Analytics service — dashboard stats, distributions, correlations."""
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from models.scanner import Scanner, Prediction


def get_dashboard_summary(db: Session) -> dict:
    """Get summary statistics for the dashboard."""
    total_scanners = db.query(Scanner).count()
    if total_scanners == 0:
        return {
            "total_scanners": 0,
            "average_risk_index": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "total_predictions": 0,
            "average_age": 0,
            "average_downtime": 0,
            "average_mtbf": 0,
            "average_maintenance_cost": 0,
        }

    scanners = db.query(Scanner).all()

    high = sum(1 for s in scanners if s.failure_risk == "High")
    medium = sum(1 for s in scanners if s.failure_risk == "Medium")
    low = sum(1 for s in scanners if s.failure_risk == "Low")
    total_predictions = db.query(Prediction).count()

    avg_risk = np.mean([s.historical_risk_index for s in scanners if s.historical_risk_index is not None])
    avg_age = np.mean([s.age for s in scanners if s.age is not None])
    avg_downtime = np.mean([s.downtime for s in scanners if s.downtime is not None])
    avg_mtbf = np.mean([s.mtbf for s in scanners if s.mtbf is not None])
    avg_cost = np.mean([s.maintenance_cost for s in scanners if s.maintenance_cost is not None])

    return {
        "total_scanners": total_scanners,
        "average_risk_index": round(float(avg_risk), 4),
        "high_risk_count": high,
        "medium_risk_count": medium,
        "low_risk_count": low,
        "total_predictions": total_predictions,
        "average_age": round(float(avg_age), 1),
        "average_downtime": round(float(avg_downtime), 2),
        "average_mtbf": round(float(avg_mtbf), 2),
        "average_maintenance_cost": round(float(avg_cost), 2),
    }


def get_risk_distribution(db: Session) -> dict:
    """Get failure risk distribution."""
    scanners = db.query(Scanner).all()
    dist = {"Low": 0, "Medium": 0, "High": 0}
    for s in scanners:
        if s.failure_risk in dist:
            dist[s.failure_risk] += 1
    return dist


def get_module_distribution(db: Session) -> list:
    """Get affected module distribution."""
    scanners = db.query(Scanner).all()
    modules = {}
    for s in scanners:
        mod = s.affected_module or "Unknown"
        modules[mod] = modules.get(mod, 0) + 1

    return [{"module": k, "count": v} for k, v in sorted(modules.items(), key=lambda x: -x[1])]


def get_correlations(db: Session) -> dict:
    """Get feature correlation matrix."""
    scanners = db.query(Scanner).all()
    if not scanners:
        return {"columns": [], "data": []}

    numeric_cols = [
        "age", "maintenance_cost", "downtime", "maintenance_frequency",
        "failure_event_count", "mtbf", "failure_rate",
        "downtime_per_failure", "maintenance_intensity", "historical_risk_index"
    ]

    display_names = [
        "Âge", "Coût Maintenance", "Temps d'arrêt", "Fréq. Maintenance",
        "Nb. Pannes", "MTBF", "Taux de Panne",
        "Arrêt/Panne", "Intensité Maint.", "Indice Risque Hist."
    ]

    records = []
    for s in scanners:
        records.append({col: getattr(s, col, 0) for col in numeric_cols})

    df = pd.DataFrame(records)
    corr = df.corr().round(3)

    return {
        "columns": display_names,
        "data": corr.values.tolist(),
    }


def get_age_distribution(db: Session) -> list:
    """Get scanner age distribution."""
    scanners = db.query(Scanner).all()
    age_groups = {"Jeune (1-4)": 0, "Moyen (5-8)": 0, "Ancien (9-12)": 0}
    for s in scanners:
        if s.age and s.age <= 4:
            age_groups["Jeune (1-4)"] += 1
        elif s.age and s.age <= 8:
            age_groups["Moyen (5-8)"] += 1
        else:
            age_groups["Ancien (9-12)"] += 1
    return [{"group": k, "count": v} for k, v in age_groups.items()]


def get_manufacturer_distribution(db: Session) -> list:
    """Get manufacturer distribution."""
    scanners = db.query(Scanner).all()
    manufacturers = {}
    for s in scanners:
        mfg = s.manufacturer or "Unknown"
        manufacturers[mfg] = manufacturers.get(mfg, 0) + 1
    return [{"manufacturer": k, "count": v} for k, v in sorted(manufacturers.items(), key=lambda x: -x[1])]


def get_risk_by_age_group(db: Session) -> list:
    """Get risk distribution by age group."""
    scanners = db.query(Scanner).all()
    groups = {}
    for s in scanners:
        if s.age and s.age <= 4:
            grp = "Jeune (1-4)"
        elif s.age and s.age <= 8:
            grp = "Moyen (5-8)"
        else:
            grp = "Ancien (9-12)"

        if grp not in groups:
            groups[grp] = {"Low": 0, "Medium": 0, "High": 0}
        if s.failure_risk in groups[grp]:
            groups[grp][s.failure_risk] += 1

    return [{"age_group": k, **v} for k, v in groups.items()]


def get_downtime_by_module(db: Session) -> list:
    """Get average downtime by module."""
    scanners = db.query(Scanner).all()
    modules = {}
    for s in scanners:
        mod = s.affected_module or "Unknown"
        if mod not in modules:
            modules[mod] = []
        modules[mod].append(s.downtime or 0)

    return [
        {"module": k, "avg_downtime": round(np.mean(v), 2), "count": len(v)}
        for k, v in sorted(modules.items(), key=lambda x: -np.mean(x[1]))
    ]


def get_cost_by_risk(db: Session) -> list:
    """Get average maintenance cost by risk level."""
    scanners = db.query(Scanner).all()
    risks = {}
    for s in scanners:
        r = s.failure_risk or "Unknown"
        if r not in risks:
            risks[r] = []
        risks[r].append(s.maintenance_cost or 0)

    return [
        {"risk_level": k, "avg_cost": round(np.mean(v), 2), "count": len(v)}
        for k, v in risks.items()
    ]
