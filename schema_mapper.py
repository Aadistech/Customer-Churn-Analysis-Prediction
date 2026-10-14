"""
AadiBI Universal Customer Churn Intelligence - Schema Mapper Engine
===================================================================
Enables flexible dataset ingest from any business domain (E-Commerce, SaaS,
Banking, Retail, Telecom, Financial Services) with:
1. Canonical feature dictionary with metadata and defaults.
2. Fuzzy matching and synonym matching (difflib + normalized regex).
3. Robust schema transformation and imputation.
4. Domain-specific sample dataset generators.
"""

import re
import difflib
import pandas as pd
import numpy as np


# ==============================================================================
# CANONICAL TARGET FEATURE SPECIFICATIONS
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
            "account_length", "accountlength", "account_len", "tenure", "tenure_months",
            "months_active", "account_age", "subscription_months", "membership_months",
            "customer_age", "duration", "days_active", "contract_length", "period",
            "customer_tenure", "seniority", "lifetime_months", "time_on_platform"
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
            "tickets", "complaints", "inquiries", "service_calls", "cases", "cs_tickets",
            "helpdesk_calls", "service_requests", "escalations", "disputes", "issue_count",
            "support_inquiries", "num_complaints", "csat_tickets", "support_cases"
        ]
    },
    "Total day charge": {
        "display_name": "Primary Spend / Monthly Bill / MRR",
        "domain_concept": "Recurring Revenue / Primary Spend / Bill",
        "description": "Primary billable charge, monthly subscription amount (MRR), total order revenue, or billing amount.",
        "required": True,
        "default": 30.60,
        "type": "numeric",
        "synonyms": [
            "total_day_charge", "day_charge", "monthlycharges", "monthly_charges", "monthly_bill",
            "spend", "monthly_spend", "mrr", "revenue", "price", "amount", "total_bill",
            "charges", "fee", "cost", "billing_amount", "arpu", "total_charge", "bill_amount",
            "order_value", "total_amount", "purchase_amount", "gross_revenue"
        ]
    },
    "Total day minutes": {
        "display_name": "Primary Activity Volume / Usage Time",
        "domain_concept": "Product Usage Volume / Active Minutes",
        "description": "Usage volume, screen time, active minutes, app session duration, or core activity units.",
        "required": True,
        "default": 180.0,
        "type": "numeric",
        "synonyms": [
            "total_day_minutes", "day_minutes", "minutes", "usage", "total_usage", "usage_time",
            "active_minutes", "screen_time", "session_duration", "duration_minutes", "hours_used",
            "active_hours", "platform_time", "total_minutes", "consumption", "units_consumed"
        ]
    },
    "Total day calls": {
        "display_name": "Transactions / Orders / Sessions Frequency",
        "domain_concept": "Action Frequency / Transactions / Orders",
        "description": "Number of primary transactions, orders, purchases, sessions, logins, or active events.",
        "required": True,
        "default": 100,
        "type": "numeric",
        "synonyms": [
            "total_day_calls", "day_calls", "calls", "transactions", "orders", "num_orders",
            "purchases", "sessions", "logins", "events", "frequency", "activities",
            "order_count", "transaction_count", "session_count", "order_frequency"
        ]
    },
    "International plan": {
        "display_name": "VIP / Premium Tier / Add-on Subscription",
        "domain_concept": "Premium Tier / Global Plan / VIP Member",
        "description": "Whether the subscriber has an active premium add-on, VIP tier, international plan, or enterprise tier.",
        "required": True,
        "default": 0,
        "type": "boolean",
        "synonyms": [
            "international_plan", "intl_plan", "is_international", "premium", "premium_member",
            "loyalty_member", "vip", "subscription_tier", "enterprise", "plan_type",
            "has_addon", "tier", "is_vip", "prime_member", "membership_tier", "is_subscriber"
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
        "domain_concept": "Secondary Plan Add-on / Voicemail",
        "description": "Secondary feature subscription (e.g. voicemail, cloud backup, SMS alerts, paperless billing).",
        "required": False,
        "default": 0,
        "type": "boolean",
        "synonyms": [
            "voice_mail_plan", "vmail_plan", "voicemail", "has_voicemail", "messaging_plan",
            "cloud_storage", "extra_features", "service_addon", "paperless_billing", "backup_plan"
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
# NORMALIZATION & FUZZY MATCHING HELPERS
# ==============================================================================

def normalize_text(text: str) -> str:
    """Strip, lower-case, and remove punctuation/delimiters for reliable comparison."""
    if not isinstance(text, str):
        text = str(text)
    return re.sub(r"[^a-z0-9]", "", text.strip().lower())


def fuzzy_match_columns(user_columns: list) -> dict:
    """
    Intelligently map user-provided CSV columns to the model's canonical features.
    
    Returns:
    {
        "mapped": { "Account length": "tenure_months", ... },
        "confidence": { "Account length": 0.95, ... },
        "unmapped_targets": [...],
        "available_columns": user_columns
    }
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
            if user_col in assigned_user_cols:
                continue
            if u_norm == target_norm:
                mapped[target_name] = user_col
                confidence[target_name] = 1.0
                match_details[target_name] = {
                    "user_col": user_col,
                    "confidence": 1.0,
                    "match_type": "exact"
                }
                assigned_user_cols.add(user_col)
                break

        # Check exact synonym match
        if target_name not in mapped:
            for user_col, u_norm in user_col_norm.items():
                if user_col in assigned_user_cols:
                    continue
                if u_norm in synonyms_norm:
                    mapped[target_name] = user_col
                    confidence[target_name] = 0.95
                    match_details[target_name] = {
                        "user_col": user_col,
                        "confidence": 0.95,
                        "match_type": "synonym"
                    }
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
            if user_col in assigned_user_cols:
                continue

            # Substring match (e.g. "tenure" is in "user_tenure_months")
            for syn in synonyms_norm:
                if len(syn) >= 4 and (syn in u_norm or u_norm in syn):
                    score = 0.85
                    if score > best_score:
                        best_score = score
                        best_user_col = user_col
                        match_type = "fuzzy"

            # Difflib similarity ratio with target or synonyms
            matches = difflib.get_close_matches(u_norm, [target_norm] + synonyms_norm, n=1, cutoff=0.7)
            if matches:
                score = 0.75
                if score > best_score:
                    best_score = score
                    best_user_col = user_col
                    match_type = "fuzzy"

        if best_user_col and best_score >= 0.7:
            mapped[target_name] = best_user_col
            conf_val = round(best_score, 2)
            confidence[target_name] = conf_val
            match_details[target_name] = {
                "user_col": best_user_col,
                "confidence": conf_val,
                "match_type": match_type
            }
            assigned_user_cols.add(best_user_col)

    unmapped_targets = [t for t in CANONICAL_TARGET_FEATURES if t not in mapped]

    return {
        "mapped": mapped,
        "confidence": confidence,
        "matches": match_details,
        "unmapped_targets": unmapped_targets,
        "available_columns": user_columns
    }


# ==============================================================================
# DATA TRANSFORMATION AND MODEL PIPELINE ADAPTER
# ==============================================================================

def transform_mapped_dataset(
    source_df: pd.DataFrame,
    mapping: dict,
    model_features: list
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Transforms any user dataframe using the provided column mapping into the
    exact feature layout required by the trained Random Forest model.
    
    Returns:
    - prepared_df: DataFrame with exact model features ready for model.predict()
    - enriched_original_df: Copy of original user DataFrame with standardized reference columns
    """
    if source_df.empty:
        raise ValueError("The uploaded dataset contains 0 records.")

    enriched_original = source_df.copy()
    prepared = pd.DataFrame(index=source_df.index)

    # 1. Map columns from source_df based on user/auto mapping
    for target_feature, user_col in mapping.items():
        if user_col and user_col in source_df.columns:
            prepared[target_feature] = source_df[user_col]

    # 2. Impute and clean Boolean / Categorical Features
    for bool_col in ("International plan", "Voice mail plan"):
        if bool_col in prepared.columns:
            str_vals = prepared[bool_col].astype(str).str.strip().str.lower()
            prepared[bool_col] = str_vals.map({
                "yes": 1, "true": 1, "1": 1, "y": 1, "active": 1, "vip": 1, "premium": 1,
                "no": 0, "false": 0, "0": 0, "n": 0, "inactive": 0, "standard": 0
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
            # If all were NaN or missing, fill with default
            if prepared[num_col].isna().all():
                prepared[num_col] = CANONICAL_TARGET_FEATURES[num_col]["default"]
            else:
                median_val = prepared[num_col].median()
                fill_val = median_val if pd.notna(median_val) else CANONICAL_TARGET_FEATURES[num_col]["default"]
                prepared[num_col] = prepared[num_col].fillna(fill_val)
        else:
            # Smart Cross-Feature Derivation:
            if num_col == "Total day minutes" and "Total day charge" in prepared.columns:
                # Approximate 1 min ~ ₹0.17 -> minutes ~ charge * 5.88
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
# SAMPLE DOMAIN DATASET GENERATORS (PORTFOLIO & DEMO READY)
# ==============================================================================

def generate_sample_domain_df(domain: str = "ecommerce") -> pd.DataFrame:
    """
    Generates realistic customer DataFrames for various business domains
    so users can instantly demonstrate cross-domain churn analysis.
    """
    domain = (domain or "ecommerce").lower().strip()

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
            {"user_id": "SAAS_501", "months_active": 14, "mrr": 49.00, "active_minutes": 320, "num_logins": 45, "complaints": 0, "enterprise_tier": "yes", "region": "CA"},
            {"user_id": "SAAS_502", "months_active": 2, "mrr": 99.00, "active_minutes": 110, "num_logins": 12, "complaints": 4, "enterprise_tier": "no", "region": "NY"},
            {"user_id": "SAAS_503", "months_active": 8, "mrr": 29.00, "active_minutes": 210, "num_logins": 28, "complaints": 1, "enterprise_tier": "no", "region": "TX"},
            {"user_id": "SAAS_504", "months_active": 22, "mrr": 199.00, "active_minutes": 450, "num_logins": 85, "complaints": 5, "enterprise_tier": "yes", "region": "MA"},
            {"user_id": "SAAS_505", "months_active": 5, "mrr": 49.00, "active_minutes": 180, "num_logins": 20, "complaints": 0, "enterprise_tier": "no", "region": "CO"},
            {"user_id": "SAAS_506", "months_active": 1, "mrr": 149.00, "active_minutes": 80, "num_logins": 8, "complaints": 3, "enterprise_tier": "yes", "region": "GA"},
        ]
    elif domain == "banking":
        data = [
            {"account_id": "BANK_8801", "tenure": 36, "monthly_spend": 35.50, "transaction_count": 25, "inquiries": 1, "credit_card": "yes", "state": "IL"},
            {"account_id": "BANK_8802", "tenure": 4, "monthly_spend": 85.00, "transaction_count": 60, "inquiries": 5, "credit_card": "no", "state": "TX"},
            {"account_id": "BANK_8803", "tenure": 18, "monthly_spend": 24.00, "transaction_count": 15, "inquiries": 0, "credit_card": "yes", "state": "NY"},
            {"account_id": "BANK_8804", "tenure": 60, "monthly_spend": 12.00, "transaction_count": 8, "inquiries": 4, "credit_card": "no", "state": "CA"},
            {"account_id": "BANK_8805", "tenure": 9, "monthly_spend": 45.20, "transaction_count": 32, "inquiries": 2, "credit_card": "yes", "state": "FL"},
        ]
    else: # Default Telecom
        data = [
            {"State": "KS", "Account length": 128, "Area code": 415, "International plan": "no", "Voice mail plan": "yes", "Number vmail messages": 25, "Total day minutes": 265.1, "Total day calls": 110, "Total day charge": 45.07, "Total eve minutes": 197.4, "Total eve calls": 99, "Total eve charge": 16.78, "Total night minutes": 244.7, "Total night calls": 91, "Total night charge": 11.01, "Total intl minutes": 10.0, "Total intl calls": 3, "Total intl charge": 2.70, "Customer service calls": 1},
            {"State": "OH", "Account length": 107, "Area code": 415, "International plan": "no", "Voice mail plan": "yes", "Number vmail messages": 26, "Total day minutes": 161.6, "Total day calls": 123, "Total day charge": 27.47, "Total eve minutes": 195.5, "Total eve calls": 103, "Total eve charge": 16.62, "Total night minutes": 254.4, "Total night calls": 103, "Total night charge": 11.45, "Total intl minutes": 13.7, "Total intl calls": 3, "Total intl charge": 3.70, "Customer service calls": 4},
            {"State": "NJ", "Account length": 137, "Area code": 415, "International plan": "no", "Voice mail plan": "no", "Number vmail messages": 0, "Total day minutes": 243.4, "Total day calls": 114, "Total day charge": 41.38, "Total eve minutes": 121.2, "Total eve calls": 110, "Total eve charge": 10.30, "Total night minutes": 162.6, "Total night calls": 104, "Total night charge": 7.32, "Total intl minutes": 12.2, "Total intl calls": 5, "Total intl charge": 3.29, "Customer service calls": 0},
        ]

    return pd.DataFrame(data)


def generate_sample_domain_csv(domain: str = "ecommerce") -> str:
    """Returns downloadable CSV string for the requested domain."""
    df = generate_sample_domain_df(domain)
    return df.to_csv(index=False)

