# Customer Churn Analysis & Prediction System (AadiBI)

## 📌 Project Overview

The **Customer Churn Analysis & Prediction System** (AadiBI Intelligence System) is a Machine Learning-powered application designed to analyze customer behavior, predict churn risk, and deliver actionable business intelligence.

Customer churn occurs when a customer stops using a company's services. By predicting churn early, organizations can identify high-risk customers, understand underlying risk drivers, and deploy proactive retention strategies.

The system performs:
- **Data Ingestion & Preprocessing:** Data cleaning, missing value handling, categorical encoding, and feature scaling.
- **Exploratory Data Analysis (EDA):** Statistical inspection and visual analysis of behavioral churn drivers.
- **Feature Selection & Preparation:** Train-test splitting and feature alignment.
- **Machine Learning Modeling:** Multiple classification algorithms (Logistic Regression, Random Forest).
- **Model Evaluation:** Performance comparison across Accuracy, Precision, Recall, F1 Score, and ROC-AUC metrics.
- **Individual & Bulk Churn Prediction:** Web application predicting churn for single customers or bulk batch datasets (CSV / Excel).
- **Interactive Business Intelligence Dashboard:** Real-time KPI summaries, dynamic Chart.js visualizations, risk level segmentation, and downloadable prediction reports.

---

## 🎯 Objectives

1. Analyze customer usage data to identify key churn indicators.
2. Build and compare classification models to identify the optimal predictor.
3. Select the best performing model (Random Forest Classifier).
4. Build a secure Flask web application supporting user roles (`admin` & `analyst`).
5. Develop an intuitive frontend interface for individual customer lookup and bulk dataset uploads.
6. Generate rule-based retention recommendations and transparent risk signals.
7. Enable CSV/Excel data export with model prediction and risk scores appended.

---

## 🏗️ Project Architecture

```text
               Customer Dataset (CSV / Excel)
                             │
                             ▼
                   Data Preprocessing
                             │
                             ▼
                Exploratory Data Analysis
                             │
                             ▼
              Feature Engineering & Preparation
                             │
                             ▼
                     Train-Test Split
                             │
                             ▼
              Machine Learning Model Training
               ┌─────────────┴─────────────┐
               ▼                           ▼
      Logistic Regression           Random Forest
               │                           │
               └─────────────┬─────────────┘
                             ▼
                     Model Evaluation
                             │
                             ▼
                 Best Model Selection (RF)
                             │
                             ▼
                      Flask Web Backend
               ┌─────────────┴─────────────┐
               ▼                           ▼
     Individual Prediction           Bulk Upload
     (Single Customer Form)       (Batch CSV/XLSX)
               │                           │
               └─────────────┬─────────────┘
                             ▼
               AadiBI Analytics Dashboard
            (KPIs, Charts, Risk Signals, CSV Export)
```

---

## 📊 Dataset & Features

The baseline dataset contains **667 customer records** with **20 original features**:

- `State`: Customer location (51 U.S. states)
- `Account length`: Duration of account active status
- `Area code`: Phone area code
- `International plan`: Binary indicator (`Yes`/`No`)
- `Voice mail plan`: Binary indicator (`Yes`/`No`)
- `Number vmail messages`: Count of voicemail messages
- `Total day minutes`, `Total day calls`, `Total day charge`: Daytime usage metrics
- `Total eve minutes`, `Total eve calls`, `Total eve charge`: Evening usage metrics
- `Total night minutes`, `Total night calls`, `Total night charge`: Night usage metrics
- `Total intl minutes`, `Total intl calls`, `Total intl charge`: International usage metrics
- `Customer service calls`: Frequency of support calls
- `Churn`: Target classification (`0` = Stayed, `1` = Churned)

Preprocessing expands state variables into 51 one-hot encoded columns, resulting in **69 feature inputs** for the model.

---

## 📈 Model Performance & Evaluation

| Metric | Logistic Regression | Random Forest (Selected Model) |
| :--- | :---: | :---: |
| **Accuracy** | 84.33% | **91.04%** |
| **Precision** | 33.33% | **100.00%** |
| **Recall** | 10.53% | **36.84%** |
| **F1 Score** | 16.00% | **53.85%** |
| **ROC-AUC** | 73.78% | **90.05%** |

### Selected Model: Random Forest Classifier
- High precision (100%) ensures zero false positives when classifying high-risk accounts.
- Superior ROC-AUC score (0.900) demonstrates strong capability in ranking customer churn probability.

---

## 📁 Project Structure

```text
Customer_Churn_Analysis_Prediction/
│
├── data/
│   ├── customer_churn.csv            # Original raw dataset
│   ├── cleaned_customer_churn.csv    # Preprocessed 69-feature dataset
│   └── bulk_prediction_results.csv   # Output prediction export file
│
├── models/
│   ├── scaler.pkl                    # StandardScaler model artifact
│   ├── logistic_model.pkl            # Trained Logistic Regression model
│   └── random_forest_model.pkl       # Trained Random Forest model
│
├── static/
│   ├── css/
│   │   └── style.css                 # Modern UI responsive styling
│   ├── js/
│   │   └── script.js                  # Frontend interactivity & Chart.js logic
│   └── images/
│       └── brandlogo.jpg              # System logo asset
│
├── templates/
│   ├── login.html                    # Authentication page
│   ├── index.html                    # Home & individual prediction form
│   ├── bulk_upload.html              # CSV/XLSX file upload interface
│   ├── bulk_result.html              # Analytics dashboard & results table
│   ├── result.html                   # Individual prediction result view
│   └── error.html                    # User-friendly error page
│
├── analysis.py                       # Module 1 & 2: Data loading and cleaning
├── eda.py                            # Module 3: Exploratory Data Analysis
├── feature_selection.py              # Module 4: ML preparation and scaling
├── train_model.py                    # Module 5: Model training
├── model_evaluation.py               # Module 6: Model evaluation metrics
├── predict.py                        # Module 7: CLI prediction utility
├── app.py                            # Module 8 & 9: Flask Web Application
├── requirements.txt                  # Project dependencies
├── .gitignore                        # Git exclusion rules
└── README.md                         # Project documentation
```

---

## 🛠️ Installation & Setup Guide

### 1. Prerequisites
Ensure Python 3.9+ is installed on your system.

### 2. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/Aadistech/Customer-Churn-Analysis-Prediction.git
cd Customer_Churn_Analysis_Prediction
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Machine Learning Pipeline (Optional re-training)
```bash
python analysis.py
python eda.py
python feature_selection.py
python train_model.py
python model_evaluation.py
```

### 5. Launch the Web Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

### Demo Credentials
- **Admin Role:** `admin` / `admin123`
- **Analyst Role:** `analyst` / `analyst123`

---

## 📌 Project Module Status

| Module | Description | Status |
| :---: | :--- | :---: |
| **Module 1** | Data Loading & Verification | ✅ Completed |
| **Module 2** | Data Cleaning & Categorical Encoding | ✅ Completed |
| **Module 3** | Exploratory Data Analysis (EDA) | ✅ Completed |
| **Module 4** | Feature Selection & Standard Scaling | ✅ Completed |
| **Module 5** | Classification Model Training | ✅ Completed |
| **Module 6** | Model Evaluation & Performance Metrics | ✅ Completed |
| **Module 7** | CLI & Web Customer Prediction System | ✅ Completed |
| **Module 8** | Flask Backend & Authentication | ✅ Completed |
| **Module 9** | Business Intelligence Frontend Dashboard | ✅ Completed |
| **Module 10** | End-to-End Testing & Comprehensive Documentation | ✅ Completed |

---

## 👨‍💻 Author & Acknowledgments

- **Developer:** Aaditya Jadhav (B.Sc. Computer Science)
- **Institution:** MGM College of CS & IT

---

## 📜 License

This project is developed for educational and academic purposes.