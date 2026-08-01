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

# CREATIVES: 5 записей
print('=== CREATIVES: запись 1/5 ===')
prompt = """ТОП-5 формул креативов для CPA в 2025-2026 с конкретными шаблонами и примерами.

1. ФОРМУЛА "БОЛЬ + РЕШЕНИЕ" (PAS - Problem Agitation Solution):
   Структура: Боль (0-3с) -> Разгорание боли (3-8с) -> Решение (8-20с) -> CTA (20-30с)
   Пример (Game Hack): "Твой аккаунт заблокировали за читы? (боль) -> Потерял все скины, ранг, годы игры (разгорание) -> Этот анлокер вернёт всё за 2 минуты (решение) -> Ссылка в профиле (CTA)"
   Визуал: экран бана -> грустное лицо -> процесс анлока -> радость -> кнопка
   Работает для: Game Hacks, App Unlocks, Account Recovery

2. ФОРМУЛА "СЕКРЕТ / ИНТРИГА" (Cliffhanger):
   Структура: "Они не хотят, чтобы ты знал..." (0-2с) -> Подсказка (2-6с) -> Раскрытие (6-15с) -> Доказательство (15-25с) -> CTA
   Пример (Sweeps): "Apple не хочет, чтобы ты знал об этом... (интрига) -> Есть способ получить iPhone 15 за $1 (подсказка) -> Просто заполни анкету и жди курьера (раскрытие) -> Скрин выплаты $0.99 (доказательство) -> Участвуй тут (CTA)"
   Визуал: заштрихованный лого Apple -> загадочное лицо -> процесс -> скрин банка -> кнопка
   Работает для: Sweepstakes, Giveaways, Free Trials

3. ФОРМУЛА "СОЦИАЛЬНОЕ ДОКАЗАТЕЛЬСТВО" (Social Proof):
   Структура: Кейс друга/знакомого (0-5с) -> Детали (5-12с) -> Твой результат (12-20с) -> "Ты тоже можешь" (20-30с)
   Пример (Nutra): "Мой друг скинул 15 кг за месяц не сидя на диете (кейс) -> Пил это утром натощак (детали) -> Я попробовал - минус 7 за 2 недели (результат) -> Попробуй сам, ссылка в био (CTA)"
   Визуал: фото до/после -> процесс приёма -> твоё фото -> кнопка
   Работает для: Nutra, Weight Loss, Supplements, Finance

4. ФОРМУЛА "НЕГАТИВНЫЙ МАРКЕТИНГ" (Anti-Marketing):
   Структура: "Хватит терять деньги на..." (0-3с) -> Почему не работает (3-8с) -> Что работает (8-18с) -> CTA
   Пример (Finance/Crypto): "Хватит терять деньги на шиткоинах (боль) -> 99% ругаются, ликвидность уходит (почему) -> Этот бот находит джемы до листинга (решение) -> Подключи кошелёк (CTA)"
   Визуал: красный график вниз -> скучающий трейдер -> зелёный график вверх -> кнопка
   Работает для: Crypto, Trading, Finance, Betting

5. ФОРМУЛА "UGC / НАТИВНАЯ ИНТЕГРАЦИЯ" (Native/UGC):
   Структура: "Просто делюсь находкой..." (0-2с) -> Демонстрация (2-15с) -> "Проверил сам — работает" (15-22с) -> CTA
   Пример (App Install): "Нашёл игру, где реально платят за прохождение уровней (находка) -> Показываю вывод $50 за 3 дня (демо) -> Вывел на карту, пришло за 10 мин (проверка) -> Название в комментариях (CTA)"
   Визуал: телефон в руке -> экран игры -> банковское приложение -> комментарии
   Работает для: App Installs, Game Rewards, Cashback Apps

МОЯ СТРАТЕГИЯ ТЕСТИРОВАНИЯ:
Запуск: 3 креатива по формулам 1, 3, 5 (самые конвертят для CPA)
Неделя 2: добавить 2 и 4
Метрика: Hook Rate (3-sec view) > 25%, Hold Rate > 30%, CTR > 1.5%"""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'creatives', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'top-formulas'}), 1, 'internal-creatives', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:creatives', 'internal-audit', 'arbitrage', 'formulas', 'PAS', 'social-proof', 'UGC']), 10))
print(f'Tokens: {tokens}, Inserted 1/5')
db.commit()

# 2/5: Hooks и заголовки
print('=== CREATIVES: запись 2/5 ===')
prompt = """ЧЕК-ЛИСТ: Хуки и заголовки, которые останавливают скролл — 50 готовых шаблонов по нишам.

ГЕЙМИНГ / GAME HACKS:
1. "Получи {скин/ранк/валюту} бесплатно за 2 минуты"
2. "Почему 90% игроков не знают об этом..."
3. "Анбан аккаунта за 5 минут — инструкция"
4. "Этот чит не детектится уже 6 месяцев"
5. "Как получить {скин} который стоит $500 за $0"

НУТРА / WEIGHT LOSS:
6. "Минус 10 кг за месяц без спортзала и диет"
7. "Она пила это каждое утро — результат шокировал врачей"
8. "Почему твой метаболизм сломан (и как починить)"
9. "3 продукта, которые жарят жир во сне"
10. "Врачи скрывают этот секрет похудения"

СВИПСТЕЙКС / GIVEAWAYS:
11. "Apple раздаёт iPhone 15 — осталось 50 штук"
12. "Заполни анкету за 30 сек — получи шанс на $1000"
13. "Ты не выиграл, потому что не знал этого..."
14. "Секрет победы в розыгрышах — 3 шага"
15. "Осталось 12 минут до конца розыгрыша iPhone"

ФИНАНСЫ / КРИПТА:
16. "Как заработать $100 в день с телефона"
17. "Этот алткоин даст x100 к концу года"
18. "Банки не хотят, чтобы ты знал об этом счете"
19. "Пассивный доход $500/мес — настройка за 10 мин"
20. "Почему 95% трейдеров теряют деньги"

APP INSTALLS / REWARDS:
21. "Играю в игру и получаю деньги на карту"
22. "Вывел $50 за вечер — вот доказательство"
23. "Топ-5 игр, которые платят реальные деньги"
24. "Забудь про кликеры — это платит в 10 раз больше"
25. "Ссылка в профиле — начни зарабатывать сейчас"

УНИВЕРСАЛЬНЫЕ (под любую нишу):
26. "Ошибка, которая стоит тебе денег каждый день"
27. "3 секунды, чтобы изменить свою жизнь"
28. "То, что гуру не рассказывают бесплатно"
29. "Проверено лично: работает или деньги назад"
30. "Сохрани этот видео, прежде чем удалят"

ПРАВИЛА ХУКА:
- Первые 1.5 секунды решают всё
- Конкретика > абстракция (цифры, имена, сроки)
- Боль/страх/любопытство/жадность — 4 триггера
- Визуал должен дублировать смысл хука
- Тестируй 3-5 хуков на один оффер"""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'creatives', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'hooks'}), 1, 'internal-creatives', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:creatives', 'internal-audit', 'arbitrage', 'hooks', 'headlines', 'templates']), 9))
print(f'Tokens: {tokens}, Inserted 2/5')
db.commit()

# 3/5: Визуальная структура
print('=== CREATIVES: запись 3/5 ===')
prompt = """ЧЕК-ЛИСТ: Визуальная структура конвертятщего Shorts/Reels — кадр за кадром.

КАДР 0-1.5с (ХУК) — САМЫЙ ВАЖНЫЙ:
- Движение в первом кадре (рука, лицо, экран, переход)
- Яркий контраст (красный/зелёный/жёлтый на фоне)
- Текст НА ЭКРАНЕ: крупно, белый+чёрный контур, по центру
- Звук: трендовый звук / резкий звук / голос "Стоп!" / "Смотри!"
- Пример: экран телефона с уведомлением "Вывод $500 выполнен" + палец тапает

КАДРЫ 1.5-5с (ПРОБЛЕМА / БОЛЬ):
- Показываешь БОЛЬ зрителя (блокировка, ошибка, лишний вес, пустой кошелёк)
- Текст: "Знакомо?" / "Тоже самое?" / "Было так же?"
- Эмоция: фрустрация, удивление, страх
- Длительность: 3-4 секунды (не затягивай)

КАДРЫ 5-15с (РЕШЕНИЕ / ПРОЦЕСС):
- Показываешь РЕШЕНИЕ в действии (скриншоты, запись экрана, демонстрация)
- Пошагово: 1 -> 2 -> 3 (максимум 3 шага)
- Текст на каждом шаге: "Шаг 1: Заходишь тут" / "Шаг 2: Нажимаешь тут"
- Скорость: динамично, без пауз, ускоренный речь (1.25-1.5x)

КАДРЫ 15-25с (ДОКАЗАТЕЛЬСТВО / РЕЗУЛЬТАТ):
- РЕАЛЬНЫЙ результат: банковское приложение, профиль в игре, весы, почта с кодом
- Скрывай лишнее (номер карты, email) — блюр / маркер
- Текст: "Вот доказательство" / "Пришло за 5 минут" / "Работает!"
- Эмоция: радость, облегчение, уверенность

КАДРЫ 25-30с (CTA — CALL TO ACTION):
- ЧЁТКИЙ CTA: "Ссылка в профиле" / "Комментарий закрепил" / "Название в описании"
- Визуал: палец указывает вниз / анимированная стрелка / стикер "Link in Bio"
- Текст: "Получи свой {бонус/скин/выигрыш} сейчас"
- Музыка: тихая, на фоне, не перебивает голос

ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ:
- 9:16 (1080x1920), 30fps, MP4, H.264
- Субтитры ОБЯЗАТЕЛЬНЫ (80% смотрят без звука)
- Шрифт: Montserrat / Roboto / Inter Bold, размер 60-80px
- Цвета текста: Белый (#FFFFFF) + чёрный контур (stroke 3px)
- Безопасные зоны: не ставить текст вверху (UI ТикТока) и внизу (описание/кнопки)

ОШИБКИ НОВИЧКОВ:
- Текст мелкий / серый / без контура — не читается
- Хук на 3-5 секунде — уже 늦но, ушли
- Длинные вступления "Привет, меня зовут..." — удали
- Музыка громче голоса — раздражает
- Нет CTA или неясный ("пиши в лс" — мало кто напишет)"""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'creatives', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'visual-structure'}), 1, 'internal-creatives', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:creatives', 'internal-audit', 'arbitrage', 'visual', 'structure', 'checklist']), 9))
print(f'Tokens: {tokens}, Inserted 3/5')
db.commit()

# 4/5: A/B тестирование креативов
print('=== CREATIVES: запись 4/5 ===')
prompt = """ЧЕК-ЛИСТ: A/B тестирование креативов — как находить विनеры и убивать лузеры.

ПРИНЦИП: Один тест = одна переменная. Всё остальное одинаковое.

ЧТО ТЕСТИРУЕМ (в порядке приоритета):
1. ХУК (первые 1.5с) — 80% результата
   - Текст хука (3-5 вариантов)
   - Визуал хука (движение vs статика, лицо vs экран)
   - Звук хука (тренд vs голос vs тишина)
2. CTA (последние 3с) — 15% результата
   - Текст: "Ссылка в профиле" vs "Комментарий закрепил" vs "Название в био"
   - Визуал: палец vs стрелка vs стикер
3. СТРУКТУРА СЕРЕДИНЫ — 5% результата
   - Скорость повествования
   - Количество шагов (2 vs 3 vs 4)
   - Наличие/отсутствие доказательства
4. МУЗЫКА/ЗВУК
   - Трендовый vs свой голос vs без музыки
5. ФОРМАТ
   - UGC (рука+телефон) vs Screen-record vs Анимация vs AI-аватар

МЕТРИКИ ДЛЯ РЕШЕНИЯ (минимум 1000 показов на вариант):
- Hook Rate (3-sec view / Impressions) > 25% — хук работает
- Hold Rate (Average watch time / Duration) > 30% — удерживает
- CTR (Clicks / Impressions) > 1.5% — кликают
- CPA (Spend / Conversions) < Target — прибыльно

ПРОТОКОЛ ТЕСТА (TikTok Ads / FB Ads):
День 1-2: Запуск 5 креативов в одной Ad Group (Budget $20/день, Cost Cap)
День 3: Выключаем креативы с CPA > Target * 1.5 или Hook Rate < 15%
День 4: Добавляем 2-3 новых варианта хука для лучшего креатива
День 5-7: Масштабируем विनнера (Budget x2), тестируем новые CTA
Неделя 2: Lookalike 1% от конвертировавшихся + новые креативы

ТАБЛИЦА РЕШЕНИЙ:
| Метрика | Действие |
|---------|----------|
| Hook Rate > 30%, CPA < Target | SCALE (бюджет x2-x3) |
| Hook Rate 20-30%, CPA ~ Target | OPTIMIZE (новые хуки/CTA) |
| Hook Rate < 20% ИЛИ CPA > Target*2 | KILL (выключить) |
| Hook Rate > 25%, но CPA > Target | Проблема в лендинге/оффере, не в креативе |

АВТОМАТИЗАЦИЯ (Keitaro / RedTrack / TikTok Automated Rules):
- Правило: IF CPA > Target * 1.5 AND Spend > $20 -> PAUSE
- Правило: IF Hook Rate > 30% AND Spend > $50 -> INCREASE BUDGET 20%
- Правило: IF CTR < 0.5% AND Impressions > 5000 -> PAUSE

ЧЕК-ЛИСТ ПЕРЕД ЗАПУСКОМ ТЕСТА:
- [ ] 5 креативов, отличающихся ТОЛЬКО хуком
- [ ] Один лендинг, один оффер, одна GEO
- [ ] Бюджет $20/день на Ad Group
- [ ] Пиксель/Постбэк настроен и тестирован
- [ ] Таблица для логирования результатов (дата, креатив, метрики, решение)"""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'creatives', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'ab-testing'}), 1, 'internal-creatives', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:creatives', 'internal-audit', 'arbitrage', 'ab-testing', 'optimization', 'metrics']), 9))
print(f'Tokens: {tokens}, Inserted 4/5')
db.commit()

# 5/5: Сравнение и чек-лист готовности
print('=== CREATIVES: запись 5/5 ===')
prompt = """ЧЕК-ЛИСТ ГОТОВНОСТИ КРЕАТИВА К ЗАПУСКУ (проходи перед каждой загрузкой):

СТРУКТУРА:
[ ] Хук в первые 1.5с (движение + текст + звук)
[ ] Проблема/боль показана чётко (3-5с)
[ ] Решение показано пошагово (макс 3 шага, 5-15с)
[ ] Доказательство РЕАЛЬНОЕ (скрин банка/профиля/весов) (15-25с)
[ ] CTA чёткий, визуальный, понятный (25-30с)

ТЕХНИЧЕСКОЕ:
[ ] 9:16, 1080x1920, 30fps, MP4, <500MB
[ ] Субтитры: крупно, белый+чёрный контур, по центру, без ошибок
[ ] Музыка 10-15% громкости, не перебивает голос
[ ] Безопасные зоны: текст не в верху (UI), не внизу (описание)
[ ] Водяной знак/лого (опционально)

ПСИХОЛОГИЯ:
[ ] Триггер: боль / страх / любопытство / жадность / социальное доказательство
[ ] Конкретика: цифры, сроки, имена, суммы (не "много", а "$500"; не "быстро", а "за 2 минуты")
[ ] Авторитет: "Я проверил" / "Мой друг" / "Эксперты подтверждают" / "Скриншот"
[ ] Срочность: "Осталось 10 минут" / "Только сегодня" / "50 мест" (если честно)
[ ] Простота: "3 шага" / "За 30 секунд" / "Одна кнопка"

МОЯ ФОРМУЛА ВЫБОРА ДЛЯ СТАРТА:
Content-Locking-CPA (Game Hacks) -> Формула 1 (PAS) + Формула 3 (Social Proof) + Формула 5 (UGC)
Sweepstakes -> Формула 2 (Cliffhanger) + Формула 3 (Social Proof)
Nutra -> Формула 1 (PAS) + Формула 3 (Social Proof) + Формула 4 (Negative Marketing)
App Installs -> Формула 5 (UGC) + Формула 3 (Social Proof)

ПРИОРИТЕТ: Не делай "крутые" креативы. Делай КОНВЕРТЯЩИЕ. Красота = ноль денег. Конверсия = деньги."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'creatives', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'readiness-checklist'}), 1, 'internal-creatives', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:creatives', 'internal-audit', 'arbitrage', 'checklist', 'readiness', 'decision']), 10))
print(f'Tokens: {tokens}, Inserted 5/5')
db.commit()
print('CREATIVES: 5/5 DONE')