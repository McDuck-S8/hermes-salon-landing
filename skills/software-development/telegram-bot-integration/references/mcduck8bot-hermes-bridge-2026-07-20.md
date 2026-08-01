# McDuck8Bot — Hermes Telegram Bridge (2026-07-20)

## Overview
`scripts/mcduck_bot.py` — Long-polling Telegram bot that acts as a **live bridge** between Telegram and Hermes agent system. Every user message goes through the full Hermes processing pipeline (LLM + hooks + KC logging) and returns a real response.

## Key Characteristics
- **No hardcoded responses** — every message hits `llm_client.call_llm()` with Hermes context
- **Async processing** — immediate "🔄 Принято. Обрабатываю..." acknowledgment, then real response
- **Uses working token** — `MCDUCK_BOT_TOKEN` (6187967109:***) from `.env`, NOT CrystalWatchBot token
- **SOCKS5 proxy** — `urllib` + `PySocks` via 127.0.0.1:10806 (V2RayN)
- **Worker thread** — non-blocking queue for Hermes processing

## Commands
| Command | Action |
|---------|--------|
| `/start` | Welcome + command list |
| `/help` | Command reference |
| `/report` | Real-time system status from `cache/system_heartbeat.json` |
| `/ripple` | Top-3 mature keys from `reports/daily_ripple_map.html` |
| Any text | Full Hermes pipeline processing |

## Architecture
```
User (Telegram) 
  → getUpdates (long-poll, 30s timeout)
  → Worker thread queue
  → process_with_hermes(text)
    → hermes_hooks.on_task_complete()
    → llm_client.call_llm(prompt, system=HERMES_SYSTEM_PROMPT)
    → kc_rag.upsert() for persistence
  → sendMessage (real response)
```

## Hermes Integration Points

### 1. System Prompt (injected into LLM)
```python
system_prompt = """Ты — Hermes, автономный AI-агент. Ты работаешь непрерывно, 
мониторишь себя, учишься на ошибках, исправляешь их сам и проактивно улучшаешься.

Твой стиль: прямой, краткий, без воды. Ты не бот для болтовни — ты исполняешь задачи.
Отвечай на русском. Максимально по делу."""
```

### 2. Hooks & Knowledge Cube
```python
hooks.on_task_complete(
    f"Telegram task: {text[:80]}",
    "Processing via McDuck8Bot bridge",
    ["telegram", "mcduck", "live"]
)
kc_rag.upsert(
    content=f"User task from @McDuck8Bot: {text}",
    tags="task,telegram,mcduck,live",
    source="mcduck_bot",
    category="task",
    confidence=0.9,
    importance=7
)
```

### 3. Chain Heartbeat Events
The bot's activity fires `event_beat()` indirectly through `kc_rag.upsert()` → `knowledge_added` event, and the LLM call goes through `llm_client` which is monitored.

## Running
```bash
# Foreground (for testing)
python scripts/mcduck_bot.py

# Background (Hermes way)
terminal(background=true, notify_on_complete=true,
    command="cd D:/Portable_Soft/hermes && python scripts/mcduck_bot.py")
```

## Dependencies
- `PySocks` (for SOCKS5 via urllib)
- `llm_client` (Hermes unified LLM client with fallback)
- `hermes_hooks` (unified event tracking)
- `kc_rag` (Knowledge Cube persistence)

## Verification
```bash
# Test bot token
curl -x socks5://127.0.0.1:10806 https://api.telegram.org/bot6187967109:***/getMe

# Send test message
curl -x socks5://127.0.0.1:10806 -X POST \
  https://api.telegram.org/bot6187967109:***/sendMessage \
  -d chat_id=737433175 -d text="test"
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `getMe 404 Not Found` | Wrong token — must use `MCDUCK_BOT_TOKEN` from `.env` |
| `httpx ConnectTimeout` on telegram_api | Gateway needs `socks5://127.0.0.1:10806` proxy |
| Bot doesn't respond | Check worker thread alive; check `process_with_hermes` logs |
| `ModuleNotFoundError: socks` | `pip install PySocks` |
| Only `/report` works | Free text not hitting `process_with_hermes` — check queue |

## Files
- `scripts/mcduck_bot.py` — Main bot (203 lines)
- `scripts/llm_client.py` — LLM pipeline (OpenRouter/Cerebras/DeepSeek fallback)
- `scripts/hermes_hooks.py` — Event tracking
- `scripts/kc_rag.py` — Knowledge Cube RAG
- `.env` — Contains `MCDUCK_BOT_TOKEN=6187967109:***`