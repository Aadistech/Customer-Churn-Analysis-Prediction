import pandas as pd
import joblib

# ============================================================
# MODULE 7: CUSTOMER CHURN PREDICTION
# STEP 2: NEW CUSTOMER PREDICTION
# ============================================================

print("\n===== MODULE 7 STARTED =====")

# 1. LOAD TRAINED MODEL

model = joblib.load("models/random_forest_model.pkl")

print("\n===== MODEL LOADED =====")
print("Random Forest model loaded successfully.")

# 2. LOAD CLEANED DATASET

df = pd.read_csv("data/cleaned_customer_churn.csv")

# Get feature columns used by the model
X = df.drop("Churn", axis=1)

model_features = X.columns.tolist()

print("\n===== MODEL FEATURE STRUCTURE =====")
print("Number of Features:", len(model_features))

# ============================================================
# 3. NEW CUSTOMER INPUT
# ============================================================

print("\n===== ENTER NEW CUSTOMER DETAILS =====")

state = input("State: ").strip().upper()

account_length = int(input("Account Length: "))

area_code = int(input("Area Code: "))

international_plan = input(
    "International Plan (Yes/No): "
).strip().lower()

voice_mail_plan = input(
    "Voice Mail Plan (Yes/No): "
).strip().lower()

number_vmail_messages = int(
    input("Number of Voice Mail Messages: ")
)

total_day_minutes = float(
    input("Total Day Minutes: ")
)

total_day_calls = int(
    input("Total Day Calls: ")
)

total_day_charge = float(
    input("Total Day Charge: ")
)

total_eve_minutes = float(
    input("Total Evening Minutes: ")
)

total_eve_calls = int(
    input("Total Evening Calls: ")
)

total_eve_charge = float(
    input("Total Evening Charge: ")
)

total_night_minutes = float(
    input("Total Night Minutes: ")
)

total_night_calls = int(
    input("Total Night Calls: ")
)

total_night_charge = float(
    input("Total Night Charge: ")
)

total_intl_minutes = float(
    input("Total International Minutes: ")
)

total_intl_calls = int(
    input("Total International Calls: ")
)

total_intl_charge = float(
    input("Total International Charge: ")
)

customer_service_calls = int(
    input("Customer Service Calls: ")
)

# ============================================================
# 4. CREATE NEW CUSTOMER DATAFRAME
# ============================================================

new_customer = pd.DataFrame({
    "Account length": [account_length],
    "Area code": [area_code],

    "International plan": [
        1 if international_plan == "yes" else 0
    ],

    "Voice mail plan": [
        1 if voice_mail_plan == "yes" else 0
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

# ============================================================
# 5. CREATE STATE ONE-HOT ENCODING
# ============================================================

state_column = "State_" + state

new_customer[state_column] = 1

# Add all missing State columns
state_columns = [
    column for column in model_features
    if column.startswith("State_")
]

for column in state_columns:

    if column not in new_customer.columns:
        new_customer[column] = 0

# ============================================================
# 6. MATCH MODEL FEATURE ORDER
# ============================================================

new_customer = new_customer.reindex(
    columns=model_features,
    fill_value=0
)

print("\n===== NEW CUSTOMER DATA PREPARED =====")
print("Features prepared:", new_customer.shape[1])

# ============================================================
# 7. MAKE PREDICTION
# ============================================================

prediction = model.predict(new_customer)

probability = model.predict_proba(new_customer)

# ============================================================
# 8. DISPLAY RESULT
# ============================================================

print("\n===== PREDICTION RESULT =====")

if prediction[0] == 1:
    print("Prediction: CUSTOMER WILL CHURN")
else:
    print("Prediction: CUSTOMER WILL STAY")

print("\n===== CHURN PROBABILITY =====")

print(
    "Stay probability :",
    round(probability[0][0] * 100, 2),
    "%"
)

print(
    "Churn probability:",
    round(probability[0][1] * 100, 2),
    "%"
)

print("\n===== MODULE 7 STEP 2 COMPLETED =====")