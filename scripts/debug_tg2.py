#!/usr/bin/env python3
"""Debug telegram send - test colon."""

import sys
sys.path.insert(0, 'scripts')

from telegram_bridge import send_telegram_message

tests = [
    "Offer adm_002 Raid Shadow Legends",
    "Offer: adm_002 Raid Shadow Legends",
    "Traffic richads gaming RU cpc 4.5",
    "Traffic: richads gaming RU cpc 4.5",
    "ROI 240% Profit 1080/day",
    "ROI: 240% | Profit: 1080/day",
]

for i, msg in enumerate(tests):
    try:
        send_telegram_message(msg)
        print(f'Test {i+1}: OK')
    except Exception as e:
        print(f'Test {i+1}: FAILED - {e}')