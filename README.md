# Customer Churn Analysis & Prediction System

## 📌 Project Overview

The **Customer Churn Analysis & Prediction System** is a Machine Learning-based application designed to analyze customer behavior and predict whether a customer is likely to **stay** or **churn**.

Customer churn refers to a situation where a customer stops using a company's services. Predicting churn helps organizations identify high-risk customers and take preventive retention actions.

The system performs:

- Data loading and preprocessing
- Exploratory Data Analysis (EDA)
- Feature preparation
- Machine Learning model training
- Model evaluation
- Customer churn prediction
- Churn probability analysis
- Web-based prediction using Flask

---

## 🎯 Objectives

The main objectives of this project are:

1. Analyze customer data to identify churn patterns.
2. Identify factors associated with customer churn.
3. Prepare customer data for Machine Learning.
4. Train multiple classification models.
5. Compare model performance using evaluation metrics.
6. Select the most suitable model for churn prediction.
7. Develop a web-based customer churn prediction system.
8. Help businesses identify customers who may be at risk of leaving.

---

## 🏗️ Project Architecture

```text
Customer Churn Analysis & Prediction System
                    │
                    ▼
             Customer Dataset
                    │
                    ▼
          Data Preprocessing
                    │
                    ▼
        Exploratory Data Analysis
                    │
                    ▼
       Feature Selection & Preparation
                    │
                    ▼
             Train-Test Split
                    │
                    ▼
             Machine Learning
              ┌─────┴─────┐
              ▼           ▼
        Logistic       Random
        Regression      Forest
              │           │
              └─────┬─────┘
                    ▼
            Model Evaluation
                    │
                    ▼
          Best Model Selection
                    │
                    ▼
          Customer Prediction
                    │
                    ▼
             Flask Backend
                    │
                    ▼
          Web Application
                    │
                    ▼
       Churn Prediction Result

📊 Dataset

The project uses a customer churn dataset containing 667 customer records and 20 original columns.

Important attributes include:
State
Account Length
Area Code
International Plan
Voice Mail Plan
Number of Voice Mail Messages
Total Day Minutes
Total Day Calls
Total Day Charge
Total Evening Minutes
Total Evening Calls
Total Evening Charge
Total Night Minutes
Total Night Calls
Total Night Charge
Total International Minutes
Total International Calls
Total International Charge
Customer Service Calls
Churn
Target Variable
Churn = 0 → Customer Stayed
Churn = 1 → Customer Churned
🔬 Project Modules
Module 1 — Data Loading

The original customer dataset is loaded using Pandas.

File:

data/customer_churn.csv
Module 2 — Data Cleaning & Preprocessing

The dataset is inspected and prepared for Machine Learning.

Operations include:

Checking missing values
Checking duplicate records
Converting categorical variables
Encoding the target variable
One-hot encoding State
Creating a cleaned dataset

Output:

data/cleaned_customer_churn.csv

The cleaned dataset contains:

667 rows × 70 columns
Module 3 — Exploratory Data Analysis

EDA is used to understand customer churn patterns.

The analysis includes:

Churn distribution
Churn by International Plan
Churn by Voice Mail Plan
Churn vs Customer Service Calls
Day Minutes vs Churn
Evening Minutes vs Churn
Night Minutes vs Churn
International Minutes vs Churn
Top States by Churn
Correlation Analysis
Key EDA Findings

The dataset contains:

Stayed   : 572
Churned  : 95

Customers with higher Total Day Minutes showed a stronger relationship with churn.

Customer service calls also showed a positive relationship with churn.

The correlation analysis showed:

Total Day Minutes       → 0.243
Customer Service Calls  → 0.233
Total Eve Minutes       → 0.176
Module 4 — Feature Selection & ML Preparation

The cleaned dataset is separated into:

X → Features
y → Target (Churn)

The data is divided into:

80% → Training
20% → Testing

Stratified splitting is used to maintain the churn distribution.

Feature scaling is performed using StandardScaler.

The scaler is saved as:

models/scaler.pkl
Module 5 — Model Training

Two Machine Learning classification algorithms are trained:

1. Logistic Regression

Used as a baseline classification model.

2. Random Forest

Used to capture nonlinear relationships and interactions between customer features.

The trained models are saved using Joblib.

models/
├── logistic_model.pkl
├── random_forest_model.pkl
└── scaler.pkl
📈 Module 6 — Model Evaluation

The models are evaluated using:

Accuracy
Precision
Recall
F1 Score
ROC-AUC
Confusion Matrix
Classification Report
Model Comparison
Metric	Logistic Regression	Random Forest
Accuracy	84.33%	91.04%
Precision	33.33%	100.00%
Recall	10.53%	36.84%
F1 Score	16.00%	53.85%
ROC-AUC	0.738	0.900
🏆 Selected Model

Random Forest was selected as the final model.

It achieved:

Accuracy : 91.04%
Precision: 100.00%
Recall   : 36.84%
F1 Score : 53.85%
ROC-AUC  : 0.900

Random Forest performed better than Logistic Regression across the major evaluation metrics.

Since the primary objective is to identify customers who may churn, recall and F1-score were also considered rather than relying only on accuracy.

🤖 Module 7 — Customer Churn Prediction

The trained Random Forest model is used to predict individual customer churn.

The prediction system provides:

Customer Information
        ↓
Machine Learning Model
        ↓
Prediction
        ↓
Stayed / Churned
        ↓
Churn Probability
🌐 Module 8 — Flask Backend

The Flask backend will connect the Machine Learning model with the web application.

The backend will:

Receive customer information
Prepare input data
Apply the saved scaler
Load the trained Random Forest model
Generate a prediction
Calculate churn probability
Return the prediction to the frontend
🎨 Module 9 — Frontend & Dashboard

The frontend will be developed using:

HTML
CSS
JavaScript

The web application will provide a professional interface for entering customer information and viewing prediction results.

Planned interface:

┌─────────────────────────────────────────┐
│       CUSTOMER CHURN PREDICTION         │
├─────────────────────────────────────────┤
│                                         │
│ Customer Information                    │
│                                         │
│ Account Length      [          ]         │
│ Area Code           [          ]         │
│ International Plan [ Yes / No ]         │
│ Voice Mail Plan     [ Yes / No ]        │
│ Day Minutes         [          ]         │
│ Evening Minutes     [          ]         │
│ Night Minutes       [          ]         │
│ Customer Calls      [          ]         │
│                                         │
│          [ Predict Churn ]              │
│                                         │
├─────────────────────────────────────────┤
│ Prediction: Customer Will Stay          │
│ Churn Probability: 18.5%                │
└─────────────────────────────────────────┘
🧪 Module 10 — Testing & Documentation

The final stage will include:

Model testing
Prediction testing
Flask application testing
Frontend testing
Input validation
Error handling
Documentation
Final project demonstration
🛠️ Technologies Used
Technology	Purpose
Python	Core programming
Pandas	Data manipulation
NumPy	Numerical operations
Scikit-learn	Machine Learning
Matplotlib	Data visualization
Flask	Backend / Web API
HTML	Frontend structure
CSS	Frontend styling
JavaScript	Frontend interaction
Joblib	Model serialization
Git	Version control
GitHub	Project repository
VS Code	Development environment
📁 Project Structure
Customer_Churn_Analysis_Prediction/
│
├── data/
│   ├── customer_churn.csv
│   └── cleaned_customer_churn.csv
│
├── models/
│   ├── scaler.pkl
│   ├── logistic_model.pkl
│   └── random_forest_model.pkl
│
├── static/
│   ├── css/
│   └── js/
│
├── Customer churn analysis and predction system/
│   ├── project images
│   └── project synopsis
│
├── analysis.py
├── eda.py
├── feature_selection.py
├── train_model.py
├── model_evaluation.py
├── predict.py
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
▶️ How to Run the Project
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
2. Open the project
cd Customer_Churn_Analysis_Prediction
3. Install dependencies
pip install -r requirements.txt
4. Run Data Analysis
python analysis.py
5. Run EDA
python eda.py
6. Prepare ML Features
python feature_selection.py
7. Train Models
python train_model.py
8. Evaluate Models
python model_evaluation.py
9. Run Prediction
python predict.py
10. Run Flask Application
python app.py

The web application will then be available locally through the Flask development server.

📌 Current Project Status
Module 1  Data Loading                  ✅
Module 2  Data Cleaning                ✅
Module 3  Exploratory Data Analysis    ✅
Module 4  ML Preparation               ✅
Module 5  Model Training               ✅
Module 6  Model Evaluation             ✅
Module 7  Prediction System             🔄
Module 8  Flask Backend                 ⏳
Module 9  Frontend & Dashboard          ⏳
Module 10 Testing & Documentation       ⏳
🔮 Future Improvements

Possible future improvements include:

Hyperparameter tuning
Cross-validation
Improved churn recall
Feature importance visualization
Customer risk scoring
Interactive dashboard
Prediction history
Database integration
Customer retention recommendations
Deployment to a cloud platform
👨‍💻 Author

Aaditya Jadhav

B.Sc. Computer Science

📜 License

This project is developed for educational and academic purposes.


### One important thing

Don't commit this README just yet if we're going to continue developing the project.

Our README currently describes **Modules 7–10 as planned/in progress**, which is correct. Once we finish the Flask application and frontend, we'll come back and update the README with:

- actual screenshots
- actual application workflow
- final project structure
- installation instructions
- final model results
- GitHub repository information

For now, create `README.md`, paste the content, save it, and then run:

```powershell
git status    