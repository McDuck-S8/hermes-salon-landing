#!/usr/bin/env python3
"""
Always-On Agent FAST Sensors — 30 min cycle
Traffic costs, CPA network health, arbitrage gaps.
Runs every 30 minutes via cron.
"""

import sys
import os
import json
import asyncio
from datetime import datetime, timezone
from pathlib import Path

HERMES_HOME = Path("D:/Portable_Soft/hermes")
sys.path.insert(0, str(HERMES_HOME / "scripts"))
sys.path.insert(0, str(HERMES_HOME / "skills" / "finance" / "arbitrage-sensors" / "scripts"))

from finance_core import get_finance_summary
from cpa_scanner import run_scan
from gap_calculator import run_calculation
from format_short_alert import format_alert, format_alert_high
from telegram_bridge import send_telegram_message


def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [FAST_SENSORS] {msg}")


def calculate_score(gap: dict) -> float:
    """Calculate 0-100 score: Impact(0-10) * Urgency(0-10) * Confidence(0-10) / 10"""
    roi = gap.get("roi", 0)
    profit = gap.get("projected_profit_per_day", 0)
    confidence = gap.get("confidence", 0)
    
    # Impact (0-10): based on projected daily profit
    if profit >= 2000: impact = 10
    elif profit >= 1000: impact = 8
    elif profit >= 500: impact = 6
    elif profit >= 200: impact = 4
    elif profit >= 100: impact = 3
    else: impact = 2
    
    # Urgency (0-10): based on ROI + conversion type bonus
    if roi >= 200: urgency = 9
    elif roi >= 100: urgency = 7
    elif roi >= 50: urgency = 5
    elif roi >= 30: urgency = 3
    else: urgency = 1
    
    # CPI/CPL gets +1 urgency
    if gap.get("offer", {}).get("conversion_type") in ("CPI", "CPL"):
        urgency = min(urgency + 1, 10)
    
    # Confidence (0-10): gap confidence * 10
    conf = min(confidence * 10, 10)
    
    score = (impact * urgency * conf) / 10
    return round(score, 1)


def main():
    log("FAST sensors starting...")
    
    # 1. Finance summary
    finance = get_finance_summary()
    log(f"Finance: net={finance.get('pnl_30d', {}).get('net_usd', 0):.2f} USD")
    
    # 2. Run CPA offer scan
    scan_result = run_scan()
    log(f"CPA scan: {scan_result.get('scanned', 0)} scanned, {scan_result.get('new', 0)} new")
    
    # 3. Run gap calculation
    gap_result = run_calculation()
    log(f"Gap calc: {gap_result.get('offers_processed', 0)} offers, {gap_result.get('new_gaps', 0)} new gaps")
    
    # 4. Load new gaps and check for CRITICAL alerts
    gaps_cache = HERMES_HOME / "cache" / "arbitrage_gaps.json"
    if not gaps_cache.exists():
        log("No gaps cache found")
        return
    
    all_gaps = json.loads(gaps_cache.read_text(encoding="utf-8"))
    
    # Get known gap IDs from state
    state_file = HERMES_HOME / "cache" / "gap_calculator_state.json"
    known_gap_ids = set()
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))
        known_gap_ids = set(state.get("known_gap_ids", []))
    
    # Find new gaps with score >= 70 (CRITICAL)
    alerts_sent = 0
    for gap in all_gaps:
        gap_id = gap.get("gap_id", "")
        if gap_id not in known_gap_ids:
            score = calculate_score(gap)
            gap["score"] = score
            
            if score >= 70:  # CRITICAL threshold
                # Format and send alert
                if score >= 70:
                    msg = format_alert(gap)
                else:
                    msg = format_alert_high(gap)
                
                try:
                    send_telegram_message(text=msg)
                    log(f"ALERT SENT: {gap.get('offer', {}).get('offer_id', '?')} + {gap.get('traffic', {}).get('source', '?')} - Score: {score}")
                    alerts_sent += 1
                except Exception as e:
                    log(f"Telegram send failed: {e}")
    
    log(f"FAST sensors complete. Alerts sent: {alerts_sent}")
    return {"alerts_sent": alerts_sent, "gaps_found": gap_result.get('new_gaps', 0)}


if __name__ == "__main__":
    result = asyncio.run(main())
    print(json.dumps(result))
    sys.exit(0)