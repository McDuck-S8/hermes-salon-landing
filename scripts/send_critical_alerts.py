#!/usr/bin/env python3
"""Send CRITICAL alerts from fast sensor run."""

import sys
sys.path.insert(0, 'D:/Portable_Soft/hermes/scripts')
from telegram_bridge import send_telegram_message

def send_alert(title, metrics, action, disclaimer):
    send_telegram_message(title)
    send_telegram_message(metrics)
    send_telegram_message(action)
    send_telegram_message(disclaimer)

# CRITICAL Alert 1: Raid Shadow Legends + RichAds
send_alert(
    'CRITICAL: Raid Shadow Legends (admitad) + RichAds gaming RU',
    'ROI 240% | Profit 1080/day | Conf 100% | Score 480',
    'ACTION: Test RichAds gaming RU 50 USD',
    'MOCK DATA - Validate live before deploy'
)
print('Alert 1 sent')

# CRITICAL Alert 2: Tinkoff Credit Card + Kadam
send_alert(
    'CRITICAL: Tinkoff Credit Card (admitad) + Kadam finance RU',
    'ROI 244% | Profit 2075/day | Conf 20% | Score 98',
    'ACTION: Test Kadam finance RU 50 USD',
    'MOCK DATA - Validate live before deploy'
)
print('Alert 2 sent')

print('All CRITICAL alerts sent successfully')