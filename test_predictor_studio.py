"""
End-to-end verification script for Individual Risk Scoring Studio across:
- E-Commerce
- SaaS / Cloud
- Banking / Financial Services
- Telecom
"""

import sys
from app import app

client = app.test_client()

# Simulate logged in user
with client.session_transaction() as sess:
    sess["username"] = "admin"
    sess["role"] = "admin"

print("--- TESTING INDIVIDUAL RISK SCORING STUDIO ---")

# 1. GET /predict (HTML page load)
res_get = client.get("/predict?domain=ecommerce")
assert res_get.status_code == 200, f"Expected 200, got {res_get.status_code}"
assert b"Risk Scoring Studio" in res_get.data
assert b"domainTabsContainer" in res_get.data
assert b"domainSectionEcommerce" in res_get.data
assert b"domainSectionSaas" in res_get.data
assert b"domainSectionBanking" in res_get.data
assert b"domainSectionTelecom" in res_get.data
print("[OK] GET /predict loads page with all 4 domain sections successfully.")

# 2. POST /api/predict (E-Commerce)
ecom_payload = {
    "domain": "ecommerce",
    "state": "NY",
    "tenure_months": 2,
    "vip_member": "no",
    "monthly_spend": 1250.0,
    "order_count": 1,
    "support_tickets": 5
}
res_ecom = client.post("/api/predict", json=ecom_payload)
assert res_ecom.status_code == 200, f"E-Commerce predict failed: {res_ecom.data}"
data_ecom = res_ecom.get_json()
assert data_ecom["success"] is True
assert data_ecom["domain"] == "ecommerce"
assert "churn_probability" in data_ecom
assert len(data_ecom["drivers"]) > 0
assert "voucher_code" in data_ecom
print(f"[OK] E-Commerce Scoring: Prob={data_ecom['churn_probability']}%, Risk={data_ecom['risk_level']}, Voucher={data_ecom['voucher_code']}")

# 3. POST /api/predict (SaaS)
saas_payload = {
    "domain": "saas",
    "tier": "Free",
    "contract_type": "Monthly",
    "days_since_last_login": 35,
    "monthly_recurring_revenue_mrr": 0.0,
    "active_users_count": 1,
    "feature_usage_score": 18,
    "support_tickets_opened": 4
}
res_saas = client.post("/api/predict", json=saas_payload)
assert res_saas.status_code == 200, f"SaaS predict failed: {res_saas.data}"
data_saas = res_saas.get_json()
assert data_saas["success"] is True
assert data_saas["domain"] == "saas"
assert "churn_probability" in data_saas
assert len(data_saas["drivers"]) > 0
assert "voucher_code" in data_saas
print(f"[OK] SaaS Scoring: Prob={data_saas['churn_probability']}%, Risk={data_saas['risk_level']}, Voucher={data_saas['voucher_code']}")

# 4. POST /api/predict (Banking)
bank_payload = {
    "domain": "banking",
    "credit_score": 520,
    "age": 55,
    "tenure_years": 1,
    "account_balance": 145000.0,
    "num_of_products": 3,
    "has_credit_card": 0,
    "is_active_member": 0,
    "estimated_salary": 45000.0
}
res_bank = client.post("/api/predict", json=bank_payload)
assert res_bank.status_code == 200, f"Banking predict failed: {res_bank.data}"
data_bank = res_bank.get_json()
assert data_bank["success"] is True
assert data_bank["domain"] == "banking"
assert "churn_probability" in data_bank
assert len(data_bank["drivers"]) > 0
assert "voucher_code" in data_bank
print(f"[OK] Banking Scoring: Prob={data_bank['churn_probability']}%, Risk={data_bank['risk_level']}, Voucher={data_bank['voucher_code']}")

# 5. POST /api/predict (Telecom)
telecom_payload = {
    "domain": "telecom",
    "state": "NJ",
    "account_length": 137,
    "area_code": 415,
    "international_plan": "yes",
    "voice_mail_plan": "no",
    "number_vmail_messages": 0,
    "total_day_minutes": 268.0,
    "total_day_calls": 112,
    "total_day_charge": 45.56,
    "total_eve_minutes": 240.0,
    "total_eve_calls": 105,
    "total_eve_charge": 20.40,
    "total_night_minutes": 220.0,
    "total_night_calls": 95,
    "total_night_charge": 9.90,
    "total_intl_minutes": 13.5,
    "total_intl_calls": 4,
    "total_intl_charge": 3.65,
    "customer_service_calls": 5
}
res_telecom = client.post("/api/predict", json=telecom_payload)
assert res_telecom.status_code == 200, f"Telecom predict failed: {res_telecom.data}"
data_telecom = res_telecom.get_json()
assert data_telecom["success"] is True
assert data_telecom["domain"] == "telecom"
assert "churn_probability" in data_telecom
assert len(data_telecom["drivers"]) > 0
assert "voucher_code" in data_telecom
print(f"[OK] Telecom Scoring: Prob={data_telecom['churn_probability']}%, Risk={data_telecom['risk_level']}, Voucher={data_telecom['voucher_code']}")

# 6. POST /predict (Form POST for E-Commerce)
res_form = client.post("/predict", data=ecom_payload)
assert res_form.status_code == 200
assert b"liveResultCard" in res_form.data
print("[OK] Form POST /predict succeeded with rendered template.")

print("\n--- ALL INDIVIDUAL RISK SCORING TESTS PASSED PERFECTLY! ---")
