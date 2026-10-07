import os
import requests
import datetime
from flask import has_request_context, session

try:
    import firebase_admin
    from firebase_admin import credentials, auth, firestore
except ImportError:
    firebase_admin = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY_PATH = os.path.join(BASE_DIR, "firebase_key.json")

# Initialize Firebase Admin SDK using Service Account Key
if firebase_admin and not firebase_admin._apps:
    try:
        if os.path.exists(KEY_PATH):
            cred = credentials.Certificate(KEY_PATH)
            firebase_admin.initialize_app(cred)
            print(f"[Firebase Admin SDK] Connected to Firebase Console via {KEY_PATH}")
        else:
            firebase_admin.initialize_app()
            print("[Firebase Admin SDK] Initialized default app")
    except Exception as e:
        print("[Firebase Admin SDK Notice]:", e)

FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY", "")
FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "customer-churn-analysis-c3be6")

is_firebase_active = bool(FIREBASE_API_KEY and FIREBASE_PROJECT_ID)


def register_or_sync_firebase_user(email, password="DefaultPassword123!", display_name=None):
    """Ensure user exists in Firebase Authentication Console (https://console.firebase.google.com/u/0/project/customer-churn-analysis-c3be6/authentication/users)."""
    if not firebase_admin:
        return None

    if not email or "@" not in email:
        email = f"{email}@aadibi.com"

    try:
        user = auth.get_user_by_email(email)
        print(f"[Firebase Auth Console] Found existing user: {user.email} (UID: {user.uid})")
        return user
    except auth.UserNotFoundError:
        try:
            user = auth.create_user(
                email=email,
                password=password if len(password) >= 6 else "DefaultPassword123!",
                display_name=display_name or email.split("@")[0].capitalize()
            )
            print(f"[Firebase Auth Console] Registered new user in Firebase Auth Console: {user.email} (UID: {user.uid})")
            return user
        except Exception as err:
            print(f"[Firebase Auth Console Notice]: {err}")
            return None
    except Exception as err:
        print(f"[Firebase Auth Console Notice]: {err}")
        return None


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
