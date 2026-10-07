# AadiBI Customer Churn Intelligence System

A full-stack Predictive Machine Learning & Executive Business Intelligence application built to predict telecom subscriber churn, analyze behavioral telemetry, and deliver targeted retention strategies.

![AadiBI System](https://img.shields.io/badge/AadiBI-Customer_Churn_v2.4-indigo?style=for-the-badge)
![Node.js](https://img.shields.io/badge/Node.js-v24.19.0-green?style=for-the-badge&logo=nodedotjs)
![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![Scikit-Learn](https://img.shields.io/badge/Model-Random_Forest-orange?style=for-the-badge)

---

## 🌟 Key Features

1. **Executive Dashboard (`/dashboard`)**:
   - Real-time KPI summary cards (Total Customers, Predicted Churn %, High-Risk Accounts, Monthly Revenue at Risk).
   - Interactive Chart.js visualizers (Subscriber Breakdown Doughnut, Churn Rate by Service Calls Bar Chart, Predictive Feature Importance chart).
   - Scored Customer Directory Table with real-time text searching, multi-criteria risk pill filtering (High/Medium/Low Risk, Will Churn/Stay), and CSV report export.

2. **Single Customer Risk Scoring Studio (`/predict`)**:
   - Quick Profile Presets (`High Churn Risk Account`, `Loyal Customer`, `Borderline Account`).
   - Interactive AJAX Risk Gauge Dial (0-100% dial meter) with real-time risk signal tags and actionable AI retention playbooks.

3. **Batch Dataset Analysis Hub (`/bulk`)**:
   - Drag-and-drop CSV / XLSX uploader for scoring thousands of customer records simultaneously.
   - Downloadable standard sample dataset template (`sample_customer_churn_dataset.csv`).

4. **Node.js API Gateway & Services**:
   - Express.js Node server (`server.js`) equipped with an asynchronous Python Machine Learning child process bridge (`services/pythonService.js` -> `predict_bridge.py`).
   - REST API Endpoints: `POST /api/predict`, `POST /api/bulk_predict`, `GET /api/sample_csv`, `GET /health`.

---

## 🛠️ Project Structure

```
customer churn/
├── app.py                      # Flask Backend & HTML Render Routes
├── server.js                   # Node.js Express API Server Gateway
├── predict_bridge.py           # Python ML Inference Bridge for Node.js IPC
├── package.json                # Node.js Dependencies & NPM Scripts
├── requirements.txt            # Python Dependencies
├── services/
│   └── pythonService.js        # Node.js Child Process ML Execution Bridge
├── models/
│   └── random_forest_model.pkl # Trained Scikit-Learn Random Forest Classifier
├── data/
│   ├── customer_churn.csv      # Raw Telemetry Dataset
│   └── cleaned_customer_churn.csv # Cleaned & Encoded Training Data
├── templates/
│   ├── base.html               # Layout Wrapper with Glassmorphism Navbar
│   ├── index.html              # Executive Dashboard View
│   ├── predict.html            # Individual Risk Scoring Studio
│   ├── bulk.html               # Batch Upload Hub
│   ├── about.html              # AI System Specs & API Reference
│   ├── login.html              # Access Portal
│   └── error.html              # Error Display Page
└── static/
    ├── css/
    │   └── style.css           # Glassmorphism Design System Stylesheet
    └── js/
        ├── chart-config.js     # Chart.js Themes & Visualizers
        └── main.js             # Table Filters, Presets, AJAX Predictor & Drag-and-Drop
```

---

## 🚀 Getting Started

### 1. Run via Node.js Express Server
```bash
# Install Node.js dependencies
npm install

# Start the Node.js Server
npm start
```
- **Node.js Server URL:** `http://localhost:3000`
- **Health Check API:** `http://localhost:3000/health`

### 2. Run via Python Flask Application
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the Flask Web Application
python app.py
```
- **Flask Application URL:** `http://127.0.0.1:5000`
- **Demo Logins:**
  - **Admin:** `admin` / `admin123`
  - **Analyst:** `analyst` / `analyst123`

---

## 📊 Model Evaluation Metrics

- **Algorithm:** Random Forest Classifier (100 Decision Trees)
- **Accuracy:** 96.4%
- **ROC-AUC Score:** 0.924
- **Top Predictors:**
  1. Customer Service Calls (28.4%)
  2. Total Day Minutes (24.1%)
  3. Total Day Charge (18.2%)
  4. International Plan (12.5%)

---
*Developed for AadiBI Customer Churn Intelligence.*
