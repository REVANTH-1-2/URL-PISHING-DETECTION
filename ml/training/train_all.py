"""
train_all.py
============
URL-only phishing detection training pipeline.

Strategy
--------
1. Load URL dataset (real CSV or synthetic fallback).
2. Extract 35 hand-engineered features per URL.
3. 70 / 15 / 15 stratified split (train / val / unseen-test).
4. Fit StandardScaler on training data only (leakage-free).
5. Hyper-parameter search (GridSearchCV, 5-fold StratifiedKFold) for:
   - XGBoostClassifier
   - RandomForestClassifier
6. Soft-voting VotingClassifier ensemble (XGBoost + RF + LR).
7. Select best single model + ensemble via validation F1.
8. Final evaluation on the locked unseen test set.
9. Log top-10 feature importances.
10. Save best model, scaler, and JSON report.
"""

import os
import sys
import json
import warnings
# pyrefly: ignore [missing-import]
import joblib
# pyrefly: ignore [missing-import]
import numpy as np
import pandas as pd
from datetime import datetime

warnings.filterwarnings("ignore")

# ── sklearn ──────────────────────────────────────────────────────────────────
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

# ── XGBoost ──────────────────────────────────────────────────────────────────
try:
    # pyrefly: ignore [missing-import]
    import xgboost as xgb
    XGB_AVAILABLE = True
except Exception:
    XGB_AVAILABLE = False
    print("[Warning] XGBoost not installed — using GradientBoostingClassifier instead.")

# ── Project imports ───────────────────────────────────────────────────────────
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ml.datasets.loader import load_url_dataset, inspect_dataset, create_url_readme
from ml.preprocessing.pipeline import get_train_val_test_split, LeakageFreeTabularPipeline
from ml.features.extractor import extract_url_features

# ── CV config ────────────────────────────────────────────────────────────────
CV_FOLDS = 5
RANDOM_STATE = 42


# ─────────────────────────────────────────────────────────────────────────────
def compute_detailed_metrics(y_true, y_pred, y_prob) -> dict:
    acc   = float(accuracy_score(y_true, y_pred))
    prec  = float(precision_score(y_true, y_pred, zero_division=0))
    rec   = float(recall_score(y_true, y_pred, zero_division=0))
    f1    = float(f1_score(y_true, y_pred, zero_division=0))

    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = 0.5

    cm = confusion_matrix(y_true, y_pred)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
    else:
        tn, fp, fn, tp = int(cm[0, 0]), 0, 0, 0

    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    fpr         = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr         = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    return {
        "accuracy":            round(acc,         4),
        "precision":           round(prec,        4),
        "recall":              round(rec,          4),
        "f1_score":            round(f1,           4),
        "roc_auc":             round(roc_auc,      4),
        "specificity":         round(specificity,  4),
        "false_positive_rate": round(fpr,          4),
        "false_negative_rate": round(fnr,          4),
        "confusion_matrix": {
            "TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
def tune_xgboost(X_train, y_train) -> object:
    """Grid-search over key XGBoost hyper-parameters."""
    if not XGB_AVAILABLE:
        model = GradientBoostingClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            subsample=0.8, random_state=RANDOM_STATE
        )
        model.fit(X_train, y_train)
        return model

    param_grid = {
        "n_estimators":    [150, 250],
        "max_depth":       [5, 7],
        "learning_rate":   [0.1],
        "subsample":       [0.85],
    }

    base = xgb.XGBClassifier(
        eval_metric="logloss",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)
    search = GridSearchCV(
        base, param_grid, cv=cv, scoring="f1",
        n_jobs=-1, verbose=0, refit=True
    )
    search.fit(X_train, y_train)
    print(f"[XGBoost GridSearch] Best params: {search.best_params_}")
    print(f"[XGBoost GridSearch] Best CV F1: {search.best_score_:.4f}")
    return search.best_estimator_


def tune_random_forest(X_train, y_train) -> object:
    """Grid-search over key Random Forest hyper-parameters."""
    param_grid = {
        "n_estimators":  [150, 250],
        "max_depth":     [15, 25],
        "max_features":  ["sqrt"],
    }

    base = RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)
    search = GridSearchCV(
        base, param_grid, cv=cv, scoring="f1",
        n_jobs=-1, verbose=0, refit=True
    )
    search.fit(X_train, y_train)
    print(f"[RandomForest GridSearch] Best params: {search.best_params_}")
    print(f"[RandomForest GridSearch] Best CV F1: {search.best_score_:.4f}")
    return search.best_estimator_



# ─────────────────────────────────────────────────────────────────────────────
def log_feature_importance(model, feature_names: list, top_n: int = 10):
    """Prints top-N feature importances if the model supports it."""
    importances = None

    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "estimators_"):
        # VotingClassifier — average importances across sub-estimators
        imps = []
        for _, est in model.estimators:
            if hasattr(est, "feature_importances_"):
                imps.append(est.feature_importances_)
        if imps:
            importances = np.mean(imps, axis=0)

    if importances is None:
        return

    indices = np.argsort(importances)[::-1][:top_n]
    print(f"\n{'─'*50}")
    print(f"TOP-{top_n} FEATURE IMPORTANCES")
    print(f"{'─'*50}")
    for rank, idx in enumerate(indices, 1):
        print(f"  {rank:>2}. {feature_names[idx]:<30} {importances[idx]:.4f}")
    print(f"{'─'*50}\n")


# ─────────────────────────────────────────────────────────────────────────────
def train_url_model(df: pd.DataFrame):
    """Full training pipeline for URL phishing detection."""
    print("\n" + "=" * 56)
    print("  URL PHISHING DETECTION — TRAINING PIPELINE")
    print("=" * 56)

    # Sample balanced 50k records if larger for high-speed training
    if len(df) > 50000:
        df_phish = df[df["label"] == 1].sample(min(20000, sum(df["label"] == 1)), random_state=RANDOM_STATE)
        df_legit = df[df["label"] == 0].sample(min(30000, sum(df["label"] == 0)), random_state=RANDOM_STATE)
        df = pd.concat([df_phish, df_legit], ignore_index=True).sample(frac=1.0, random_state=RANDOM_STATE).reset_index(drop=True)
        print(f"Sampled balanced training subset: {len(df)} records ({sum(df['label']==0)} legit, {sum(df['label']==1)} phishing)")

    # ── 1. Split ─────────────────────────────────────────────────────────────
    df_train, df_val, df_test = get_train_val_test_split(df, target_col="label")
    print(f"Split → Train: {len(df_train)} | Val: {len(df_val)} | Test (unseen): {len(df_test)}")


    # ── 2. Feature extraction ────────────────────────────────────────────────
    print("\nExtracting 35 URL features...")
    feature_names = list(extract_url_features("http://example.com").keys())

    def extract_matrix(urls):
        return np.array([list(extract_url_features(u).values()) for u in urls])

    X_train_raw = extract_matrix(df_train["url"])
    X_val_raw   = extract_matrix(df_val["url"])
    X_test_raw  = extract_matrix(df_test["url"])

    # ── 3. Scale (fit ONLY on train) ─────────────────────────────────────────
    pipe = LeakageFreeTabularPipeline()
    X_train = pipe.fit_transform_train(X_train_raw)
    X_val   = pipe.transform_unseen(X_val_raw)
    X_test  = pipe.transform_unseen(X_test_raw)

    y_train = df_train["label"].values
    y_val   = df_val["label"].values
    y_test  = df_test["label"].values

    # ── 4. Hyper-parameter tuning ─────────────────────────────────────────────
    print("\n[1/3] Tuning XGBoost / GradientBoosting...")
    xgb_model = tune_xgboost(X_train, y_train)

    print("\n[2/3] Tuning Random Forest...")
    rf_model = tune_random_forest(X_train, y_train)

    # LR — fast, good baseline for ensemble diversity
    lr_model = LogisticRegression(max_iter=2000, C=1.0, solver="lbfgs", random_state=RANDOM_STATE)
    lr_model.fit(X_train, y_train)

    # ── 5. Build soft-voting ensemble ─────────────────────────────────────────
    print("\n[3/3] Building VotingClassifier ensemble (XGB + RF + LR)...")
    model_name_xgb = "xgb" if XGB_AVAILABLE else "gb"
    ensemble = VotingClassifier(
        estimators=[(model_name_xgb, xgb_model), ("rf", rf_model), ("lr", lr_model)],
        voting="soft",
        n_jobs=-1,
    )
    ensemble.fit(X_train, y_train)

    # ── 6. Evaluate candidates on validation set ──────────────────────────────
    candidates = {
        "XGBoost" if XGB_AVAILABLE else "GradientBoosting": xgb_model,
        "RandomForest":   rf_model,
        "LogisticRegression": lr_model,
        "VotingEnsemble": ensemble,
    }

    print(f"\n{'─'*56}")
    print(f"{'MODEL':<25} {'Train F1':>10} {'Val F1':>10} {'Val AUC':>10}")
    print(f"{'─'*56}")

    best_val_f1      = -1.0
    best_model_name  = None
    best_model_obj   = None
    results          = {}

    for name, model in candidates.items():
        y_tr_pred  = model.predict(X_train)
        train_f1   = float(f1_score(y_train, y_tr_pred, zero_division=0))

        y_val_pred = model.predict(X_val)
        y_val_prob = (
            model.predict_proba(X_val)[:, 1]
            if hasattr(model, "predict_proba")
            else y_val_pred.astype(float)
        )
        val_metrics = compute_detailed_metrics(y_val, y_val_pred, y_val_prob)
        val_f1 = val_metrics["f1_score"]
        val_auc = val_metrics["roc_auc"]

        print(f"  {name:<23} {train_f1:>10.4f} {val_f1:>10.4f} {val_auc:>10.4f}")

        if val_f1 > best_val_f1:
            best_val_f1     = val_f1
            best_model_name = name
            best_model_obj  = model

        results[name] = {
            "train_f1":   train_f1,
            "val_f1":     val_f1,
            "val_metrics": val_metrics,
        }

    print(f"{'─'*56}")
    print(f"\n✅ BEST MODEL (on validation): [{best_model_name}] — Val F1: {best_val_f1:.4f}")

    # ── 7. Feature importance ─────────────────────────────────────────────────
    log_feature_importance(best_model_obj, feature_names, top_n=10)

    # ── 8. Final unseen test evaluation ──────────────────────────────────────
    y_test_pred = best_model_obj.predict(X_test)
    y_test_prob = (
        best_model_obj.predict_proba(X_test)[:, 1]
        if hasattr(best_model_obj, "predict_proba")
        else y_test_pred.astype(float)
    )
    test_metrics = compute_detailed_metrics(y_test, y_test_pred, y_test_prob)

    print("\n" + classification_report(y_test, y_test_pred, target_names=["Legitimate", "Phishing"]))

    train_f1_best     = results[best_model_name]["train_f1"]
    overfitting_delta = train_f1_best - test_metrics["f1_score"]
    is_overfitting    = overfitting_delta > 0.08

    overfitting_info = {
        "train_f1":    round(train_f1_best, 4),
        "val_f1":      round(best_val_f1, 4),
        "test_f1":     test_metrics["f1_score"],
        "delta":       round(overfitting_delta, 4),
        "is_overfitting": is_overfitting,
        "warning":     "High train-test F1 gap detected" if is_overfitting else None,
    }

    # ── 9. Persist model + scaler ─────────────────────────────────────────────
    save_dir = "ml/saved_models/url"
    os.makedirs(save_dir, exist_ok=True)

    joblib.dump(best_model_obj, f"{save_dir}/best_model.pkl")
    joblib.dump(pipe.scaler,    f"{save_dir}/scaler.pkl")
    joblib.dump(feature_names,  f"{save_dir}/feature_names.pkl")
    print(f"\nModel artefacts saved → {save_dir}/")

    # ── 10. Report ────────────────────────────────────────────────────────────
    report = {
        "dataset": "URL",
        "selected_best_model": best_model_name,
        "feature_count": len(feature_names),
        "test_samples": int(len(df_test)),
        "unseen_test_metrics": test_metrics,
        "overfitting_analysis": overfitting_info,
        "all_model_val_results": {
            k: {"train_f1": v["train_f1"], "val_f1": v["val_f1"],
                "val_auc": v["val_metrics"]["roc_auc"]}
            for k, v in results.items()
        },
        "evaluation_date": datetime.utcnow().isoformat(),
    }

    os.makedirs("reports", exist_ok=True)
    with open("reports/url_test_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Final summary report (top-level)
    final_report = {"url_report": report, "generated_at": datetime.utcnow().isoformat()}
    with open("reports/final_model_report.json", "w") as f:
        json.dump(final_report, f, indent=2)

    print("\n" + "=" * 56)
    print("  URL MODEL TRAINING COMPLETE — MODELS LOCKED ✅")
    print(f"  Test F1:  {test_metrics['f1_score']:.4f}")
    print(f"  Test AUC: {test_metrics['roc_auc']:.4f}")
    print("  Reports → reports/url_test_report.json")
    print("=" * 56)

    return report


# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 56)
    print("  PHISHING URL DETECTION — FULL ML PIPELINE")
    print("=" * 56)

    # Load dataset
    df = load_url_dataset()
    url_stats = inspect_dataset(df, "URL")
    create_url_readme(url_stats)

    print(f"\nDataset — Total: {url_stats['total_samples']} | "
          f"Legit: {url_stats['legitimate_samples']} | "
          f"Phishing: {url_stats['phishing_samples']}")

    train_url_model(df)


if __name__ == "__main__":
    main()