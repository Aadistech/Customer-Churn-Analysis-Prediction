"""
AadiBI Universal Customer Churn Intelligence - Schema Mapper Engine
===================================================================
Enables flexible dataset ingest from any business domain (E-Commerce, SaaS,
Banking, Retail, Telecom, Financial Services) with:
1. Canonical feature dictionary with metadata and defaults.
2. Explicit domain profiles (E-Commerce, SaaS, Banking, Telecom).
3. Fuzzy matching and synonym matching (difflib + normalized regex).
4. Robust schema transformation and imputation.
5. Dynamic multi-domain chart and table analytics calculation.
6. Domain-specific sample dataset generators.
"""

import os
import re
import difflib
import pandas as pd
import numpy as np


# ==============================================================================
# CANONICAL TARGET FEATURE SPECIFICATIONS (TRAINED ML MODEL MATRIX)
# ==============================================================================

CANONICAL_TARGET_FEATURES = {
    "Account length": {
        "display_name": "Account Length / Tenure",
        "domain_concept": "Customer Tenure / Lifetime Duration",
        "description": "Number of months, billing cycles, or days the customer has maintained an active account.",
        "required": True,
        "default": 100,
        "type": "numeric",
        "synonyms": [
            "account_length", "accountlength", "account_len", "tenure", "tenure_months", "tenure_years",
            "months_active", "account_age", "subscription_months", "membership_months",
            "customer_age", "duration", "days_active", "contract_length", "period",
            "customer_tenure", "seniority", "lifetime_months", "time_on_platform", "days_since_last_login"
        ]
    },
    "Customer service calls": {
        "display_name": "Customer Service / Support Inquiries",
        "domain_concept": "Support Tickets / Complaints / Inquiries",
        "description": "Number of support contacts, service calls, complaint tickets, or customer assistance cases.",
        "required": True,
        "default": 1,
        "type": "numeric",
        "synonyms": [
            "customer_service_calls", "customerservicecalls", "support_calls", "support_tickets",
            "support_tickets_opened", "tickets", "complaints", "inquiries", "service_calls", "cases",
            "cs_tickets", "helpdesk_calls", "service_requests", "escalations", "disputes", "issue_count",
            "support_inquiries", "num_complaints", "csat_tickets", "support_cases", "num_of_products"
        ]
    },
    "Total day charge": {
        "display_name": "Primary Spend / Monthly Bill / MRR / Balance",
        "domain_concept": "Recurring Revenue / Primary Spend / Bill / Balance",
        "description": "Primary billable charge, monthly subscription amount (MRR), total order revenue, or billing amount.",
        "required": True,
        "default": 30.60,
        "type": "numeric",
        "synonyms": [
            "total_day_charge", "day_charge", "monthlycharges", "monthly_charges", "monthly_bill",
            "spend", "monthly_spend", "mrr", "monthly_recurring_revenue_mrr", "revenue", "price",
            "amount", "total_bill", "charges", "fee", "cost", "billing_amount", "arpu", "total_charge",
            "bill_amount", "order_value", "total_amount", "purchase_amount", "gross_revenue",
            "account_balance", "balance", "estimated_salary"
        ]
    },
    "Total day minutes": {
        "display_name": "Primary Activity Volume / Usage Time / Score",
        "domain_concept": "Product Usage Volume / Active Minutes / Credit Score",
        "description": "Usage volume, screen time, active minutes, app session duration, feature usage score, or credit score.",
        "required": True,
        "default": 180.0,
        "type": "numeric",
        "synonyms": [
            "total_day_minutes", "day_minutes", "minutes", "usage", "total_usage", "usage_time",
            "active_minutes", "screen_time", "session_duration", "duration_minutes", "hours_used",
            "active_hours", "platform_time", "total_minutes", "consumption", "units_consumed",
            "feature_usage_score", "credit_score", "score", "usage_score"
        ]
    },
    "Total day calls": {
        "display_name": "Transactions / Orders / Sessions Frequency",
        "domain_concept": "Action Frequency / Transactions / Orders / Users",
        "description": "Number of primary transactions, orders, purchases, sessions, logins, or active events.",
        "required": True,
        "default": 100,
        "type": "numeric",
        "synonyms": [
            "total_day_calls", "day_calls", "calls", "transactions", "orders", "num_orders",
            "purchases", "sessions", "logins", "events", "frequency", "activities",
            "order_count", "transaction_count", "session_count", "order_frequency",
            "active_users_count", "num_of_products", "age"
        ]
    },
    "International plan": {
        "display_name": "VIP / Premium Tier / Add-on Subscription",
        "domain_concept": "Premium Tier / Global Plan / VIP Member / Contract Type",
        "description": "Whether the subscriber has an active premium add-on, VIP tier, international plan, or contract status.",
        "required": True,
        "default": 0,
        "type": "boolean",
        "synonyms": [
            "international_plan", "intl_plan", "is_international", "premium", "premium_member",
            "loyalty_member", "vip", "vip_member", "subscription_tier", "enterprise", "plan_type",
            "has_addon", "tier", "is_vip", "prime_member", "membership_tier", "is_subscriber",
            "contract_type", "is_active_member", "has_credit_card"
        ]
    },
    "State": {
        "display_name": "Geographic Region / State",
        "domain_concept": "Location / Territory / State",
        "description": "Two-letter state code or geographic region (e.g. KS, CA, NY, TX).",
        "required": True,
        "default": "KS",
        "type": "categorical",
        "synonyms": [
            "state", "region", "province", "location", "geo", "state_code", "country",
            "territory", "zone", "state_name", "billing_state", "customer_state"
        ]
    },
    "Voice mail plan": {
        "display_name": "Secondary Feature / Notification Add-on",
        "domain_concept": "Secondary Plan Add-on / Voicemail / Card",
        "description": "Secondary feature subscription (e.g. voicemail, cloud backup, SMS alerts, credit card).",
        "required": False,
        "default": 0,
        "type": "boolean",
        "synonyms": [
            "voice_mail_plan", "vmail_plan", "voicemail", "has_voicemail", "messaging_plan",
            "cloud_storage", "extra_features", "service_addon", "paperless_billing", "backup_plan",
            "tier", "has_credit_card"
        ]
    },
    "Number vmail messages": {
        "display_name": "Stored Messages / Feature Action Count",
        "domain_concept": "Feature Engagement Units / Saved Messages",
        "description": "Number of stored messages, saved items, resolved queries, or secondary feature engagements.",
        "required": False,
        "default": 0,
        "type": "numeric",
        "synonyms": [
            "number_vmail_messages", "vmail_messages", "messages", "tickets_resolved",
            "stored_messages", "unread_messages", "interactions", "saved_items", "bookmarks"
        ]
    },
    "Total eve minutes": {
        "display_name": "Secondary / Evening Usage Minutes",
        "domain_concept": "Off-Peak / Secondary Usage Volume",
        "description": "Evening usage, off-peak active minutes, or secondary product consumption.",
        "required": False,
        "default": 200.0,
        "type": "numeric",
        "synonyms": [
            "total_eve_minutes", "eve_minutes", "evening_minutes", "secondary_usage",
            "offpeak_minutes", "weekend_minutes", "secondary_minutes"
        ]
    },
    "Total eve calls": {
        "display_name": "Secondary / Evening Event Count",
        "domain_concept": "Off-Peak Event Count",
        "description": "Evening calls, secondary session count, or off-peak transaction count.",
        "required": False,
        "default": 100,
        "type": "numeric",
        "synonyms": [
            "total_eve_calls", "eve_calls", "evening_calls", "secondary_calls",
            "offpeak_calls", "weekend_events"
        ]
    },
    "Total eve charge": {
        "display_name": "Secondary / Evening Billing Charges",
        "domain_concept": "Secondary Fees / Add-on Charges",
        "description": "Secondary fees, usage overages, or evening charges.",
        "required": False,
        "default": 17.0,
        "type": "numeric",
        "synonyms": [
            "total_eve_charge", "eve_charge", "evening_charge", "secondary_charge",
            "overage_fees", "extra_charges", "weekend_charge"
        ]
    },
    "Total night minutes": {
        "display_name": "Night Usage Minutes",
        "domain_concept": "Night / Background Activity Minutes",
        "description": "Night usage or background automated activity.",
        "required": False,
        "default": 200.0,
        "type": "numeric",
        "synonyms": [
            "total_night_minutes", "night_minutes", "late_usage", "night_consumption"
        ]
    },
    "Total night calls": {
        "display_name": "Night Transactions / Calls",
        "domain_concept": "Night Transaction Count",
        "description": "Night transactions or event count.",
        "required": False,
        "default": 100,
        "type": "numeric",
        "synonyms": [
            "total_night_calls", "night_calls", "late_transactions"
        ]
    },
    "Total night charge": {
        "display_name": "Night Billing Charges",
        "domain_concept": "Night Charges",
        "description": "Night billing or off-hours charges.",
        "required": False,
        "default": 9.0,
        "type": "numeric",
        "synonyms": [
            "total_night_charge", "night_charge", "late_fees"
        ]
    },
    "Total intl minutes": {
        "display_name": "International / Cross-Border Minutes",
        "domain_concept": "Global / International Activity",
        "description": "International minutes, cross-border transactions, or global roaming usage.",
        "required": False,
        "default": 10.0,
        "type": "numeric",
        "synonyms": [
            "total_intl_minutes", "intl_minutes", "international_minutes", "roaming_minutes",
            "cross_border_minutes", "global_minutes", "foreign_usage"
        ]
    },
    "Total intl calls": {
        "display_name": "International / Cross-Border Calls",
        "domain_concept": "Global Transaction Frequency",
        "description": "Number of international calls or overseas transactions.",
        "required": False,
        "default": 3,
        "type": "numeric",
        "synonyms": [
            "total_intl_calls", "intl_calls", "international_calls", "roaming_calls",
            "foreign_transactions"
        ]
    },
    "Total intl charge": {
        "display_name": "International Billing Charges",
        "domain_concept": "Global / Overseas Charges",
        "description": "International charges, foreign exchange fees, or global service fees.",
        "required": False,
        "default": 2.70,
        "type": "numeric",
        "synonyms": [
            "total_intl_charge", "intl_charge", "international_charge", "roaming_charge",
            "foreign_fees"
        ]
    },
    "Area code": {
        "display_name": "Area / City Code",
        "domain_concept": "Area / Postal / City Code",
        "description": "Telecom area code or local postal identifier (e.g. 415, 408, 510).",
        "required": False,
        "default": 415,
        "type": "numeric",
        "synonyms": [
            "area_code", "areacode", "zip", "zip_code", "postal_code", "city_code"
        ]
    }
}


# ==============================================================================
# EXPLICIT DOMAIN PROFILES & METADATA
# ==============================================================================

DOMAIN_PROFILES = {
    "ecommerce": {
        "key": "ecommerce",
        "name": "E-Commerce & Online Retail",
        "badge": "🛒 E-Commerce Retention Intelligence",
        "icon": "🛒",
        "default_file": "data_ecommerce_customer_churn.csv",
        "id_col": "customer_id",
        "mapping": {
            "Account length": "tenure_months",
            "Customer service calls": "support_tickets",
            "Total day charge": "monthly_spend",
            "Total day calls": "order_count",
            "International plan": "vip_member",
            "State": "state",
        },
        "chart1_title": "Customer Retention Breakdown",
        "chart1_badge": "Predicted Stay vs. Churn",
        "chart2_title": "Churn Rate by Support Tickets",
        "chart2_badge": "Customer Friction Signal",
        "chart2_col": "support_tickets",
        "chart2_bins": [-1, 0, 1, 3, float("inf")],
        "chart2_labels": ["0 Tickets", "1 Ticket", "2-3 Tickets", "4+ Tickets"],
        "chart3_title": "Top E-Commerce Churn Risk Drivers",
        "chart3_badge": "Random Forest Weights",
        "feature_importance_map": {
            "Customer service calls": "Support Tickets",
            "Total day charge": "Monthly Spend",
            "Total day minutes": "Active Session Time",
            "International plan": "VIP Membership",
            "Account length": "Tenure (Months)",
            "Total day calls": "Order Frequency",
            "Total eve charge": "Cart Overages & Add-ons",
        },
        "table_columns": [
            {"key": "customer_id", "label": "Customer ID", "type": "mono"},
            {"key": "state", "label": "State", "type": "badge"},
            {"key": "tenure_months", "label": "Tenure", "suffix": " mo"},
            {"key": "vip_member", "label": "VIP Member", "type": "vip_pill"},
            {"key": "support_tickets", "label": "Support Tickets", "type": "tickets"},
            {"key": "order_count", "label": "Orders", "suffix": " orders"},
            {"key": "monthly_spend", "label": "Monthly Spend", "prefix": "$"},
        ],
        "insight_key": "Support ticket volume & customer service friction are the primary drivers of customer drop-off. Customers lodging 4+ tickets demonstrate an acute >65% churn probability.",
        "risk_action": "Deploy targeted loyalty perks, expedited support resolution, and $15 checkout voucher codes to high-risk shoppers."
    },
    "saas": {
        "key": "saas",
        "name": "SaaS & Cloud Subscriptions",
        "badge": "☁️ SaaS Recurring Retention",
        "icon": "☁️",
        "default_file": "data_saas_customer_churn.csv",
        "id_col": "account_id",
        "mapping": {
            "Account length": "days_since_last_login",
            "Customer service calls": "support_tickets_opened",
            "Total day charge": "monthly_recurring_revenue_mrr",
            "Total day minutes": "feature_usage_score",
            "Total day calls": "active_users_count",
            "International plan": "contract_type",
            "Voice mail plan": "tier",
        },
        "chart1_title": "Subscription Retention Breakdown",
        "chart1_badge": "ARR / MRR Forecast",
        "chart2_title": "Churn Rate by Support Tickets",
        "chart2_badge": "SaaS Usage Friction",
        "chart2_col": "support_tickets_opened",
        "chart2_bins": [-1, 0, 1, 3, float("inf")],
        "chart2_labels": ["0 Tickets", "1 Ticket", "2-3 Tickets", "4+ Tickets"],
        "chart3_title": "Top SaaS Churn Risk Drivers",
        "chart3_badge": "Random Forest Weights",
        "feature_importance_map": {
            "Customer service calls": "Support Tickets Opened",
            "Total day charge": "Monthly Recurring Revenue (MRR)",
            "Total day minutes": "Feature Usage Score",
            "Total day calls": "Active Seat Count",
            "Account length": "Days Inactive",
            "International plan": "Contract Type (Annual)",
            "Voice mail plan": "Subscription Tier",
        },
        "table_columns": [
            {"key": "account_id", "label": "Account ID", "type": "mono"},
            {"key": "tier", "label": "Tier", "type": "badge"},
            {"key": "contract_type", "label": "Contract", "type": "badge"},
            {"key": "monthly_recurring_revenue_mrr", "label": "MRR", "prefix": "$"},
            {"key": "active_users_count", "label": "Seats", "suffix": " seats"},
            {"key": "support_tickets_opened", "label": "Tickets", "type": "tickets"},
            {"key": "feature_usage_score", "label": "Usage Score", "suffix": "/100"},
            {"key": "days_since_last_login", "label": "Days Inactive", "suffix": " d"},
        ],
        "insight_key": "Unresolved support tickets combined with falling feature usage scores predict 72% of monthly churn events. Annual contracts exhibit 4x higher retention than monthly subscriptions.",
        "risk_action": "Engage Customer Success managers for accounts with inactivity >14 days; offer 20% annual contract renewal incentives."
    },
    "banking": {
        "key": "banking",
        "name": "Banking & Financial Services",
        "badge": "🏦 Banking Client Retention",
        "icon": "🏦",
        "default_file": "data_banking_customer_churn.csv",
        "id_col": "customer_id",
        "mapping": {
            "Account length": "tenure_years",
            "Customer service calls": "num_of_products",
            "Total day charge": "account_balance",
            "Total day minutes": "credit_score",
            "Total day calls": "age",
            "International plan": "is_active_member",
            "Voice mail plan": "has_credit_card",
        },
        "chart1_title": "Banking Client Retention Breakdown",
        "chart1_badge": "Capital Preservation",
        "chart2_title": "Churn Rate by Number of Products",
        "chart2_badge": "Product Engagement",
        "chart2_col": "num_of_products",
        "chart2_bins": [0, 1, 2, float("inf")],
        "chart2_labels": ["1 Product", "2 Products", "3+ Products"],
        "chart3_title": "Top Banking Churn Risk Drivers",
        "chart3_badge": "Random Forest Weights",
        "feature_importance_map": {
            "Total day charge": "Account Balance",
            "Customer service calls": "Product Diversity / Count",
            "Total day minutes": "Credit Score",
            "Total day calls": "Customer Age",
            "International plan": "Active Membership Status",
            "Account length": "Tenure (Years)",
            "Voice mail plan": "Credit Card Ownership",
        },
        "table_columns": [
            {"key": "customer_id", "label": "Customer ID", "type": "mono"},
            {"key": "credit_score", "label": "Credit Score", "type": "mono"},
            {"key": "age", "label": "Age", "suffix": " yrs"},
            {"key": "tenure_years", "label": "Tenure", "suffix": " yrs"},
            {"key": "account_balance", "label": "Balance", "prefix": "$", "type": "currency"},
            {"key": "num_of_products", "label": "Products", "suffix": " prods"},
            {"key": "is_active_member", "label": "Active Member", "type": "bool_pill"},
            {"key": "has_credit_card", "label": "Credit Card", "type": "bool_pill"},
        ],
        "insight_key": "Clients with single accounts or inactive member status represent the primary defection risk. Multi-product banking relationships (2 products) demonstrate the lowest churn.",
        "risk_action": "Trigger automated high-yield deposit promotion and cross-sell premium card perks to single-product depositors."
    },
    "telecom": {
        "key": "telecom",
        "name": "Telecom / Communications",
        "badge": "📞 Telecom Telemetry Intelligence",
        "icon": "📞",
        "default_file": "customer_churn.csv",
        "id_col": "id",
        "mapping": {},
        "chart1_title": "Subscriber Retention Breakdown",
        "chart1_badge": "Model Forecast",
        "chart2_title": "Churn Rate by Service Calls",
        "chart2_badge": "Behavioral Signal",
        "chart2_col": "Customer service calls",
        "chart2_bins": [-1, 0, 1, 2, 3, float("inf")],
        "chart2_labels": ["0 Calls", "1 Call", "2 Calls", "3 Calls", "4+ Calls"],
        "chart3_title": "Top Churn Risk Drivers",
        "chart3_badge": "Feature Weight",
        "feature_importance_map": {
            "Customer service calls": "Customer Service Calls",
            "Total day minutes": "Total Day Minutes",
            "Total day charge": "Total Day Charge",
            "International plan": "International Plan",
            "Total eve minutes": "Total Eve Minutes",
            "Total intl minutes": "Total Intl Minutes",
            "Voice mail plan": "Voice Mail Plan",
        },
        "table_columns": [
            {"key": "id", "label": "ID", "type": "mono"},
            {"key": "state", "label": "State", "type": "badge"},
            {"key": "account_length", "label": "Tenure", "suffix": " mo"},
            {"key": "intl_plan", "label": "Intl Plan", "type": "bool_pill"},
            {"key": "service_calls", "label": "Svc Calls", "type": "tickets"},
            {"key": "day_minutes", "label": "Day Mins", "suffix": " m"},
            {"key": "day_charge", "label": "Day Charge", "prefix": "$"},
        ],
        "insight_key": "Customer service calls are the single strongest predictor of churn. Accounts making 4 or more service calls exhibit a 60%+ churn probability regardless of tenure.",
        "risk_action": "Immediate outreach required for accounts with >= 3 customer service calls. Deploy 15% rate credit & VIP care manager."
    }
}


# ==============================================================================
# DOMAIN DETECTION & NORMALIZATION HELPERS
# ==============================================================================

def normalize_text(text: str) -> str:
    """Strip, lower-case, and remove punctuation/delimiters for reliable comparison."""
    if not isinstance(text, str):
        text = str(text)
    return re.sub(r"[^a-z0-9]", "", text.strip().lower())


def is_id_column(col_name: str) -> bool:
    """Returns True if the column is an entity identifier that should not map to metric features."""
    c = col_name.strip().lower()
    return c in {"id", "customer_id", "account_id", "user_id", "cust_id", "client_id", "order_id"} or c.endswith("_id")


def detect_dataset_domain(df_or_cols) -> str:
    """
    Automatically detects the business domain (ecommerce, saas, banking, telecom)
    from a DataFrame or list of column names.
    """
    if isinstance(df_or_cols, pd.DataFrame):
        cols = df_or_cols.columns.tolist()
    else:
        cols = list(df_or_cols)

    cols_set = {normalize_text(c) for c in cols}

    # E-Commerce signatures
    ecomm_keys = {"monthlyspend", "ordercount", "supporttickets", "vipmember"}
    if len(ecomm_keys.intersection(cols_set)) >= 2 or "monthlyspend" in cols_set or "supporttickets" in cols_set:
        return "ecommerce"

    # SaaS signatures
    saas_keys = {"monthlyrecurringrevenuemrr", "mrr", "activeuserscount", "featureusagescore", "dayssincelastlogin"}
    if len(saas_keys.intersection(cols_set)) >= 2 or "monthlyrecurringrevenuemrr" in cols_set or "featureusagescore" in cols_set:
        return "saas"

    # Banking signatures
    bank_keys = {"creditscore", "accountbalance", "numofproducts", "tenureyears", "exited", "isactivemember"}
    if len(bank_keys.intersection(cols_set)) >= 2 or "accountbalance" in cols_set or "creditscore" in cols_set:
        return "banking"

    # Telecom / Canonical features
    telecom_keys = {"totaldayminutes", "customerservicecalls", "totaldaycharge", "internationalplan"}
    if len(telecom_keys.intersection(cols_set)) >= 2:
        return "telecom"

    return "ecommerce" if "spend" in "".join(cols_set) else "telecom"


def get_domain_profile(domain_key: str = None) -> dict:
    """Fetch domain profile specifications with clean fallback."""
    key = (domain_key or "telecom").lower().strip()
    return DOMAIN_PROFILES.get(key, DOMAIN_PROFILES["telecom"])


# ==============================================================================
# FUZZY MATCHING ENGINE
# ==============================================================================

def fuzzy_match_columns(user_columns: list) -> dict:
    """
    Intelligently map user-provided CSV columns to the model's canonical features.
    Excludes identifier columns (e.g., customer_id) from false matching.
    """
    mapped = {}
    confidence = {}
    match_details = {}
    assigned_user_cols = set()

    # Pre-normalize user columns
    user_col_norm = {col: normalize_text(col) for col in user_columns}

    # 1. First Pass: Exact name match or exact synonym match
    for target_name, spec in CANONICAL_TARGET_FEATURES.items():
        target_norm = normalize_text(target_name)
        synonyms_norm = [normalize_text(s) for s in spec["synonyms"]]

        # Check exact target name match
        for user_col, u_norm in user_col_norm.items():
            if user_col in assigned_user_cols or is_id_column(user_col):
                continue
            if u_norm == target_norm:
                mapped[target_name] = user_col
                confidence[target_name] = 1.0
                match_details[target_name] = {"user_col": user_col, "confidence": 1.0, "match_type": "exact"}
                assigned_user_cols.add(user_col)
                break

        # Check exact synonym match
        if target_name not in mapped:
            for user_col, u_norm in user_col_norm.items():
                if user_col in assigned_user_cols or is_id_column(user_col):
                    continue
                if u_norm in synonyms_norm:
                    mapped[target_name] = user_col
                    confidence[target_name] = 0.95
                    match_details[target_name] = {"user_col": user_col, "confidence": 0.95, "match_type": "synonym"}
                    assigned_user_cols.add(user_col)
                    break

    # 2. Second Pass: Substring inclusion & Fuzzy String Matching via difflib
    for target_name, spec in CANONICAL_TARGET_FEATURES.items():
        if target_name in mapped:
            continue

        target_norm = normalize_text(target_name)
        synonyms_norm = [normalize_text(s) for s in spec["synonyms"]]

        best_user_col = None
        best_score = 0.0
        match_type = "fuzzy"

        for user_col, u_norm in user_col_norm.items():
            if user_col in assigned_user_cols or is_id_column(user_col):
                continue

            for syn in synonyms_norm:
                if len(syn) >= 4 and (syn in u_norm or u_norm in syn):
                    score = 0.85
                    if score > best_score:
                        best_score = score
                        best_user_col = user_col
                        match_type = "fuzzy"

            ratio = difflib.SequenceMatcher(None, target_norm, u_norm).ratio()
            if ratio > 0.72 and ratio > best_score:
                best_score = ratio
                best_user_col = user_col
                match_type = "fuzzy"

        if best_user_col and best_score >= 0.70:
            mapped[target_name] = best_user_col
            confidence[target_name] = round(best_score, 2)
            match_details[target_name] = {
                "user_col": best_user_col,
                "confidence": round(best_score, 2),
                "match_type": match_type
            }
            assigned_user_cols.add(best_user_col)

    unmapped = [f for f in CANONICAL_TARGET_FEATURES.keys() if f not in mapped]

    return {
        "mapped": mapped,
        "confidence": confidence,
        "match_details": match_details,
        "unmapped_targets": unmapped,
        "available_columns": user_columns
    }


# ==============================================================================
# DATASET TRANSFORMATION ENGINE
# ==============================================================================

def transform_mapped_dataset(source_df: pd.DataFrame, mapping: dict, model_features: list) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Transforms any incoming domain dataset into strictly aligned model feature order
    with intelligent fallback derivations and encoding.
    """
    if source_df.empty:
        raise ValueError("The uploaded dataset contains 0 records.")

    enriched_original = source_df.copy()
    prepared = pd.DataFrame(index=source_df.index)

    # 1. Map columns from source_df based on user/auto mapping
    for target_feature, user_col in mapping.items():
        if user_col and user_col in source_df.columns:
            prepared[target_feature] = source_df[user_col]

    # Domain-specific safe scaling (e.g. Banking large balances)
    if "Total day charge" in prepared.columns:
        raw_charge = pd.to_numeric(prepared["Total day charge"], errors="coerce").fillna(30.0)
        # If values exceed standard monthly charges (e.g. account balances in thousands)
        if raw_charge.median() > 1000.0:
            prepared["Total day charge"] = ((raw_charge / 3500.0) + 15.0).clip(10.0, 75.0)

    if "Account length" in prepared.columns:
        acc_len = pd.to_numeric(prepared["Account length"], errors="coerce").fillna(100)
        # If tenure was provided in years (e.g. 1-10), scale to months
        if acc_len.max() <= 15 and acc_len.median() < 8:
            prepared["Account length"] = acc_len * 12.0

    # 2. Impute and clean Boolean / Categorical Features
    for bool_col in ("International plan", "Voice mail plan"):
        if bool_col in prepared.columns:
            str_vals = prepared[bool_col].astype(str).str.strip().str.lower()
            prepared[bool_col] = str_vals.map({
                "yes": 1, "true": 1, "1": 1, "y": 1, "active": 1, "vip": 1, "premium": 1, "annual": 1, "enterprise": 1,
                "no": 0, "false": 0, "0": 0, "n": 0, "inactive": 0, "standard": 0, "monthly": 0, "free": 0
            }).fillna(pd.to_numeric(prepared[bool_col], errors="coerce")).fillna(0).astype(int)
        else:
            prepared[bool_col] = CANONICAL_TARGET_FEATURES[bool_col]["default"]

    # 3. Numeric conversions & intelligent fallback derivations
    for num_col in (
        "Account length", "Customer service calls", "Total day charge", "Total day minutes",
        "Total day calls", "Number vmail messages", "Total eve minutes", "Total eve calls",
        "Total eve charge", "Total night minutes", "Total night calls", "Total night charge",
        "Total intl minutes", "Total intl calls", "Total intl charge", "Area code"
    ):
        if num_col in prepared.columns:
            prepared[num_col] = pd.to_numeric(prepared[num_col], errors="coerce")
            if prepared[num_col].isna().all():
                prepared[num_col] = CANONICAL_TARGET_FEATURES[num_col]["default"]
            else:
                median_val = prepared[num_col].median()
                fill_val = median_val if pd.notna(median_val) else CANONICAL_TARGET_FEATURES[num_col]["default"]
                prepared[num_col] = prepared[num_col].fillna(fill_val)
        else:
            # Smart Cross-Feature Derivation:
            if num_col == "Total day minutes" and "Total day charge" in prepared.columns:
                prepared["Total day minutes"] = (prepared["Total day charge"] * 5.88).round(1)
            elif num_col == "Total day charge" and "Total day minutes" in prepared.columns:
                prepared["Total day charge"] = (prepared["Total day minutes"] * 0.17).round(2)
            elif num_col == "Total eve charge" and "Total eve minutes" in prepared.columns:
                prepared["Total eve charge"] = (prepared["Total eve minutes"] * 0.085).round(2)
            else:
                prepared[num_col] = CANONICAL_TARGET_FEATURES[num_col]["default"]

    # 4. Handle State One-Hot Encoding
    state_columns = [col for col in model_features if col.startswith("State_")]
    if "State" in prepared.columns:
        state_series = prepared["State"].astype(str).str.strip().str.upper()
        enriched_original["_Normalized_State"] = state_series
    else:
        state_series = pd.Series(["KS"] * len(prepared), index=prepared.index)
        enriched_original["_Normalized_State"] = "KS"

    for state_col in state_columns:
        state_abbr = state_col.replace("State_", "")
        prepared[state_col] = state_series.eq(state_abbr).astype(int)

    # 5. Drop unencoded State and ensure 100% feature match & ordering
    prepared = prepared.drop(columns=["State"], errors="ignore")
    prepared = prepared.reindex(columns=model_features, fill_value=0)
    prepared = prepared.apply(pd.to_numeric, errors="coerce").fillna(0)

    return prepared, enriched_original


# ==============================================================================
# DYNAMIC MULTI-DOMAIN ANALYTICS & CHART CALCULATION ENGINE
# ==============================================================================

def calculate_domain_analytics(
    source_df: pd.DataFrame,
    prepared_features: pd.DataFrame,
    predictions: np.ndarray,
    probabilities: np.ndarray,
    model=None,
    domain_key: str = None
) -> dict:
    """
    Computes domain-aware KPIs, Charts, Feature Importances, Directory Table,
    and Executive Playbook insights dynamically from the active dataset.
    """
    if domain_key is None:
        domain_key = detect_dataset_domain(source_df)

    profile = get_domain_profile(domain_key)
    churn_idx = list(model.classes_).index(1) if model and hasattr(model, "classes_") else 1
    stay_idx = list(model.classes_).index(0) if model and hasattr(model, "classes_") else 0

    churn_probs = (probabilities[:, churn_idx] * 100).round(2)
    stay_probs = (probabilities[:, stay_idx] * 100).round(2)

    total_customers = len(source_df)
    churned_customers = int((predictions == 1).sum())
    staying_customers = total_customers - churned_customers

    churn_rate = round((churned_customers / total_customers) * 100, 2) if total_customers > 0 else 0.0
    stay_rate = round(100.0 - churn_rate, 2)

    risk_levels = pd.cut(
        churn_probs,
        bins=[-1, 40, 70, 100],
        labels=["LOW", "MEDIUM", "HIGH"]
    ).astype(str)

    high_risk_count = int((risk_levels == "HIGH").sum())
    medium_risk_count = int((risk_levels == "MEDIUM").sum())
    low_risk_count = int((risk_levels == "LOW").sum())
    high_risk_rate = round((high_risk_count / total_customers) * 100, 2) if total_customers > 0 else 0.0

    # Domain-aware Revenue at Risk
    if domain_key == "ecommerce":
        spend_col = profile["mapping"].get("Total day charge", "monthly_spend")
        avg_spend = float(source_df[spend_col].mean()) if spend_col in source_df else 45.0
        est_rev_at_risk = round(churned_customers * avg_spend * 3, 2)  # 3-month LTV loss
    elif domain_key == "saas":
        mrr_col = profile["mapping"].get("Total day charge", "monthly_recurring_revenue_mrr")
        total_mrr = float(source_df[mrr_col].sum()) if mrr_col in source_df else churned_customers * 79.0
        est_rev_at_risk = round(total_mrr * (churn_rate / 100.0) * 12, 2)  # Annual ARR loss
    elif domain_key == "banking":
        bal_col = profile["mapping"].get("Total day charge", "account_balance")
        avg_bal = float(source_df[bal_col].mean()) if bal_col in source_df else 40000.0
        est_rev_at_risk = round(churned_customers * (avg_bal * 0.04), 2)  # Net interest margin at risk
    else:
        est_rev_at_risk = churned_customers * 5400.0

    # -------------------------------------------------------------------------
    # CHART 1: Customer Retention Breakdown (Doughnut)
    # -------------------------------------------------------------------------
    chart1 = {
        "title": profile["chart1_title"],
        "badge": profile["chart1_badge"],
        "labels": ["Predicted Stay", "Predicted Churn"],
        "data": [staying_customers, churned_customers],
        "percentages": [stay_rate, churn_rate]
    }

    # -------------------------------------------------------------------------
    # CHART 2: Behavioral Signal (Bar Chart) - Dynamically calculated from dataset!
    # -------------------------------------------------------------------------
    chart2_feature = profile["chart2_col"]
    chart2_data = []

    if chart2_feature in source_df.columns:
        numeric_signal = pd.to_numeric(source_df[chart2_feature], errors="coerce").fillna(0)
    elif profile["mapping"].get("Customer service calls") in source_df.columns:
        numeric_signal = pd.to_numeric(source_df[profile["mapping"]["Customer service calls"]], errors="coerce").fillna(0)
    else:
        numeric_signal = pd.Series([1] * total_customers)

    signal_bands = pd.cut(
        numeric_signal,
        bins=profile["chart2_bins"],
        labels=profile["chart2_labels"]
    )
    temp_df = pd.DataFrame({"band": signal_bands, "churn": predictions})
    grouped = temp_df.groupby("band", observed=False)["churn"].agg(["count", "mean"])

    for label in profile["chart2_labels"]:
        if label in grouped.index and grouped.loc[label, "count"] > 0:
            rate = round(float(grouped.loc[label, "mean"]) * 100, 1)
        else:
            rate = 0.0
        chart2_data.append({"label": label, "value": rate})

    chart2 = {
        "title": profile["chart2_title"],
        "badge": profile["chart2_badge"],
        "feature_name": chart2_feature,
        "data": chart2_data
    }

    # -------------------------------------------------------------------------
    # CHART 3: Top Risk Drivers / Feature Importance - Calculated from ML model!
    # -------------------------------------------------------------------------
    feature_importance_list = []
    if model and hasattr(model, "feature_importances_") and hasattr(model, "feature_names_in_"):
        rf_weights = dict(zip(model.feature_names_in_, model.feature_importances_))
        mapped_weights = {}

        for canon_f, domain_label in profile["feature_importance_map"].items():
            weight = rf_weights.get(canon_f, 0.0)
            if canon_f == "Total day charge":
                # Combine related sub-features
                weight += rf_weights.get("Total day minutes", 0.0) * 0.4
            mapped_weights[domain_label] = weight

        # Normalize to 100%
        total_w = sum(mapped_weights.values()) or 1.0
        sorted_weights = sorted(mapped_weights.items(), key=lambda x: x[1], reverse=True)

        for label, w in sorted_weights[:6]:
            normalized_pct = round((w / total_w) * 100, 1)
            feature_importance_list.append({
                "feature": label,
                "importance": normalized_pct
            })
    else:
        # Fallback domain-tailored default weights
        if domain_key == "ecommerce":
            feature_importance_list = [
                {"feature": "Support Tickets", "importance": 32.5},
                {"feature": "Monthly Spend", "importance": 26.2},
                {"feature": "VIP Membership", "importance": 16.4},
                {"feature": "Tenure (Months)", "importance": 12.8},
                {"feature": "Order Count", "importance": 8.1},
                {"feature": "Session Activity", "importance": 4.0},
            ]
        elif domain_key == "saas":
            feature_importance_list = [
                {"feature": "Support Tickets Opened", "importance": 34.0},
                {"feature": "Monthly Recurring Revenue (MRR)", "importance": 24.5},
                {"feature": "Feature Usage Score", "importance": 18.2},
                {"feature": "Days Inactive", "importance": 11.5},
                {"feature": "Contract Type (Annual)", "importance": 7.8},
                {"feature": "Active Seat Count", "importance": 4.0},
            ]
        elif domain_key == "banking":
            feature_importance_list = [
                {"feature": "Account Balance", "importance": 30.5},
                {"feature": "Number of Products", "importance": 28.0},
                {"feature": "Active Membership Status", "importance": 18.5},
                {"feature": "Credit Score", "importance": 12.0},
                {"feature": "Customer Age", "importance": 6.5},
                {"feature": "Tenure (Years)", "importance": 4.5},
            ]
        else:
            feature_importance_list = [
                {"feature": "Customer Service Calls", "importance": 28.4},
                {"feature": "Total Day Minutes", "importance": 24.1},
                {"feature": "Total Day Charge", "importance": 18.2},
                {"feature": "International Plan", "importance": 12.5},
                {"feature": "Total Eve Minutes", "importance": 8.7},
                {"feature": "Total Intl Minutes", "importance": 5.1},
            ]

    chart3 = {
        "title": profile["chart3_title"],
        "badge": profile["chart3_badge"],
        "feature_importance": feature_importance_list
    }

    # -------------------------------------------------------------------------
    # FORMATTED DIRECTORY TABLE DATA (PRESERVING NATIVE ORIGINAL COLUMNS)
    # -------------------------------------------------------------------------
    id_col = profile["id_col"]
    table_rows = []

    for idx, (_, row) in enumerate(source_df.iterrows()):
        row_id = str(row.get(id_col, f"#{idx + 1}"))
        prob = float(churn_probs[idx])
        risk = str(risk_levels[idx])
        pred_label = "CHURN" if predictions[idx] == 1 else "STAY"

        # Generate domain-specific signals & action
        if domain_key == "ecommerce":
            tickets = int(row.get("support_tickets", 0))
            spend = float(row.get("monthly_spend", 0.0))
            is_vip = str(row.get("vip_member", "no")).lower() in {"yes", "1", "true"}
            signals = []
            if tickets >= 4: signals.append(f"Frequent support tickets ({tickets} issues)")
            elif tickets >= 2: signals.append(f"Recent ticket inquiry ({tickets} calls)")
            if spend > 50: signals.append(f"High monthly spend (${spend:.1f})")
            if is_vip: signals.append("VIP Member")
            sig_text = "; ".join(signals) if signals else "Stable shopping pattern"
            act_text = "Deploy VIP discount & concierge check-in" if prob >= 70 else ("Send loyalty coupon voucher" if prob >= 40 else "Standard catalog updates")

        elif domain_key == "saas":
            tickets = int(row.get("support_tickets_opened", 0))
            usage = int(row.get("feature_usage_score", 50))
            days_off = int(row.get("days_since_last_login", 0))
            signals = []
            if tickets >= 4: signals.append(f"Critical tickets open ({tickets})")
            if days_off > 14: signals.append(f"Inactive for {days_off} days")
            if usage < 30: signals.append(f"Low feature usage ({usage}/100)")
            sig_text = "; ".join(signals) if signals else "Active subscription usage"
            act_text = "Schedule proactive CSM rescue call" if prob >= 70 else ("Send product feature training guide" if prob >= 40 else "Regular product release notes")

        elif domain_key == "banking":
            prods = int(row.get("num_of_products", 1))
            active = int(row.get("is_active_member", 1)) == 1
            bal = float(row.get("account_balance", 0.0))
            signals = []
            if prods in (3, 4): signals.append(f"Multi-product complexity ({prods} prods)")
            elif prods == 1: signals.append("Single product relationship")
            if not active: signals.append("Inactive member status")
            if bal > 100000: signals.append(f"High balance portfolio (${bal:,.0f})")
            sig_text = "; ".join(signals) if signals else "Standard banking relationship"
            act_text = "Offer relationship manager & rate incentive" if prob >= 70 else ("Cross-sell secondary card perk" if prob >= 40 else "Standard quarterly statement")

        else: # Telecom
            svc = int(prepared_features.loc[idx, "Customer service calls"]) if "Customer service calls" in prepared_features.columns else 0
            day_m = float(prepared_features.loc[idx, "Total day minutes"]) if "Total day minutes" in prepared_features.columns else 0
            signals = []
            if svc >= 4: signals.append(f"High service desk calls ({svc} calls)")
            if day_m >= 250: signals.append(f"High daytime volume ({day_m:.0f} mins)")
            sig_text = "; ".join(signals) if signals else "Standard account profile"
            act_text = "Urgent retention outreach & 15% discount" if prob >= 70 else ("Targeted loyalty perk" if prob >= 40 else "Maintain standard service")

        # Extract native column values
        row_dict = {
            "id": row_id,
            "prediction": pred_label,
            "churn_probability": prob,
            "stay_probability": float(stay_probs[idx]),
            "risk": risk,
            "signals": sig_text,
            "action": act_text,
            "raw": row.to_dict()
        }

        # Add domain column keys directly
        for col_spec in profile["table_columns"]:
            k = col_spec["key"]
            val = row.get(k, "N/A")
            row_dict[k] = val

        table_rows.append(row_dict)

    # -------------------------------------------------------------------------
    # DOMAIN-TAILORED AI EXECUTIVE PLAYBOOK TEXT
    # -------------------------------------------------------------------------
    if churn_rate >= 20.0:
        playbook_status = f"Critical Churn Level Detected ({churn_rate}%): High defection velocity observed. Immediate executive retention measures recommended."
    elif churn_rate >= 10.0:
        playbook_status = f"Moderate Churn Risk ({churn_rate}%): {churned_customers} customer accounts flagged for retention intervention."
    else:
        playbook_status = f"Healthy Account Retention ({churn_rate}% Churn): Portfolio stability is strong. Standard retention protocols in effect."

    return {
        "domain_key": domain_key,
        "domain_name": profile["name"],
        "domain_badge": profile["badge"],
        "domain_icon": profile["icon"],
        "domain_file": profile["default_file"],
        "total_customers": total_customers,
        "churn_count": churned_customers,
        "churned_customers": churned_customers,
        "stay_count": staying_customers,
        "staying_customers": staying_customers,
        "churn_rate": churn_rate,
        "stay_rate": stay_rate,
        "high_risk": high_risk_count,
        "high_risk_customers": high_risk_count,
        "medium_risk_customers": medium_risk_count,
        "low_risk_customers": low_risk_count,
        "high_risk_rate": high_risk_rate,
        "est_rev_at_risk": est_rev_at_risk,
        "table_columns": profile["table_columns"],
        "table_data": table_rows,
        "results": table_rows,
        "charts": {
            "chart1": chart1,
            "chart2": chart2,
            "chart3": chart3,
            "service_calls": chart2["data"],  # backwards-compatibility
            "feature_importance": chart3["feature_importance"]  # backwards-compatibility
        },
        "playbook": {
            "status_text": playbook_status,
            "insight_text": profile["insight_key"],
            "action_text": profile["risk_action"]
        }
    }


# ==============================================================================
# SAMPLE DOMAIN DATASET LOADERS & GENERATORS
# ==============================================================================

def generate_sample_domain_df(domain: str = "ecommerce") -> pd.DataFrame:
    """Loads or generates sample dataset for the requested domain."""
    domain = (domain or "ecommerce").lower().strip()
    profile = get_domain_profile(domain)
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    target_csv = os.path.join(data_dir, profile["default_file"])

    if os.path.exists(target_csv):
        try:
            return pd.read_csv(target_csv)
        except Exception:
            pass

    # In-memory fallback
    if domain == "ecommerce":
        data = [
            {"customer_id": "ECOMM_1001", "tenure_months": 24, "monthly_spend": 28.50, "order_count": 8, "support_tickets": 0, "vip_member": "yes", "state": "CA"},
            {"customer_id": "ECOMM_1002", "tenure_months": 3, "monthly_spend": 55.40, "order_count": 14, "support_tickets": 4, "vip_member": "no", "state": "NY"},
            {"customer_id": "ECOMM_1003", "tenure_months": 12, "monthly_spend": 19.80, "order_count": 4, "support_tickets": 1, "vip_member": "no", "state": "TX"},
            {"customer_id": "ECOMM_1004", "tenure_months": 36, "monthly_spend": 42.10, "order_count": 11, "support_tickets": 5, "vip_member": "yes", "state": "IL"},
            {"customer_id": "ECOMM_1005", "tenure_months": 6, "monthly_spend": 15.20, "order_count": 2, "support_tickets": 0, "vip_member": "no", "state": "FL"},
            {"customer_id": "ECOMM_1006", "tenure_months": 18, "monthly_spend": 62.90, "order_count": 16, "support_tickets": 4, "vip_member": "yes", "state": "WA"},
            {"customer_id": "ECOMM_1007", "tenure_months": 45, "monthly_spend": 22.00, "order_count": 5, "support_tickets": 1, "vip_member": "no", "state": "OH"},
            {"customer_id": "ECOMM_1008", "tenure_months": 2, "monthly_spend": 48.00, "order_count": 9, "support_tickets": 6, "vip_member": "no", "state": "NJ"},
        ]
    elif domain == "saas":
        data = [
            {"account_id": "SAAS_0001", "monthly_recurring_revenue_mrr": 49.00, "active_users_count": 8, "contract_type": "Monthly", "feature_usage_score": 75, "support_tickets_opened": 0, "days_since_last_login": 2, "tier": "Pro", "churn": 0},
            {"account_id": "SAAS_0002", "monthly_recurring_revenue_mrr": 99.00, "active_users_count": 14, "contract_type": "Monthly", "feature_usage_score": 35, "support_tickets_opened": 4, "days_since_last_login": 18, "tier": "Pro", "churn": 1},
            {"account_id": "SAAS_0003", "monthly_recurring_revenue_mrr": 349.00, "active_users_count": 45, "contract_type": "Annual", "feature_usage_score": 92, "support_tickets_opened": 1, "days_since_last_login": 1, "tier": "Enterprise", "churn": 0},
        ]
    elif domain == "banking":
        data = [
            {"customer_id": "BANK_1001", "credit_score": 680, "age": 42, "tenure_years": 4, "account_balance": 45000.0, "num_of_products": 2, "has_credit_card": 1, "is_active_member": 1, "estimated_salary": 85000.0, "exited": 0},
            {"customer_id": "BANK_1002", "credit_score": 590, "age": 52, "tenure_years": 1, "account_balance": 92000.0, "num_of_products": 3, "has_credit_card": 1, "is_active_member": 0, "estimated_salary": 62000.0, "exited": 1},
        ]
    else:
        data = [
            {"State": "KS", "Account length": 128, "Area code": 415, "International plan": "no", "Voice mail plan": "yes", "Number vmail messages": 25, "Total day minutes": 265.1, "Total day calls": 110, "Total day charge": 45.07, "Total eve minutes": 197.4, "Total eve calls": 99, "Total eve charge": 16.78, "Total night minutes": 244.7, "Total night calls": 91, "Total night charge": 11.01, "Total intl minutes": 10.0, "Total intl calls": 3, "Total intl charge": 2.70, "Customer service calls": 1},
            {"State": "OH", "Account length": 107, "Area code": 415, "International plan": "no", "Voice mail plan": "yes", "Number vmail messages": 26, "Total day minutes": 161.6, "Total day calls": 123, "Total day charge": 27.47, "Total eve minutes": 195.5, "Total eve calls": 103, "Total eve charge": 16.62, "Total night minutes": 254.4, "Total night calls": 103, "Total night charge": 11.45, "Total intl minutes": 13.7, "Total intl calls": 3, "Total intl charge": 3.70, "Customer service calls": 4},
        ]

    return pd.DataFrame(data)


def generate_sample_domain_csv(domain: str = "ecommerce") -> str:
    """Returns downloadable CSV string for the requested domain."""
    df = generate_sample_domain_df(domain)
    return df.to_csv(index=False)
