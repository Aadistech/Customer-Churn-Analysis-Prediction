import pandas as pd

# Load dataset
df = pd.read_csv("data/customer_churn.csv")

# Basic information
print("\n===== FIRST 5 ROWS =====")
print(df.head())

print("\n===== DATASET SHAPE =====")
print(df.shape)

print("\n===== COLUMN NAMES =====")
print(df.columns.tolist())

print("\n===== DATA TYPES =====")
print(df.dtypes)

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())

print("\n===== CHURN DISTRIBUTION =====")
print(df["Churn"].value_counts())

#MODULE 2: DATA CLEANING AND PREPROCESSING 

print("\n===== DUPLICATE RECORDS =====")
print(df.duplicated().sum())

#check unique values in categorical columns 
print("\n===== INTERNATIONAL PLAN =====")
print(df["International plan"].value_counts())

print("\n===== VOICE MAIL PLAN =====")
print(df["Voice mail plan"].value_counts())

print("\n===== STATES =====")
print(df["State"].unique())

#Convert target variable
df["Churn"] = df["Churn"].astype(int)

#Convert Yes/No columns to 0/1
df["International plan"] = df["International plan"].map({
    "No": 0,
    "Yes": 1
})

df["Voice mail plan"] = df["Voice mail plan"].map({
    "No": 0,
    "Yes": 1
})

print("\n===== AFTER CONVERSION =====")
print(df[["International plan", "Voice mail plan", "Churn"]].head())

#One-hot encode State
df = pd.get_dummies(df, columns=["State"], dtype=int)

print("\n===== DATA AFTER ENCODING =====")
print(df.head())

print("\n===== NEW DATASET SHAPE =====")
print(df.shape)

#Save cleaned dataset
df.to_csv("data/cleaned_customer_churn.csv",index=False)

print("\n===== CLEANED DATASET SAVED =====")
print("data/cleaned_customer_churn.csv")