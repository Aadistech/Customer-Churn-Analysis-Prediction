import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def generate_viva_doc(output_path):
    doc = Document()
    
    # Page setup - 1 inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("AadiBI: Customer Churn Intelligence & Retention System")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(30, 41, 59) # Slate 800
    
    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_sub.add_run("Comprehensive Viva Voce & Project Defense Master Guide\n(Architecture, Machine Learning, Full-Stack Engineering, Cloud Deployment & Real-World FAQs)")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(12)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(79, 70, 229) # Indigo 600
    
    doc.add_paragraph() # Spacer

    # Metadata Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Project Title:", "Enterprise Customer Churn Analysis, Prediction & Retention Intelligence System (AadiBI)"),
        ("Technology Stack:", "Python 3.11, Flask, Scikit-Learn, Pandas, NumPy, SQLAlchemy, Gunicorn, Firebase Admin/Auth/Firestore, Render Cloud"),
        ("Machine Learning Models:", "Random Forest Classifier, Logistic Regression, Multi-Domain Pipelines (Telecom, E-Commerce, SaaS, Banking)"),
        ("Key Innovation:", "Dynamic Cross-Domain Schema Mapping, INR Revenue-at-Risk Calibration, What-If Retention ROI Simulation")
    ]
    for row_idx, (k, v) in enumerate(meta_data):
        row = meta_table.rows[row_idx]
        cell_k, cell_v = row.cells[0], row.cells[1]
        cell_k.width = Inches(2.2)
        cell_v.width = Inches(4.3)
        set_cell_background(cell_k, "F1F5F9")
        set_cell_background(cell_v, "F8FAFC")
        set_cell_margins(cell_k, 80, 80, 120, 120)
        set_cell_margins(cell_v, 80, 80, 120, 120)
        
        pk = cell_k.paragraphs[0]
        rk = pk.add_run(k)
        rk.font.name = "Arial"
        rk.font.size = Pt(9.5)
        rk.font.bold = True
        rk.font.color.rgb = RGBColor(30, 41, 59)
        
        pv = cell_v.paragraphs[0]
        rv = pv.add_run(v)
        rv.font.name = "Arial"
        rv.font.size = Pt(9.5)
        rv.font.color.rgb = RGBColor(51, 65, 85)
        
    doc.add_paragraph() # Spacer

    # Helper for adding sections
    def add_section_header(title_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title_text)
        run.font.name = "Arial"
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(67, 56, 202) # Indigo 700

    def add_qa(q_num, question, answer, key_tip=None):
        pq = doc.add_paragraph()
        pq.paragraph_format.space_before = Pt(10)
        pq.paragraph_format.space_after = Pt(3)
        pq.paragraph_format.keep_with_next = True
        rq = pq.add_run(f"Q{q_num}. {question}")
        rq.font.name = "Arial"
        rq.font.size = Pt(11)
        rq.font.bold = True
        rq.font.color.rgb = RGBColor(15, 23, 42) # Slate 900
        
        pa = doc.add_paragraph()
        pa.paragraph_format.space_before = Pt(2)
        pa.paragraph_format.space_after = Pt(6)
        ra = pa.add_run(answer)
        ra.font.name = "Arial"
        ra.font.size = Pt(10)
        ra.font.color.rgb = RGBColor(51, 65, 85)
        
        if key_tip:
            pt = doc.add_paragraph()
            pt.paragraph_format.space_before = Pt(2)
            pt.paragraph_format.space_after = Pt(8)
            rt_label = pt.add_run("💡 Examiner Pro-Tip / Key Formula: ")
            rt_label.font.name = "Arial"
            rt_label.font.size = Pt(9.5)
            rt_label.font.bold = True
            rt_label.font.color.rgb = RGBColor(180, 83, 9) # Amber 700
            
            rt_val = pt.add_run(key_tip)
            rt_val.font.name = "Arial"
            rt_val.font.size = Pt(9.5)
            rt_val.font.italic = True
            rt_val.font.color.rgb = RGBColor(146, 64, 14)

    # ==========================================
    # SECTION 1: PROJECT OVERVIEW & MOTIVATION
    # ==========================================
    add_section_header("1. Project Overview & Business Value")
    
    add_qa(
        1, "What is the primary objective of the AadiBI Customer Churn Intelligence System?",
        "Customer churn represents the percentage of subscribers or customers who stop doing business with a company over a given timeframe. "
        "The objective of AadiBI is to develop an end-to-end, multi-domain machine learning system that not only predicts customer defection "
        "before it happens, but also diagnoses specific behavioral risk drivers, calculates financial revenue at risk in Indian Rupees (₹), "
        "and provides an interactive retention simulator to test mitigation strategies.",
        "Acquiring a new customer costs 5 to 7 times more than retaining an existing one. A 5% increase in customer retention can boost corporate profits by 25% to 95%."
    )
    
    add_qa(
        2, "What business domains does your platform support, and why did you design it for multi-domain use?",
        "AadiBI supports four major enterprise industries: Telecom/Communications, E-Commerce, SaaS (Cloud Software), and Banking/Financial Services. "
        "Most existing academic churn projects are rigidly hardcoded to a single legacy telecom CSV. In real-world enterprise consulting, "
        "churn patterns vary by domain (e.g., E-Commerce churn is driven by support tickets and order frequency, SaaS by MRR and inactive login days, "
        "Banking by products used and credit score, Telecom by contract commitments and monthly bill charges). Designing a multi-domain platform "
        "with an adaptive schema mapper demonstrates enterprise scalability.",
        "Demonstrate how AadiBI auto-detects column names and shifts KPI dashboards, risk drivers, and presets dynamically when switching domains."
    )
    
    add_qa(
        3, "How does your system calculate 'Revenue at Risk' in Indian Rupees (₹)?",
        "The system estimates revenue at risk by multiplying the count of predicted churned customers by the cohort's average monthly billing "
        "over an annualized/half-year retention window (6 months) calibrated at 1 USD = 83.0 INR:\n"
        "Revenue at Risk (₹) = Churned Customers × (Average Monthly Spend × 83.0) × 6 months.\n"
        "For banking datasets, it computes capital defection risk based on total at-risk customer balances.",
        "Always state the exchange rate calibration (1 USD = 83.0 INR) and explain that churn isn't just an abstract percentage—it is a measurable balance-sheet risk."
    )

    # ==========================================
    # SECTION 2: MACHINE LEARNING & ALGORITHMS
    # ==========================================
    add_section_header("2. Machine Learning Algorithms & Modeling")

    add_qa(
        4, "Why did you choose Random Forest Classifier as your primary model over simple Logistic Regression or complex Deep Learning?",
        "1. Non-linear relationships: Customer churn behaviors (e.g., high monthly charges combined with month-to-month contracts and lack of tech support) "
        "are inherently non-linear and interactive, which standard Logistic Regression struggles to capture without manual interaction terms.\n"
        "2. Robustness to Overfitting: Random Forest uses bagging (Bootstrap Aggregation) and random feature subspace sampling, creating an ensemble of decorrelated decision trees that significantly reduces model variance compared to individual decision trees.\n"
        "3. Interpretability & Feature Importance: Random Forest provides explicit feature importances (MDI / Gini impurity reduction), allowing business executives to pinpoint exactly which attributes drive defection.\n"
        "4. Tabular Efficiency vs. Deep Learning: Deep neural networks on tabular datasets with a few thousand records suffer from high computational overhead, risk of severe overfitting, and lack of transparency without providing higher accuracy than gradient boosting or random forests.",
        "Emphasize the bias-variance tradeoff: Decision trees have low bias but high variance; Random Forests average multiple trees to slash variance while maintaining low bias."
    )

    add_qa(
        5, "Explain the internal mechanism of Bagging (Bootstrap Aggregation) in Random Forest.",
        "Bagging operates in two steps:\n"
        "1. Bootstrapping: Given a training set of N samples, the algorithm draws N samples with replacement multiple times to create B independent bootstrap datasets. Approximately 63.2% of unique samples are selected in each bootstrap, while the remaining 36.8% form Out-of-Bag (OOB) samples used for internal validation.\n"
        "2. Random Feature Subspace: At each node split in every tree, instead of evaluating all M features, only a random subset (typically sqrt(M)) is considered. This decorrelates the trees—ensuring that dominant features do not dictate every tree.\n"
        "3. Aggregation: For classification, each individual tree votes on the class label. The final prediction probability is the majority vote or average class probability across all trees.",
        "Variance Reduction Formula: If all B trees were identical and perfectly correlated, variance would be unchanged. By decorrelating trees through random feature selection, the variance of the ensemble converges toward Var(Tree) / B."
    )

    add_qa(
        6, "How does a Decision Tree decide where to split a node? (Gini Impurity vs. Entropy)",
        "Decision trees evaluate split points by measuring the purity of child nodes after the split.\n"
        "• Gini Impurity: Measures the probability that a randomly chosen element from the set would be incorrectly labeled if it were randomly labeled according to the distribution of labels in the subset:\n"
        "  Gini = 1 - Σ (p_i)^2\n"
        "  A pure node (all churn or all stay) has Gini = 0.0. Maximum impurity for binary classification is 0.5.\n"
        "• Entropy (Information Gain): Measures disorder using logarithmic information theory:\n"
        "  Entropy = - Σ (p_i * log2(p_i))\n"
        "  Information Gain = Entropy(Parent) - Σ [ (|Child_v| / |Parent|) * Entropy(Child_v) ].\n"
        "Our Random Forest implementation uses Gini impurity by default because it computes significantly faster (no logarithms) while yielding identical splits in >98% of cases.",
        "Scikit-learn's default is criterion='gini'. If asked why not entropy, state computational efficiency during ensemble tree induction."
    )

    add_qa(
        7, "How do you calculate Feature Importance in Random Forest?",
        "We utilize Mean Decrease in Impurity (MDI). Whenever a node split occurs on feature j, the Gini impurity decreases from the parent node to its children. "
        "The decrease in impurity is weighted by the proportion of samples reaching that node. "
        "The overall importance of feature j is computed by summing these weighted impurity reductions across all trees in the forest and normalizing the total sum to 1.0 (100%). "
        "In our Telco model, Contract Type (34.2%), Monthly Charges (25.8%), and Tenure (17.5%) emerged as the top risk drivers.",
        "Examiner trap: 'Can MDI be biased?' Answer: Yes, MDI can artificially favor numerical features with high cardinality. For critical validation, Permutation Importance can be computed as a cross-check."
    )

    # ==========================================
    # SECTION 3: DATA PREPROCESSING & CLEANING
    # ==========================================
    add_section_header("3. Data Preprocessing, Cleaning & Feature Engineering")

    add_qa(
        8, "What data cleaning challenges did you encounter in the Kaggle Telco Churn dataset, and how did you resolve them?",
        "1. Whitespace in Numerical Fields: For customers with tenure = 0, the 'TotalCharges' column contains empty whitespace strings (' ') instead of 0.0. Standard pd.to_numeric() converts these to NaN, which caused ValueError: Cannot convert non-finite values to integer when calling .astype(int).\n"
        "2. Currency Symbols and Formatting: Uploaded spreadsheets often format currency as '$56.95', '₹1,889.50', or with thousands commas.\n"
        "3. Multi-Class Categorical Flags: Telco columns include values such as 'No phone service', 'No internet service', 'Month-to-month', 'One year', and 'Two year'.\n"
        "Resolution: We engineered safe_numeric_clean() which strips symbols ($/₹/€/£/commas), replaces empty strings with 0.0, and safely casts to float. We also constructed BOOLEAN_MAPPING_DICT to cleanly map multi-class text into binary/ordinal integers without unhandled NaNs.",
        "Mention the specific customer case: Customer ID '4472-LVYGI' with tenure=0 and empty TotalCharges was the classic trigger for the crash before safe_numeric_clean() was implemented."
    )

    add_qa(
        9, "How did you handle categorical encoding, and why did you avoid Label Encoding for nominal categories?",
        "Categorical variables are divided into binary, ordinal, and nominal categories:\n"
        "• Binary variables (e.g., Partner, Dependents, PhoneService, PaperlessBilling) were mapped directly to 0/1 integers.\n"
        "• Ordinal categories (e.g., Contract: Month-to-month=0, 1-year=1, 2-year=2) preserve intuitive progression.\n"
        "• Nominal categories (e.g., State codes AK through WY, InternetService DSL/Fiber Optic/None) were One-Hot Encoded (Dummy Encoded).\n"
        "We avoided Label Encoding for nominal attributes like State or Internet Service because assigning arbitrary integers (e.g., Fiber Optic = 1, DSL = 2, None = 3) inadvertently implies an artificial mathematical hierarchy or distance that tree and linear models can misinterpret.",
        "One-hot encoding creates binary indicators (e.g., State_CA, State_NY). Our model feature vector explicitly aligns with all 69 model.feature_names_in_ columns."
    )

    add_qa(
        10, "What is Class Imbalance, how does it affect churn models, and how did you address it?",
        "Class imbalance occurs when the majority of customer accounts stay (e.g., 73%-85%) while only a minority defect (15%-27%). "
        "If a naive model predicts 'Stay' for every customer, it achieves 85% accuracy while failing 100% of churn detection. "
        "To address this:\n"
        "1. Algorithm Level: We utilized class_weight='balanced' in Random Forest, which automatically adjusts sample weights inversely proportional to class frequencies:\n"
        "   Weight_j = Total_Samples / (n_classes * Samples_in_Class_j)\n"
        "2. Resampling Strategies: Demonstrated SMOTE (Synthetic Minority Over-sampling Technique) to synthetically generate minority churn instances by interpolating between k-nearest neighbors in feature space.\n"
        "3. Evaluation Metrics: We rejected Accuracy as our primary metric and instead optimized for Recall, Precision, and the ROC-AUC curve.",
        "High Recall is critical in churn prediction: It is much cheaper to send a discount email to a non-churner (False Positive) than to let a high-value customer defect unnoticed (False Negative)."
    )

    # ==========================================
    # SECTION 4: MULTI-DOMAIN SCHEMA MAPPING
    # ==========================================
    add_section_header("4. Universal Schema Mapping & Dynamic Adaptation")

    add_qa(
        11, "How does your Universal Schema Mapper work when a user uploads an arbitrary CSV or Excel file?",
        "The schema mapper acts as an intelligent abstraction layer between arbitrary user spreadsheets and the trained ML pipeline:\n"
        "1. Header Extraction: Extracts all column headers from the uploaded CSV/XLSX file.\n"
        "2. Fuzzy String Matching: Uses token similarity (difflib / Levenshtein distance) against canonical predictive dimensions (Tenure, Charges, Complaints, Activity, Contracts).\n"
        "3. Domain Detection: Scans key indicator columns (e.g., if 'mrr' or 'active_users' -> SaaS; if 'credit_score' or 'balance' -> Banking; if 'order_count' -> E-Commerce; if 'contract' or 'phone_service' -> Telecom).\n"
        "4. Feature Transformation & Vector Alignment: Maps user columns to target features, cleans missing values with safe_numeric_clean(), one-hot encodes state indicators, and reindexes the matrix to match the exact feature_names_in_ layout expected by the model.",
        "This allows a company to drag-and-drop raw datasets from Shopify, Stripe, HubSpot, or Salesforce directly into AadiBI without writing code."
    )

    add_qa(
        12, "What happens if a user uploads a dataset with missing columns?",
        "The schema mapper implements a Fallback & Imputation Architecture. "
        "Every canonical feature in CANONICAL_TARGET_FEATURES has a defined domain default (e.g., if 'support_tickets' is absent, it defaults to median 1; "
        "if 'voice mail plan' is absent, it defaults to 0). "
        "During feature transformation, the DataFrame is reindexed with .reindex(columns=model_features, fill_value=default_value). "
        "This guarantees that the input matrix strictly matches the model's required dimensionality without throwing shape mismatch exceptions.",
        "Always highlight that graceful degradation prevents runtime crashes in production."
    )

    # ==========================================
    # SECTION 5: MODEL EVALUATION & METRICS
    # ==========================================
    add_section_header("5. Model Evaluation, Metrics & Validation")

    add_qa(
        13, "Explain Confusion Matrix, Precision, Recall, and F1-Score in the context of Customer Churn.",
        "A Confusion Matrix categorizes prediction outcomes into four quadrants:\n"
        "• True Positive (TP): Model predicts customer will churn, and they actually churn (Success).\n"
        "• True Negative (TN): Model predicts customer will stay, and they actually stay (Success).\n"
        "• False Positive (FP, Type I Error): Model predicts churn, but the customer intended to stay (Cost: Minor unnecessary retention discount).\n"
        "• False Negative (FN, Type II Error): Model predicts stay, but the customer actually churned (Cost: Severe—loss of total customer lifetime value).\n\n"
        "Key Metrics:\n"
        "• Precision = TP / (TP + FP) -> Out of all customers flagged as at-risk, what percentage truly churned?\n"
        "• Recall (Sensitivity) = TP / (TP + FN) -> Out of all customers who actually churned, what percentage did we catch?\n"
        "• F1-Score = 2 * (Precision * Recall) / (Precision + Recall) -> Harmonic mean balancing precision and recall.",
        "In customer churn, Recall is typically prioritized over Precision because the business cost of losing a customer (FN) vastly exceeds the cost of a promotional email (FP)."
    )

    add_qa(
        14, "What is ROC-AUC, and why is it superior to Accuracy for churn evaluation?",
        "The Receiver Operating Characteristic (ROC) curve plots True Positive Rate (Recall) on the Y-axis against False Positive Rate (1 - Specificity) on the X-axis across all possible classification decision thresholds (from 0.0 to 1.0).\n"
        "The Area Under the Curve (AUC) measures the model's ability to rank order risk:\n"
        "• AUC = 0.5: Random guessing (no discriminative ability).\n"
        "• AUC = 0.85 - 0.93: Excellent discriminative power (as achieved by our Random Forest pipeline).\n"
        "AUC is threshold-independent and invariant to class distribution, meaning it remains reliable even when the churn rate is heavily imbalanced.",
        "An AUC of 0.90 means that if you randomly choose one churned customer and one retained customer, there is a 90% probability the model assigns a higher churn probability to the churned customer."
    )

    add_qa(
        15, "How do you evaluate whether your model is overfitting, and what techniques prevent it?",
        "Overfitting occurs when a model memorizes noise in the training set and fails to generalize to unseen test data (indicated by 99% training accuracy but 75% test accuracy).\n"
        "Detection: We evaluated our model using Stratified 5-Fold Cross-Validation, ensuring that training and validation subsets maintain identical churn class distributions across all folds.\n"
        "Mitigation Techniques Applied:\n"
        "1. Tree Depth Limitation: Constrained max_depth to prevent individual trees from growing excessively deep.\n"
        "2. Minimum Samples Split/Leaf: Enforced min_samples_split=5 and min_samples_leaf=2 to ensure leaf nodes represent statistically meaningful customer segments.\n"
        "3. Ensemble Averaging: Bootstrapped sampling across 100+ trees averages out idiosyncratic variances.",
        "Always mention Stratified K-Fold: Standard K-Fold can accidentally create folds with zero churn cases if the dataset is small and imbalanced."
    )

    # ==========================================
    # SECTION 6: WEB APPLICATION & SYSTEM ARCHITECTURE
    # ==========================================
    add_section_header("6. Web Application & Backend Architecture")

    add_qa(
        16, "Explain the architecture of your Flask backend and how requests flow through the application.",
        "Our system utilizes an MVC (Model-View-Controller) pattern:\n"
        "1. Client Layer: Web browser rendering responsive HTML5, modern CSS variables, Chart.js visualizations, and asynchronous Fetch API requests.\n"
        "2. Routing & Controller Layer (app.py): Handles HTTP endpoints, session-based authentication decorators (@login_required, @admin_required), and input validation.\n"
        "3. Business & Analytics Logic (schema_mapper.py): Analyzes datasets, transforms input feature matrices, runs model inference, and calculates retention insights.\n"
        "4. Model Persistence (joblib): Pre-trained model binaries loaded into memory at startup to serve predictions with sub-millisecond latency.\n"
        "5. Persistence Layer (database.py): SQLAlchemy ORM providing transparent abstraction across SQLite (local development) and MySQL / PostgreSQL (production).",
        "Draw or describe the flow: User uploads CSV -> /api/upload_preview -> schema_mapper.fuzzy_match -> user maps -> /api/process_mapped_dataset -> model.predict_proba -> dashboard sync."
    )

    add_qa(
        17, "What is the difference between WSGI (Gunicorn) and Flask's built-in development server?",
        "Flask's built-in werkzeug server (app.run()) is single-threaded, synchronous, and intended exclusively for local debugging. "
        "It cannot handle concurrent connections, crashes easily under load, and poses security risks if exposed directly to the internet.\n"
        "Gunicorn (Green Unicorn) is a battle-tested Python WSGI (Web Server Gateway Interface) HTTP server for UNIX environments. "
        "It acts as a master process that manages worker processes and threads, pre-forking workers, handling worker timeouts, and binding to network sockets.",
        "In production, a reverse proxy (Nginx or Render's Envoy proxy) receives incoming HTTPS requests and forwards them to Gunicorn over HTTP."
    )

    add_qa(
        18, "Why did you use SQLAlchemy ORM instead of raw SQL queries?",
        "1. Database Independence: SQLAlchemy abstracts the underlying SQL dialect. The exact same Python code works seamlessly on SQLite during local development and on MySQL or PostgreSQL in production without changing SQL syntax.\n"
        "2. SQL Injection Prevention: SQLAlchemy uses parameterized queries and prepared statements by default, neutralizing SQL injection vulnerabilities.\n"
        "3. Object-Relational Mapping: Allows developers to interact with database records as standard Python objects (e.g., user = User(username='admin') instead of writing raw INSERT statements).\n"
        "4. Connection Pooling: Provides built-in connection pool management (pool_pre_ping=True) that detects dropped connections and automatically reconnects.",
        "Mention your database models: User, CustomerPrediction, BatchAnalyticsRun, and ModelRetrainLog."
    )

    # ==========================================
    # SECTION 7: CLOUD INTEGRATIONS & SECURITY
    # ==========================================
    add_section_header("7. Cloud Integrations, Firebase & Security")

    add_qa(
        19, "How is Firebase integrated into your application?",
        "We implemented a dual Firebase architecture:\n"
        "1. Firebase Admin SDK (Backend): Authenticates via service account credentials (supporting both local firebase_key.json and the FIREBASE_SERVICE_ACCOUNT_JSON environment variable for secure cloud deployment). It syncs high-risk customer predictions and batch analytics runs to Cloud Firestore in real time.\n"
        "2. Firebase Authentication (Frontend / SSO): Implements Google OAuth 2.0 Single Sign-On (SSO) on the login page via the Firebase Web SDK. When a user logs in with Google, the token is verified and the user account is provisioned in the database.",
        "Emphasize Twelve-Factor App security: Sensitive service account keys are injected via environment variables rather than hardcoded in source control."
    )

    add_qa(
        20, "How do you protect your web application against common security vulnerabilities (OWASP Top 10)?",
        "• Broken Access Control: Enforced strict role-based route decorators (@login_required, @admin_required) preventing unauthorized access to batch uploads or model retraining.\n"
        "• Sensitive Data Exposure: Password hashes, secret keys, and database credentials are read from environment variables; session cookies have HttpOnly=True and SameSite='Lax' enabled to mitigate XSS session hijacking.\n"
        "• SQL Injection: Eliminated by using SQLAlchemy ORM parameterized queries exclusively.\n"
        "• File Upload Safety: The batch upload wizard validates file extensions (.csv, .xlsx, .xls), sanitizes filenames, and saves files with cryptographically unique UUIDs (uuid.uuid4()) to prevent path traversal attacks.",
        "State that debug mode is strictly disabled in production (FLASK_DEBUG=false)."
    )

    # ==========================================
    # SECTION 8: DEPLOYMENT & DEVOPS
    # ==========================================
    add_section_header("8. Cloud Deployment, DevOps & Real-World Troubleshooting")

    add_qa(
        21, "Explain how you deployed the application on Render and resolved the HTTP ERROR 502 Bad Gateway.",
        "During testing on Render's Free Tier (512 MB RAM limit), the application encountered an HTTP 502 Bad Gateway error. We diagnosed and resolved two critical issues:\n"
        "1. Memory Exhaustion (OOM SIGKILL): When testing the 7,043-row Kaggle Telco dataset, the dashboard template attempted to compile 7,043 table rows plus 7,043 Bootstrap modals. This produced a 28 Megabyte HTML response, consuming >400 MB of heap memory and causing the Linux kernel to SIGKILL the Gunicorn worker. We solved this by capping the interactive table to the top 250 prioritized at-risk accounts (reducing HTML payload by 96.3% from 28MB to 1MB and rendering in 0.3s) while keeping the full 7,043 records in the CSV export and for all KPI calculations.\n"
        "2. Port Binding & Thread Optimization: Created a dedicated gunicorn.conf.py that dynamically binds to 0.0.0.0:$PORT. Configured workers=1 and threads=4: instead of running multiple heavy worker processes that duplicate model memory, a single process with multi-threading shares memory space, keeping RAM comfortably below 280 MB.",
        "This is an outstanding answer for an examiner: It shows real-world debugging, systems engineering, profiling, and production problem-solving beyond pure academic theory."
    )

    add_qa(
        22, "What is the role of the /health endpoint in cloud deployment?",
        "Cloud container orchestrators (like Render, AWS ECS, or Kubernetes) continuously send HTTP health checks to verify that a web service container is alive and responding. "
        "If a service takes too long to respond to a health check, the load balancer assumes the container is dead and returns a 502 Bad Gateway. "
        "We implemented a lightweight /health endpoint that bypasses database and heavy model scoring queries, immediately returning HTTP 200 with service status in <1ms. "
        "This allows the container to pass cloud health probes instantly.",
        "Endpoint: GET /health -> {'status': 'healthy', 'service': 'AadiBI', 'timestamp': '...'}"
    )

    # ==========================================
    # SECTION 9: BUSINESS RETENTION & SIMULATION
    # ==========================================
    add_section_header("9. Business Retention Strategies & What-If Simulation")

    add_qa(
        23, "Explain how the 'What-If Retention Simulator' works in your application.",
        "The What-If Simulator allows business executives to test retention strategies on high-risk customer accounts in real time:\n"
        "1. Baseline Evaluation: A customer profile with 85% churn probability is loaded (e.g., Month-to-month contract, no Tech Support, high monthly spend).\n"
        "2. Counterfactual Intervention: The user adjusts policy levers via the UI (e.g., offering a 1-year contract extension, bundling complimentary Tech Support, or providing a 15% discount).\n"
        "3. Live Re-scoring: The modified feature vector is passed to the ML pipeline via the /api/simulate endpoint. The model re-evaluates probabilities and calculates the Risk Delta:\n"
        "   Risk Delta = New Churn Probability - Original Churn Probability (e.g., 85% -> 22%, Delta: -63%).\n"
        "4. AI Copy Generation: Generates personalized executive retention outreach playbooks tailored to the customer's specific grievance.",
        "Demonstrate the business outcome: Shifting an account from Month-to-month to 1-Year contract with Tech Support slashes churn probability by >60%."
    )

    add_qa(
        24, "What are the key retention playbooks recommended by your system for different domains?",
        "• Telecom: High-bill and month-to-month subscribers are targeted with 1-year contract extensions paired with a 20% discount and free bundled Tech Support or streaming add-ons.\n"
        "• E-Commerce: Accounts with ≥2 support tickets and declining order frequency are triggered for priority customer service callback and ₹500 store credit.\n"
        "• SaaS: Enterprise tiers with >14 days since last login receive automated in-app guided product tours and executive Customer Success check-ins.\n"
        "• Banking: Inactive accounts with high balances are targeted with wealth management advisory and zero-fee credit card rewards.",
        "Prescriptive analytics bridges the gap between predictive modeling ('who will churn') and operational business strategy ('what should we do about it')."
    )

    # ==========================================
    # SECTION 10: ADVANCED / GRILL-ME QUESTIONS
    # ==========================================
    add_section_header("10. Advanced / 'Grill-Me' Technical Viva Traps")

    add_qa(
        25, "Examiner Trap: 'Why didn't you use XGBoost or LightGBM? Isn't XGBoost always better than Random Forest?'",
        "Counter-Answer: While XGBoost and LightGBM are powerful gradient boosting algorithms, Random Forest was deliberately chosen for this production system for three specific engineering reasons:\n"
        "1. Hyperparameter Sensitivity: Gradient Boosting sequentially builds trees to correct residual errors, making it highly sensitive to hyperparameters (learning rate, subsample, gamma, tree depth) and prone to rapid overfitting if not extensively tuned for each domain.\n"
        "2. Parallelization: Random Forest trees are completely independent and can be trained/evaluated in parallel across all CPU cores without sequential dependencies, ensuring rapid re-training in our web app.\n"
        "3. Robustness to Noisy/Uncleaned Inputs: In a self-service tool where users upload arbitrary datasets with varied distributions, Random Forest's bagging architecture provides superior resilience against out-of-distribution outliers and noisy features without requiring extensive hyperparameter grid search.",
        "Conclude: 'We also designed our ml_pipeline.py architecture to support modular model swapping, meaning XGBoost can be plugged in as an alternate estimator with zero changes to the web controller.'"
    )

    add_qa(
        26, "Examiner Trap: 'What is Concept Drift and Data Drift, and how does your system handle it in production?'",
        "Counter-Answer:\n"
        "• Data Drift: Occurs when the input feature distributions change over time (e.g., inflation increases average monthly spend from ₹2,000 to ₹4,000, or a competitor launches a fiber optic plan).\n"
        "• Concept Drift: Occurs when the statistical relationship between features and the target variable changes (e.g., customer service calls were previously the #1 churn driver, but now network outage frequency becomes the main driver).\n"
        "How AadiBI handles it: We engineered an Automated Model Retraining Pipeline (ml_pipeline.py and /api/retrain). Administrators can trigger retraining directly from the web interface using freshly uploaded customer datasets. The system re-evaluates accuracy, precision, recall, and ROC-AUC against a holdout test split, logs the benchmark results into the model_retrain_logs database table, and atomically replaces the active model artifact on disk only if performance thresholds are met.",
        "Emphasize the database audit trail: Every retrain event is logged with accuracy, precision, recall, F1, and dataset name."
    )

    add_qa(
        27, "Examiner Trap: 'What is Data Leakage, and how did you ensure it didn't occur during preprocessing?'",
        "Counter-Answer: Data Leakage occurs when information from the target variable or the test dataset is inadvertently shared with the training dataset during preprocessing (e.g., fitting a StandardScaler or imputer on the entire dataset before splitting).\n"
        "How we prevented it: We strictly split the dataset into train and test sets (train_test_split(..., test_size=0.2, stratify=y)) BEFORE fitting any scaler or imputer. Transformers are fit ONLY on the training data and then used to transform the test data. Furthermore, any post-churn attributes (e.g., cancellation survey results or churn timestamps) were excluded from feature matrices to ensure strictly predictive, pre-event modeling.",
        "Remember: Always fit on train, transform on test. Never fit on the whole dataset."
    )

    add_qa(
        28, "Examiner Trap: 'How do you interpret prediction confidence for an individual customer?'",
        "Counter-Answer: Rather than outputting a binary '0' or '1', model.predict_proba(X) calculates the proportion of trees in the forest that voted for the churn class. "
        "A predicted probability of 88.5% means that 88.5% of the ensemble trees independently classified that customer as a defector. "
        "We group these probabilities into intuitive, risk-tiered cohorts: Low Risk (<40%), Medium Risk (40%-69%), and High Risk (≥70%), "
        "enabling marketing teams to allocate retention budgets where they have the highest marginal return.",
        "Explain that high-probability accounts receive expensive human outreach, while low-risk accounts receive zero-cost automated nudges."
    )

    add_qa(
        29, "Examiner Trap: 'If you had another 3 months to work on this project, what would you add?'",
        "Counter-Answer: I would expand AadiBI in three directions:\n"
        "1. Survival Analysis (Time-to-Event Modeling): Implement Cox Proportional Hazards or Kaplan-Meier estimators to predict not just IF a customer will churn, but WHEN (expected time to churn in months), allowing even more precise lifecycle marketing.\n"
        "2. SHAP (SHapley Additive exPlanations): Integrate TreeSHAP to calculate exact, game-theoretic individual feature contributions for each single prediction modal, complementing our global feature importances.\n"
        "3. Automated CI/CD & Model Registry: Integrate MLflow or DVC (Data Version Control) to version control datasets and models, with automated canary deployments on Kubernetes.",
        "Examiners love forward-looking answers that demonstrate awareness of advanced enterprise ML architectures like SHAP and Survival Analysis."
    )

    doc.save(output_path)
    print(f"Viva document successfully generated at: {output_path}")

if __name__ == "__main__":
    out_file = os.path.join(os.path.dirname(__file__), "reports", "Customer_Churn_Viva_Comprehensive_Guide.docx")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    generate_viva_doc(out_file)
