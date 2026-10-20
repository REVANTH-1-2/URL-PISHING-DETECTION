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
    sms_obj = joblib.load("ml/saved_models/sms/best_model.pkl")
    if isinstance(sms_obj, dict):
        sms_model = sms_obj["model"]
        sms_vec = sms_obj.get("pipeline", joblib.load("ml/saved_models/sms/vectorizer.pkl"))
        sms_th = sms_obj.get("tuned_threshold", 0.5)
    else:
        sms_model = sms_obj
        sms_vec = joblib.load("ml/saved_models/sms/vectorizer.pkl")
        sms_th = 0.5

    # Load locked Email model & vectorizer
    email_obj = joblib.load("ml/saved_models/email/best_model.pkl")
    if isinstance(email_obj, dict):
        email_model = email_obj["model"]
        email_vec = email_obj.get("pipeline", joblib.load("ml/saved_models/email/vectorizer.pkl"))
        email_th = email_obj.get("tuned_threshold", 0.5)
    else:
        email_model = email_obj
        email_vec = joblib.load("ml/saved_models/email/vectorizer.pkl")
        email_th = 0.5

    # Load locked URL model & scaler
    url_model = joblib.load("ml/saved_models/url/best_model.pkl")
    url_scaler = joblib.load("ml/saved_models/url/scaler.pkl")

    # 1. SMS Real World Samples
    with open("tests/real_world_samples/sms_samples.json") as f:
        sms_samples = json.load(f)
    print(f"\n--- Testing {len(sms_samples)} Real-World SMS Samples ---")
    for sample in sms_samples:
        X = sms_vec.transform([sample["message"]])
        prob = float(sms_model.predict_proba(X)[0][1]) if hasattr(sms_model, "predict_proba") else float(sms_model.predict(X)[0])
        pred_label = "PHISHING" if prob >= sms_th else "SAFE"
        print(f"[{sample['id']}] Category: {sample['category']} | Expected: {sample['expected_label']} | Predicted: {pred_label} (Prob: {prob:.2f})")
        assert pred_label == sample["expected_label"], f"SMS sample {sample['id']} prediction '{pred_label}' does not match expected '{sample['expected_label']}'"

    # 2. Email Real World Samples
    with open("tests/real_world_samples/email_samples.json") as f:
        email_samples = json.load(f)
    print(f"\n--- Testing {len(email_samples)} Real-World Email Samples ---")
    for sample in email_samples:
        parts = []
        if sample.get("sender"):
            parts.append(f"Sender: {sample['sender']}")
        if sample.get("subject"):
            parts.append(f"Subject: {sample['subject']}")
        if sample.get("body"):
            parts.append(f"Body: {sample['body']}")
        text = " | ".join(parts) if parts else sample.get("body", "")

        X = email_vec.transform([text])
        prob = float(email_model.predict_proba(X)[0][1]) if hasattr(email_model, "predict_proba") else float(email_model.predict(X)[0])
        pred_label = "PHISHING" if prob >= email_th else "SAFE"
        print(f"[{sample['id']}] Category: {sample['category']} | Expected: {sample['expected_label']} | Predicted: {pred_label} (Prob: {prob:.2f})")
        assert pred_label == sample["expected_label"], f"Email sample {sample['id']} prediction '{pred_label}' does not match expected '{sample['expected_label']}'"

    # 3. URL Real World Samples
    with open("tests/real_world_samples/url_samples.json") as f:
        url_samples = json.load(f)
    print(f"\n--- Testing {len(url_samples)} Real-World URL Samples ---")
    for sample in url_samples:
        feats = np.array([list(extract_url_features(sample["url"]).values())])
        X = url_scaler.transform(feats)
        prob = float(url_model.predict_proba(X)[0][1]) if hasattr(url_model, "predict_proba") else float(url_model.predict(X)[0])
        pred_label = "PHISHING" if prob >= 0.5 else "SAFE"
        print(f"[{sample['id']}] Category: {sample['category']} | Expected: {sample['expected_label']} | Predicted: {pred_label} (Prob: {prob:.2f})")
        assert pred_label == sample["expected_label"], f"URL sample {sample['id']} prediction '{pred_label}' does not match expected '{sample['expected_label']}'"

    print("\n==================================================")
    print("REAL-WORLD SAMPLE TESTING COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    test_real_world_samples()
