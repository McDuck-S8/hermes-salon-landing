import sys
sys.path.insert(0, 'scripts')
from telegram_bridge import send_telegram_message

# Test message - plain text, < 8 lines, no $ or markdown
message = """🔴 CRITICAL (Score 80)
Raid Shadow Legends (admitad adm_002)
RichAds RU gaming CPI
ROI: 240pct | Profit: 1080 perday
Conf: 100pct
Action: Test RichAds RU gaming 100 USD"""

try:
    send_telegram_message(text=message)
    print("Telegram message sent successfully!")
except Exception as e:
    print(f"Error: {e}")