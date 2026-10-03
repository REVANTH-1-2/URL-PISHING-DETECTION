"""
evaluate.py
===========
Evaluation & Visualization Suite for DETECT SMS and Email Phishing Models.
"""

import os
import json
import warnings
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    roc_curve,
    precision_recall_curve,
)

import config
import preprocessing

warnings.filterwarnings("ignore")

# Set publication style for matplotlib
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({"font.size": 11, "figure.dpi": 300, "axes.titlesize": 13, "axes.labelsize": 11})


def compute_test_metrics(y_true, y_prob, threshold):
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


def plot_confusion_matrices(sms_data, email_data, output_path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # SMS CM
    cm_sms = np.array(sms_data["metrics"]["confusion_matrix"])
    sns.heatmap(
        cm_sms,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        ax=axes[0],
        xticklabels=["Legitimate", "Suspicious/Spam"],
        yticklabels=["Legitimate", "Suspicious/Spam"],
    )
    axes[0].set_title(f"SMS Model ({sms_data['model_name']})\nThreshold = {sms_data['threshold']:.4f}")
    axes[0].set_xlabel("Predicted Label")
    axes[0].set_ylabel("True Label")

    # Email CM
    cm_email = np.array(email_data["metrics"]["confusion_matrix"])
    sns.heatmap(
        cm_email,
        annot=True,
        fmt="d",
        cmap="Greens",
        cbar=False,
        ax=axes[1],
        xticklabels=["Legitimate", "Phishing"],
        yticklabels=["Legitimate", "Phishing"],
    )
    axes[1].set_title(f"Email Model ({email_data['model_name']})\nThreshold = {email_data['threshold']:.4f}")
    axes[1].set_xlabel("Predicted Label")
    axes[1].set_ylabel("True Label")

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"[Plot Saved] Confusion matrices -> {output_path}")


def plot_roc_curves(sms_evals, email_evals, output_path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # SMS ROC
    for name, data in sms_evals.items():
        y_true = data["y_true"]
        y_prob = data["y_prob"]
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        auc_score = data["metrics"]["roc_auc"]
        axes[0].plot(fpr, tpr, label=f"{name} (AUC = {auc_score:.4f})", lw=2)

    axes[0].plot([0, 1], [0, 1], "k--", lw=1.5)
    axes[0].set_title("SMS Models - ROC Curves")
    axes[0].set_xlabel("False Positive Rate (FPR)")
    axes[0].set_ylabel("True Positive Rate (Recall)")
    axes[0].legend(loc="lower right")

    # Email ROC
    for name, data in email_evals.items():
        y_true = data["y_true"]
        y_prob = data["y_prob"]
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        auc_score = data["metrics"]["roc_auc"]
        axes[1].plot(fpr, tpr, label=f"{name} (AUC = {auc_score:.4f})", lw=2)

    axes[1].plot([0, 1], [0, 1], "k--", lw=1.5)
    axes[1].set_title("Email Models - ROC Curves")
    axes[1].set_xlabel("False Positive Rate (FPR)")
    axes[1].set_ylabel("True Positive Rate (Recall)")
    axes[1].legend(loc="lower right")

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"[Plot Saved] ROC curves -> {output_path}")


def plot_precision_recall_curves(sms_evals, email_evals, output_path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # SMS PR
    for name, data in sms_evals.items():
        y_true = data["y_true"]
        y_prob = data["y_prob"]
        prec, rec, _ = precision_recall_curve(y_true, y_prob)
        axes[0].plot(rec, prec, label=name, lw=2)

    axes[0].set_title("SMS Models - Precision-Recall Curves")
    axes[0].set_xlabel("Recall")
    axes[0].set_ylabel("Precision")
    axes[0].legend(loc="lower left")

    # Email PR
    for name, data in email_evals.items():
        y_true = data["y_true"]
        y_prob = data["y_prob"]
        prec, rec, _ = precision_recall_curve(y_true, y_prob)
        axes[1].plot(rec, prec, label=name, lw=2)

    axes[1].set_title("Email Models - Precision-Recall Curves")
    axes[1].set_xlabel("Recall")
    axes[1].set_ylabel("Precision")
    axes[1].legend(loc="lower left")

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"[Plot Saved] PR curves -> {output_path}")


def plot_threshold_vs_fpr_recall(sms_evals, email_evals, output_path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    thresholds = np.linspace(0.01, 0.99, 100)

    # SMS Threshold Trade-off (Best Model)
    best_sms_name = list(sms_evals.keys())[0]
    y_true_sms = sms_evals[best_sms_name]["y_true"]
    y_prob_sms = sms_evals[best_sms_name]["y_prob"]
    tuned_th_sms = sms_evals[best_sms_name]["threshold"]

    sms_fprs, sms_recs = [], []
    for th in thresholds:
        preds = (y_prob_sms >= th).astype(int)
        cm = confusion_matrix(y_true_sms, preds, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (int(cm[0, 0]), 0, 0, 0)
        sms_fprs.append(float(fp / (fp + tn)) * 100 if (fp + tn) > 0 else 0.0)
        sms_recs.append(float(tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0.0)

    axes[0].plot(thresholds, sms_recs, label="Recall (%)", color="green", lw=2)
    axes[0].plot(thresholds, sms_fprs, label="FPR (%)", color="red", lw=2)
    axes[0].axvline(x=tuned_th_sms, color="purple", linestyle="--", label=f"Tuned Threshold ({tuned_th_sms:.4f})")
    axes[0].axvline(x=0.5, color="gray", linestyle=":", label="Default (0.50)")
    axes[0].axhline(y=config.TARGET_MIN_RECALL * 100, color="darkgreen", linestyle="-.", label="Target Recall (95%)")
    axes[0].set_title(f"SMS Trade-off ({best_sms_name})")
    axes[0].set_xlabel("Classification Threshold")
    axes[0].set_ylabel("Rate (%)")
    axes[0].legend(loc="best")

    # Email Threshold Trade-off (Best Model)
    best_email_name = list(email_evals.keys())[0]
    y_true_email = email_evals[best_email_name]["y_true"]
    y_prob_email = email_evals[best_email_name]["y_prob"]
    tuned_th_email = email_evals[best_email_name]["threshold"]

    email_fprs, email_recs = [], []
    for th in thresholds:
        preds = (y_prob_email >= th).astype(int)
        cm = confusion_matrix(y_true_email, preds, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (int(cm[0, 0]), 0, 0, 0)
        email_fprs.append(float(fp / (fp + tn)) * 100 if (fp + tn) > 0 else 0.0)
        email_recs.append(float(tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0.0)

    axes[1].plot(thresholds, email_recs, label="Recall (%)", color="green", lw=2)
    axes[1].plot(thresholds, email_fprs, label="FPR (%)", color="red", lw=2)
    axes[1].axvline(x=tuned_th_email, color="purple", linestyle="--", label=f"Tuned Threshold ({tuned_th_email:.4f})")
    axes[1].axvline(x=0.5, color="gray", linestyle=":", label="Default (0.50)")
    axes[1].axhline(y=config.TARGET_MIN_RECALL * 100, color="darkgreen", linestyle="-.", label="Target Recall (95%)")
    axes[1].set_title(f"Email Trade-off ({best_email_name})")
    axes[1].set_xlabel("Classification Threshold")
    axes[1].set_ylabel("Rate (%)")
    axes[1].legend(loc="best")

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"[Plot Saved] Threshold vs FPR & Recall -> {output_path}")


def save_error_analysis(df_test, y_true, y_prob, threshold, prefix):
    preds = (y_prob >= threshold).astype(int)
    df_err = df_test.copy()
    df_err["true_label"] = y_true
    df_err["predicted_prob"] = np.round(y_prob, 4)
    df_err["predicted_label"] = preds

    # False Positives: True = 0 (Legitimate), Pred = 1 (Phishing)
    fp_df = df_err[(df_err["true_label"] == 0) & (df_err["predicted_label"] == 1)]
    # False Negatives: True = 1 (Phishing), Pred = 0 (Legitimate)
    fn_df = df_err[(df_err["true_label"] == 1) & (df_err["predicted_label"] == 0)]

    fp_path = config.ERRORS_DIR / f"{prefix}_false_positives.csv"
    fn_path = config.ERRORS_DIR / f"{prefix}_false_negatives.csv"

    fp_df.to_csv(fp_path, index=False)
    fn_df.to_csv(fn_path, index=False)

    print(f"[Errors Exported] {prefix} False Positives: {len(fp_df)} -> {fp_path}")
    print(f"[Errors Exported] {prefix} False Negatives: {len(fn_df)} -> {fn_path}")


def evaluate_all():
    print("=" * 60)
    print("      DETECT: EVALUATION & VISUALIZATION SUITE           ")
    print("=" * 60)

    # 1. Load trained pipelines
    if not os.path.exists(config.SMS_MODEL_PATH) or not os.path.exists(config.EMAIL_MODEL_PATH):
        print("[Error] Trained models missing. Run train_sms.py and train_email.py first.")
        return

    sms_pkg = joblib.load(config.SMS_MODEL_PATH)
    email_pkg = joblib.load(config.EMAIL_MODEL_PATH)

    # Load dataset metrics files
    with open(config.METRICS_DIR / "sms_metrics.json") as f:
        sms_raw_metrics = json.load(f)
    with open(config.METRICS_DIR / "email_metrics.json") as f:
        email_raw_metrics = json.load(f)

    # Re-extract test data splits
    sms_df, _ = preprocessing.load_sms_dataset()
    _, _, sms_test_df = preprocessing.group_stratified_split(sms_df)

    email_df, _ = preprocessing.load_email_dataset()
    _, _, email_test_df = preprocessing.group_stratified_split(email_df)

    # 2. Collect test evaluations for SMS
    sms_pipeline = sms_pkg["pipeline"]
    X_sms_test = sms_pipeline.transform(sms_test_df["text"])
    y_sms_test = sms_test_df["label"].values

    sms_evals = {}
    for name, m_info in sms_raw_metrics["all_models"].items():
        th = m_info["tuned_threshold"]
        # Retrieve test probs from recorded training results or predict
        test_probs = np.array(m_info["test_probs"])
        test_m = compute_test_metrics(y_sms_test, test_probs, threshold=th)
        sms_evals[name] = {
            "y_true": y_sms_test,
            "y_prob": test_probs,
            "threshold": th,
            "metrics": test_m,
        }

    # 3. Collect test evaluations for Email
    email_pipeline = email_pkg["pipeline"]
    X_email_test = email_pipeline.transform(email_test_df["text"])
    y_email_test = email_test_df["label"].values

    email_evals = {}
    for name, m_info in email_raw_metrics["all_models"].items():
        th = m_info["tuned_threshold"]
        test_probs = np.array(m_info["test_probs"])
        test_m = compute_test_metrics(y_email_test, test_probs, threshold=th)
        email_evals[name] = {
            "y_true": y_email_test,
            "y_prob": test_probs,
            "threshold": th,
            "metrics": test_m,
        }

    # 4. Generate Plots
    plot_confusion_matrices(
        {"model_name": sms_pkg["model_name"], "metrics": sms_evals[sms_pkg["model_name"]]["metrics"], "threshold": sms_pkg["tuned_threshold"]},
        {"model_name": email_pkg["model_name"], "metrics": email_evals[email_pkg["model_name"]]["metrics"], "threshold": email_pkg["tuned_threshold"]},
        config.PLOTS_DIR / "confusion_matrices.png",
    )

    plot_roc_curves(sms_evals, email_evals, config.PLOTS_DIR / "roc_curves.png")
    plot_precision_recall_curves(sms_evals, email_evals, config.PLOTS_DIR / "precision_recall_curves.png")
    plot_threshold_vs_fpr_recall(sms_evals, email_evals, config.PLOTS_DIR / "threshold_vs_fpr_recall.png")

    # 5. Export Error Analysis
    save_error_analysis(
        sms_test_df, y_sms_test, sms_evals[sms_pkg["model_name"]]["y_prob"], sms_pkg["tuned_threshold"], "sms"
    )
    save_error_analysis(
        email_test_df, y_email_test, email_evals[email_pkg["model_name"]]["y_prob"], email_pkg["tuned_threshold"], "email"
    )

    # 6. Build & Save Comparison Table
    table_rows = []
    for domain, evals in [("SMS", sms_evals), ("Email", email_evals)]:
        for model_name, data in evals.items():
            m = data["metrics"]
            table_rows.append({
                "Domain": domain,
                "Model": model_name,
                "Tuned Threshold": f"{data['threshold']:.4f}",
                "Accuracy (%)": f"{m['accuracy']:.2f}%",
                "Precision (%)": f"{m['precision']:.2f}%",
                "Recall (%)": f"{m['recall']:.2f}%",
                "Specificity (%)": f"{m['specificity']:.2f}%",
                "F1-Score (%)": f"{m['f1_score']:.2f}%",
                "ROC-AUC": f"{m['roc_auc']:.4f}",
                "FPR (%)": f"{m['fpr']:.2f}%",
                "FNR (%)": f"{m['fnr']:.2f}%",
            })

    comparison_df = pd.DataFrame(table_rows)
    csv_path = config.METRICS_DIR / "model_comparison_table.csv"
    comparison_df.to_csv(csv_path, index=False)
    print(f"\n[Comparison Table Exported] -> {csv_path}")

    print("\n" + "=" * 80)
    print("                    FINAL MODEL COMPARISON TABLE                       ")
    print("=" * 80)
    print(comparison_df.to_string(index=False))
    print("=" * 80)


if __name__ == "__main__":
    evaluate_all()
