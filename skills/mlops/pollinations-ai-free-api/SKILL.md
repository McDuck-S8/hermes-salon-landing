---
name: pollinations-ai-free-api
description: "Pollinations.ai — free, no-API-key image/video/audio generation. No signup, no limits, URL-based API. Use for AI OFM content generation and any project needing free AI media."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [image-generation, video-generation, free-api, AI, pollinations]
    related_skills: [comfyui, image_generate]
---

# Pollinations.ai — Free AI Media Generation API

**Бесплатная генерация изображений, видео, аудио и текста.** Без регистрации, без API ключа.

**⚠️ Rate limit:** ~1 запрос/15-20 сек. После 2-3 быстрых запросов → HTTP 429. Таймаут запроса ставь 75-90 сек (FLUX медленный). 
- 1-2 изображения: `time.sleep(20)` между запросами, таймаут 60с
- 3-4 изображения: `time.sleep(30)` между запросами, таймаут 90с 
- 5+ изображений: POST на `gen.pollinations.ai` с API ключом (или растяни на 5+ минут)
- При 429: пауза 60+ сек, затем повтор с тем же seed
- `time.sleep(10)` НЕДОСТАТОЧНО — приводит к 429 на 3-м запросе

## Адреса

| Endpoint | Описание | Auth |
|----------|----------|------|
| `https://image.pollinations.ai/prompt/...` | Изображения по GET-запросу | ❌ не нужна |
| `https://gen.pollinations.ai` | OpenAI-совместимый API (POST) | ✅ `sk_*` ключ |
| `https://media.pollinations.ai` | Хостинг медиа | ❌ публичный |

## Генерация изображений (без ключа)

Самый простой способ — GET-запрос:

```
https://image.pollinations.ai/prompt/{url_encoded_prompt}
```

Параметры:

| Параметр | Значение по умолч. | Описание |
|----------|-------------------|----------|
| `width` | 1024 | Ширина |
| `height` | 1024 | Высота |
| `seed` | random | Seed для воспроизводимости |
| `model` | flux | Модель: flux, seedream, turbo, nanobanana |
| `nologo` | false | `true` — убрать логотип |

Пример (Python):

```python
import urllib.request, urllib.parse

prompt = "Beautiful ethereal fantasy woman portrait, digital art"
encoded = urllib.parse.quote(prompt)
url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1024&seed=42&model=flux"

req = urllib.request.Request(url, headers={"User-Agent": "Hermes-Agent/1.0"})
with urllib.request.urlopen(req, timeout=60) as resp:
    data = resp.read()  # bytes — JPEG image
    with open("output.jpg", "wb") as f:
        f.write(data)
```

Пример (curl):

```bash
curl -o output.jpg "https://image.pollinations.ai/prompt/beautiful%20woman%20portrait?width=768&height=1024&seed=42&model=flux"
```

## Модели изображений

| Модель | Качество | Скорость | Примечание |
|--------|----------|----------|------------|
| `flux` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | FLUX.1 — лучшая бесплатная |
| `seedream` | ⭐⭐⭐⭐ | ⭐⭐⭐ | ByteDance Seedream |
| `turbo` | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Быстрая генерация |
| `nanobanana` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Nano Banana |

## OpenAI-совместимый API (POST, нужен ключ)

```
POST https://gen.pollinations.ai/v1/images/generations
Authorization: Bearer sk_ваш_ключ
```

Тело:

```json
{
  "prompt": "beautiful woman portrait",
  "model": "flux",
  "size": "768x1024",
  "n": 1,
  "response_format": "b64_json"
}
```

Ключ получается на [enter.pollinations.ai](https://enter.pollinations.ai) — бесплатный тир существует.

## Hybrid Video Assembly (Pollinations.ai + FFmpeg)

Pollinations.ai НЕ генерирует видео напрямую (endpoint experimental). Рабочий подход:

1. **Генерация реальных AI-картинок** через `image.pollinations.ai/prompt/...` (FLUX, 720×1280, 9:16)
2. **Сборка видео** через FFmpeg: каждый кадр → 3-сек клип → crossfade между ними

```python
# Шаг 1: генерация кадров (rate limit: 1 запрос/10 сек)
import urllib.request, urllib.parse, time

prompts = [
    "luxury lifestyle man counting stacks of money cinematic photorealistic",
    "crypto trader celebrating Bitcoin chart green candles dramatic lighting"
]
for i, prompt in enumerate(prompts):
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=720&height=1280&model=flux&nologo=true&seed={42+i}"
    req = urllib.request.Request(url, headers={"User-Agent": "Hermes-Agent/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        with open(f"frame_{i+1}.jpg", "wb") as f:
            f.write(resp.read())
    time.sleep(10)

# Шаг 2: FFmpeg assembly (каждый кадр 3 сек, crossfade 1 сек)
for i in 1 2 3:
  ffmpeg -y -loop 1 -i frame_$i.jpg -c:v libx264 -t 3 \
    -vf "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,fade=t=in:st=0:d=0.5,fade=t=out:st=2.5:d=0.5" \
    -r 30 clip_$i.mp4

ffmpeg -y -i clip_1.mp4 -i clip_2.mp4 -i clip_3.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=1:offset=2[12v];[12v][2:v]xfade=transition=fade:duration=1:offset=4[outv]" \
  -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p -r 30 final_video.mp4

# Шаг 3: текстовые оверлеи (CTA)
ffmpeg -i final_video.mp4 \
  -vf "drawtext=text='HEADLINE':fontsize=32:fontcolor=white:x=(w-text_w)/2:y=h*0.08:box=1:boxcolor=black@0.5:boxborderw=5" \
  -c:v libx264 final_cta.mp4
```

**Характеристики:**
- 5 кадров → 15 сек видео (с crossfade), ~1.3 MB, 9:16
- Подходит для TikTok/Shorts/Reels (вертикальный формат)
- Zero API dependencies: Pollinations не требует ключа, FFmpeg локальный

## Composio + Gemini Veo — настоящая AI-видеогенерация (free, No Auth)

**Альтернатива FFmpeg-сборке.** Вместо гибридной сборки кадров → видео можно генерировать настоящее AI-видео через Google Veo 3, доступное через Composio Gemini toolkit.

**Composio SDK (установлен):** `pip install composio`

```python
import os
from composio import Composio

os.environ["COMPOSIO_API_KEY"] = "ak_..."
c = Composio()

# Создать сессию
session = c.create(user_id="hermes")
tools = session.tools()

# Генерация видео через Gemini Veo
result = tools.execute(
    action="GEMINI_GENERATE_VIDEOS",
    params={
        "prompt": "luxury lifestyle cinematic vertical video 9:16",
        "model": "veo-3.0-generate-preview"
    }
)
operation_name = result.get("operation_name")  # для отслеживания прогресса

# Проверка статуса (ждём готовности)
status = tools.execute(
    action="GEMINI_WAIT_FOR_VIDEO",
    params={"operation_name": operation_name}
)
```

**Доступные Gemini-экшены через Composio (No Auth):**

| Action | Описание |
|--------|----------|
| `GEMINI_GENERATE_CONTENT` | Текст/аудио через Gemini Flash/Pro |
| `GEMINI_GENERATE_IMAGE` | Nano Banana (gemini-2.5-flash-image / gemini-3-pro-image-preview) |
| `GEMINI_GENERATE_VIDEOS` | Google Veo 3 — генерация видео из текста |
| `GEMINI_WAIT_FOR_VIDEO` | Ожидание готовности видео (Veo) |
| `GEMINI_GET_VIDEOS_OPERATION` | Проверка статуса операции Veo |
| `GEMINI_COUNT_TOKENS` | Подсчёт токенов |
| `GEMINI_EMBED_CONTENT` | Текстовые эмбеддинги |

**⚠️ Настройка API ключа:**
1. Зайти в дашборд Composio → Settings → API Keys
2. Создать ключ с правами `tools:read` + `tools:write` (минимум)
3. Положить в `.env`: `COMPOSIO_API_KEY=ak_...`
4. SDK сам читает `COMPOSIO_API_KEY` из окружения

## BrowserOS как основной инструмент (вместо API хаков)

Для анализа видео/изображений **не использовать API-хаки** (DeepSeek upload не работает). Вместо этого:

1. Открыть Gemini/Claude/ChatGPT через **BrowserOS**
2. Загрузить файл через интерфейс
3. Получить результат

**Бесплатные сервисы для анализа видео (через BrowserOS):**
- `https://gemini.google.com` — Gemini понимает видео нативно
- `https://claude.ai` — Claude умеет загружать и анализировать видео
- `https://chat.openai.com` — ChatGPT (GPT-4o) смотрит видео

## Когда использовать

| Задача | Инструмент |
|--------|-----------|
| **Изображения** (бесплатно, без ключа) | `image.pollinations.ai/prompt/...` GET |
| **Изображения** (продвинутые) | `gen.pollinations.ai` POST с ключом |
| **Видео** (FFmpeg + AI кадры) | Pollinations FLUX кадры → FFmpeg assembly |
| **Видео** (настоящее AI-видео) | Composio + Gemini Veo 3 (No Auth) |
| **Анализ медиа** | BrowserOS → Gemini/Claude/ChatGPT веб-интерфейс |

## Ограничения

- **Rate limit:** ~1 запрос/10 сек. После 2+ быстрых запросов → 429 Too Many Requests.
  - Решение: `time.sleep(10)` между запросами + retry с паузой 30с при 429
  - Для массовой генерации (10+ изображений) — используйте POST на `gen.pollinations.ai` с API ключом
- NSFW-контент: параметр `safe` отключён по умолчанию (не фильтруется), но модели могут не генерировать откровенный контент
- Размер: до 2048px по каждой стороне
- Скорость: зависит от нагрузки (обычно 3-30 секунд на изображение)
- Для production с высокими требованиями — используйте `gen.pollinations.ai` с ключом (более стабильно)
- **Pollinations НЕ генерирует видео.** Для видео — Hybrid Assembly (см. секцию выше)

## Known Issues

- Иногда таймаут (30+ секунд) — повторный запрос с тем же seed решает
- Модель `seedream` может быть медленнее `flux`
- Качество зависит от промпта — подробные промпты работают лучше

## References

- `references/composio-gemini-veo-setup.md` — настройка Composio + Gemini Veo для настоящей AI-видеогенерации
- `references/content-locking-prompts-2026-07-21.md` — проверенные промпты для content locking ниш
- `references/session-test-results-2026-07-15.md` — результаты тестирования генерации
