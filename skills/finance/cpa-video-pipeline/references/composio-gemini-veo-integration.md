# Composio + Gemini/Veo Integration

## Дата
2026-07-21. Сессия: исследование бесплатной AI видео-генерации.

## Контекст
Пользователь требует НАСТОЯЩЕЕ AI-видео (не FFmpeg drawtext подделку).
Проблема: vision_analyze ⛔ 403, xAI video_generate ⛔ платный, DeepSeek upload ⛔ тупик.

## Composio SDK версия
`composio==0.17.1` (установлен в venv `D:\Portable_Soft\hermes\hermes-agent\.venv`)
API key: создан в дашборде `dashboard.composio.dev` → Settings → API Keys

## Архитектура SDK

### Session meta tools (6 штук)
```python
session = c.create(user_id='hermes-agent')
tools = session.tools()  # → 6 meta tools
```
1. `COMPOSIO_SEARCH_TOOLS` — поиск тулкитов по app name
2. `COMPOSIO_MULTI_EXECUTE_TOOL` — параллельный executor
3. `COMPOSIO_MANAGE_CONNECTIONS` — управление подключениями
4. `COMPOSIO_GET_TOOL_SCHEMAS` — получить input schema для tool
5. `COMPOSIO_REMOTE_BASH_TOOL` — удалённый bash
6. `COMPOSIO_REMOTE_WORKBENCH` — удалённый Python

### Методы session
```python
session.execute(tool_slug, arguments={...})  # выполнить meta tool или action
session.search(query='gemini')               # поиск действий
session.proxy_execute(toolkit='gemini', ...)  # прямой прокси
c.use(session_id=sid)                         # переиспользовать session
```

## Полный рабочий код

### Шаг 1: Session + Connection
```python
import os
os.environ['COMPOSIO_API_KEY'] = 'ak_YOUR_KEY'

from composio import Composio
c = Composio()
session = c.create(user_id='hermes-agent')
sid = session.session_id

# Gemini — No Auth, подключается мгновенно
conn = session.execute('COMPOSIO_MANAGE_CONNECTIONS', arguments={
    'toolkits': ['gemini'],
    'action': 'connect'
})
# conn.data.results.gemini.status == 'active'
```

### Шаг 2: Generate Video (Veo 3.1) — правильная сигнатура

**ВАЖНО:** `session.execute()` принимает `tool_slug` и `arguments=`, НЕ `action_name=`.

```python
result = session.execute('GEMINI_GENERATE_VIDEOS', arguments={
    'prompt': 'fitness gym workout motivational video cinematic 9:16',
    'aspect_ratio': '9:16',
    'resolution': '720p',
    'duration_seconds': 8,
    'model': 'veo-3.1-fast-generate-preview'
})
# ВАЖНО: operation_name в result.data['operation_name'], не в result.data['raw']
op_name = result.data['operation_name']
# 'models/veo-3.1-fast-generate-preview/operations/xxxx'
```

**Параметры GEMINI_GENERATE_VIDEOS (полный input_schema):**
| Параметр | Тип | Обязательный | Значения |
|----------|-----|:-----------:|---------|
| `prompt` | string | ✅ | Описание видео |
| `model` | string | — | `veo-3.1-generate-preview` (default), `veo-3.1-fast-generate-preview` |
| `aspect_ratio` | string | — | `16:9`, `9:16` |
| `resolution` | string | — | `720p`, `1080p` |
| `duration_seconds` | integer | — | `4`, `6`, `8` |
| `person_generation` | string | — | `allow_all` |
| `seed` | integer | — | Для воспроизводимости |
| `negative_prompt` | string | — | "cartoon, drawing, low quality" |

### Шаг 3: Поллинг — GEMINI_GET_VIDEOS_OPERATION (предпочтительно)

WAIT_FOR_VIDEO может висеть 30+ секунд через Composio (ретрят запросы пока операция не завершится). Использовать GET_VIDEOS_OPERATION для быстрой проверки:

```python
# Быстрая проверка (не виснет)
check = session.execute('GEMINI_GET_VIDEOS_OPERATION', arguments={
    'operation_name': op_name
})
if check.data.get('done', False):
    # Получить s3url через WAIT_FOR_VIDEO (теперь быстро, т.к. done=True)
    wait = session.execute('GEMINI_WAIT_FOR_VIDEO', arguments={
        'operation_name': op_name
    })
    url = wait.data['video_file']['s3url']
```

### Шаг 3: Поллинг — GEMINI_GET_VIDEOS_OPERATION (предпочтительно)

WAIT_FOR_VIDEO может висеть 30+ секунд через Composio (ретрят запросы пока операция не завершится). Использовать GET_VIDEOS_OPERATION для быстрой проверки:

```python
import time

# Поллинг через быстрый GET_VIDEOS_OPERATION
for attempt in range(12):
    # Использовать GET_VIDEOS_OPERATION (не виснет)
    check = session.execute('GEMINI_GET_VIDEOS_OPERATION', arguments={
        'operation_name': op_name
    })
    done = check.data.get('done', False)
    if done:
        # Получить s3url через WAIT_FOR_VIDEO (теперь быстро, т.к. done=True)
        wait = session.execute('GEMINI_WAIT_FOR_VIDEO', arguments={
            'operation_name': op_name
        })
        url = wait.data['video_file']['s3url']
        print(f'Video URL: {url}')
        break
    print(f'Still generating... (attempt {attempt+1})')
    time.sleep(15)
```

### Шаг 4: Download
```python
import urllib.request
urllib.request.urlretrieve(video_url, 'cache/veo_generated_video.mp4')
# ~2.3 MB, MP4, 9:16, 5 sec
```

## Gemini Image Generation (Nano Banana)
```python
# Модели:
# - gemini-2.5-flash-image (GA stable, fast)
# - gemini-3-pro-image-preview (Nano Banana Pro, 4K, thinking mode, до 14 ref images)
# - gemini-2.0-flash-exp-image-generation (2.0 Flash experimental)

result = session.execute('GEMINI_GENERATE_IMAGE', arguments={
    'prompt': 'luxury yacht sunset cinematic 8K photorealistic',
    'model': 'gemini-3-pro-image-preview',
    'aspect_ratio': '9:16',
    'image_size': '4K'
})

# Извлечение s3url из ответа:
def get_image_link(resp):
    d = (resp or {}).get('data', {}) if isinstance(resp, dict) else {}
    img = d.get('image') or {}
    if isinstance(img, dict) and img.get('s3url'):
        return img['s3url']
    for r in (d.get('results') or []):
        img = (((r.get('response') or {}).get('data') or {}).get('image') or {})
        if img.get('s3url'):
            return img['s3url']
    return None
```

## Известные ошибки и решения

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `NameError: name 'session' is not defined. Did you mean: 'ession'?` | Оппечатка `ession = c.create()` | Проверить имя переменной |
| `No active connection found for toolkit(s) 'gemini'` | Не вызван `COMPOSIO_MANAGE_CONNECTIONS` | Выполнить connect перед execute |
| `This API key does not have the permissions required...` | Ключ создан без Read/Write Tools permissions | Создать новый с "Read All" + "Write All" |
| `PermissionDeniedError: 403 on /api/v3.1/toolkits` | Toolkits Read access нужен для listing | Grant "toolkits" read access |
| `429 RESOURCE_EXHAUSTED` | Concurrent limit превышен | Exponential backoff, ≤ 3 concurrent |
| `400 BAD_REQUEST: invalid tool_slugs` | Неправильное имя параметра | Использовать `tool_slugs` (snake_case) |
| Session timeout на execute() | Tool router session перегружен | Использовать `c.use(session_id=...)` для reuse |

## Анализ альтернатив (research-first)

**Проблема:** генерация AI-видео бесплатно.
**3 найденных варианта:**
1. **Composio + Gemini Veo 3.1** ✅ — бесплатно, ~20 сек, реальное motion video, через установленный SDK
2. **Pollinations.ai image** ✅ — бесплатный FLUX image gen, затем FFmpeg сборка (slideshow, не motion)
3. **xAI video_generate** ❌ — платный, нет credits (401)
4. **Runway/Pika** ⏳ — free trial, требует регистрацию (HITL)
5. **BrowserOS → Gemini web** ⏳ — бесплатно, но через браузер, не программно

**Итог:** Composio Veo — лучший вариант для программной генерации real AI видео.
