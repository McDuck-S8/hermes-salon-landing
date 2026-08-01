import sys
sys.path.insert(0, 'D:/Portable_Soft/hermes/skills/finance/arbitrage-sensors/scripts')
from format_short_alert import format_alert
gap = {'offer': {'offer_id': 'adm_002', 'network': 'admitad', 'vertical': 'gaming', 'geo': 'RU'}, 'traffic': {'source': 'richads', 'vertical': 'gaming', 'geo': 'RU', 'cpc': 4.5}, 'roi': 240.0, 'projected_profit_per_day': 1080, 'confidence': 1.0, 'score': 480}
msg = format_alert(gap)
print('Message:')
print(repr(msg))
print('Lines:', len(msg.split('\n')))