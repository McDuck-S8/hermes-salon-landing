import sqlite3, json, hashlib
from datetime import datetime
import urllib.request

url = 'http://localhost:9655/v1/chat/completions'

def research(prompt):
    payload = json.dumps({'model': 'deepseek-chat', 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': 3000}).encode()
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=180) as resp:
        body = json.loads(resp.read().decode())
    return body['choices'][0]['message']['content'], body.get('usage', {}).get('total_tokens', 0)

db = sqlite3.connect('cache/knowledge_cube.db')
c = db.cursor()

# CPA-NETWORKS: 5 записей (continuing from 1/5 done)
# 2/5: KYC и регистрация
print('=== CPA-NETWORKS: запись 2/5 ===')
prompt = """ЧЕК-ЛИСТ: Регистрация и прохождение KYC в CPAGrip / OGAds / AdCombo - пошагово.

CPAGrip:
1. Рег: username, email, пароль, страна, промо-код (если есть)
2. Профиль: имя, адрес, телефон, Skype/Telegram для связи с AM
3. Трафик: источники (FB, TT, IG, TikTok, Native, Email, Organic), примеры креативов/лендингов
4. KYC (если спросят): паспорт/ID (фото), селфи с паспортом, подтверждение адреса (коммуналка/банк <3 мес)
5. AM назначается после одобрения - пиши в Telegram/Skype сразу

OGAds:
1. Рег: email, пароль, страна
2. Профиль: полные данные, источники трафика (обязательно примеры!)
3. KYC: почти всегда - паспорт, селфи, адрес
4. Модерация 2-5 дней, AM пишет в TG/Email

AdCombo:
1. Рег: детальная анкета (имя, компания, сайт, источники, опыт, бюджет)
2. KYC: обязательно - паспорт, селфи, адрес, иногда видео-звонок
3. Модерация 3-7 дней, строже всех

ЧАСТЫЕ ОШИБКИ НОВИЧКА:
- Пустые поля \"источники трафика\" - авто-отказ
- \"Я новичок, учусь\" - отказ (пиши: \"опыт 1+ год, бюджет $500/мес, тестирую game hacks/sweeps\")
- Фейковые скрины статс - бан навсегда
- Нет Telegram/Skype для связи с AM - задержка недели

ДОКУМЕНТЫ: паспорт (разворот + селфи), коммунальный счет / выписка из банка (английский/русский), иногда - скрин админки трекера/РК."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'cpa-networks', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'kyc-checklist'}), 1, 'internal-cpa-networks', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:cpa-networks', 'internal-audit', 'arbitrage', 'kyc', 'checklist']), 9))
print(f'Tokens: {tokens}, Inserted 2/5')
db.commit()