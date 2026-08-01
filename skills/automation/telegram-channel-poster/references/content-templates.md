# Content Templates for Telegram Channel Poster

## Template Structure

Each template category has multiple variations. Templates use Python `str.format()` with named placeholders.

### ai_news — AI Releases & Announcements
**Placeholders:** `title`, `summary`, `url`, `opinion`
```html
🚀 <b>{title}</b>

{summary}

🔗 <a href="{url}">Читать подробнее</a>
```

### ai_tool — Tool Reviews & Tutorials
**Placeholders:** `name`, `url`, `tagline`, `description`, `features`, `pricing`
```html
🛠 <b>Инструмент дня:</b> <a href="{url}">{name}</a>

{description}

✨ <b>Фишки:</b> {features}

👉 <a href="{url}">Попробовать бесплатно</a>
```

### code_tip — Code Snippets & Patterns
**Placeholders:** `title`, `code`, `explanation`
```html
💻 <b>Сниппет:</b> {title}

<pre><code>{code}</code></pre>

📝 {explanation}

#coding #python #ai
```

### analytics — Traffic/CPA Insights
**Placeholders:** `title`, `insight`, `conclusion`, `url`, `action`
```html
📊 <b>Аналитика:</b> {title}

{insight}

📈 <b>Вывод:</b> {conclusion}

🔗 Источник: {url}
```

### motivation — Quotes & Productivity
**Placeholders:** `quote`, `author`, `title`, `body`, `action`
```html
💭 <b>Мысль дня</b>

<blockquote>"{quote}"</blockquote>

— {author}

#motivation #mindset
```

## Button Patterns

### Category-Specific Buttons (first row)
| Category | Button Text | URL/Callback |
|----------|-------------|--------------|
| `ai_tool` | 🚀 Попробовать | Tool URL |
| `code_tip` | 💾 Сохранить | `save_{title[:20]}` |
| `analytics` | 📊 Подробнее | Source URL |
| `ai_news` | 🔗 Источник | Source URL |
| `motivation` | (none) | — |

### Global Buttons (always appended, 2 rows)
**Row 1:**
- 📢 Все каналы → `https://t.me/max_brain_chef_official`
- 🤖 Бот → `https://t.me/max_brain_chef_bot`

**Row 2:**
- 💬 Чат → `https://t.me/+nVpNjeTXzXE5YTRi`
- 🔥 Топ → `callback_data="top_posts"`

## Hashtag Injection

Automatic hashtags per category:
- `ai_news` → `#AI #News #LLM`
- `ai_tool` → `#AITools #Review #Productivity`
- `code_tip` → `#coding #python #AI`
- `analytics` → `#analytics #CPA #traffic`
- `motivation` → `#motivation #mindset`

## Channel-Specific Adaptations

| Channel | Focus | Preferred Categories |
|---------|-------|---------------------|
| `@max_brain_chef_official` | General AI & Agents | ai_news, ai_tool, code_tip, analytics |
| `@ai_frontier_you` | Frontier AI, new models | ai_news, ai_tool |
| `@max_brain_chef_ai` | AI coding, dev tools | code_tip, ai_tool, analytics |
| `@neuro_kitchen_ai` | Lifestyle, motivation, recipes | motivation, ai_news |

## Example Rendered Posts

### AI Tool Post
```
🛠 <b>Инструмент дня:</b> <a href="https://fal.ai">Fal.ai</a>

Запускай Flux, SDXL, Whisper, Llama на серверлесс GPU. Платишь за секунды.

✨ <b>Фишки:</b> Flux/SDXL/Whisper, serverless, OpenAI-совместимый API

👉 <a href="https://fal.ai">Попробовать бесплатно</a>

[🚀 Попробовать] [📢 Все каналы] [🤖 Бот]
                                      [💬 Чат] [🔥 Топ]
```

### Code Tip Post
```
💻 <b>Сниппет:</b> Async HTTP клиент с retry

<pre><code>import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=30)
        r.raise_for_status()
        return r.json()</code></pre>

📝 Экспоненциальный бэкофф + автоматический ретрай. Экономит нервы при флакинге API.

#coding #python #ai

[💾 Сохранить] [📢 Все каналы] [🤖 Бот]
              [💬 Чат] [🔥 Топ]
```