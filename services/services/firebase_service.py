import os
import requests
import datetime
from flask import has_request_context, session

FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY", "")
FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "customer-churn-analysis-c3be6")

is_firebase_active = bool(FIREBASE_API_KEY and FIREBASE_PROJECT_ID)

def sync_prediction_to_firestore(prediction_data):
    """Sync single customer prediction result to Cloud Firestore."""
    if not is_firebase_active:
        return False
    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/churn_predictions?key={FIREBASE_API_KEY}"
    
    current_user = session.get("username", "anonymous") if has_request_context() else "system"
    fields = {
        "record_type": {"stringValue": "individual_prediction"},
        "timestamp": {"stringValue": datetime.datetime.now(datetime.timezone.utc).isoformat()},
        "user": {"stringValue": current_user}
    }
    for k, v in prediction_data.items():
        if isinstance(v, (int, float)):
            fields[k] = {"doubleValue": float(v)}
        elif isinstance(v, bool):
            fields[k] = {"booleanValue": v}
        elif isinstance(v, list):
            fields[k] = {"stringValue": "; ".join(map(str, v))}
        else:
            fields[k] = {"stringValue": str(v)}
            
    try:
        res = requests.post(url, json={"fields": fields}, timeout=4)
        return res.status_code in (200, 201)
    except Exception as e:
        print("[Firebase Sync Notice]:", e)
        return False

def sync_analytics_to_firestore(summary_data):
    """Sync bulk executive analytics summary metrics to Cloud Firestore."""
    if not is_firebase_active:
        return False
    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/churn_predictions?key={FIREBASE_API_KEY}"
    
    current_user = session.get("username", "anonymous") if has_request_context() else "system"
    fields = {
        "record_type": {"stringValue": "bulk_batch_analysis"},
        "timestamp": {"stringValue": datetime.datetime.now(datetime.timezone.utc).isoformat()},
        "user": {"stringValue": current_user}
    }
    for k in ["total_customers", "churned_customers", "churn_rate", "high_risk_customers", "est_rev_at_risk"]:
        if k in summary_data and summary_data[k] is not None:
            fields[k] = {"doubleValue": float(summary_data[k])}
            
    try:
        res = requests.post(url, json={"fields": fields}, timeout=4)
        return res.status_code in (200, 201)
    except Exception as e:
        print("[Firebase Analytics Notice]:", e)
        return False
