---
name: task-driven-agent
description: >-
  Build an autonomous AI agent that interprets natural language tasks via LLM
  and executes them through modular skill modules. Covers the agent-core +
  skill architecture, project structure, skill interface, scheduler, and
  Telegram integration.
trigger: >-
  When the user wants to build an AI agent (like MIRA) that understands
  natural language, routes tasks to plugins/skills, and executes autonomously.
  Also when replicating a "Telegram AI assistant" pattern with content
  generation, social posting, scheduling, and moderation.
usage: >-
  Load with skill_view(name='task-driven-agent') before starting to build
  or extend a task-driven agent. Follow the architecture section to scaffold
  the project.
tags: [agent, architecture, telegram, llm, modular, skills, automation]
---
# Task-Driven Agent Architecture

Build an AI agent that understands natural language and executes tasks through modular skills.

## Architecture

```
User text → agent_core.interpret_task()
                ↓ LLM
           {skill, action, params}
                ↓
        execute_plan() dispatcher
                ↓
     ┌──────┬──────┬──────┬──────┐
  content social scheduler crypto ...
     └──────┴──────┴──────┴──────┘
                ↓
    Result string → back to user
```

### Core Components

**agent_core.py** — The brain:
1. `interpret_task(user_text)` — sends text + system prompt to LLM, returns structured plan `{skill, action, params, reasoning}`
2. `execute_plan(plan)` — dispatches to the right skill module by name

**Skill modules** — Each in `skills/<name>.py` with a uniform interface:
```python
def handle_<skill>(action: str, params: dict) -> str:
    """Returns human-readable result string."""
```

**bot.py** — Platform interface (Telegram, CLI, etc.). Receives input, calls interpreter, sends result back.

## Project Structure

```
agent-name/
├── bot.py              # Entry point (Telegram, CLI, etc.)
├── agent_core.py       # LLM interpreter + dispatch
├── config.py           # Env-based config loader
├── run.py              # Start/stop/watchdog
├── requirements.txt
├── .env.example
├── README.md
├── skills/             # Modular skill modules
│   ├── content.py      # Text + image generation
│   ├── social.py       # Social media posting
│   ├── email.py        # Email management
│   ├── scheduler.py    # Recurring tasks (SQLite)
│   ├── moderation.py   # Chat moderation
│   ├── crypto.py       # Cryptocurrency prices
│   └── search.py       # Web search
├── data/               # Runtime data (created)
└── logs/               # Logs (created)
```

## agent_core.py Pattern

### System Prompt (for LLM task interpretation)

```python
SYSTEM_PROMPT = """Ты — планировщик задач AI-агента MIRA.
Пользователь пишет на естественном языке, а ты преобразуешь задачу в JSON.

Доступные навыки (skills):
- content  — генерация текста, картинок, видео
- social   — постинг в соцсети, ответ на комментарии, аналитика
- email    — чтение почты, очистка спама
- scheduler — создание повторяющихся задач, расписание
- moderation — модерация Telegram чата, проверка нарушений
- crypto   — курс криптовалют, анализ рынка
- search   — поиск информации в интернете

Формат ответа (только JSON, без объяснений):
{
  "skill": "social",
  "action": "post",
  "params": {"platform": "instagram", "text": "текст поста"},
  "reasoning": "почему выбрал этот навык"
}

Для повторяющихся задач:
{
  "skill": "scheduler",
  "action": "create",
  "params": {
    "schedule": "0 16 * * *",
    "task": { ... вложенная задача ... },
    "description": "ежедневный пост"
  }
}
"""
```

### Interpreter

```python
def interpret_task(user_text: str, context: dict = None) -> dict:
    """NL → structured action via LLM. Falls back to search if no API key."""
    if not LLM_API_KEY:
        return {"skill": "search", "action": "search",
                "params": {"query": user_text}, "reasoning": "LLM unavailable"}

    resp = httpx.post(LLM_API_URL, headers={"Authorization": f"Bearer {LLM_API_KEY}"},
        json={"model": LLM_MODEL, "messages": [...], "temperature": 0.3, "max_tokens": 500},
        timeout=30)
    plan = json.loads(extract_json(resp.json()["choices"][0]["message"]["content"]))
    return plan
```

### Dispatcher

```python
def execute_plan(plan: dict) -> str:
    skill = plan.get("skill")
    action = plan.get("action")
    params = plan.get("params", {})
    module = SKILL_MAP.get(skill)
    if module:
        return module(action, params)
    return f"⚠️ Skill '{skill}' not found"
```

## Skill Module Interface

Each module **must**:
1. Be importable from `skills/<name>.py`
2. Export `handle_<name>(action, params) → str`
3. Log via `logging.getLogger("mira.skills.<name>")`
4. Handle dry-run gracefully when API keys are missing

### Example: content.py

```python
def handle_content(action: str, params: dict) -> str:
    if action in ("generate_text", "text"):
        text = generate_text(params.get("topic", "AI"))
        return f"📝 {text}"
    elif action in ("generate_image", "image"):
        prompt = params.get("prompt", "art")
        img = generate_image(prompt)
        return f"🎨 {img['url']}"
    return f"⚠️ Unknown action: {action}"
```

## Config Pattern

Use a `config.py` that reads from `.env` in the parent directory:

```python
def _load_env(key: str, default: str = "") -> str:
    """Lazy-load .env on first call, then cache."""
    if not hasattr(_load_env, "_cache"):
        _load_env._cache = {}
        env_path = Path(__file__).resolve().parent.parent / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    _load_env._cache[k.strip()] = v.strip()
    return _load_env._cache.get(key, default)

BOT_TOKEN = _load_env("MIRA_BOT_TOKEN", _load_env("TELEGRAM_BOT_TOKEN", ""))
LLM_API_KEY = _load_env("MIRA_LLM_KEY", "")
```

## Pitfalls

### 1. LLM returns non-JSON or markdown-wrapped JSON
Always strip markdown code fences before parsing:
```python
content = content.strip()
if content.startswith("```"):
    content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
plan = json.loads(content)
```

### 2. Same token, two bots = TelegramConflictError
The MIRA bot and gateway/CPA bot **cannot share a token**. Always create a dedicated bot via @BotFather for each service. Use `MIRA_BOT_TOKEN` sep-arately from `TELEGRAM_BOT_TOKEN`.

### 3. LLM unavailable = silent fallback
Without `MIRA_LLM_KEY`, `interpret_task()` returns a `search` plan. The bot still works but only searches. Log a warning so the user knows.

### 4. Skill import errors crash the dispatcher
Wrap skill imports in `execute_plan`:
```python
try:
    module = __import__(f"skills.{skill}", fromlist=["handle"])
    return module.__dict__[f"handle_{skill}"](action, params)
except (ImportError, KeyError) as e:
    log.error("Skill load failed: %s", e)
    return f"⚠️ Skill '{skill}' not available"
```

### 5. Voice messages are ignored if no STT
Add a voice handler that acknowledges receipt and explains the limitation:
```python
async def handle_voice(update, context):
    await update.message.reply_text(
        "🎤 Голосовой ввод получен. STT будет доступен после настройки."
    )
```

## See Also

- `telegram-bot-integration` — low-level Telegram proxy/networking/subprocess setup
- `content-pipeline` — content generation for arbitrage (companion to the content skill)
- `references/mira-agent-2026-07-10.md` — full implementation: project structure, all 7 skill modules, interpreter design
