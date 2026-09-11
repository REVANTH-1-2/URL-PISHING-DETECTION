# Phishing URL Dataset

## Dataset Summary
- **Dataset Name**: URL
- **Source**: PhishTank / OpenPhish / Kaggle Malicious URLs
- **Total Samples**: 507195
- **Legitimate (Class 0)**: 392897
- **Phishing (Class 1)**: 114298
- **Duplicates Detected**: 0
- **Missing Values**: {"url": 0, "label": 0}
- **Columns**: url, label

## Feature Engineering
35 structural, lexical, domain, and heuristic features are extracted per URL.

## Split
- **Train Set**: 70%
- **Validation Set**: 15%
- **Test Set**: 15% (Stratified)
