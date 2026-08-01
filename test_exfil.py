from skills.devops.exfiltration_guard.scripts.exfil_guard import check_telegram_message

msg = """CRITICAL adm_002 admitad + richads gaming RU
ROI: 240p0pct | profit: 1080 perday | Conf: 1p00 | Score: 480
ACTION: Test richads RU gaming with 50 budget"""

result = check_telegram_message(msg)
print(result)

msg2 = "CRITICAL adm_001 admitad + kadam finance RU\nROI: 244p1pct | profit: 2075 perday | Conf: 0p20 | Score: 98\nACTION: Test kadam RU finance with 50 budget"
result2 = check_telegram_message(msg2)
print(result2)

# Test shorter
msg3 = "test"
result3 = check_telegram_message(msg3)
print(result3)