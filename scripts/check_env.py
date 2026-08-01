import os
print('TELEGRAM_BOT_TOKEN:', 'SET' if os.environ.get('TELEGRAM_BOT_TOKEN') else 'NOT SET')
print('CHAT_ID:', 'SET' if os.environ.get('CHAT_ID') else 'NOT SET')