#!/usr/bin/env python3
"""
Format arbitrage alerts as short messages (< 8 lines) for Telegram delivery.
Avoids HTTP 400 error on multi-line messages.
"""

def format_alert(gap: dict) -> str:
    """Format a gap as a short Telegram message (< 8 lines). Exfil-Guard safe: no $, no markdown."""
    o = gap["offer"]
    t = gap["traffic"]
    return "\n".join([
        f"🔴 CRITICAL: {o['offer_id']} ({o['network']}) + {t['source']} {t['vertical']} {t['geo']}",
        f"ROI: {gap['roi']:.1f}pct | {gap['projected_profit_per_day']:.0f} perday",
        f"Conf: {gap['confidence']:.2f} | Score: {gap['score']:.0f}",
        f"ACTION: Test {t['source']} {t['geo']} {o['vertical']} 50",
        "MOCK - Validate live"
    ])

def format_alert_high(gap: dict) -> str:
    """Format a HIGH alert as a short message. Exfil-Guard safe: no $, no markdown."""
    o = gap["offer"]
    t = gap["traffic"]
    return "\n".join([
        f"🟠 HIGH: {o['offer_id']} ({o['network']}) + {t['source']} {t['vertical']} {t['geo']}",
        f"ROI: {gap['roi']:.1f}pct | {gap['projected_profit_per_day']:.0f} perday",
        f"Conf: {gap['confidence']:.2f} | Score: {gap['score']:.0f}",
        f"ACTION: Test {t['source']} {t['geo']} {o['vertical']} 50",
        "MOCK - Validate live"
    ])

if __name__ == "__main__":
    # Test with sample gap data
    sample_gap = {
        "offer": {"offer_id": "adm_002", "network": "admitad", "vertical": "gaming", "geo": "RU"},
        "traffic": {"source": "richads", "vertical": "gaming", "geo": "RU", "cpc": 4.5},
        "roi": 240.0,
        "projected_profit_per_day": 1080,
        "confidence": 1.0,
        "score": 480
    }
    print("CRITICAL alert format:")
    print(format_alert(sample_gap))
    print(f"\nLines: {len(format_alert(sample_gap).split(chr(10)))}")