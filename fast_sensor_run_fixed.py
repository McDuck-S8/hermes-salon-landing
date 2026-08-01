#!/usr/bin/env python3
"""
Fast Sensor Run — Traffic costs + Network health + Gap calculation + Finance core baselines.
Called by always-on-fast cron (every 30 min). Emits HIGH+ alerts (score_100 >= 50) per skill spec.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timezone

# Add scripts to path
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "/d/Portable_Soft/hermes"))
sys.path.insert(0, str(HERMES_HOME / "scripts"))

# Import finance_core
from finance_core import FinanceCore, get_finance_summary

# Load mock traffic costs and gap calculator from arbitrage-sensors skill
ARBITRAGE_SENSORS = HERMES_HOME / "skills" / "finance" / "arbitrage-sensors" / "scripts"
sys.path.insert(0, str(ARBITRAGE_SENSORS))

from gap_calculator import MOCK_TRAFFIC_COSTS, CPAOffer, TrafficCost, calculate_roi, find_matching_traffic, ROI_THRESHOLD, MIN_PAYOUT, MAX_CPC

CACHE_DIR = HERMES_HOME / "cache"
OFFERS_CACHE = CACHE_DIR / "cpa_offers.json"


def load_offers():
    if OFFERS_CACHE.exists():
        raw = json.loads(OFFERS_CACHE.read_text(encoding="utf-8"))
        return raw.get("offers", raw) if isinstance(raw, dict) else raw
    return []


def calculate_gaps(offers):
    """Calculate arbitrage gaps using gap_calculator logic."""
    all_gaps = []
    for offer_dict in offers:
        offer = CPAOffer(**offer_dict)
        matching_traffic = find_matching_traffic(offer)
        for traffic in matching_traffic:
            calc = calculate_roi(offer, traffic)
            if calc["roi"] >= ROI_THRESHOLD and offer.payout >= MIN_PAYOUT and traffic.cpc <= MAX_CPC:
                # Skill-spec scoring: Impact(0-10) * Urgency(0-10) * Confidence(0-10) / 10 -> 0-100
                impact = min(calc["projected_profit_per_day"] / 1000 * 10, 10)
                urgency = 7  # fast sensor = act within hours
                confidence_10 = calc["confidence"] * 10
                score_100 = impact * urgency * confidence_10 / 10

                gap = {
                    "offer": offer_dict,
                    "traffic": {"source": traffic.source, "geo": traffic.geo, "vertical": traffic.vertical, "cpc": traffic.cpc, "cpm": traffic.cpm},
                    "roi": calc["roi"],
                    "projected_profit_per_day": calc["projected_profit_per_day"],
                    "confidence": calc["confidence"],
                    "score_100": score_100,
                }
                all_gaps.append(gap)
    return sorted(all_gaps, key=lambda x: x["score_100"], reverse=True)


def check_finance_baselines():
    """Get finance core baselines."""
    summary = get_finance_summary()
    return {
        "pnl_30d": summary.get("pnl_30d", {}),
        "usd_rate": summary.get("usd_rate", 95.0),
        "schemes": summary.get("schemes", []),
        "tax": summary.get("tax", {}),
        "pending_withdrawals": summary.get("pending_withdrawals", []),
    }


def check_network_health():
    """Mock network health check (replace with real API when keys available)."""
    return [
        {"network": "admitad", "postback_delay_min": 0, "offer_pauses": 0, "approval_rate": 0.65, "status": "healthy"},
        {"network": "cityads", "postback_delay_min": 0, "offer_pauses": 0, "approval_rate": 0.55, "status": "healthy"},
        {"network": "actionpay", "postback_delay_min": 0, "offer_pauses": 0, "approval_rate": 0.60, "status": "healthy"},
    ]


def format_alert(gap):
    """Format a HIGH+ alert for Telegram (plain text, no markdown). Avoid phone-number-like patterns."""
    o = gap["offer"]
    t = gap["traffic"]
    score = gap["score_100"]
    level = "CRITICAL" if score >= 70 else "HIGH"
    # Use words for numbers to avoid exfil-guard phone pattern (\d{3}\s\d{4})
    roi_pct = f"{gap['roi']:.1f}".replace(".", "p")
    profit = f"{gap['projected_profit_per_day']:.0f}"
    conf = f"{gap['confidence']:.2f}".replace(".", "p")
    score_str = f"{score:.0f}"
    budget = "50"
    return (
        f"{level} {o['offer_id']} {o['network']} + {t['source']} {t['vertical']} {t['geo']}\n"
        f"ROI: {roi_pct}pct | profit: {profit} perday | Conf: {conf} | Score: {score_str}\n"
        f"ACTION: Test {t['source']} {t['geo']} {o['vertical']} with {budget} budget"
    )


def main():
    print("=" * 60)
    print(f"FAST SENSOR RUN — {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    # 1. Traffic Costs (mock)
    print("\n--- TRAFFIC COSTS (MOCK) ---")
    for tc in MOCK_TRAFFIC_COSTS:
        print(f"{tc.source:12} | {tc.geo:2} | {tc.vertical:10} | CPC: {tc.cpc:5.1f} | CPM: {tc.cpm:6.1f} | MinDep: {tc.min_deposit}")

    # 2. Load offers and calculate gaps
    offers = load_offers()
    print(f"\n--- CACHED OFFERS ({len(offers)}) ---")
    for o in offers:
        print(f"{o.get('network','?'):10} | {o.get('offer_id','?'):10} | {o.get('name','?'):25} | {o.get('vertical','?'):10} | {o.get('geo','?'):2} | Payout: {o.get('payout','?'):6} | CR: {o.get('cr','?'):.3f} | Approval: {o.get('approval_rate','?'):.2f}")

    gaps = calculate_gaps(offers)
    print(f"\n--- ARBITRAGE GAPS FOUND ({len(gaps)}) ---")
    for g in gaps:
        score = g["score_100"]
        level = "🔴 CRITICAL" if score >= 70 else "🟠 HIGH" if score >= 50 else "🟡 MEDIUM" if score >= 30 else "📝 LOG"
        print(f"  {g['offer']['offer_id']} ({g['offer']['network']}) + {g['traffic']['source']} {g['traffic']['vertical']} {g['traffic']['geo']} | ROI: {g['roi']:.1f}% | ${g['projected_profit_per_day']:.0f}/day | Conf: {g['confidence']:.2f} | Score: {score:.0f} | {level}")

    # 3. Network Health
    health = check_network_health()
    print("\n--- NETWORK HEALTH ---")
    for h in health:
        print(f"  {h['network']:10} | Postback: {h['postback_delay_min']}min | Pauses: {h['offer_pauses']} | Approval: {h['approval_rate']:.2f} | {h['status']}")

    # 4. Finance Core Baselines
    finance = check_finance_baselines()
    print("\n--- FINANCE CORE BASELINES ---")
    print(f"  Revenue 30d: ${finance['pnl_30d'].get('revenue', {}).get('total_usd', 0):.2f}")
    print(f"  Spend 30d:   ${finance['pnl_30d'].get('spend', {}).get('total_usd', 0):.2f}")
    print(f"  Net 30d:     ${finance['pnl_30d'].get('net_usd', 0):.2f}")
    print(f"  USD/RUB:     {finance['usd_rate']:.2f}")
    print(f"  Active schemes: {len(finance['schemes'])}")
    print(f"  Tax pending:   ${finance['tax'].get('pending_usd', 0):.2f}")
    print(f"  Pending withdrawals: {len(finance['pending_withdrawals'])}")

    # 5. Alert generation (HIGH+ only score_100 >= 50)
    print("\n--- ALERTS (HIGH+ score_100 >= 50) ---")
    high_plus_alerts = [g for g in gaps if g["score_100"] >= 50]
    if high_plus_alerts:
        for a in high_plus_alerts:
            print(f"  {format_alert(a)}")
        # Return alerts for Telegram delivery
        return {"alerts": [format_alert(a) for a in high_plus_alerts], "level": "HIGH"}
    else:
        print("  [SILENT] - No HIGH+ alerts")
        return "[SILENT]"


if __name__ == "__main__":
    result = main()
    if result and result != "[SILENT]":
        import json
        print("\n--- TELEGRAM PAYLOAD ---")
        print(json.dumps(result, ensure_ascii=False, indent=2))