"""Clear all pending Telegram updates to avoid 409 Conflict."""
import os
import json
import time
import urllib.request

# Load .env
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
PROXY = 'socks5://127.0.0.1:10806'

ph = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
opener = urllib.request.build_opener(ph)

# Drop webhook
url = f'https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true'
r = opener.open(urllib.request.Request(url), timeout=10)
print('webhook:', json.loads(r.read()))

time.sleep(2)

# Drain all pending updates
offset = 0
total = 0
while True:
    url = f'https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=1'
    r = opener.open(urllib.request.Request(url), timeout=10)
    d = json.loads(r.read())
    results = d.get('result', [])
    if not results:
        break
    offset = results[-1]['update_id'] + 1
    total += len(results)
    print(f'Drained {len(results)} updates (offset={offset})')

print(f'Queue cleared. Total drained: {total}')
