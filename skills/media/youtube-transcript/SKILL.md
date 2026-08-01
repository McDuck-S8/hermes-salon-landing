---
name: youtube-transcript
description: Извлечение транскриптов YouTube через youtube-transcript-api — автоматизация YouTube→текст→AI→Telegram
category: media
tags: [youtube, transcript, api, media, ai, telegram, pipeline]
---

# YouTube Transcript API — Извлечение транскриптов

## Что это

`youtube-transcript-api` — Python-библиотека для извлечения субтитров/транскриптов из YouTube-видео без авторизации и API-ключа. Работает с авто-сгенерированными и ручными субтитрами на любом языке.

## Возможности

- **Бесплатно** — не нужен YouTube API ключ
- **Автосубтитры** — извлекает автоматически сгенерированные субтитры (все языки)
- **Ручные субтитры** — поддержка официальных субтитров создателей
- **Прокси** — поддержка прокси для обхода ограничений
- **Пакетная обработка** — извлечение транскриптов из плейлиста

## Пайплайн: YouTube → Текст → AI → Telegram

Классический сценарий автоматизации:

1. **YouTube** — получаем URL видео или список видео из плейлиста
2. **Транскрипт** — извлекаем текст субтитров через `youtube-transcript-api`
3. **AI** — отправляем транскрипт в LLM для суммаризации / анализа / перевода
4. **Telegram** — публикуем результат в канал или отправляем пользователю

### Пример пайплайна

```python
from youtube_transcript_api import YouTubeTranscriptApi

# 1. Извлечение транскрипта (API v1.x — instance + fetch)
api = YouTubeTranscriptApi()
transcript = api.fetch("VIDEO_ID")
text = " ".join([snippet.text for snippet in transcript])

# 2. Отправка в AI для суммаризации
summary = llm.summarize(text)

# 3. Публикация в Telegram
bot.send_message(chat_id, f"📝 Резюме видео:\n\n{summary}")
```

## API Change (2026-06-25)
The `youtube-transcript-api` library has changed. `get_transcript()` no longer exists.
Use `api.fetch(video_id)` instead. The new API returns snippet objects with `.text` attribute.

```python
# OLD (broken):
transcript = YouTubeTranscriptApi.get_transcript("VIDEO_ID")

# NEW (working):
api = YouTubeTranscriptApi()
transcript = api.fetch("VIDEO_ID")
text = " ".join([snippet.text for snippet in transcript])
```

## Установка

```bash
pip install youtube-transcript-api
```

### Проверка

```python
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
print(api.fetch("dQw4w9WgXcQ")[:3])
```

## Код из 3 строк

Самый простой способ получить транскрипт:

```python
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
transcript = api.fetch("VIDEO_ID")
text = " ".join([snippet.text for snippet in transcript])
```

## Примеры использования

### 1. Суммаризация видео

```python
from youtube_transcript_api import YouTubeTranscriptApi

def summarize_youtube(video_id, llm):
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)
    text = " ".join([snippet.text for snippet in transcript])
    return llm.summarize(f"Краткое содержание видео:\n{text}")
```

### 2. Перевод транскрипта

```python
def translate_transcript(video_id, target_lang="ru"):
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)
    text = " ".join([snippet.text for snippet in transcript])
    return llm.translate(text, target_lang)
```

### 3. Пакетная обработка плейлиста

```python
from youtube_transcript_api import YouTubeTranscriptApi

def process_playlist(video_ids, llm, bot, chat_id):
    api = YouTubeTranscriptApi()
    for vid in video_ids:
        try:
            transcript = api.fetch(vid)
            text = " ".join([snippet.text for snippet in transcript])
            summary = llm.summarize(text)
            bot.send_message(chat_id, f"🎬 {vid}:\n{summary}")
        except Exception as e:
            print(f"Ошибка для {vid}: {e}")
```

## Работа с прокси

### Зачем нужен прокси

YouTube может блокировать запросы с серверных IP. Прокси помогает обойти ограничения.

### Настройка прокси

```python
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

# Через Webshare proxy
proxy_config = WebshareProxyConfig(
    proxy_url="http://user:pass@proxy.example.com:8080"
)
api = YouTubeTranscriptApi(proxy_config=proxy_config)
transcript = api.fetch("VIDEO_ID")
```

### Через通用 прокси

```python
import requests

proxies = {
    "http": "http://user:pass@proxy.example.com:8080",
    "https": "http://user:pass@proxy.example.com:8080"
}

# youtube-transcript-api поддерживает прокси через конфиг
```

### Рекомендации по прокси

- **Бесплатные прокси** — ненадёжные, могут быть заблокированы
- **Платные прокси** — Webshare, Bright Data, SmartProxy
- **Ротация IP** — используйте прокси с ротацией для пакетной обработки
- **Лимиты** — ~100-200 запросов в час без прокси; с прокси — больше

## Питфоллы

1. **Нет транскрипта** — не все видео имеют субтитры; проверяйте `TranscriptNotFound`
2. **Язык** — по умолчанию ищет на указанном языке; попробуйте `languages=["ru", "en"]`
3. **Длинные видео** — транскрипт может быть очень большим; обрезайте или разбивайте
4. **rate limit** — YouTube может временно блокировать; используйте прокси и задержки
5. **Специальные символы** — авто-субтитры могут содержать ошибки; нормализуйте текст
6. **Блокировка** — при частых запросах YouTube вернёт 429; используйте прокси
7. **SSL blocking (Crimea/RU)** — `youtube-transcript-api` may fail with `SSLEOFError` or `SSL_ERROR_SYSCALL` from restricted regions. The library connects directly to youtube.com which may be blocked. **Workaround**: use `noembed.com` for video metadata (title, author, thumbnail) without SSL issues:
   ```bash
   curl -s "https://noembed.com/embed?url=https://www.youtube.com/watch?v=VIDEO_ID"
   ```
   For full transcript, route through a proxy (see pitfall #4 above).
   **Alternative fallback**: `web_search()` with `site:youtube.com "VIDEO_ID"` — google often returns the video's description and linked resources even when direct access fails.

8. **ASR-дубли** — автосубтитры YouTube часто содержат тройное повторение каждого сегмента (слово-фраза-предложение). Используйте `python scripts/clean_vtt.py` — он включает дедупликацию.

9. **Правило I violation** — получить транскрипт, сохранить и отчитаться — НЕ артефакт. Ты обязан: извлечь знание → применить → создать работающий результат. Без этого Кольцо разорвано.

10. **RequestBlocked (Innertube API ban)** — при частых запросах YouTube блокирует Innertube API даже через прокси. Симптом: `youtube-transcript-api` возвращает `RequestBlocked`, yt-dlp требует `Sign in to confirm you are not a bot`. **Решение**: переключиться на Шаг 1.5 (ytInitialData HTML parsing) — скачать страницу через curl и вытащить `attributedDescription`. Прокси-IP может быть забанен на Innertube, но HTML-страницы всё ещё доступны. Если нужен полноценный транскрипт — попросить пользователя скачать вручную через интерфейс YouTube.

## ⚠ Правило I (Information) — обязательное звено Кольца

**Информация пришла → обработана → ценное извлечено → применено → артефакт создан.**

Это правило встроено в Кольцо (E→3→0→E):

```
Информация (I) → Обработка (3) → Артефакт (0) → новое Событие (E)
     ↑              ↑               ↑
     I              3               0
```

**Если нарушено Правило I:**
- Инфа пришла, но не обработана → Действия нет → Правило 3 нарушено
- Ценное не извлечено → Артефакта нет → Правило 0 нарушено
- События нет → Правило E нарушено → **Кольцо разорвано**

**Что конкретно значит "артефакт":**
- Не текст-отчёт. Не "я сохранил". Не список того что сделал.
- Работающий измеримый результат: benchmark, граф, схема, скрипт, интеграция.
- Если ты получил ссылки — ты обязан: извлечь → превратить в действие → показать артефакт.

## Полный пайплайн URL → Артефакт (соблюдает Правило I)

Вместо того чтобы просто сохранить транскрипт и отчитаться:

```
1. Получить URL (от пользователя или из events.db)
2. Извлечь транскрипт (yt-dlp через прокси)
3. Очистить VTT → чистый текст (удалить тайм-коды, ASR-дубли, HTML-теги)
4. Прочитать текст, извлечь схемы/паттерны/цифры/инструменты
5. Сохранить извлечённое в Knowledge Cube как knowledge_added с тегами scheme:/pattern:/tool:
6. СОЗДАТЬ АРТЕФАКТ: применить извлечённое (запустить инструмент, построить граф, написать скрипт)
7. Показать пользователю артефакт и его метрики, а не список "я сохранил"
```

**Критерий успеха:** После твоего ответа пользователь может взять артефакт и ИСПОЛЬЗОВАТЬ его. Не читать. Использовать.

## Полный fallback workflow (когда транскрипт недоступен)

Когда прямой транскрипт не работает (SSL, geo-block, network timeout), используйте этот проверенный путь. **Попробуйте в порядке приоритета:**

### Шаг 0: Обнаружить работающий прокси (Windows/v2rayN) — ОБЯЗАТЕЛЬНО

**Это не опция. Это первый шаг. Не начинай сетевую работу пока не проверишь.**

Пользователь использует v2rayN на Windows. Прокси может быть активен, но env-переменные не выставлены. Сканируй порты:

```bash
# 1. Проверить жив ли v2rayN
tasklist /FI "IMAGENAME eq v2rayN.exe" 2>/dev/null

# 2. Сканировать порты (v2rayN часто на 10806)
for port in 10806 10808 10809 1080 1081; do
  curl -s --connect-timeout 2 -x http://127.0.0.1:$port \
    https://www.google.com -o /dev/null -w "$port=%{http_code}\n"
done

# 3. Если порт найден — используй для всего
PROXY="http://127.0.0.1:10806"
curl -s --proxy $PROXY "https://www.youtube.com/watch?v=VIDEO_ID" | head -1
```

**Проверено:** v2rayN на 127.0.0.1:10806 (HTTP+SOCKS5) — YouTube, GitHub, всё работает.
**Ошибка:** не проверить прокси → youtube-transcript-api падает с SSLEOFError → тратишь время на fallback'и.

### Шаг 1: yt-dlp через прокси (САМЫЙ НАДЁЖНЫЙ)

Когда `youtube-transcript-api` падает с SSL/TLS ошибкой — переключайтесь на `yt-dlp` через найденный прокси:

```bash
# Установка
pip install yt-dlp

# Базовый вызов (автосубтитры, все языки)
yt-dlp --proxy http://127.0.0.1:<PORT> \
  --write-auto-subs --sub-lang "ru,en" \
  --skip-download -o "%(id)s" \
  "https://www.youtube.com/watch?v=VIDEO_ID"

# Очистка VTT → чистый текст
python -c "
import re
raw = open('VIDEO_ID.en.vtt').read()
lines = raw.split('\n')
clean = []
for line in lines:
    line = line.strip()
    if not line or line.startswith('WEBVTT') or line.startswith('Kind:') or \
       line.startswith('Language:') or '-->' in line or line.startswith('NOTE') or \
       re.match(r'^\d+$', line):
        continue
    line = re.sub(r'<[^>]+>', '', line)
    clean.append(line)
text = re.sub(r'\s+', ' ', ' '.join(clean)).strip()
open('VIDEO_ID.txt', 'w').write(text)
print(f'{len(text)} chars')
"
```

**Плюсы yt-dlp:**
- Работает через HTTP и SOCKS5 прокси
- Автоматически выбирает лучший язык субтитров (ru > en)
- Справляется с JS-челленджами
- Пакетная загрузка без API-ключа

**Ограничения:**
- Не все видео имеют автосубтитры (проверяйте с `--sub-lang "ru,en,de,fr,es"`)
- 429 при слишком частых запросах — добавляйте `sleep 2` между видео
- Некоторые видео могут быть недоступны "This video is not available"

### Шаг 1.5: ytInitialData HTML parsing (когда всё остальное заблокировано)

Когда YouTube блокирует Innertube API (RequestBlocked), yt-dlp и youtube-transcript-api перестают работать, и web_extract тоже падает. **Но скачать HTML-страницу видео через `curl` и вытащить описание из `ytInitialData.attributedDescription` — почти всегда работает.**

Эта техника даёт полное описание видео: таймкоды, ссылки на репозитории, список инструментов. Не транскрипт, но достаточно для извлечения actionable-знания.

```bash
# Использование встроенного скрипта
python skills/media/youtube-transcript/scripts/yt_extract_desc.py \
  VIDEO_ID http://127.0.0.1:10806

# Пример:
# python skills/media/youtube-transcript/scripts/yt_extract_desc.py \
#   lsj9T5y5OP0 http://127.0.0.1:10806
```

**Что возвращает:** Полный текст описания видео от автора — таймкоды, ссылки, GitHub-репозитории, промокоды, список инструментов.

**Плюсы:**
- Работает даже когда API забанен (RequestBlocked)
- Не требует YouTube API ключа
- Не зависит от Python-библиотек (только curl + sys)
- Никаких rate limits (YouTube не блокирует просмотр страниц)

**Ограничения:**
- Только описание, не транскрипт (нет текста речи)
- Некоторые видео имеют обрезанное описание
- Требует curl (есть на Windows/MSYS по умолчанию)

**Встроенный скрипт:** `scripts/yt_extract_desc.py` — извлекает attributedDescription из ytInitialData. Автоматически ретраит при SSL-ошибках (exit 35, intermittent через прокси).

### Валидация (2026-07-29): ytInitialData parsing — РАБОЧИЙ ФОЛБЭК

Сессионно проверено: когда YouTube блокирует Innertube API (RequestBlocked), yt-dlp и youtube-transcript-api падают, `web_extract` тоже падает. **Парсинг `ytInitialData.attributedDescription` через curl + regex — работает стабильно.**

**Что извлекается:** Полное описание видео от автора — таймкоды, ссылки на репозитории, промокоды, список инструментов. Не транскрипт, но достаточно для actionable-знания.

**Команда:**
```bash
python skills/media/youtube-transcript/scripts/yt_extract_desc.py \
  VIDEO_ID http://127.0.0.1:10806
```

**Плюсы подтверждены сессией:**
- Работает когда API забанен (RequestBlocked)
- Не требует YouTube API ключа
- Не зависит от Python-библиотек (curl + sys)
- Никаких rate limits
- v2rayN прокси на 10806 — стабильно работает

### Шаг 0: Обнаружить работающий прокси (Windows/v2rayN) — ОБЯЗАТЕЛЬНО

**Это не опция. Это первый шаг. Не начинай сетевую работу пока не проверишь.**

Пользователь использует v2rayN на Windows. Прокси может быть активен, но env-переменные не выставлены. Сканируй порты:

```bash
# 1. Проверить жив ли v2rayN
tasklist /FI "IMAGENAME eq v2rayN.exe" 2>/dev/null

# 2. Сканировать порты (v2rayN часто на 10806)
for port in 10806 10808 10809 1080 1081; do
  curl -s --connect-timeout 2 -x http://127.0.0.1:$port \
    https://www.google.com -o /dev/null -w "$port=%{http_code}\n"
done

# 3. Если порт найден — используй для всего
PROXY="http://127.0.0.1:10806"
curl -s --proxy $PROXY "https://www.youtube.com/watch?v=VIDEO_ID" | head -1
```

**Проверено:** v2rayN на 127.0.0.1:10806 (HTTP+SOCKS5) — YouTube, GitHub, всё работает.
**Ошибка:** не проверить прокси → youtube-transcript-api падает с SSLEOFError → тратишь время на fallback'и.

### Шаг 1: yt-dlp через прокси (САМЫЙ НАДЁЖНЫЙ)

Когда `youtube-transcript-api` падает с SSL/TLS ошибкой — переключайтесь на `yt-dlp` через найденный прокси:

```bash
# Установка
pip install yt-dlp

# Базовый вызов (автосубтитры, все языки)
yt-dlp --proxy http://127.0.0.1:<PORT> \
  --write-auto-subs --sub-lang "ru,en" \
  --skip-download -o "%(id)s" \
  "https://www.youtube.com/watch?v=VIDEO_ID"

# Очистка VTT → чистый текст
python -c "
import re
raw = open('VIDEO_ID.en.vtt').read()
lines = raw.split('\n')
clean = []
for line in lines:
    line = line.strip()
    if not line or line.startswith('WEBVTT') or line.startswith('Kind:') or \
       line.startswith('Language:') or '-->' in line or line.startswith('NOTE') or \
       re.match(r'^\d+$', line):
        continue
    line = re.sub(r'<[^>]+>', '', line)
    clean.append(line)
text = re.sub(r'\s+', ' ', ' '.join(clean)).strip()
open('VIDEO_ID.txt', 'w').write(text)
print(f'{len(text)} chars')
"
```

**Плюсы yt-dlp:**
- Работает через HTTP и SOCKS5 прокси
- Автоматически выбирает лучший язык субтитров (ru > en)
- Справляется с JS-челленджами
- Пакетная загрузка без API-ключа

**Ограничения:**
- Не все видео имеют автосубтитры (проверяйте с `--sub-lang "ru,en,de,fr,es"`)
- 429 при слишком частых запросах — добавляйте `sleep 2` между видео
- Некоторые видео могут быть недоступны "This video is not available"

### Шаг 1.5: ytInitialData HTML parsing (когда всё остальное заблокировано)

Когда YouTube блокирует Innertube API (RequestBlocked), yt-dlp и youtube-transcript-api перестают работать, и web_extract тоже падает. **Но скачать HTML-страницу видео через `curl` и вытащить описание из `ytInitialData.attributedDescription` — почти всегда работает.**

Эта техника даёт полное описание видео: таймкоды, ссылки на репозитории, список инструментов. Не транскрипт, но достаточно для извлечения actionable-знания.

```bash
# Использование встроенного скрипта
python skills/media/youtube-transcript/scripts/yt_extract_desc.py \
  VIDEO_ID http://127.0.0.1:10806

# Пример:
# python skills/media/youtube-transcript/scripts/yt_extract_desc.py \
#   lsj9T5y5OP0 http://127.0.0.1:10806
```

**Что возвращает:** Полный текст описания видео от автора — таймкоды, ссылки, GitHub-репозитории, промокоды, список инструментов.

**Плюсы:**
- Работает даже когда API забанен (RequestBlocked)
- Не требует YouTube API ключа
- Не зависит от Python-библиотек (только curl + sys)
- Никаких rate limits (YouTube не блокирует просмотр страниц)

**Ограничения:**
- Только описание, не транскрипт (нет текста речи)
- Некоторые видео имеют обрезанное описание
- Требует curl (есть на Windows/MSYS по умолчанию)

**Встроенный скрипт:** `scripts/yt_extract_desc.py` — извлекает attributedDescription из ytInitialData. Автоматически ретраит при SSL-ошибках (exit 35, intermittent через прокси).

### Шаг 2: `web_extract()` на URL видео

```python
result = web_extract(urls=["https://www.youtube.com/watch?v=VIDEO_ID"], char_limit=8000)
page = result["results"][0]
# page["content"] contains full description + transcript + comments
```

`web_extract()` загружает страницу YouTube через провайдера (Firecrawl, Tavily и др.) и возвращает markdown с описанием. Не требует YouTube API ключа.

**ВНИМАНИЕ**: Tavily часто выдаёт ошибку 432. Пробуйте с разными провайдерами:
```python
# Firecrawl работает когда Tavily падает
result = web_extract_plus(urls=[url], provider="firecrawl")
```

### Шаг 3: `noembed.com` для метаданных

Когда всё остальное не работает — хотя бы метаданные:

```bash
curl -s "https://noembed.com/embed?url=https://www.youtube.com/watch?v=VIDEO_ID"
```

Возвращает title, author_name, url, thumbnail. Работает без SSL проблем в любых регионах.

### Шаг 4: Сохранение извлечённого знания (не текста!)

**Критично: не сохраняй сырой транскрипт. Сохраняй ИЗВЛЕЧЁННОЕ ЗНАНИЕ.**

При извлечении "схемы" или "паттерна":
   ```python
   from hermes_hooks import get_hooks
   hooks = get_hooks()
   hooks.on_task_complete("SCHEME: Title", content, ["scheme", "youtube", "extracted"])
   ```
   И прямая вставка в `experiences` с `axis_domain='themes-schemes'`. `content` + `raw_text` обязательны (оба NOT NULL).

### Шаг E: Артефакт — ПРАВИЛО I

**НЕЛЬЗЯ** закончить пайплайн на сохранении транскрипта.

**Правило I (Information) встроено в Кольцо:**
```
Инфа пришла → обработана → ценное извлечено → применено → артефакт
```

**После извлечения транскрипта ты ОБЯЗАН:**
1. Прочитать текст (не просто сохранить)
2. Извлечь схемы/паттерны/цифры/инструменты
3. Сохранить как `knowledge_added` с тегами scheme:/pattern:/tool:
4. **СОЗДАТЬ АРТЕФАКТ** — установить инструмент, запустить benchmark, собрать пайплайн
5. Показать пользователю артефакт с метриками, а не список "я сохранил"

**Критерий успеха:** твой ответ содержит работающий результат, а не отчёт о том что ты делал.

**Типовые нарушения (и их цена):**
- "Я вытащил инфу, сохранил, вот список" → нарушение Правила I → Кольцо разорвано
- "Я посмотрел 15 видео" → не артефакт → нарушение Правила 0
- "Я извлёк схемы" без применения → информация есть, ценности нет

**Как исправить сразу после извлечения:**
```python
from event_evolution import emit_event

# Сохраняй знание, а не текст
emit_event("knowledge_added", {
    "content": "SCHEME: ... (конкретная схема с цифрами, не пересказ видео)",
    "tags": ["scheme", "youtube"],
    "source": "youtube-research"
})

# Сразу создай артефакт: установи tool, запусти benchmark, примени паттерн
```

Для 10+ видео — запускайте через execute_code с паузами между запросами:

```python
import subprocess, time, json
from pathlib import Path

WORK = Path("output_dir")
WORK.mkdir(exist_ok=True)
PROXY = "http://127.0.0.1:10806"

for i, vid in enumerate(VIDEO_IDS):
    print(f"[{i+1}/{len(VIDEO_IDS)}] {vid}")
    r = subprocess.run(
        ["yt-dlp", "--proxy", PROXY,
         "--write-auto-subs", "--sub-lang", "ru,en",
         "--skip-download", "-o", str(WORK / vid),
         f"https://www.youtube.com/watch?v={vid}"],
        capture_output=True, text=True, timeout=60
    )
    # Check all language variants
    for vtt in WORK.glob(f"{vid}.*.vtt"):
        # Clean VTT as above
        pass
    time.sleep(2)  # rate limit protection
```

## Связанные навыки

- `media/youtube-content` — YouTube transcripts → summaries, threads, blogs
- `media/gif-search` — поиск и скачивание GIF
- `mcp/native-mcp` — настройка MCP-серверов в Hermes
- `media/youtube-research` — YouTube video description extraction, link harvesting, source verification, multi-resource research compilation

## Reference: Matt Pocock Pipeline (2026-07-29)

Session: извлечено из видео `bYaw3Nwqzn0` (Никита Велc разбирает пайплайн Matt Pocock для Claude Code).
Содержимое: `references/matt-pocock-pipeline-2026-07-29.md` — Grill Me → To Spec → To Tickets → Implement → Wayfinder.
Прямое соответствие Hermes workflow: brainstorming → writing-plans → beads → subagent-driven-development.
