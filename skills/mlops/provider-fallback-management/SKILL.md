---
name: provider-fallback-management
category: mlops
description: >-
  Automatic and manual provider fallback for Hermes when the primary LLM provider
  hits rate limits, timeouts, or API errors. Includes switch_provider.py for manual
  switching, provider_guard.py for auto-detection, and cron-based monitoring.
tags: [provider, fallback, switch, rate-limit, auto-recovery, hermes-config]
---

# Provider Fallback Management

## Overview

Hermes supports multiple LLM providers in `config.yaml`. When the active provider
hits rate limits (429), timeouts, or persistent API errors, two scripts handle
switching:

- **`scripts/switch_provider.py`** — manual switch by name
- **`scripts/provider_guard.py`** — auto-detects errors and chains through fallbacks

## Provider Revolver (Within-Provider Rotation)

**Проблема:** Один провайдер (opencode-zen) даёт несколько free моделей, но при rate limit на одной — система падает, хотя другие free модели того же провайдера работают.

**Решение:** Revolver — крутить free модели одного провайдера по кругу.

```yaml
# config.yaml — гипотетическая структура
model:
  provider: opencode_zen
  revolver: [deepseek-v4-flash-free, deepseek-v3-free, deepseek-r1-free]
  default: deepseek-v4-flash-free
```

**Когда применять:**
- Текущий провайдер (opencode-zen) имеет несколько free моделей
- Rate limit (429) на одной модели → переключиться на следующую в револьвере
- **Автокомпрессия контекста должна использовать ДРУГУЮ модель из револьвера, не основную** — чтобы не создавать rate limit на основной модели

**Разница между revolver и fallback:**
- **Fallback** (существующий): между разными провайдерами (opencode_zen → deepseek → qwen)
- **Revolver** (новый): между моделями ОДНОГО провайдера (deepseek-v4 → deepseek-v3 → deepseek-r1)

**Pitfall:** Не реализовано в коде (2026-07-27). Только концепт. Нужно расширить provider_guard.py
или switch_provider.py поддержкой rotate-to-next-model для одного провайдера.

## Available Providers (from .env API keys)

| Name | Model | Base URL | Env Key | Status (2026-07-09) |
|------|-------|----------|---------|---------------------|
| `cerebras` | gemma-4-31b | api.cerebras.ai/v1 | CEREBRAS_API_KEY | ✅ Primary (cloud) |
| `deepseek-local` | deepseek-chat | localhost:9655/v1 | _LOCAL_DEEPSEEK | ✅ Local FreeDeepseekAPI |
| `deepseek` | deepseek-chat | api.deepseek.com/v1 | DEEPSEEK_API_KEY | ❌ 402 Insufficient Balance |
| `groq` | llama-3.3-70b-versatile | api.groq.com/openai/v1 | GROQ_API_KEY | ❌ 403 Region blocked |
| `openrouter` | openai/gpt-4o-mini | openrouter.ai/api/v1 | OPENROUTER_API_KEY | ❌ 404 No providers |
| `opengateway` | meta-llama/llama-3.3-70b-instruct | api.opengateway.ai/v1 | OPENGATEWAY_API_KEY | ❌ SSL error |

### DeepSeek Local (FreeDeepseekAPI) — Second Working Provider

`deepseek-local` connects to FreeDeepseekAPI on `localhost:9655`. This is a
browser-session proxy for DeepSeek Web Chat — no API key needed (uses saved
browser auth tokens from `deepseek-auth.json`).

**Starting the server:**
```bash
cd D:/Portable_Soft/FreeDeepseekAPI
# Must use pty=true for Node.js readline menu:
# terminal(background=true, pty=true) → submit "3" to start proxy
```

**Available models:** deepseek-chat, deepseek-v3, deepseek-reasoner, deepseek-r1,
deepseek-chat-search, deepseek-expert, deepseek-v4-pro (11 models total).

**In llm_client.py:** `deepseek-local` is always included in the provider chain
(it uses `_LOCAL_DEEPSEEK` sentinel key, not a real API key). Falls back to
it when Cerebras fails.

### Critical: Windows SSL Workaround
Standard `aiohttp` (used by litellm) and `requests` fail with SSL errors on this
Windows machine. **httpx with `verify=False, proxy=None` is the only working transport.**
This is configured in `scripts/llm_client.py` via `_get_httpx()`.

litellm's import also requires aiohttp to be fully installed (namespace package
corruption — missing `__init__.py` — seen on 2026-07-09). Fix: `rm -rf aiohttp && pip install aiohttp`.

## switch_provider.py — Manual

```bash
python scripts/switch_provider.py status              # current provider + model
python scripts/switch_provider.py deepseek-free        # switch to DeepSeek free
python scripts/switch_provider.py qwen-free            # switch to Qwen free
python scripts/switch_provider.py opencode_zen         # switch back to primary
```

Edits `model.provider` and `model.default` in `config.yaml`. Changes take effect
after `/reset` (new session).

## provider_guard.py — Auto-Fallback

```bash
python scripts/provider_guard.py          # single check (for cron)
python scripts/provider_guard.py --status  # current state
```

**How it works:**
1. Scans logs under `logs/` for rate_limit/429/timeout errors in the last 5 minutes
2. If 3+ errors detected, advances through the fallback chain:
   `opencode_zen → deepseek-free → qwen-free → deepseek-free-reasoner`
3. After 1 hour without errors on a fallback, returns to `opencode_zen`
4. State persisted in `cache/provider_guard_state.json`

**Pitfalls:**
- Log files may contain errors from OTHER providers or processes (title generator,
  gateway, failed experiments). provider_guard counts ALL rate_limit entries, so
  a non-primary provider's errors can trigger a false switch.
- Fastest false-positive fix: refine `check_recent_errors()` to filter by provider
  name in the log line.

## Provider Test Script

See `references/2026-07-09-provider-connectivity-test.py` — standalone script
that tests all configured providers. Run with `python references/2026-07-09-provider-connectivity-test.py`.

The live version is at `scripts/test_providers.py` (same logic, more detail in output).

## Cron Integration

A recurring cron job runs provider_guard every 5 minutes:

```bash
hermes cron create "*/5 * * * *" --script scripts/provider_guard.py
```

Created via cronjob tool with:
- action='create', schedule='*/5 * * * *', script='scripts/provider_guard.py'
- The script's stdout is injected into the cron agent's prompt
- If errors detected, the agent reports them and auto-switches

## Manual Switch Commands

For quick switching during a conversation, use:

```bash
python /absolute/path/to/hermes/scripts/switch_provider.py <name>
```

### Bash Aliases (Windows git-bash / Linux)

Added to `~/.bashrc` for one-word switching:

| Alias | Action |
|-------|--------|
| `hermes-deepseek` | Switch to deepseek-free |
| `hermes-deepseek-reasoner` | Switch to deepseek-free-reasoner |
| `hermes-qwen` | Switch to qwen-free |
| `hermes-opencode` | Return to opencode_zen |
| `hermes-provider` | Show current provider + model |

```bash
# Install by adding to ~/.bashrc:
alias hermes-deepseek='cd /path/to/hermes && python scripts/switch_provider.py deepseek-free'
alias hermes-deepseek-reasoner='cd /path/to/hermes && python scripts/switch_provider.py deepseek-free-reasoner'
alias hermes-qwen='cd /path/to/hermes && python scripts/switch_provider.py qwen-free'
alias hermes-opencode='cd /path/to/hermes && python scripts/switch_provider.py opencode_zen'
alias hermes-provider='cd /path/to/hermes && python scripts/switch_provider.py status'
```

Then `/reset` to start a new session with the new provider.

## Config Structure

```yaml
# config.yaml — what gets edited
model:
  default: deepseek-v4-flash-free    # model name
  provider: opencode_zen             # provider key from config
```

Each provider entry has its own `base_url` and optional `api_key` defined
elsewhere in the same config.

## Relationship to model_registry.py

- `model_registry.py` (covered by `provider-model-management` skill) routes LLM
  calls from **internal scripts** (voice loop, security monitor, etc.) to working
  providers using a ping-based registry.
- `switch_provider.py` + `provider_guard.py` change **Hermes' own config** — the
  provider you're chatting with.
- Both can coexist: model_registry handles script-level fallback; provider_guard
  handles conversation-level fallback.

## OpenRouter + openai SDK Routing Issue

When calling OpenRouter via the `openai` Python SDK (v1.x), requests fail with
404 "No allowed providers are available" even with a valid key. This is caused
by `x-stainless-*` headers the SDK sends — OpenRouter uses them for provider
routing, and the route group may not include providers that host the model.

**Workaround: Use model provider's direct API instead of OpenRouter.**

See `references/openrouter-openai-sdk-routing.md` for full diagnosis, affected
models, and tested working alternatives (Mistral API direct works reliably).

## User Preference

When the user says "далее" = DO THE NEXT THING, not analyze. If a provider switch
is pending (rate_limit detected), switch immediately without asking. The scripts
exist — use them.
