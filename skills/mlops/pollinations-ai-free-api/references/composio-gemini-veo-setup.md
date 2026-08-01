# Composio + Gemini Veo — Setup & Usage

## Что это

Composio предоставляет Gemini toolkit с **No Auth** — не нужен API ключ Gemini.
Composio сам проксирует запросы к Gemini API через свой backend.

**Доступно:** Veo 3 video generation, Nano Banana image gen, Gemini Flash text, embeddings.

## API Key (создание)

1. Зайти на `https://dashboard.composio.dev/{workspace}/{project}/settings/api-keys`
2. Нажать "Create API Key"
3. Дать имя (например, `hermes-agent-key`)
4. **Обязательно включить:** `tools:read` + `tools:write` (остальные по желанию)
5. Скопировать ключ (показывается один раз)
6. Положить в `.env`:
   ```
   COMPOSIO_API_KEY=ak_...
   ```

## Проверка работоспособности

```python
import os
os.environ["COMPOSIO_API_KEY"] = "ak_..."

from composio import Composio
c = Composio()

# Создать сессию
session = c.create(user_id="hermes-test")
print(f"Session: {session.session_id}")

# Получить Gemini инструменты
tools = c.tools.get(user_id="hermes-test", search="gemini")
for t in tools:
    print(f"  {t.name}: {t.display_name}")
```

## Gemini Actions (через Composio)

| Action | Эндпоинт | Описание |
|--------|----------|----------|
| `GEMINI_GENERATE_VIDEOS` | Veo 3 | Генерация видео из текста (30-180+ сек) |
| `GEMINI_WAIT_FOR_VIDEO` | Veo 3 | Ожидание готовности видео |
| `GEMINI_GET_VIDEOS_OPERATION` | Veo 3 | Проверка статуса операции |
| `GEMINI_GENERATE_IMAGE` | Nano Banana | Изображения (gemini-2.5-flash-image, gemini-3-pro-image-preview) |
| `GEMINI_GENERATE_CONTENT` | Gemini Flash/Pro | Текст, TTS аудио |
| `GEMINI_COUNT_TOKENS` | - | Подсчёт токенов |
| `GEMINI_EMBED_CONTENT` | - | Текстовые эмбеддинги |

## Примечания

- **Gemini - No Auth** — Composio предоставляет свой API ключ Gemini
- **Rate limit:** Concurrent usage may trigger HTTP 429 — keep concurrency ≤3, use exponential backoff
- **Veo видео:** возвращает `operation_name`, нужно передать в `GEMINI_WAIT_FOR_VIDEO`
- **Nano Banana:** поддерживает до 14 reference images, 4K resolution
