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

# TRACKING: 5 записей
print('=== TRACKING: запись 1/5 ===')
prompt = """ТОП-3 трекера для CPA в 2025-2026 с конкретными цифрами.

1. KEITARO (Self-hosted, золотой стандарт):
   - Цена: $59/мес (Pro) или $149/мес (Agency) — lifetime лицензия $499/$999
   - VPS: 2 vCPU / 4GB RAM / 40GB SSD = $6-15/мес (Timeweb, Aeza, Contabo)
   - Фичи: кампании, потоки, фильтры, бот-фильтр, клоакинг, A/B, лендинги, постбэки, API, мульти-юзер
   - Интеграции: 100+ CPA сетей, FB/TT/Google Ads API, Telegram Bot API
   - Плюсы: полный контроль, данные твои, нет лимитов, клоакинг из коробки
   - Минусы: нужен VPS, настройка 1-2 дня, обновления вручную

2. BINOM (Self-hosted, быстрый, лёгкий):
   - Цена: $69/мес или $999 lifetime
   - VPS: 1 vCPU / 2GB RAM / 20GB SSD = $4-10/мес
   - Фичи: сверхбыстрые отчёты (клики за секунды), потоки, правила, постбэки, API
   - Плюсы: скорость отчётов, дешевле Keitaro, проще интерфейс
   - Минусы: меньше фич для клоакинга, нет встроенного лендинг-билдера

3. REDTRACK / VOLUUM (SaaS — когда не хочешь VPS):
   - RedTrack: $99/мес (100к кликов), $299/мес (1М) — облачный, быстрый старт
   - Voluum: $69/мес (100к) -> $699/мес (10М) — дороже, энтерпрайз
   - Плюсы: 0 админки, автоскейл, поддержка, быстрый старт
   - Минусы: лимиты кликов, данные у них, дороже при объёме, клоакинг ограничен

МОЙ ВЫБОР ДЛЯ СТАРТА: Keitaro на VPS ($59 + $10 = $69/мес) — инвестиция в контроль и клоакинг.
АЛЬТЕРНАТИВА $0: Google Sheets + Apps Script (см. запись 4)."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'tracking', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'top-trackers'}), 1, 'internal-tracking', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:tracking', 'internal-audit', 'arbitrage', 'keitaro', 'binom', 'redtrack']), 10))
print(f'Tokens: {tokens}, Inserted 1/5')
db.commit()

# 2/5: Keitaro глубоко
print('=== TRACKING: запись 2/5 ===')
prompt = """ЧЕК-ЛИСТ: Развёртывание Keitaro на VPS — от 0 до работающего трекера за 2 часа.

VPS ПОДГОТОВКА:
1. Провайдер: Timeweb / Aeza / Contabo / DigitalOcean — Ubuntu 22.04, 2 vCPU / 4GB RAM / 40GB SSD
2. SSH: ssh root@ip -> apt update && apt upgrade -y
3. Docker: curl -fsSL https://get.docker.com | sh
4. Docker Compose: apt install docker-compose-plugin

KEITARO УСТАНОВКА:
1. cd /opt && git clone https://github.com/keitaro/keitaro.git && cd keitaro
2. cp env.example .env -> редактируй: KEITARO_HOST=your-domain.com, DB_PASS=strongpass, LICENSE_KEY=your_key
3. docker compose up -d (поднимет: nginx, php-fpm, mysql, redis, clickhouse, cron)
4. Проверка: https://your-domain.com/admin -> логин admin / пароль из .env

НАСТРОЙКА ПОСЛЕ УСТАНОВКИ:
1. SSL: Settings -> SSL -> Let's Encrypt (авто) -> включаем Force HTTPS
2. Крон: Settings -> Cron -> включить все задачи (click processing, postbacks, reports)
3. Бот-фильтр: Settings -> Bot Filter -> включить (User-Agent + IP репутация)
4. Гео-база: Settings -> Geo DB -> обновить (MaxMind GeoLite2 бесплатно)
5. Часовой пояс: Settings -> Timezone -> Europe/Moscow (или твой)

КАМПАНИЯ ДЛЯ CPA:
1. Campaigns -> New -> Name: "CPAGrip_GameHacks_US" -> Traffic Source: Custom
2. Streams -> New Stream -> Type: Direct -> URL: https://cpa-network.com/lander/abc?subid={clickid}
3. Filters -> добавить: Bot Filter (enable), Country (US, CA, UK), Device (Desktop/Mobile)
4. Postback: Settings -> Postback URL -> вставить из CPAGrip -> Test -> Save
5. Landing Pages (опционально): New -> HTML код преленда -> Save -> привязать к Stream

ТЕСТ:
1. Campaign -> Get Link -> копируем tracking link
2. Открываем в инкогнито -> проходим флоу -> делаем конверсию
3. Reports -> Realtime -> проверяем: click -> lead -> payout
4. Postbacks Log -> проверяем: status=1, payout>0, subid совпал"""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'tracking', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'keitaro-setup'}), 1, 'internal-tracking', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:tracking', 'internal-audit', 'arbitrage', 'keitaro', 'setup', 'vps']), 9))
print(f'Tokens: {tokens}, Inserted 2/5')
db.commit()

# 3/5: Клоакинг и фильтры
print('=== TRACKING: запись 3/5 ===')
prompt = """ЧЕК-ЛИСТ: Клоакинг и защита в Keitaro — как не сгореть на модерации FB/TT/Google.

КЛОАКИНГ В KEITARO (Stream -> Filters -> Cloaking):
1. Safe Page (White Page): создаём чистую страницу на той же нише (блог/обзор/статья)
   - Хостим на том же домене / поддомене (safe.domain.com)
   - Никаких CPA ссылок, только контент + возможно безобидная кнопка "Read More"
2. Stream для бота/модератора:
   - Filter: ISP -> Cloudflare, Google, Facebook, Amazon, Microsoft, DigitalOcean, OVH, Hetzner
   - Filter: User-Agent -> googlebot, bingbot, facebookexternalhit, twitterbot, slackbot
   - Filter: IP Range -> известные диапазоны модераторов (есть базы в Keitaro Marketplace)
   - Action: Redirect -> Safe Page URL
4. Stream для живого трафика:
   - Filter: NOT (ISP ботов + User-Agent ботов + IP ботов)
   - Action: Direct -> Оффер / Преленд -> Оффер

ДОПОЛНИТЕЛЬНЫЕ ЗАЩИТЫ:
1. Bot Filter (Settings -> Bot Filter): включить + обновлять базу еженедельно
2. Click Processing: Settings -> Click Processing -> "Process unique clicks only" (дедуп)
3. Landing Page Protection: если хостим преленд на Keitaro -> добавить мета-тег noindex, nofollow
4. Local Storage / Cookie: сохранять click_id в localStorage для ретаргетинга

ПРОВЕРКА КЛОАКИНГА:
1. User-Agent Switcher (расширение) -> ставим "facebookexternalhit" -> открываем tracking link -> должен открыться Safe Page
2. VPN/Прокси с IP дата-центра (DigitalOcean, AWS) -> открываем -> Safe Page
3. Мобильный / домашний IP -> открываем -> Оффер / Преленд

РИСКИ: 
- Неполные базы IP модераторов -> пропуск бота на оффер -> бан аккаунта
- Safe Page слишком пустой -> ручная модерация -> бан
- Кэширование CDN (Cloudflare) -> кэширует Safe Page для всех -> решаем: Cloudflare Page Rules -> Bypass Cache на tracking domain"""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'tracking', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'cloaking'}), 1, 'internal-tracking', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:tracking', 'internal-audit', 'arbitrage', 'cloaking', 'keitaro', 'bot-filter']), 10))
print(f'Tokens: {tokens}, Inserted 3/5')
db.commit()

# 4/5: $0 трекинг (Google Sheets)
print('=== TRACKING: запись 4/5 ===')
prompt = """ЧЕК-ЛИСТ: Трекер на Google Sheets + Apps Script — $0, 30 минут настройки, для тестов до $100/день.

ПРИНЦИП: Apps Script принимает постбэк -> пишет в Google Sheets -> формулы считают CPA/ROI.

НАСТРОЙКА:
1. Создаём Google Таблицу: колонки A:Date, B:ClickID, C:Source, D:Campaign, E:Offer, F:Country, G:Device, H:Payout, I:Status, J:Revenue
2. Tools -> Script Editor -> вставляем код Apps Script:
```
function doPost(e) {
  const ss = SpreadsheetApp.openById('YOUR_SHEET_ID');
  const sheet = ss.getSheetByName('Data');
  const data = JSON.parse(e.postData.contents);
  const row = [new Date(), data.subid, data.source, data.campaign, data.offer_id, data.country, data.device, data.payout, data.status, data.payout];
  sheet.appendRow(row);
  return ContentService.createTextOutput('OK');
}
```
3. Deploy -> New Deployment -> Type: Web App -> Execute as: Me -> Who has access: Anyone -> Deploy -> копируем URL
4. В CPA сети (CPAGrip/OGAds): Postback URL = твой Apps Script URL?subid={subid}&payout={payout}&status={status}&offer_id={offer_id}&source=cpagrip

UTM В ССЫЛКЕ НА ОФФЕР:
https://cpa-network.com/lander/abc?aff_sub={click_id}&utm_source=fb&utm_medium=cpa&utm_campaign=test1
В Apps Script парсим: data.source = e.parameter.utm_source || 'cpagrip'

ФОРМУЛЫ В ТАБЛИЦЕ (в строке 2, тащим вниз):
- CPA: =IF(I2="approved", H2, 0) / COUNTIF(B:B, B2) — грубо
- ROI: =SUMIF(I:I, "approved", H:H) / SUM(траты из другой вкладки)
- Ежедневный отчёт: QUERY(Data!A:J, "select A, count(B), sum(H) where I='approved' group by A label count(B) 'Leads', sum(H) 'Revenue'")

ОГРАНИЧЕНИЯ:
- Лимит Apps Script: 20k выполнений/день (достаточно для <5000 кликов/день)
- Нет реалтайма (задержка 1-30 сек)
- Нет A/B, клоакинга, бот-фильтра
- Данные в Google (не твои полностью)

КОГДА ПЕРЕХОДИТЬ НА KEITARO: деньга >$100/день, нужен клоакинг, A/B, скорость, свои данные."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'tracking', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'free-tracking'}), 1, 'internal-tracking', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:tracking', 'internal-audit', 'arbitrage', 'google-sheets', 'apps-script', 'free']), 8))
print(f'Tokens: {tokens}, Inserted 4/5')
db.commit()

# 5/5: Сравнение и чек-лист выбора
print('=== TRACKING: запись 5/5 ===')
prompt = """СРАВНИТЕЛЬНАЯ ТАБЛИЦА: выбор трекера под этап (2025-2026).

| Критерий | Google Sheets ($0) | Binom ($69/мес) | Keitaro ($59/мес) | RedTrack ($99/мес) |
|----------|-------------------|----------------|------------------|-------------------|
| Стоимость в мес | $0 | $69 + $10 VPS | $59 + $10 VPS | $99 |
| VPS нужен | Нет | Да | Да | Нет (SaaS) |
| Скорость отчётов | Медленно | Мгновенно | Быстро | Мгновенно |
| Клоакинг | Нет | Базовый | Полный | Ограничен |
| Бот-фильтр | Нет | Базовый | Продвинутый | Есть |
| A/B тесты | Нет | Есть | Есть | Есть |
| Постбэки | Ручной | Авто | Авто | Авто |
| API | Нет | Есть | Есть | Есть |
| Мульти-юзер | Нет | Нет | Agency тариф | Есть |
| Данные | У Google | Твои на VPS | Твои на VPS | У них |
| Лимит кликов | ~5k/день | Безлимит | Безлимит | По тарифу |
| Сложность входа | 30 мин | 2-4 часа | 2-4 часа | 15 мин |

МОЯ ДОРОЖНАЯ КАРТА:
1. $0-50/день: Google Sheets + Apps Script (тест офферов, поиск рабочего)
2. $50-200/день: Binom (быстрее отчёты, дешевле Keitaro, хватает на скейл)
3. $200-500/день: Keitaro (клоакинг, бот-фильтр, лендинги, API для автоматизации)
4. $500+/день: Keitaro Agency + команда / или RedTrack/Voluum если лень админить VPS

ЧЕК-ЛИСТ ГОТОВНОСТИ К ПЕРЕХОДУ:
- [ ] Стабильный ROI > 30% 7 дней подряд
- [ ] Ежедневный бюджет > $50
- [ ] Нужен клоакинг (FB/TT модерация бьёт)
- [ ] Нужны A/B тесты лендингов/офферов
- [ ] Постбэки теряются / задерживаются в Sheets
- [ ] Хочу автоматизацию через API (правила, блэклисты)

ПРИОРИТЕТ: Не переплачивай за трекер, пока не ударишь в его лимиты."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'tracking', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'comparison'}), 1, 'internal-tracking', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:tracking', 'internal-audit', 'arbitrage', 'comparison', 'decision']), 10))
print(f'Tokens: {tokens}, Inserted 5/5')
db.commit()
print('TRACKING: 5/5 DONE')