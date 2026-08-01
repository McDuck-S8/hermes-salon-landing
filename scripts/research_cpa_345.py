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

# CPA-NETWORKS: 3/5 - Офферы и выбор
print('=== CPA-NETWORKS: запись 3/5 ===')
prompt = """ЧЕК-ЛИСТ: Как выбирать оффер в CPAGrip/OGAds - метрики и фильтры.

МЕТРИКИ (смотреть в Offers -> Columns):
1. EPC (Earnings Per Click) - главная: >$0.50 для Tier-1, >$0.20 для Tier-2/3
2. CR (Conversion Rate) - >5% для SOI/DOI, >10% для App Install, >1% для CPS
3. Approval Rate - >85% (ниже = много шейва/риджектов)
4. Cap (дневной лимит лидов) - есть ли место, не забит ли
5. Hold - Net-15 стандартно, Net-7 лучше, Instant - подозрительно
6. Тип конверсии: SOI (email submit) - легче, DOI (double opt-in) - платят больше, CPI (install) - нужны инсталлы, CPS (sale) - рискнее

ФИЛЬТРЫ ДЛЯ СТАРТА:
- Вертикаль: Content Locking / Game Hacks / Sweepstakes (проще)
- GEO: US/CA/UK/AU (Tier-1) - выше EPC, но дороже трафик
- GEO: BR/IN/ID/PH/VN (Tier-2/3) - дешевле трафик, ниже EPC, объём больше
- Устройства: Mobile (Android/iOS) - для OGAds, Desktop - для CPAGrip локеров

ПРИМЕР ВЫБОРА (Content-Locking-CPA):
CPAGrip -> Search: "Game Hack" -> Filter: EPC > $0.80, CR > 8%, Approval > 90%, GEO: US/CA/UK -> Sort by EPC -> Top 3 оффера -> Тест по $10 каждый.

ЧТО ИЗБЕГАТЬ: офферы с EPC $0.00 (новые/без даты), Cap 0/день, Approval < 70%, страшные лендинги (вирусный вид)."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'cpa-networks', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'offer-selection'}), 1, 'internal-cpa-networks', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:cpa-networks', 'internal-audit', 'arbitrage', 'offer-selection', 'checklist']), 9))
print(f'Tokens: {tokens}, Inserted 3/5')
db.commit()

# 4/5: Постбэки и трекинг
print('=== CPA-NETWORKS: запись 4/5 ===')
prompt = """ЧЕК-ЛИСТ: Настройка постбэков (S2S) в CPAGrip/OGAds + трекер (Keitaro/Binom).

CPAGrip постбэк:
URL: https://your-tracker.com/postback?subid={subid}&payout={payout}&status={status}
Параметры:
- {subid} / {aff_sub} - ваш click_id (обязательно!)
- {payout} - выплата за лид
- {status} - 1 (approved) / 2 (rejected) / 3 (pending)
- {offer_id} - ID оффера
- {aff_id} - ваш ID в сети

OGAds постбэк:
URL: https://tracker.com/postback?click_id={click_id}&payout={payout}&status={status}
Параметры: {click_id}, {payout}, {status}, {offer_name}

AdCombo постбэк:
URL: https://tracker.com/postback?subid={subid}&sum={payout}&status={status}
Параметры: {subid}, {sum}, {status}, {offer_id}

НАСТРОЙКА В KEITARO:
1. Sources -> CPAGrip -> Postback URL: вставить выше
2. Campaign -> Postback: включить, выбрать источник
3. Test: Tools -> Postback Test -> вставить test subid -> Send -> Check logs

ЧАСТЫЕ ОШИБКИ:
- Не передаёшь click_id в ссылке на оффер: ?subid={click_id} или &aff_sub={click_id}
- Не включил постбэк в кампейне трекера
- Не проверил тестовым постбэком (в логах трекера пусто)
- Используешь HTTP вместо HTTPS (блокируют)

ПРОВЕРКА: Пройди свой линк в инкогнито -> сделай конверсию -> проверь лог постбэка в трекере (должен быть status=1, payout>0)."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'cpa-networks', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'postback-setup'}), 1, 'internal-cpa-networks', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:cpa-networks', 'internal-audit', 'arbitrage', 'postback', 'keitaro', 'binom']), 9))
print(f'Tokens: {tokens}, Inserted 4/5')
db.commit()

# 5/5: Выплаты и налоги
print('=== CPA-NETWORKS: запись 5/5 ===')
prompt = """ЧЕК-ЛИСТ: Выплаты из CPA-сетей на карту/крипту - методы, лимиты, налоги (РФ 2025).

МЕТОДЫ ВЫПЛАТЫ (CPAGrip/OGAds/AdCombo):
1. Payoneer: $50 мин, $2.99 за вывод, карта Mastercard ($29.95/год), привязка к трекерам/сетям просто
2. USDT (TRC20): $50 мин, $0-5 комиссия сети, мгновенно, лучшая для РФ (нет SWIFT)
3. Wire (SWIFT): $100-500 мин, $15-50 комиссия, 3-7 дней, риск блокировки РФ банков
4. Capitalist: $10 мин, карта Visa/Mastercard, привязка к Payoneer/USDT, удобно для РФ
5. WebMoney / Payeer: старые методы, высокие комиссии, не рекомендую

НАЛОГИ (РФ, самозанятость 4% физлиц / 6% юрлица):
- Рег в "Мой налог" (App/Госуслуги) - 10 мин
- Каждый доход: чек в приложении (сумма в рублях по курсу ЦБ на день получения)
- КУДИР не нужен для самозанятых
- Патент (6% + фикс. плата) - если доход >2.4 млн/год или нужны страховые
- ИП УСН 6% - если скейл >$3-5к/мес, нужны страховки ~50к/год

СХЕМА "ДЕНЬГИ НА КАРТУ":
CPA-сеть -> USDT (TRC20) -> Обменник (BestChange, выбор по курсу) -> Карта РФ (Сбер/Тинькофф/Альфа) -> Чек в "Мой налог"
ИЛИ: CPA -> Payoneer -> Карта Payoneer -> ATM/покупки / Вывод на РФ карту через обменник

РИСКИ: AML-проверки обменников (чекни на GetBlock/Chainalysis), заморозка Payoneer (редко, но бывает), курсы обменников (-2-4% от рыночного)."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'cpa-networks', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'payouts-tax'}), 1, 'internal-cpa-networks', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:cpa-networks', 'internal-audit', 'arbitrage', 'payouts', 'tax', 'compliance']), 10))
print(f'Tokens: {tokens}, Inserted 5/5')
db.commit()
print('CPA-NETWORKS: 5/5 DONE')