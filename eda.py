import pandas as pd
import matplotlib.pyplot as plt

# MODULE 3: EXPLORATORY DATA ANALYSIS (EDA)
# LOAD ORIGINAL DATASET
df = pd.read_csv("data/customer_churn.csv")

print("\n===== EDA STARTED =====")
print("Dataset loaded successfully.")
print("Dataset shape:", df.shape)

#1. CHURN DISTRIBUTION
print("\n===== CHRUN DISTRIBUTION =====")
print(df["Churn"].value_counts())

churn_counts = df["Churn"].value_counts()

plt.figure(figsize=(7,5))
plt.bar(
    ["Stayed","Churned"],
    [
        churn_counts.get(False, 0),
        churn_counts.get(True, 0)
    ]
      )

plt.title("Customer churn Distribution")
plt.xlabel("Customer Status")
plt.ylabel("Number of Customers")
plt.tight_layout()
plt.show()

#2. CHURN BY INTERNATIONAL PLAN

print("\n===== CHURN BY INTERNATIONAL PLAN =====")

international_churn = pd.crosstab(
    df["International plan"],
    df["Churn"]
)

print(international_churn)

international_churn.plot(
    kind="bar",
    figsize=(8,5)
)

plt.title("Churn by International Plan")
plt.xlabel("International Plan")
plt.ylabel("Number of Customers")
plt.xticks(rotation=0)
plt.legend(["Stayed", "Churned"])
plt.tight_layout()
plt.show()

#3. CHURN BY VOICE MAIL PLAN
print("\n===== CHURN BY VOICE MAIL PLAN =====")
voice_mail_churn = pd.crosstab(
    df["Voice mail plan"], 
    df["Churn"]
    )

print(voice_mail_churn)

voice_mail_churn.plot(
    kind="bar",
    figsize=(8,5)
)
plt.title("Churn by Voice Mail Plan")
plt.xlabel("Voice Mail Plan")
plt.ylabel("Number of Customers")
plt.xticks(rotation=0)
plt.legend(["Stayed", "Churned"])
plt.tight_layout()
plt.show()

#4. CHURN VS CUSTOMER SERVICE CALLS

print("\n===== CHURN VS CUSTOMER SERVICE CALLS =====")

service_calls_churn = pd.crosstab(
    df["Customer service calls"],
    df["Churn"]
)

print(service_calls_churn)

service_calls_churn.plot(
    kind="bar",
    figsize=(9,5)
)

plt.title("Churn vs Customer Service Calls")
plt.xlabel("Number of Customer Service Calls")
plt.ylabel("Number of Customers")
plt.xticks(rotation=0)
plt.legend(["Stayed", "Churned"])
plt.tight_layout()
plt.show()

#5. DAY MINUTES ANALYSIS

print("\n===== DAY MINUTES BY CHURN STATUS =====")

print(
    df.groupby("Churn")["Total day minutes"].mean()
)

plt.figure(figsize=(8,5))

df.boxplot(
    column="Total day minutes",
    by="Churn",
)

plt.title("Day Minutes vs Churn")
plt.suptitle("")
plt.xlabel("Churn")
plt.ylabel("Total Day Minutes")

plt.tight_layout()
plt.show()

#6. EVENING MINUTES ANALYSIS

print("\n===== EVENING MINUTES BY CHURN STATUS =====")

evening_minutes = df.groupby("Churn")["Total eve minutes"].mean()

print(evening_minutes)

plt.figure(figsize=(8,5))

df.boxplot(
    column="Total eve minutes",
    by="churn"
)

plt.title("Evening Minutes vs Churn")
plt.suptitle("")
plt.xlabel("Churn")
plt.ylabel("Total Evening Minutes")

plt.tight_layout()
plt.show()

#7. NIGHT MINUTES BY CHURN STATUS

print("\n===== NIGHT MINUTES BY CHURN STATUS =====")

night_minutes = df.groupby("Churn")["Total night minutes"].mean()

print(night_minutes)

plt.figure(figsize=(8,5))

df.boxplot(
    column="Total night minutes",
    by="Churn"
)

plt.title("Night Minutes vs Churn")
plt.suptitle("")
plt.xlabel("Churn")
plt.ylabel("Total Night Minutes")

plt.tight_layout()
plt.show()

#8. INTERNATIONAL MINUTES BY CHURN STATUS

print("\n===== INTERNATIONAL MINUTES BY CHURN STATUS =====")

international_minutes = df.groupby("Churn")["Total intl minutes"].mean()

print(international_minutes)

plt.figure(figsize=(8,5))

df.boxplot(
    column="Total intl minutes",
    by="Churn"
)

plt.title("International Minutes vs Churn")
plt.suptitle("")
plt.xlabel("Churn")
plt.ylabel("Total International Minutes")

plt.tight_layout()
plt.show()

#9. TOP STATE BY CHURN

print("\n===== TOP STATE BY CHURN =====")

state_churn =(
    df[df["Churn"] == True]
    .groupby("State")
    .size()
    .sort_values(ascending=False)
)

print(state_churn.head(10))

plt.figure(figsize=(10,6))

state_churn.head(10).plot(
    kind="bar"
)

plt.title("Top 10 States by Number of Churned Customers")
plt.xlabel("State")
plt.ylabel("Number of Churned Customers")
plt.xticks (rotation=45)

plt.tight_layout()
plt.show()

# ============================================================
# 10. CORRELATION ANALYSIS
# ============================================================

print("\n===== CORRELATION ANALYSIS =====")

numeric_df = df.select_dtypes(
    include=["int64", "float64", "bool"]
)

correlation = numeric_df.corr()["Churn"].sort_values(
    ascending=False
)

print(correlation)


print("\n===== MODULE 3 COMPLETED =====")