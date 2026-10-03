"""
load_model.py
=============
Model Loading & Inference Engine for DETECT Multi-Modal Phishing Detection.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Union, List

import config
import preprocessing


def extract_feature_contributions(model, pipeline, sample_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Extracts top contributing text n-grams and structural features for linear/tree models.
    """
    X_vec = pipeline.transform([sample_text])
    feature_names = pipeline.feature_names_

    contributions = []
    if hasattr(model, "coef_"):
        coefs = model.coef_[0]
        X_arr = X_vec.toarray()[0]
        contrib_values = coefs * X_arr
        top_idx = np.argsort(contrib_values)[::-1][:top_k]

        for idx in top_idx:
            val = float(contrib_values[idx])
            if val > 0.001:
                feat_name = feature_names[idx]
                clean_name = feat_name.replace("aux_", "").replace("_", " ")
                contributions.append({
                    "feature": feat_name,
                    "readable_name": clean_name,
                    "contribution_score": round(val, 4),
                })

    elif hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        X_arr = X_vec.toarray()[0]
        active_idx = np.where(X_arr > 0)[0]
        active_importances = [(importances[i], feature_names[i]) for i in active_idx]
        active_importances.sort(reverse=True)

        for imp, feat_name in active_importances[:top_k]:
            clean_name = feat_name.replace("aux_", "").replace("_", " ")
            contributions.append({
                "feature": feat_name,
                "readable_name": clean_name,
                "contribution_score": round(float(imp), 4),
            })

    return contributions


def generate_explanation(label_str: str, probability: float, threshold: float, contributions: List[Dict[str, Any]], domain: str) -> str:
    """
    Generates a concise, plain-English explanation for predictions.
    Clear disclaimers are included to distinguish generic spam from targeted phishing.
    """
    is_phishing = probability >= threshold
    prob_pct = round(probability * 100, 2)
    th_pct = round(threshold * 100, 2)

    top_feats = [c["readable_name"] for c in contributions[:3]]
    feat_str = ", ".join(f"'{f}'" for f in top_feats) if top_feats else "lexical & syntactic patterns"

    if is_phishing:
        explanation = (
            f"This {domain} was flagged as {label_str} because its estimated phishing probability ({prob_pct}%) "
            f"exceeds the calibrated safety threshold ({th_pct}%). Key contributing factors include {feat_str}. "
            f"Note: High probability indicates suspicious attributes, but manual verification is recommended."
        )
    else:
        explanation = (
            f"This {domain} was classified as {label_str} with an estimated phishing probability ({prob_pct}%), "
            f"which remains safely below the threshold ({th_pct}%)."
        )

    if domain == "SMS" and is_phishing:
        explanation += " Disclaimer: Generic SMS spam may share characteristics with phishing."

    return explanation


class MultiModalPhishingDetector:
    """
    Unified multi-modal classifier loading separate SMS, Email, and URL pipelines.
    """

    def __init__(
        self,
        sms_model_path: str = str(config.SMS_MODEL_PATH),
        email_model_path: str = str(config.EMAIL_MODEL_PATH),
        url_model_path: str = str(config.URL_MODEL_PATH),
    ):
        self.sms_pkg = self._load_package(sms_model_path, "SMS")
        self.email_pkg = self._load_package(email_model_path, "Email")
        self.url_pkg = self._load_package(url_model_path, "URL")

    def _load_package(self, path: str, name: str) -> Dict[str, Any]:
        if os.path.exists(path):
            try:
                pkg = joblib.load(path)
                print(f"[Loader] Loaded {name} model pipeline from: {path}")
                return pkg
            except Exception as e:
                print(f"[Warning] Failed to load {name} model from {path}: {e}")
                return None
        else:
            print(f"[Warning] {name} model file not found at: {path}")
            return None

    def predict_sms(self, message: str) -> Dict[str, Any]:
        if not self.sms_pkg:
            raise RuntimeError("SMS model pipeline is not loaded.")

        clean_msg = preprocessing.clean_text(message)
        pipeline = self.sms_pkg["pipeline"]
        model = self.sms_pkg["model"]
        threshold = self.sms_pkg["tuned_threshold"]

        X_vec = pipeline.transform([clean_msg])
        prob = float(model.predict_proba(X_vec)[:, 1][0])
        pred_label = 1 if prob >= threshold else 0
        label_str = config.SMS_LABEL_MAP.get(pred_label, "Unknown")

        contributions = extract_feature_contributions(model, pipeline, clean_msg)
        explanation = generate_explanation(label_str, prob, threshold, contributions, "SMS")

        return {
            "domain": "SMS",
            "raw_input": message,
            "cleaned_input": clean_msg,
            "predicted_class": pred_label,
            "predicted_label": label_str,
            "probability": round(prob, 4),
            "probability_percentage": f"{round(prob * 100, 2)}%",
            "selected_threshold": round(threshold, 4),
            "is_phishing_or_suspicious": bool(pred_label == 1),
            "contributing_features": contributions,
            "explanation": explanation,
        }

    def predict_email(self, sender: str = "", subject: str = "", body: str = "", raw_text: str = "") -> Dict[str, Any]:
        if not self.email_pkg:
            raise RuntimeError("Email model pipeline is not loaded.")

        if raw_text:
            clean_email_str = preprocessing.clean_text(raw_text)
        else:
            clean_email_str = preprocessing.clean_email_components(sender, subject, body)

        pipeline = self.email_pkg["pipeline"]
        model = self.email_pkg["model"]
        threshold = self.email_pkg["tuned_threshold"]

        X_vec = pipeline.transform([clean_email_str])
        prob = float(model.predict_proba(X_vec)[:, 1][0])
        pred_label = 1 if prob >= threshold else 0
        label_str = config.EMAIL_LABEL_MAP.get(pred_label, "Unknown")

        contributions = extract_feature_contributions(model, pipeline, clean_email_str)
        explanation = generate_explanation(label_str, prob, threshold, contributions, "Email")

        return {
            "domain": "Email",
            "raw_input": {"sender": sender, "subject": subject, "body": body, "raw_text": raw_text},
            "cleaned_input": clean_email_str,
            "predicted_class": pred_label,
            "predicted_label": label_str,
            "probability": round(prob, 4),
            "probability_percentage": f"{round(prob * 100, 2)}%",
            "selected_threshold": round(threshold, 4),
            "is_phishing": bool(pred_label == 1),
            "contributing_features": contributions,
            "explanation": explanation,
        }


def load_all_models() -> MultiModalPhishingDetector:
    return MultiModalPhishingDetector()
