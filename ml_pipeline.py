import os
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server generation
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve,
)

# Import MySQL database logger
from database import log_retrain_event_to_db

# Directories setup
IMG_DIR = os.path.join("static", "images")
MODEL_DIR = "models"
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# Set Seaborn / Matplotlib Style
sns.set_theme(style="darkgrid")
plt.rcParams.update({
    "font.sans-serif": "DejaVu Sans",
    "axes.edgecolor": "#374151",
    "axes.facecolor": "#111827",
    "figure.facecolor": "#0B0F19",
    "text.color": "#F9FAFB",
    "axes.labelcolor": "#9CA3AF",
    "xtick.color": "#9CA3AF",
    "ytick.color": "#9CA3AF"
})


def preprocess_churn_dataset(df):
    """
    Cleans raw customer churn dataframe and performs featurization.
    """
    clean_df = df.copy()

    # Drop target column from features
    target = None
    if "Churn" in clean_df.columns:
        target_col = clean_df["Churn"]
        target = (
            target_col.astype(str).str.strip().str.lower()
            .map({"true": 1, "false": 0, "yes": 1, "no": 0, "1": 1, "0": 0})
            .fillna(0).astype(int)
        )
        clean_df = clean_df.drop(columns=["Churn"])

    # Binary encoding for plans
    for col in ("International plan", "Voice mail plan"):
        if col in clean_df.columns:
            values = clean_df[col].astype(str).str.strip().str.lower()
            clean_df[col] = values.map({"yes": 1, "no": 0}).fillna(
                pd.to_numeric(clean_df[col], errors="coerce")
            ).fillna(0)

    # One-hot encode State column
    if "State" in clean_df.columns:
        state_dummies = pd.get_dummies(clean_df["State"], prefix="State", dtype=int)
        clean_df = clean_df.drop(columns=["State"])
        clean_df = pd.concat([clean_df, state_dummies], axis=1)

    # Convert all columns to numeric
    clean_df = clean_df.apply(pd.to_numeric, errors="coerce").fillna(0)
    return clean_df, target


def generate_evaluation_plots(model, X_test, y_test, feature_names):
    """
    Generates Matplotlib / Seaborn visual plots:
    1. Confusion Matrix Heatmap
    2. ROC Curve
    3. Feature Importance Horizontal Bar Chart
    """
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # --- 1. CONFUSION MATRIX PLOT ---
    fig, ax = plt.subplots(figsize=(6, 5))
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax,
                xticklabels=['Retained', 'Churned'], yticklabels=['Retained', 'Churned'])
    ax.set_title('Model Confusion Matrix', fontsize=14, fontweight='bold', color='#FFFFFF', pad=15)
    ax.set_xlabel('Predicted Label', fontsize=11, labelpad=10)
    ax.set_ylabel('Actual True Label', fontsize=11, labelpad=10)
    plt.tight_layout()
    cm_path = os.path.join(IMG_DIR, 'confusion_matrix.png')
    plt.savefig(cm_path, dpi=200, bbox_inches='tight')
    plt.close()

    # --- 2. ROC CURVE PLOT ---
    fig, ax = plt.subplots(figsize=(6, 5))
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    auc_val = roc_auc_score(y_test, y_proba)

    ax.plot(fpr, tpr, color='#4F46E5', lw=2.5, label=f'Random Forest (AUC = {auc_val:.3f})')
    ax.plot([0, 1], [0, 1], color='#6B7280', linestyle='--', lw=1.5, label='Random Chance')
    ax.set_title('Receiver Operating Characteristic (ROC)', fontsize=14, fontweight='bold', color='#FFFFFF', pad=15)
    ax.set_xlabel('False Positive Rate', fontsize=11, labelpad=10)
    ax.set_ylabel('True Positive Rate', fontsize=11, labelpad=10)
    ax.legend(loc='lower right', facecolor='#111827', edgecolor='#374151')
    plt.tight_layout()
    roc_path = os.path.join(IMG_DIR, 'roc_curve.png')
    plt.savefig(roc_path, dpi=200, bbox_inches='tight')
    plt.close()

    # --- 3. FEATURE IMPORTANCE PLOT ---
    fig, ax = plt.subplots(figsize=(8, 5))
    importances = model.feature_importances_
    indices = np.argsort(importances)[-10:]  # Top 10 features

    top_features = [feature_names[i] for i in indices]
    top_importances = importances[indices] * 100

    ax.barh(range(len(indices)), top_importances, align='center', color='#3B82F6')
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels(top_features, fontsize=10, fontweight='bold')
    ax.set_xlabel('Relative Importance (%)', fontsize=11, labelpad=10)
    ax.set_title('Top 10 Churn Predictive Features', fontsize=14, fontweight='bold', color='#FFFFFF', pad=15)
    plt.tight_layout()
    feat_path = os.path.join(IMG_DIR, 'feature_importance.png')
    plt.savefig(feat_path, dpi=200, bbox_inches='tight')
    plt.close()

    print(f"[OK] Matplotlib & Seaborn evaluation plots generated successfully in {IMG_DIR}!")


def retrain_model_pipeline(df, dataset_name="customer_churn.csv"):
    """
    Retrains the Random Forest Classifier on new data using Pandas, NumPy, Matplotlib & Scikit-Learn.
    Logs evaluation metrics to MySQL database.
    """
    print(f"\n[ML Pipeline] Initiating model retraining on dataset: {dataset_name}...")

    X, y = preprocess_churn_dataset(df)
    if y is None or len(y.unique()) < 2:
        raise ValueError("The dataset does not contain a valid 'Churn' target column for retraining.")

    # Split dataset Chronologically / Stratified
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=150,
        max_depth=8,
        min_samples_split=8,
        min_samples_leaf=4,
        max_features=0.7,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)

    # Predict & Evaluate
    y_pred = rf_model.predict(X_test)
    y_proba = rf_model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
    }

    # Save updated model binary
    model_file = os.path.join(MODEL_DIR, "random_forest_model.pkl")
    joblib.dump(rf_model, model_file)
    print(f"[OK] Retrained model saved to {model_file}. Metrics: {metrics}")

    # Generate Matplotlib & Seaborn plots
    generate_evaluation_plots(rf_model, X_test, y_test, X.columns.tolist())

    # Log to MySQL Database
    log_retrain_event_to_db(metrics, dataset_name=dataset_name)

    return metrics


if __name__ == "__main__":
    # Test script standalone execution
    csv_file = os.path.join("data", "customer_churn.csv")
    if os.path.exists(csv_file):
        test_df = pd.read_csv(csv_file)
        res = retrain_model_pipeline(test_df)
        print("Standalone Retrain Test Metrics:", res)
