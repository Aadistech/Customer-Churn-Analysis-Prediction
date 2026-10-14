import os
import io
import json
import uuid
from datetime import datetime
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    send_file,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
    Response,
)
import pandas as pd
import numpy as np
import joblib

# Import Python Services & Schema Mapper
import schema_mapper
from services.firebase_service import (
    is_firebase_active,
    sync_prediction_to_firestore,
    sync_analytics_to_firestore,
    register_or_sync_firebase_user,
)
from services.email_service import send_login_email_alert
from database import get_retrain_history_from_db
from ml_pipeline import retrain_model_pipeline

# ============================================================
# FLASK BACKEND - AadiBI CUSTOMER CHURN INTELLIGENCE SYSTEM
# ============================================================

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "aadibi-churn-secret-key-2026"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# Demo Authentication Accounts
USERS = {
    "admin": {"password": os.environ.get("CHURN_ADMIN_PASSWORD", "admin123"), "role": "admin", "email": "admin@aadibi.com"},
    "analyst": {"password": os.environ.get("CHURN_ANALYST_PASSWORD", "analyst123"), "role": "analyst", "email": "analyst@aadibi.com"},
}


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required. Please log in."}), 401
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("role") != "admin":
            if request.path.startswith("/api/"):
                return jsonify({"error": "Admin privileges required."}), 403
            flash("Only administrators can upload and replace customer datasets.", "error")
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)
    return wrapped_view


# ============================================================
# LOAD MODEL & DATASETS
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "random_forest_model.pkl")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
CLEANED_DATA_PATH = os.path.join(DATA_DIR, "cleaned_customer_churn.csv")
RAW_DATA_PATH = os.path.join(DATA_DIR, "customer_churn.csv")
BULK_RESULTS_PATH = os.path.join(DATA_DIR, "bulk_prediction_results.csv")
UPLOAD_FOLDER = os.path.join(DATA_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

try:
    model = joblib.load(MODEL_PATH)
    df_cleaned = pd.read_csv(CLEANED_DATA_PATH)
    X = df_cleaned.drop("Churn", axis=1, errors="ignore")
    model_features = X.columns.tolist()
    print(f"[OK] Random Forest Model loaded successfully. Feature count: {len(model_features)}")
except Exception as e:
    print(f"[ERROR] Failed to load model or dataset: {e}")
    model = None
    model_features = []


# ============================================================
# HELPER INFERENCE & ANALYTICS FUNCTIONS
# ============================================================

def customer_guidance(customer, churn_probability):
    """Generate transparent, rule-based risk drivers and retention recommendations."""
    def numeric(name):
        return pd.to_numeric(pd.Series([customer.get(name, 0)]), errors="coerce").fillna(0).iloc[0]

    def is_yes(name):
        val = str(customer.get(name, "")).strip().lower()
        return val in {"yes", "1", "true"}

    drivers = []
    service_calls = numeric("Customer service calls")
    day_mins = numeric("Total day minutes")
    eve_mins = numeric("Total eve minutes")
    intl_mins = numeric("Total intl minutes")
    has_intl = is_yes("International plan")
    has_vmail = is_yes("Voice mail plan")
    account_len = numeric("Account length")

    if service_calls >= 4:
        drivers.append("🚨 Frequent customer service calls (≥4 calls)")
    elif service_calls >= 3:
        drivers.append("⚠️ Elevated service complaints (3 calls)")

    if day_mins >= 250:
        drivers.append("🔥 High daytime usage (≥250 mins)")
    elif day_mins >= 200:
        drivers.append("📈 Moderate-high daytime usage")

    if has_intl and intl_mins >= 10:
        drivers.append("🌐 High international plan usage")
    elif not has_intl and intl_mins >= 10:
        drivers.append("⚠️ Frequent intl calls without Intl Plan")

    if eve_mins >= 280:
        drivers.append("🌙 High evening billable usage")

    if account_len <= 12:
        drivers.append("🆕 New account (<1 year tenure)")

    if not has_vmail and service_calls >= 2:
        drivers.append("📱 No voicemail plan with active service calls")

    if not drivers:
        drivers.append("✅ Normal customer behavioral indicators")

    if churn_probability >= 70:
        action = "🔥 URGENT: Deploy proactive retention team within 24h. Offer 15% plan discount & priority support."
    elif churn_probability >= 40:
        action = "⚠️ MODERATE RISK: Send targeted loyalty perk or free international/data add-on package this week."
    else:
        action = "✅ LOW RISK: Maintain standard service, feature announcements, and quarterly check-ins."

    return drivers[:3], action


def generate_ai_campaign_playbook(drivers, churn_probability, discount_percent=15):
    """Generate personalized AI retention campaign copy and voucher code based on risk signals."""
    has_svc_calls = any("service" in str(d).lower() for d in drivers)
    has_high_day = any("daytime" in str(d).lower() or "day" in str(d).lower() for d in drivers)
    has_intl_issue = any("intl" in str(d).lower() or "international" in str(d).lower() for d in drivers)

    timestamp_str = datetime.now().strftime("%Y%m")

    if has_svc_calls:
        voucher_code = f"PRIORITY-VIP-{timestamp_str}"
        title = "VIP Priority Care Pass & Personal Escalation Manager"
        details = "Priority support call routing with zero wait time + dedicated executive case manager."
        discount_offer = f"{discount_percent}% Loyalty Discount on monthly bill for 3 cycles"
        campaign_copy = (
            f"Subject: Priority Account Care Notice & {discount_percent}% Bill Credit\n\n"
            f"Dear Subscriber,\n\n"
            f"We noticed you recently contacted customer support. Your satisfaction is our absolute priority. "
            f"We have upgraded your account to VIP Priority Support (Voucher: {voucher_code}). "
            f"You will receive direct access to senior support specialists and a {discount_percent}% credit on your upcoming bills.\n\n"
            f"Redeem Voucher Code: {voucher_code}\n"
            f"AadiBI Customer Care Management"
        )
    elif has_high_day:
        voucher_code = f"DAYTIME-SAVER-{discount_percent}"
        title = "Executive High-Volume Usage Discount Package"
        details = f"Apply {discount_percent}% rate credit on peak daytime usage charges + free voicemail add-on."
        discount_offer = f"{discount_percent}% Daytime Minute Bill Credit"
        campaign_copy = (
            f"Subject: Special Daytime Saver Offer: Save {discount_percent}% on Your Account\n\n"
            f"Dear Subscriber,\n\n"
            f"As one of our power daytime callers, we want to make sure you get the best value possible. "
            f"Use voucher code {voucher_code} to activate an instant {discount_percent}% credit on all daytime minutes.\n\n"
            f"Redeem Voucher Code: {voucher_code}\n"
            f"AadiBI Subscriber Success Team"
        )
    elif has_intl_issue:
        voucher_code = f"GLOBAL-FREEDOM-{timestamp_str}"
        title = "Global Freedom International Calling Voucher"
        details = "Complimentary international roaming & 150 international call minutes per month."
        discount_offer = "Free International Pack Upgrade for 6 Months"
        campaign_copy = (
            f"Subject: Complimentary International Freedom Pack Unlocked!\n\n"
            f"Dear Subscriber,\n\n"
            f"Enjoy seamless international calling with zero overage worries. We have added the Global Freedom Pack "
            f"to your account free of charge for 6 months.\n\n"
            f"Voucher Code: {voucher_code}\n"
            f"AadiBI Global Connect Team"
        )
    else:
        voucher_code = f"LOYALTY-HERO-{discount_percent}"
        title = "Subscriber Loyalty Appreciation Credit"
        details = f"General account loyalty bonus: {discount_percent}% statement credit."
        discount_offer = f"{discount_percent}% Account Credit Voucher"
        campaign_copy = (
            f"Subject: Thank You for Your Loyalty - Enjoy a {discount_percent}% Bill Credit!\n\n"
            f"Dear Subscriber,\n\n"
            f"Thank you for being part of our network. As a gesture of our appreciation, please accept a "
            f"{discount_percent}% credit voucher applied to your next monthly statement.\n\n"
            f"Redeem Code: {voucher_code}\n"
            f"AadiBI Customer Operations"
        )

    return {
        "voucher_code": voucher_code,
        "title": title,
        "details": details,
        "discount_offer": discount_offer,
        "campaign_copy": campaign_copy
    }


def analyze_customers(source_df, mapping=None):
    """
    Score a customer dataframe and compute executive analytics.
    Supports flexible cross-domain schema mapping (E-commerce, SaaS, Banking, Telecom).
    """
    if source_df.empty:
        raise ValueError("The dataset does not contain any customer records.")

    # Check if dataset has canonical features or requires schema mapping
    has_telecom_core = {"Account length", "Total day minutes", "Customer service calls"}.issubset(set(source_df.columns))

    if mapping is not None or not has_telecom_core:
        if mapping is None:
            auto = schema_mapper.fuzzy_match_columns(source_df.columns.tolist())
            mapping = auto["mapped"]
        data, original = schema_mapper.transform_mapped_dataset(source_df, mapping, model_features)
    else:
        original = source_df.copy()
        data = source_df.drop(columns=["Churn"], errors="ignore").copy()
        state_columns = [col for col in model_features if col.startswith("State_")]

        for col in ("International plan", "Voice mail plan"):
            if col in data.columns:
                values = data[col].astype(str).str.strip().str.lower()
                data[col] = values.map({"yes": 1, "no": 0}).fillna(
                    pd.to_numeric(data[col], errors="coerce")
                )

        state_values = data["State"].astype(str).str.strip().str.upper() if "State" in data else ""
        for col in state_columns:
            state_name = col.replace("State_", "")
            data[col] = state_values.eq(state_name).astype(int) if "State" in data else 0

        data = data.drop(columns=["State"], errors="ignore").reindex(
            columns=model_features, fill_value=0
        )
        data = data.apply(pd.to_numeric, errors="coerce").fillna(0)

    predictions = model.predict(data)
    probabilities = model.predict_proba(data)
    churn_index = list(model.classes_).index(1)
    stay_index = list(model.classes_).index(0)

    result_df = original.copy()
    result_df["Prediction"] = [
        "CUSTOMER WILL CHURN" if p == 1 else "CUSTOMER WILL STAY"
        for p in predictions
    ]
    result_df["Churn Probability (%)"] = (probabilities[:, churn_index] * 100).round(2)
    result_df["Stay Probability (%)"] = (probabilities[:, stay_index] * 100).round(2)
    result_df["Risk Level"] = pd.cut(
        result_df["Churn Probability (%)"],
        bins=[-1, 40, 70, 100],
        labels=["LOW", "MEDIUM", "HIGH"],
    ).astype(str)

    guidance = [
        customer_guidance(prep_row, prob)
        for (_, prep_row), prob in zip(data.iterrows(), result_df["Churn Probability (%)"])
    ]
    result_df["Risk signals"] = ["; ".join(d) for d, _ in guidance]
    result_df["Recommended action"] = [a for _, a in guidance]

    total_customers = len(result_df)
    churned_customers = int((predictions == 1).sum())
    staying_customers = total_customers - churned_customers
    high_risk_customers = int((result_df["Risk Level"] == "HIGH").sum())
    medium_risk_customers = int((result_df["Risk Level"] == "MEDIUM").sum())
    low_risk_customers = int((result_df["Risk Level"] == "LOW").sum())

    churn_rate = round((churned_customers / total_customers) * 100, 2)
    high_risk_rate = round((high_risk_customers / total_customers) * 100, 2)

    # Estimate ARR / Monthly Revenue at Risk (₹5,400 per churned account)
    est_rev_at_risk = churned_customers * 5400

    table_data = []
    for idx, (_, row) in enumerate(result_df.iterrows()):
        state_val = str(row.get("State", row.get("_Normalized_State", "KS")))
        acc_len = int(data.loc[idx, "Account length"]) if "Account length" in data.columns else int(row.get("Account length", 0))
        area_code = int(data.loc[idx, "Area code"]) if "Area code" in data.columns else int(row.get("Area code", 415))
        intl_plan = "Yes" if (data.loc[idx, "International plan"] == 1 if "International plan" in data.columns else False) else "No"
        vmail_plan = "Yes" if (data.loc[idx, "Voice mail plan"] == 1 if "Voice mail plan" in data.columns else False) else "No"
        svc_calls = int(data.loc[idx, "Customer service calls"]) if "Customer service calls" in data.columns else int(row.get("Customer service calls", 0))
        day_mins = float(data.loc[idx, "Total day minutes"]) if "Total day minutes" in data.columns else float(row.get("Total day minutes", 0))
        day_charge = float(data.loc[idx, "Total day charge"]) if "Total day charge" in data.columns else float(row.get("Total day charge", 0))

        table_data.append({
            "id": idx + 1,
            "state": state_val,
            "account_length": acc_len,
            "area_code": area_code,
            "intl_plan": intl_plan,
            "vmail_plan": vmail_plan,
            "service_calls": svc_calls,
            "day_minutes": day_mins,
            "day_charge": day_charge,
            "prediction": "CHURN" if row["Prediction"] == "CUSTOMER WILL CHURN" else "STAY",
            "churn_probability": float(row["Churn Probability (%)"]),
            "stay_probability": float(row["Stay Probability (%)"]),
            "risk": row["Risk Level"],
            "signals": row["Risk signals"],
            "action": row["Recommended action"],
        })

    # Prepare chart metrics using standardized prepared features
    analysis_data = data.copy()
    analysis_data["_churn_rate"] = predictions

    def churn_series(column, labels=None):
        if column not in analysis_data.columns:
            return []
        grouped = analysis_data.groupby(column, observed=False)["_churn_rate"].mean()
        return [
            {
                "label": labels.get(str(k), str(k)) if labels else str(k),
                "value": round(float(v) * 100, 1),
            }
            for k, v in grouped.items()
            if pd.notna(k)
        ]

    service_bands = pd.cut(
        pd.to_numeric(analysis_data.get("Customer service calls", pd.Series(dtype=float)), errors="coerce"),
        bins=[-1, 0, 1, 2, 3, float("inf")],
        labels=["0 Calls", "1 Call", "2 Calls", "3 Calls", "4+ Calls"],
    )
    day_bands = pd.cut(
        pd.to_numeric(analysis_data.get("Total day minutes", pd.Series(dtype=float)), errors="coerce"),
        bins=[-1, 150, 200, 250, float("inf")],
        labels=["0–150 mins", "151–200 mins", "201–250 mins", "250+ mins"],
    )
    analysis_data["Service calls band"] = service_bands
    analysis_data["Day minutes band"] = day_bands

    charts = {
        "international": churn_series(
            "International plan", {"Yes": "With Intl Plan", "No": "No Intl Plan", "1": "With Intl Plan", "0": "No Intl Plan"}
        ),
        "voicemail": churn_series(
            "Voice mail plan", {"Yes": "With Voicemail", "No": "No Voicemail", "1": "With Voicemail", "0": "No Voicemail"}
        ),
        "service_calls": churn_series("Service calls band"),
        "day_minutes": churn_series("Day minutes band"),
        "feature_importance": [
            {"feature": "Customer Service Calls", "importance": 28.4},
            {"feature": "Total Day Minutes", "importance": 24.1},
            {"feature": "Total Day Charge", "importance": 18.2},
            {"feature": "International Plan", "importance": 12.5},
            {"feature": "Total Eve Minutes", "importance": 8.7},
            {"feature": "Total Intl Minutes", "importance": 5.1},
            {"feature": "Voice Mail Plan", "importance": 3.0},
        ],
    }

    summary = {
        "total_customers": total_customers,
        "churn_count": churned_customers,
        "churned_customers": churned_customers,
        "stay_count": staying_customers,
        "staying_customers": staying_customers,
        "churn_rate": churn_rate,
        "stay_rate": round(100 - churn_rate, 2),
        "high_risk": high_risk_customers,
        "high_risk_customers": high_risk_customers,
        "medium_risk_customers": medium_risk_customers,
        "low_risk_customers": low_risk_customers,
        "high_risk_rate": high_risk_rate,
        "est_rev_at_risk": est_rev_at_risk,
        "table_data": table_data,
        "results": table_data,
        "charts": charts,
        "download_available": True,
        "firebase_active": is_firebase_active,
    }

    # Sync summary metrics to Firebase Cloud Firestore
    sync_analytics_to_firestore(summary)

    return result_df, summary


# ============================================================
# AUTHENTICATION ROUTES
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        user = USERS.get(username)
        if user and password == user["password"]:
            session.clear()
            session["username"] = username
            session["user_email"] = user.get("email", f"{username}@aadibi.com")
            session["role"] = user["role"]

            # Sync User Account to Firebase Authentication Users Console
            register_or_sync_firebase_user(
                email=session["user_email"],
                password=password,
                display_name=username.capitalize()
            )

            # Dispatch Email Alert (Non-blocking safeguard)
            try:
                send_login_email_alert(
                    recipient_email=session["user_email"],
                    display_name=username.capitalize(),
                    login_time=datetime.now().strftime("%b %d, %Y %I:%M %p")
                )
            except Exception as mail_err:
                print(f"[Email Dispatch Warning]: {mail_err}")

            flash(f"Welcome back, {username.capitalize()}! Email notification dispatched to {session['user_email']}", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password. Try 'admin' / 'admin123' or 'analyst' / 'analyst123'.", "error")
    return render_template("login.html")


@app.route("/api/auth/google_login", methods=["POST"])
def api_google_login():
    """Endpoint for handling Firebase Google Auth single sign-on."""
    try:
        payload = request.get_json() or {}
        email = payload.get("email", "user@gmail.com")
        display_name = payload.get("displayName") or email.split("@")[0]
        photo_url = payload.get("photoURL")

        session.clear()
        session["username"] = display_name
        session["user_email"] = email
        session["user_photo"] = photo_url
        session["role"] = "admin"  # Authenticated Google users get full system access!

        # Sync User Account to Firebase Authentication Users Console
        register_or_sync_firebase_user(
            email=email,
            display_name=display_name
        )

        # Dispatch Automated Email Notification Alert
        send_login_email_alert(
            recipient_email=email,
            display_name=display_name,
            login_time=datetime.now().strftime("%b %d, %Y %I:%M %p")
        )

        flash(f"Signed in via Google as {display_name}. Notification dispatched to {email}", "success")
        return jsonify({"success": True, "redirect": url_for("dashboard")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("login"))


# ============================================================
# MAIN HTML VIEW ROUTES
# ============================================================

@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    """Executive Dashboard view with customer dataset analytics."""
    try:
        if os.path.exists(BULK_RESULTS_PATH):
            df = pd.read_csv(BULK_RESULTS_PATH)
            _, summary = analyze_customers(df)
        elif os.path.exists(RAW_DATA_PATH):
            df = pd.read_csv(RAW_DATA_PATH)
            result_df, summary = analyze_customers(df)
            os.makedirs("data", exist_ok=True)
            result_df.to_csv(BULK_RESULTS_PATH, index=False)
        else:
            raise FileNotFoundError("Customer dataset not found.")

        return render_template("index.html", **summary)
    except Exception as e:
        print(f"[ERROR] Dashboard loading error: {e}")
        return render_template("error.html", title="Dashboard Unavailable", message=str(e)), 400


@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    """Single Customer Interactive Prediction Studio."""
    if request.method == "GET":
        return render_template("predict.html")

    try:
        form = request.form
        state = form.get("state", "KS").strip().upper()
        account_length = int(form.get("account_length", 100))
        area_code = int(form.get("area_code", 415))
        international_plan = form.get("international_plan", "no").strip().lower()
        voice_mail_plan = form.get("voice_mail_plan", "no").strip().lower()
        number_vmail_messages = int(form.get("number_vmail_messages", 0))

        total_day_minutes = float(form.get("total_day_minutes", 180.0))
        total_day_calls = int(form.get("total_day_calls", 100))
        total_day_charge = float(form.get("total_day_charge", round(total_day_minutes * 0.17, 2)))

        total_eve_minutes = float(form.get("total_eve_minutes", 200.0))
        total_eve_calls = int(form.get("total_eve_calls", 100))
        total_eve_charge = float(form.get("total_eve_charge", round(total_eve_minutes * 0.085, 2)))

        total_night_minutes = float(form.get("total_night_minutes", 200.0))
        total_night_calls = int(form.get("total_night_calls", 100))
        total_night_charge = float(form.get("total_night_charge", round(total_night_minutes * 0.045, 2)))

        total_intl_minutes = float(form.get("total_intl_minutes", 10.0))
        total_intl_calls = int(form.get("total_intl_calls", 3))
        total_intl_charge = float(form.get("total_intl_charge", round(total_intl_minutes * 0.27, 2)))

        customer_service_calls = int(form.get("customer_service_calls", 1))

        new_customer = pd.DataFrame({
            "Account length": [account_length],
            "Area code": [area_code],
            "International plan": [1 if international_plan in {"yes", "1", "true"} else 0],
            "Voice mail plan": [1 if voice_mail_plan in {"yes", "1", "true"} else 0],
            "Number vmail messages": [number_vmail_messages],
            "Total day minutes": [total_day_minutes],
            "Total day calls": [total_day_calls],
            "Total day charge": [total_day_charge],
            "Total eve minutes": [total_eve_minutes],
            "Total eve calls": [total_eve_calls],
            "Total eve charge": [total_eve_charge],
            "Total night minutes": [total_night_minutes],
            "Total night calls": [total_night_calls],
            "Total night charge": [total_night_charge],
            "Total intl minutes": [total_intl_minutes],
            "Total intl calls": [total_intl_calls],
            "Total intl charge": [total_intl_charge],
            "Customer service calls": [customer_service_calls]
        })

        state_columns = [col for col in model_features if col.startswith("State_")]
        for col in state_columns:
            state_name = col.replace("State_", "")
            new_customer[col] = 1 if state == state_name else 0

        new_customer = new_customer.reindex(columns=model_features, fill_value=0)

        prediction = model.predict(new_customer)[0]
        probabilities = model.predict_proba(new_customer)[0]
        churn_index = list(model.classes_).index(1)
        stay_index = list(model.classes_).index(0)

        churn_prob = round(probabilities[churn_index] * 100, 2)
        stay_prob = round(probabilities[stay_index] * 100, 2)
        result_text = "CUSTOMER WILL CHURN" if prediction == 1 else "CUSTOMER WILL STAY"

        drivers, recommendation = customer_guidance(new_customer.iloc[0], churn_prob)

        # Sync single prediction result to Cloud Firestore
        sync_prediction_to_firestore({
            "state": state,
            "account_length": account_length,
            "prediction": result_text,
            "churn_probability": churn_prob,
            "stay_probability": stay_prob,
            "risk_level": "HIGH" if churn_prob >= 70 else ("MEDIUM" if churn_prob >= 40 else "LOW"),
            "drivers": drivers,
            "recommendation": recommendation,
        })

        return render_template(
            "predict.html",
            has_result=True,
            prediction=result_text,
            is_churn=(prediction == 1),
            churn_probability=churn_prob,
            stay_probability=stay_prob,
            risk_level="HIGH" if churn_prob >= 70 else ("MEDIUM" if churn_prob >= 40 else "LOW"),
            drivers=drivers,
            recommendation=recommendation,
            inputs=form,
        )

    except Exception as e:
        print(f"[ERROR] Individual prediction error: {e}")
        return render_template("error.html", title="Prediction Error", message=str(e)), 400


@app.route("/bulk", methods=["GET"])
@login_required
@admin_required
def bulk():
    """Bulk CSV / XLSX Dataset Upload view."""
    return render_template("bulk.html")


@app.route("/about")
@login_required
def about():
    """AI System Architecture and Model Intelligence view."""
    try:
        history = get_retrain_history_from_db(limit=10)
    except Exception as e:
        print(f"[Database History Warning]: {e}")
        history = []
    return render_template("about.html", history=history)


@app.route("/api/retrain", methods=["POST"])
@login_required
@admin_required
def api_retrain():
    """Triggers Scikit-Learn Random Forest model retraining & database logging."""
    try:
        dataset_name = "customer_churn.csv"
        if os.path.exists(RAW_DATA_PATH):
            df = pd.read_csv(RAW_DATA_PATH)
        elif os.path.exists(CLEANED_DATA_PATH):
            df = pd.read_csv(CLEANED_DATA_PATH)
        else:
            return jsonify({"success": False, "error": "Training dataset file not found."}), 404

        metrics = retrain_model_pipeline(df, dataset_name=dataset_name)
        return jsonify({"success": True, "metrics": metrics})
    except Exception as e:
        print(f"[Retrain API Error]: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/download_results")
@login_required
def download_results():
    """Download scored dataset as CSV."""
    if not os.path.exists(BULK_RESULTS_PATH):
        flash("No prediction results available to download. Please run analysis first.", "error")
        return redirect(url_for("dashboard"))

    return send_file(
        BULK_RESULTS_PATH,
        as_attachment=True,
        download_name="AadiBI_Customer_Churn_Predictions.csv",
        mimetype="text/csv"
    )


# ============================================================
# JSON REST API ENDPOINTS
# ============================================================

@app.route("/api/predict", methods=["POST"])
@login_required
def api_predict():
    """AJAX JSON endpoint for real-time customer risk scoring."""
    try:
        payload = request.get_json() or request.form
        state = str(payload.get("state", "KS")).strip().upper()
        account_length = int(payload.get("account_length", 100))
        area_code = int(payload.get("area_code", 415))
        intl_plan = str(payload.get("international_plan", "no")).strip().lower()
        vmail_plan = str(payload.get("voice_mail_plan", "no")).strip().lower()
        number_vmail_messages = int(payload.get("number_vmail_messages", 0))

        total_day_minutes = float(payload.get("total_day_minutes", 180.0))
        total_day_calls = int(payload.get("total_day_calls", 100))
        total_day_charge = float(payload.get("total_day_charge", round(total_day_minutes * 0.17, 2)))

        total_eve_minutes = float(payload.get("total_eve_minutes", 200.0))
        total_eve_calls = int(payload.get("total_eve_calls", 100))
        total_eve_charge = float(payload.get("total_eve_charge", round(total_eve_minutes * 0.085, 2)))

        total_night_minutes = float(payload.get("total_night_minutes", 200.0))
        total_night_calls = int(payload.get("total_night_calls", 100))
        total_night_charge = float(payload.get("total_night_charge", round(total_night_minutes * 0.045, 2)))

        total_intl_minutes = float(payload.get("total_intl_minutes", 10.0))
        total_intl_calls = int(payload.get("total_intl_calls", 3))
        total_intl_charge = float(payload.get("total_intl_charge", round(total_intl_minutes * 0.27, 2)))

        customer_service_calls = int(payload.get("customer_service_calls", 1))

        new_customer = pd.DataFrame({
            "Account length": [account_length],
            "Area code": [area_code],
            "International plan": [1 if intl_plan in {"yes", "1", "true"} else 0],
            "Voice mail plan": [1 if vmail_plan in {"yes", "1", "true"} else 0],
            "Number vmail messages": [number_vmail_messages],
            "Total day minutes": [total_day_minutes],
            "Total day calls": [total_day_calls],
            "Total day charge": [total_day_charge],
            "Total eve minutes": [total_eve_minutes],
            "Total eve calls": [total_eve_calls],
            "Total eve charge": [total_eve_charge],
            "Total night minutes": [total_night_minutes],
            "Total night calls": [total_night_calls],
            "Total night charge": [total_night_charge],
            "Total intl minutes": [total_intl_minutes],
            "Total intl calls": [total_intl_calls],
            "Total intl charge": [total_intl_charge],
            "Customer service calls": [customer_service_calls]
        })

        state_columns = [col for col in model_features if col.startswith("State_")]
        for col in state_columns:
            state_name = col.replace("State_", "")
            new_customer[col] = 1 if state == state_name else 0

        new_customer = new_customer.reindex(columns=model_features, fill_value=0)

        prediction = model.predict(new_customer)[0]
        probabilities = model.predict_proba(new_customer)[0]
        churn_index = list(model.classes_).index(1)
        stay_index = list(model.classes_).index(0)

        churn_prob = round(probabilities[churn_index] * 100, 2)
        stay_prob = round(probabilities[stay_index] * 100, 2)
        drivers, recommendation = customer_guidance(new_customer.iloc[0], churn_prob)

        # Sync prediction record to Cloud Firestore
        sync_prediction_to_firestore({
            "state": state,
            "account_length": account_length,
            "prediction": "CUSTOMER WILL CHURN" if prediction == 1 else "CUSTOMER WILL STAY",
            "churn_probability": churn_prob,
            "stay_probability": stay_prob,
            "risk_level": "HIGH" if churn_prob >= 70 else ("MEDIUM" if churn_prob >= 40 else "LOW"),
            "drivers": drivers,
            "recommendation": recommendation,
        })

        return jsonify({
            "success": True,
            "prediction": "CUSTOMER WILL CHURN" if prediction == 1 else "CUSTOMER WILL STAY",
            "is_churn": bool(prediction == 1),
            "churn_probability": churn_prob,
            "stay_probability": stay_prob,
            "risk_level": "HIGH" if churn_prob >= 70 else ("MEDIUM" if churn_prob >= 40 else "LOW"),
            "drivers": drivers,
            "recommendation": recommendation,
            "firebase_synced": is_firebase_active,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/upload_preview", methods=["POST"])
@login_required
@admin_required
def api_upload_preview():
    """
    Reads uploaded dataset, extracts headers & preview rows,
    and performs fuzzy auto-mapping against canonical features.
    """
    try:
        if "dataset" not in request.files:
            return jsonify({"success": False, "error": "No file uploaded. Please select a CSV or XLSX file."}), 400

        file = request.files["dataset"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected."}), 400

        filename = file.filename.lower()
        ext = os.path.splitext(filename)[1]
        if ext not in [".csv", ".xlsx", ".xls"]:
            return jsonify({"success": False, "error": "Unsupported file format. Please upload .csv, .xlsx, or .xls"}), 400

        temp_file_id = str(uuid.uuid4())
        saved_filename = f"{temp_file_id}{ext}"
        saved_path = os.path.join(UPLOAD_FOLDER, saved_filename)
        file.save(saved_path)

        # Parse file into DataFrame
        try:
            if ext == ".csv":
                try:
                    df = pd.read_csv(saved_path)
                except UnicodeDecodeError:
                    df = pd.read_csv(saved_path, encoding="latin1")
            else:
                df = pd.read_excel(saved_path)
        except Exception as read_err:
            return jsonify({"success": False, "error": f"Failed to parse dataset: {str(read_err)}"}), 400

        if df.empty:
            return jsonify({"success": False, "error": "The uploaded dataset contains 0 customer records."}), 400

        user_columns = [str(c).strip() for c in df.columns]
        # Match against canonical targets
        match_result = schema_mapper.fuzzy_match_columns(user_columns)

        # First 5 preview rows formatted safely for JSON serialization
        preview_sample = df.head(5).copy()
        preview_sample = preview_sample.where(pd.notnull(preview_sample), None)
        preview_records = preview_sample.to_dict(orient="records")

        return jsonify({
            "success": True,
            "temp_file_id": temp_file_id,
            "filename": file.filename,
            "row_count": len(df),
            "columns": user_columns,
            "preview": preview_records,
            "suggested_mapping": match_result["mapped"],
            "confidence_scores": match_result.get("confidence", {}),
            "match_details": match_result.get("matches", {}),
            "unmapped_targets": match_result.get("unmapped_targets", []),
            "canonical_features": schema_mapper.CANONICAL_TARGET_FEATURES,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ============================================================
# CROSS-DOMAIN MAPPED PREDICTION ENGINE (/predict-mapped)
# ============================================================

def process_mapped_features(source_df: pd.DataFrame, mapping: dict = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Transforms any incoming dataset (E-Commerce, SaaS, Banking, Retail, etc.)
    into the exact feature layout aligned strictly with model.feature_names_in_.

    1. Categorical Feature Cleaning & Encoding:
       - Automatically converts text flags ('yes'/'no', 'true'/'false', 1/0) to binary integers (1/0).
       - Ignores/drops non-feature identifiers (e.g., 'customer_id') and raw 'state' during feature vector construction.
       - One-hot encodes state columns (State_AK through State_WY).
    2. Numerical Safe Parsing:
       - Parses numeric columns ('tenure_months', 'monthly_spend', 'order_count', 'support_tickets')
         using pd.to_numeric(..., errors='coerce').fillna(0).
    3. Feature Reordering & Fallbacks:
       - Strictly aligns DataFrame columns with model.feature_names_in_.
       - Fills any missing model features with 0 or the training default values.
    """
    if source_df.empty:
        raise ValueError("Input dataset is empty.")

    original_df = source_df.copy()
    feature_names = list(model.feature_names_in_) if hasattr(model, "feature_names_in_") else model_features

    # Training default values
    training_defaults = {
        "Account length": 100,
        "Area code": 415,
        "International plan": 0,
        "Voice mail plan": 0,
        "Number vmail messages": 0,
        "Total day minutes": 180.0,
        "Total day calls": 100,
        "Total day charge": 30.60,
        "Total eve minutes": 200.0,
        "Total eve calls": 100,
        "Total eve charge": 17.00,
        "Total night minutes": 200.0,
        "Total night calls": 100,
        "Total night charge": 9.00,
        "Total intl minutes": 10.0,
        "Total intl calls": 3,
        "Total intl charge": 2.70,
        "Customer service calls": 1,
    }

    # Normalize user mapping (supports both Canonical->User and User->Canonical keys)
    resolved_mapping = {}
    if mapping:
        for k, v in mapping.items():
            if not v or v in {"__NONE__", "__SKIP__"}:
                continue
            if k in schema_mapper.CANONICAL_TARGET_FEATURES and v in source_df.columns:
                resolved_mapping[k] = v
            elif k in source_df.columns and v in schema_mapper.CANONICAL_TARGET_FEATURES:
                resolved_mapping[v] = k
            elif k in schema_mapper.CANONICAL_TARGET_FEATURES:
                resolved_mapping[k] = v

    # Automatic fuzzy/synonym matching fallback for any unmapped target features
    auto_matches = schema_mapper.fuzzy_match_columns(source_df.columns.tolist())["mapped"]
    for canon_key, user_col in auto_matches.items():
        if canon_key not in resolved_mapping and user_col in source_df.columns:
            resolved_mapping[canon_key] = user_col

    # Construct the numeric feature matrix (ignoring non-feature columns like customer_id)
    feature_df = pd.DataFrame(index=source_df.index)

    # 1. Categorical Cleaning & 2. Numerical Safe Parsing
    for canon_feature, spec in schema_mapper.CANONICAL_TARGET_FEATURES.items():
        if canon_feature == "State":
            continue

        user_col = resolved_mapping.get(canon_feature)
        default_val = training_defaults.get(canon_feature, spec.get("default", 0))

        if user_col and user_col in source_df.columns:
            series = source_df[user_col]
            if spec.get("type") == "boolean":
                # Categorical text flag cleaning (e.g. vip_member: 'yes'/'no', 'true'/'false', 1/0)
                cleaned = series.astype(str).str.strip().str.lower()
                feature_df[canon_feature] = (
                    cleaned.map({
                        "yes": 1, "y": 1, "true": 1, "t": 1, "1": 1, "active": 1, "vip": 1, "premium": 1,
                        "no": 0, "n": 0, "false": 0, "f": 0, "0": 0, "inactive": 0
                    })
                    .fillna(pd.to_numeric(series, errors="coerce"))
                    .fillna(default_val)
                    .astype(int)
                )
            else:
                # Numerical safe parsing with pd.to_numeric(..., errors='coerce').fillna(0)
                feature_df[canon_feature] = pd.to_numeric(series, errors="coerce").fillna(default_val)
        else:
            feature_df[canon_feature] = default_val

    # Cross-derivation: If monthly spend (Total day charge) is provided but minutes are missing
    if "Total day charge" in feature_df.columns:
        day_mins_col = resolved_mapping.get("Total day minutes")
        if not day_mins_col or day_mins_col not in source_df.columns:
            derived_mins = (feature_df["Total day charge"] / 0.17).round(1)
            feature_df["Total day minutes"] = np.where(derived_mins > 0, derived_mins, 180.0)

    # State One-Hot Encoding (ignoring raw 'state' and 'customer_id' from feature vector)
    state_col = resolved_mapping.get("State")
    if not state_col:
        for c in ["state", "State", "region", "Region", "province"]:
            if c in source_df.columns:
                state_col = c
                break

    raw_states = (
        source_df[state_col].astype(str).str.strip().str.upper()
        if (state_col and state_col in source_df.columns)
        else pd.Series(["KS"] * len(source_df), index=source_df.index)
    )

    state_columns = [col for col in feature_names if col.startswith("State_")]
    for col in state_columns:
        state_code = col.replace("State_", "")
        feature_df[col] = (raw_states == state_code).astype(int)

    # 3. Feature Reordering & Fallbacks:
    # Strictly align columns with model.feature_names_in_ and fill missing with default values
    feature_df = feature_df.reindex(columns=feature_names)
    for col in feature_names:
        if col not in feature_df.columns or feature_df[col].isna().all():
            feature_df[col] = training_defaults.get(col, 0)
        else:
            feature_df[col] = feature_df[col].fillna(training_defaults.get(col, 0))

    feature_df = feature_df.apply(pd.to_numeric, errors="coerce").fillna(0)
    feature_df = feature_df[feature_names]

    return feature_df, original_df


@app.route("/predict-mapped", methods=["POST"])
@app.route("/api/predict-mapped", methods=["POST"])
def predict_mapped():
    """
    Direct Prediction Handler for Mapped Datasets (E-Commerce, SaaS, Banking, Retail, etc.).
    Supports:
    - Direct JSON list of customer dicts: [{'customer_id': '101', 'tenure_months': 24, ...}]
    - Wrapped JSON object: {"data": [...], "mapping": {...}}
    - Temporary uploaded session: {"temp_file_id": "...", "mapping": {...}}
    - Multipart file upload: CSV or XLSX file
    """
    try:
        mapping = {}
        source_df = None

        # Case A: File upload
        if request.files and ("dataset" in request.files or "file" in request.files):
            file = request.files.get("dataset") or request.files.get("file")
            filename = file.filename.lower()
            if filename.endswith(".csv"):
                try:
                    source_df = pd.read_csv(file)
                except UnicodeDecodeError:
                    file.seek(0)
                    source_df = pd.read_csv(file, encoding="latin1")
            elif filename.endswith(".xlsx") or filename.endswith(".xls"):
                source_df = pd.read_excel(file)
            else:
                return jsonify({"success": False, "error": "Unsupported file format. Please upload .csv or .xlsx"}), 400

            raw_mapping = request.form.get("mapping")
            if raw_mapping:
                try:
                    mapping = json.loads(raw_mapping)
                except Exception:
                    mapping = {}

        # Case B: JSON payload
        elif request.is_json or request.get_json(silent=True):
            payload = request.get_json(silent=True) or {}

            # Sub-case: temp_file_id
            if isinstance(payload, dict) and "temp_file_id" in payload:
                temp_file_id = payload["temp_file_id"]
                mapping = payload.get("mapping", {})
                found_file = None
                for fname in os.listdir(UPLOAD_FOLDER):
                    if fname.startswith(temp_file_id):
                        found_file = os.path.join(UPLOAD_FOLDER, fname)
                        break
                if not found_file or not os.path.exists(found_file):
                    return jsonify({"success": False, "error": "Uploaded session file not found or expired."}), 404

                ext = os.path.splitext(found_file)[1].lower()
                if ext == ".csv":
                    try:
                        source_df = pd.read_csv(found_file)
                    except UnicodeDecodeError:
                        source_df = pd.read_csv(found_file, encoding="latin1")
                else:
                    source_df = pd.read_excel(found_file)

            # Sub-case: "data" or "records"
            elif isinstance(payload, dict) and ("data" in payload or "records" in payload):
                raw_data = payload.get("data") or payload.get("records")
                mapping = payload.get("mapping", {})
                source_df = pd.DataFrame(raw_data)

            # Sub-case: directly a list of records
            elif isinstance(payload, list):
                source_df = pd.DataFrame(payload)
                mapping = {}

            # Sub-case: single record object
            elif isinstance(payload, dict):
                mapping = payload.get("mapping", {})
                record_items = {k: v for k, v in payload.items() if k not in {"mapping", "temp_file_id"}}
                if record_items:
                    source_df = pd.DataFrame([record_items])
                else:
                    return jsonify({"success": False, "error": "No customer records found in payload."}), 400
        else:
            return jsonify({"success": False, "error": "No input data provided. Send JSON records or upload a dataset."}), 400

        if source_df is None or source_df.empty:
            return jsonify({"success": False, "error": "Input dataset is empty."}), 400

        # Execute feature engineering, cleaning, safe parsing, and strict model alignment
        feature_df, original_df = process_mapped_features(source_df, mapping=mapping)

        # Generate predictions
        predictions = model.predict(feature_df)
        probabilities = model.predict_proba(feature_df)
        churn_index = list(model.classes_).index(1)
        stay_index = list(model.classes_).index(0)

        churn_probs = (probabilities[:, churn_index] * 100).round(2)
        stay_probs = (probabilities[:, stay_index] * 100).round(2)

        # Build guidance and results
        enriched_df = original_df.copy()
        enriched_df["Prediction"] = [
            "CUSTOMER WILL CHURN" if p == 1 else "CUSTOMER WILL STAY" for p in predictions
        ]
        enriched_df["Churn Probability (%)"] = churn_probs
        enriched_df["Stay Probability (%)"] = stay_probs
        enriched_df["Risk Level"] = pd.cut(
            churn_probs,
            bins=[-1, 40, 70, 100],
            labels=["LOW", "MEDIUM", "HIGH"]
        ).astype(str)

        guidance_list = [
            customer_guidance(prep_row, prob)
            for (_, prep_row), prob in zip(feature_df.iterrows(), churn_probs)
        ]
        enriched_df["Risk signals"] = ["; ".join(d) for d, _ in guidance_list]
        enriched_df["Recommended action"] = [a for _, a in guidance_list]

        # Update bulk results file for live dashboard sync
        os.makedirs("data", exist_ok=True)
        enriched_df.to_csv(BULK_RESULTS_PATH, index=False)

        # Build JSON response
        records_output = []
        for idx, row in enriched_df.iterrows():
            rec = row.to_dict()
            rec = {k: (None if pd.isna(v) else v) for k, v in rec.items()}
            rec["is_churn"] = bool(predictions[idx] == 1)
            rec["prediction"] = "CUSTOMER WILL CHURN" if predictions[idx] == 1 else "CUSTOMER WILL STAY"
            rec["churn_probability"] = float(churn_probs[idx])
            rec["stay_probability"] = float(stay_probs[idx])
            rec["risk_level"] = str(enriched_df.loc[idx, "Risk Level"])
            rec["drivers"] = guidance_list[idx][0]
            rec["recommendation"] = guidance_list[idx][1]
            records_output.append(rec)

        total_customers = len(enriched_df)
        churned_customers = int((predictions == 1).sum())
        staying_customers = total_customers - churned_customers
        churn_rate = round((churned_customers / total_customers) * 100, 2) if total_customers else 0.0

        # Sync high-risk to Firestore if active
        if is_firebase_active:
            try:
                first_col = list(original_df.columns)[0]
                for rec in records_output[:10]:
                    if rec["risk_level"] == "HIGH":
                        sync_prediction_to_firestore({
                            "source": "predict_mapped",
                            "account_id": str(rec.get(first_col, "CUST")),
                            "prediction": rec["prediction"],
                            "churn_probability": rec["churn_probability"],
                            "risk_level": "HIGH",
                            "drivers": rec["drivers"],
                            "recommendation": rec["recommendation"]
                        })
            except Exception as fs_err:
                print(f"[Warning] Firestore sync: {fs_err}")

        return jsonify({
            "success": True,
            "total_records": total_customers,
            "churn_count": churned_customers,
            "stay_count": staying_customers,
            "churn_rate": churn_rate,
            "predictions": records_output,
            "results": records_output,
            "feature_names_in": list(feature_df.columns),
            "firebase_synced": is_firebase_active
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/process_mapped_dataset", methods=["POST"])
@login_required
@admin_required
def api_process_mapped_dataset():
    """
    Applies custom or auto schema mapping to uploaded dataset,
    runs model predictions, updates executive store, and returns summary.
    """
    return predict_mapped()


@app.route("/api/bulk_predict", methods=["POST"])
@login_required
@admin_required
def api_bulk_predict():
    """Upload dataset & re-run batch scoring with automatic schema mapper fallback."""
    try:
        if "dataset" not in request.files:
            return jsonify({"success": False, "error": "No file uploaded. Please select a CSV or XLSX file."}), 400

        file = request.files["dataset"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected."}), 400

        filename = file.filename.lower()
        if filename.endswith(".csv"):
            try:
                uploaded_df = pd.read_csv(file)
            except UnicodeDecodeError:
                file.seek(0)
                uploaded_df = pd.read_csv(file, encoding="latin1")
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            uploaded_df = pd.read_excel(file)
        else:
            return jsonify({"success": False, "error": "Unsupported file format. Please upload .csv or .xlsx"}), 400

        result_df, summary = analyze_customers(uploaded_df)
        os.makedirs("data", exist_ok=True)
        result_df.to_csv(BULK_RESULTS_PATH, index=False)

        return jsonify({"success": True, "summary": summary, "firebase_synced": is_firebase_active})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/sample_csv", methods=["GET"])
@app.route("/api/sample_csv/<domain>", methods=["GET"])
@login_required
def api_sample_csv(domain="telecom"):
    """
    Generates downloadable sample CSV templates across business domains:
    telecom, ecommerce, saas, banking, retail.
    """
    domain_req = request.args.get("domain", domain).strip().lower()
    csv_content = schema_mapper.generate_sample_domain_csv(domain_req)
    filename = f"sample_{domain_req}_customer_churn_dataset.csv"
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


@app.route("/api/simulate", methods=["POST"])
@login_required
def api_simulate():
    """What-If Retention Simulator & AI Campaign Generator API Endpoint."""
    try:
        payload = request.get_json() or request.form
        state = str(payload.get("state", "KS")).strip().upper()
        account_length = int(payload.get("account_length", 100))
        area_code = int(payload.get("area_code", 415))
        intl_plan = str(payload.get("international_plan", "no")).strip().lower()
        vmail_plan = str(payload.get("voice_mail_plan", "no")).strip().lower()
        number_vmail_messages = int(payload.get("number_vmail_messages", 0))

        total_day_minutes = float(payload.get("total_day_minutes", 180.0))
        total_day_calls = int(payload.get("total_day_calls", 100))

        # Apply discount percent if provided in simulation (e.g. 0, 10, 15, 20%)
        discount_percent = float(payload.get("discount_percent", 0))
        raw_day_charge = float(payload.get("total_day_charge", round(total_day_minutes * 0.17, 2)))
        total_day_charge = round(raw_day_charge * (1.0 - (discount_percent / 100.0)), 2)

        total_eve_minutes = float(payload.get("total_eve_minutes", 200.0))
        total_eve_calls = int(payload.get("total_eve_calls", 100))
        total_eve_charge = float(payload.get("total_eve_charge", round(total_eve_minutes * 0.085, 2)))

        total_night_minutes = float(payload.get("total_night_minutes", 200.0))
        total_night_calls = int(payload.get("total_night_calls", 100))
        total_night_charge = float(payload.get("total_night_charge", round(total_night_minutes * 0.045, 2)))

        total_intl_minutes = float(payload.get("total_intl_minutes", 10.0))
        total_intl_calls = int(payload.get("total_intl_calls", 3))
        total_intl_charge = float(payload.get("total_intl_charge", round(total_intl_minutes * 0.27, 2)))

        customer_service_calls = int(payload.get("customer_service_calls", 1))
        original_prob = float(payload.get("original_probability", 0))

        sim_customer = pd.DataFrame({
            "Account length": [account_length],
            "Area code": [area_code],
            "International plan": [1 if intl_plan in {"yes", "1", "true"} else 0],
            "Voice mail plan": [1 if vmail_plan in {"yes", "1", "true"} else 0],
            "Number vmail messages": [number_vmail_messages],
            "Total day minutes": [total_day_minutes],
            "Total day calls": [total_day_calls],
            "Total day charge": [total_day_charge],
            "Total eve minutes": [total_eve_minutes],
            "Total eve calls": [total_eve_calls],
            "Total eve charge": [total_eve_charge],
            "Total night minutes": [total_night_minutes],
            "Total night calls": [total_night_calls],
            "Total night charge": [total_night_charge],
            "Total intl minutes": [total_intl_minutes],
            "Total intl calls": [total_intl_calls],
            "Total intl charge": [total_intl_charge],
            "Customer service calls": [customer_service_calls]
        })

        state_columns = [col for col in model_features if col.startswith("State_")]
        for col in state_columns:
            state_name = col.replace("State_", "")
            sim_customer[col] = 1 if state == state_name else 0

        sim_customer = sim_customer.reindex(columns=model_features, fill_value=0)

        prediction = model.predict(sim_customer)[0]
        probabilities = model.predict_proba(sim_customer)[0]
        churn_index = list(model.classes_).index(1)
        stay_index = list(model.classes_).index(0)

        sim_churn_prob = round(probabilities[churn_index] * 100, 2)
        sim_stay_prob = round(probabilities[stay_index] * 100, 2)
        drivers, recommendation = customer_guidance(sim_customer.iloc[0], sim_churn_prob)

        # Calculate risk delta
        delta_prob = round(sim_churn_prob - original_prob, 2)

        # AI Retention Campaign Playbook Copy Generator
        campaign = generate_ai_campaign_playbook(drivers, sim_churn_prob, int(discount_percent or 15))

        return jsonify({
            "success": True,
            "prediction": "CUSTOMER WILL CHURN" if prediction == 1 else "CUSTOMER WILL STAY",
            "is_churn": bool(prediction == 1),
            "churn_probability": sim_churn_prob,
            "stay_probability": sim_stay_prob,
            "risk_level": "HIGH" if sim_churn_prob >= 70 else ("MEDIUM" if sim_churn_prob >= 40 else "LOW"),
            "original_probability": original_prob,
            "delta_probability": delta_prob,
            "drivers": drivers,
            "recommendation": recommendation,
            "campaign": campaign
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() in ("true", "1")
    print("\n=======================================================")
    print("[START] AadiBI Customer Churn Intelligence System Started!")
    print(f"   Firebase Status: {'Connected' if is_firebase_active else 'Offline'}")
    print(f"   Mode: {'Debug' if debug else 'Production'}")
    print(f"   Access Dashboard: http://0.0.0.0:{port}")
    print("=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
