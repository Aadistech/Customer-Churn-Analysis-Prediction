import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Path to service account key
KEY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "firebase_key.json")

db = None
is_firebase_active = False

try:
    if os.path.exists(KEY_PATH):
        if not firebase_admin._apps:
            cred = credentials.Certificate(KEY_PATH)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        is_firebase_active = True
        print("[OK] Python Firebase Admin SDK Connected to Cloud Firestore!")
    else:
        print(f"[WARN] Firebase key not found at {KEY_PATH}")
except Exception as e:
    print(f"[ERROR] Failed to initialize Python Firebase: {e}")


def sync_prediction_to_firestore(data):
    """Store single prediction result in Cloud Firestore collection 'churn_predictions'."""
    if not is_firebase_active or db is None:
        return None

    try:
        doc_ref = db.collection("churn_predictions").document()
        payload = dict(data)
        payload["timestamp"] = firestore.SERVER_TIMESTAMP
        doc_ref.set(payload)
        return doc_ref.id
    except Exception as e:
        print(f"[Firebase Firestore Error]: {e}")
        return None


def sync_analytics_to_firestore(summary):
    """Update 'latest_summary' document in Cloud Firestore collection 'churn_analytics'."""
    if not is_firebase_active or db is None:
        return None

    try:
        doc_ref = db.collection("churn_analytics").document("latest_summary")
        clean_summary = {
            "total_customers": summary.get("total_customers", 0),
            "churned_customers": summary.get("churned_customers", 0),
            "staying_customers": summary.get("staying_customers", 0),
            "churn_rate": summary.get("churn_rate", 0.0),
            "high_risk_customers": summary.get("high_risk_customers", 0),
            "est_rev_at_risk": summary.get("est_rev_at_risk", 0),
            "updatedAt": firestore.SERVER_TIMESTAMP
        }
        doc_ref.set(clean_summary, merge=True)
    except Exception as e:
        print(f"[Firebase Analytics Sync Error]: {e}")
