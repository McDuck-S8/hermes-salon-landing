#!/usr/bin/env python3
"""
Unknown Error Classifier — автоматически классифицирует 'unknown' ошибки.
"""
import re
from typing import Optional

# Правила классификации по паттернам сообщений
UNKNOWN_RULES = [
    # Network errors
    (r"httpx\.connecterror|httpcore\.connecterror", "network_connection"),
    (r"connection.*refused|connection.*timeout|connection.*reset", "network_connection"),
    (r"dns|name.*resolution.*failed", "network_dns"),
    
    # Telegram errors
    (r"telegram\.error\.networkerror", "telegram_network"),
    (r"telegram\.error\.timedout", "telegram_timeout"),
    (r"telegram\.error\.retryafter", "telegram_rate_limit"),
    
    # API errors
    (r"tavily.*432|client.*error.*432", "tavily_rate_limit"),
    (r"rate.*limit|too.*many.*requests|429", "api_rate_limit"),
    (r"unauthorized|401|invalid.*token", "api_auth"),
    (r"forbidden|403", "api_forbidden"),
    (r"not.*found|404", "api_not_found"),
    (r"server.*error|500|502|503", "api_server_error"),
    
    # Tool errors
    (r"subprocess.*timeout|command.*timeout", "tool_timeout"),
    (r"permission.*denied|access.*denied", "tool_permission"),
    (r"file.*not.*found|no.*such.*file", "tool_file_not_found"),
    
    # Browser/automation
    (r"playwright|selenium|browser.*crash|navigator.*not.*found", "browser_error"),
    (r"element.*not.*found|selector.*not.*found", "browser_selector"),
    
    # Memory/resource
    (r"out.*of.*memory|memory.*error|oom", "resource_memory"),
    (r"disk.*full|no.*space.*left", "resource_disk"),
]

def classify_unknown(error_msg: str) -> Optional[str]:
    """Вернуть категорию для unknown ошибки или None."""
    if not error_msg:
        return None
    msg = error_msg.lower()
    for pattern, category in UNKNOWN_RULES:
        if re.search(pattern, msg, re.IGNORECASE):
            return category
    return None

def enrich_unknown(error_dict: dict) -> dict:
    """Добавить категорию к unknown ошибке."""
    if error_dict.get("error_type") == "unknown" or error_dict.get("issue_type") == "log_unknown":
        msg = error_dict.get("message", "") or error_dict.get("pattern", "")
        category = classify_unknown(msg)
        if category:
            error_dict["classified_as"] = category
            error_dict["error_type"] = category
    return error_dict


if __name__ == "__main__":
    # Тесты
    test_msgs = [
        "httpx.connecterror: connection refused",
        "telegram.error.networkerror: httpx.connecterror",
        "tavily search failed: client error '432'",
        "subprocess timeout after 60s",
        "permission denied: /root/file",
    ]
    
    for msg in test_msgs:
        cat = classify_unknown(msg)
        print(f"'{msg}' -> {cat}")
