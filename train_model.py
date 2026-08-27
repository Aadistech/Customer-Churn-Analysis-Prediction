#5. MODEL TRAINING

import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

print("\n===== MODULE 5 STARTED =====")

#1 LOAD CLEANED DATASET 

df = pd.read_csv("data/cleaned_customer_churn.csv")

print("\n===== DATASET LOADED =====")
print("Dataset shape:", df.shape)

#2. SEPARATE FEATURES AND TARGTE

X = df.drop("Churn", axis=1)
y = df["Churn"]

print("\nFeature shape:", X.shape)
print("Target shape:", y.shape)

#3. TRAIN-TEST SPLIT

X_train, X_test, y_train, y_test =  train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\n===== TRAIN-TEST SPLIT =====")
print("Training data:", X_train.shape)
print("Testing data:", X_test.shape)

#4. CREATING MODELS

print("\n===== CREATING MODLES =====")

logistic_model = LogisticRegression(
    max_iter=1000,\
    random_state=42
)

random_forest_model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

print("Logistic Regression created.")
print("Random Forest created.")

#5. TRAIN LOGISTIC REGRESSION

print("\n===== TRAINING LOGISTIC REGRESSION =====")

logistic_model.fit(X_train, y_train)

print("Logistic Regression training completed.")

#6. TRAIN RANDOM FOREST 

print("\n===== TRAINING RANDOM FOREST =====")

random_forest_model.fit(X_train, y_train)

print("Random Forest training completed.")

#7. CREATE MODLES DISRECTORY

os.makedirs("models", exist_ok=True)

#8. SAVE TRAINED MODELS

joblib.dump(
    logistic_model,
    "models/logistic_model.pkl"
)

joblib.dump(
    random_forest_model,
    "models/ranndom_forest_model.pkl"
)

print("\n===== MODELS SAVED =====")
print("Logistic Regression -> models/logistic_model.pkl")
print("Random Forest -> models/random_forest_model.pkl")

print("\n===== MODULE 5 COMPLETED =====")
