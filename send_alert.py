import sys
sys.path.insert(0, 'D:/Portable_Soft/hermes/skills/autonomous-ai-agents/always-on-agent/scripts')
from send_short_alert import send_short_alert

alert = "CRITICAL adm_002 admitad + richads gaming RU\nROI: 240p0pct | profit: 1080 perday | Conf: 1p00 | Score: 70\nACTION: Test richads RU gaming with 50 budget"

send_short_alert(alert)
print("Alert sent!")