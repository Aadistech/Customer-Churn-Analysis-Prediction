const admin = require('firebase-admin');
const { getFirestore } = require('firebase-admin/firestore');
const path = require('path');
const fs = require('fs');

let db = null;
let isFirebaseInitialized = false;

// Path to Service Account JSON key
const KEY_PATH = path.join(__dirname, '..', 'firebase_key.json');

try {
  if (fs.existsSync(KEY_PATH)) {
    const serviceAccount = JSON.parse(fs.readFileSync(KEY_PATH, 'utf8'));
    
    if (admin.getApps().length === 0) {
      admin.initializeApp({
        credential: admin.cert(serviceAccount),
        projectId: serviceAccount.project_id || 'customer-churn-analysis-c3be6'
      });
    }

    db = getFirestore();
    isFirebaseInitialized = true;
    console.log(`[OK] Firebase Cloud Firestore Initialized! Project ID: ${serviceAccount.project_id}`);
  } else {
    console.warn(`[WARN] Firebase key file not found at ${KEY_PATH}. Running in offline fallback mode.`);
  }
} catch (error) {
  console.error('[ERROR] Failed to initialize Firebase Admin SDK:', error.message);
}

/**
 * Save Single Prediction Record to Firestore
 */
async function savePredictionToFirestore(predictionData) {
  if (!isFirebaseInitialized || !db) {
    return { success: false, reason: 'Firebase not configured' };
  }

  try {
    const docRef = db.collection('churn_predictions').doc();
    const payload = {
      ...predictionData,
      createdAt: new Date().toISOString(),
      docId: docRef.id
    };

    await docRef.set(payload);
    return { success: true, docId: docRef.id };
  } catch (error) {
    console.error('[Firebase Firestore Save Error]:', error.message);
    return { success: false, error: error.message };
  }
}

/**
 * Update Churn Analytics Summary in Firestore
 */
async function saveAnalyticsToFirestore(summary) {
  if (!isFirebaseInitialized || !db) return;

  try {
    const docRef = db.collection('churn_analytics').doc('latest_summary');
    await docRef.set({
      ...summary,
      updatedAt: new Date().toISOString()
    }, { merge: true });
  } catch (error) {
    console.error('[Firebase Firestore Analytics Error]:', error.message);
  }
}

module.exports = {
  isFirebaseInitialized: () => isFirebaseInitialized,
  savePredictionToFirestore,
  saveAnalyticsToFirestore
};
