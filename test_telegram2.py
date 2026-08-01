import sys
sys.path.insert(0, 'D:/Portable_Soft/hermes/scripts')
from telegram_bridge import send_telegram_message

# Test message from format_short_alert (new format without $, no markdown)
msg = "🔴 CRITICAL: adm_002 (admitad) + richads gaming RU\nROI: 240.0pct | 1080 perday\nConf: 1.00 | Score: 480\nACTION: Test richads RU gaming 50\nMOCK - Validate live"

try:
    # Use plain text (no parse_mode)
    send_telegram_message(msg, parse_mode=None)
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")