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

# TRAFFIC-SOURCES: 5 записей
print('=== TRAFFIC-SOURCES: запись 1/5 ===')
prompt = """ТОП-3 источника трафика для старта CPA в 2025-2026 с конкретными цифрами.

1. TIKTOK ADS (лучший для контент-локеров / game hacks / app installs):
   - Мин. депозит: $20 (рег) / $50 (рабочий бюджет)
   - CPM: $1-5 (US), $0.30-1.50 (Tier-2/3)
   - CPC: $0.10-0.50
   - Таргетинг: интересы (gaming, tech, apps), возраст 13-35, пол, устройства, ОС
   - Креативы: вертикальное видео 9:16, 15-30 сек, хуки в первые 3 сек, CTA в конце
   - Модерация: строгая к клоакингу, adult, gambling — нужен агентский аккаунт или клоакинг
   - Агентство: $500-1000/мес за доступ к agency ad account (меньше банов)
   - ROI: 30-100% при умелом подходе, скейл до $500-1000/день

2. TELEGRAM ADS / КАНАЛЫ (дешевый, нативный, для RU/СНГ):
   - Официальный Telegram Ads: мин. €100, CPM €2-10, таргетинг по каналам/интересам
   - Покупка постов в каналах: Telega.in, Epicstars, Getgems — $5-50 за пост в канале 10-50к
   - Тизерки: 1-2 рубля за клик, большой охват, низкое качество
   - Боты: автопостинг в группы, рассылки — риск бана
   - Лучше для: RU/СНГ офферы (nutra, sweeps, crypto), низкий чек

3. FACEBOOK/INSTAGRAM ADS (классика, но сложно):
   - BM + фановые аккаунты ($5-20 за шт) или агентские ($200-500/мес)
   - Клоакинг обязателен (Keitaro + фильтры + safe page)
   - CAPI (Conversions API) + Pixel для оптимизации
   - CPM: $5-15 (US), $1-3 (Tier-2/3)
   - Вертикали: nutra, sweeps, finance, dating, crypto
   - Риск: постоянные баны, нужны фермы аккаунтов, прокси, антидетект браузеры

МОЙ ВЫБОР ДЛЯ СТАРТА ($50-100 бюджет):
Неделя 1-2: TikTok Ads (самостоятельно, без агентства) — тест 3-5 креативов по $10-20
Неделя 3-4: Telegram каналы (RU/СНГ) — параллельно, дешевле лиды
Месяц 2+: FB/IG если нужен скейл Tier-1 и есть бюджет на ферму/клоакинг."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'traffic-sources', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'top-sources'}), 1, 'internal-traffic-sources', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:traffic-sources', 'internal-audit', 'arbitrage', 'tiktok', 'telegram', 'facebook']), 10))
print(f'Tokens: {tokens}, Inserted 1/5')
db.commit()

# 2/5: TikTok Ads глубоко
print('=== TRAFFIC-SOURCES: запись 2/5 ===')
prompt = """ЧЕК-ЛИСТ: Запуск TikTok Ads для CPA (Content Locking / Game Hacks) — от 0 до первых лидов.

ПОДГОТОВКА:
1. Аккаунт: TikTok Ads Manager -> регистрация (бизнес/индивидуал), верификация email/телефон
2. Пиксель: Assets -> Events -> Create Pixel -> Web -> Manual -> установить на лендинг/преленд
3. Клоакинг (если вертикаль серенькая): Keitaro -> Stream -> Filter -> Safe Page (white hat) -> Offer
   Safe page: статья/обзор/блог на той же нише, без прямых CPA ссылок

КАМПАНИЯ:
1. Objective: Conversions (Complete Registration / App Install / Click)
2. Budget: Daily $20-50 (не Lifetime!)
3. Ad Group: Placement -> TikTok only (отключить Pangle/BuzzVideo для качества)
4. Targeting: Location (US/CA/UK или BR/ID/PH), Age 18-35, Gender: All, Languages: English
   Interests: Mobile Games, Action Games, Strategy Games, Tech, Apps
5. Optimization: Conversion Event -> CompleteRegistration (или ваш пиксель)
   Bid: Cost Cap (начни с $2-5 за лид) или Lowest Cost

КРЕАТИВЫ (3-5 на запуск):
- Формат: 9:16, 1080x1920, MP4, <500MB, 15-30 сек
- Структура: Хук (0-3с) -> Проблема/Боль (3-8с) -> Решение (8-20с) -> CTA (20-30с)
- Музыка: тикток-тренды (Commercial Sounds Library)
- Текст на видео: да, крупно, контрастно
- CTA кнопка: "Download", "Get Now", "Claim Reward"

ЗАПУСК И ОПТИМИЗАЦИЯ:
День 1-2: не трогать, собирать данные (минимум 20-30 конверсий на адгруппу)
День 3: выключить плохие креативы (CPA > target * 1.5), добавить новые
День 5-7: сузить таргетинг (возраст, интересы), тестировать новые хуки
Неделя 2: Lookalike аудитории (1%, 3%, 5% от конвертировавшихся)

МЕТРИКИ ДЛЯ РЕШЕНИЯ:
- CPA < $3 (Tier-1) / < $1 (Tier-2/3) -> скейл
- CTR > 1.5% -> креатив работает
- CVR > 5% -> лендинг/оффер конвертит
- CPM > $10 -> аудитория перегорела, меняй таргетинг/креатив."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'traffic-sources', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'tiktok-checklist'}), 1, 'internal-traffic-sources', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:traffic-sources', 'internal-audit', 'arbitrage', 'tiktok', 'checklist']), 9))
print(f'Tokens: {tokens}, Inserted 2/5')
db.commit()

# 3/5: Telegram каналы
print('=== TRAFFIC-SOURCES: запись 3/5 ===')
prompt = """ЧЕК-ЛИСТ: Покупка трафика в Telegram-каналах (RU/СНГ) для CPA.

ПЛАТФОРМЫ:
1. Telega.in - крупнейшая биржа, фильтры по темам/охватам/цене, защита сделки
2. Epicstars - удобный интерфейс, есть API, статистика каналов
3. Getgems / Telemetr / TGStat - аналитика каналов перед покупкой
4. Прямые договорённости с админами - дешевле, но риск мошенничества

ВЫБОР КАНАЛА:
1. Тема: игры / софт / заработок / техно / мемы (под вертикаль)
2. Ох
   Подписчики: 10к-100к (микро) = дешевле, выше engagement; 100к+ = охват, дороже
3. ER (Engagement Rate): >15% для микро, >8% для макро (просмотры/подписчики)
4. Цена за пост: $5-50 (10-50к), $50-200 (100к+)
5. Формат: пост с фото/видео + кнопка/ссылка, фиксация 24-48ч
6. Условия: без удаления, статистика в личке, возврат если бот/накрутка

СТРАТЕГИЯ:
- Тест: 3-5 каналов по $10-20 каждый = $50-100 бюджет
- Трек: уникальная ссылка на канал (UTM: utm_source=tg&utm_medium=channel&utm_campaign={name})
- Метрики: CPC < 5 руб, CPL < 100-200 руб (под RU nutra/sweeps)
- Масштаб: находишь 2-3 рабочих канала -> договоришься на постоянку (скидка 20-30%)
- Ретаргетинг: пиксель на лендинге -> аудитория посетителей -> ТГ таргет (Telegram Ads)

РИСКИ: накрутка ботов (проверяй TGStat/Telemetr), админ удалит пост, бан канала, низкое качество трафика."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'traffic-sources', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'telegram-checklist'}), 1, 'internal-traffic-sources', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:traffic-sources', 'internal-audit', 'arbitrage', 'telegram', 'checklist']), 9))
print(f'Tokens: {tokens}, Inserted 3/5')
db.commit()

# 4/5: Нативка / Push / Pop
print('=== TRAFFIC-SOURCES: запись 4/5 ===')
prompt = """ЧЕК-ЛИСТ: Нативная реклама / Push / Pop-under (PropellerAds, RichAds, AdMaven, Monetizer).

ПЛАТФОРМЫ (ТОП-4):
1. PropellerAds - крупнейшая, push + pop + native + interstitial, $100 мин депозит
2. RichAds - качественный push/native, автооптимизация (CPA Goal), $100 мин
3. AdMaven - push + pop, сильные в Tier-2/3, $50 мин
4. Monetizer - попандеры, дешево, большой объём, $50 мин

НАСТРОЙКА КАМПАНИИ (Push - лучший для CPA):
1. Депозит: $100-200 для тестов
2. Формат: Push Notifications (Classic / In-Page)
3. GEO: Tier-2/3 (BR, IN, ID, PH, VN, TH, MX, CO, PE, RU) - дешевле, объёмнее
4. Таргетинг: OS (Android/iOS), Browser, Connection Type (WiFi/3G/4G), Carrier
5. Частота: 1-3 показа в день на юзера (Frequency Cap)
6. Блэклисты: отключить плохие сайды/зоны (по ID) после сбора данных

КРЕАТИВЫ ДЛЯ PUSH:
- Заголовок: 30-50 символов, интрига/боль/выгода
- Текст: 60-90 символов, конкретика + CTA
- Иконка: 192x192, яркая, релевантная
- Картинка (Big Image): 360x240, опционально, повышает CTR 20-30%

МЕТРИКИ:
- CPC: $0.01-0.05 (Tier-2/3), $0.05-0.15 (Tier-1)
- CTR: >0.5% нормально, >1% хорошо
- CVR: зависит от лендинга/оффера
- ROI: 20-80% при умелом подходе

ОПТИМИЗАЦИЯ:
- День 1-2: сбор данных, все зоны включены
- День 3: блэклист зон с CPA > target * 2 или 0 конверсий при >100 кликах
- День 5: вайт-лист лучших зон -> отдельная кампания с higher bid
- Неделя: тест новых креативов (3-5 в неделю), сужение GEO/OS

ДЛЯ СТАРТА: RichAds (CPA Goal автооптимизация) + Tier-2/3 GEO + Push + $100 бюджет."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'traffic-sources', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'native-push-checklist'}), 1, 'internal-traffic-sources', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:traffic-sources', 'internal-audit', 'arbitrage', 'native', 'push', 'propellerads', 'richads']), 9))
print(f'Tokens: {tokens}, Inserted 4/5')
db.commit()

# 5/5: Сравнение и выбор
print('=== TRAFFIC-SOURCES: запись 5/5 ===')
prompt = """СРАВНИТЕЛЬНАЯ ТАБЛИЦА: выбор источника трафика под задачу (2025-2026).

| Критерий | TikTok Ads | Telegram Каналы | FB/IG Ads | Нативка/Push (RichAds) |
|----------|------------|-----------------|-----------|------------------------|
| Мин. бюджет | $50 | $20 | $200 (ферма/клоак) | $100 |
| CPM (US) | $2-5 | N/A | $5-15 | $1-3 |
| CPM (RU/Tier-2) | $0.5-1.5 | $0.5-2 (CPC) | $1-3 | $0.3-1 |
| Сложность входа | Низкая | Низкая | Очень высокая | Низкая |
| Клоакинг нужен | Иногда | Нет | Обязательно | Иногда |
| Скорость старта | 30 мин | 1 час | 1-2 дня | 30 мин |
| Качество трафика | Высокое | Среднее | Высокое | Низкое-среднее |
| Скейл | Отличный | Ограничен каналами | Огромный | Огромный |
| Вертикали | Game, App, Sweeps | Nutra, Sweeps, Crypto | Все | Все (кроме белых) |
| Риск бана | Средний | Низкий | Критический | Низкий |

МОЯ СТРАТЕГИЯ (Content-Locking-CPA, $100 старт):
1. День 1-14: TikTok Ads ($70) - 3 креатива, US/CA/UK, тест офферов CPAGrip
2. День 1-14 параллельно: Telegram каналы ($30) - 3 канала RU, тест sweeps/nutra
3. День 15-30: работающий источник -> скейл бюджет x2-x3, новые креативы/GEO
4. День 30+: если TikTok работает -> добавить RichAds Push ($100) для скейла объёма
5. Месяц 3+: если нужен Tier-1 скейл -> FB/IG (только с фермой/клоакингом)

ПРИОРИТЕТ: TikTok (качество+скейл) > Telegram (дешево+RU) > Push (объём) > FB (только профи)."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'traffic-sources', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'comparison'}), 1, 'internal-traffic-sources', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:traffic-sources', 'internal-audit', 'arbitrage', 'comparison', 'decision']), 10))
print(f'Tokens: {tokens}, Inserted 5/5')
db.commit()
print('TRAFFIC-SOURCES: 5/5 DONE')