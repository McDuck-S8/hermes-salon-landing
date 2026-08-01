---
name: forge-dynamic-tools
description: Dynamic Tool Creation (Forge-lite) — LLM generates Python code, validates security, executes in isolated sandbox, returns structured result. Enables Hermes to create new tools on-demand without manual coding.
tags: [forge, code-generation, sandbox, dynamic-tools, self-improvement, deepseek]
version: 1.0.0
---

# Forge-lite: Dynamic Tool Creation System

## Overview
Implements the "Forge" pattern from Ada-SI: LLM generates Python code → security validation → isolated sandbox execution → structured JSON result. Allows Hermes to create new capabilities on-demand without human coding.

## Architecture

```
User Task → Forge Prompt → Unified LLM Client (Cerebras primary) → Python Code
    ↓
Security Validation (forbidden patterns, allowed imports)
    ↓
Sandbox Execution (subprocess, clean env, tempfile, timeout)
    ↓
Structured Result: {"success": bool, "data": ..., "error": ..., "code": ...}
```

The LLM backend switched from raw `call_deepseek()` (localhost:9655) to
`scripts/llm_client.py` — a unified client with Cerebras gemma-4-31b as primary
provider and automatic fallback. See `provider-fallback-management` skill for
the full provider chain details.

## Core Components

### 1. Forge Prompt (`FORGE_PROMPT`)
System prompt that instructs DeepSeek to generate:
- Self-contained Python script (single file)
- Only stdlib imports from `ALLOWED_IMPORTS`
- No forbidden patterns (`FORBIDDEN_PATTERNS`)
- JSON output to stdout: `{"success": true, "data": {...}}` or `{"success": false, "error": "..."}`
- Uses `tempfile` for file operations
- Production-ready: error handling, types, docstrings

### 2. Security Validation (`validate_code()`)
- Checks `FORBIDDEN_PATTERNS`: subprocess, eval, exec, socket, threading, multiprocessing, ctypes, importlib, file deletion, os.remove, etc.
- Validates imports against `ALLOWED_IMPORTS` whitelist (json, os, pathlib, datetime, urllib, tempfile, etc.)
- Rejects code with `open()` for writing outside tempfile (initially too strict, relaxed to allow `open()` for tempfile writes)

### 3. Sandbox Execution (`run_in_sandbox()`)
- Writes code to temp file in `cache/forge/`
- Runs via `subprocess.run()` with:
  - Clean environment (`PYTHONPATH=''`, `PYTHONDONTWRITEBYTECODE=1`)
  - Timeout (default 30s)
  - Working directory = `cache/forge/`
- Parses JSON stdout, returns structured result
- Cleans up temp file after execution

### 4. Main Entry Point (`forge()`)
- Retries up to `max_retries` (default 2) on validation/execution failure
- Returns: `{"success": bool, "data": ..., "error": ..., "code": ..., "message": ...}`
- Convenience wrapper `forge_and_save(task, output_path)` saves generated code to file

## Usage

### CLI
```bash
python scripts/forge.py "Task description" [output_file.py] [--provider NAME]
# --provider: override LLM provider (e.g. "cerebras", "deepseek")
# If omitted, uses llm_client's default fallback chain (Cerebras first)
```

### Python API
```python
from scripts.forge import forge, forge_and_save

# Execute and get result
result = forge("Create HTML landing page for beauty salon")

# Execute and save generated code
result = forge_and_save("Create Telegram bot for booking", "scripts/booking_bot.py")
```

## Example Tasks
- "Create HTML landing page for beauty salon with hero, services, reviews, contact form"
- "Generate Telegram bot with calendar booking for salon"
- "Create Excel report from JSON metrics log"
- "Build SVG icons for 6 salon services"
- "Write Avito price parser for real estate category"

## Security Model
| Layer | Protection |
|-------|------------|
| Prompt | Instructs LLM to avoid dangerous patterns |
| Validation | Static analysis: forbidden patterns, import whitelist |
| Sandbox | Isolated subprocess, clean env, no PYTHONPATH, timeout |
| Output | Only JSON via stdout, no side effects in main process |

## LLM Backend (Updated 2026-07-09)

Forge now calls `scripts/llm_client.py` instead of raw `call_deepseek()`.

### llm_client.py — Unified LLM Client
- **Primary**: Cerebras `gemma-4-31b` (via httpx, SSL verify=False)
- **Fallback chain**: Cerebras → DeepSeek → Groq → OpenRouter
- **Transport**: httpx with `verify=False, proxy=None` (Windows SSL workaround)
- **Modes**: `call_llm()` (text), `call_structured()` (Pydantic via instructor), `call_json()`
- **API keys**: Loaded from `.env` (CEREBRAS_API_KEY, DEEPSEEK_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY)

### Provider Status (as of 2026-07-09)
| Provider | Model | Status | Notes |
|----------|-------|--------|-------|
| Cerebras | gemma-4-31b | ✅ WORKS | Primary provider (cloud) |
| DeepSeek Local | deepseek-chat | ✅ WORKS | FreeDeepseekAPI on localhost:9655 |
| DeepSeek | deepseek-chat | ❌ 402 | Insufficient balance (cloud API) |
| Groq | llama-3.3-70b | ❌ 403 | Region/network blocked |
| OpenRouter | gpt-4o-mini | ❌ 404 | No providers for free models |

## Pitfalls & Lessons Learned

### 1. `open()` Validation Too Strict
**Problem**: Initial `FORBIDDEN_PATTERNS` included `"open("` which blocked legitimate `tempfile` file writes.
**Fix**: Removed `"open("`, `"read("`, `"write("` from forbidden list. Rely on sandbox isolation instead.
**Lesson**: Validate dangerous *capabilities* (subprocess, eval, network), not basic I/O needed for the task.

### 2. DeepSeek Returns Markdown
**Problem**: LLM wraps code in ````python```...````.
**Fix**: Strip markdown fences in `forge()` before validation.
**Lesson**: Always post-process LLM output for code generation tasks.

### 3. Timeout on Complex Tasks
**Problem**: Large HTML generation (21KB) timed out at 120s CLI timeout.
**Fix**: Increase CLI timeout or reduce max_tokens for simpler tasks.
**Lesson**: Set appropriate timeouts; complex generation needs 60-120s.

### 4. DeepSeek API Latency on Code Generation
**Problem**: DeepSeek (localhost:9655) sometimes times out on code generation tasks (>60s).
**Fix**: Reduce max_tokens for simpler tasks, increase timeout for complex ones.
**Lesson**: Free-tier LLM latency is unpredictable; design prompts for smaller outputs or chain calls.

### 5. Sandbox Import Restrictions (Updated 2026-07-09)
**Problem**: Generated code using `html.parser` import failed validation because `html.parser` not in `ALLOWED_IMPORTS` (only `html`).
**Fix**: Added `html.parser` to `ALLOWED_IMPORTS` in `scripts/forge.py`.
**Lesson**: Keep import whitelist updated as LLM discovers new stdlib modules.

### 11. FORGE_PROMPT JSON Braces vs .format() (2026-07-09)
**Problem**: FORGE_PROMPT contains JSON examples with `{}` braces. When `.format(task=task)` is called, Python interprets `{\"success\": ...}` as format placeholders → `KeyError`.
**Fix**: Escape all literal braces in FORGE_PROMPT as `{{` and `}}`. Only the actual `{task}` placeholder stays unescaped.
**Lesson**: Any prompt template with JSON examples MUST double-brace all non-placeholder `{}`.

### 12. Sandbox Blocks API Keys (2026-07-09)
**Problem**: Forge sandbox runs with `PYTHONPATH=''` and clean env. Generated scripts that call external APIs (e.g. `os.environ.get('CEREBRAS_API_KEY')`) get empty strings — no keys available.
**Workaround**: For scripts that need API access, write them directly instead of forge-generating. Forge is best for stdlib-only logic. API-calling scripts should import `llm_client.py` directly.
**Lesson**: Forge sandbox is deliberately isolated. Use forge for pure computation, not API integration.

### 13. `urllib` vs `urllib.request` in ALLOWED_IMPORTS (2026-07-09)
**Problem**: LLM generates `import urllib` (the parent package) but ALLOWED_IMPORTS only has `urllib.request`, `urllib.parse`, `urllib.error`. Validator rejects it.
**Fix**: Added `urllib` to ALLOWED_IMPORTS.
**Lesson**: Import whitelist needs parent packages too, not just leaf modules.

### 14. Hand-Coding Loop — Use Forge Instead (2026-07-15)
**Problem**: User caught me hand-coding HTML for a PWA landing, Telegram Mini App, and SEO article — then saying "I should create a skill for this." The loop: hand-code → create skill → hand-code skill. User's fury: "ты снова сам кодишь? а нахрена тогда тебе вся эта система?"

**Root cause**: Reflexive hand-coding instead of prompting forge. Creating a new skill when forge could generate the artifact is hand-coding by proxy.

**Fix**: Hand-coding STOP → forge prompt → artifact saved. Creation loop broken.

**Workflow**:
```
Task: generate web artifact (PWA, Mini App, landing, SEO page)
→ WRONG: write HTML/CSS/JS by hand (30 min, one-off, no reuse)
→ WRONG: create a new skill and code inside it (hand-coding by proxy)
→ RIGHT: write forge prompt → forge generates HTML (5 min, prompt reusable)
→ OPTIONAL: save the prompt as a reference file under existing umbrella
```

**Prompt template**:
```
python scripts/forge.py "Generate a complete self-contained [PWA LANDING | TELEGRAM MINI APP | SEO ARTICLE | ...] HTML file for [topic]. Requirements: 1) Dark theme with [colors], 2) [feature 1], 3) [feature 2], 4) CTA to [link], 5) Mobile responsive. Output ONLY the HTML string in the data field." --provider opencode-zen
```

**Detection — HAND-CODING TRAP**:
```
You're about to write HTML/CSS/JS by hand → STOP
→ Can forge generate this? → YES → write prompt → done
→ Can forge NOT generate this? → is there an existing template/skill? → YES → use it
→ Can forge NOT generate this? → no template exists → THEN write minimal code
```

**Lesson**: Never write code that forge can generate. A forge prompt replaces hand-writing any web artifact. Skills are for processes, not one-shot outputs.

**Reference**: `references/2026-07-15-forge-html-prompts.md` — actual prompts that generated PWA/Mini App/SEO article this session.

### 5. DeepSeek Timeout on Complex Tasks (2026-07-07)
**Problem**: Complex generation (HTML landing page ~200 lines, A/B calculator ~300 lines) timed out at 60s LLM timeout.
**Root cause**: DeepSeek on localhost:9655 (free tier) has variable latency; large outputs exceed 60s.
**Fix**: 
- Reduce `max_tokens` for simpler tasks (1500-2000 vs 3000)
- Increase CLI timeout to 120-180s for complex generations
- Use `deepseek-reasoner` for complex logic (thinking mode)
**Lesson**: Free-tier LLM latency is unpredictable; design prompts for smaller outputs or chain multiple calls.

### 6. Validation Pattern Success (2026-07-07)
**Observation**: Current validation works well for stdlib-only tasks.
- HTML generation: ✅ (tempfile, datetime, json, pathlib, typing, html.parser)
- A/B calculator: ✅ (math, statistics, json, sys, dataclasses, enum, typing)
- JSON→CSV: ✅ (csv, json, sys, pathlib)
- Simple functions: ✅ (typing, decimal, fractions)
**Pattern**: Tasks using only ALLOWED_IMPORTS pass validation on first try.
**Lesson**: Keep task scope aligned with ALLOWED_IMPORTS; avoid requests needing external libs (requests, pandas, etc.)

### 7. Sandbox Execution Reliability (2026-07-07)
**Observation**: Subprocess isolation with clean env works reliably.
- Temp file cleanup: consistent
- JSON stdout parsing: works when LLM follows contract
- Exit codes: 0 = success, 1 = execution error (handled)
**Lesson**: The sandbox model is solid; bottlenecks are LLM latency and output size.

### 8. Integration with Persona System (2026-07-07)
**Context**: Created `scripts/persona_system.py` with 4 modes (arbitrage, sales, analyst, developer).
**Synergy**: Forge-lite can be invoked from any persona mode.
**Integration**: Each persona has different `tools_priority` and `temperature` — forge respects these via config.

## Files
- `scripts/forge.py` — Main forge implementation (integrated with llm_client)
- `scripts/llm_client.py` — Unified LLM client (Cerebras primary, httpx transport)
- `scripts/test_providers.py` — Provider connectivity test script
- `cache/forge/` — Sandbox working directory (auto-created)
- Generated tools saved to specified output path

## Integration Points
- Can be called from `autonomous_agent.py` as a dynamic action
- Compatible with `event_bus.py` for event-driven tool creation
- Works with `proactive_executor.py` for autonomous capability expansion

## References
- `references/ada-si-forge-analysis.md` — Ada-SI Forge architecture analysis
- `references/security-model.md` — Detailed security model documentation
- `templates/forge-task-template.md` — Prompt template for new task types