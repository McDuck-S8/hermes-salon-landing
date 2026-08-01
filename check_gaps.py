import json

with open('D:/Portable_Soft/hermes/cache/arbitrage_gaps.json', 'r', encoding='utf-8') as f:
    gaps = json.load(f)

critical_gaps = [g for g in gaps if g.get('roi', 0) >= 70]
high_gaps = [g for g in gaps if 50 <= g.get('roi', 0) < 70]

print(f"Total gaps: {len(gaps)}")
print(f"CRITICAL (ROI >= 70): {len(critical_gaps)}")
print(f"HIGH (50 <= ROI < 70): {len(high_gaps)}")

if critical_gaps:
    print("\n=== CRITICAL GAPS (ROI >= 70) ===")
    for g in critical_gaps[:10]:
        print(f"  {g['gap_id']}: ROI={g['roi']}% Profit/day=${g['projected_profit_per_day']:.2f} Offer={g['offer']['name']} ({g['offer']['network']}:{g['offer']['offer_id']}) Traffic={g['traffic']['source']} CPC={g['traffic']['cpc']}")

if high_gaps:
    print("\n=== HIGH GAPS (50 <= ROI < 70) ===")
    for g in high_gaps[:10]:
        print(f"  {g['gap_id']}: ROI={g['roi']}% Profit/day=${g['projected_profit_per_day']:.2f} Offer={g['offer']['name']} ({g['offer']['network']}:{g['offer']['offer_id']}) Traffic={g['traffic']['source']} CPC={g['traffic']['cpc']}")