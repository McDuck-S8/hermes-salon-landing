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

# CONTENT-PRODUCTION: 5 записей
print('=== CONTENT-PRODUCTION: запись 1/5 ===')
prompt = """ТОП-5 способов производства контента для Shorts/Reels/TikTok в 2025-2026 с конкретными инструментами и затратами.

1. AI FULL AUTO (HeyGen / Synthesia / InVideo AI / Pictory):
   - Вход: тема/скрипт -> выход: готовое видео с аватаром/стоком/войсом
   - HeyGen: $24/мес (15 мин) -> $99/мес (60 мин) — лучшие аватары, lip-sync
   - Synthesia: $22/мес (10 мин) — корпоративный стиль, 140+ аватаров
   - InVideo AI: $20/мес (50 мин) — промпт -> видео, стоковые кадры, голос
   - Pictory: $19/мес (30 мин) — статья/скрипт -> видео, субтитры авто
   - Затраты: $20-100/мес, время: 5-15 мин/видео, качество: среднее-высокое
   - Риск: "AI view" детекция (шэдоубан), одинаковые аватары у всех

2. AI ASSISTED (CapCut + ChatGPT + ElevenLabs + Pexels/Pixabay):
   - ЧатGPT: скрипт/хуки/заголовки ($20/мес Plus)
   - ElevenLabs: $5/мес (30к символов) — лучшие AI голоса, клонирование
   - CapCut (Desktop/Mobile): бесплатно — монтаж, субтитры авто, эффекты, музыка
   - Сток: Pexels, Pixabay, Mixkit — бесплатные видео/фото/музыка
   - Затраты: $25/мес, время: 20-40 мин/видео, качество: высокое (ручной контроль)

3. UGC СТИЛЬ (телефон + рука + натуральный свет):
   - Пишешь скрипт -> снимаешь сам / просишь друга -> монтируешь в CapCut
   - Затраты: $0 (телефон), время: 30-60 мин/видео
   - Плюсы: максимальное доверие, алгоритмы любят "живой" контент
   - Минусы: не масштабируется, нужен "лицо" или актёр

4. REPURPOSING (OpusClip / Vidyo.ai / 2short.ai):
   - Вход: длинное видео (YouTube, вебинар, подкаст) -> 10-20 Shorts
   - OpusClip: $19/мес (200 мин) — AI ищет виральные моменты, рефрейм, субтитры
   - Vidyo.ai: $21/мес — похоже, есть шаблоны
   - 2short.ai: $10/мес — дешевле, проще
   - Затраты: $10-20/мес, время: 5 мин/пакет, масштаб: огромный

5. АУТСОРС (Fiverr / Upwork / Telegram чаты редакторы):
   - Fiverr: $10-50 за Shorts (зависит от сложности)
   - Upwork: $5-15/час редакторы из Philippines/India/Pakistan
   - ТГ чаты: @videoredactors, @content_makers — $5-20 за штуку
   - ТЗ: скрипт + референсы + брендбук (шрифты, цвета, лого)
   - Затраты: $100-500/мес за 20-50 видео, время твоего контроля: 10 мин/день

МОЙ ВЫБОР ДЛЯ СТАРТА ($0-50/мес):
Неделя 1-2: CapCut + ChatGPT + ElevenLabs + Pexels (ручной контроль, уникальность)
Неделя 3-4: + OpusClip (репупсинг longs -> shorts для объёма)
Месяц 2+: Аутсорс (Fiverr/ТГ) для 20+ видео/день, ты — только ТЗ и контроль."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'content-production', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'top-methods'}), 1, 'internal-content-production', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:content-production', 'internal-audit', 'arbitrage', 'heygen', 'capcut', 'opusclip', 'elevenlabs']), 10))
print(f'Tokens: {tokens}, Inserted 1/5')
db.commit()

# 2/5: CapCut workflow
print('=== CONTENT-PRODUCTION: запись 2/5 ===')
prompt = """ЧЕК-ЛИСТ: Производство Shorts в CapCut (Desktop) + ChatGPT + ElevenLabs — полный конвейер за 20 мин/видео.

ПОДГОТОВКА (один раз):
1. CapCut Desktop: скачай, установи, войди (бесплатно)
2. ChatGPT Plus ($20/мес): промпт для скриптов (сохрани как Custom GPT)
3. ElevenLabs: регистрация, $5/мес (Starter), создай Voice -> клонируй свой или выбери "Conversational"
4. Pexels/Pixabay: закладки для стока
5. Папка проекта: /Content/ProjectName/{Scripts,Voice,Stock,Project,Export}

КОНВЕЙЕР (20 мин/видео):
МИНУТЫ 0-5: СКРИПТ (ChatGPT)
- Промпт: "Напиши скрипт для TikTok 30 сек: хук (боль/интрига) -> проблема -> решение (оффер) -> CTA. Тема: {ниша}. Тон: энергичный, экспертный. Вывод: таблица: Сцена | Текст на экране | Глагол | Визуал | Длительность"
- Сохраняй в /Scripts/{date}_topic.txt

МИНУТЫ 5-10: ВОЙС (ElevenLabs)
- Вставляешь скрипт (колонка "Глагол") -> Generate -> Download MP3 -> /Voice/{date}_topic.mp3
- Настройки: Stability 0.5, Similarity 0.75, Style 0.3

МИНУТЫ 10-15: СТОК (Pexels/Pixabay)
- Поиск по ключевым словам из колонки "Визуал" -> качаешь 5-10 клипов -> /Stock/

МИНУТЫ 15-20: МОНТАЖ (CapCut)
1. Новый проект 9:16 -> импорт Voice + Stock
2. Расставляешь клипы по таймингу из скрипта
3. Текст -> Авто-субтитры -> стиль: крупный, контрастный, по центру, анимация "появление по словам"
4. Музыка: CapCut библиотека (Commercial) -> громкость 10-15%
5. Эффекты: Zoom в хуке, Blur переходы, Sticker (стрелка/кружок) на CTA
6. Экспорт: 1080p, 30fps, H.264, High Quality -> /Export/{date}_topic.mp4

ЧЕК-ЛИСТ ПЕРЕД ПУБЛИКАЦИЕЙ:
- [ ] Хук в первые 1.5 сек (движение/звук/вопрос)
- [ ] Субтитры читаются (контраст, размер, нет ошибок)
- [ ] CTA чёткий: "Ссылка в профиле" / "Комментарию пишу" / "Профиль -> Link in bio"
- [ ] Музыка не перебивает голос
- [ ] Водяной знак/лого (опционально, для бренда)
- [ ] Файл < 500MB (ТикТок лимит)"""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'content-production', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'capcut-workflow'}), 1, 'internal-content-production', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:content-production', 'internal-audit', 'arbitrage', 'capcut', 'workflow', 'checklist']), 9))
print(f'Tokens: {tokens}, Inserted 2/5')
db.commit()

# 3/5: Репупсинг
print('=== CONTENT-PRODUCTION: запись 3/5 ===')
prompt = """ЧЕК-ЛИСТ: Репупсинг Long-form -> Shorts через OpusClip — масштаб 1 длинное = 15 Shorts за 5 мин.

КАК РАБОТАЕТ:
1. Заливаешь YouTube ссылку / загружаешь MP4 (подкаст, вебинар, обзор, интервью >10 мин)
2. OpusClip AI анализирует: речь, эмоции, ключевые моменты, виральность
3. Выдаёт 10-20 клипов 30-60 сек с рейтингом "Viral Score" (0-100)
4. Авто-рефрейм: вертикальный кроп по лицу/действию
5. Авто-субтитры: динамические, по словам, эмодзи, подсветка ключевых слов
6. Экспорт: пакет MP4 или прямо в TikTok/Reels/Shorts (с планировщиком)

НАСТРОЙКА (один раз):
- Brand Kit: лого, цвета, шрифт, аутро (твой CTA) -> применяется ко всем клипам
- Templates: выбери 2-3 стиля (минималистичный / энергичный / экспертный)
- Language: Russian / English / Auto
- Min/Max duration: 15-60 сек

WORKFLOW (еженедельно):
Понедельник: записываешь 1 Long (30-60 мин) — обзор оффера / кейс / обучение
Вторник: OpusClip -> получаешь 15 Shorts -> выбираешь топ-5 по Viral Score > 70
Среда-Пятница: публикуешь по 1-2 в день (TikTok + Reels + Shorts одновременно)
Выходные: анализ метрик -> лучшие моменты -> идеи для след. Long

МЕТРИКИ УСПЕХА:
- Viral Score > 70 = публикуем
- Views/Impressions > 10% = хороший хук
- Watch time > 50% = удерживает
- Shares/Saves > 1% = вирально

РИСКИ И РЕШЕНИЯ:
- Одинаковые клипы у конкурентов (один и тот же подкаст) -> ТВОЙ Long = уникальный контент
- AI рефрейм обрезает лицо -> ручной поправка в CapCut (1 мин/клип)
- Субтитры с ошибками -> правка в OpusClip перед экспортом (клик на слово -> исправь)

СТОИМОСТЬ: OpusClip Pro $19/мес (200 мин обработки) = ~40 Long в месяц = 600 Shorts = 20 Shorts/день."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'content-production', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'repurposing'}), 1, 'internal-content-production', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:content-production', 'internal-audit', 'arbitrage', 'opusclip', 'repurposing', 'workflow']), 9))
print(f'Tokens: {tokens}, Inserted 3/5')
db.commit()

# 4/5: Аутсорс
print('=== CONTENT-PRODUCTION: запись 4/5 ===')
prompt = """ЧЕК-ЛИСТ: Аутсорс контента на Fiverr / Upwork / Telegram — 20+ видео/день под ТЗ.

ПЛАТФОРМЫ И ЦЕНЫ (2025):
1. Fiverr: поиск "TikTok Shorts editor" / "Reels editor"
   - Уровень 1 (новички): $5-10 за Shorts, нужны 3-5 правок
   - Уровень 2 (Pro): $15-30 за Shorts, 1-2 правки, понимают маркетинг
   - Уровень 3 (Top Rated): $30-50, 턴ки, свои идеи, брендбук
2. Upwork: Hourly $5-15/час (Philippines, Pakistan, India, Nigeria)
   - Пост: "Need 20 TikTok Shorts/week, provide script+voice+stock, you edit in CapCut. $100/week. Long-term."
   - Интервью: тестовое 1 видео (оплачиваешь $10) -> оцениваешь скорость/качество/коммуникацию
3. Telegram: @videoredactors, @content_makers, @editors_for_hire, @freelance_video
   - Пишешь: "Ищу редактора Shorts, 20 в неделю, $150/неделю, даю скрипт+войс+сток, нужен CapCut проект + MP4. Портфолио в лс."
   - Быстрее, дешевле, но риск пропадания выше -> договор + предоплата 50%

ТЗ (TEMPLATE — копируй и заполняй):
```
ПРОЕКТ: {Название схемы}
НИША: {Game Hacks / Nutra / Sweeps}
ЦЕЛЬ: Клик на ссылку в профиле / комментарий
БРЕНДБУК: Цвета (#HEX), Шрифты (ссылка на Google Fonts), Лого (файл), Стиль (минимум/энергия/эксперт)
СКРИПТЫ: Google Docs ссылка (колонки: Сцена, Текст, Глагол, Визуал, Длительность)
ВОЙС: ElevenLabs ссылка на MP3 (или "сделай сам из скрипта")
СТОК: Ключевые слова для Pexels/Pixabay на каждую сцену
ТЕХНИЧЕСКОЕ: 9:16, 1080x1920, 30fps, MP4, H.264, <500MB, субтитры ОБЯЗАТЕЛЬНЫ (стиль: крупный, белый+чёрный контур, по центру)
МУЗЫКА: CapCut Commercial Library, громкость 10%
CTA ВИЗУАЛЬНЫЙ: Стикер "Ссылка в профиле" / Анимация пальца вниз
ДЕДЛАЙН: {дата} 18:00 МСК
ОПЛАТА: {сумма} за {кол-во} видео, карта/USDT/USDC, после приёмки
```

КАЧЕСТВО КОНТРОЛЯ (QC):
1. Авто-проверка: файл <500MB, 9:16, 30fps, субтитры есть
2. Ручная: смотришь на 2x скорость — хук, CTA, читаемость, синк голос/видео
3. Метрика: публикуешь тестовые 3-5 -> если CTR > 1% и Hold > 3с -> берёшь на постоянку

ОПЛАТА И ДОКУМЕНТЫ:
- Самозанятый: чек в "Мой налог" (4%) — проси отправлять сразу после оплаты
- Договор ГПХ (шаблон в Нетологии/Яндекс.Практикуме) — для защиты
- НДС не нужен (самозанятые)"""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'content-production', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'outsourcing'}), 1, 'internal-content-production', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:content-production', 'internal-audit', 'arbitrage', 'outsourcing', 'fiverr', 'upwork', 'tg']), 9))
print(f'Tokens: {tokens}, Inserted 4/5')
db.commit()

# 5/5: Сравнение и выбор
print('=== CONTENT-PRODUCTION: запись 5/5 ===')
prompt = """СРАВНИТЕЛЬНАЯ ТАБЛИЦА: выбор способа производства контента под этап (2025-2026).

| Критерий | CapCut+ChatGPT+11Labs ($25/мес) | OpusClip ($19/мес) | AI Full Auto (HeyGen $99) | Аутсорс ($300-500/мес) | UGC Сам ($0) |
|----------|-------------------------------|-------------------|--------------------------|----------------------|--------------|
| Затраты/мес | $25 | $19 | $99 | $300-500 | $0 |
| Время твоё/видео | 20 мин | 5 мин (пакет) | 5 мин | 5 мин (ТЗ+QC) | 45 мин |
| Уникальность | Высокая | Зависит от Long | Низкая (общие аватары) | Высокая (разные редакторы) | Максимальная |
| Масштаб | 3-5 в день | 20+ в день | 10-20 в день | 50+ в день | 1-2 в день |
| Качество | Ты контролируешь | AI + твоя правка | Шаблонное | Зависит от ТЗ/редактора | Живое, но непрофессиональное |
| Риск шэдоубана | Низкий | Низкий | Высокий | Низкий | Низкий |
| Лучше для | Старт, тест офферов | Объём из Long | Только если нет времени | Скейл $500+/день | Личный бренд |

МОЯ ДОРОЖНАЯ КАРТА:
$0-50/день: CapCut+ChatGPT+11Labs (ручной контроль, уникальность, обучение)
$50-200/день: + OpusClip (репупсинг 1 Long -> 15 Shorts для объёма)
$200-500/день: Аутсорс Fiverr/Upwork (ты — ТЗ + QC, редакторы — монтаж)
$500+/день: Команда (твой продюсер + 2-3 редактора + скриптер) + свой Long контент

ЧЕК-ЛИСТ ПЕРЕХОДА:
- [ ] Стабильно 5+ видео/день своими руками -> время становится бутылком
- [ ] ROI > 50% 7 дней -> можно инвестировать в аутсорс
- [ ] Есть ТЗ, брендбук, скрипты -> можно делегировать
- [ ] Бюджет $300/мес на контент не бьёт по кассе

ПРИОРИТЕТ: Уникальность и контроль на старте -> Объём через репупсинг -> Делегирование через ТЗ."""

content, tokens = research(prompt)
row_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute('''INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome, dynamic_axes, is_white_spot, white_spot_cluster_id, source, confidence, tags, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(datetime.now().isoformat(), content, content, row_hash, 'content-production', 'success', json.dumps({'topic': 'arbitrage', 'internal_audit': True, 'type': 'comparison'}), 1, 'internal-content-production', 'white-spot-explorer', 0.95, json.dumps(['white-spot-explorer', 'domain:content-production', 'internal-audit', 'arbitrage', 'comparison', 'decision']), 10))
print(f'Tokens: {tokens}, Inserted 5/5')
db.commit()
print('CONTENT-PRODUCTION: 5/5 DONE')