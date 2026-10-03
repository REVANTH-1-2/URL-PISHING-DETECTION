"""
predict.py
==========
Command Line Interface for Predicting SMS and Email Phishing with Explainable AI.
"""

import sys
import json
import argparse
from load_model import load_all_models


def main():
    parser = argparse.ArgumentParser(description="DETECT: AI-Enhanced Multi-Modal Phishing Detector")
    parser.add_argument("--type", choices=["sms", "email"], default="sms", help="Type of input: 'sms' or 'email'")
    parser.add_argument("--text", type=str, help="Text message or email body to evaluate")
    parser.add_argument("--sender", type=str, default="", help="Email sender address (optional)")
    parser.add_argument("--subject", type=str, default="", help="Email subject line (optional)")
    args = parser.parse_args()

    detector = load_all_models()

    if not args.text:
        print("\n--- Running Demo Inference on Sample Inputs ---\n")
        # Demo SMS
        sms_sample = "URGENT: Your Chase bank account is suspended! Verify at http://chase-security-update.xyz/login"
        print(f"[SMS Sample]: {sms_sample}")
        sms_res = detector.predict_sms(sms_sample)
        print(json.dumps(sms_res, indent=2))

        print("\n" + "-" * 60 + "\n")

        # Demo Email
        email_sender = "tax-department@irs-gov-portal.xyz"
        email_subject = "IMMEDIATE ACTION REQUIRED: Unpaid Tax Refund Claim"
        email_body = "Dear Taxpayer, click http://irs-refund-claim.top to verify your bank details within 24 hours."
        print(f"[Email Sample] Sender: {email_sender} | Subject: {email_subject}")
        email_res = detector.predict_email(sender=email_sender, subject=email_subject, body=email_body)
        print(json.dumps(email_res, indent=2))

    else:
        if args.type == "sms":
            result = detector.predict_sms(args.text)
        else:
            result = detector.predict_email(sender=args.sender, subject=args.subject, body=args.text)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
