import json
from datetime import datetime

# Load gaps cache
with open('D:/Portable_Soft/hermes/cache/arbitrage_gaps.json') as f:
    all_gaps = json.load(f)

# Load state to get new gap IDs
with open('D:/Portable_Soft/hermes/cache/gap_calculator_state.json') as f:
    state = json.load(f)

# The 6 new gap IDs from this run (timestamp 1784759733 = 2026-07-22T22:35:33)
new_gap_ids = [
    "gap_admitad_adm_001_kadam_1784759733",
    "gap_admitad_adm_001_google_1784759733",
    "gap_cityads_cit_001_kadam_1784759733",
    "gap_cityads_cit_002_kadam_1784759733",
    "gap_admitad_adm_002_richads_1784759733",
    "gap_admitad_adm_001_facebook_1784759733",
]

# Find the new gaps
new_gaps = [g for g in all_gaps if g['gap_id'] in new_gap_ids]

# Deduplicate by offer_id + source (keep latest)
unique = {}
for g in new_gaps:
    key = (g['offer']['offer_id'], g['traffic']['source'])
    if key not in unique or g['created_at'] > unique[key]['created_at']:
        unique[key] = g

print("=== NEW GAPS FROM THIS RUN ===\n")
for g in unique.values():
    offer = g['offer']
    traffic = g['traffic']
    roi = g['roi']
    profit = g['projected_profit_per_day']
    conf = g['confidence']
    
    # Calculate signal score per always-on-agent formula
    # Impact (0-10): scale profit_per_day, cap at $2000 = 10
    impact = min(profit / 2000 * 10, 10)
    
    # Urgency (0-10): new gaps = high urgency (8)
    urgency = 8
    
    # Confidence (0-10): from gap's confidence (0-1 scaled to 0-10)
    confidence = conf * 10
    
    score = impact * urgency * confidence
    
    level = "CRITICAL" if score >= 70 else ("HIGH" if score >= 50 else ("MEDIUM" if score >= 30 else "LOG"))
    
    print(f"GAP: {offer['network']}:{offer['offer_id']} + {traffic['source']}")
    print(f"  Offer: {offer['name']} ({offer['vertical']}/{offer['geo']}) - {offer['payout']} RUB")
    print(f"  Traffic: {traffic['source']} CPC={traffic['cpc']}")
    print(f"  ROI: {roi}% | Profit/day: ${profit} | Confidence: {conf}")
    print(f"  Impact: {impact:.1f} | Urgency: {urgency} | Confidence: {confidence:.1f}")
    print(f"  SCORE: {score:.0f} -> {level}")
    print()