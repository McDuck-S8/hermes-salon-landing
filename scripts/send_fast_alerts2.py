#!/usr/bin/env python3
"""Send FAST sensor CRITICAL alerts to Telegram using short format."""

import sys
sys.path.insert(0, 'scripts')

from telegram_bridge import send_telegram_message

# Alert 1: Raid Shadow Legends + RichAds (using format_short_alert style)
msg1 = """🔴 CRITICAL: adm_002 (admitad) + richads gaming RU
ROI: 240p0% | $1080 perday
Conf: 1p00 | Score: 480
ACTION: Test richads RU gaming $50
⚠️ MOCK - Validate live"""

# Alert 2: Tinkoff + Kadam  
msg2 = """🔴 CRITICAL: adm_001 (admitad) + kadam finance RU
ROI: 244p1% | $2075 perday
Conf: 0p20 | Score: 98
ACTION: Test kadam RU finance $50
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