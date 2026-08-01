# LLM Provider Status (Hermes Machine — 2026-07-09)

Tested from `D:\Portable_Soft\hermes` on Windows 11.

## Working

### Cerebras (`api.cerebras.ai`)
- **Key env var:** `CEREBRAS_API_KEY` (52 chars, `csk-...`)
- **HTTP client:** `httpx.Client(verify=False, proxy=None)`
- **Available models:** `gemma-4-31b`, `gpt-oss-120b`, `zai-glm-4.7`
- **Note:** Model names are NOT the standard OpenAI-style names. Check `/v1/models` endpoint.
- **litellm model string:** `cerebras/gemma-4-31b` (but may need custom base_url)

## Partially Working

### DeepSeek (`api.deepseek.com`)
- **Key env var:** `DEEPSEEK_API_KEY` (35 chars, `sk-...`)
- **Status:** 402 "Insufficient Balance" — key is valid, account needs top-up
- **Models:** `deepseek-chat`, `deepseek-reasoner`

### OpenRouter (`openrouter.ai`)
- **Key env var:** `OPENROUTER_API_KEY` (73 chars, `sk-or-v1-...`)
- **Status:** Free models return 404 "No allowed providers are available"
- **Root cause:** Network/region restriction — free model providers are geo-blocked
- **Paid models:** May work but untested (no credits)

## Not Working

### Groq (`api.groq.com`)
- **Status:** 403 "Access denied. Please check your network settings."
- **Root cause:** Region/IP block

### OpenGateway (`api.opengateway.ai`)
- **Status:** SSL handshake timeout even with httpx verify=False
- **Root cause:** Different SSL termination behavior

## Local Servers

### DeepSeek local (localhost:9655)
- **Status:** Not running
- **Note:** Was previously configured but server is down

## Unified LLM Client

Created at `scripts/llm_client.py`:
- `call_llm()` — text completion with fallback chain
- `call_structured()` — instructor + Pydantic guaranteed output
- `call_json()` — JSON extraction from LLM responses
- Provider chain: Cerebras → DeepSeek → OpenRouter (auto-fallback)
- All calls use httpx with verify=False due to Windows SSL issue
