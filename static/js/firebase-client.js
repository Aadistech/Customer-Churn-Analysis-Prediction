/**
 * AadiBI Customer Churn Intelligence - Firebase Modular Client SDK (Auth & Firestore)
 */

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { getFirestore, collection, doc, addDoc, onSnapshot, query, orderBy, limit, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

// Firebase App Web Configuration
const firebaseConfig = {
  apiKey: "AIzaSyBoc5JX-FLOBiHDpH1g6A5Pr2o5s2asz8c",
  authDomain: "customer-churn-analysis-c3be6.firebaseapp.com",
  projectId: "customer-churn-analysis-c3be6",
  storageBucket: "customer-churn-analysis-c3be6.firebasestorage.app",
  messagingSenderId: "351385399138",
  appId: "1:351385399138:web:506a3cbafbd2798db7c63b",
  measurementId: "G-X459FWNH1H"
};

// Initialize Firebase App, Auth & Firestore
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const googleProvider = new GoogleAuthProvider();

console.log("🔥 Firebase Modular Client SDK Initialized! Auth & Cloud Firestore Connected.");

// Attach Firebase Service utilities to window.AadiFirebase
window.AadiFirebase = {
  app,
  auth,
  db,
  googleProvider,
  signInWithPopup,

  /**
   * Listen to real-time Cloud Firestore prediction documents
   */
  listenToPredictions(callback) {
    try {
      const q = query(collection(db, "churn_predictions"), orderBy("timestamp", "desc"), limit(25));
      return onSnapshot(q, (snapshot) => {
        const docs = [];
        snapshot.forEach((docSnap) => {
          docs.push({ id: docSnap.id, ...docSnap.data() });
        });
        if (typeof callback === 'function') callback(docs);
      }, (err) => {
        console.warn("[Firestore Client Real-time Warning]:", err.message);
      });
    } catch (e) {
      console.error("[Firestore Listen Error]:", e.message);
    }
  },

  /**
   * Listen to real-time Cloud Firestore executive summary document
   */
  listenToAnalytics(callback) {
    try {
      const docRef = doc(db, "churn_analytics", "latest_summary");
      return onSnapshot(docRef, (docSnap) => {
        if (docSnap.exists() && typeof callback === 'function') {
          callback(docSnap.data());
        }
      }, (err) => {
        console.warn("[Firestore Analytics Warning]:", err.message);
      });
    } catch (e) {
      console.error("[Firestore Analytics Error]:", e.message);
    }
  },

  /**
   * Save single customer risk prediction directly into Cloud Firestore
   */
  async savePrediction(data) {
    try {
      const docRef = await addDoc(collection(db, "churn_predictions"), {
        ...data,
        timestamp: serverTimestamp()
      });
      console.log("[OK] Saved prediction to Firestore. Doc ID:", docRef.id);
      return docRef.id;
    } catch (e) {
      console.error("[Firestore Save Error]:", e.message);
      return null;
    }
  }
};
