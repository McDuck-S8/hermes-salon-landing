# FreeLLMAPI — Free LLM Aggregator

## What

OpenAI-compatible proxy that stacks free tiers from 14 AI providers behind one endpoint.
~1.3 billion tokens/month, zero cost. MIT license, 5800+ stars (May 2026).

GitHub: https://github.com/tashfeenahmed/freellmapi

## Providers

| Provider | Key Models | Free Tier |
|----------|-----------|-----------|
| Google | Gemini 2.5 Flash/Pro, 3.x previews | High |
| Groq | Llama 3.3, Llama 4, Qwen3 | Medium |
| Cerebras | Qwen3 235B | Medium |
| SambaNova | DeepSeek V3, Llama 4, Gemma 3 | Medium |
| Mistral | Large 3, Medium 3.5, Codestral, Devstral | Medium |
| OpenRouter | 21 free-tier models | Varies |
| GitHub Models | GPT-4.1, GPT-4o | Low (experimentation) |
| Cloudflare | Kimi K2, GLM-4.7, Granite 4 | Medium |
| Cohere | Command R+, Command-A (trial) | Low |
| Z.ai (Zhipu) | GLM-4.5, GLM-4.7 Flash | Medium |
| HuggingFace | DeepSeek V4, Kimi K2.6, Qwen3 | Medium |
| NVIDIA | NIM (disabled by default) | Trial only |

## How It Works

- Single `POST /v1/chat/completions` endpoint (OpenAI-compatible)
- Automatic failover: 429/5xx → cooldown → next provider
- Per-key rate tracking (RPM/RPD/TPM/TPD)
- Sticky sessions: multi-turn stays on same model for 30 min
- AES-256-GCM encrypted key storage
- Tool calling supported (translated for Gemini)
- Admin dashboard (React + Vite)

## Quick Start

```bash
git clone https://github.com/tashfeenahmed/freellmapi.git
cd freellmapi
npm install
cp .env.example .env
echo "ENCRYPTION_KEY=$(node -e "console.log(require('crypto').randomBytes(32).toString('hex'))")" >> .env
npm run dev
# Dashboard: http://localhost:5173
# API: http://localhost:3001/v1
```

## Usage with Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:3001/v1",
    api_key="freellmapi-your-unified-key",
)

resp = client.chat.completions.create(
    model="auto",  # router picks best available
    messages=[{"role": "user", "content": "Hello!"}],
)
```

## Relevance for Business

1. **Zero-cost LLM for bots** — hotel/salon bots can use free models for AI features
2. **No API key management** — one unified key, router handles provider selection
3. **Failover built-in** — if Gemini hits limit, falls to Groq/Cerebras automatically
4. **Hermes integration** — can be set as custom provider in Hermes config
5. **Client demos** — show clients AI features without explaining API costs

## Limitations

- No frontier models (GPT-5, Claude Opus)
- Intelligence degrades late in day (top models hit daily caps)
- Latency varies (Cerebras/Groq fast, others not)
- Free tiers can change without notice
- Text only — no vision, audio, embeddings, images
- Single-user, local-only (don't expose to internet)

## ToS Summary (May 2026)

- ✅ OK: Groq, Cerebras, Mistral, OpenRouter, Zhipu, Ollama Cloud
- ⚠️ Caution: Google, NVIDIA, GitHub Models, SambaNova, Cloudflare, Z.ai
- ❌ Avoid: Cohere (forbids personal/household use)
