import sys
sys.path.insert(0, 'D:/Portable_Soft/hermes/scripts')
from telegram_bridge import send_telegram_message

alerts = [
    {'alert_id': 'alert_admitad_adm_001_kadam_critical', 'offer': 'Кредитная карта Тинькофф (admitad)', 'traffic': 'Kadam RU finance', 'roi': 244.12, 'profit': 2075, 'conf': 0.20, 'score': 162, 'action': 'Test Kadam RU finance $100 budget'},
    {'alert_id': 'alert_admitad_adm_001_facebook_critical', 'offer': 'Кредитная карта Тинькофф (admitad)', 'traffic': 'Facebook RU finance', 'roi': 62.5, 'profit': 1125, 'conf': 0.20, 'score': 112, 'action': 'Test FB Ads RU finance $56 budget'},
    {'alert_id': 'alert_admitad_adm_001_google_critical', 'offer': 'Кредитная карта Тинькофф (admitad)', 'traffic': 'Google RU finance', 'roi': 32.95, 'profit': 725, 'conf': 0.20, 'score': 84, 'action': 'Test Google Ads RU finance $36 budget'},
    {'alert_id': 'alert_admitad_adm_002_richads_critical', 'offer': 'Raid Shadow Legends (admitad)', 'traffic': 'RichAds RU gaming', 'roi': 240.0, 'profit': 1080, 'conf': 1.00, 'score': 720, 'action': 'Launch RichAds gaming RU $100 test'},
    {'alert_id': 'alert_cityads_cit_002_kadam_critical', 'offer': 'Страховка авто РасСтрехование (cityads)', 'traffic': 'Kadam RU finance', 'roi': 82.0, 'profit': 697, 'conf': 0.24, 'score': 98, 'action': 'Test Kadam RU finance $34 budget'},
]

for a in alerts:
    msg = f"""🔴 CRITICAL ARBITRAGE SIGNAL
Alert: {a['alert_id']}
Offer: {a['offer']}
Traffic: {a['traffic']}
ROI: {a['roi']:.1f}%
Projected: ${a['profit']:.0f}/day
Confidence: {a['conf']:.0%}
Score: {a['score']}
Action: {a['action']}
⚠️ MOCK DATA - Validate live before deploy
"""
    try:
        send_telegram_message(msg)
        print(f'Sent: {a["alert_id"]}')
    except Exception as e:
        print(f'Failed {a["alert_id"]}: {e}')