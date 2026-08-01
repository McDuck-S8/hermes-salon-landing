#!/usr/bin/env python3
"""Test telegram with numbers that might trigger Exfiltration Guard."""

import sys
sys.path.insert(0, 'scripts')

from telegram_bridge import send_telegram_message

# Test with numbers that match phone pattern \d{3}\s\d{4}
send_telegram_message('Test 1080')
print('Test 1 sent')

send_telegram_message('Test 1080 2075')
print('Test 2 sent')