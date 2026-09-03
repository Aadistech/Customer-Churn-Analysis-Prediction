from flask import Flask, render_template, request
import pandas as pd
import joblib

# ============================================================
# MODULE 8: FLASK BACKEND
# ============================================================

app = Flask(__name__)

print("\n===== FLASK APPLICATION STARTED =====")

# Load trained Random Forest model
model = joblib.load("models/random_forest_model.pkl")

# Load cleaned dataset to get the exact feature structure
df = pd.read_csv("data/cleaned_customer_churn.csv")

X = df.drop("Churn", axis=1)

# Store the exact feature order used by the model
model_features = X.columns.tolist()

print("Random Forest model loaded successfully.")
print("Number of model features:", len(model_features))


# ============================================================
# HOME ROUTE
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# PREDICTION ROUTE
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():

    # Get customer information from the HTML form

    state = request.form["state"].strip().upper()

    account_length = int(request.form["account_length"])
    area_code = int(request.form["area_code"])

    international_plan = request.form["international_plan"]
    voice_mail_plan = request.form["voice_mail_plan"]

    number_vmail_messages = int(
        request.form["number_vmail_messages"]
    )

    total_day_minutes = float(
        request.form["total_day_minutes"]
    )

    total_day_calls = int(
        request.form["total_day_calls"]
    )

    total_day_charge = float(
        request.form["total_day_charge"]
    )

    total_eve_minutes = float(
        request.form["total_eve_minutes"]
    )

    total_eve_calls = int(
        request.form["total_eve_calls"]
    )

    total_eve_charge = float(
        request.form["total_eve_charge"]
    )

    total_night_minutes = float(
        request.form["total_night_minutes"]
    )

    total_night_calls = int(
        request.form["total_night_calls"]
    )

    total_night_charge = float(
        request.form["total_night_charge"]
    )

    total_intl_minutes = float(
        request.form["total_intl_minutes"]
    )

    total_intl_calls = int(
        request.form["total_intl_calls"]
    )

    total_intl_charge = float(
        request.form["total_intl_charge"]
    )

    customer_service_calls = int(
        request.form["customer_service_calls"]
    )


    # ========================================================
    # CREATE CUSTOMER DATA
    # ========================================================

    new_customer = pd.DataFrame({
        "Account length": [account_length],
        "Area code": [area_code],

        "International plan": [
            1 if international_plan == "Yes" else 0
        ],

        "Voice mail plan": [
            1 if voice_mail_plan == "Yes" else 0
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


    # ========================================================
    # STATE ONE-HOT ENCODING
    # ========================================================

    state_column = "State_" + state

    new_customer[state_column] = 1

    state_columns = [
        column
        for column in model_features
        if column.startswith("State_")
    ]

    for column in state_columns:

        if column not in new_customer.columns:
            new_customer[column] = 0


    # Match exact model feature order
    new_customer = new_customer.reindex(
        columns=model_features,
        fill_value=0
    )


    # ========================================================
    # MAKE PREDICTION
    # ========================================================

    prediction = model.predict(new_customer)

    probability = model.predict_proba(new_customer)

    stay_probability = round(
        probability[0][0] * 100,
        2
    )

    churn_probability = round(
        probability[0][1] * 100,2
    )


    if prediction[0] == 1:

        result = "CUSTOMER WILL CHURN"

    else:

        result = "CUSTOMER WILL STAY"


    # ========================================================
    # SEND RESULT TO FRONTEND
    # ========================================================

    return render_template(
        "result.html",
        prediction=result,
        stay_probability=stay_probability,
        churn_probability=churn_probability
    )


# ============================================================
# RUN FLASK APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )