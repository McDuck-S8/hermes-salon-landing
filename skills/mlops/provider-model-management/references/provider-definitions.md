# Provider Definitions — as of 2026-06-28 (v1.2)

This file mirrors the PROVIDERS dict from model_registry.py for reference.
When adding/editing providers, edit model_registry.py, then update this file.

## Provider Sort Order

Models are sorted by: **priority** (lower first) → **cloud before local** → **latency** (lower first).
This means: if a gateway (cloud) provider is alive at low latency, it's preferred over a local
LM Studio model. Local models serve as fallback when cloud providers are unreachable.

## opencode_zen (Gateway) — PRIMARY

Primary provider — routes through Hermes gateway. Ping via TCP (no `/models` endpoint).

```python
"opencode_zen": {
    "name": "OpenCode Zen (Gateway)",
    "type": "api",
    "base_url": None,  # read from Hermes config at runtime
    "api_key": None,   # read from Hermes config
    "models": {
        "deepseek-v4-flash-free": {"priority": 1, "tags": ["chat", "fast", "free"]},
        "mimo-v2.5-free":         {"priority": 2, "tags": ["chat", "free"]},
        "nemotron-3-ultra-free":  {"priority": 3, "tags": ["chat", "free"]},
        "qwen3.6-plus":           {"priority": 4, "tags": ["chat"]},
        "qwen3.5-plus":           {"priority": 5, "tags": ["chat"]},
    },
    "chat_endpoint": "/chat/completions",
    "ping_endpoint": None,  # TCP ping only — gateway has no /models
    "openai_compat": True,
}
```

For opencode_zen, base_url is read dynamically from Hermes config.yaml (model.base_url).
Ping: TCP connection check to the gateway host:port (typically port 443).

## qwen-free (Local Proxy)

Free Qwen API proxy running locally.

```python
"qwen-free": {
    "name": "Qwen Free Proxy",
    "type": "proxy",
    "base_url": "http://localhost:3264/api",
    "api_key": "dummy-key",
    "models": {"qwen3.7-max": {"priority": 1, "tags": ["chat", "free"]}},
    "chat_endpoint": "",
    "ping_endpoint": "",
    "openai_compat": False,
}
```

Ping: TCP port check only (no HTTP endpoint). Only marked alive if port 3264 accepts connections.

## deepseek-free (Local Proxy)

```python
"deepseek-free": {
    "name": "DeepSeek Free Proxy",
    "type": "proxy",
    "base_url": "http://localhost:9655/v1",
    "api_key": "dummy-key",
    "models": {"deepseek-chat": {"priority": 1, "tags": ["chat", "fast", "free"]}},
    "chat_endpoint": "/chat/completions",
    "ping_endpoint": "/models",
    "openai_compat": True,
}
```

## deepseek-free-reasoner (Local Proxy)

```python
"deepseek-free-reasoner": {
    "name": "DeepSeek Reasoner Proxy",
    "type": "proxy",
    "base_url": "http://localhost:9655/v1",
    "api_key": "dummy-key",
    "models": {"deepseek-reasoner": {"priority": 1, "tags": ["chat", "reasoning", "free"]}},
    "chat_endpoint": "/chat/completions",
    "ping_endpoint": "/models",
    "openai_compat": True,
}
```

## lm-studio (Local)

Runs entirely on this machine, no internet needed. OpenAI-compatible API.

```python
"lm-studio": {
    "name": "LM Studio (Local)",
    "type": "local",
    "base_url": "http://localhost:1234/v1",
    "api_key": "not-needed",
    "models": {
        "qwen3.5-4b":                     {"priority": 1,  "tags": ["chat", "fast", "local"]},
        "gemma-3-4b":                     {"priority": 2,  "tags": ["chat", "local"]},
        "ministral-3-3b":                 {"priority": 3,  "tags": ["chat", "fast", "local"]},
        "qwen3-coder-30b-a3b-instruct":   {"priority": 4,  "tags": ["code", "local"]},
        "qwen3.6-35b-a3b-mtp-mixed-q8":  {"priority": 5,  "tags": ["chat", "local"]},
        "llama-3.2-1b":                   {"priority": 10, "tags": ["chat", "fast", "local"]},
    },
    "chat_endpoint": "/chat/completions",
    "ping_endpoint": "/models",
    "openai_compat": True,
}
```

Notes:
- LM Studio must have a model *loaded* (via UI) before inference works
- /v1/models endpoint responds even without a loaded model
- Inference fails with "No models loaded" error if no model loaded

---

## NEW: LiteLLM Proxy (Unified Gateway) — 2026-06-28

**LiteLLM** runs as a local proxy on `http://localhost:4000/v1` — unified OpenAI-compatible endpoint for 19 models across 6 tiers.

```python
"litellm-proxy": {
    "name": "LiteLLM Proxy (Local Gateway)",
    "type": "proxy",
    "base_url": "http://localhost:4000/v1",
    "api_key": "not-needed",
    "models": {
        # TIER 1: Generous Free Tiers (No Credit Card)
        "gemini-2.5-flash":      {"priority": 1, "tags": ["chat", "fast", "free", "cloud"]},
        "gemini-2.5-pro":        {"priority": 2, "tags": ["chat", "reasoning", "free", "cloud"]},
        "mistral-large":         {"priority": 3, "tags": ["chat", "code", "free", "cloud"]},
        "mistral-small":         {"priority": 4, "tags": ["chat", "fast", "free", "cloud"]},
        "deepseek-v3":           {"priority": 5, "tags": ["chat", "fast", "free", "cloud"]},
        "deepseek-r1":           {"priority": 6, "tags": ["reasoning", "free", "cloud"]},
        # TIER 2: Sign-up Credits ($$ value)
        "grok-3":                {"priority": 7, "tags": ["chat", "creative", "credits", "cloud"]},
        "grok-4":                {"priority": 8, "tags": ["chat", "reasoning", "credits", "cloud"]},
        "claude-3-5-haiku":      {"priority": 9, "tags": ["chat", "fast", "credits", "cloud"]},
        "claude-sonnet-4":       {"priority": 10, "tags": ["chat", "reasoning", "credits", "cloud"]},
        "gpt-4o-mini":           {"priority": 11, "tags": ["chat", "fast", "credits", "cloud"]},
        # TIER 3: Together AI ($100 credit)
        "llama-3.3-70b":         {"priority": 12, "tags": ["chat", "code", "credits", "cloud"]},
        "qwen-2.5-72b":          {"priority": 13, "tags": ["chat", "credits", "cloud"]},
        "nemotron-3-ultra":      {"priority": 14, "tags": ["chat", "reasoning", "credits", "cloud"]},
        # TIER 4: OpenRouter
        "openrouter-auto":       {"priority": 15, "tags": ["chat", "free", "cloud"]},
        # TIER 5: Cloudflare Workers AI
        "cf-llama-3.1-8b":       {"priority": 16, "tags": ["chat", "fast", "free", "edge"]},
        # TIER 6: GitHub Models
        "github-gpt-4o":         {"priority": 17, "tags": ["chat", "code", "free", "cloud"]},
    },
    "chat_endpoint": "/chat/completions",
    "ping_endpoint": "/models",
    "openai_compat": True,
}
```

**Config file:** `D:/Portable_Soft/hermes/litellm_config.yaml`
**Run:** `litellm --config D:/Portable_Soft/hermes/litellm_config.yaml --port 4000`

### Free AI API Stack 2026 (Sign-up Credits Available)

| Provider | Free Tier | Signup Credits | Startup Program |
|----------|-----------|----------------|-----------------|
| **Google Gemini** | Unlimited, 15 RPM (Flash) | $300 (GCP) | $1K-25K |
| **xAI Grok** | $25 + $150/mo (opt-in) | $25 + $150/mo | Variable |
| **Mistral** | Unlimited, rate-limited | None | Available |
| **DeepSeek** | Rate-limited V3/R1 | None | None (already cheap) |
| **Together AI** | Trial | $100 | $15K-50K |
| **OpenRouter** | Rotating free models | None | - |
| **Hugging Face** | Small models free | None | - |
| **GitHub Models** | In IDE | None | - |
| **Cloudflare Workers AI** | Edge free allowance | None | - |
| **Cerebras** | Rate-limited | None | Available |

**Solo Dev Stack (immediate): $335+ credits in 30 min**
- Anthropic + OpenAI $5 trials = $10
- xAI Grok = $25 + $150/mo
- Google Cloud = $300
- Unlimited: Mistral, DeepSeek, Gemini

**Startup Stack (application): $19K-251K+**
- Anthropic: $1K-25K
- OpenAI: $500-50K
- AWS Activate: $1K-100K (includes Claude via Bedrock)
- Google Cloud: $1K-25K (Vertex AI multi-model)
- Together AI: $15K-50K
- Microsoft Founders Hub: $500-1K

---

## NEW: FreeModel (freemodel.dev) — 2026-06-28

```python
"freemodel": {
    "name": "FreeModel (Anthropic-compatible)",
    "type": "api",
    "base_url": "https://cc.freemodel.dev",
    "api_key": "fe_oa_25ca47faa9970f33c1707692fd55fbb8f72bca1525c38d3c",
    "models": {
        "claude-haiku-4-5-20251001": {"priority": 1, "tags": ["chat", "fast", "free"]},
        "claude-sonnet-4-6":         {"priority": 2, "tags": ["chat", "reasoning", "free"]},
        "claude-opus-4-6":           {"priority": 3, "tags": ["chat", "reasoning", "free"]},
        "claude-opus-4-7":           {"priority": 4, "tags": ["chat", "reasoning", "free"]},
        "claude-opus-4-8":           {"priority": 5, "tags": ["chat", "reasoning", "free"]},
        "claude-fable-5":            {"priority": 6, "tags": ["chat", "reasoning", "free"]},
    },
    "chat_endpoint": "/v1/messages",
    "ping_endpoint": "/v1/models",
    "openai_compat": False,  # Anthropic format
    "headers": {"anthropic-version": "2023-06-01"},
}
```

**Status:** ✅ Key valid (200 on /v1/models), ❌ 503 "Account pool empty: no ready account" — shared pool exhausted.

---

## Model Priorities

Lower priority number = higher preference. The registry sorts by:
1. priority (lower first)
2. is_local (cloud before local — gateways preferred as primary)
3. latency_ms (faster preferred)
4. (fallback: first match wins)

## Tags

- `chat` — general conversation
- `fast` — low latency (<3s per response)
- `free` — no API cost
- `local` — runs on this machine (works offline)
- `code` — coding tasks
- `reasoning` — chain-of-thought / deep reasoning
- `credits` — uses signup credits (limited duration)
- `cloud` — requires internet
- `edge` — runs on Cloudflare edge

## Pitfalls

- **CHECK WHAT'S ALREADY INSTALLED FIRST.** Before suggesting new providers or models, verify what's already configured in `config.yaml` and what services are running. The user has FreeQwenApi, FreeDeepseekAPI, Ollama, and LM Studio already installed. Don't suggest adding things that are already there — check ports (`netstat -ano | grep PORT`), check config, then act.
- **FREE MODELS ONLY.** User does NOT use paid APIs. All model recommendations must be free: opencode-zen, Ollama, FreeQwenApi, FreeDeepseekAPI, Google AI Studio (free tier), Groq (free tier). Never suggest paid options. DeepSeek free is 5M tokens one-time, not sustainable.
- **When user says "switch to X provider" — RESEARCH X FIRST.** Do NOT assume X matches an existing provider ID in the registry. The user may be referring to a completely different service (e.g., "zen" meant OpenCode Zen at opencode.ai/zen/v1, not the opencode_zen gateway entry). Web search the user's term before changing anything.
- **"Disabled" means disabled forever until the user says otherwise.** Never re-enable a provider the user explicitly told you to disable.
- **`ping_all(force=True)` blocks up to 6s** — use `force=False` (cached) for frequent checks
- **First call after script start always pings** (cache empty)
- **Provider with no ping_endpoint** only gets TCP port check
- **API keys**: store in `PROVIDERS` definition; the key `not-needed` or `dummy-key` skips Authorization header
- **Model not loaded (LM Studio)**: `/v1/models` responds 200 even with no loaded model — inference will fail with "No models loaded" error. The registry only checks if the API is reachable, not if inference works.
- **`base_url` and `api_key` both empty/None**: `_ping_provider()` returns DEAD ("not configured"). This prevents unconfigured providers (e.g., a gateway with URL and key removed) from being selected ahead of properly configured ones. Previously these were assumed alive, causing silent failures where every API call returned 400/402.
- **LiteLLM proxy requires all API keys as env vars** — keys not stored in config.yaml, loaded from environment at runtime
- **FreeModel pool empty** — shared free pool may be exhausted, retry later or use other providers