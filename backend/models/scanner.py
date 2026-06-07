"""SQLAlchemy ORM models for the CT Scanner platform."""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from database import Base


class Scanner(Base):
    __tablename__ = "scanners"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(20), unique=True, nullable=False, index=True)
    device_type = Column(String(50), default="CT Scanner")
    purchase_date = Column(String(20))
    age = Column(Integer)
    manufacturer = Column(String(100))
    model = Column(String(100))
    country = Column(String(100))
    maintenance_cost = Column(Float)
    downtime = Column(Float)
    maintenance_frequency = Column(Integer)
    failure_event_count = Column(Integer)
    maintenance_class = Column(Integer)
    maintenance_report = Column(Text)
    mtbf = Column(Float)
    failure_rate = Column(Float)
    downtime_per_failure = Column(Float)
    maintenance_intensity = Column(Float)
    historical_risk_index = Column(Float)
    failure_risk = Column(String(20))
    affected_module = Column(String(100))

    # Engineered features
    scanner_age_group = Column(String(20))
    failure_frequency_level = Column(String(20))
    maintenance_efficiency_score = Column(Float)
    downtime_severity = Column(String(20))
    risk_indicator_composite = Column(Float)

    created_at = Column(DateTime, server_default=func.now())


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(20), index=True)
    scanner_data = Column(JSON)
    predicted_risk = Column(String(20))
    risk_probabilities = Column(JSON)
    health_score = Column(Float)
    predicted_module = Column(String(100), nullable=True)
    recommendation = Column(Text)
    technician_name = Column(String(100), nullable=True)
    technician_role = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), nullable=False)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    cv_mean = Column(Float)
    cv_std = Column(Float)
    confusion_matrix = Column(JSON)
    classification_report = Column(JSON)
    is_best = Column(Integer, default=0)
    training_date = Column(DateTime, server_default=func.now())
    feature_importance = Column(JSON, nullable=True)
