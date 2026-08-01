#!/usr/bin/env python3
"""
Score arbitrage gaps using always-on-agent formula:
Score = Impact * Urgency * Confidence (each 0-10)
Thresholds: >=70 CRITICAL, >=50 HIGH, >=30 MEDIUM, <30 LOG
"""
import json
import sys

# Load latest gaps
with open("cache/arbitrage_gaps.json", "r", encoding="utf-8") as f:
    gaps = json.load(f)

# Get the 6 latest gaps (from the most recent run with timestamp 1784767044)
latest_gaps = [g for g in gaps if g["gap_id"].endswith("_1784767044")]

def score_signal(gap):
    """Calculate signal score per always-on-agent spec"""
    roi = gap["roi"]
    profit = gap["projected_profit_per_day"]
    conf = gap["confidence"]  # 0-1
    
    # Impact: based on projected daily profit
    if profit >= 2000: impact = 9
    elif profit >= 1000: impact = 8
    elif profit >= 500: impact = 7
    elif profit >= 200: impact = 6
    elif profit >= 100: impact = 5
    else: impact = 4
    
    # Urgency: based on ROI (higher ROI = act faster before cap fills)
    if roi >= 200: urgency = 9
    elif roi >= 100: urgency = 8
    elif roi >= 50: urgency = 7
    elif roi >= 30: urgency = 6
    elif roi >= 20: urgency = 5
    else: urgency = 4
    
    # Confidence: 0-10 scale
    confidence = max(1, int(conf * 10))
    
    score = impact * urgency * confidence
    
    if score >= 70: level = "CRITICAL"
    elif score >= 50: level = "HIGH"
    elif score >= 30: level = "MEDIUM"
    else: level = "LOG"
    
    return {
        "gap_id": gap["gap_id"],
        "offer": gap["offer"]["name"],
        "traffic": f"{gap['traffic']['source']} {gap['traffic']['geo']} {gap['traffic']['vertical']}",
        "roi": roi,
        "projected_profit_per_day": profit,
        "confidence": conf,
        "impact": impact,
        "urgency": urgency,
        "confidence_10": confidence,
        "score": score,
        "level": level,
        "action": f"Test {gap['traffic']['source']} {gap['traffic']['geo']} {gap['traffic']['vertical']} ${min(100, int(profit*0.05))} budget"
    }

# Score all latest gaps
signals = [score_signal(g) for g in latest_gaps]

# Filter CRITICAL
critical = [s for s in signals if s["level"] == "CRITICAL"]
high = [s for s in signals if s["level"] == "HIGH"]

print("=== FAST SENSOR RUN - SIGNAL SCORING ===")
print(f"Total gaps analyzed: {len(latest_gaps)}")
print(f"CRITICAL (score>=70): {len(critical)}")
print(f"HIGH (score 50-69): {len(high)}")
print()

for s in signals:
    print(f"[{s['level']:8}] Score: {s['score']:3d} | {s['offer']} + {s['traffic']} | ROI: {s['roi']:.1f}% | Profit: ${s['projected_profit_per_day']:.0f}/day | Conf: {s['confidence']:.2f}")
    print(f"         Action: {s['action']}")

# Save to state
import datetime
state = {
    "last_run": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "sensor": "fast",
    "offers_scanned": 6,
    "gaps_found": len(latest_gaps),
    "signals_scored": {
        "CRITICAL": len(critical),
        "HIGH": len(high),
        "MEDIUM": len([s for s in signals if s["level"] == "MEDIUM"]),
        "LOG": len([s for s in signals if s["level"] == "LOG"])
    },
    "critical_signals": critical,
    "high_signals": high,
    "notes": "FAST sensors: traffic_cost_monitor (mock data - Kadam, RichAds, Facebook, Google, TikTok embedded) + network_health (mock data). All alerts from mock sources — treat as HYPOTHESES requiring live validation. Finance Core: $0 revenue, $0.01 infra spend, 0 active schemes.",
    "alerts_emitted": [f"alert_{s['gap_id'].replace('gap_', '').replace('_', '_').replace('_1784767044', '_critical')}" for s in critical]
}

with open("cache/always_on_state.json", "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

print("\n=== STATE UPDATED ===")
print(f"CRITICAL alerts to emit: {len(critical)}")

# Print Telegram-ready alerts for CRITICAL
if critical:
    print("\n=== TELEGRAM ALERTS (CRITICAL only) ===")
    for s in critical:
        alert = {
            "alert_id": f"alert_{s['gap_id'].replace('gap_', '').replace('_', '_').replace('_1784767044', '_critical')}",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "sensor": "fast_traffic_cost_gap",
            "signal": "ARBITRAGE_GAP",
            "score": s["score"],
            "payload": {
                "network": s["offer"].split("(")[0].strip() if "(" in s["offer"] else "admitad",
                "offer_name": s["offer"],
                "traffic_source": s["traffic"],
                "roi": s["roi"],
                "projected_profit_per_day": s["projected_profit_per_day"],
                "confidence": s["confidence"]
            },
            "action": s["action"],
            "expires": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=12)).isoformat()
        }
        print(json.dumps(alert, ensure_ascii=False))