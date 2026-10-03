"""
train_email.py
==============
Training, Threshold Tuning, and Model Selection Pipeline for Email Phishing Detection.
"""

import os
import json
import warnings
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

import config
import preprocessing
from train_sms import tune_classification_threshold, compute_metrics

warnings.filterwarnings("ignore")


def train_email_pipeline():
    print("=" * 60)
    print("      DETECT: EMAIL PHISHING TRAINING PIPELINE           ")
    print("=" * 60)

    # 1. Load Data
    email_dedup, raw_stats = preprocessing.load_email_dataset()
    print(f"[Dataset] Email Total Records: {raw_stats['total_records']}, Unique Records: {raw_stats['deduplicated_records']}")
    print(f"[Dataset] Label Distribution: Legitimate={raw_stats['label_counts'].get(0, 0)}, Phishing={raw_stats['label_counts'].get(1, 0)}")

    # 2. Group-Stratified Split (Leakage Free)
    train_df, val_df, test_df = preprocessing.group_stratified_split(email_dedup)
    print(f"[Split] Train: {len(train_df)}, Validation: {len(val_df)}, Test: {len(test_df)}")

    # 3. Fit Preprocessing Pipeline ON TRAIN ONLY
    pipeline = preprocessing.PhishingFeaturePipeline(
        ngram_range=config.TFIDF_PARAMS["ngram_range"],
        min_df=config.TFIDF_PARAMS["min_df"],
        sublinear_tf=config.TFIDF_PARAMS["sublinear_tf"],
    )
    X_train = pipeline.fit_transform(train_df["text"])
    X_val = pipeline.transform(val_df["text"])
    X_test = pipeline.transform(test_df["text"])

    y_train = train_df["label"].values
    y_val = val_df["label"].values
    y_test = test_df["label"].values

    # 4. Define Candidate Models
    models = {
        "Logistic Regression": LogisticRegression(random_state=config.RANDOM_STATE, C=1.0, max_iter=1000, solver="liblinear"),
        "Linear SVM": CalibratedClassifierCV(
            LinearSVC(random_state=config.RANDOM_STATE, max_iter=2000, C=1.0), cv=2
        ),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=config.RANDOM_STATE, max_depth=10),
        "XGBoost": XGBClassifier(n_estimators=100, random_state=config.RANDOM_STATE, eval_metric="logloss", max_depth=4, learning_rate=0.1),
    }

    results = {}
    best_model_name = None
    best_val_f1 = -1.0
    best_model_obj = None
    best_tuned_threshold = config.DEFAULT_THRESHOLD

    # 5. Train & Evaluate on Validation Set
    for name, model in models.items():
        print(f"\n--- Training {name} ---")
        model.fit(X_train, y_train)

        val_probs = model.predict_proba(X_val)[:, 1]
        test_probs = model.predict_proba(X_test)[:, 1]

        # Tune Threshold on Validation
        tuned_th, target_achieved, val_rec_at_th, val_fpr_at_th = tune_classification_threshold(y_val, val_probs)

        # Default vs Tuned Metrics on Validation
        val_default_metrics = compute_metrics(y_val, val_probs, threshold=config.DEFAULT_THRESHOLD)
        val_tuned_metrics = compute_metrics(y_val, val_probs, threshold=tuned_th)

        # Metrics on Held-out Test Set (Untouched during tuning)
        test_default_metrics = compute_metrics(y_test, test_probs, threshold=config.DEFAULT_THRESHOLD)
        test_tuned_metrics = compute_metrics(y_test, test_probs, threshold=tuned_th)

        results[name] = {
            "val_probs": val_probs.tolist(),
            "test_probs": test_probs.tolist(),
            "tuned_threshold": tuned_th,
            "target_recall_achieved": target_achieved,
            "val_default_metrics": val_default_metrics,
            "val_tuned_metrics": val_tuned_metrics,
            "test_default_metrics": test_default_metrics,
            "test_tuned_metrics": test_tuned_metrics,
        }

        print(f"Validation F1 (Default 0.5): {val_default_metrics['f1_score']:.2f}% | FPR: {val_default_metrics['fpr']:.2f}%")
        print(f"Validation F1 (Tuned {tuned_th:.4f}): {val_tuned_metrics['f1_score']:.2f}% | FPR: {val_tuned_metrics['fpr']:.2f}% | Recall Target (>=95%) Achieved: {target_achieved}")

        if val_tuned_metrics["f1_score"] > best_val_f1:
            best_val_f1 = val_tuned_metrics["f1_score"]
            best_model_name = name
            best_model_obj = model
            best_tuned_threshold = tuned_th

    print(f"\n[Model Selection] Best Email Model: {best_model_name} (Val F1: {best_val_f1:.2f}%, Tuned Threshold: {best_tuned_threshold:.4f})")

    # 6. Save Pipeline & Metadata
    email_package = {
        "model_name": best_model_name,
        "model": best_model_obj,
        "pipeline": pipeline,
        "tuned_threshold": best_tuned_threshold,
        "label_mapping": config.EMAIL_LABEL_MAP,
        "feature_names": pipeline.feature_names_,
        "trained_at": datetime.now().isoformat(),
        "dataset_stats": raw_stats,
        "split_counts": {"train": len(train_df), "val": len(val_df), "test": len(test_df)},
        "val_results": results[best_model_name]["val_tuned_metrics"],
        "test_results": results[best_model_name]["test_tuned_metrics"],
    }

    joblib.dump(email_package, config.EMAIL_MODEL_PATH)
    os.makedirs(os.path.dirname(config.ML_SAVED_EMAIL_PATH), exist_ok=True)
    joblib.dump(email_package, config.ML_SAVED_EMAIL_PATH)
    print(f"[Model Saved] Saved best Email pipeline to {config.EMAIL_MODEL_PATH}")

    # Save summary metrics JSON
    metrics_export = {
        "timestamp": datetime.now().isoformat(),
        "selected_model": best_model_name,
        "selected_threshold": best_tuned_threshold,
        "dataset_info": raw_stats,
        "splits": {"train": len(train_df), "val": len(val_df), "test": len(test_df)},
        "all_models": {
            k: {
                "val_probs": v["val_probs"],
                "test_probs": v["test_probs"],
                "tuned_threshold": v["tuned_threshold"],
                "target_recall_achieved": v["target_recall_achieved"],
                "val_default_metrics": v["val_default_metrics"],
                "val_tuned_metrics": v["val_tuned_metrics"],
                "test_default_metrics": v["test_default_metrics"],
                "test_tuned_metrics": v["test_tuned_metrics"],
            }
            for k, v in results.items()
        },
    }

    with open(config.METRICS_DIR / "email_metrics.json", "w") as f:
        json.dump(metrics_export, f, indent=2)

    print(f"[Metrics Exported] Saved Email evaluation metrics to {config.METRICS_DIR / 'email_metrics.json'}")
    return email_package, results, (train_df, val_df, test_df)


if __name__ == "__main__":
    train_email_pipeline()
