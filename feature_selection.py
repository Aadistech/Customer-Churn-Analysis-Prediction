#MODULE 4: FEATURE SELECTION & ML PREPATION

import pandas as pd

print("\n===== MODULE 4 STARTED =====")

#1. LOAD CLEANED DATASET
df =pd.read_csv("data/cleaned_customer_churn.csv")

print("\n===== DATASET LOADED =====")
print("Dataset shape:",df.shape)

#2. DISPLAY COLUMN NAMES 
print("\n===== FEATURE COLUMNS =====")
print(df.columns.tolist())

#3. SEPARATE FEATURES (X) AND TARGET (y)
X = df.drop("Churn", axis=1)
y = df["Churn"]

print("\n===== FEATURES (X) =====")
print("Features shape:", X.shape)

print("\n===== TARGET (y) =====")
print("Target shape:", y.shape)

#4. CHECK TARGET DISTRIBUTION 

print("\n ===== TARGET DISTRIBUTION =====")
print(y.value_counts())

#5. CHECK FOR MISSING VALUES 

print("\n===== FEATURE DATA TYPES =====")
print(X.isnull().sum().sum())

#6. CHECK FEATURE DATA TYPES

print("\n===== FEATURE DATA TYPES =====")
print(X.dtypes)

# ============================================================
# 7. TRAIN-TEST SPLIT
# ============================================================

from sklearn.model_selection import train_test_split

print("\n===== TRAIN-TEST SPLIT =====")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training features:", X_train.shape)
print("Testing features:", X_test.shape)

print("\n===== TRAINING TARGET DISTRIBUTION =====")
print(y_train.value_counts())

print("\n===== TESTING TARGET DISTRIBUTION =====")
print(y_test.value_counts())

print("\n===== MODULE 4 STEP 2 COMPLETED =====")

#8. FEATURE SCALING 

from sklearn.preprocessing import StandardScaler

print("\n===== FEATURE SCALING =====")

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("Scaled training data shape:", X_train_scaled.shape)
print("Scaled testing data shape:", X_test_scaled.shape)

print("\n===== FEATURE SCALING COMPLETED =====")

#9. SAVE SCALER

import joblib 
import os

print("\n===== SAVING SCALER =====")

#Create models folder if it doesn't exist 
os.makedirs("models", exist_ok=True)

#Save the scaler
joblib.dump(scaler,"models/scaler.pkl")

print("Scaler saved successfully at: models/scaler.pkl")

print("\n===== MODULE 4 COMPLETED =====")