const express = require('express');
const path = require('path');
const fs = require('fs');
const cors = require('cors');
const multer = require('multer');
const { runPythonPrediction } = require('./services/pythonService');
const { 
  isFirebaseInitialized, 
  savePredictionToFirestore, 
  saveAnalyticsToFirestore 
} = require('./services/firebaseService');

// Initialize Node.js Express App
const app = express();
const PORT = process.env.PORT || 3000;

// Configure Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static frontend assets (CSS, JS, Images)
app.use('/static', express.static(path.join(__dirname, 'static')));

// Configure Multer for File Uploads
const upload = multer({ dest: path.join(__dirname, 'uploads/') });

// ============================================================
// HEALTH CHECK ENDPOINT
// ============================================================
app.get('/health', (req, res) => {
  res.json({
    status: 'online',
    system: 'AadiBI Customer Churn Intelligence System',
    runtime: 'Node.js v' + process.version,
    firebaseConnected: isFirebaseInitialized(),
    projectId: 'customer-churn-dc52d',
    timestamp: new Date().toISOString()
  });
});

// ============================================================
// GOOGLE AUTHENTICATION SESSION ENDPOINT
// ============================================================
app.post('/api/auth/google_login', (req, res) => {
  try {
    const { uid, displayName, email, photoURL } = req.body || {};
    res.json({
      success: true,
      user: {
        uid,
        displayName: displayName || email.split('@')[0],
        email,
        photoURL,
        role: 'admin'
      },
      redirect: '/dashboard'
    });
  } catch (error) {
    res.status(400).json({ success: false, error: error.message });
  }
});

// ============================================================
// REST API ENDPOINTS WITH FIREBASE CLOUD SYNC
// ============================================================

/**
 * POST /api/predict
 * Real-time AJAX single customer prediction endpoint with Firestore persistence
 */
app.post('/api/predict', async (req, res) => {
  try {
    const payload = req.body;
    const result = await runPythonPrediction(payload);
    
    // Asynchronously sync prediction record to Firebase Cloud Firestore
    if (result && result.success) {
      savePredictionToFirestore({
        inputs: payload,
        prediction: result.prediction,
        churn_probability: result.churn_probability,
        risk_level: result.risk_level,
        drivers: result.drivers,
        recommendation: result.recommendation
      }).catch(err => console.error('Background Firebase Sync Error:', err.message));
    }

    res.json(result);
  } catch (error) {
    console.error('[Node.js API Error]:', error.message);
    res.status(400).json({ success: false, error: error.message });
  }
});

/**
 * GET /api/sample_csv
 * Downloadable sample dataset CSV endpoint
 */
app.get('/api/sample_csv', (req, res) => {
  const sampleCSV = `State,Account length,Area code,International plan,Voice mail plan,Number vmail messages,Total day minutes,Total day calls,Total day charge,Total eve minutes,Total eve calls,Total eve charge,Total night minutes,Total night calls,Total night charge,Total intl minutes,Total intl calls,Total intl charge,Customer service calls
KS,128,415,no,yes,25,265.1,110,45.07,197.4,99,16.78,244.7,91,11.01,10.0,3,2.70,1
OH,107,415,no,yes,26,161.6,123,27.47,195.5,103,16.62,254.4,103,11.45,13.7,3,3.70,1
NJ,137,415,no,no,0,243.4,114,41.38,121.2,110,10.30,162.6,104,7.32,12.2,5,3.29,0`;

  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', 'attachment; filename="sample_customer_churn_dataset.csv"');
  res.send(sampleCSV);
});

// ============================================================
// PROXY / VIEW ROUTES TO FLASK OR HTML
// ============================================================
app.get('*', (req, res) => {
  const fbStatus = isFirebaseInitialized() ? 'CONNECTED 🔥' : 'OFFLINE ⚠️';
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>AadiBI Node.js Gateway</title>
      <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
      <div class="container" style="max-width: 650px; margin-top: 4rem; text-align: center;">
        <div class="card">
          <div class="badge badge-success" style="margin-bottom: 1rem;">FIREBASE GOOGLE AUTH & CLOUD FIRESTORE ACTIVE</div>
          <h2 class="text-gradient" style="font-size: 1.8rem; margin-bottom: 0.5rem;">Node.js Express Server Online</h2>
          <p style="color: var(--text-muted); margin-bottom: 1.5rem;">
            Node.js API Gateway (v${process.version}) is active with Firebase Web Auth Project <strong>customer-churn-dc52d</strong>.
          </p>
          <div style="display: flex; gap: 0.75rem; justify-content: center;">
            <a href="http://127.0.0.1:5000" class="btn btn-primary">🚀 Launch Flask UI Dashboard</a>
            <a href="/health" class="btn btn-outline">💚 Node & Firebase Health API</a>
          </div>
        </div>
      </div>
    </body>
    </html>
  `);
});

// Start Node.js Express Server
app.listen(PORT, () => {
  console.log('\n======================================================');
  console.log(`🟢 AadiBI Node.js Express API Server Running!`);
  console.log(`   Node.js Server URL: http://localhost:${PORT}`);
  console.log(`   Firebase Web App:   customer-churn-dc52d`);
  console.log('======================================================\n');
});
