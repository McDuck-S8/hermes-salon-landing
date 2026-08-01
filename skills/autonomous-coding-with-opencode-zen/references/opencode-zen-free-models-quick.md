# OpenCode Zen Provider Quick Reference

## Free Models (No Additional API Keys)

All models authenticated via single opencode API key in `~/.local/share/opencode/auth.json`.

| Model | Best For | Typical Latency |
|-------|----------|-----------------|
| `nemotron-3-ultra-free` | General reasoning, code analysis | 5-10s |
| `deepseek-v4-flash-free` | Fast coding tasks | 3-6s |
| `mimo-v2.5-free` | Quick responses, simple tasks | 2-5s |
| `qwen3.6-plus` | Complex reasoning, longer context | 5-12s |
| `qwen3.5-plus` | Alternative Qwen model | 5-10s |

List current: `D:/npm-global/node_modules/opencode-ai/bin/opencode.exe models opencode`

## Windows Setup

### The `.cmd` Wrapper Problem

The npm-installed `opencode.cmd` fails with **WinError 193** ("not a valid Win32 application") when called from Python `subprocess.run()`.

**Solution**: Use the direct executable:
```python
OPENCODE_CMD = "D:/npm-global/node_modules/opencode-ai/bin/opencode.exe"
```

Or ensure `D:/npm-global` is in PATH and call `opencode.exe` directly.

### Proxy Configuration

If behind corporate proxy:
```bash
set HTTP_PROXY=http://127.0.0.1:10806
set HTTPS_PROXY=http://127.0.0.1:10806
```

These must be set **before** running opencode, or passed via `env` in `subprocess.run()`.

## Auto-Rotation Pattern

```python
FREE_MODELS = [
    "nemotron-3-ultra-free",
    "deepseek-v4-flash-free",
    "mimo-v2.5-free",
    "qwen3.6-plus",
    "qwen3.5-plus",
]

def call_with_rotation(prompt: str) -> Optional[str]:
    for model in FREE_MODELS:
        for attempt in range(MAX_RETRIES_PER_MODEL):
            response = call_opencode(prompt, model)
            if response:
                return response
    return None  # All models failed
```

### Rotation Triggers
| Trigger | Detection |
|---------|-----------|
| Timeout | > 120s no response |
| Error | Non-zero exit code, stderr contains error |
| Rate Limit | HTTP 429 or "FreeUsageLimitError" |
| Empty Response | Valid exit code but no usable output |

## Prompt Engineering for Structured Output

**Critical**: For `fix_type: "patch"`, the LLM MUST output valid unified diff format:

```json
{
  "fix_type": "patch",
  "description": "Fix IndentationError in proactive_executor.py",
  "patch_or_action": "--- a/scripts/proactive_executor.py\n+++ b/scripts/proactive_executor.py\n@@ -1150,7 +1150,7 @@\n                 )\n \n-    if not errors:\n+    if not errors:\n         report(\"  No cron jobs with errors detected — all green\")",
  "confidence": 0.95,
  "target_file": "scripts/proactive_executor.py"
}
```

The prompt must explicitly require this format. See `scripts/llm_analyst.py` `build_prompt()` for the working prompt template.

## Description-to-Patch Patterns

When LLM returns description instead of patch, these patterns are auto-generated:

| Pattern | Trigger | Generated Fix |
|---------|---------|---------------|
| Indentation after `if` | "indentation" + "if" or "line 1154" | Adds 4-space indent to line after `if:` |
| Missing import | "import" + "module" | Adds import at top of file |
| Typo in string | "typo" + "string" | Replaces incorrect string |

Add new patterns to `generate_patch_from_description()` in `proactive_executor.py`.

## Rate Limit Behavior

| Model | Typical Limit | Behavior on Limit |
|-------|---------------|-------------------|
| nemotron-3-ultra-free | ~50 req/min | HTTP 429, retry after 120s |
| deepseek-v4-flash-free | ~60 req/min | HTTP 429, retry after 60s |
| mimo-v2.5-free | ~30 req/min | HTTP 429, retry after 120s |
| qwen3.6-plus | ~40 req/min | HTTP 429, retry after 90s |

The auto-rotation handles this transparently — when one model hits limits, it immediately tries the next.

## Cron Job for Continuous Operation

```yaml
# cron/llm_analyst.yaml
name: llm-analyst
schedule: "30s"
script: "scripts/llm_analyst.py"
no_agent: true
model:
  provider: opencode_zen
  model: nemotron-3-ultra-free
enabled_toolsets: ["terminal", "file"]
```

Start: `hermes cron start llm-analyst`