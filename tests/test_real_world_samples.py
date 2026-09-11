import os
import sys
import json
import joblib
import numpy as np

# Ensure path includes project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.features.extractor import extract_url_features
from ml.explainability.xai_engine import XAIEngine

def test_real_world_samples():
    print("==================================================")
    print("RUNNING REAL-WORLD UNSEEN SAMPLE TEST SUITE")
    print("==================================================")

    # Load locked SMS model & vectorizer
    sms_model = joblib.load("ml/saved_models/sms/best_model.pkl")
    sms_vec = joblib.load("ml/saved_models/sms/vectorizer.pkl")

    # Load locked Email model & vectorizer
    email_model = joblib.load("ml/saved_models/email/best_model.pkl")
    email_vec = joblib.load("ml/saved_models/email/vectorizer.pkl")

    # Load locked URL model & scaler
    url_model = joblib.load("ml/saved_models/url/best_model.pkl")
    url_scaler = joblib.load("ml/saved_models/url/scaler.pkl")

    # 1. SMS Real World Samples
    with open("tests/real_world_samples/sms_samples.json") as f:
        sms_samples = json.load(f)
    print(f"\n--- Testing {len(sms_samples)} Real-World SMS Samples ---")
    for sample in sms_samples:
        X = sms_vec.transform([sample["message"]]).toarray()
        pred = sms_model.predict(X)[0]
        prob = sms_model.predict_proba(X)[0][1] if hasattr(sms_model, "predict_proba") else pred
        pred_label = "PHISHING" if prob >= 0.5 else "SAFE"
        print(f"[{sample['id']}] Category: {sample['category']} | Expected: {sample['expected_label']} | Predicted: {pred_label} (Prob: {prob:.2f})")

    # 2. Email Real World Samples
    with open("tests/real_world_samples/email_samples.json") as f:
        email_samples = json.load(f)
    print(f"\n--- Testing {len(email_samples)} Real-World Email Samples ---")
    for sample in email_samples:
        text = f"{sample.get('subject', '')} {sample['body']}"
        X = email_vec.transform([text]).toarray()
        pred = email_model.predict(X)[0]
        prob = email_model.predict_proba(X)[0][1] if hasattr(email_model, "predict_proba") else pred
        pred_label = "PHISHING" if prob >= 0.5 else "SAFE"
        print(f"[{sample['id']}] Category: {sample['category']} | Expected: {sample['expected_label']} | Predicted: {pred_label} (Prob: {prob:.2f})")

    # 3. URL Real World Samples
    with open("tests/real_world_samples/url_samples.json") as f:
        url_samples = json.load(f)
    print(f"\n--- Testing {len(url_samples)} Real-World URL Samples ---")
    for sample in url_samples:
        feats = np.array([list(extract_url_features(sample["url"]).values())])
        X = url_scaler.transform(feats)
        pred = url_model.predict(X)[0]
        prob = url_model.predict_proba(X)[0][1] if hasattr(url_model, "predict_proba") else pred
        pred_label = "PHISHING" if prob >= 0.5 else "SAFE"
        print(f"[{sample['id']}] Category: {sample['category']} | Expected: {sample['expected_label']} | Predicted: {pred_label} (Prob: {prob:.2f})")

    print("\n==================================================")
    print("REAL-WORLD SAMPLE TESTING COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    test_real_world_samples()
