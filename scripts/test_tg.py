#!/usr/bin/env python3
"""Test minimal telegram send."""

import sys
sys.path.insert(0, 'scripts')

from telegram_bridge import send_telegram_message

send_telegram_message('Test: CRITICAL arbitrage gap found')
print('Sent test message')