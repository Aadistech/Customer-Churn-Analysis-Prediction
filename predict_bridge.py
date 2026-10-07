import sys
import json
import os
import pandas as pd
import joblib

# ============================================================
# PYTHON - NODE.JS ML INFERENCE BRIDGE SCRIPT
# ============================================================

MODEL_PATH = os.path.join("models", "random_forest_model.pkl")
CLEANED_DATA_PATH = os.path.join("data", "cleaned_customer_churn.csv")

try:
    model = joblib.load(MODEL_PATH)
    df_cleaned = pd.read_csv(CLEANED_DATA_PATH)
    X = df_cleaned.drop("Churn", axis=1, errors="ignore")
    model_features = X.columns.tolist()
except Exception as e:
    sys.stderr.write(f"Error loading model: {e}\n")
    sys.exit(1)


def customer_guidance(customer, churn_probability):
    """Generate transparent risk signals and retention action."""
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


def predict_single(payload):
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

    return {
        "success": True,
        "prediction": "CUSTOMER WILL CHURN" if prediction == 1 else "CUSTOMER WILL STAY",
        "is_churn": bool(prediction == 1),
        "churn_probability": churn_prob,
        "stay_probability": stay_prob,
        "risk_level": "HIGH" if churn_prob >= 70 else ("MEDIUM" if churn_prob >= 40 else "LOW"),
        "drivers": drivers,
        "recommendation": recommendation,
    }


def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            sys.exit(0)

        payload = json.loads(input_data)
        result = predict_single(payload)
        sys.stdout.write(json.dumps(result))
    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
