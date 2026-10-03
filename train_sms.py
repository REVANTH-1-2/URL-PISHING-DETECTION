"""
train_sms.py
============
Training, Threshold Tuning, and Model Selection Pipeline for SMS Phishing / Spam Detection.
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

warnings.filterwarnings("ignore")


def tune_classification_threshold(y_val, y_val_prob, target_recall=config.TARGET_MIN_RECALL):
    """
    Tunes the classification threshold on validation data to minimize False Positive Rate (FPR)
    while maintaining a minimum target phishing recall (default 95%).
    Returns: tuned_threshold, target_achieved, recall_at_th, fpr_at_th
    """
    candidate_thresholds = np.linspace(0.01, 0.99, 100)
    best_th = config.DEFAULT_THRESHOLD
    min_fpr = 1.0
    best_recall = 0.0
    target_achieved = False

    valid_candidates = []
    for th in candidate_thresholds:
        preds = (y_val_prob >= th).astype(int)
        cm = confusion_matrix(y_val, preds, labels=[0, 1])
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
        else:
            tn, fp, fn, tp = int(cm[0, 0]), 0, 0, 0

        rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

        if rec >= target_recall:
            valid_candidates.append((fpr, -rec, th))
            target_achieved = True

    if valid_candidates:
        valid_candidates.sort()
        min_fpr = valid_candidates[0][0]
        best_recall = -valid_candidates[0][1]
        best_th = float(valid_candidates[0][2])
    else:
        all_candidates = []
        for th in candidate_thresholds:
            preds = (y_val_prob >= th).astype(int)
            cm = confusion_matrix(y_val, preds, labels=[0, 1])
            tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (int(cm[0, 0]), 0, 0, 0)
            rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
            fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
            all_candidates.append((-rec, fpr, th))
        all_candidates.sort()
        best_recall = -all_candidates[0][0]
        min_fpr = all_candidates[0][1]
        best_th = float(all_candidates[0][2])

    return best_th, target_achieved, best_recall, min_fpr


def compute_metrics(y_true, y_prob, threshold=0.5):
    y_pred = (y_prob >= threshold).astype(int)
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = 0.5

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
    else:
        tn, fp, fn, tp = int(cm[0, 0]), 0, 0, 0

    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    return {
        "accuracy": round(acc * 100, 2),
        "precision": round(prec * 100, 2),
        "recall": round(rec * 100, 2),
        "specificity": round(specificity * 100, 2),
        "f1_score": round(f1 * 100, 2),
        "roc_auc": round(roc_auc, 4),
        "fpr": round(fpr * 100, 2),
        "fnr": round(fnr * 100, 2),
        "confusion_matrix": cm.tolist(),
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
    }


def train_sms_pipeline():
    print("=" * 60)
    print("      DETECT: SMS PHISHING / SPAM TRAINING PIPELINE      ")
    print("=" * 60)

    # 1. Load Data
    sms_dedup, raw_stats = preprocessing.load_sms_dataset()
    print(f"[Dataset] SMS Total Records: {raw_stats['total_records']}, Unique Records: {raw_stats['deduplicated_records']}")
    print(f"[Dataset] Label Distribution: Legitimate={raw_stats['label_counts'].get(0, 0)}, Spam/Phishing={raw_stats['label_counts'].get(1, 0)}")

    # 2. Group-Stratified Split (Leakage Free)
    train_df, val_df, test_df = preprocessing.group_stratified_split(sms_dedup)
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
            LinearSVC(random_state=config.RANDOM_STATE, max_iter=2000, C=1.0), cv=3
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

    print(f"\n[Model Selection] Best SMS Model: {best_model_name} (Val F1: {best_val_f1:.2f}%, Tuned Threshold: {best_tuned_threshold:.4f})")

    # 6. Save Pipeline & Metadata
    sms_package = {
        "model_name": best_model_name,
        "model": best_model_obj,
        "pipeline": pipeline,
        "tuned_threshold": best_tuned_threshold,
        "label_mapping": config.SMS_LABEL_MAP,
        "feature_names": pipeline.feature_names_,
        "trained_at": datetime.now().isoformat(),
        "dataset_stats": raw_stats,
        "split_counts": {"train": len(train_df), "val": len(val_df), "test": len(test_df)},
        "val_results": results[best_model_name]["val_tuned_metrics"],
        "test_results": results[best_model_name]["test_tuned_metrics"],
    }

    joblib.dump(sms_package, config.SMS_MODEL_PATH)
    os.makedirs(os.path.dirname(config.ML_SAVED_SMS_PATH), exist_ok=True)
    joblib.dump(sms_package, config.ML_SAVED_SMS_PATH)
    print(f"[Model Saved] Saved best SMS pipeline to {config.SMS_MODEL_PATH}")

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

    with open(config.METRICS_DIR / "sms_metrics.json", "w") as f:
        json.dump(metrics_export, f, indent=2)

    print(f"[Metrics Exported] Saved SMS evaluation metrics to {config.METRICS_DIR / 'sms_metrics.json'}")
    return sms_package, results, (train_df, val_df, test_df)


if __name__ == "__main__":
    train_sms_pipeline()
