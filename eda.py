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

churn_counts = df["churn"].value_counts()

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
