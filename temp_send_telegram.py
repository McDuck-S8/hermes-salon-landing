import urllib.request
import json
import os

token = os.environ.get('TELEGRAM_BOT_TOKEN')
chat_id = os.environ.get('CHAT_ID', '737433175')

# Test 1: Simple message
text = "Test message from fast sensor"
url = f'https://api.telegram.org/bot{token}/sendMessage'
data = json.dumps({'chat_id': chat_id, 'text': text}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req) as resp:
        print('Test 1:', resp.read().decode())
except Exception as e:
    print('Test 1 Error:', e)

# Test 2: Alert message (plain text, no markdown)
text2 = "CRITICAL adm_002 admitad + richads gaming RU\nROI: 240 pct | profit: 1080/day | Conf: 1.00 | Score: 480\nACTION: Test richads RU gaming with 50 budget"
data2 = json.dumps({'chat_id': chat_id, 'text': text2}).encode('utf-8')
req2 = urllib.request.Request(url, data=data2, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req2) as resp:
        print('Test 2:', resp.read().decode())
except Exception as e:
    print('Test 2 Error:', e)

# Test 3: Alert message with parse_mode=MarkdownV2
text3 = "CRITICAL adm_001 admitad + kadam finance RU\nROI: 244 pct | profit: 2075/day | Conf: 0.20 | Score: 98\nACTION: Test kadam RU finance with 50 budget"
data3 = json.dumps({'chat_id': chat_id, 'text': text3, 'parse_mode': 'Markdown'}).encode('utf-8')
req3 = urllib.request.Request(url, data=data3, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req3) as resp:
        print('Test 3:', resp.read().decode())
except Exception as e:
    print('Test 3 Error:', e)