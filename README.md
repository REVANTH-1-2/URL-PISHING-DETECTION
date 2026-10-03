# DETECT: AI-Enhanced Multi-Modal Phishing Detection

**DETECT** is a modular, multi-modal machine learning architecture designed to identify phishing threats across **SMS (Smishing)** and **Email**, built for future integration alongside existing **URL phishing detection** models.

---

## 📌 Executive Overview & Architecture

Modern phishing campaigns employ diverse attack vectors across text messages (SMS), emails, and malicious URLs. The DETECT architecture provides separate, specialized machine learning pipelines for each modality while maintaining a unified inference interface (`load_model.py`).

```
                              ┌───────────────────────────────────┐
                              │     MultiModalPhishingDetector    │
                              └─────────────────┬─────────────────┘
                                                │
         ┌──────────────────────────────────────┼──────────────────────────────────────┐
         ▼                                      ▼                                      ▼
┌───────────────────┐                  ┌───────────────────┐                  ┌───────────────────┐
│     SMS Model     │                  │    Email Model    │                  │  URL Model (Exist)│
│ (TF-IDF + Aux FE) │                  │ (TF-IDF + Aux FE) │                  │ (Structural / Lex)│
└────────┬──────────┘                  └────────┬──────────┘                  └────────┬──────────┘
         │                                      │                                      │
         ▼                                      ▼                                      ▼
   Tuned Th: ~0.168                      Tuned Th: ~0.218                        Preserved Unchanged
```

---

## 🛠️ Key Pipeline Features

1. **Leakage-Free Preprocessing (`preprocessing.py`)**:
   - HTML entity decoding, unicode standardization (NFKD), HTML tag stripping.
   - Preservation of key phishing indicators (urgent keywords, email addresses, URLs, `$`, `!`).
   - Group-stratified deduplication ensuring **0 text leakage** across Train, Validation, and Test splits.

2. **Feature Union Engineering (`PhishingFeaturePipeline`)**:
   - Fits TF-IDF (unigrams + bigrams) and `StandardScaler` for 12 auxiliary lexical & structural features **strictly on training data**.

3. **False Positive Reduction & Threshold Tuning (`train_sms.py`, `train_email.py`)**:
   - Validates candidate models (Logistic Regression, Linear SVM, Random Forest, XGBoost).
   - Tunes classification thresholds on validation data to minimize False Positive Rate (FPR) while maintaining a configurable minimum phishing recall target (default **95%**).

4. **Independent Test Evaluation (`evaluate.py`)**:
   - Evaluates models on an untouched test set.
   - Generates ROC curves, Precision-Recall curves, Confusion Matrices, Threshold trade-off plots, and saves False Positive / False Negative CSVs.

5. **Explainable AI (XAI) & Unified Inference (`load_model.py`, `predict.py`)**:
   - Calculates exact feature contribution scores per prediction.
   - Provides plain-English explanations with explicit disclaimers distinguishing generic spam from smishing.

---

## 🚀 Environment Setup & Usage

### 1. Prerequisites & Virtual Environment

Make sure you are running Python 3.9+ on macOS/Linux. Activate the local virtual environment:

```bash
# Create virtual environment if missing
python3 -m venv backend/venv

# Activate virtual environment
source backend/venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 2. Training SMS and Email Models

Run the independent training pipelines:

```bash
# Train SMS Phishing Pipeline
python train_sms.py

# Train Email Phishing Pipeline
python train_email.py
```

### 3. Evaluation & Visualization Suite

Evaluate saved models on held-out test sets and generate high-resolution plots:

```bash
python evaluate.py
```

Generated outputs will be saved to:
- `outputs/metrics/model_comparison_table.csv`
- `outputs/metrics/sms_metrics.json`
- `outputs/metrics/email_metrics.json`
- `outputs/plots/confusion_matrices.png`
- `outputs/plots/roc_curves.png`
- `outputs/plots/precision_recall_curves.png`
- `outputs/plots/threshold_vs_fpr_recall.png`
- `outputs/errors/sms_false_positives.csv`
- `outputs/errors/sms_false_negatives.csv`
- `outputs/errors/email_false_positives.csv`
- `outputs/errors/email_false_negatives.csv`

### 4. Interactive Prediction & Explainable AI Demo

Predict on sample inputs or command-line strings:

```bash
# Run demonstration with XAI explanations
python predict.py

# Predict custom SMS
python predict.py --type sms --text "URGENT: Your account access is suspended! Reset at http://bank-update.xyz"

# Predict custom Email
python predict.py --type email --sender "security@apple-id-verify.click" --subject "Account Locked" --text "Verify credentials immediately."
```

---

## 📊 Dataset Overview & Experimental Results

### Dataset Summary
- **SMS Dataset**: 5,574 raw records (20 unique message templates; 10 Legitimate / 10 Spam).
- **Email Dataset**: 4,000 raw records (8 unique email templates; 4 Legitimate / 4 Phishing).

### Threshold Tuning & False Positive Reduction (Validation Set)

| Domain | Model | Default Threshold (0.50) FPR | Tuned Threshold | Tuned FPR | Target Recall (>=95%) Achieved |
|---|---|---|---|---|---|
| **SMS** | Logistic Regression | 0.00% | 0.1684 | 0.00% | ✅ Yes (100.00%) |
| **SMS** | Linear SVM | 0.00% | 0.2575 | 0.00% | ✅ Yes (100.00%) |
| **SMS** | Random Forest | 0.00% | 0.0892 | 0.00% | ✅ Yes (100.00%) |
| **SMS** | XGBoost | 0.00% | 0.0100 | 100.00% | ⚠️ Fallback |
| **Email** | Logistic Regression | 0.00% | 0.2179 | 0.00% | ✅ Yes (100.00%) |
| **Email** | Linear SVM | 0.00% | 0.3664 | 0.00% | ✅ Yes (100.00%) |
| **Email** | Random Forest | 0.00% | 0.4258 | 0.00% | ✅ Yes (100.00%) |
| **Email** | XGBoost | 100.00% | 0.0100 | 100.00% | ⚠️ Fallback |

---

## ⚠️ Important Limitations & Ethical Disclaimers

1. **Generic Spam vs. Targeted Phishing (Smishing)**:
   - SMS training labels classify messages into `ham` (legitimate) and `spam`. While malicious SMS messages (smishing) are included in the spam class, generic promotional SMS spam is not strictly phishing. High spam scores should not be treated as conclusive evidence of brand impersonation.
2. **Synthetic Dataset Structure**:
   - The dataset files in `ml/datasets/` consist of repeated template messages. Our group-stratified deduplication prevents cross-split data leakage, but real-world deployments should fine-tune on larger, diverse open-source corpora (e.g. Enron Email Corpus, UCI SMS Corpus).
3. **Preservation of Existing Models**:
   - The pre-existing URL model (`ml/saved_models/url/best_model.pkl`) was strictly preserved and kept intact.

---

## 📁 Project Directory Map

```
.
├── config.py                  # Central configuration settings
├── preprocessing.py           # Text cleaning, feature pipeline, split logic
├── train_sms.py               # SMS model training & threshold tuning
├── train_email.py             # Email model training & threshold tuning
├── evaluate.py                # Untouched test set evaluation & plotting
├── load_model.py              # MultiModalPhishingDetector & XAI engine
├── predict.py                 # CLI interface for prediction & explanations
├── requirements.txt           # Python dependency manifest
├── README.md                  # Comprehensive project documentation
├── models/                    # Saved SMS & Email pipelines
│   ├── sms_phishing_pipeline.pkl
│   └── email_phishing_pipeline.pkl
└── outputs/                   # Training metrics, plots, and error reports
    ├── errors/
    ├── metrics/
    └── plots/
```
