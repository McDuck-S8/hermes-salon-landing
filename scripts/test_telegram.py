import sys
sys.path.insert(0, 'D:/Portable_Soft/hermes/scripts')
from telegram_bridge import send_telegram_message

# Test simple message
msg = "Test: Always-on-agent fast sensor CRITICAL alert"
try:
    send_telegram_message(msg)
    print("Test sent OK")
except Exception as e:
    print(f"Test failed: {e}")