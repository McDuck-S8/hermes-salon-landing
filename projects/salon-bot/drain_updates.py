"""Drain all pending Telegram updates."""
import os
import json
import urllib.request

with open(os.path.join(os.path.dirname(__file__), '..', '..', '.env')) as f:
    for line in f:
        line = line.strip()
        if line and '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

TOKEN=os.environ.get('TELEGRAM_BOT_TOKEN', '')
PROXY = 'socks5://127.0.0.1:10806'

ph = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
opener = urllib.request.build_opener(ph)

offset = 0
total = 0
while True:
    url = f'https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=2'
    r = opener.open(urllib.request.Request(url), timeout=10)
    d = json.loads(r.read())
    results = d.get('result', [])
    if not results:
        break
    offset = results[-1]['update_id'] + 1
    total += len(results)
    for u in results:
        msg = u.get('message', {})
        cb = u.get('callback_query', {})
        if msg:
            print(f'  msg: {msg.get("text","?")} from {msg["from"].get("username","?")}')
        if cb:
            print(f'  callback: {cb.get("data","?")} from {cb["from"].get("username","?")}')

print(f'Drained {total} updates. Queue empty.')
