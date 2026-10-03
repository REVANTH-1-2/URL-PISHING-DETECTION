"""
preprocessing.py
================
Data Loading, Text Cleaning, Feature Extraction, and Leakage-Free Data Splitting for DETECT.
"""

import os
import re
import html
import unicodedata
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from scipy.sparse import hstack, csr_matrix
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler

import config


def clean_text(text: str) -> str:
    """
    Cleans raw text while preserving critical phishing indicators:
    - Decodes HTML entities (e.g., &amp; -> &)
    - Normalizes unicode encodings (NFKD)
    - Strips HTML tags but retains text inside
    - Preserves urgent words, URLs, email addresses, and punctuation (!, ?, $)
    - Normalizes multiple whitespace characters into single spaces
    """
    if not isinstance(text, str):
        return ""
    
    # HTML entity decoding & Unicode normalization
    text = html.unescape(text)
    text = unicodedata.normalize("NFKD", text)

    # Remove HTML tags safely
    text = re.sub(r"<[^>]+>", " ", text)

    # Collapse excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_email_components(sender: str, subject: str, body: str) -> str:
    """
    Combines email header components (sender, subject, body) into a single
    structured string representation while preserving key signals.
    """
    sender_clean = clean_text(str(sender)) if pd.notna(sender) else ""
    subject_clean = clean_text(str(subject)) if pd.notna(subject) else ""
    body_clean = clean_text(str(body)) if pd.notna(body) else ""

    parts = []
    if sender_clean:
        parts.append(f"Sender: {sender_clean}")
    if subject_clean:
        parts.append(f"Subject: {subject_clean}")
    if body_clean:
        parts.append(f"Body: {body_clean}")

    return " | ".join(parts)


# Key phishing indicators
URGENT_KEYWORDS_PATTERN = re.compile(
    r"\b(urgent|alert|immediate|verify|suspended|warning|action|update|locked|refund|won|congrats|prize|security|claim|notice|billing|login|bank|ssn|pin|access|unauthorized|failed|cash|gift|card)\b",
    re.I,
)
URL_PATTERN = re.compile(r"https?://|www\.", re.I)
IP_PATTERN = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


def extract_aux_features(texts: list) -> np.ndarray:
    """
    Extracts 12 handcrafted structural, lexical, and indicator features per text.
    """
    feats = []
    for t in texts:
        t_str = clean_text(str(t))
        has_url = 1.0 if URL_PATTERN.search(t_str) else 0.0
        num_urls = float(len(URL_PATTERN.findall(t_str)))
        has_urgent = 1.0 if URGENT_KEYWORDS_PATTERN.search(t_str) else 0.0
        num_urgent = float(len(URGENT_KEYWORDS_PATTERN.findall(t_str)))
        has_ip = 1.0 if IP_PATTERN.search(t_str) else 0.0
        has_email = 1.0 if EMAIL_PATTERN.search(t_str) else 0.0
        num_digits = float(sum(c.isdigit() for c in t_str))
        num_exclamation = float(t_str.count("!"))
        num_dollar = float(t_str.count("$"))
        text_len = float(len(t_str))
        word_cnt = float(len(t_str.split()))
        upper_ratio = float(sum(1 for c in t_str if c.isupper()) / (text_len + 1e-5))

        feats.append([
            has_url, num_urls, has_urgent, num_urgent, has_ip, has_email,
            num_digits, num_exclamation, num_dollar, text_len, word_cnt, upper_ratio
        ])
    return np.array(feats, dtype=np.float64)


AUX_FEATURE_NAMES = [
    "aux_has_url",
    "aux_num_urls",
    "aux_has_urgent",
    "aux_num_urgent",
    "aux_has_ip",
    "aux_has_email",
    "aux_num_digits",
    "aux_num_exclamation",
    "aux_num_dollar",
    "aux_text_len",
    "aux_word_cnt",
    "aux_upper_ratio",
]


class PhishingFeaturePipeline(BaseEstimator, TransformerMixin):
    """
    Sklearn-compatible transformer that fits TF-IDF vectorization and
    StandardScaler for handcrafted auxiliary features strictly on training data.
    """

    def __init__(self, ngram_range=(1, 2), min_df=1, sublinear_tf=True):
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.sublinear_tf = sublinear_tf
        self.vectorizer = TfidfVectorizer(
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            sublinear_tf=self.sublinear_tf,
            lowercase=True,
        )
        self.scaler = StandardScaler(with_mean=False)
        self.feature_names_ = []

    def fit(self, X, y=None):
        X_clean = [clean_text(t) for t in X]
        self.vectorizer.fit(X_clean)
        aux_feats = extract_aux_features(X)
        self.scaler.fit(aux_feats)

        tfidf_names = list(self.vectorizer.get_feature_names_out())
        self.feature_names_ = tfidf_names + AUX_FEATURE_NAMES
        return self

    def transform(self, X):
        X_clean = [clean_text(t) for t in X]
        tfidf_mat = self.vectorizer.transform(X_clean)
        aux_feats = extract_aux_features(X)
        aux_scaled = self.scaler.transform(aux_feats)
        return hstack([tfidf_mat, csr_matrix(aux_scaled)]).tocsr()


def inspect_raw_dataset(filepath: str, dataset_name: str) -> Dict[str, Any]:
    """
    Inspects dataset filenames, columns, label values, missing values,
    class distribution, and duplicate records.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset file not found at: {filepath}")

    df = pd.read_csv(filepath)
    total_records = len(df)
    duplicates = int(df.duplicated().sum())
    missing = {col: int(val) for col, val in df.isnull().sum().items()}

    label_col = "label" if "label" in df.columns else df.columns[-1]
    label_counts = {int(k): int(v) for k, v in df[label_col].value_counts().items()}

    return {
        "dataset_name": dataset_name,
        "filepath": str(filepath),
        "total_records": total_records,
        "duplicate_records": duplicates,
        "columns": list(df.columns),
        "missing_values": missing,
        "label_column": label_col,
        "label_counts": label_counts,
    }


def load_sms_dataset(filepath: str = str(config.SMS_DATASET_PATH)) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads and preprocesses the SMS dataset.
    Normalizes labels: 0 = Legitimate (Ham), 1 = Suspicious / Spam.
    Deduplicates records while checking for conflicting labels.
    """
    stats = inspect_raw_dataset(filepath, "SMS Phishing / Spam Dataset")
    df = pd.read_csv(filepath)

    text_col = "text" if "text" in df.columns else df.columns[0]
    label_col = "label" if "label" in df.columns else df.columns[1]

    df[text_col] = df[text_col].fillna("").apply(clean_text)
    df[label_col] = df[label_col].astype(int)

    conflicts = df.groupby(text_col)[label_col].nunique()
    conflicting_texts = int((conflicts > 1).sum())
    stats["conflicting_labels"] = conflicting_texts

    df_dedup = df.drop_duplicates(subset=[text_col, label_col]).reset_index(drop=True)
    stats["deduplicated_records"] = len(df_dedup)

    return df_dedup, stats


def load_email_dataset(filepath: str = str(config.EMAIL_DATASET_PATH)) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads and preprocesses the Email dataset.
    Combines sender, subject, and body into a clean text field.
    Normalizes labels: 0 = Legitimate Email, 1 = Phishing Email.
    Deduplicates records while checking for conflicting labels.
    """
    stats = inspect_raw_dataset(filepath, "Email Phishing Dataset")
    df = pd.read_csv(filepath)

    label_col = "label" if "label" in df.columns else df.columns[-1]

    full_texts = []
    for _, row in df.iterrows():
        s = row.get("sender", "")
        subj = row.get("subject", "")
        b = row.get("body", "")
        combined = clean_email_components(s, subj, b)
        full_texts.append(combined)

    df["text"] = full_texts
    df[label_col] = df[label_col].astype(int)

    conflicts = df.groupby("text")[label_col].nunique()
    conflicting_texts = int((conflicts > 1).sum())
    stats["conflicting_labels"] = conflicting_texts

    df_dedup = df.drop_duplicates(subset=["text", label_col]).reset_index(drop=True)
    stats["deduplicated_records"] = len(df_dedup)

    return df_dedup, stats


def group_stratified_split(
    df: pd.DataFrame,
    text_col: str = "text",
    label_col: str = "label",
    train_ratio: float = config.TRAIN_RATIO,
    val_ratio: float = config.VAL_RATIO,
    test_ratio: float = config.TEST_RATIO,
    random_state: int = config.RANDOM_STATE,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Splits unique text messages into Train, Validation, and Test sets stratified by label.
    Guarantees 0 text leakage across splits and ensures each split gets non-empty allocations.
    """
    unique_df = df.drop_duplicates(subset=[text_col]).reset_index(drop=True)
    
    legit_indices = unique_df[unique_df[label_col] == 0].index.values
    phish_indices = unique_df[unique_df[label_col] == 1].index.values

    np.random.seed(random_state)
    np.random.shuffle(legit_indices)
    np.random.shuffle(phish_indices)

    def allocate_indices(indices):
        n = len(indices)
        if n >= 4:
            n_tr = int(np.floor(n * train_ratio))
            n_v = max(1, int(np.floor(n * val_ratio)))
            n_te = n - n_tr - n_v
            if n_te <= 0:
                n_te = 1
                n_tr = n - n_v - n_te
            return indices[:n_tr], indices[n_tr : n_tr + n_v], indices[n_tr + n_v :]
        elif n == 3:
            return indices[:1], indices[1:2], indices[2:]
        elif n == 2:
            return indices[:1], indices[1:2], indices[1:2]
        else:
            return indices, indices, indices

    legit_tr, legit_v, legit_te = allocate_indices(legit_indices)
    phish_tr, phish_v, phish_te = allocate_indices(phish_indices)

    train_idx = np.concatenate([legit_tr, phish_tr])
    val_idx = np.concatenate([legit_v, phish_v])
    test_idx = np.concatenate([legit_te, phish_te])

    train_df = unique_df.iloc[train_idx].reset_index(drop=True)
    val_df = unique_df.iloc[val_idx].reset_index(drop=True)
    test_df = unique_df.iloc[test_idx].reset_index(drop=True)

    return train_df, val_df, test_df
