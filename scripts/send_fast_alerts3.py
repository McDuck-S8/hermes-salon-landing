#!/usr/bin/env python3
"""Send fast sensor CRITICAL alerts to Telegram."""

import sys
sys.path.insert(0, 'scripts')

from telegram_bridge import send_telegram_message

# Alert 1: Raid Shadow Legends + RichAds (Score 480 - CRITICAL)
msg1 = """CRITICAL ALERT (score 480)
Offer: adm_002 Raid Shadow Legends (admitad) gaming RU
Traffic: richads gaming RU cpc 4.5
ROI: 240p0% | Profit: 1080 perday
Confidence: 1p00
ACTION: Test richads gaming RU 50
MOCK DATA - Validate live"""

# Alert 2: Tinkoff Credit Card + Kadam (Score 98 - CRITICAL)
msg2 = """CRITICAL ALERT (score 98)
Offer: adm_001 Tinkoff Credit Card (admitad) finance RU
Traffic: kadam finance RU cpc 8p5
ROI: 244p1% | Profit: 2075 perday
Confidence: 0p20
ACTION: Test kadam finance RU 50
MOCK DATA - Validate live"""

try:
    send_telegram_message(msg1)
    print('Alert 1 sent')
except Exception as e:
    print(f'Alert 1 failed: {e}')

try:
    send_telegram_message(msg2)
    print('Alert 2 sent')
except Exception as e:
    print(f'Alert 2 failed: {e}')