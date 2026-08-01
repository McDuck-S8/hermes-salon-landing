import sys
from pathlib import Path
HERMES_HOME = Path('D:/Portable_Soft/hermes')
sys.path.insert(0, str(HERMES_HOME / 'scripts'))
sys.path.insert(0, str(HERMES_HOME / 'skills' / 'finance' / 'arbitrage-sensors' / 'scripts'))

from format_short_alert import format_alert

# The CRITICAL gap: admitad adm_002 (Raid Shadow Legends) + richads gaming RU
gap = {
    'offer': {'offer_id': 'adm_002', 'network': 'admitad', 'vertical': 'gaming', 'geo': 'RU'},
    'traffic': {'source': 'richads', 'vertical': 'gaming', 'geo': 'RU', 'cpc': 4.5},
    'roi': 240.0,
    'projected_profit_per_day': 1080,
    'confidence': 1.0,
    'score': 80
}

msg = format_alert(gap)
print('Message to send:')
print(msg)
print(f'Lines: {len(msg.split(chr(10)))}')