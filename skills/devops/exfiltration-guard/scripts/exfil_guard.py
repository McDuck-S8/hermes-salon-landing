#!/usr/bin/env python3
"""
Exfiltration Guard — scans outbound content for secrets, PII, API keys.
Blocks, logs to audit, alerts operator, quarantines suspicious content.
"""

import os
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
QUARANTINE_DIR = HERMES_HOME / "cache" / "exfil_quarantine"
QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

# ─── Patterns ──────────────────────────────────────────────────────────
# API Keys
API_KEY_PATTERNS = [
    (r"sk-ant-[a-zA-Z0-9_-]{95,}", "anthropic_api_key"),
    (r"sk-[a-zA-Z0-9]{48,}", "openai_api_key"),
    (r"ghp_[a-zA-Z0-9]{36,}", "github_pat"),
    (r"xoxb-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24,}", "slack_bot_token"),
    (r"xoxp-[0-9]{10,}-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{32,}", "slack_user_token"),
    (r"AKIA[0-9A-Z]{16}", "aws_access_key"),
    (r"[0-9a-zA-Z/+]{40}", "aws_secret_key"),  # generic
    (r"ya29\.[0-9A-Za-z_-]+", "google_oauth_token"),
    (r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*", "jwt_token"),
    (r"Bearer\s+[a-zA-Z0-9._-]{20,}", "bearer_token"),
    (r"api[_-]?key\s*[=:]\s*[\"']?[a-zA-Z0-9_-]{20,}", "generic_api_key"),
]

# PII
PII_PATTERNS = [
    (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "email"),
    (r"(?:\+\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}", "phone"),  # US/Intl format
    (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "credit_card"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "ssn"),
    (r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", "private_key"),
    (r"ssh-rsa\s+[A-Za-z0-9+/]+[=]{0,3}", "ssh_public_key"),
]

# Secrets in URLs/headers
EXFIL_PATTERNS = [
    (r"curl\s+[^\n]*https?://[^\s\"'`]*\$\w*(?:KEY|TOKEN|SECRET|PASSWORD)\w*", "exfil_curl_url"),
    (r"wget\s+[^\n]*https?://[^\s\"'`]*\$\w*(?:KEY|TOKEN|SECRET|PASSWORD)\w*", "exfil_wget_url"),
    (r"curl\s+[^\n]*(?:-H|--header)\s+[\"']Authorization:\s*\$\w*", "exfil_auth_header"),
]

ALL_PATTERNS = (
    [(p, t) for p, t in API_KEY_PATTERNS] +
    [(p, t) for p, t in PII_PATTERNS] +
    [(p, t) for p, t in EXFIL_PATTERNS]
)

COMPILED_PATTERNS = [(re.compile(p, re.IGNORECASE), t) for p, t in ALL_PATTERNS]


def scan_outbound(content: str, source: str = "unknown") -> Dict:
    """
    Scan content for exfiltration patterns.
    
    Returns:
        {
            "blocked": bool,
            "matches": [{"type": "...", "match": "...", "position": N}],
            "quarantine_id": str or None,
            "audit_entry": {...}
        }
    """
    matches = []
    content_lower = content.lower()
    
    for pattern, ptype in COMPILED_PATTERNS:
        for m in pattern.finditer(content):
            # Redact the match for logging
            match_text = m.group(0)
            if len(match_text) > 50:
                match_text = match_text[:50] + "..."
            matches.append({
                "type": ptype,
                "match": match_text,
                "position": m.start(),
                "length": len(m.group(0))
            })
    
    blocked = len(matches) > 0
    quarantine_id = None
    audit_entry = None
    
    if blocked:
        # Quarantine
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        quarantine_id = f"exfil_{timestamp}_{content_hash}"
        quarantine_file = QUARANTINE_DIR / f"{quarantine_id}.json"
        
        quarantine_data = {
            "id": quarantine_id,
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "content_length": len(content),
            "matches": matches,
            "content": content  # Full content for forensic analysis
        }
        quarantine_file.write_text(json.dumps(quarantine_data, indent=2), encoding="utf-8")
        
        # Audit entry
        audit_entry = {
            "event_id": quarantine_id,
            "timestamp": datetime.now().isoformat(),
            "type": "exfiltration_blocked",
            "source": source,
            "matches_count": len(matches),
            "match_types": [m["type"] for m in matches],
            "quarantine_file": str(quarantine_file),
            "content_hash": content_hash
        }
        
        # Log to audit log if enabled
        audit_log_path = HERMES_HOME / "logs" / "audit" / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
        audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit_entry) + "\n")
    
    return {
        "blocked": blocked,
        "matches": matches,
        "quarantine_id": quarantine_id,
        "audit_entry": audit_entry
    }


def scan_file(filepath: str, source: str = None) -> Dict:
    """Scan a file for exfiltration patterns."""
    path = Path(filepath)
    if not path.exists():
        return {"blocked": False, "error": f"File not found: {filepath}"}
    
    content = path.read_text(encoding="utf-8", errors="replace")
    src = source or f"file:{filepath}"
    return scan_outbound(content, src)


def check_telegram_message(text: str) -> Dict:
    """Wrapper for telegram_bridge integration."""
    return scan_outbound(text, source="telegram_bridge")


def check_http_request(url: str, headers: dict = None, body: str = None) -> Dict:
    """Wrapper for HTTP client integration."""
    combined = f"URL: {url}\n"
    if headers:
        combined += f"Headers: {json.dumps(headers)}\n"
    if body:
        combined += f"Body: {body}\n"
    return scan_outbound(combined, source="http_client")


def check_write_file(path: str, content: str) -> Dict:
    """Wrapper for write_file tool integration."""
    return scan_outbound(content, source=f"write_file:{path}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: exfil_guard.py <text|file:path>")
        sys.exit(1)
    
    arg = sys.argv[1]
    if arg.startswith("file:"):
        result = scan_file(arg[5:])
    else:
        result = scan_outbound(arg, source="cli")
    
    print(json.dumps(result, indent=2))
    if result["blocked"]:
        sys.exit(1)