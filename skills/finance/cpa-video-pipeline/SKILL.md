---
name: cpa-video-pipeline
description: Use when orchestrating full video generation pipeline for CPA — script generation → stock footage (Pexels/Pixabay) → voiceover (ElevenLabs) → FFmpeg composition → metadata/UTM → upload adapters
---

# CPA Video Pipeline

End-to-end orchestration for vertical video production (TikTok/Shorts/Reels) at scale. Connects all components: scripts → clips → audio → compose → metadata → upload.

## When to Use

- Need to produce 5-50 vertical videos/day for CPA campaigns
- Want automated pipeline: script → stock footage → voiceover → composition → upload
- Need A/B/C variant testing with UTM tracking
- Need platform-specific upload (TikTok API, YouTube Shorts API, Instagram Graph API)
- Want cost control (kill switches for daily limit, cost limit)

## Pipeline Stages

### 0. CONTENT LOCKING VIDEO — REAL AI IMAGES (актуальный подход, 2026-07-21)

**⚠️ ВАЖНО: FFmpeg drawtext на пустом фоне = "фон с надписью". Пользователь категорически rejects.**
Не использовать `lavfi color` + `drawtext`. Это не видео, это подделка.

**Правильный подход: Pollinations.ai (free FLUX) → реальные AI-картинки → FFmpeg сборка**

```python
# Этап 1: Генерация реальных AI-картинок (Pollinations.ai, бесплатно, без ключа)
import urllib.request, urllib.parse, time

niche_prompts = [
    "luxury lifestyle man counting stacks of hundred dollar bills marble table cinematic photorealistic",
    "young successful businessman looking at yacht from balcony harbor sunset luxury lifestyle",
    "crypto trader celebrating in front of screens Bitcoin chart green candles going up dramatic lighting",
    "luxury sports car red Ferrari in front of glass mansion sunset golden hour cinematic 8K",
    "attractive couple laughing holding champagne infinity pool ocean sunset luxury lifestyle candid"
]

for i, prompt in enumerate(niche_prompts):
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=720&height=1280&model=flux&nologo=true&seed={42+i}"
    req = urllib.request.Request(url, headers={"User-Agent": "Hermes-Agent/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
        with open(f"cache/ai_frame_{i+1}.jpg", "wb") as f:
            f.write(data)
    time.sleep(10)  # rate limit protection

# Этап 2: Сборка видео (FFmpeg — только assembly, не генерация)
# Каждый кадр 3 сек, crossfade 1 сек между, 9:16 (720×1280)
for i in 1..5:
    ffmpeg -y -loop 1 -i cache/ai_frame_$i.jpg -c:v libx264 -t 3 \
      -pix_fmt yuv420p \
      -vf "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,fade=t=in:st=0:d=0.5,fade=t=out:st=2.5:d=0.5" \
      -r 30 cache/clip_$i.mp4

# Конкатенация с crossfade
ffmpeg -y -i cache/clip_1.mp4 -i cache/clip_2.mp4 -i cache/clip_3.mp4 ... \
  -filter_complex "[0:v]setpts=PTS-STARTPTS[0v];[1:v]setpts=PTS-STARTPTS+2/TB[1v];...\
    [0v][1v]xfade=transition=fade:duration=1:offset=2[12v];..." \
  -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p -r 30 \
  cache/ai_video_final.mp4

# Этап 3: Текстовые оверлеи с CTA
ffmpeg -i cache/ai_video_final.mp4 \
  -vf "drawtext=text='HOW I MAKE \$500/DAY':fontsize=32:fontcolor=white:...\
        drawtext=text='CLICK LINK BELOW ↓':fontsize=28:fontcolor=yellow:..." \
  cache/content_locking_final.mp4
```

**Характеристики:**
- **Pollinations.ai FLUX** — лучшая бесплатная AI-генерация изображений (77-86 KB/файл)
- **Rate limit:** ~1 запрос/10 сек, после 1-2 запросов подряд → 429 (Too Many Requests)
  - Решение: `time.sleep(10)` между запросами, повтор при 429
- **Качество:** зависит от промпта — подробные, конкретные промпты дают лучший результат
- **Итоговое видео:** ~1.3 MB, 15 сек, 9:16, реальный AI-контент
- **Zero API dependencies:** Pollinations не требует ключа. FFmpeg локальный

**Ниши (проверенные промпты для content locking):**
- Wealth/lifestyle: "luxury lifestyle", "money stacks", "yacht", "sports car", "mansion"
- Fitness: "gym workout", "athletic body", "six pack abs", "yoga beach sunset"
- Crypto: "crypto trader", "bitcoin chart", "green candles", "blockchain visualization"

### 0b. VERIFICATION (когда нет vision API)

После генерации видео нужно проверить что получилось. **НЕ использовать vision_analyze** — он падает с 403 на этой конфигурации.

**Правило: показать результат пользователю в браузере, не описывать файловый путь.**
Пользователь категорически: "если мне что то показываешь, то открывай в браузере!"

Рабочие методы (в порядке предпочтения):

| Метод | Команда | Что даёт |
|-------|---------|----------|
| **Открыть в браузере** | `python -m http.server 8765` (background) → `mcp__browseros__new_page(url="http://127.0.0.1:8765/cache/file.mp4")` | Пользователь смотрит сам, в браузере |
| **BrowserOS скриншот** | `mcp__browseros__save_screenshot` → `C:\\\\Users\\\\Asus\\\\Desktop\\\\preview.jpg` | Если нужно показать визуально |
| **ffprobe** | `ffprobe cache/video.mp4` | Длительность, битрейт, кодек, размер |
| **Проводник** | `explorer /select,\\"D:\\\\...\\\\.mp4\\"` | Открыть папку в проводнике |

**Правило:** vision_analyze упал 1 раз → STOP. Не ретраить.

### 0c. REAL AI VIDEO — Google Veo 3.1 through Composio (актуальный подход, 2026-07-21)

**⚠️ ВАЖНО: Это НАСТОЯЩЕЕ AI-видео, не FFmpeg drawtext подделка.**
Google Veo 3.1 генерирует полноценное видео с motion, объектами, сценами.

**Pre-requisite:** Composio API key (full access) в `COMPOSIO_API_KEY` env или .env.
Workspace: `soczakladk_workspace`, project: `soczakladk_workspace_first_project`.

**Паттерн (рабочий код с session-сессии):**

```python
import os
os.environ['COMPOSIO_API_KEY'] = 'ak_YOUR_KEY_HERE'

from composio import Composio
c = Composio()

# 1. Создать session (каждый раз новый user_id)
session = c.create(user_id='hermes-agent')
sid = session.session_id

# 2. Подключить Gemini toolkit (No Auth — работает без API ключа)
session.execute('COMPOSIO_MANAGE_CONNECTIONS', arguments={
    'toolkits': ['gemini'], 'action': 'connect'
})
# → {'results': {'gemini': {'status': 'active', 'instruction': 'gemini does not require authentication'}}}

# 3. Запустить генерацию видео (Veo 3.1)
result = session.execute('GEMINI_GENERATE_VIDEOS', arguments={
    'prompt': 'A person doing intense weightlifting in a modern gym, cinematic lighting, slow motion, 9:16'
})
op_name = result.data['operation_name']
# → 'models/veo-3.1-generate-preview/operations/xxxx'

После этого:

**Правильный поллинг: GEMINI_GET_VIDEOS_OPERATION + WAIT_FOR_VIDEO (2026-07-21):**
WAIT_FOR_VIDEO может висеть 30+ сек через Composio, пока операция не завершится.
Лучше поллить через GET_VIDEOS_OPERATION (быстрый, не виснет):

```python
# Быстрая проверка статуса (не виснет)
check = session.execute("GEMINI_GET_VIDEOS_OPERATION", arguments={
    "operation_name": op_name
})
done = check.data.get("done", False)

# Если done=True, получить s3url через WAIT_FOR_VIDEO
# WAIT_FOR_VIDEO возвращает s3url только когда done=True
wait = session.execute("GEMINI_WAIT_FOR_VIDEO", arguments={
    "operation_name": op_name
})
url = wait.data["video_file"]["s3url"]
```

# 5. Скачать видео

# 5. Скачать видео
import urllib.request
urllib.request.urlretrieve(video_url, 'cache/veo_generated_video.mp4')
```

**Характеристики Veo 3.1 через Composio:**
- **Время генерации:** ~20-30 секунд (первые результаты)
- **Формат:** MP4, ~2.3 MB за 5-секундный ролик
- **Аспект:** можно указать 9:16, 16:9, 1:1
- **Качество:** реальное motion video, объекты, свет, камера
- **Лимиты:** 3-5 concurrent jobs, 429 RESOURCE_EXHAUSTED → exponential backoff
- **Доступ:** через Composio Gemini toolkit (No Auth) — бесплатно, без своего API ключа

**Veo 3.1 actions в Composio:**
| Action | Назначение |
|--------|-----------|
| `GEMINI_GENERATE_VIDEOS` | Запустить генерацию, возвращает operation_name |
| `GEMINI_WAIT_FOR_VIDEO` | Получить результат по operation_name (поллинг, может висеть 30+ сек) |\n| `GEMINI_GET_VIDEOS_OPERATION` | Быстрая проверка статуса (done=true/false, не виснет) |
| `GEMINI_GENERATE_IMAGE` | Nano Banana image gen (альтернатива Pollinations) |

**Параметры GEMINI_GENERATE_VIDEOS (input_schema, 2026-07-21):**
- `prompt` (required) — текстовое описание видео
- `model` — `veo-3.1-generate-preview` (default) или `veo-3.1-fast-generate-preview`
- `aspect_ratio` — `16:9` или `9:16`
- `resolution` — `720p` или `1080p`
- `duration_seconds` — `4`, `6`, или `8`
- `person_generation` — `allow_all`
- `seed` — для воспроизводимости
- `negative_prompt` — что избегать (e.g. "cartoon, low quality")

**Структура ответа GEMINI_WAIT_FOR_VIDEO:**
```
SessionExecuteResponse(
    data={
        'success': True,
        'video_file': {
            'mimetype': 'video/mp4',
            'name': 'generated_video_xxx.mp4',
            's3url': 'https://temp.r2.cloudflarestorage.com/...'
        }
    }
)
```

**Pitfalls:**
- **Response parsing:** `result.data['operation_name']` (через `.data`, не `['data']`)
- **Session reuse:** всегда `c.use(session_id=sid)` для повторных вызовов в том же сеансе
- **No active connection error:** "No active connection found for toolkit" → запустить `COMPOSIO_MANAGE_CONNECTIONS` сначала
- **API ключ:** создаётся в дашборде Composio → Settings → API Keys. Нужен с правами Read+Write на все scope'ы
- **Permission denied при listing:** ключ без Toolkits Read → 403. Создавать с "Read All" + "Write All"
- **BrowserOS page ownership:** `mcp__browserclaw__*` не работают на страницах, открытых пользователем. Только `mcp__browseros__*`
- **SPA navigation:** Composio dashboard — SPA. Прямая навигация по URL может не сработать. Использовать `evaluate_script` → `window.location.href = url`

### 0d. FREE AI IMAGES — Nano Banana through Composio

Gemini toolkit включает `GEMINI_GENERATE_IMAGE` — альтернатива Pollinations.ai с более высоким качеством.

```python
result = session.execute('GEMINI_GENERATE_IMAGE', arguments={
    'prompt': 'luxury lifestyle yacht sunset cinematic 8K',
    'model': 'gemini-3-pro-image-preview',  # Nano Banana Pro — 4K, thinking mode
    'aspect_ratio': '9:16',
    'image_size': '4K'
})
```

**Модели:** `gemini-2.5-flash-image` (fast, GA), `gemini-3-pro-image-preview` (Pro, 4K, thinking mode), `gemini-2.0-flash-exp-image-generation` (experimental)

**Параметры:** prompt, model, aspect_ratio (1:1, 9:16, 16:9, 4:3, 3:2 и др.), image_size (1K, 2K, 4K), temperature, top_k, top_p, safety_settings

**Извлечение URL из ответа GEMINI_GENERATE_IMAGE:**
```python
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

### upload_file на React SPA (почему не работает)

BrowserOS/BrowserClaw `upload_file` устанавливают файл на `<input type="file">`, но **не триггерят React synthetic onChange**. React не видит файл — DOM обновлён, а состояние React не изменилось.

**Чинить через CDP escape hatch (BrowserClaw):**
```javascript
const doc = await browser.cdp('DOM.getDocument');
const search = await browser.cdp('DOM.querySelector', {
  nodeId: doc.root.nodeId, selector: 'input[type="file"]'
});
await browser.cdp('DOM.setFileInputFiles', {
  nodeId: search.nodeId, files: ['/path/to/file.mp4']
});
```

Или использовать `maresin/deepseek-automation-api` (Playwright делает это правильно).

## Pitfalls

### ❌ Не изобретай велосипед — research first, multiple alternatives

Перед тем как писать кастомное решение — **search first**. GitHub, StackOverflow, npm/PyPI.

**Ключевое правило: найди 3+ варианта, не останавливайся на первом.**
В сессии 2026-07-21 было найдено первое попавшееся GitHub-решение (maresin/deepseek-automation-api) и сразу предложено клонировать. Пользователь справедливо заметил: "а что в инете больше нет вариантов?"

**Процесс:**
1. Собрать 3+ альтернативы (GitHub, web search, npm/PyPI)
2. Сравнить: звёзды, лицензия, актуальность, платформа, зависимости
3. Выбрать лучшее — и только тогда действовать

**Контрпример (как НЕ надо):** 50+ tool calls на хак вокруг DeepSeek upload вместо того чтобы найти готовую библиотеку.

**Правило:** на каждую неочевидную проблему — минимум 2 поиска готовых решений перед 1 строкой кода.

Если скриншот сохраняется на диск пользователя — сообщить абсолютный путь.

### 1. SCRIPT GENERATION
   generate_content_locking_videos.py scripts
   → cache/video_pipeline/scripts_batch_*.json
   (topics × variants × platforms)

2. STOCK FOOTAGE
   stock_fetcher.py --topic "Free V-Bucks" --count 5
   → cache/stock_footage/free_v_bucks/pexels_*.mp4
   (Pexels/Pixabay API, vertical 9:16)

3. VOICEOVER
   voiceover_generator.py --script-file scripts_batch.json
   → cache/voiceovers/free_v_bucks/line1_*.mp3
   (ElevenLabs, niche-optimized voices)

4. COMPOSITION
   ffmpeg_composer.py --scripts cache/video_pipeline --clips cache/stock_footage --audio cache/voiceovers
   → cache/videos/video_free_v_bucks_A_tiktok.mp4
   (drawtext overlays: hook, body, CTA; 1080x1920, 30fps)

5. METADATA
   generate_content_locking_videos.py metadata
   → cache/video_pipeline/metadata/meta_*.json
   (title, description, hashtags, UTM URL, thumbnail text)

6. UPLOAD
   upload_adapters/tiktok_uploader.py
   upload_adapters/youtube_shorts_uploader.py
   upload_adapters/instagram_reels_uploader.py
   (platform APIs, staggered scheduling)
```

## CLI Usage

```bash
# Stage 1: Generate scripts (21 scripts: 7 niches × 3 variants × 1 platform)
python scripts/generate_content_locking_videos.py scripts --topics "Free V-Bucks" "Free Robux" "Free Crypto" --variants A B C --platforms tiktok

# Stage 2: Fetch stock footage (requires PEXELS_API_KEY, PIXABAY_API_KEY)
python scripts/stock_fetcher.py --topic "Free V-Bucks" --count 5
python scripts/stock_fetcher.py --topic "Free Robux" --count 5
# ... or batch all topics

# Stage 3: Generate voiceovers (requires ELEVENLABS_API_KEY)
python scripts/voiceover_generator.py --script-file cache/video_pipeline/scripts_batch_*.json

# Stage 4: Compose videos (requires ffmpeg)
python scripts/ffmpeg_composer.py --scripts cache/video_pipeline --clips cache/stock_footage --audio cache/voiceovers

# Stage 5: Generate metadata + UTM links
python scripts/generate_content_locking_videos.py metadata

# Stage 6: Upload (requires platform API credentials)
python scripts/upload_adapters/tiktok_uploader.py --video cache/videos/video_*.mp4 --meta cache/video_pipeline/metadata/meta_*.json
```

## Kill Switches (env vars)

```env
HERMES_VIDEO_GEN_ENABLED=true
HERMES_VIDEO_GEN_DAILY_LIMIT=50
HERMES_VIDEO_GEN_COST_LIMIT_USD=5.00
```

- Pipeline checks these before each stage
- Stops gracefully if limit reached
- Logs reason for stop

## A/B/C Variant Flow

| Stage | Variant Handling |
|-------|------------------|
| Scripts | `--variants A B C` generates all three |
| Footage | Same clips reused across variants (cost saving) |
| Voiceover | Same audio reused (only hook/CTA differ slightly) |
| Composition | Different drawtext overlays per variant |
| Metadata | Variant-specific UTM (`control_neutral`, `fomo_timer`, `social_live`) |
| Upload | Separate upload per variant for clean tracking |

## Cost Estimates (per video)

| Component | Cost | Notes |
|-----------|------|-------|
| Stock footage | $0 | Pexels/Pixabay free tier |
| Voiceover (ElevenLabs) | ~$0.02 | ~500 chars, multilingual v2 |
| FFmpeg compose | $0 | Local compute |
| Upload API | $0 | Platform free |
| **Total** | **~$0.02/video** | 50 videos = $1/day |

## Integration

- **Upstream:** `cpa-income-pipeline`, `cpa-video-script-generator`, `cpa-landing-generator`
- **Downstream:** `cpa-telegram-bot-generator` (traffic → landing), platform upload
- **Tracking:** UTM template in `cpa-income-pipeline` skill

### VEO 3.1 PROMPT ENGINEERING (2026-07-21)

**Формула Google Cloud:** `[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]`

**Формула Runway:** `[Camera Movement] + [Scene] + [Action] + [Details]`

**Типы движения камеры:** Static locked, handheld, dolly forward/backward, tracking, crane, orbit, dolly zoom (vertigo), FPV, drone ascending.

**Промпты для CPA-вертикалей (реальные, протестированы в этой сессии):**
| Вертикаль | Пример промпта |
|-----------|---------------|
| Gambling Proof | `Phone screen showing "YOU WON $2,450" with gold coins, neon lights, dark gaming room, shallow DOF, 9:16` |
| Gambling Exploit | `Young man pointing at laptop with betting site showing glitch, coffee shop, vlog style, 9:16` |
| Hot Take | `Direct to camera, serious, holding phone with red chart, raw YouTube style, dramatic pauses, 9:16` |

Подробнее: `references/veo-prompt-engineering-and-viral-hooks.md`

### 7 ВИРАЛЬНЫХ ХУКОВ ДЛЯ CPA (данные 8,426 видео, 2026)

| # | Тип | Avg Engagement | Пример для CPA |
|---|-----|---------------|----------------|
| 1 | **Hot Take** | 7.8% | "Букмекеры разводят вас. Вот доказательство." |
| 2 | **Flip the Script** | 6.3% | "Врачи молчат об этой добавке. Я скажу." |
| 3 | **Pull Them In** | 6.1% | "Как я вывел $2,450 за 10 минут?" |
| 4 | **Lead with Proof** | 5.2% | "Вот мой скриншот баланса. 100% реально." |
| 5 | **Open Loop** | — | "Я нашёл баг в этой букмекерской конторе." |
| 6 | **Confession** | — | "Я потерял $4,000 прежде чем понял эту стратегию." |
| 7 | **Identity Call** | — | "Если твои Reels набирают 200 просмотров — это для тебя." |

**Правило:** хук = секунды 1-3 видео. Без хука видео умирает в скролле.

Подробнее с 64+ шаблонами: `references/veo-prompt-engineering-and-viral-hooks.md`

## References

- `references/veo-prompt-engineering-and-viral-hooks.md` — Veo 3.1 prompting, viral hooks, CPA copywriting (2026-07-21)

- `skills/finance/arbitrage-execution/references/video-generation-content-locking-cpa.md` — full pipeline architecture
- `skills/finance/arbitrage-execution/references/ab-test-content-locking-fomo-social-proof-2026-07-07.md` — A/B test design
- `references/ffmpeg-windows-drawtext-fix.md` — Windows FFmpeg drawtext path pitfall fix
- `references/composio-gemini-veo-integration.md` — Composio SDK + Google Veo 3.1 video generation via Gemini toolkit