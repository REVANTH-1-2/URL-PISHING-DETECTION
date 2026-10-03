"""
config.py
=========
Central Configuration File for DETECT: AI-Enhanced Multi-Modal Phishing Detection.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "ml" / "datasets"
MODELS_DIR = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs"

METRICS_DIR = OUTPUTS_DIR / "metrics"
PLOTS_DIR = OUTPUTS_DIR / "plots"
ERRORS_DIR = OUTPUTS_DIR / "errors"

# Ensure directories exist
for path in [MODELS_DIR, METRICS_DIR, PLOTS_DIR, ERRORS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Dataset Paths
SMS_DATASET_PATH = DATA_DIR / "sms" / "sms_dataset.csv"
EMAIL_DATASET_PATH = DATA_DIR / "email" / "email_dataset.csv"
URL_DATASET_PATH = DATA_DIR / "url" / "url_dataset.csv"

# Saved Model Output Paths (Do NOT overwrite existing URL model)
SMS_MODEL_PATH = MODELS_DIR / "sms_phishing_pipeline.pkl"
EMAIL_MODEL_PATH = MODELS_DIR / "email_phishing_pipeline.pkl"
URL_MODEL_PATH = BASE_DIR / "ml" / "saved_models" / "url" / "best_model.pkl"

# Also maintain models in ml/saved_models for backward compatibility
ML_SAVED_SMS_PATH = BASE_DIR / "ml" / "saved_models" / "sms" / "best_model.pkl"
ML_SAVED_EMAIL_PATH = BASE_DIR / "ml" / "saved_models" / "email" / "best_model.pkl"

# Random Seed & Reproducibility
RANDOM_STATE = 42

# Dataset Split Configuration (70% Train, 15% Validation, 15% Test)
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# False Positive Control & Threshold Tuning Target
# Initial target minimum phishing recall rate (configurable)
TARGET_MIN_RECALL = 0.95
DEFAULT_THRESHOLD = 0.50

# Label Mappings
SMS_LABEL_MAP = {0: "Legitimate (Ham)", 1: "Suspicious / Spam"}
EMAIL_LABEL_MAP = {0: "Legitimate Email", 1: "Phishing Email"}

# TF-IDF Vectorizer Defaults
TFIDF_PARAMS = {
    "ngram_range": (1, 2),
    "min_df": 1,
    "sublinear_tf": True,
    "lowercase": True
}
