# M
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

print("\n===== MODULE 6 STARTED =====")

#1. LOAD CLEANED DATASET


df = pd.read_csv("data/cleaned_customer_churn.csv")

print("\n===== DATASET LOADED =====")
print("Dataset shape:", df.shape)

# 2. SEPARATE FEATURES AND TARGET

X = df.drop("Churn", axis=1)
y = df["Churn"]

# 3. SAME TRAIN-TEST SPLIT USED DURING TRAINING

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\n===== TEST DATA READY =====")
print("Testing data:", X_test.shape)

# 4. LOAD TRAINED MODELS

logistic_model = joblib.load(
    "models/logistic_model.pkl"
)

random_forest_model = joblib.load(
    "models/random_forest_model.pkl"
)

print("\n===== MODELS LOADED =====")
print("Logistic Regression loaded.")
print("Random Forest loaded.")

# ============================================================
# 5. LOGISTIC REGRESSION PREDICTION
# ============================================================

print("\n===== LOGISTIC REGRESSION EVALUATION =====")

logistic_prediction = logistic_model.predict(X_test)

logistic_probability = logistic_model.predict_proba(X_test)[:, 1]

logistic_accuracy = accuracy_score(
    y_test,
    logistic_prediction
)

logistic_precision = precision_score(
    y_test,
    logistic_prediction,
    zero_division=0
)

logistic_recall = recall_score(
    y_test,
    logistic_prediction,
    zero_division=0
)

logistic_f1 = f1_score(
    y_test,
    logistic_prediction,
    zero_division=0
)

logistic_auc = roc_auc_score(
    y_test,
    logistic_probability
)

print("Accuracy :", logistic_accuracy)
print("Precision:", logistic_precision)
print("Recall   :", logistic_recall)
print("F1 Score :", logistic_f1)
print("ROC-AUC  :", logistic_auc)

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, logistic_prediction))

# ============================================================
# 6. RANDOM FOREST PREDICTION
# ============================================================

print("\n===== RANDOM FOREST EVALUATION =====")

rf_prediction = random_forest_model.predict(X_test)

rf_probability = random_forest_model.predict_proba(X_test)[:, 1]

rf_accuracy = accuracy_score(
    y_test,
    rf_prediction
)

rf_precision = precision_score(
    y_test,
    rf_prediction,
    zero_division=0
)

rf_recall = recall_score(
    y_test,
    rf_prediction,
    zero_division=0
)

rf_f1 = f1_score(
    y_test,
    rf_prediction,
    zero_division=0
)

rf_auc = roc_auc_score(
    y_test,
    rf_probability
)

print("Accuracy :", rf_accuracy)
print("Precision:", rf_precision)
print("Recall   :", rf_recall)
print("F1 Score :", rf_f1)
print("ROC-AUC  :", rf_auc)

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, rf_prediction))

# ============================================================
# 7. CLASSIFICATION REPORTS
# ============================================================

print("\n===== LOGISTIC REGRESSION REPORT =====")

print(
    classification_report(
        y_test,
        logistic_prediction,
        zero_division=0
    )
)

print("\n===== RANDOM FOREST REPORT =====")

print(
    classification_report(
        y_test,
        rf_prediction,
        zero_division=0
    )
)

# ============================================================
# 8. MODEL COMPARISON
# ============================================================

print("\n===== MODEL COMPARISON =====")

comparison = pd.DataFrame({
    "Model": [
        "Logistic Regression",
        "Random Forest"
    ],
    "Accuracy": [
        logistic_accuracy,
        rf_accuracy
    ],
    "Precision": [
        logistic_precision,
        rf_precision
    ],
    "Recall": [
        logistic_recall,
        rf_recall
    ],
    "F1 Score": [
        logistic_f1,
        rf_f1
    ],
    "ROC-AUC": [
        logistic_auc,
        rf_auc
    ]
})

print(comparison)

print("\n===== MODULE 6 COMPLETED =====")