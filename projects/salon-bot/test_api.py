"""Quick test: can we reach Telegram API through proxy?"""
import os
import json
import urllib.request

# Load .env
with open(os.path.join(os.path.dirname(__file__), '..', '..', '.env')) as f:
    for line in f:
        line = line.strip()
        if line and '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
PROXY = 'socks5://127.0.0.1:10806'

ph = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
opener = urllib.request.build_opener(ph)

# Test getMe
url = f'https://api.telegram.org/bot{TOKEN}/getMe'
print(f'Testing getMe...', flush=True)
r = opener.open(urllib.request.Request(url), timeout=10)
data = json.loads(r.read())
print(f'Bot: @{data["result"]["username"]} - OK', flush=True)

# Drop webhook
url2 = f'https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true'
print(f'Clearing webhook...', flush=True)
r2 = opener.open(urllib.request.Request(url2), timeout=10)
print(f'deleteWebhook: {json.loads(r2.read())}', flush=True)

print('READY TO LAUNCH BOT', flush=True)
