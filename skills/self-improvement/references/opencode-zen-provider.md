# OpenCode Zen Provider

## Status: ✅ WORKING

The system's configured LLM provider. Used for all LLM operations.

## Config
```yaml
# In config.yaml
model:
  provider: opencode_zen
  
# In .env
OPENCODE_ZEN_API_KEY=***  # exists, redacted
```

## Works For

- **Current session** — all real-time agent interactions
- **Simple cron prompts** (no tools) — e.g. "Say hello in 3 words"
- **Self-evolution plugin** — DSPy pipelines

## Does NOT Work For

- **Tool-calling cron jobs** (session_search, read_file, web_search) — times out at ~25-30s
- **Model `gpt-4o`** — returns `ModelError: Model gpt-4o is not supported`

## Working Cron Model

```
provider: opencode_zen
model: deepseek-v4-flash-free
```

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| `Model gpt-4o is not supported` | Job uses default model (gpt-4o) | Set model=deepseek-v4-flash-free explicitly |
| `Invalid API response after 3 retries: response time 30.2s` | Prompt calls tools in cron | Convert to no_agent + script |
| `401 ...` | API key missing | OPENCODE_ZEN_API_KEY must be in .env |

## CRITICAL: reasoning_content Field (Discovered 2026-06-09)

OpenCode Zen returns `reasoning_content` instead of `content` for deepseek models:

```json
{"choices": [{"message": {"content": "", "reasoning_content": "actual response..."}}]}
```

**Correct extraction pattern:**
```python
msg = r.json()["choices"][0]["message"]
return msg.get("content") or msg.get("reasoning_content") or msg.get("reasoning") or ""
```

This affects ALL scripts: knowledge_gap_filler, uncertainty_observer, llm_analyst, etc.

## Comparison: OpenRouter vs OpenCode Zen

| Aspect | OpenRouter | OpenCode Zen |
|---|---|---|
| Status | ❌ NO CREDITS (402) | ✅ WORKING |
| Free? | Tiered (free models exist) | Free |
| Cron-ready? | ❌ | ✅ (simple prompts) |
| Tool-calling in cron? | ❌ (same timeout) | ❌ (same timeout) |
| Model | meta-llama/llama-3.1-8b-instruct | deepseek-v4-flash-free |
