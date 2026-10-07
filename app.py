from flask import Flask, render_template, request, send_file, redirect, url_for, session, flash
import pandas as pd
import joblib
import os
from functools import wraps

# ============================================================
# MODULE 8 + MODULE 9: FLASK BACKEND
# CUSTOMER CHURN ANALYSIS & PREDICTION SYSTEM
# ============================================================

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "local-development-change-me"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# Local demo accounts
USERS = {
    "admin": {"password": os.environ.get("CHURN_ADMIN_PASSWORD", "admin123"), "role": "admin"},
    "analyst": {"password": os.environ.get("CHURN_ANALYST_PASSWORD", "analyst123"), "role": "analyst"},
}


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Only administrators can upload and replace customer datasets.", "error")
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)
    return wrapped_view


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        user = USERS.get(username)
        if user and password == user["password"]:
            session.clear()
            session["username"] = username
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


print("\n===== FLASK APPLICATION STARTED =====")



# ============================================================
# LOAD TRAINED MODEL & PREPARATION
# ============================================================

model = joblib.load("models/random_forest_model.pkl")
df_cleaned = pd.read_csv("data/cleaned_customer_churn.csv")
X = df_cleaned.drop("Churn", axis=1)
model_features = X.columns.tolist()

print("Random Forest model loaded successfully.")
print("Number of model features:", len(model_features))


def customer_guidance(customer, churn_probability):
    """Generate transparent, rule-based risk signals and a retention action."""
    def numeric(name):
        return pd.to_numeric(pd.Series([customer.get(name, 0)]), errors="coerce").fillna(0).iloc[0]

    def is_yes(name):
        return str(customer.get(name, "")).strip().lower() in {"yes", "1", "true"}

    drivers = []
    if numeric("Customer service calls") >= 4:
        drivers.append("Frequent customer service calls")
    if numeric("Total day minutes") >= 250:
        drivers.append("Very high daytime usage")
    if is_yes("International plan") and numeric("Total intl minutes") >= 10:
        drivers.append("High international-plan usage")
    if numeric("Total eve minutes") >= 280:
        drivers.append("High evening usage")
    if numeric("Account length") <= 12:
        drivers.append("New customer account")

    if not drivers:
        drivers.append("No strong risk signal detected")

    if churn_probability >= 70:
        action = "Urgent: contact the customer within 24 hours and offer a tailored retention plan."
    elif churn_probability >= 40:
        action = "Review the account this week and send a proactive service or plan offer."
    else:
        action = "Maintain engagement and monitor future usage or service-call changes."
    return drivers[:3], action


def analyze_customers(source_df):
    """Score a customer dataset and return dashboard-ready results."""
    if source_df.empty:
        raise ValueError("The dataset does not contain any customer records.")

    original = source_df.copy()
    data = source_df.drop(columns=["Churn"], errors="ignore").copy()
    state_columns = [column for column in model_features if column.startswith("State_")]

    for column in ("International plan", "Voice mail plan"):
        if column in data.columns:
            values = data[column].astype(str).str.strip().str.lower()
            data[column] = values.map({"yes": 1, "no": 0}).fillna(
                pd.to_numeric(data[column], errors="coerce")
            )

    state_values = data["State"].astype(str).str.strip().str.upper() if "State" in data else ""
    for column in state_columns:
        state_name = column.replace("State_", "")
        data[column] = state_values.eq(state_name).astype(int) if "State" in data else 0

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
        "CUSTOMER WILL CHURN" if prediction == 1 else "CUSTOMER WILL STAY"
        for prediction in predictions
    ]
    result_df["Churn Probability (%)"] = (probabilities[:, churn_index] * 100).round(2)
    result_df["Stay Probability (%)"] = (probabilities[:, stay_index] * 100).round(2)
    result_df["Risk Level"] = pd.cut(
        result_df["Churn Probability (%)"],
        bins=[-1, 40, 70, 100],
        labels=["LOW", "MEDIUM", "HIGH"],
    ).astype(str)
    
    guidance = [
        customer_guidance(row, probability)
        for (_, row), probability in zip(
            result_df.iterrows(), result_df["Churn Probability (%)"]
        )
    ]
    result_df["Risk signals"] = ["; ".join(drivers) for drivers, _ in guidance]
    result_df["Recommended action"] = [action for _, action in guidance]

    total_customers = len(result_df)
    churned_customers = int((predictions == 1).sum())
    staying_customers = total_customers - churned_customers
    high_risk_customers = int((result_df["Risk Level"] == "HIGH").sum())
    churn_rate = round(churned_customers / total_customers * 100, 2)
    high_risk_rate = round(high_risk_customers / total_customers * 100, 2)

    table_data = [
        {
            "customer": index + 1,
            "prediction": "CHURN" if row["Prediction"] == "CUSTOMER WILL CHURN" else "STAY",
            "churn_probability": float(row["Churn Probability (%)"]),
            "risk": row["Risk Level"],
            "signals": row["Risk signals"],
            "action": row["Recommended action"],
        }
        for index, (_, row) in enumerate(result_df.head(20).iterrows())
    ]

    known_churn = original.get("Churn", pd.Series(predictions, index=original.index))
    analysis_churn = (
        known_churn.astype(str).str.strip().str.lower()
        .map({"true": 1, "false": 0, "yes": 1, "no": 0, "1": 1, "0": 0})
        .fillna(pd.Series(predictions, index=original.index))
        .astype(int)
    )
    analysis_data = original.copy()
    analysis_data["_churn_rate"] = analysis_churn

    def churn_series(column, labels=None):
        if column not in analysis_data.columns:
            return []
        grouped = analysis_data.groupby(column, observed=False)["_churn_rate"].mean()
        return [
            {
                "label": labels.get(str(key), str(key)) if labels else str(key),
                "value": round(float(value) * 100, 1),
            }
            for key, value in grouped.items()
            if pd.notna(key)
        ]

    service_bands = pd.cut(
        pd.to_numeric(analysis_data.get("Customer service calls", pd.Series(dtype=float)), errors="coerce"),
        bins=[-1, 0, 1, 2, 3, float("inf")],
        labels=["0", "1", "2", "3", "4+"],
    )
    day_bands = pd.cut(
        pd.to_numeric(analysis_data.get("Total day minutes", pd.Series(dtype=float)), errors="coerce"),
        bins=[-1, 150, 200, 250, float("inf")],
        labels=["0–150", "151–200", "201–250", "250+"],
    )
    analysis_data["Service calls"] = service_bands
    analysis_data["Day minutes"] = day_bands
    charts = {
        "international": churn_series(
            "International plan", {"Yes": "International plan", "No": "No international plan", "1": "International plan", "0": "No international plan"}
        ),
        "voicemail": churn_series(
            "Voice mail plan", {"Yes": "Voice mail", "No": "No voice mail", "1": "Voice mail", "0": "No voice mail"}
        ),
        "service_calls": churn_series("Service calls"),
        "day_minutes": churn_series("Day minutes"),
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
        "high_risk_rate": high_risk_rate,
        "low_medium_risk": total_customers - high_risk_customers,
        "low_medium_risk_rate": round(100 - high_risk_rate, 2),
        "results": table_data,
        "table_data": table_data,
        "charts": charts,
        "download_available": True,
    }
    return result_df, summary


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
@login_required
def home():
    return render_template("index.html")


@app.route("/about")
@login_required
def about():
    return render_template("about.html")


@app.route("/dashboard")
@login_required
def dashboard():
    """Analyze every customer in the included dataset in one request."""
    try:
        dataset_path = os.path.join("data", "customer_churn.csv")
        customers = pd.read_csv(dataset_path)
        result_df, summary = analyze_customers(customers)
        os.makedirs("data", exist_ok=True)
        result_df.to_csv(os.path.join("data", "bulk_prediction_results.csv"), index=False)
        return render_template("bulk_result.html", **summary)
    except Exception as error:
        return render_template(
            "error.html",
            title="Dashboard unavailable",
            message=str(error),
        ), 400


@app.route("/bulk")
@login_required
@admin_required
def bulk():
    return render_template("bulk_upload.html")


@app.route("/predict", methods=["POST"])
@login_required
def predict():
    try:
        state = request.form.get("state", "").strip().upper()
        account_length = int(request.form.get("account_length", 0))
        area_code = int(request.form.get("area_code", 0))
        international_plan = request.form.get("international_plan", "").strip().lower()
        voice_mail_plan = request.form.get("voice_mail_plan", "").strip().lower()
        number_vmail_messages = int(request.form.get("number_vmail_messages", 0))

        total_day_minutes = float(request.form.get("total_day_minutes", 0.0))
        total_day_calls = int(request.form.get("total_day_calls", 0))
        total_day_charge = float(request.form.get("total_day_charge", 0.0))

        total_eve_minutes = float(request.form.get("total_eve_minutes", 0.0))
        total_eve_calls = int(request.form.get("total_eve_calls", 0))
        total_eve_charge = float(request.form.get("total_eve_charge", 0.0))

        total_night_minutes = float(request.form.get("total_night_minutes", 0.0))
        total_night_calls = int(request.form.get("total_night_calls", 0))
        total_night_charge = float(request.form.get("total_night_charge", 0.0))

        total_intl_minutes = float(request.form.get("total_intl_minutes", 0.0))
        total_intl_calls = int(request.form.get("total_intl_calls", 0))
        total_intl_charge = float(request.form.get("total_intl_charge", 0.0))

        customer_service_calls = int(request.form.get("customer_service_calls", 0))

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

        prediction = model.predict(new_customer)
        probability = model.predict_proba(new_customer)

        stay_probability = round(probability[0][0] * 100, 2)
        churn_probability = round(probability[0][1] * 100, 2)
        result = "CUSTOMER WILL CHURN" if prediction[0] == 1 else "CUSTOMER WILL STAY"

        drivers, recommendation = customer_guidance(new_customer.iloc[0], churn_probability)

        return render_template(
            "result.html",
            prediction=result,
            stay_probability=stay_probability,
            churn_probability=churn_probability,
            drivers=drivers,
            recommendation=recommendation
        )

    except Exception as e:
        print("Individual prediction error:", e)
        return render_template(
            "error.html",
            title="Prediction Error",
            message=str(e),
        ), 400


@app.route("/bulk_predict", methods=["POST"])
@login_required
@admin_required
def bulk_predict():
    try:
        print("\n====================================")
        print("       BULK PREDICTION STARTED")
        print("====================================")

        if "dataset" not in request.files:
            return render_template(
                "error.html",
                title="No file uploaded",
                message="Please select a CSV or XLSX dataset file to upload.",
            ), 400

        file = request.files["dataset"]
        if file.filename == "":
            return render_template(
                "error.html",
                title="No file selected",
                message="Please select a dataset before clicking Analyze Dataset.",
            ), 400

        filename = file.filename.lower()
        if filename.endswith(".csv"):
            uploaded_df = pd.read_csv(file)
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            uploaded_df = pd.read_excel(file)
        else:
            return render_template(
                "error.html",
                title="Unsupported File Format",
                message="Please upload a file in .csv or .xlsx format.",
            ), 400

        result_df, summary = analyze_customers(uploaded_df)
        os.makedirs("data", exist_ok=True)
        result_df.to_csv(os.path.join("data", "bulk_prediction_results.csv"), index=False)
        return render_template("bulk_result.html", **summary)

    except Exception as e:
        print("Bulk prediction error:", e)
        return render_template(
            "error.html",
            title="Dataset Analysis Error",
            message=str(e),
        ), 400


@app.route("/download_results")
@login_required
def download_results():
    output_path = os.path.join("data", "bulk_prediction_results.csv")
    if not os.path.exists(output_path):
        return render_template(
            "error.html",
            title="No Prediction Results",
            message="No prediction results available. Please run a prediction or bulk analysis first.",
        ), 404

    return send_file(
        output_path,
        as_attachment=True,
        download_name="customer_churn_predictions.csv"
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)

