---
name: provider-model-management
description: "Central registry for LLM providers and models — model_registry.py pattern. Eliminates hardcoded provider URLs, model names, and API keys across scripts."
version: 1.1.0
author: Hermes
tags: [providers, models, registry, architecture, llm, configuration, model-registry]
---

# Provider & Model Registry Management

## Overview

A proven architectural pattern: one central registry (`model_registry.py`) owns all provider configs and model lists. Every script calls `get_working_model()` instead of hardcoding URLs or model names.

**Why this exists**: Hardcoding `http://localhost:1234` and `qwen3.5-4b` in every script is fragile. Adding a new provider means editing N files. The registry pattern flips this: add the provider in one place, every script picks it up automatically.

## Architecture

```
model_registry.py              ← single source of truth
  ├── PROVIDERS dict           ← all known providers + their models
  ├── ping_all()               ← parallel health check (6s max)
  ├── get_working_model()      ← best alive model by tags
  ├── get_model_config()       ← specific model lookup
  └── list_available()         ← full status table

scripts/jarvis_voice_loop.py   ← consumer: calls get_working_model()
scripts/jarvis_security_monitor.py ← consumer: calls ping_all()
...any future script           ← consumer: same API
```

## Adding a New Provider

Edit `PROVIDERS` dict in `scripts/model_registry.py`:

```python
PROVIDERS["my-provider"] = {
    "name": "My Provider Name",
    "type": "api",              # api | proxy | local
    "base_url": "http://localhost:9999/v1",
    "api_key": "not-needed",    # or real key
    "models": {
        "model-name": {
            "priority": 1,      # lower = preferred
            "tags": ["chat", "fast", "free", "local", "code"],
        },
    },
    "chat_endpoint": "/chat/completions",
    "ping_endpoint": "/models",
    "openai_compat": True,
}
```

No script changes needed — `get_working_model()` picks up new providers automatically on next ping.

## Consumer Pattern (for any script)

```python
from model_registry import get_working_model

def resolve_llm():
    """Get the best alive LLM config for this task."""
    # Preferences cascade:
    config = get_working_model(tags=["chat", "fast", "local"])
    if not config:
        config = get_working_model(tags=["chat"])
    if not config:
        # Fallback: known default
        config = {
            "provider": "lm-studio",
            "model": "qwen3.5-4b",
            "base_url": "http://localhost:1234/v1",
            "endpoint": "http://localhost:1234/v1/chat/completions",
            "api_key": "not-needed",
        }
    return config
```

## Recent Model Updates (2026-06-27)

New models/providers detected via self-upgrade signals:

### OpenAI GPT-5.6 Sol (June 26, 2026)
- Next-generation model, system card released
- Tags: `chat`, `reasoning`
- Cost: Check OpenAI pricing page
- Status: Preview/testing phase

### DeepSeek V4-Pro (June 2026)
- **75% price cut** — now very cheap API
- Tags: `chat`, `code`, `fast`, `cheap`
- Good candidate for code generation tasks

### DeepSeek V4-Flash-Free (current default)
- **Active default model** — used in this session via opencode-zen provider
- Free tier, fast inference
- Tags: `chat`, `fast`, `free`

### Anthropic Claude Fable 5 & Mythos 5 (June 9, 2026)
- New Claude variants
- Tags: `chat`, `reasoning`, `code`
- Claude Tag: team collaboration via Slack @Claude
- Claude Gov: US government security-cleared variant

### Google Gemini Operating Layer (I/O 2026, May)
- Gemini evolving from chatbot to agentic system
- Tags: `chat`, `agents`, `multimodal`, `video`
- Omni mode for video understanding

### User Action Items
- Try DeepSeek V4-Pro for codegen (cheap after 75% cut)
- Monitor GPT-5.6 Sol availability
- Evaluate Claude Tag if working in teams with Claude

## Tag System

Tags filter models by capability:

| Tag | Meaning |
|-----|---------|
| `chat` | General conversation |
| `fast` | Low latency (preferred for voice) |
| `free` | No API cost |
| `local` | Runs on this machine (offline-capable) |
| `code` | Optimised for code generation |
| `reasoning` | Chain-of-thought / reasoning models |
## Parallel Ping

`ping_all()` pings all providers **simultaneously** (threading, max 6s total). Results cache
for 15 seconds. Each provider's ping type is auto-selected:

| `ping_endpoint` value | Ping type | Example |
|---|---|---|
| HTTP path (e.g. `/models`) | HTTP GET with 5s timeout, checks 200 | LM Studio, DeepSeek proxy |
| `None` (set explicitly) | TCP port connect | Gateway (no models endpoint) |
| empty string `""` | TCP port connect | Qwen proxy |
| `None` + no base_url + no api_key | DEAD — not configured | Unconfigured provider (gateway removed/disabled) |
| `None` + no base_url + has api_key | Assumed alive (no check) | opencode_zen with key but no URL (legacy path) |

## Migration: Hardcoded → Registry

1. Add `sys.path` to reach `scripts/` in the consumer script
2. Replace hardcoded `llm_url`, `llm_model`, `api_key` with `get_working_model()` call
3. Pass the returned config dict to the LLM client class
4. The LLM client reads `endpoint`, `model`, `api_key` from the config

## Pitfalls

- **CHECK WHAT'S ALREADY INSTALLED FIRST.** Before suggesting new providers or models, verify what's already configured in `config.yaml` and what services are running. The user has FreeQwenApi, FreeDeepseekAPI, Ollama, and LM Studio already installed. Don't suggest adding things that are already there — check ports (`netstat -ano | grep PORT`), check config, then act.
- **FREE MODELS ONLY.** User does NOT use paid APIs. All model recommendations must be free: opencode-zen, Ollama, FreeQwenApi, FreeDeepseekAPI, Google AI Studio (free tier), Groq (free tier). Never suggest paid options. DeepSeek free is 5M tokens one-time, not sustainable.
- **When user says "switch to X provider" — RESEARCH X FIRST.** Do NOT assume X matches
  an existing provider ID in the registry. The user may be referring to a completely
  different service (e.g., "zen" meant OpenCode Zen at opencode.ai/zen/v1, not the
  opencode_zen gateway entry). Web search the user's term before changing anything.
- **"Disabled" means disabled forever until the user says otherwise.** Never re-enable
  a provider the user explicitly told you to disable.
- **`ping_all(force=True)` blocks up to 6s** — use `force=False` (cached) for frequent checks
- **First call after script start always pings** (cache empty)
- **Provider with no ping_endpoint** only gets TCP port check
- **API keys**: store in `PROVIDERS` definition; the key `not-needed` or `dummy-key` skips Authorization header
- **Model not loaded (LM Studio)**: `/v1/models` responds 200 even with no loaded model — inference will fail with "No models loaded" error. The registry only checks if the API is reachable, not if inference works.
- **`base_url` and `api_key` both empty/None**: `_ping_provider()` returns DEAD ("not configured"). This prevents unconfigured providers (e.g., a gateway with URL and key removed) from being selected ahead of properly configured ones. Previously these were assumed alive, causing silent failures where every API call returned 400/402.
