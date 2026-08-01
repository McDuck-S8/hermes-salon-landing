#!/usr/bin/env python3
"""
Send short arbitrage alerts via Telegram bridge.
Uses format_short_alert.py for Exfil-Guard safe formatting (< 8 lines, no $, no markdown).
"""

import sys
import os
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
sys.path.insert(0, str(HERMES_HOME / "scripts"))
sys.path.insert(0, str(HERMES_HOME / "skills" / "finance" / "arbitrage-sensors" / "scripts"))

from format_short_alert import format_alert, format_alert_high


def send_telegram_alert(message: str) -> bool:
    """Send short alert via telegram_bridge."""
    try:
        from telegram_bridge import send_telegram_message
        send_telegram_message(text=message, parse_mode=None)  # plain text, no markdown
        return True
    except Exception as e:
        print(f"[SEND_SHORT_ALERT] Telegram send failed: {e}")
        return False


def send_alert(gap: dict) -> bool:
    """Format and send alert based on gap score."""
    if gap.get("score", 0) >= 70:
        msg = format_alert(gap)
    else:
        msg = format_alert_high(gap)
    return send_telegram_alert(msg)


if __name__ == "__main__":
    # Test with sample gap data
    sample_gap = {
        "offer": {"offer_id": "adm_002", "network": "admitad", "vertical": "gaming", "geo": "RU"},
        "traffic": {"source": "richads", "vertical": "gaming", "geo": "RU", "cpc": 4.5},
        "roi": 240.0,
        "projected_profit_per_day": 1080,
        "confidence": 1.0,
        "score": 80
    }
    print("Test CRITICAL alert:")
    print(format_alert(sample_gap))
    print(f"\nLines: {len(format_alert(sample_gap).split(chr(10)))}")