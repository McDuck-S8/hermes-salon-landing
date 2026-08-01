---
name: token-compression
description: Compress LLM tool outputs (JSON, code, logs) to save 50-88% tokens. Zero-dependency Python. Use when tool outputs are large, token costs matter, or context window is tight.
tags: [cost-optimization, tokens, compression, llm, zero-dependency]
related_skills: [action-over-documentation]
---

# Token Compression

## Core Rule

Compress large tool outputs BEFORE they enter LLM context. Every token costs money. 50-88% savings are routine.

## When to Use

- Tool output > 500 tokens (JSON dumps, log files, code blocks)
- Context window approaching limit
- Cost optimization needed
- Repeated/similar outputs in conversation

## Zero-Dependency Compressor

Location: `D:/Portable_Soft/hermes/tools/simple_compress.py`

```python
import sys
sys.path.insert(0, "D:/Portable_Soft/hermes/tools")
from simple_compress import compress, estimate_tokens

# Single text
result = compress(large_json_string)
print(f"Saved: {result.tokens_before - result.tokens_after} tokens")

# Auto-detect content type
from hermes_compress import compress_for_llm
compressed = compress_for_llm(tool_output)

# Auto-mode (only compresses if > 500 tokens)
from auto_compress import auto_compress_output
compressed = auto_compress_output(raw_output)
```

## Compression Strategies by Type

### JSON (88% savings typical)
- Preserve keys (navigational — LLM needs schema)
- Compress long string values: `"description": "long text..." → "description": "first 30 chars...[200 chars]"`
- Compress long arrays: `[item1, item2, ...50 items]`
- Keep booleans, nulls, short numbers

### Code (59% savings typical)
- Remove comments (`#`, `//`, `/* */`)
- Remove docstrings (`"""..."""`)
- Remove empty lines
- Keep actual code

### Logs (56% savings typical)
- Remove timestamps (redundant for LLM)
- Deduplicate repeated lines
- Keep error messages and key events

### Text (20-30% savings)
- Remove excess whitespace
- No semantic compression (risky)

## Integration Points

### In agent loop (before LLM call):
```python
from auto_compress import auto_compress
messages = auto_compress(messages)  # compresses tool messages automatically
```

### In hooks (before storing):
```python
from hermes_compress import compress_tool_output
result = compress_tool_output(huge_output)
```

## Pitfalls

### Don't compress system messages
System prompts are small and critical — never compress them.

### Don't compress user messages
User input is sacred — never modify it.

### Don't over-compress
If output is < 500 tokens, the overhead of compression isn't worth it. Check `should_compress()` first.

### Headroom — production-grade context compression (59.4k★)

[headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom) achieves 60-95% fewer tokens (JSON) / 15-20% (code) with content-aware compressors:
- **SmartCrusher** (JSON), **CodeCompressor** (AST), **Kompress-v2-base** (ML text)
- **Modes**: Python/TS library, `headroom proxy` (zero code changes), MCP server, `headroom wrap <agent>`
- **Reversible (CCR)**: originals cached locally, LLM retrieves on demand
- **Output token reduction**: also trims what the model writes back (not just input)
- **Cross-agent memory**: shared store across Claude, Codex, Gemini, Grok
- **`headroom learn`**: mines failed sessions, writes corrections to CLAUDE.local.md

**Install (Windows, pip):**
```bash
pip install "headroom-ai[proxy,mcp,code]"
# Avoid uv tool install — litellm>=1.92 needs Rust build on Windows
```

**Wrap agent:**
```bash
headroom wrap codex    # wraps Codex CLI
headroom wrap openclaw # wraps OpenClaw
# wrap --help hangs on Windows (v0.26 bug), but wrap <agent> works
```

**MCP server mode:**
```bash
headroom mcp serve    # exposes headroom_compress, headroom_retrieve, headroom_stats
```

**Quick test:**
```bash
headroom proxy --port 8787  # drop-in local proxy, any OpenAI-compatible client
```

Use Headroom when deps are OK and you want maximum compression + reversibility.
Use `simple_compress` (zero-dep) when you can't install packages.

## Economics

Example: 10k tokens/session × 100 sessions = 1M tokens/day
- GPT-4o: $2.50/1M input tokens = $75/month
- With 60% compression: $30/month
- **Savings: $45/month**

At 10x scale: **$4,500/month saved**

---

## Integration with Finance Core (2026-07-05)

### Cost Tracker + Token Compression
- `scripts/cost_tracker.py` logs actual token usage from LLM responses
- `auto_compress` reduces tokens BEFORE sending to LLM
- Combined effect: smaller requests + accurate cost tracking

```python
# In llm_analyst.py call_llm()
messages = auto_compress(messages)  # Compress first
result = call_llm(model, messages, ...)  # Send compressed
# Response includes usage.prompt_tokens + usage.completion_tokens
log_cost(model, input_tokens, output_tokens, ...)  # Track actual cost
```

### Integration Points
1. **llm_analyst.py** — `auto_compress(messages)` at start of `call_llm()` + `analyze_batch()`
2. **autonomous_agent.py** — imports `auto_compress`, available for any LLM calls
3. **cost_tracker.py** — logs actual tokens from API response (not estimates)

### Verification
```bash
# Test compression
python tools/simple_compress.py
python tools/auto_compress.py

# Test cost tracking
python scripts/cost_tracker.py summary
python scripts/cost_tracker.py limit

# Both work together
python scripts/llm_analyst.py --status
python scripts/autonomous_agent.py --dry
```

### Results (2026-07-05)
- White Spot Explorer: 9 domains × ~2000 tokens = 18k tokens → $0.0013
- Auto-compression active in all LLM calls
- Cost check at start of every autonomous agent run
