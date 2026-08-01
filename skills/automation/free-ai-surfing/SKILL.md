---
name: free-ai-surfing
version: 1.1.0
description: "Серфинг по бесплатным AI-сайтам: поиск бесплатных генераторов изображений, видео, аудио, а также анализ контента — без API-ключа. Работа через BrowserOS + web_extract."
tags: [free-ai, surfing, browser, no-api-key, image-generation, video-analysis]
---

# Free AI Surfing — бесплатные AI-инструменты без API-ключа

Навык для поиска и использования бесплатных AI-сервисов, не требующих API-ключа или подписки.

## Принцип

Пользователь сказал: *"Ты просишь апикей, но у нас нет чем оплатить... есть сайты на которых это можно делать бесплатно... освой скилл сёрфинга по сайтам и заведи себе почту"*

Значит:
- **НЕ просить API-ключи**
- **НЕ регистрироваться с реальной почтой**
- **Использовать BrowserOS для работы с бесплатными сервисами**
- **Временная почта — temp-mail.org / 10minutemail.net**
- **Composio для авторизации** — если есть, используй для поддержания сессий на сайтах

## Key Insight (2026-07-21): upload + анализ контента через BrowserOS

**Проблема:** vision_analyze возвращает 403. video_generate не работает (xAI нет кредитов). API ключи невалидны.

**Решение:** Использовать BrowserOS для загрузки файлов в бесплатные веб-сервисы.

### Бесплатные сервисы для анализа контента (через BrowserOS)

| Сервис | URL | Что умеет | Лимиты |
|--------|-----|-----------|--------|
| **Gemini** | https://gemini.google.com | Видит видео нативно, описывает кадры | Бесплатно |
| **Claude** | https://claude.ai | Загружает файлы, анализирует | Бесплатный тир |
| **ChatGPT** | https://chat.openai.com | GPT-4o смотрит видео | Free tier |
| **DeepSeek** | https://chat.deepseek.com | Загружает файлы, Instant/Vision mode | Бесплатно |
| **Qwen** | https://chat.qwen.ai | Vision, file upload | Бесплатно |

### Процедура загрузки файла через BrowserOS

1. **Открыть сервис** — `mcp__browseros__new_page(url)`
2. **Дождаться загрузки** — `browser_snapshot()` или `take_snapshot()`
3. **Найти кнопку upload** — по snapshot (ref из квадратных скобок)
4. **Нажать кнопку** — `click(page, element)`
5. **Использовать upload_file** — `upload_file(page, element, files=[абсолютный_путь])`
   - Работает для стандартных `<input type="file">` элементов с нативным onChange
   - НЕ работает для React Synthetic onChange (SPA) — проверять на конкретном сайте
6. **Отправить запрос** — `type()` + `press_key('Enter')`
7. **Дождаться ответа** — через `get_page_content()` или `evaluate_script()`
8. **Извлечь результат** — `get_page_content()` или DOM парсинг

### Если upload_file не работает (React SPA)

Причина: BrowserOS upload_file устанавливает файл в DOM, но React не видит изменения (synthetic events).

**Обход через CDP (BrowserClaw):**
```javascript
const doc = await browser.cdp('DOM.getDocument');
const search = await browser.cdp('DOM.querySelector', {
  nodeId: doc.root.nodeId,
  selector: 'input[type="file"]'
});
await browser.cdp('DOM.setFileInputFiles', {
  nodeId: search.nodeId,
  files: ['/path/to/file.mp4']
});
```

**Либо:** использовать Playwright-based proxy — maresin/deepseek-automation-api (GitHub, ~3.4k⭐)

## Бесплатные генераторы изображений (без API-ключа)

| Сервис | URL | Особенности |
|--------|-----|-------------|
| **Pollinations.ai** | https://image.pollinations.ai/prompt/{text} | GET-based, FLUX модель, rate limit ~1/10s |
| AI Free Forever | https://aifreeforever.com/image-generators | 20+ моделей, Flux 2, Imagen 4, Seedream 5, no signup |
| FreeGen | https://freegen.app | No signup, no limits, быстрый |
| NoteGPT | https://notegpt.io/ai-image-generator | Unlimited, бесплатно |
| Duck.ai | https://duck.ai | DuckDuckGo, анонимно |
| Hugging Face | https://huggingface.co/spaces | FLUX Schnell, SDXL, бесплатные Space'ы |

### Pollinations.ai — генерация реального AI-контента

Используй **вместо** FFmpeg drawtext на пустом фоне (пользователь rejects такое как "фон с надписью").

```python
import urllib.request, urllib.parse, time

prompt = "luxury lifestyle man counting stacks of hundred dollar bills marble table cinematic"
encoded = urllib.parse.quote(prompt)
url = f"https://image.pollinations.ai/prompt/{encoded}?width=720&height=1280&model=flux&nologo=true&seed=42"

req = urllib.request.Request(url, headers={"User-Agent": "Hermes-Agent/1.0"})
with urllib.request.urlopen(req, timeout=60) as resp:
    data = resp.read()  # bytes — JPEG (~77KB for 720×1280)
    with open("cache/ai_frame.jpg", "wb") as f:
        f.write(data)
```

**Rate limit:** ~1 запрос/10 сек. После 2-х подряд — 429. Решение: `time.sleep(10)` и retry.

**Валидность:** работает 2026-07-21, 200 OK, ~77KB на кадр.

## Показ результатов пользователю

**Правило:** если показываешь визуальный контент (видео, картинку, HTML) — открывай в браузере, не просто пиши путь.

```python
# 1. Запустить HTTP сервер (background)
terminal("cd /d/Portable_Soft/hermes && python -m http.server 8765 --bind 127.0.0.1", background=true)

# 2. Открыть в BrowserOS
mcp__browseros__new_page(url=f"http://127.0.0.1:8765/cache/файл.mp4")
```

Не пиши "смотри файл по пути X:\path" — открой browser page и дай пользователю увидеть.

## Бесплатные AI API (с free tier, без карты)

| Сервис | Free tier | API |
|--------|-----------|-----|
| Gemini API | Gemini 2.5 Flash — бесплатно | AI Studio API key |
| OpenRouter | Free models: Qwen, Llama | openrouter.ai |
| Together AI | FLUX schnell free endpoint | together.ai |
| Groq | Llama 3, Mixtral free tier | groq.com |

## Процедура работы с бесплатным сервисом

1. **browser_navigate(URL)** — открыть сайт
2. **browser_vision()** — посмотреть что там (есть ли поле ввода)
3. **browser_type(ref, prompt)** — ввести промпт
4. **browser_click(ref)** — нажать Generate
5. **browser_vision()** — проверить результат
6. **browser_get_images()** — получить URL изображения

Для контентных сайтов без UI:
1. **web_extract(URL)** — получить чистый контент
2. **web_search(query)** — найти лучший сервис
3. **browser** — если нужна интерактивность

## Временная почта

- **temp-mail.org** — сайт, одноразовая почта
- **10minutemail.net** — почта на 10 минут
- Использовать browser: navigate → скопировать адрес → использовать для регистрации

## Pitfalls

- **Бесплатные сервисы меняются** — всегда проверяй что сайт ещё жив (browser_navigate)
- **Лимиты** — даже бесплатные сервисы имеют rate limits. Если не работает — попробуй другой
- **Качество** — бесплатные версии могут давать меньший размер/качество. Используй upscaler (например freegen.app)
- **Временная почта может быть заблокирована** — некоторые сайты не принимают temp-mail. Попробуй 10minutemail
- **Не сохраняй сгенерированное как "готовое"** — покажи пользователю, он решит
- **Не изобретай велосипед** — перед тем как писать кастомное решение, проверь 3+ альтернативы (GitHub, web search, npm/PyPI). Не останавливайся на первом найденном.
- **Если upload_file не сработал — не ретрай 50 раз** — переключись на другой подход (API, другой сервис, CDP escape hatch)
