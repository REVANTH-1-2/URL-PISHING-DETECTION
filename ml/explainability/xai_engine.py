"""
xai_engine.py
=============
Explainable AI (XAI) engine — URL phishing detection only.
Maps all 35 extracted features to human-readable risk factors with
severity levels and actionable recommendations.
"""

import re
from typing import Dict, Any, List, Optional
from ml.features.extractor import extract_url_features



class XAIEngine:
    """Produces human-readable risk explanations from URL feature vectors."""

    @staticmethod
    def analyze_url(url_str: str, risk_score: float) -> Dict[str, Any]:
        """
        Analyse a URL using all 35 features and return:
        - detected_in: list of URL structural zones flagged
        - risk_factors: list of {factor, severity, explanation}
        - recommendations: actionable advice list
        """
        feats = extract_url_features(url_str)
        detected_in: List[str] = ["URL"]
        risk_factors: List[Dict[str, str]] = []

        # ── Domain structure ─────────────────────────────────────────────────
        if feats["is_ip"] > 0:
            detected_in.append("DOMAIN")
            risk_factors.append({
                "factor": "Numerical IP Address Instead of Domain",
                "severity": "HIGH",
                "explanation": (
                    "The URL uses a raw IP address (e.g. http://192.168.1.1/...) instead of a "
                    "registered domain name. Legitimate services almost never expose IP-based links."
                ),
            })

        if feats["has_punycode"] > 0:
            detected_in.append("DOMAIN")
            risk_factors.append({
                "factor": "Punycode / IDN Homograph Attack",
                "severity": "HIGH",
                "explanation": (
                    "The domain uses Punycode (xn-- prefix) which can disguise look-alike "
                    "Unicode characters as trusted brand names (e.g. аpple.com ≠ apple.com)."
                ),
            })

        if feats["has_suspicious_tld"] > 0:
            detected_in.append("DOMAIN")
            risk_factors.append({
                "factor": "High-Risk Top-Level Domain (TLD)",
                "severity": "HIGH",
                "explanation": (
                    "The domain uses a TLD (e.g. .xyz, .top, .click, .info) that is statistically "
                    "associated with phishing, spam, and malware distribution."
                ),
            })

        if feats["domain_brand_mismatch"] > 0:
            detected_in.append("DOMAIN")
            risk_factors.append({
                "factor": "Brand Impersonation / Typosquatting Detected",
                "severity": "HIGH",
                "explanation": (
                    "A well-known brand name or character-substitution typosquat appears in the domain, "
                    "but the site is NOT hosted on an official domain of that brand (e.g. paypal-verify.com or paypa1.com). "
                    "This is a primary credential harvesting technique."
                ),
            })

        if feats["brand_in_subdomain"] > 0:
            detected_in.append("DOMAIN")
            risk_factors.append({
                "factor": "Legitimate Brand Impersonated via Subdomain",
                "severity": "HIGH",
                "explanation": (
                    "A trusted brand name is used as a subdomain prefix (e.g. paypal.evil.xyz) "
                    "to create the visual impression of legitimacy while the actual domain is malicious."
                ),
            })

        if feats["domain_entropy"] > 3.8:
            detected_in.append("DOMAIN")
            risk_factors.append({
                "factor": "High Domain Entropy — Possible DGA Domain",
                "severity": "MEDIUM",
                "explanation": (
                    f"Domain randomness score is {feats['domain_entropy']:.2f} (threshold 3.8). "
                    "High-entropy strings (e.g. xkqtrmzbl.top) are hallmarks of Domain Generation "
                    "Algorithm (DGA) malware used by botnets and phishing kits."
                ),
            })

        if feats["dga_vowel_signal"] > 0:
            risk_factors.append({
                "factor": "Abnormally Low Vowel Ratio in Domain (DGA Signal)",
                "severity": "MEDIUM",
                "explanation": (
                    "The domain root contains very few vowels relative to consonants, "
                    "a statistical indicator of machine-generated domain names used in phishing."
                ),
            })

        if feats["has_consonant_cluster"] > 0:
            risk_factors.append({
                "factor": "Consecutive Consonant Cluster in Domain (DGA Signal)",
                "severity": "LOW",
                "explanation": (
                    "The domain contains 4+ consecutive consonants, which is rare in human-readable "
                    "words and common in algorithmically generated domain strings."
                ),
            })

        if feats["numeric_heavy_domain"] > 0:
            risk_factors.append({
                "factor": "Numeric-Heavy Domain Name",
                "severity": "MEDIUM",
                "explanation": (
                    "More than 30% of the domain name consists of digits. "
                    "Legitimate organisations rarely use number-heavy domain names."
                ),
            })

        if feats["subdomain_count"] >= 3:
            detected_in.append("DOMAIN")
            risk_factors.append({
                "factor": f"Excessive Subdomain Depth ({int(feats['subdomain_count'])} levels)",
                "severity": "MEDIUM",
                "explanation": (
                    "The URL contains an unusually deep subdomain chain "
                    "(e.g. login.secure.verify.evil.xyz). Attackers use this to hide the true domain."
                ),
            })

        if feats["domain_hyphen_count"] >= 2:
            risk_factors.append({
                "factor": "Multiple Hyphens in Domain Name",
                "severity": "LOW",
                "explanation": (
                    f"The domain contains {int(feats['domain_hyphen_count'])} hyphens. "
                    "While not conclusive alone, phishing domains frequently join brand keywords "
                    "with hyphens (e.g. secure-paypal-login.xyz)."
                ),
            })

        # ── URL structure ────────────────────────────────────────────────────
        if feats["is_shortened"] > 0:
            detected_in.append("URL")
            risk_factors.append({
                "factor": "URL Shortening Service Detected",
                "severity": "HIGH",
                "explanation": (
                    "A URL shortener (bit.ly, tinyurl, etc.) is used to hide the real destination. "
                    "Attackers use shorteners to bypass link-based filters and deceive users."
                ),
            })

        if feats["has_at_symbol"] > 0:
            detected_in.append("URL")
            risk_factors.append({
                "factor": "@ Symbol in URL",
                "severity": "HIGH",
                "explanation": (
                    "An @ symbol in the URL causes browsers to ignore everything before it, "
                    "redirecting to a potentially malicious domain after the @."
                ),
            })

        if feats["has_double_slash"] > 0:
            risk_factors.append({
                "factor": "Double Slash (//) in URL Path",
                "severity": "MEDIUM",
                "explanation": (
                    "A double slash in the path can indicate an open redirect or URL obfuscation "
                    "used to bypass security filters."
                ),
            })

        if feats["has_hex_encoding"] > 0:
            risk_factors.append({
                "factor": "Hex-Encoded Characters in URL",
                "severity": "MEDIUM",
                "explanation": (
                    "The URL contains percent-encoded characters (%xx) which can obfuscate "
                    "malicious content and bypass keyword-based security scanners."
                ),
            })

        if feats["has_port"] > 0:
            risk_factors.append({
                "factor": "Non-Standard Port in URL",
                "severity": "MEDIUM",
                "explanation": (
                    "An explicit port number is present in the URL. Phishing pages are "
                    "often hosted on non-standard ports to evade firewall rules."
                ),
            })

        if feats["uses_https"] == 0:
            risk_factors.append({
                "factor": "No HTTPS — Unencrypted Connection",
                "severity": "MEDIUM",
                "explanation": (
                    "The URL uses plain HTTP, meaning any data you submit (passwords, card numbers) "
                    "is transmitted in cleartext. Modern legitimate sites use HTTPS."
                ),
            })

        if feats["has_exec_extension"] > 0:
            detected_in.append("PATH")
            risk_factors.append({
                "factor": "Executable / Script File Extension in Path",
                "severity": "HIGH",
                "explanation": (
                    "The URL path ends with an executable or script extension (.exe, .php, .bat, etc.). "
                    "This is a strong indicator of malware delivery or phishing page infrastructure."
                ),
            })

        if feats["suspicious_kw_count"] >= 2:
            detected_in.append("PATH")
            risk_factors.append({
                "factor": f"Multiple Authentication Keywords in URL ({int(feats['suspicious_kw_count'])} found)",
                "severity": "MEDIUM",
                "explanation": (
                    "The URL contains multiple authentication-related keywords "
                    "(e.g. login, verify, account, password). Legitimate URLs rarely chain these together."
                ),
            })
        elif feats["suspicious_kw_count"] == 1:
            risk_factors.append({
                "factor": "Suspicious Keyword in URL Path",
                "severity": "LOW",
                "explanation": (
                    "The URL contains a credential or authentication keyword (login, verify, account, etc.)."
                ),
            })

        if feats["url_length"] > 100:
            risk_factors.append({
                "factor": f"Abnormally Long URL ({int(feats['url_length'])} characters)",
                "severity": "LOW",
                "explanation": (
                    "Unusually long URLs are often constructed to hide the malicious domain "
                    "and add authentic-looking path segments to appear legitimate."
                ),
            })

        if feats["query_param_count"] >= 5:
            risk_factors.append({
                "factor": f"High Query Parameter Count ({int(feats['query_param_count'])} params)",
                "severity": "LOW",
                "explanation": (
                    "A large number of query parameters can be used to pass tracking tokens, "
                    "redirect targets, or obfuscated payloads."
                ),
            })

        # ── Trusted domain (positive signal) ─────────────────────────────────
        if feats["is_trusted_domain"] > 0 and risk_score < 40:
            risk_factors.append({
                "factor": "Recognised Trusted Domain",
                "severity": "INFO",
                "explanation": (
                    "The registered domain matches a known-safe list of major legitimate sites, "
                    "which reduces phishing probability."
                ),
            })

        # ── Deduplicate detected_in ───────────────────────────────────────────
        detected_in = list(dict.fromkeys(detected_in))

        # ── Recommendations ───────────────────────────────────────────────────
        recommendations = _build_recommendations(feats, risk_score)

        return {
            "detected_in":    detected_in,
            "risk_factors":   risk_factors,
            "recommendations": recommendations,
        }




def _build_recommendations(feats: Dict[str, float], risk_score: float) -> List[str]:
    recs = []

    if risk_score >= 75:
        recs += [
            "🚨 HIGH RISK: Do NOT open or interact with this URL.",
            "❌ Never enter passwords, OTPs, or financial details on this page.",
            "✅ Close the browser tab immediately.",
            "✅ Report this URL to your IT/Security team or via phishtank.com.",
        ]
    elif risk_score >= 40:
        recs += [
            "⚠️ SUSPICIOUS: Proceed with extreme caution.",
            "❌ Do not submit any personal or financial information.",
            "✅ Independently verify the URL by navigating to the official website manually.",
            "✅ Check the sender or source that shared this link.",
        ]
    else:
        recs += [
            "✅ No critical phishing indicators detected.",
            "ℹ️ Always hover over links to preview the destination before clicking.",
        ]

    if feats.get("uses_https", 0) == 0:
        recs.append("❌ Avoid submitting any data — this connection is not encrypted (HTTP).")

    if feats.get("is_shortened", 0) > 0:
        recs.append("✅ Use a URL expander (e.g. checkshorturl.com) to reveal the real destination before clicking.")

    if feats.get("has_exec_extension", 0) > 0:
        recs.append("🚨 Do not download or execute any file from this URL.")

    return recs
