#!/usr/bin/env python3
"""Debug telegram send step by step."""

import sys
sys.path.insert(0, 'scripts')

from telegram_bridge import send_telegram_message

# Test progressively more complex messages
tests = [
    "Test",
    "Test 123",
    "CRITICAL ALERT (score 480)",
    "Offer: adm_002 Raid Shadow Legends",
    "Traffic: richads gaming RU cpc 4.5",
    "ROI: 240% | Profit: 1080/day",
    "Confidence: 100%",
    "ACTION: Test richads gaming RU 50",
    "MOCK - Validate live",
    # Full message
    "CRITICAL ALERT (score 480)\nOffer: adm_002 Raid Shadow Legends\nTraffic: richads gaming RU cpc 4.5\nROI: 240% | Profit: 1080/day\nConfidence: 100%\nACTION: Test richads gaming RU 50\nMOCK - Validate live",
]

for i, msg in enumerate(tests):
    try:
        send_telegram_message(msg)
        print(f'Test {i+1}: OK ({len(msg)} chars, {msg.count(chr(10))+1} lines)')
    except Exception as e:
        print(f'Test {i+1}: FAILED - {e}')
        break