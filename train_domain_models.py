"""
Train and export production Scikit-learn pipelines for all 4 business domains:
1. E-Commerce (model_ecommerce.pkl)
2. SaaS / Cloud (model_saas.pkl)
3. Banking / Financial Services (model_banking.pkl)
4. Telecom (model_telecom.pkl)
"""

import os
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(MODELS_DIR, exist_ok=True)

print("--- TRAINING MULTI-DOMAIN MODELS ---")

# 1. E-Commerce Model
ecom_path = os.path.join(DATA_DIR, "data_ecommerce_customer_churn.csv")
if os.path.exists(ecom_path):
    df_ecom = pd.read_csv(ecom_path)
    # Ensure vip_member is lower string
    df_ecom["vip_member"] = df_ecom["vip_member"].astype(str).str.lower().str.strip()
    
    cat_cols = ["state", "vip_member"]
    num_cols = ["tenure_months", "monthly_spend", "order_count", "support_tickets"]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
            ("num", StandardScaler(), num_cols)
        ]
    )
    
    pipeline_ecom = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42))
    ])
    
    X_ecom = df_ecom[cat_cols + num_cols]
    y_ecom = df_ecom["churn"]
    pipeline_ecom.fit(X_ecom, y_ecom)
    joblib.dump(pipeline_ecom, os.path.join(MODELS_DIR, "model_ecommerce.pkl"))
    print("[OK] E-Commerce Model Pipeline trained & saved successfully.")

# 2. SaaS Model
saas_path = os.path.join(DATA_DIR, "data_saas_customer_churn.csv")
if os.path.exists(saas_path):
    df_saas = pd.read_csv(saas_path)
    df_saas["tier"] = df_saas["tier"].astype(str).str.strip()
    df_saas["contract_type"] = df_saas["contract_type"].astype(str).str.strip()
    
    cat_cols_saas = ["tier", "contract_type"]
    num_cols_saas = [
        "days_since_last_login",
        "monthly_recurring_revenue_mrr",
        "active_users_count",
        "feature_usage_score",
        "support_tickets_opened"
    ]
    
    preprocessor_saas = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols_saas),
            ("num", StandardScaler(), num_cols_saas)
        ]
    )
    
    pipeline_saas = Pipeline([
        ("preprocessor", preprocessor_saas),
        ("classifier", RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42))
    ])
    
    X_saas = df_saas[cat_cols_saas + num_cols_saas]
    y_saas = df_saas["churn"]
    pipeline_saas.fit(X_saas, y_saas)
    joblib.dump(pipeline_saas, os.path.join(MODELS_DIR, "model_saas.pkl"))
    print("[OK] SaaS Model Pipeline trained & saved successfully.")

# 3. Banking Model
banking_path = os.path.join(DATA_DIR, "data_banking_customer_churn.csv")
if os.path.exists(banking_path):
    df_banking = pd.read_csv(banking_path)
    
    num_cols_bank = [
        "credit_score",
        "age",
        "tenure_years",
        "account_balance",
        "num_of_products",
        "has_credit_card",
        "is_active_member",
        "estimated_salary"
    ]
    
    preprocessor_bank = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols_bank)
        ]
    )
    
    pipeline_bank = Pipeline([
        ("preprocessor", preprocessor_bank),
        ("classifier", RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42))
    ])
    
    X_bank = df_banking[num_cols_bank]
    y_bank = df_banking["exited"]
    pipeline_bank.fit(X_bank, y_bank)
    joblib.dump(pipeline_bank, os.path.join(MODELS_DIR, "model_banking.pkl"))
    print("[OK] Banking Model Pipeline trained & saved successfully.")

# 4. Telecom Model
# Duplicate or load existing random_forest_model.pkl
rf_path = os.path.join(MODELS_DIR, "random_forest_model.pkl")
telecom_dest = os.path.join(MODELS_DIR, "model_telecom.pkl")
if os.path.exists(rf_path):
    m_rf = joblib.load(rf_path)
    joblib.dump(m_rf, telecom_dest)
    print("[OK] Telecom Model saved to model_telecom.pkl.")

print("All domain models successfully trained and stored in models/")
