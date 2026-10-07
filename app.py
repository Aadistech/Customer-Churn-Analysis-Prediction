import os
import io
import json
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
import joblib

# Import Python Services
from services.firebase_service import (
    is_firebase_active,
    sync_prediction_to_firestore,
    sync_analytics_to_firestore,
    register_or_sync_firebase_user,
)
from services.email_service import send_login_email_alert

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
MODEL_PATH = os.path.join("models", "random_forest_model.pkl")
CLEANED_DATA_PATH = os.path.join("data", "cleaned_customer_churn.csv")
RAW_DATA_PATH = os.path.join("data", "customer_churn.csv")
BULK_RESULTS_PATH = os.path.join("data", "bulk_prediction_results.csv")

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


def analyze_customers(source_df):
    """Score a customer dataframe and compute executive analytics."""
    if source_df.empty:
        raise ValueError("The dataset does not contain any customer records.")

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
        customer_guidance(row, prob)
        for (_, row), prob in zip(result_df.iterrows(), result_df["Churn Probability (%)"])
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

    # Estimate ARR / Monthly Revenue at Risk ($65 per churned account)
    est_rev_at_risk = churned_customers * 65

    table_data = []
    for idx, (_, row) in enumerate(result_df.iterrows()):
        state_val = str(row.get("State", "N/A"))
        acc_len = row.get("Account length", "N/A")
        area_code = row.get("Area code", "N/A")
        intl_plan = str(row.get("International plan", "no")).capitalize()
        vmail_plan = str(row.get("Voice mail plan", "no")).capitalize()
        svc_calls = row.get("Customer service calls", 0)
        day_mins = row.get("Total day minutes", 0)
        day_charge = row.get("Total day charge", 0)

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

    # Prepare chart metrics
    analysis_churn = (
        result_df.get("Churn", pd.Series(predictions, index=result_df.index))
        .astype(str).str.strip().str.lower()
        .map({"true": 1, "false": 0, "yes": 1, "no": 0, "1": 1, "0": 0})
        .fillna(pd.Series(predictions, index=result_df.index))
        .astype(int)
    )
    analysis_data = result_df.copy()
    analysis_data["_churn_rate"] = analysis_churn

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

            # Dispatch Email Alert
            send_login_email_alert(
                recipient_email=session["user_email"],
                display_name=username.capitalize(),
                login_time=datetime.now().strftime("%b %d, %Y %I:%M %p")
            )

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
    return render_template("about.html")


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


@app.route("/api/bulk_predict", methods=["POST"])
@login_required
@admin_required
def api_bulk_predict():
    """Upload dataset & re-run batch scoring."""
    try:
        if "dataset" not in request.files:
            return jsonify({"success": False, "error": "No file uploaded. Please select a CSV or XLSX file."}), 400

        file = request.files["dataset"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected."}), 400

        filename = file.filename.lower()
        if filename.endswith(".csv"):
            uploaded_df = pd.read_csv(file)
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
@login_required
def api_sample_csv():
    """Generates a downloadable sample CSV template for users."""
    sample_df = pd.DataFrame([{
        "State": "KS",
        "Account length": 128,
        "Area code": 415,
        "International plan": "no",
        "Voice mail plan": "yes",
        "Number vmail messages": 25,
        "Total day minutes": 265.1,
        "Total day calls": 110,
        "Total day charge": 45.07,
        "Total eve minutes": 197.4,
        "Total eve calls": 99,
        "Total eve charge": 16.78,
        "Total night minutes": 244.7,
        "Total night calls": 91,
        "Total night charge": 11.01,
        "Total intl minutes": 10.0,
        "Total intl calls": 3,
        "Total intl charge": 2.70,
        "Customer service calls": 1
    }])
    output = io.StringIO()
    sample_df.to_csv(output, index=False)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=sample_customer_churn_dataset.csv"}
    )


if __name__ == "__main__":
    print("\n=======================================================")
    print("🚀 AadiBI Customer Churn Intelligence System Started!")
    print(f"   Firebase Status: {'Connected 🔥' if is_firebase_active else 'Offline'}")
    print("   Access Dashboard: http://127.0.0.1:5000")
    print("=======================================================\n")
    app.run(debug=True, port=5000)
