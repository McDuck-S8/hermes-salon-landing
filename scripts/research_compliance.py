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

# COMPLIANCE: 5 записей
print('=== COMPLIANCE: запись 1/5 ===')
prompt = """ТОП-5 аспектов комплаенса, банков, выплат для арбитражника в РФ 2025-2026 с конкретными действиями.

1. ВИРТУАЛЬНЫЕ КАРТЫ ДЛЯ РАСХОДОВ (фарминг, расходы на рекламу):
   - PST.net: BINы US/EU, 3DS, $2/карта, пополнение USDT/Карта, API для автоматизации
   - 4x4.io: BINы US, 3DS, $1.5/карта, удобный интерфейс, команда
   - B4B (Payoneer): если есть Payoneer - выдача карт бесплатно, лимиты выше
   - Capitalist: карты Visa/Mastercard, пополнение USDT/Payoneer, $0.99/мес
   - Binance Card (если доступна в РФ): крипта -> карта, кэшбэк 1-8%
   - ЧЕК-ЛИСТ ФАРМИНГА: новая карта -> 3-5 дней мелкие траты (Google, Apple, Netflix) -> привязка к Ads -> запуск $5/день -> плавное увеличение
   - ЛИМИТЫ: не больше $500/день на новую карту первую неделю

2. КРИПТОВАЛЮТА ДЛЯ ВЫПЛАТ И РАСХОДОВ:
   - USDT TRC20 (Tron): $1-2 комиссия, 1-3 мин, основной для CPA сетей
   - USDT ERC20 (Ethereum): $5-20 комиссия, 5-30 мин, для крупных сумм
   - BTC / USDC: альтернативы
   - ОБМЕННИКИ: BestChange.ru -> сортировка по курсу + отзывам -> проверка на AML (GetBlock, Chainalysis, AMLBot - $1-3 за проверку)
   - ХОЛОДНЫЕ КОШЕЛЬКИ: Ledger / Trezor / Tangem - для хранения >$1000
   - ГОРЯЧИЕ: Trust Wallet / MetaMask / Phantom - для работы
   - ЧЕК-ЛИСТ ВЫВОДА: CPA -> USDT TRC20 -> Обменник (BestChange) -> Карта РФ -> Чек в "Мой налог"

3. PAYONEER / WISE / CAPITALIST - МЕЖДУНАРОДНЫЕ ВЫПЛАТЫ:
   - Payoneer: регистрация через партнёрку (CPA сеть даёт ссылку) -> верификация паспортом + селфи -> карта $29.95/год -> приём от сетей -> ATM/покупки/вывод на РФ карту через обменник
   - Wise: сложнее для РФ (нужен EU/US резидент), но лучшие курсы
   - Capitalist: рег по паспорту РФ, карта Visa/Mastercard, приём USDT/Payoneer, вывод на РФ карту
   - РИСКИ: заморозка при подозрении (AML), лимиты $10к/мес без доп. верификации

4. АНТИФРОД И КЛОАКИНГ - ЗАЩИТА ОТ БАНОВ:
   - Keitaro Bot Filter: включить + обновлять базу еженедельно (Settings -> Bot Filter)
   - IP Quality: проверка через IPQualityScore / Scamalytics API (в Keitaro есть интеграция)
   - User-Agent Spoofing: антидетект браузеры (Dolphin Anty, GoLogin, AdsPower) - профили под разные GEO/устройства
   - Прокси: мобильные (LTE/5G) - лучшие для FB/TT ($3-5/IP/день), резидентные ($1-2), дата-центр ($0.5) - только для скрейпинга
   - Клоакинг: Keitaro Streams -> Filters (ISP ботов + UA ботов + IP ботов) -> Safe Page
   - ЧЕК-ЛИСТ ПЕРЕД ЗАПУСКОМ РК: прокси чистые (проверь на whoer.net/ipqualityscore), антидетект профиль соответствует GEO, клоакинг протестирован (UA Switcher + VPN)

5. НАЛОГИ РФ (2025) - ОФИЦИАЛИЗАЦИЯ ДОХОДОВ:
   - САМОЗАНЯТОСТЬ (НПД 4% физлиц / 6% юрлиц): рег в "Мой налог" (Госуслуги/Приложение) 10 мин, нет КУДИР, нет страховых, лимит 2.4 млн/год
   - ИП УСН 6% (Доходы): рег 3-5 дней, страховки ~50к/год (пенсионные + мед), КУДИР обязателен, лимит 265 млн/год
   - ПАТЕНТ (6% + фикс. плата по региону): для розницы/услуг, нет КУДИР, страховки платишь сам
   - ЧЕК-ЛИСТ КАЖДОГО ДОХОДА: получение USDT -> обмен на RUB (курс ЦБ на день) -> чек в "Мой налог" (сумма в RUB) -> сохранение скрина обмена + чека
   - КОГДА ПЕРЕХОДИТЬ НА ИП: доход >$3-5к/мес стабильно, нужны страховые/пенсия, работа с контрагентами (договоры), найм сотрудников"""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'compliance', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'top-aspects'}), 1, 'internal-compliance', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:compliance', 'internal-audit', 'arbitrage', 'cards', 'crypto', 'payoneer', 'antifraud', 'tax']), 10))
print(f'Tokens: {tokens}, Inserted 1/5')
db.commit()

# 2/5: Карты глубоко
print('=== COMPLIANCE: запись 2/5 ===')
prompt = """ЧЕК-ЛИСТ: Работа с виртуальными картами - от покупки до фарминга и масштаба.

ВЫБОР СЕРВИСА (2025):
1. PST.net - лучший для FB/TT/Google Ads
   - BINы: 40+ стран (US, UK, DE, FR, CA, AU, SG, HK)
   - 3DS: есть (проходит авто-3DS в Ads)
   - Цена: $2/карта + 2-3% пополнения
   - API: да (авто-выпуск, пополнение, списание)
   - Команда: роли, лимиты, отчёты
2. 4x4.io - дешевле, удобнее для команды
   - BINы: US, UK, CA
   - 3DS: есть
   - Цена: $1.5/карта + 2% пополнения
   - API: есть
3. Capitalist - если нет USDT для пополнения других
   - Пополнение: карта РФ / Payoneer / USDT
   - Карты: Visa/Mastercard, $0.99/мес
   - 3DS: базовый

ФАРМИНГ НОВОЙ КАРТЫ (КРИТИЧНО!):
День 1-3: ТОЛЬКО мелкие проверенные траты
- Google Play / App Store: $1-5 (подписки, приложения)
- Netflix / Spotify / YouTube Premium: $5-15/мес
- Apple iCloud / Google One: $1-3/мес
- НЕ ПРИВЯЗЫВАЙ К ADS МГНОВЕННО!

День 4-7: Привязка к Ads аккаунту
- Создаёшь BM / Ads аккаунт на том же IP/профиле где фармил карту
- Привязываешь карту -> мелкий порог ($5-10)
- Запускаешь белую кампанию (Page Likes / Traffic на белый сайт) -> $3-5/день 3-5 дней
- Плавно увеличиваешь бюджет на 20-30% в день

День 7-14: Рабочие РК
- Переносишь на рабочие РК
- Бюджет $20-50/день
- Мониторишь успешность списаний (Success Rate > 95%)

ОШИБКИ = БАН КАРТЫ / BM:
- Мгновенная привязка к Ads -> отказ / бан
- Крупные списания с нового места -> фрод-алерт банка
- Один IP для 5+ карт -> связка -> массовый бан
- Пополнение с грязным USDT (AML) -> заморозка карты

МАСШТАБ (Command Center в PST/4x4):
- Роли: Admin (ты), Buyer (настройка РК), Finance (пополнение/отчёты)
- Лимиты на карту: Daily $100-500, Monthly $5-10к
- Авто-пополнение: если баланс < $50 -> пополнить $200
- Отчёты: еженедельный CSV -> загрузка в finance_core / таблицу

БЮДЖЕТ НА КАРТЫ (при $500/день расходов):
- 5-10 карт в ротации (меняешь каждые 2-3 недели)
- Стоимость: 10 карт * $2 = $20/мес + 3% пополнений (~$450/мес) = ~$470/мес
- Закладывай в COGS (Cost of Goods Sold) в P&L"""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'compliance', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'cards-farming'}), 1, 'internal-compliance', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:compliance', 'internal-audit', 'arbitrage', 'cards', 'farming', 'pst', '4x4']), 9))
print(f'Tokens: Inserted 2/5')
db.commit()

# 3/5: Крипта и AML
print('=== COMPLIANCE: запись 3/5 ===')
prompt = """ЧЕК-ЛИСТ: Криптовалюта для арбитражника - получение, обмен, вывод, безопасность.

ПОЛУЧЕНИЕ ИЗ CPA СЕТЕЙ:
1. Настройка в CPAGrip/OGAds/AdCombo: Payout Method -> USDT TRC20 -> ТВОЙ TRC20 адрес
2. Мин. выплата: $50 (CPAGrip, OGAds), $50-100 (AdCombo)
3. Холд: Net-15 (стандарт), иногда Net-7 для топов
4. Адрес: ОДИН адрес на сеть (не путай с ERC20!)

ОБМЕН НА RUB (Карта РФ):
1. BestChange.ru -> USDT TRC20 -> Сбербанк/Тинькофф/Альфа/Райф
2. Фильтры: Рейтинг > 4.5, Отзывы > 100, Время работы > 1 год
3. Проверка AML (ОБЯЗАТЕЛЬНО перед большими суммами):
   - GetBlock.io / AMLBot.pro / Chainalysis (API) -> $1-3 за проверку
   - Если Risk Score > 30% -> НЕ используй этот обменник
   - Чистый USDT = зелёная зона
4. Курс: Рыночный - 1.5-3% (комиссия обменника + спред)
5. Лимиты: обычно 50к-500к RUB за заявку, можно дробить

СХЕМА БЕЗОПАСНОГО ВЫВОДА:
CPA сеть -> Твой TRC20 (Trust Wallet / MetaMask) -> 
-> Разбивка на мелкие суммы ($100-500) -> 
-> Разные обменники (ротация 3-5) -> 
-> Разные карты (ротация 2-3) -> 
-> Чек в "Мой налог" КАЖДЫЙ РАЗ

ХРАНЕНИЕ:
- < $1000: Trust Wallet / MetaMask (горячий)
- $1000-10000: Tangem / Ledger Nano S Plus (холодной, удобный)
- > $10000: Ledger Nano X / Trezor Safe 3 + Passphrase (макс. безопасность)
- Seed фраза: ТОЛЬКО на бумаге, в 2 местах (дом + сейф), НИГДЕ ЦИФРОВО

РИСКИ И ЗАЩИТА:
- AML-заморозка на обменнике: используй только проверенные, дроби суммы
- Фишинг: проверяй URL обменника (BestChange даёт проверенные ссылки)
- Потеря доступа: seed фраза = доступ ко ВСЕМ средствам
- Налоги: каждый обмен = доход в RUB по курсе ЦБ на день -> чек в "Мой налог" (4%)"""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'compliance', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'crypto-aml'}), 1, 'internal-compliance', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:compliance', 'internal-audit', 'arbitrage', 'crypto', 'aml', 'bestchange', 'withdrawal']), 9))
print(f'Tokens: Inserted 3/5')
db.commit()

# 4/5: Антифрод и клоакинг
print('=== COMPLIANCE: запись 4/5 ===')
prompt = """ЧЕК-ЛИСТ: Антифрод, клоакинг, прокси, антидетект - полная защита РК.

ПРОКСИ (выбор под источник):
1. TIKTOK ADS / FB ADS / GOOGLE ADS:
   - МОБИЛЬНЫЕ (LTE/5G) - лучшие, trust score 90-99%
   - Провайдеры: iProxy, MobileProxy.space, Proxy-Seller (mobile), AstroProxy
   - Цена: $3-7/IP/день (аренда модема) или $30-50/мес за выделенный
   - 1 IP = 1 Ads аккаунт = 1 антидетект профиль
2. TELEGRAM / НАТИВКА / ПУШ:
   - РЕЗИДЕНТНЫЕ (ISP домашние) - достаточно
   - Провайдеры: Bright Data, Smartproxy, Oxylabs, Proxy-Seller (residential)
   - Цена: $1-3/GB или $5-15/IP/мес
3. СКРЕЙПИНГ / ПАРСИНГ:
   - ДАТА-ЦЕНТР (DC) - дешево, быстро, низкий trust
   - Цена: $0.3-1/IP/мес

АНТИДЕТЕКТ БРАУЗЕРЫ (2025):
1. Dolphin Anty - лучший для команд, бесплатно до 10 профилей, затем $89/мес
2. GoLogin - удобный, $24/мес (50 профилей), есть API
3. AdsPower - популярный в Китае/СНГ, $54/мес (100 профилей), RPA
4. Octo Browser - новый, быстрый, $29/мес (10 профилей)

НАСТРОЙКА ПРОФИЛЯ (1 IP = 1 Профиль = 1 Ads Аккаунт):
- User-Agent: Chrome latest на Windows 10/11 или macOS (под твой GEO)
- WebRTC: отключен (или подменён на IP прокси)
- Canvas / WebGL / AudioContext: Noise mode (уникальный отпечаток)
- Timezone / Language / Geolocation: под GEO таргета
- Screen Resolution: типичный для устройства (1920x1080 / 1366x768)
- Fonts / Extensions: минимальный набор (как у обычного юзера)
- Cookies / LocalStorage: чистые при создании, накапливаются при фарминге

КЛОАКИНГ В KEITARO (повторение + детали):
Stream 1 (Боты/Модераторы):
- Filter: ISP -> Cloudflare, Google, Facebook, Amazon, Microsoft, DigitalOcean, OVH, Hetzner, Linode, Vultr
- Filter: UA -> googlebot, bingbot, facebookexternalhit, twitterbot, slackbot, telegrambot
- Filter: IP -> известные подсети модераторов (Keitaro Marketplace -> IP Lists)
- Action: Redirect -> Safe Page (https://safe.yourdomain.com/article)

Stream 2 (Живой трафик):
- Filter: NOT (все выше)
- Action: Direct -> Преленд / Оффер

SAFE PAGE (ТРЕБОВАНИЯ):
- Контент: статья/обзор/блог на нише (500+ слов, фото, видео)
- Нет CPA ссылок, нет локеров, нет агрессивных CTA
- Meta: noindex, nofollow (опционально)
- Скорость: <2с загрузки, HTTPS, мобильная версия
- Домен: тот же или поддомен (safe.domain.com)

ПРОВЕРКА (КАЖДЫЙ ЗАПУСК):
1. UA Switcher -> facebookexternalhit -> твой трекинг линк -> Safe Page? OK
2. VPN (DigitalOcean IP) -> трекинг линк -> Safe Page? OK
3. Мобильный IP (твой телефон) -> трекинг линк -> Оффер/Преленд? OK
4. Keitaro -> Reports -> Realtime -> боты на Safe Page, живые на Оффере? OK"""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'compliance', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'antifraud-cloaking'}), 1, 'internal-compliance', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:compliance', 'internal-audit', 'arbitrage', 'antifraud', 'cloaking', 'proxies', 'antidetect', 'keitaro']), 10))
print(f'Tokens: Inserted 4/5')
db.commit()

# 5/5: Налоги и дорожная карта
print('=== COMPLIANCE: запись 5/5 ===')
prompt = """ЧЕК-ЛИСТ: Налоги РФ 2025 - от самозанятости к ИП, дорожная карта легализации.

РЕЖИМЫ (2025):
1. САМОЗАНЯТОСТЬ (НПД):
   - Ставка: 4% (физлица) / 6% (юрлица/ИП)
   - Лимит: 2.4 млн RUB/год
   - Рег: 10 мин в "Мой налог" (Госуслуги/Приложение)
   - Отчётность: НЕТ (только чеки в приложении)
   - Страховки: НЕТ (добровольно ~50к/год за пенсию)
   - КУДИР: НЕТ
   - Идеально для: старт, тесты, доход <$2к/мес

2. ИП УСН "ДОХОДЫ" (6%):
   - Ставка: 6% от выручки
   - Лимит: 265 млн RUB/год (2025)
   - Рег: 3-5 дней через Госуслуги/МФЦ/Нотариус
   - Страховки: ОБЯЗАТЕЛЬНЫ ~50к/год (пенс. 34к + мед. 9к + травм. 0.1%)
   - КУДИР: ОБЯЗАТЕЛЬНЫЙ (простой Excel/Google Sheets)
   - Отчётность: Декларация раз в год (до 25 апреля)
   - Банк-счёт: ОБЯЗАТЕЛЬНЫЙ (для входящих платежей)
   - Идеально для: скейл >$3-5к/мес, работа с контрагентами, найм

3. ПАТЕНТ (ПСН):
   - Ставка: 6% от потенциального дохода (по региону) + фикс. плата
   - Лимит: 60 млн RUB/год, до 15 сотрудников
   - Страховки: платишь сам (как ИП)
   - КУДИР: НЕТ (только книга учёта доходов)
   - Только для: розница, бытовые услуги, такси, обучение (не для CPA напрямую)

ДОРОЖНАЯ КАРТА ЛЕГАЛИЗАЦИИ:
Месяц 1-3 (Тест): Самозанятость
- Рег в "Мой налог"
- Каждый вывод: обмен USDT -> RUB (курс ЦБ) -> чек в приложении
- Учёт в finance_core / Google Sheets: Дата, USDT, RUB, Чек №

Месяц 4-6 (Стабилизация $1-3к/мес): Самозанятость + оптимизация
- Отдельная карта для бизнеса (Тинькофф Бизнес / МодульБанк / Точка)
- Учёт расходов (карты, прокси, трекер, хостинг) -> уменьшают налог? НЕТ (НПД 4% от выручки без вычетов)
- Накопление под ИП регистрацию (~15к)

Месяц 7-12 (Скейл >$3к/мес стабильно): Переход на ИП УСН 6%
- Рег ИП (выбор банка: Тинькофф/МодульБанк/Сбер Бизнес - тариф 0 руб/мес первый год)
- Настройка 1С / Моё Дело / Контур.Эльба для учёта (или Excel КУДИР)
- Оплата страховок за год вперёд (~50к) -> снижает налог на 50к
- Найм ВА / редактора (ГПХ договоры, самозанятые) -> расходы НЕ вычитаются из УСН 6% (только страховки)

ЧЕК-ЛИСТ КАЖДОЙ НЕДЕЛИ:
[ ] Все выводы занесены в "Мой налог" (чеки есть)
[ ] Расходы зафиксированы в finance_core (для P&L и будущего ИП)
[ ] USDT на холодном кошельке > недели расходов
[ ] Карты для расходов фармятся / живы
[ ] Прокси / антидетект профили чистые
[ ] Keitaro бот-фильтр обновлён

ПРИОРИТЕТ: Не жди когда заработаю. Рег самозанятость ДЕНЬ 1. Это 10 минут и спасает от вопросов банка/налоговой."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'compliance', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'tax-roadmap'}), 1, 'internal-compliance', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:compliance', 'internal-audit', 'arbitrage', 'tax', 'samozanyatost', 'ip', 'roadmap']), 10))
print(f'Tokens: Inserted 5/5')
db.commit()
print('COMPLIANCE: 5/5 DONE')