#!/usr/bin/env python3
"""Send FAST sensor CRITICAL alerts to Telegram."""

import sys
sys.path.insert(0, 'scripts')

from telegram_bridge import send_telegram_message

# Alert 1: Raid Shadow Legends + RichAds
msg1 = """🔴 CRITICAL: adm_002 (admitad) + richads gaming RU
ROI: 240.0% | $1080/day
Conf: 1.00 | Score: 480
ACTION: Test RichAds gaming RU $50
⚠️ MOCK - Validate live"""

# Alert 2: Tinkoff + Kadam  
msg2 = """🔴 CRITICAL: adm_001 (admitad) + kadam finance RU
ROI: 244.1% | $2075/day
Conf: 0.20 | Score: 98
ACTION: Test Kadam finance RU $50
⚠️ MOCK - Validate live"""

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