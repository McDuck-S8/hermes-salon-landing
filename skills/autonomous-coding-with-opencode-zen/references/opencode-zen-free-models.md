# OpenCode Zen Free Models — Patterns for Autonomous Cron Jobs

## Overview
This document captures patterns for using OpenCode Zen with free models in Hermes cron jobs, discovered during the autonomous proactivity engine implementation (June 2026).

## Free Model Priority List (Auto-Rotation)

| Priority | Model | Use Case |
|----------|-------|----------|
| 1 | nemotron-3-ultra-free | General reasoning, code analysis |
| 2 | deepseek-v4-flash-free | Fast analysis, structured output |
| 3 | mimo-v2.5-free | Complex reasoning (slower, has thinking tokens) |
| 4 | qwen3.6-plus | Alternative, good multilingual |
| 5 | qwen3.5-plus | Fallback |

## CLI Path Resolution

**Critical**: `opencode` command not in PATH after `npm i -g opencode-ai@latest`.

```python
# Correct path on Windows
OPENCODE_CMD = "D:/npm-global/node_modules/opencode-ai/bin/opencode.exe"

# Or dynamically resolve:
import subprocess, os
npm_prefix = subprocess.check_output(["npm", "prefix", "-g"], text=True).strip()
OPENCODE_CMD = os.path.join(npm_prefix, "node_modules", "opencode-ai", "bin", "opencode.exe")
```

## Auto-Rotation Implementation

```python
FREE_MODELS = [
    {"provider": "opencode", "model": "nemotron-3-ultra-free", "priority": 1},
    {"provider": "opencode", "model": "deepseek-v4-flash-free", "priority": 2},
    {"provider": "opencode", "model": "mimo-v2.5-free", "priority": 3},
    {"provider": "opencode", "model": "qwen3.6-plus", "priority": 4},
    {"provider": "opencode", "model": "qwen3.5-plus", "priority": 5},
]

ROTATE_ON = ["timeout", "error", "rate_limit", "empty_response"]
MAX_RETRIES_PER_MODEL = 2

def call_with_rotation(prompt: str) -> Optional[str]:
    for model_info in FREE_MODELS:
        for attempt in range(MAX_RETRIES_PER_MODEL):
            result = call_opencode(prompt, model_info["model"])
            if result:
                return result
            # Log failure, continue to next attempt/model
    return None
```

## Prompt Engineering for Structured Output

**Required**: LLM must return ONLY valid JSON array, no markdown.

```python
def build_prompt(issues: List[Dict]) -> str:
    return f"""You are an expert code analyst. Analyze these issues and produce actionable fixes.

Output ONLY valid JSON array with objects:
{{
  "fix_type": "patch|command|investigation",
  "description": "What this fix does",
  "patch_or_action": "For patch: FULL unified diff (--- a/file.py\\n+++ b/file.py\\n@@ -line,count +line,count@@\\n context\\n-old\\n+new). For command: shell command. For investigation: action description.",
  "confidence": 0.0-1.0,
  "target_file": "path/to/file.py"
}}

Issues to analyze:
{json.dumps(issues, indent=2, default=str)}

Return ONLY the JSON array. No markdown, no explanation."""
```

## Patch Format Requirements

For `fix_type: "patch"`, the `patch_or_action` MUST be a valid unified diff:

```diff
--- a/scripts/proactive_executor.py
+++ b/scripts/proactive_executor.py
@@ -1150,7 +1150,7 @@
                 )
 
-    if not errors:
+    if not errors:
         report("  No cron jobs with errors detected — all green")
```

**Common pitfall**: LLM returns descriptive text instead of diff.
**Fix**: Include example in prompt, validate with `patch_content.strip().startswith('--- ') and '+++ ' in patch_content and '@@' in patch_content`

## Description-to-Patch Generator

When LLM returns description instead of diff, generate patch for known patterns:

```python
def generate_patch_from_description(target_file: str, description: str) -> str | None:
    desc_lower = description.lower()
    
    # Pattern: IndentationError after 'if' statement
    if 'indentation' in desc_lower and ('if' in desc_lower or 'line' in desc_lower):
        # Read file, find 'if ...:' followed by unindented line, generate diff
        # ...
        return unified_diff
    
    return None
```

## Cron Job Configuration

```yaml
# cron/llm_analyst.yaml
name: llm-analyst
schedule: "30s"
script: "scripts/llm_analyst.py"
no_agent: true
model:
  provider: opencode_zen
  model: nemotron-3-ultra-free
```

## Configuration (config.yaml)

```yaml
llm_analyst:
  free_models:
    - provider: opencode
      model: nemotron-3-ultra-free
      priority: 1
    - provider: opencode
      model: deepseek-v4-flash-free
      priority: 2
    - provider: opencode
      model: mimo-v2.5-free
      priority: 3
    - provider: opencode
      model: qwen3.6-plus
      priority: 4
    - provider: opencode
      model: qwen3.5-plus
      priority: 5
  auto_rotate: true
  rotate_on: ["timeout", "error", "rate_limit", "empty_response"]
  max_retries_per_model: 2
  poll_interval_seconds: 30
  max_issues_per_batch: 10
```

## Testing

```bash
# 1. Test opencode CLI directly
D:/npm-global/node_modules/opencode-ai/bin/opencode.exe run "Say TEST_OK" --model opencode/mimo-v2.5-free

# 2. Test LLM Analyst service
python scripts/test_llm_analyst.py

# 3. Test proactive executor integration
python scripts/proactive_executor.py

# 4. Verify cron job registration
hermes cron list
```

## Key Lessons

1. **Free models have rate limits** — auto-rotation is not optional, it's required
2. **CLI path varies by npm prefix** — always resolve dynamically or use absolute path
3. **LLM output format is fragile** — strict prompt + validation + fallback generator essential
4. **opencode-zen works for cron** — unlike OpenRouter (402 credits) and OpenGateway (404 dead)
5. **Model `mimo-v2.5-free` is reasoning model** — adds 5-15s latency for "thinking tokens"
5. **User requirement**: "мы используем в системе только фри модели провайдеров!!!!" — enforce in all cron configs