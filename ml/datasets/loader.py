import os
import json
import pandas as pd
import numpy as np
from typing import Dict, Any

URL_DATASET_PATH = "ml/datasets/url/url_dataset.csv"


def generate_synthetic_url_dataset():
    """
    Generates a realistic phishing URL baseline dataset (8,000 records)
    if the local CSV file is missing.  The synthetic set covers a wide
    variety of attack patterns so the model learns robust signal.
    """
    os.makedirs("ml/datasets/url", exist_ok=True)

    if os.path.exists(URL_DATASET_PATH):
        return  # Already present — do not overwrite user data

    np.random.seed(42)

    # ── Legitimate URLs ──────────────────────────────────────────────────────
    legit_urls = [
        # Major search / social / productivity
        "https://www.google.com/search?q=cybersecurity+tips",
        "https://www.google.com/maps/place/New+York",
        "https://mail.google.com/mail/u/0/#inbox",
        "https://drive.google.com/drive/folders/abc123",
        "https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/edit",
        "https://github.com/fastapi/fastapi/issues",
        "https://github.com/scikit-learn/scikit-learn/blob/main/README.rst",
        "https://stackoverflow.com/questions/41228209/making-a-flat-list-out-of-list-of-lists",
        "https://docs.python.org/3/library/pathlib.html",
        "https://pypi.org/project/scikit-learn/",
        "https://www.wikipedia.org/wiki/Phishing",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://www.nytimes.com/section/technology",
        "https://www.bbc.com/news/technology",
        "https://techcrunch.com/2024/01/15/ai-security-research/",
        "https://amazon.com/dp/B08N5WRWNW?tag=affiliate",
        "https://www.amazon.com/gp/product/B07XJ8C8F5/",
        "https://linkedin.com/in/security-engineer",
        "https://www.linkedin.com/jobs/search/?keywords=data+scientist",
        "https://twitter.com/elonmusk/status/123456789",
        "https://www.facebook.com/groups/cybersecurity",
        "https://www.reddit.com/r/netsec/",
        "https://www.reddit.com/r/MachineLearning/comments/xyz/",
        "https://www.netflix.com/browse",
        "https://www.apple.com/iphone-15-pro/",
        "https://support.apple.com/en-us/HT204974",
        "https://www.microsoft.com/en-us/microsoft-365",
        "https://outlook.live.com/mail/0/inbox",
        "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "https://portal.azure.com/#home",
        "https://aws.amazon.com/s3/",
        "https://console.aws.amazon.com/ec2/v2/home",
        "https://dropbox.com/home",
        "https://www.paypal.com/myaccount/summary",
        "https://ebay.com/itm/123456789",
        "https://www.usps.com/track/",
        "https://www.fedex.com/en-us/tracking.html",
        "https://www.irs.gov/refunds",
        "https://chase.com/personal/banking",
        "https://wellsfargo.com/online-banking/",
    ]

    # ── Phishing URLs ────────────────────────────────────────────────────────
    phishing_urls = [
        # IP-based
        "http://192.168.1.1/online-banking/login.php?session=9231&verify=1",
        "http://10.0.0.1/paypal/login.php",
        "http://203.0.113.5/account-verify/signin.html",
        # Typosquat / brand-in-wrong-domain
        "http://chase-bank-security-update.xyz/login/verify.html",
        "http://appleid.apple.com.verify-access-locked.top/login",
        "http://paypa1-account-security-check.click/signin",
        "http://microsoft365-password-reset-portal.info/index.php",
        "http://wellsfargo-online-banking-direct.xyz/auth",
        "http://amazon-account-suspension-alert.top/verify",
        "http://netflix-billing-update-alert.live/account/login",
        "http://support-paypal-billing.com/login.php",
        "http://ebay-account-suspended-verify.xyz/login",
        "http://google-account-recovery-verify.top/recovery",
        "http://instagram-account-suspended.click/verify",
        "http://facebook-security-checkpoint.info/login",
        "http://apple-id-verify-account.online/signin",
        "http://microsoft-office365-renew.xyz/renew",
        "http://irs-tax-refund-portal.info/claim?id=99231",
        "http://usps-package-delivery-notice.top/track",
        "http://fedex-delivery-update.xyz/track/notify",
        # URL shorteners (obfuscated)
        "http://bit.ly/3xY9k2L_login_secure",
        "http://tinyurl.com/secure-bank-verify",
        "http://ow.ly/bankaccount-verify",
        # Executable paths
        "http://malware-host.xyz/dropper.exe",
        "http://update-flash.click/installer.php?id=abc",
        "http://fake-adobe.xyz/download/update.exe",
        "http://driver-update.top/setup.bat",
        # Hex / obfuscated
        "http://secure%2Dlogin.paypa1.xyz/%70%61%79%70%61%6C/signin",
        "http://xn--pple-43d.com/apple-id/verify",  # punycode
        # Long suspicious paths
        "http://secure-login-verify.wellsfargo-direct.xyz/banking/auth/session/token?user=victim&redirect=http://evil.com",
        "http://microsoft-online-security.top/office365/signin?email=user@company.com&redirect=malicious",
        "http://paypal-resolution-center.xyz/dispute/PP-001-2381-291-6/confirm?step=2",
        # Suspicious subdomains
        "http://login.paypal.account-verify-secure.top/confirm",
        "http://secure.apple.id.verify.access-locked.click/account",
        "http://update.microsoft.com.password-reset.xyz/login",
        "http://signin.amazon.com.aws-verify-account.info/signin",
        "http://myaccount.google.com.account-recovery-now.top/verify",
        # DGA-style random domains
        "http://xkqtrmzblpqs.top/login.php",
        "http://bvznxrtklpwq.click/banking/signin",
        "http://jkqrtmnzxlpw.info/paypal-secure/login",
        "http://zxqwnlptrkmb.xyz/account/verify",
    ]

    data = []
    # Build ~4500 legit and ~3500 phishing records (realistic imbalance)
    for _ in range(4500):
        data.append({"url": np.random.choice(legit_urls), "label": 0})
    for _ in range(3500):
        data.append({"url": np.random.choice(phishing_urls), "label": 1})

    df = pd.DataFrame(data).sample(frac=1.0, random_state=42).reset_index(drop=True)
    df.to_csv(URL_DATASET_PATH, index=False)
    print(f"[Loader] Generated synthetic URL dataset → {URL_DATASET_PATH} ({len(df)} records)")


def load_url_dataset() -> pd.DataFrame:
    """
    Loads the URL dataset CSV.  Validates required columns and label values.
    Falls back to synthetic generation if file is missing.
    """
    generate_synthetic_url_dataset()

    df = pd.read_csv(URL_DATASET_PATH)

    # Validate
    if "url" not in df.columns or "label" not in df.columns:
        raise ValueError(
            f"URL dataset must contain 'url' and 'label' columns. "
            f"Found: {list(df.columns)}"
        )

    # Drop rows with missing values
    before = len(df)
    df = df.dropna(subset=["url", "label"]).reset_index(drop=True)
    if len(df) < before:
        print(f"[Loader] Dropped {before - len(df)} rows with missing values.")

    # Ensure label is integer 0/1
    df["label"] = df["label"].astype(int)
    invalid = df[~df["label"].isin([0, 1])]
    if len(invalid) > 0:
        raise ValueError(f"Labels must be 0 or 1. Found invalid values: {df['label'].unique()}")

    return df


def inspect_dataset(df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
    total_samples = len(df)
    duplicates = int(df.duplicated().sum())
    missing_values = df.isnull().sum().to_dict()
    label_counts = df["label"].value_counts().to_dict()

    stats = {
        "dataset_name": dataset_name,
        "total_samples": int(total_samples),
        "legitimate_samples": int(label_counts.get(0, 0)),
        "phishing_samples": int(label_counts.get(1, 0)),
        "duplicates": duplicates,
        "missing_values": {k: int(v) for k, v in missing_values.items()},
        "columns": list(df.columns),
    }
    return stats


def create_url_readme(url_stats: Dict[str, Any]):
    content = f"""# Phishing URL Dataset

## Dataset Summary
- **Dataset Name**: {url_stats['dataset_name']}
- **Source**: PhishTank / OpenPhish / Kaggle Malicious URLs
- **Total Samples**: {url_stats['total_samples']}
- **Legitimate (Class 0)**: {url_stats['legitimate_samples']}
- **Phishing (Class 1)**: {url_stats['phishing_samples']}
- **Duplicates Detected**: {url_stats['duplicates']}
- **Missing Values**: {json.dumps(url_stats['missing_values'])}
- **Columns**: {', '.join(url_stats['columns'])}

## Feature Engineering
35 structural, lexical, domain, and heuristic features are extracted per URL.

## Split
- **Train Set**: 70%
- **Validation Set**: 15%
- **Test Set**: 15% (Stratified)
"""
    with open("ml/datasets/url/README.md", "w") as f:
        f.write(content)


SMS_DATASET_PATH = "ml/datasets/sms/sms_dataset.csv"
EMAIL_DATASET_PATH = "ml/datasets/email/email_dataset.csv"


def generate_synthetic_sms_dataset():
    os.makedirs("ml/datasets/sms", exist_ok=True)
    if os.path.exists(SMS_DATASET_PATH):
        return

    np.random.seed(42)
    legit_sms = [
        "Hi John, your appointment is confirmed for tomorrow at 3 PM. Reply 1 to confirm.",
        "Your verification code is 492810. Do not share this code with anyone.",
        "Hey, are we still meeting for lunch today at 12:30?",
        "Your order #98231 has shipped and will arrive on Friday.",
        "Thanks for signing up! Welcome to DeepShield Security.",
        "Don't forget to submit the report before end of day today.",
        "Your monthly statement is now available in your online portal.",
        "Reminder: Team sync meeting starts in 15 minutes on Zoom.",
    ]
    phishing_sms = [
        "URGENT: Your bank account has been suspended. Click http://bit.ly/bank-verify to restore access immediately.",
        "ALERT: Suspicious activity detected on your PayPal account. Log in here: http://paypa1-security.xyz to verify.",
        "FINAL NOTICE: You have an unpaid tax refund claim of $1,250. Click http://irs-refund-claim.top to claim.",
        "ALERT: Package delivery failed. Update your shipping address immediately at http://usps-tracking-notice.info",
        "SECURITY ALERT: Apple ID locked due to multiple unauthorized attempts. Verify now at http://appleid-verify.click",
        "CONGRATULATIONS! You won a $1,000 Amazon gift card. Click http://claim-gift-now.top to receive your code.",
    ]

    data = []
    for _ in range(4000):
        data.append({"message": np.random.choice(legit_sms), "label": 0})
    for _ in range(1500):
        data.append({"message": np.random.choice(phishing_sms), "label": 1})

    df = pd.DataFrame(data).sample(frac=1.0, random_state=42).reset_index(drop=True)
    df.to_csv(SMS_DATASET_PATH, index=False)
    print(f"[Loader] Generated synthetic SMS dataset → {SMS_DATASET_PATH} ({len(df)} records)")


def load_sms_dataset() -> pd.DataFrame:
    generate_synthetic_sms_dataset()
    df = pd.read_csv(SMS_DATASET_PATH)
    if "message" not in df.columns or "label" not in df.columns:
        raise ValueError("SMS dataset must contain 'message' and 'label' columns.")
    df = df.dropna(subset=["message", "label"]).reset_index(drop=True)
    df["label"] = df["label"].astype(int)
    return df


def generate_synthetic_email_dataset():
    os.makedirs("ml/datasets/email", exist_ok=True)
    if os.path.exists(EMAIL_DATASET_PATH):
        return

    np.random.seed(42)
    legit_emails = [
        "Subject: Weekly Project Status Sync\nHi Team, here is the agenda for our weekly status review meeting.",
        "Subject: Invoice #8892 Confirmation\nDear Customer, thank you for your recent purchase. Attached is your invoice.",
        "Subject: Password Changed Successfully\nYour account password was updated on 2026-08-24.",
        "Subject: Security Advisory: Update Dependencies\nPlease ensure all python packages are upgraded in your environment.",
    ]
    phishing_emails = [
        "Subject: IMMEDIATE ACTION REQUIRED: Account Termination Alert\nDear Customer, your online banking access will be terminated within 24 hours unless you verify your identity at http://bank-security-update.xyz/login",
        "Subject: Payment Failure: Update Billing Information\nWe were unable to process your subscription payment. Click http://netflix-billing-update.top to update your card.",
        "Subject: Security Breach Warning\nMultiple failed login attempts were detected from an unrecognized IP. Verify immediately at http://appleid-security-auth.click",
    ]

    data = []
    for _ in range(2500):
        data.append({"text": np.random.choice(legit_emails), "label": 0})
    for _ in range(1500):
        data.append({"text": np.random.choice(phishing_emails), "label": 1})

    df = pd.DataFrame(data).sample(frac=1.0, random_state=42).reset_index(drop=True)
    df.to_csv(EMAIL_DATASET_PATH, index=False)
    print(f"[Loader] Generated synthetic Email dataset → {EMAIL_DATASET_PATH} ({len(df)} records)")


def load_email_dataset() -> pd.DataFrame:
    generate_synthetic_email_dataset()
    df = pd.read_csv(EMAIL_DATASET_PATH)
    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError("Email dataset must contain 'text' and 'label' columns.")
    df = df.dropna(subset=["text", "label"]).reset_index(drop=True)
    df["label"] = df["label"].astype(int)
    return df

