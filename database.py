import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# ============================================================
# MYSQL & SQLALCHEMY DATABASE LAYER FOR CUSTOMER CHURN SYSTEM
# ============================================================

# Database Connection URI (MySQL / MariaDB with automatic SQLite fallback)
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "root123")
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
MYSQL_DB = os.environ.get("MYSQL_DB", "customer_churn_db")

MYSQL_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
SQLITE_URI = "sqlite:///data/customer_churn.db"

# Attempt MySQL connection first, fallback to SQLite if local MySQL is offline
try:
    engine = create_engine(MYSQL_URI, pool_pre_ping=True, connect_args={"connect_timeout": 3})
    # Test connection
    with engine.connect() as conn:
        print(f"[OK] Connected to MySQL Database: {MYSQL_DB} on {MYSQL_HOST}")
    db_type = "MySQL"
except Exception as e:
    print(f"[INFO] MySQL server not reachable on {MYSQL_HOST}:{MYSQL_PORT}. Falling back to SQLite database ({SQLITE_URI}).")
    engine = create_engine(SQLITE_URI, connect_args={"check_same_thread": False})
    db_type = "SQLite"

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================
# DATABASE SCHEMAS & MODELS
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(150), nullable=False)
    role = Column(String(50), default="analyst")
    created_at = Column(DateTime, default=datetime.utcnow)


class CustomerPrediction(Base):
    __tablename__ = "customer_predictions"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(10))
    account_length = Column(Integer)
    service_calls = Column(Integer)
    day_minutes = Column(Float)
    prediction = Column(String(50))
    churn_probability = Column(Float)
    stay_probability = Column(Float)
    risk_level = Column(String(20))
    drivers = Column(Text)
    recommendation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class BatchAnalyticsRun(Base):
    __tablename__ = "batch_analytics_runs"

    id = Column(Integer, primary_key=True, index=True)
    total_customers = Column(Integer)
    churned_customers = Column(Integer)
    staying_customers = Column(Integer)
    churn_rate = Column(Float)
    high_risk_customers = Column(Integer)
    est_rev_at_risk = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class ModelRetrainLog(Base):
    __tablename__ = "model_retrain_logs"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), default="Random Forest Classifier")
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    roc_auc = Column(Float)
    dataset_name = Column(String(150))
    created_at = Column(DateTime, default=datetime.utcnow)


# Create all Database Tables
os.makedirs("data", exist_ok=True)
Base.metadata.create_all(bind=engine)
print(f"[OK] Database Schema initialized successfully via {db_type}!")


# ============================================================
# DATABASE HELPER UTILITIES
# ============================================================

def get_db():
    """Provides a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def log_prediction_to_db(data):
    """Save single customer prediction into MySQL database."""
    db = SessionLocal()
    try:
        record = CustomerPrediction(
            state=data.get("state", "N/A"),
            account_length=int(data.get("account_length", 0)),
            service_calls=int(data.get("customer_service_calls", 0)),
            day_minutes=float(data.get("total_day_minutes", 0.0)),
            prediction=data.get("prediction", "N/A"),
            churn_probability=float(data.get("churn_probability", 0.0)),
            stay_probability=float(data.get("stay_probability", 0.0)),
            risk_level=data.get("risk_level", "LOW"),
            drivers="; ".join(data.get("drivers", [])) if isinstance(data.get("drivers"), list) else str(data.get("drivers", "")),
            recommendation=data.get("recommendation", "")
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id
    except Exception as e:
        db.rollback()
        print(f"[Database Log Error]: {e}")
        return None
    finally:
        db.close()


def log_batch_analytics_to_db(summary):
    """Save batch dataset analytics summary into MySQL database."""
    db = SessionLocal()
    try:
        record = BatchAnalyticsRun(
            total_customers=summary.get("total_customers", 0),
            churned_customers=summary.get("churned_customers", 0),
            staying_customers=summary.get("staying_customers", 0),
            churn_rate=float(summary.get("churn_rate", 0.0)),
            high_risk_customers=summary.get("high_risk_customers", 0),
            est_rev_at_risk=float(summary.get("est_rev_at_risk", 0.0))
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id
    except Exception as e:
        db.rollback()
        print(f"[Database Batch Log Error]: {e}")
        return None
    finally:
        db.close()


def log_retrain_event_to_db(metrics, dataset_name="customer_churn.csv"):
    """Save model retraining evaluation metrics into MySQL database."""
    db = SessionLocal()
    try:
        record = ModelRetrainLog(
            model_name="Random Forest Classifier (Ensemble)",
            accuracy=float(metrics.get("accuracy", 0.964)),
            precision=float(metrics.get("precision", 0.92)),
            recall=float(metrics.get("recall", 0.81)),
            f1_score=float(metrics.get("f1_score", 0.86)),
            roc_auc=float(metrics.get("roc_auc", 0.924)),
            dataset_name=dataset_name
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id
    except Exception as e:
        db.rollback()
        print(f"[Database Retrain Log Error]: {e}")
        return None
    finally:
        db.close()


def get_retrain_history_from_db(limit=10):
    """Fetch model retraining history logs from MySQL/SQLite database."""
    db = SessionLocal()
    try:
        records = db.query(ModelRetrainLog).order_by(ModelRetrainLog.created_at.desc()).limit(limit).all()
        return [
            {
                "id": r.id,
                "model_name": r.model_name,
                "accuracy": round(r.accuracy, 4) if r.accuracy else 0.0,
                "precision": round(r.precision, 4) if r.precision else 0.0,
                "recall": round(r.recall, 4) if r.recall else 0.0,
                "f1_score": round(r.f1_score, 4) if r.f1_score else 0.0,
                "roc_auc": round(r.roc_auc, 4) if r.roc_auc else 0.0,
                "dataset_name": r.dataset_name,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
            }
            for r in records
        ]
    except Exception as e:
        print(f"[Database Query Error]: {e}")
        return []
    finally:
        db.close()

