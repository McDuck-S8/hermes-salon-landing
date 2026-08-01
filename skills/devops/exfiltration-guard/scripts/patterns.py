"""
Exfiltration Guard - Regex Patterns for Secret/PII Detection
Patterns for API keys, PII, private keys, and high-entropy strings.
"""

import re

# =============================================================================
# API KEY PATTERNS (CRITICAL SEVERITY)
# =============================================================================

API_KEY_PATTERNS = {
    # Anthropic API Keys
    "anthropic_api_key": {
        "pattern": r"sk-ant-[a-zA-Z0-9\-_]{20,}",
        "severity": "CRITICAL",
        "description": "Anthropic API Key (sk-ant-...)",
        "examples": ["sk-ant-api03-abcdefghijklmnopqrstuvwxyz"]
    },
    # OpenAI API Keys (various formats)
    "openai_api_key": {
        "pattern": r"sk-[a-zA-Z0-9]{20,}",
        "severity": "CRITICAL",
        "description": "OpenAI API Key (sk-...)",
        "examples": ["sk-abcdefghijklmnopqrstuvwxyz123456", "sk-proj-abcdefghijklmnopqrstuvwxyz"]
    },
    # GitHub Personal Access Tokens
    "github_pat_classic": {
        "pattern": r"ghp_[a-zA-Z0-9]{36}",
        "severity": "CRITICAL",
        "description": "GitHub Personal Access Token (classic)",
        "examples": ["ghp_abcdefghijklmnopqrstuvwxyz123456"]
    },
    "github_pat_fine_grained": {
        "pattern": r"github_pat_[a-zA-Z0-9_]{82}",
        "severity": "CRITICAL",
        "description": "GitHub Fine-grained PAT",
        "examples": ["github_pat_abcdefghijklmnopqrstuvwxyz123456789012345678901234"]
    },
    "github_oauth_token": {
        "pattern": r"gho_[a-zA-Z0-9]{36}",
        "severity": "CRITICAL",
        "description": "GitHub OAuth Token",
        "examples": ["gho_abcdefghijklmnopqrstuvwxyz123456"]
    },
    "github_app_token": {
        "pattern": r"ghs_[a-zA-Z0-9]{36}",
        "severity": "CRITICAL",
        "description": "GitHub App Token",
        "examples": ["ghs_abcdefghijklmnopqrstuvwxyz123456"]
    },
    "github_refresh_token": {
        "pattern": r"ghr_[a-zA-Z0-9]{36}",
        "severity": "CRITICAL",
        "description": "GitHub Refresh Token",
        "examples": ["ghr_abcdefghijklmnopqrstuvwxyz123456"]
    },
    # Slack Tokens
    "slack_bot_token": {
        "pattern": r"xoxb-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}",
        "severity": "CRITICAL",
        "description": "Slack Bot Token (xoxb-)",
        "examples": ["xoxb-123456789012-1234567890123-abcdefghijklmnopqrstuv"]
    },
    "slack_user_token": {
        "pattern": r"xoxp-[0-9]{10,13}-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{32}",
        "severity": "CRITICAL",
        "description": "Slack User Token (xoxp-)",
        "examples": ["xoxp-123456789012-123456789012-123456789012-abcdefghijklmnopqrstuvwx"]
    },
    "slack_app_token": {
        "pattern": r"xapp-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}",
        "severity": "CRITICAL",
        "description": "Slack App Token (xapp-)",
        "examples": ["xapp-123456789012-1234567890123-abcdefghijklmnopqrstuv"]
    },
    "slack_signing_secret": {
        "pattern": r"[0-9a-f]{32}",
        "severity": "CRITICAL",
        "description": "Slack Signing Secret (32-char hex)",
        "examples": ["abcdef1234567890abcdef1234567890"]
    },
    # AWS Keys
    "aws_access_key_id": {
        "pattern": r"AKIA[0-9A-Z]{16}",
        "severity": "CRITICAL",
        "description": "AWS Access Key ID",
        "examples": ["AKIAIOSFODNN7EXAMPLE"]
    },
    "aws_secret_access_key": {
        "pattern": r"[A-Za-z0-9/+=]{40}",
        "severity": "CRITICAL",
        "description": "AWS Secret Access Key (40 chars)",
        "examples": ["wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"]
    },
    "aws_session_token": {
        "pattern": r"Fwo[0-9A-Za-z/+]+",
        "severity": "CRITICAL",
        "description": "AWS Session Token",
        "examples": ["FwoGZXIvYXdzEF0aCXVv...long_token"]
    },
    # Google Cloud / GCP
    "gcp_api_key": {
        "pattern": r"AIza[0-9A-Za-z\-_]{35}",
        "severity": "CRITICAL",
        "description": "Google API Key",
        "examples": ["AIzaSyBdVl-cTICSwYKrZ95SuvNw7dbMuZsBxGk"]
    },
    "gcp_service_account_key": {
        "pattern": r"-----BEGIN PRIVATE KEY-----[\s\S]*?-----END PRIVATE KEY-----",
        "severity": "CRITICAL",
        "description": "GCP Service Account Private Key",
        "examples": ["-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQD..."]
    },
    # Stripe
    "stripe_secret_key": {
        "pattern": r"sk_live_[a-zA-Z0-9]{24,}",
        "severity": "CRITICAL",
        "description": "Stripe Secret Key (live)",
        "examples": ["sk_live_abcdefghijklmnopqrstuvwx"]
    },
    "stripe_test_key": {
        "pattern": r"sk_test_[a-zA-Z0-9]{24,}",
        "severity": "HIGH",
        "description": "Stripe Secret Key (test)",
        "examples": ["sk_test_abcdefghijklmnopqrstuvwx"]
    },
    "stripe_publishable_key": {
        "pattern": r"pk_live_[a-zA-Z0-9]{24,}",
        "severity": "MEDIUM",
        "description": "Stripe Publishable Key (live)",
        "examples": ["pk_live_abcdefghijklmnopqrstuvwx"]
    },
    # Twilio
    "twilio_account_sid": {
        "pattern": r"AC[a-zA-Z0-9]{32}",
        "severity": "CRITICAL",
        "description": "Twilio Account SID",
        "examples": ["ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"]
    },
    "twilio_auth_token": {
        "pattern": r"[a-zA-Z0-9]{32}",
        "severity": "CRITICAL",
        "description": "Twilio Auth Token",
        "examples": ["abcdefghijklmnopqrstuvwxyz123456"]
    },
    # SendGrid
    "sendgrid_api_key": {
        "pattern": r"SG\.[a-zA-Z0-9_\-]{22}\.[a-zA-Z0-9_\-]{43}",
        "severity": "CRITICAL",
        "description": "SendGrid API Key",
        "examples": ["SG.abcdefghijklmnopqrst.uvwxyz1234567890abcdefghij"]
    },
    # Discord
    "discord_bot_token": {
        "pattern": r"[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}",
        "severity": "CRITICAL",
        "description": "Discord Bot Token",
        "examples": ["MTAxMjM0NTY3ODkwMTIzNDU2NzAu.GhIjKl.MnoPqRsTuVwXyZ1234567890AbCdEfGhIjKlMnOpQrStUvWxYz"]
    },
    # Notion
    "notion_integration_token": {
        "pattern": r"secret_[a-zA-Z0-9]{43}",
        "severity": "CRITICAL",
        "description": "Notion Integration Token",
        "examples": ["secret_abcdefghijklmnopqrstuvwxyz1234567890123"]
    },
    # Vercel
    "vercel_token": {
        "pattern": r"[a-zA-Z0-9]{24}_[a-zA-Z0-9]{32}",
        "severity": "CRITICAL",
        "description": "Vercel Token",
        "examples": ["abcdefghijklmnopqrstuvwx_1234567890abcdefghijklmnopqrstuv"]
    },
    # Generic high-entropy strings (potential secrets)
    "high_entropy_base64": {
        "pattern": r"[A-Za-z0-9+/]{40,}={0,2}",
        "severity": "HIGH",
        "description": "High-entropy Base64 string (possible secret)",
        "examples": ["SGVsbG8gV29ybGQhSGVsbG8gV29ybGQhSGVsbG8gV29ybGQh"]
    },
    "high_entropy_hex": {
        "pattern": r"[0-9a-fA-F]{40,}",
        "severity": "HIGH",
        "description": "High-entropy hex string (possible secret/hash)",
        "examples": ["a1b2c3d4e5f6789012345678901234567890abcd"]
    },
    # Generic API key pattern (fallback)
    "generic_api_key": {
        "pattern": r"(?i)(api[_-]?key|apikey|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*['\"]?[a-zA-Z0-9_\-]{20,}['\"]?",
        "severity": "HIGH",
        "description": "Generic API key/secret pattern",
        "examples": ["api_key = 'sk-abcdefghijklmnopqrst'"]
    },
}

# =============================================================================
# PII PATTERNS (MEDIUM/HIGH SEVERITY)
# =============================================================================

PII_PATTERNS = {
    # Email addresses
    "email": {
        "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "severity": "MEDIUM",
        "description": "Email address",
        "examples": ["user@example.com", "john.doe@company.com"]
    },
    # Phone numbers (various formats)
    "phone_us": {
        "pattern": r"(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})",
        "severity": "MEDIUM",
        "description": "US Phone number",
        "examples": ["+1-555-123-4567", "(555) 123-4567", "555.123.4567"]
    },
    "phone_international": {
        "pattern": r"\+[1-9]\d{1,14}",
        "severity": "MEDIUM",
        "description": "International phone number (E.164)",
        "examples": ["+442071234567", "+15551234567"]
    },
    # Credit Card Numbers (Luhn-validated would be better, but regex is first pass)
    "credit_card_visa": {
        "pattern": r"\b4[0-9]{3}[- ]?[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}\b",
        "severity": "HIGH",
        "description": "Visa credit card",
        "examples": ["4111 1111 1111 1111", "4111-1111-1111-1111"]
    },
    "credit_card_mastercard": {
        "pattern": r"\b5[1-5][0-9]{2}[- ]?[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}\b",
        "severity": "HIGH",
        "description": "Mastercard credit card",
        "examples": ["5555 5555 5555 5555"]
    },
    "credit_card_amex": {
        "pattern": r"\b3[47][0-9]{2}[- ]?[0-9]{6}[- ]?[0-9]{5}\b",
        "severity": "HIGH",
        "description": "American Express credit card",
        "examples": ["3782 822463 10005"]
    },
    "credit_card_generic": {
        "pattern": r"\b(?:\d[ -]*?){13,16}\b",
        "severity": "HIGH",
        "description": "Generic credit card number (13-16 digits)",
        "examples": ["1234 5678 9012 3456"]
    },
    # SSN (US)
    "ssn_us": {
        "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
        "severity": "HIGH",
        "description": "US Social Security Number",
        "examples": ["123-45-6789"]
    },
    # IP Addresses (could be sensitive in some contexts)
    "ipv4_address": {
        "pattern": r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
        "severity": "LOW",
        "description": "IPv4 address",
        "examples": ["192.168.1.1", "10.0.0.1"]
    },
    "ipv6_address": {
        "pattern": r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b",
        "severity": "LOW",
        "description": "IPv6 address",
        "examples": ["2001:0db8:85a3:0000:0000:8a2e:0370:7334"]
    },
    # JWT Tokens
    "jwt_token": {
        "pattern": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
        "severity": "HIGH",
        "description": "JWT Token",
        "examples": ["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"]
    },
}

# =============================================================================
# PRIVATE KEY PATTERNS (CRITICAL SEVERITY)
# =============================================================================

PRIVATE_KEY_PATTERNS = {
    "rsa_private_key": {
        "pattern": r"-----BEGIN RSA PRIVATE KEY-----[\s\S]*?-----END RSA PRIVATE KEY-----",
        "severity": "CRITICAL",
        "description": "RSA Private Key",
        "examples": ["-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA..."]
    },
    "openssh_private_key": {
        "pattern": r"-----BEGIN OPENSSH PRIVATE KEY-----[\s\S]*?-----END OPENSSH PRIVATE KEY-----",
        "severity": "CRITICAL",
        "description": "OpenSSH Private Key",
        "examples": ["-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXktdjE..."]
    },
    "generic_private_key": {
        "pattern": r"-----BEGIN (?:RSA|DSA|EC|OPENSSH|PGP|ENCRYPTED)? ?PRIVATE KEY-----[\s\S]*?-----END (?:RSA|DSA|EC|OPENSSH|PGP|ENCRYPTED)? ?PRIVATE KEY-----",
        "severity": "CRITICAL",
        "description": "Generic Private Key (PEM format)",
        "examples": ["-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQD..."]
    },
    "public_key": {
        "pattern": r"-----BEGIN (?:RSA|DSA|EC|OPENSSH|PGP)? ?PUBLIC KEY-----[\s\S]*?-----END (?:RSA|DSA|EC|OPENSSH|PGP)? ?PUBLIC KEY-----",
        "severity": "MEDIUM",
        "description": "Public Key (PEM format)",
        "examples": ["-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..."]
    },
    "ssh_public_key": {
        "pattern": r"ssh-(?:rsa|dsa|ecdsa|ed25519)\s+[A-Za-z0-9+/]+[=]{0,3}",
        "severity": "MEDIUM",
        "description": "SSH Public Key",
        "examples": ["ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC..."]
    },
    "pgp_private_key": {
        "pattern": r"-----BEGIN PGP PRIVATE KEY BLOCK-----[\s\S]*?-----END PGP PRIVATE KEY BLOCK-----",
        "severity": "CRITICAL",
        "description": "PGP Private Key Block",
        "examples": ["-----BEGIN PGP PRIVATE KEY BLOCK-----\nlQOYBF..."]
    },
}

# =============================================================================
# COMPILED PATTERNS (for performance)
# =============================================================================

def compile_patterns():
    """Compile all regex patterns for performance."""
    compiled = {}
    
    for category, patterns in {
        "api_keys": API_KEY_PATTERNS,
        "pii": PII_PATTERNS,
        "private_keys": PRIVATE_KEY_PATTERNS,
    }.items():
        compiled[category] = {}
        for name, config in patterns.items():
            try:
                compiled[category][name] = {
                    "pattern": re.compile(config["pattern"], re.IGNORECASE | re.MULTILINE),
                    "severity": config["severity"],
                    "description": config["description"],
                    "examples": config.get("examples", [])
                }
            except re.error as e:
                print(f"WARNING: Failed to compile pattern {name}: {e}")
    
    return compiled

COMPILED_PATTERNS = compile_patterns()

# =============================================================================
# SEVERITY LEVELS
# =============================================================================

SEVERITY_LEVELS = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1
}

SEVERITY_COLORS = {
    "CRITICAL": "\033[91m",  # Red
    "HIGH": "\033[93m",      # Yellow
    "MEDIUM": "\033[94m",    # Blue
    "LOW": "\033[92m",       # Green
    "RESET": "\033[0m"
}

def get_severity_level(severity: str) -> int:
    """Get numeric severity level for comparison."""
    return SEVERITY_LEVELS.get(severity.upper(), 0)

# =============================================================================
# PATTERN MATCHING FUNCTIONS
# =============================================================================

def find_matches(content: str, min_severity: str = "LOW") -> list[dict]:
    """
    Find all pattern matches in content.
    
    Args:
        content: Text content to scan
        min_severity: Minimum severity level to report ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    
    Returns:
        List of match dictionaries with keys: pattern_name, category, severity, description, match, start, end
    """
    min_level = get_severity_level(min_severity)
    matches = []
    
    for category, patterns in COMPILED_PATTERNS.items():
        for pattern_name, config in patterns.items():
            if get_severity_level(config["severity"]) < min_level:
                continue
            
            pattern = config["pattern"]
            for match in pattern.finditer(content):
                matches.append({
                    "pattern_name": pattern_name,
                    "category": category,
                    "severity": config["severity"],
                    "description": config["description"],
                    "match": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "context": content[max(0, match.start()-50):match.end()+50]
                })
    
    # Sort by severity (highest first), then by position
    severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    matches.sort(key=lambda m: (-severity_order.get(m["severity"], 0), m["start"]))
    
    return matches

def scan_outbound(content: str, min_severity: str = "LOW") -> dict:
    """
    Main scanning function - scans outbound content for secrets/PII.
    
    Args:
        content: Text content to scan
        min_severity: Minimum severity to report
    
    Returns:
        Dict with:
        - blocked: bool (True if any CRITICAL or HIGH severity found)
        - matches: list of matches found
        - max_severity: highest severity found
        - match_count: total matches found
    """
    matches = find_matches(content, min_severity)
    
    max_severity = "LOW"
    blocked = False
    
    if matches:
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        max_severity = max(matches, key=lambda m: severity_order.get(m["severity"], 0))["severity"]
        blocked = severity_order.get(max_severity, 0) >= 3  # HIGH or CRITICAL
    
    return {
        "blocked": blocked,
        "matches": matches,
        "max_severity": max_severity,
        "match_count": len(matches)
    }

def redact_content(content: str, matches: list[dict] = None, replacement: str = "[REDACTED]") -> str:
    """
    Redact matched patterns from content.
    
    Args:
        content: Original content
        matches: Optional pre-computed matches (will scan if not provided)
        replacement: Replacement string for matches
    
    Returns:
        Redacted content
    """
    if matches is None:
        scan_result = scan_outbound(content)
        matches = scan_result["matches"]
    
    if not matches:
        return content
    
    # Sort matches by start position (reverse for replacement)
    matches_sorted = sorted(matches, key=lambda m: m["start"], reverse=True)
    
    result = content
    for match in matches_sorted:
        start, end = match["start"], match["end"]
        result = result[:start] + replacement + result[end:]
    
    return result

# =============================================================================
# TESTING / DEMO
# =============================================================================

if __name__ == "__main__":
    test_content = """
    Here's my API key: sk-ant-api03-abcdefghijklmnopqrstuvwxyz123456
    And my email: john.doe@example.com
    My phone: +1-555-123-4567
    Credit card: 4111-1111-1111-1111
    SSH key: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...
    API_KEY = "sk-abcdefghijklmnopqrstuvwxyz123456"
    """
    
    print("=" * 60)
    print("EXFILTRATION GUARD - PATTERN SCANNER TEST")
    print("=" * 60)
    
    result = scan_outbound(test_content)
    
    print(f"\nBlocked: {result['blocked']}")
    print(f"Max Severity: {result['max_severity']}")
    print(f"Match Count: {result['match_count']}")
    print(f"\nMatches found:")
    
    for match in result["matches"]:
        color = SEVERITY_COLORS.get(match["severity"], "")
        reset = SEVERITY_COLORS["RESET"]
        print(f"  {color}[{match['severity']}]{reset} {match['pattern_name']} ({match['category']})")
        print(f"       Match: {match['match'][:60]}{'...' if len(match['match']) > 60 else ''}")
        print(f"       Context: ...{match['context']}...")
        print()
    
    print("Redacted content:")
    print(redact_content(test_content, result["matches"]))