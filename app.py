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

# Local demo accounts. Set the matching environment variables before sharing
# the app outside your own computer.
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
# LOAD TRAINED MODEL
# ============================================================

model = joblib.load(
    "models/random_forest_model.pkl"
)

# Load cleaned dataset to get the exact
# feature structure used during training
df = pd.read_csv(
    "data/cleaned_customer_churn.csv"
)

# Separate features from target
X = df.drop(
    "Churn",
    axis=1
)

# Exact feature order used during model training
model_features = X.columns.tolist()


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
    required_columns = [column for column in model_features if column not in state_columns]
    missing_columns = [column for column in required_columns if column not in data.columns]

    if missing_columns:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing_columns)
        )

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

    # Dashboard charts use the known churn label when a source dataset has it;
    # uploaded datasets without a label use the model prediction instead.
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
        pd.to_numeric(analysis_data["Customer service calls"], errors="coerce"),
        bins=[-1, 0, 1, 2, 3, float("inf")],
        labels=["0", "1", "2", "3", "4+"],
    )
    day_bands = pd.cut(
        pd.to_numeric(analysis_data["Total day minutes"], errors="coerce"),
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
        "stay_count": total_customers - churned_customers,
        "churn_rate": churn_rate,
        "stay_rate": round(100 - churn_rate, 2),
        "high_risk": high_risk_customers,
        "high_risk_rate": high_risk_rate,
        "low_medium_risk": total_customers - high_risk_customers,
        "low_medium_risk_rate": round(100 - high_risk_rate, 2),
        "results": table_data,
        "charts": charts,
        "download_available": True,
    }
    return result_df, summary

print(
    "Random Forest model loaded successfully."
)

print(
    "Number of model features:",
    len(model_features)
)


# ============================================================
# HOME ROUTE
# ============================================================

@app.route("/")
@login_required
def home():

    return render_template(
        "index.html"
    )


@app.route("/dashboard")
@login_required
def dashboard():
    """Analyze every customer in the included dataset in one request."""
    try:
        dataset_path = os.path.join("data", "customer_churn.csv")
        customers = pd.read_csv(dataset_path)
        result_df, summary = analyze_customers(customers)
        result_df.to_csv(os.path.join("data", "bulk_prediction_results.csv"), index=False)
        return render_template("bulk_result.html", **summary)
    except Exception as error:
        return render_template(
            "error.html",
            title="Dashboard unavailable",
            message=str(error),
        ), 400


# ============================================================
# BULK UPLOAD PAGE
# ============================================================

@app.route("/bulk")
@login_required
@admin_required
def bulk():

    return render_template(
        "bulk_upload.html"
    )


# ============================================================
# INDIVIDUAL CUSTOMER PREDICTION
# ============================================================

@app.route(
    "/predict",
    methods=["POST"]
)
@login_required
def predict():

    try:

        # ----------------------------------------------------
        # GET CUSTOMER INFORMATION FROM FORM
        # ----------------------------------------------------

        state = request.form[
            "state"
        ].strip().upper()

        account_length = int(
            request.form[
                "account_length"
            ]
        )

        area_code = int(
            request.form[
                "area_code"
            ]
        )

        international_plan = request.form[
            "international_plan"
        ]

        voice_mail_plan = request.form[
            "voice_mail_plan"
        ]

        number_vmail_messages = int(
            request.form[
                "number_vmail_messages"
            ]
        )

        total_day_minutes = float(
            request.form[
                "total_day_minutes"
            ]
        )

        total_day_calls = int(
            request.form[
                "total_day_calls"
            ]
        )

        total_day_charge = float(
            request.form[
                "total_day_charge"
            ]
        )

        total_eve_minutes = float(
            request.form[
                "total_eve_minutes"
            ]
        )

        total_eve_calls = int(
            request.form[
                "total_eve_calls"
            ]
        )

        total_eve_charge = float(
            request.form[
                "total_eve_charge"
            ]
        )

        total_night_minutes = float(
            request.form[
                "total_night_minutes"
            ]
        )

        total_night_calls = int(
            request.form[
                "total_night_calls"
            ]
        )

        total_night_charge = float(
            request.form[
                "total_night_charge"
            ]
        )

        total_intl_minutes = float(
            request.form[
                "total_intl_minutes"
            ]
        )

        total_intl_calls = int(
            request.form[
                "total_intl_calls"
            ]
        )

        total_intl_charge = float(
            request.form[
                "total_intl_charge"
            ]
        )

        customer_service_calls = int(
            request.form[
                "customer_service_calls"
            ]
        )


        # ----------------------------------------------------
        # CREATE CUSTOMER DATAFRAME
        # ----------------------------------------------------

        new_customer = pd.DataFrame({

            "Account length": [
                account_length
            ],

            "Area code": [
                area_code
            ],

            "International plan": [
                1
                if international_plan == "Yes"
                else 0
            ],

            "Voice mail plan": [
                1
                if voice_mail_plan == "Yes"
                else 0
            ],

            "Number vmail messages": [
                number_vmail_messages
            ],

            "Total day minutes": [
                total_day_minutes
            ],

            "Total day calls": [
                total_day_calls
            ],

            "Total day charge": [
                total_day_charge
            ],

            "Total eve minutes": [
                total_eve_minutes
            ],

            "Total eve calls": [
                total_eve_calls
            ],

            "Total eve charge": [
                total_eve_charge
            ],

            "Total night minutes": [
                total_night_minutes
            ],

            "Total night calls": [
                total_night_calls
            ],

            "Total night charge": [
                total_night_charge
            ],

            "Total intl minutes": [
                total_intl_minutes
            ],

            "Total intl calls": [
                total_intl_calls
            ],

            "Total intl charge": [
                total_intl_charge
            ],

            "Customer service calls": [
                customer_service_calls
            ]
        })


        # ----------------------------------------------------
        # STATE ONE-HOT ENCODING
        # ----------------------------------------------------

        state_columns = [

            column

            for column in model_features

            if column.startswith(
                "State_"
            )

        ]


        for column in state_columns:

            state_name = column.replace(
                "State_",
                ""
            )

            if state == state_name:

                new_customer[
                    column
                ] = 1

            else:

                new_customer[
                    column
                ] = 0


        # ----------------------------------------------------
        # MATCH EXACT MODEL FEATURE ORDER
        # ----------------------------------------------------

        new_customer = new_customer.reindex(

            columns=model_features,

            fill_value=0

        )


        # ----------------------------------------------------
        # MAKE PREDICTION
        # ----------------------------------------------------

        prediction = model.predict(
            new_customer
        )

        probability = model.predict_proba(
            new_customer
        )


        stay_probability = round(
            probability[0][0] * 100,
            2
        )

        churn_probability = round(
            probability[0][1] * 100,
            2
        )


        # ----------------------------------------------------
        # DETERMINE RESULT
        # ----------------------------------------------------

        if prediction[0] == 1:

            result = (
                "CUSTOMER WILL CHURN"
            )

        else:

            result = (
                "CUSTOMER WILL STAY"
            )

        drivers, recommendation = customer_guidance(
            new_customer.iloc[0], churn_probability
        )


        # ----------------------------------------------------
        # SEND RESULT TO FRONTEND
        # ----------------------------------------------------

        return render_template(

            "result.html",

            prediction=result,

            stay_probability=
                stay_probability,

            churn_probability=
                churn_probability,

            drivers=drivers,

            recommendation=recommendation

        )


    except Exception as e:

        print(
            "Individual prediction error:",
            e
        )

        return f"""

        <h2>Prediction Error</h2>

        <p>{e}</p>

        <a href="/">
            Go Back
        </a>

        """


# ============================================================
# BULK CUSTOMER PREDICTION
# ============================================================

@app.route(
    "/bulk_predict",
    methods=["POST"]
)
@login_required
@admin_required
def bulk_predict():

    try:

        print("\n====================================")
        print("       BULK PREDICTION STARTED")
        print("====================================")


        # ----------------------------------------------------
        # CHECK FILE
        # ----------------------------------------------------

        if "dataset" not in request.files:

            return """

            <h2>No dataset uploaded.</h2>

            <a href="/bulk">
                Go Back
            </a>

            """


        file = request.files[
            "dataset"
        ]


        if file.filename == "":

            return """

            <h2>No file selected.</h2>

            <a href="/bulk">
                Go Back
            </a>

            """


        # ----------------------------------------------------
        # READ CSV / EXCEL
        # ----------------------------------------------------

        filename = (
            file.filename.lower()
        )


        if filename.endswith(
            ".csv"
        ):

            uploaded_df = pd.read_csv(
                file
            )


        elif filename.endswith(
            ".xlsx"
        ):

            uploaded_df = pd.read_excel(
                file
            )


        else:

            return """

            <h2>Invalid file format.</h2>

            <p>
            Please upload a CSV or XLSX file.
            </p>

            <a href="/bulk">
                Go Back
            </a>

            """


        # Use the validated dashboard pipeline for every uploaded dataset.
        # It accepts both raw Yes/No fields and already-cleaned 0/1 fields.
        result_df, summary = analyze_customers(uploaded_df)
        result_df.to_csv(
            os.path.join("data", "bulk_prediction_results.csv"), index=False
        )
        return render_template("bulk_result.html", **summary)

        print(
            "Uploaded dataset shape:",
            uploaded_df.shape
        )


        # ----------------------------------------------------
        # CHECK EMPTY DATASET
        # ----------------------------------------------------

        if uploaded_df.empty:

            return """

            <h2>Empty Dataset</h2>

            <p>
            The uploaded dataset does not
            contain any customer records.
            </p>

            <a href="/bulk">
                Go Back
            </a>

            """


        # ----------------------------------------------------
        # CREATE COPY
        # ----------------------------------------------------

        data = uploaded_df.copy()


        # ----------------------------------------------------
        # REMOVE TARGET COLUMN IF PRESENT
        # ----------------------------------------------------

        if "Churn" in data.columns:

            data = data.drop(
                "Churn",
                axis=1
            )


        # ----------------------------------------------------
        # CONVERT YES / NO FEATURES
        # ----------------------------------------------------

        if (
            "International plan"
            in data.columns
        ):

            data[
                "International plan"
            ] = (

                data[
                    "International plan"
                ]

                .astype(str)
                .str.strip()
                .map({

                    "Yes": 1,
                    "No": 0

                })

            )


        if (
            "Voice mail plan"
            in data.columns
        ):

            data[
                "Voice mail plan"
            ] = (

                data[
                    "Voice mail plan"
                ]

                .astype(str)
                .str.strip()
                .map({

                    "Yes": 1,
                    "No": 0

                })

            )


        # ----------------------------------------------------
        # STATE ONE-HOT ENCODING
        # ----------------------------------------------------

        state_columns = [

            column

            for column in model_features

            if column.startswith(
                "State_"
            )

        ]


        for column in state_columns:

            state_name = column.replace(
                "State_",
                ""
            )


            if "State" in data.columns:

                data[
                    column
                ] = (

                    data[
                        "State"
                    ]

                    .astype(str)
                    .str.strip()
                    .str.upper()
                    .eq(
                        state_name
                    )
                    .astype(int)

                )

            else:

                data[
                    column
                ] = 0


        # ----------------------------------------------------
        # REMOVE ORIGINAL STATE COLUMN
        # ----------------------------------------------------

        if "State" in data.columns:

            data = data.drop(
                "State",
                axis=1
            )


        # ----------------------------------------------------
        # MATCH MODEL FEATURES
        # ----------------------------------------------------

        data = data.reindex(

            columns=model_features,

            fill_value=0

        )


        # ----------------------------------------------------
        # HANDLE MISSING VALUES
        # ----------------------------------------------------

        data = data.fillna(0)


        # ----------------------------------------------------
        # MAKE BULK PREDICTIONS
        # ----------------------------------------------------

        predictions = model.predict(
            data
        )

        probabilities = model.predict_proba(
            data
        )


        # ----------------------------------------------------
        # ADD PREDICTIONS TO ORIGINAL DATASET
        # ----------------------------------------------------

        result_df = uploaded_df.copy()


        result_df[
            "Prediction"
        ] = [

            "CUSTOMER WILL CHURN"

            if prediction == 1

            else "CUSTOMER WILL STAY"

            for prediction in predictions

        ]


        result_df[
            "Churn Probability (%)"
        ] = (

            probabilities[:, 1] * 100

        ).round(2)


        result_df[
            "Stay Probability (%)"
        ] = (

            probabilities[:, 0] * 100

        ).round(2)


        # ----------------------------------------------------
        # ADD RISK LEVEL
        # ----------------------------------------------------

        result_df[
            "Risk Level"
        ] = (

            result_df[
                "Churn Probability (%)"
            ]

            .apply(

                lambda probability:

                "HIGH"

                if probability >= 70

                else (

                    "MEDIUM"

                    if probability >= 40

                    else "LOW"

                )

            )

        )


        # ----------------------------------------------------
        # CALCULATE STATISTICS
        # ----------------------------------------------------

        total_customers = len(
            result_df
        )


        churned_customers = int(

            (
                predictions == 1
            ).sum()

        )


        staying_customers = int(

            (
                predictions == 0
            ).sum()

        )


        # ----------------------------------------------------
        # CHURN RATE
        # ----------------------------------------------------

        if total_customers > 0:

            churn_rate = round(

                (
                    churned_customers
                    /
                    total_customers
                )
                * 100,

                2

            )

        else:

            churn_rate = 0


        # ----------------------------------------------------
        # STAY RATE
        # ----------------------------------------------------

        if total_customers > 0:

            stay_rate = round(

                (
                    staying_customers
                    /
                    total_customers
                )
                * 100,

                2

            )

        else:

            stay_rate = 0


        # ----------------------------------------------------
        # HIGH RISK CUSTOMERS
        # ----------------------------------------------------

        high_risk_customers = int(

            (

                result_df[
                    "Churn Probability (%)"
                ]

                >= 70

            ).sum()

        )


        # ----------------------------------------------------
        # HIGH RISK RATE
        # ----------------------------------------------------

        if total_customers > 0:

            high_risk_rate = round(

                (
                    high_risk_customers
                    /
                    total_customers
                )
                * 100,

                2

            )

        else:

            high_risk_rate = 0


        # ----------------------------------------------------
        # LOW + MEDIUM RISK CUSTOMERS
        # ----------------------------------------------------

        low_medium_risk = (

            total_customers
            -
            high_risk_customers

        )


        # ----------------------------------------------------
        # LOW + MEDIUM RISK RATE
        # ----------------------------------------------------

        if total_customers > 0:

            low_medium_risk_rate = round(

                (
                    low_medium_risk
                    /
                    total_customers
                )
                * 100,

                2

            )

        else:

            low_medium_risk_rate = 0


        # ====================================================
        # PREPARE TABLE DATA FOR DASHBOARD
        # ====================================================

        table_data = []


        # Show first 20 customers
        # in the dashboard table

        display_df = result_df.head(
            20
        )


        for i, (
            index,
            row
        ) in enumerate(
            display_df.iterrows()
        ):


            churn_probability = float(

                row[
                    "Churn Probability (%)"
                ]

            )


            # Determine risk

            if churn_probability >= 70:

                risk = "HIGH"

            elif churn_probability >= 40:

                risk = "MEDIUM"

            else:

                risk = "LOW"


            # Determine prediction

            if predictions[i] == 1:

                prediction_text = "CHURN"

            else:

                prediction_text = "STAY"


            table_data.append({

                "customer":
                    i + 1,

                "prediction":
                    prediction_text,

                "churn_probability":
                    churn_probability,

                "risk":
                    risk

            })


        # ====================================================
        # SAVE BULK RESULTS
        # ====================================================

        output_path = (
            "data/bulk_prediction_results.csv"
        )


        result_df.to_csv(

            output_path,

            index=False

        )


        # ----------------------------------------------------
        # PRINT RESULTS
        # ----------------------------------------------------

        print(
            "Total customers:",
            total_customers
        )

        print(
            "Predicted churn:",
            churned_customers
        )

        print(
            "Predicted stay:",
            staying_customers
        )

        print(
            "Churn rate:",
            churn_rate,
            "%"
        )

        print(
            "Stay rate:",
            stay_rate,
            "%"
        )

        print(
            "High-risk customers:",
            high_risk_customers
        )

        print(
            "Results saved to:",
            output_path
        )

        print(
            "===================================="
        )


        # ====================================================
        # SEND DATA TO DASHBOARD
        # ====================================================

        return render_template(

            "bulk_result.html",

            total_customers=
                total_customers,

            churn_count=
                churned_customers,

            stay_count=
                staying_customers,

            churn_rate=
                churn_rate,

            stay_rate=
                stay_rate,

            high_risk=
                high_risk_customers,

            high_risk_rate=
                high_risk_rate,

            low_medium_risk=
                low_medium_risk,

            low_medium_risk_rate=
                low_medium_risk_rate,

            results=
                table_data,

            download_available=
                True

        )


    except Exception as e:

        print(
            "Bulk prediction error:",
            e
        )

        return render_template(
            "error.html",
            title="We could not analyze this file",
            message=str(e),
        ), 400


# ============================================================
# DOWNLOAD BULK PREDICTION RESULTS
# ============================================================

@app.route(
    "/download_results"
)
@login_required
def download_results():

    output_path = (
        "data/bulk_prediction_results.csv"
    )


    # --------------------------------------------------------
    # CHECK WHETHER RESULTS EXIST
    # --------------------------------------------------------

    if not os.path.exists(
        output_path
    ):

        return """

        <h2>
            No prediction results available.
        </h2>

        <p>
        Please upload a dataset and
        run prediction first.
        </p>

        <a href="/bulk">
            Go Back
        </a>

        """


    # --------------------------------------------------------
    # SEND FILE TO USER
    # --------------------------------------------------------

    return send_file(

        output_path,

        as_attachment=True,

        download_name=
            "customer_churn_predictions.csv"

    )


# ============================================================
# RUN FLASK APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
