#!/usr/bin/env python3
"""Send CRITICAL alerts from fast sensor run to Telegram"""

import sys
import os
sys.path.insert(0, 'D:/Portable_Soft/hermes/scripts')
sys.path.insert(0, 'D:/Portable_Soft/hermes/skills/finance/arbitrage-sensors/scripts')

from format_short_alert import format_alert
from telegram_bridge import send_telegram_message

# Critical alert 1: adm_002 (Raid Shadow Legends) + richads gaming RU
gap1 = {
    'offer': {
        'offer_id': 'adm_002',
        'network': 'admitad',
        'vertical': 'gaming',
        'geo': 'RU'
    },
    'traffic': {
        'source': 'richads',
        'vertical': 'gaming',
        'geo': 'RU'
    },
    'roi': 240.0,
    'projected_profit_per_day': 1080,
    'confidence': 1.0,
    'score': 480
}

# Critical alert 2: adm_001 (Tinkoff Credit Card) + kadam finance RU
gap2 = {
    'offer': {
        'offer_id': 'adm_001',
        'network': 'admitad',
        'vertical': 'finance',
        'geo': 'RU'
    },
    'traffic': {
        'source': 'kadam',
        'vertical': 'finance',
        'geo': 'RU'
    },
    'roi': 244.1,
    'projected_profit_per_day': 2075,
    'confidence': 0.20,
    'score': 98
}

def main():
    # Format alerts
    msg1 = format_alert(gap1)
    msg2 = format_alert(gap2)
    
    print("Sending Alert 1:")
    print(msg1)
    print()
    print("Sending Alert 2:")
    print(msg2)
    print()
    
    # Send to Telegram
    try:
        send_telegram_message(text=msg1, parse_mode=None)
        print("✅ Alert 1 sent successfully")
    except Exception as e:
        print(f"❌ Alert 1 failed: {e}")
    
    try:
        send_telegram_message(text=msg2, parse_mode=None)
        print("✅ Alert 2 sent successfully")
    except Exception as e:
        print(f"❌ Alert 2 failed: {e}")

if __name__ == "__main__":
    main()