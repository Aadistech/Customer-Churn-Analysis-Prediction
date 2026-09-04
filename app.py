from flask import Flask, render_template, request, send_file
import pandas as pd
import joblib
import os

# ============================================================
# MODULE 8 + MODULE 9: FLASK BACKEND
# CUSTOMER CHURN ANALYSIS & PREDICTION SYSTEM
# ============================================================

app = Flask(__name__)

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
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# BULK UPLOAD PAGE
# ============================================================

@app.route("/bulk")
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


        # ----------------------------------------------------
        # SEND RESULT TO FRONTEND
        # ----------------------------------------------------

        return render_template(

            "result.html",

            prediction=result,

            stay_probability=
                stay_probability,

            churn_probability=
                churn_probability

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

        return f"""

        <h2>Bulk Prediction Error</h2>

        <p>{e}</p>

        <a href="/bulk">
            Go Back
        </a>

        """


# ============================================================
# DOWNLOAD BULK PREDICTION RESULTS
# ============================================================

@app.route(
    "/download_results"
)
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