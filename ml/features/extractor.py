import re
import math
import numpy as np
from typing import Dict, Any, List
from urllib.parse import urlparse, unquote

# ── Suspicious signals ──────────────────────────────────────────────────────
import re
import math
import numpy as np
from typing import Dict, Any, List
from urllib.parse import urlparse, unquote

# ── Suspicious signals ──────────────────────────────────────────────────────
SUSPICIOUS_KEYWORDS = [
    'login', 'signin', 'verify', 'account', 'banking', 'secure', 'update',
    'password', 'credential', 'confirm', 'paypal', 'chase', 'wellsfargo',
    'appleid', 'microsoft', 'netflix', 'amazon', 'support', 'billing',
    'auth', 'authenticate', 'validation', 'suspend', 'restore', 'unlock',
    'webscr', 'checkout', 'purchase', 'transaction', 'refund', 'citi',
    'docusign', 'sharepoint', 'onedrive', 'outlook', 'icloud', 'notice',
    'claim', 'token', 'session', 'wallet', 'security', 'alert', 'dispute'
]

SUSPICIOUS_TLDS = [
    'xyz', 'top', 'live', 'click', 'info', 'zip', 'online', 'site',
    'work', 'tk', 'ml', 'cf', 'ga', 'gq', 'pw', 'cc', 'ru', 'cn',
    'bid', 'loan', 'men', 'download', 'win', 'stream', 'racing',
    'cfd', 'icu', 'rest', 'cam', 'monster', 'buzz', 'quest', 'cyou',
    'shop', 'space', 'club', 'digital', 'agency', 'best', 'fit'
]

URL_SHORTENERS = [
    'bit.ly', 'goo.gl', 'tinyurl', 't.co', 'ow.ly', 'is.gd',
    'rebrand.ly', 'buff.ly', 'short.link', 'tiny.cc', 'cutt.ly',
    'rb.gy', 'shorturl.at'
]

EXEC_EXTENSIONS = ['.php', '.exe', '.cgi', '.asp', '.aspx', '.jsp', '.bat', '.sh', '.py', '.pl']

# Mapping of brand names to their legitimate registered domain roots
OFFICIAL_BRAND_DOMAINS = {
    'paypal': ['paypal.com', 'paypal.me'],
    'apple': ['apple.com', 'icloud.com'],
    'google': ['google.com', 'youtube.com', 'gmail.com'],
    'microsoft': ['microsoft.com', 'office.com', 'office365.com', 'live.com', 'outlook.com', 'azure.com', 'msn.com', 'windows.net'],
    'amazon': ['amazon.com', 'aws.amazon.com'],
    'netflix': ['netflix.com'],
    'facebook': ['facebook.com', 'fb.com'],
    'instagram': ['instagram.com'],
    'twitter': ['twitter.com', 'x.com'],
    'linkedin': ['linkedin.com'],
    'chase': ['chase.com'],
    'wellsfargo': ['wellsfargo.com'],
    'citibank': ['citibank.com', 'citi.com'],
    'bankofamerica': ['bankofamerica.com', 'bofa.com'],
    'usps': ['usps.com', 'usps.gov'],
    'fedex': ['fedex.com'],
    'dhl': ['dhl.com'],
    'ups': ['ups.com'],
    'irs': ['irs.gov'],
    'ebay': ['ebay.com'],
    'dropbox': ['dropbox.com'],
    'whatsapp': ['whatsapp.com'],
    'telegram': ['telegram.org', 't.me'],
    'steam': ['steampowered.com', 'steamcommunity.com'],
    'roblox': ['roblox.com'],
    'coinbase': ['coinbase.com'],
    'binance': ['binance.com'],
    'stripe': ['stripe.com'],
    'docusign': ['docusign.com', 'docusign.net'],
    'metamask': ['metamask.io'],
}

BRAND_NAMES = list(OFFICIAL_BRAND_DOMAINS.keys())

# Regex patterns for common character-replacement typosquatting
TYPOSQUAT_PATTERNS = [
    r'p[a4@]yp[a4@][l1|i]', r'g[0o]{2}gl[e3]', r'm[i1l|]cr[o0]s[o0]ft',
    r'am[a4@]z[o0]n', r'n[e3]tfl[i1l|]x', r'f[a4@]c[e3]b[o0]{2}k',
    r'ch[a4@]s[e3]', r'w[e3]llsf[a4@]rg[o0]', r'a[p1]pl[e3]',
    r'b[a4@]nk[o0]f[a4@]m[e3]r[i1]c[a4@]', r'c[i1]t[i1]', r'd[o0]c[u3]s[i1]gn'
]

# Alexa-style top-1000 domain whitelist (sample of known-safe roots)
TRUSTED_DOMAINS = {
    'google.com', 'youtube.com', 'facebook.com', 'amazon.com', 'wikipedia.org',
    'twitter.com', 'instagram.com', 'linkedin.com', 'reddit.com', 'github.com',
    'stackoverflow.com', 'apple.com', 'microsoft.com', 'netflix.com', 'paypal.com',
    'ebay.com', 'dropbox.com', 'whatsapp.com', 'nytimes.com', 'bbc.com',
    'cnn.com', 'techcrunch.com', 'python.org', 'docs.python.org', 'fastapi.tiangolo.com'
}


# ── Utility ──────────────────────────────────────────────────────────────────
def calculate_entropy(text: str) -> float:
    """Shannon entropy — detects DGA-style random domain strings."""
    if not text:
        return 0.0
    prob = [float(text.count(c)) / len(text) for c in set(text)]
    return float(-sum(p * math.log2(p) for p in prob if p > 0))


def _get_registered_domain(netloc: str) -> str:
    """Return the registered domain (last two dot-parts) from a netloc."""
    parts = netloc.split('.')
    if len(parts) >= 2:
        return '.'.join(parts[-2:])
    return netloc


# ── Main extractor (35 features) ─────────────────────────────────────────────
def extract_url_features(url_str: str) -> Dict[str, float]:
    """
    Extracts 35 structural, lexical, domain, and heuristic features from a URL
    for phishing detection.
    """
    url_lower = url_str.lower().strip()
    try:
        parsed = urlparse(url_lower if '://' in url_lower else f'http://{url_lower}')
    except Exception:
        parsed = urlparse('http://invalid-url-parse-fallback.com')

    netloc = parsed.netloc or parsed.path.split('/')[0]
    # Strip port from netloc for domain analysis
    domain_no_port = netloc.split(':')[0]
    path = parsed.path
    query = parsed.query
    fragment = parsed.fragment

    # Subdomain parts
    domain_parts = domain_no_port.split('.')
    registered_domain = _get_registered_domain(domain_no_port)
    subdomains = domain_parts[:-2] if len(domain_parts) > 2 else []
    tld = domain_parts[-1] if domain_parts else ''

    # ── Feature 1: URL total length ──────────────────────────────────────────
    url_length = float(len(url_str))

    # ── Feature 2: Domain length ─────────────────────────────────────────────
    domain_length = float(len(domain_no_port))

    # ── Feature 3: Path length ───────────────────────────────────────────────
    path_length = float(len(path))

    # ── Feature 4: Number of dots ────────────────────────────────────────────
    dot_count = float(url_str.count('.'))

    # ── Feature 5: Number of hyphens ─────────────────────────────────────────
    hyphen_count = float(url_str.count('-'))

    # ── Feature 6: Number of slashes ─────────────────────────────────────────
    slash_count = float(url_str.count('/'))

    # ── Feature 7: Special character count (@?=%&_~#) ───────────────────────
    special_char_count = float(len(re.findall(r'[@?=%&_~#]', url_str)))

    # ── Feature 8: Digit count ───────────────────────────────────────────────
    digit_count = float(len(re.findall(r'\d', url_str)))

    # ── Feature 9: Has @ symbol ──────────────────────────────────────────────
    has_at_symbol = 1.0 if '@' in url_str else 0.0

    # ── Feature 10: Has query string ─────────────────────────────────────────
    has_query = 1.0 if query else 0.0

    # ── Feature 11: Has fragment ─────────────────────────────────────────────
    has_fragment = 1.0 if fragment else 0.0

    # ── Feature 12: URL path depth ───────────────────────────────────────────
    url_depth = float(len([p for p in path.split('/') if p]))

    # ── Feature 13: Uses HTTPS ───────────────────────────────────────────────
    uses_https = 1.0 if parsed.scheme == 'https' else 0.0

    # ── Feature 14: IP address as domain ─────────────────────────────────────
    is_ip = 1.0 if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain_no_port) else 0.0

    # ── Feature 15: Suspicious keyword count ─────────────────────────────────
    suspicious_kw_count = float(sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in url_lower))

    # ── Feature 16: URL shortening service ───────────────────────────────────
    is_shortened = 1.0 if any(s in domain_no_port for s in URL_SHORTENERS) else 0.0

    # ── Feature 17: Suspicious TLD ───────────────────────────────────────────
    has_suspicious_tld = 1.0 if tld in SUSPICIOUS_TLDS else 0.0

    # ── Feature 18: Domain entropy (Shannon) ─────────────────────────────────
    domain_entropy = calculate_entropy(domain_no_port)

    # ── Feature 19: Subdomain count ──────────────────────────────────────────
    subdomain_count = float(len(subdomains))

    # ── Feature 20: Double slash in path (redirect indicator) ────────────────
    has_double_slash = 1.0 if '//' in path else 0.0

    # ── Feature 21: Port explicitly specified ────────────────────────────────
    has_port = 1.0 if ':' in netloc and netloc.split(':')[-1].isdigit() else 0.0

    # ── Feature 22: Hex-encoded characters (%xx) ─────────────────────────────
    has_hex_encoding = 1.0 if re.search(r'%[0-9a-fA-F]{2}', url_str) else 0.0

    # ── Feature 23: Punycode / IDN homograph (xn--) ──────────────────────────
    has_punycode = 1.0 if 'xn--' in url_lower else 0.0

    # ── Feature 24: Brand name in subdomain (not in legitimate brand domain) ─
    brand_in_subdomain = 0.0
    if subdomains:
        subdomain_str = '.'.join(subdomains).lower()
        for brand, official_domains in OFFICIAL_BRAND_DOMAINS.items():
            if brand in subdomain_str and registered_domain not in official_domains:
                brand_in_subdomain = 1.0
                break

    # ── Feature 25: Domain brand mismatch / typosquatting ─────────────────────
    domain_brand_mismatch = 0.0
    is_official_brand_dom = any(registered_domain in off_doms for off_doms in OFFICIAL_BRAND_DOMAINS.values())

    if not is_official_brand_dom:
        for brand, official_domains in OFFICIAL_BRAND_DOMAINS.items():
            if brand in domain_no_port:
                domain_brand_mismatch = 1.0
                break

        if domain_brand_mismatch == 0.0:
            for pat in TYPOSQUAT_PATTERNS:
                if re.search(pat, domain_no_port):
                    domain_brand_mismatch = 1.0
                    break

    # ── Feature 26: Numeric-heavy domain (>30% digits in registered domain) ──
    reg_domain_root = registered_domain.split('.')[0]
    digit_ratio_domain = (
        float(len(re.findall(r'\d', reg_domain_root))) / float(len(reg_domain_root))
        if reg_domain_root else 0.0
    )
    numeric_heavy_domain = 1.0 if digit_ratio_domain > 0.3 else 0.0

    # ── Feature 27: Executable file extension in path ────────────────────────
    has_exec_extension = 1.0 if any(path.endswith(ext) for ext in EXEC_EXTENSIONS) else 0.0

    # ── Feature 28: Path token count (words in path) ─────────────────────────
    path_token_count = float(len([t for t in re.split(r'[/\-_=&?]', path) if t]))

    # ── Feature 29: Digit-to-alpha ratio in full URL ─────────────────────────
    alpha_count = len(re.findall(r'[a-zA-Z]', url_str))
    digit_alpha_ratio = (
        float(digit_count) / float(alpha_count) if alpha_count > 0 else 0.0
    )

    # ── Feature 30: Trusted domain whitelist match ────────────────────────────
    is_trusted_domain = 1.0 if registered_domain in TRUSTED_DOMAINS else 0.0

    # ── Feature 31: Vowel-to-consonant ratio in domain (DGA indicator) ───────
    vowels = len(re.findall(r'[aeiou]', reg_domain_root))
    consonants = len(re.findall(r'[bcdfghjklmnpqrstvwxyz]', reg_domain_root))
    vowel_ratio = float(vowels) / float(vowels + consonants) if (vowels + consonants) > 0 else 0.5
    # Low vowel ratio (< 0.25) is a DGA signal
    dga_vowel_signal = 1.0 if vowel_ratio < 0.25 else 0.0

    # ── Feature 32: Consecutive consonant clusters (DGA indicator) ───────────
    consonant_clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{4,}', reg_domain_root)
    has_consonant_cluster = 1.0 if consonant_clusters else 0.0

    # ── Feature 33: Query string length ──────────────────────────────────────
    query_length = float(len(query))

    # ── Feature 34: Number of query parameters ───────────────────────────────
    query_param_count = float(len(query.split('&'))) if query else 0.0

    # ── Feature 35: Hyphen count in domain only (not full URL) ───────────────
    domain_hyphen_count = float(domain_no_port.count('-'))

    return {
        # Structural / length
        "url_length": url_length,
        "domain_length": domain_length,
        "path_length": path_length,
        "dot_count": dot_count,
        "hyphen_count": hyphen_count,
        "slash_count": slash_count,
        "special_char_count": special_char_count,
        "digit_count": digit_count,
        # Binary presence flags
        "has_at_symbol": has_at_symbol,
        "has_query": has_query,
        "has_fragment": has_fragment,
        "uses_https": uses_https,
        "is_ip": is_ip,
        "is_shortened": is_shortened,
        "has_suspicious_tld": has_suspicious_tld,
        "has_double_slash": has_double_slash,
        "has_port": has_port,
        "has_hex_encoding": has_hex_encoding,
        "has_punycode": has_punycode,
        "has_exec_extension": has_exec_extension,
        "is_trusted_domain": is_trusted_domain,
        # Lexical counts
        "url_depth": url_depth,
        "suspicious_kw_count": suspicious_kw_count,
        "subdomain_count": subdomain_count,
        "path_token_count": path_token_count,
        "query_length": query_length,
        "query_param_count": query_param_count,
        "domain_hyphen_count": domain_hyphen_count,
        # Domain / brand heuristics
        "brand_in_subdomain": brand_in_subdomain,
        "domain_brand_mismatch": domain_brand_mismatch,
        "numeric_heavy_domain": numeric_heavy_domain,
        "digit_alpha_ratio": digit_alpha_ratio,
        # Entropy / DGA signals
        "domain_entropy": domain_entropy,
        "dga_vowel_signal": dga_vowel_signal,
        "has_consonant_cluster": has_consonant_cluster,
    }

