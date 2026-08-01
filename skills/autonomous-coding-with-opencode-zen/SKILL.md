---
name: autonomous-coding-with-opencode-zen
description: "Delegate coding tasks to OpenCode Zen agent and capture knowledge from the outcome. Use when you need autonomous code generation, refactoring, or debugging with the OpenCode CLI."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [coding-agent, opencode, zen, autonomous, code-generation]
    related_skills: [hermes-agent, event-driven-self-evolution, auto-recall]
---

# Autonomous Coding with OpenCode Zen

This skill provides a procedure for using the OpenCode Zen agent to perform coding tasks autonomously, and then capturing the knowledge from the task completion via Hermes' event-driven self-evolution system.

## When to Use

- User asks to write, refactor, or debug code and wants an autonomous agent to handle it
- You need to generate code, tests, or documentation with minimal supervision
- You want to leverage external AI coding agents while maintaining knowledge capture in Hermes
- The task is well-described and can be accomplished in a bounded session

## Prerequisites

1. OpenCode Zen installed globally:
   ```bash
   npm i -g opencode-ai@latest
   ```
2. Provider configured for OpenCode Zen:
   - Get an API key from https://opencode.ai/zen
   - Set environment variable `OPENCODE_API_KEY`
   - (Optional) Configure proxy if needed: `HTTP_PROXY`, `HTTPS_PROXY`
3. Verify installation:
   ```bash
   opencode --version
   opencode auth list
   ```
   **Windows note**: The `opencode` command may be a `.cmd` wrapper that fails with WinError 193. Use the direct executable:
   ```bash
   D:/npm-global/node_modules/opencode-ai/bin/opencode.exe --version
   ```
4. Hermes event evolution system is active (it is by default).

### Free Models Available (No API Key Required)

The following free models work via opencode-zen without additional credentials (authenticated via the opencode API key in `~/.local/share/opencode/auth.json`):

| Model | Best For |
|-------|----------|
| `nemotron-3-ultra-free` | General reasoning, code analysis |
| `deepseek-v4-flash-free` | Fast coding tasks |
| `mimo-v2.5-free` | Quick responses |
| `qwen3.6-plus` | Complex reasoning |
| `qwen3.5-plus` | Alternative Qwen model |

List all available: `opencode models opencode`

### Headroom + LLMLingua Integration (Context Compression Stack)

**Purpose**: Fix timeout issues and enable free models to handle large contexts by compressing context before LLM calls.

**Components:**
- **Headroom (chopratejas/headroom)**: Compresses tool outputs, logs, RAG chunks, files — 60-95% fewer tokens
- **LLMLingua (microsoft/LLMLingua)**: Compresses prompts (system + user + RAG) — LLMLingua-2 up to 20x compression, RAG +21.4% at 1/4 tokens

**Synergy (Full Stack Compression):**
```
Hermes Agent → tool outputs, logs, RAG
    ↓
[Headroom] → 60-95% compression (tool outputs, logs, files)
    ↓
[LLMLingua-2] → 4-20x compression (prompts, RAG, system prompt)
    ↓
[Free LLM] → fast, cheap, quality preserved
```

**Integration Points:**
1. **LLM Analyst Wrapper** (immediate timeout fix):
   ```bash
   headroom wrap python scripts/llm_analyst.py
   ```
   - Fixes 120s timeout by compressing context before LLM
   - Use direct executable: `D:/npm-global/node_modules/opencode-ai/bin/opencode.exe`

2. **MCP Server** (all agents):
   ```bash
   headroom mcp install
   ```

3. **LLMLingua-2 in Proactive Executor** (Phase 2.5):
   ```python
   from llmlingua import PromptCompressor
   compressor = PromptCompressor(model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank")
   compressed = compressor.compress_prompt(prompt=huge_prompt, rate=0.25, target_token=2000)
   ```

4. **Headroom Learn** (auto-pattern learning):
   ```bash
   headroom learn
   ```

**Installation:**
```bash
D:/Portable_Soft/hermes/hermes-agent/venv/Scripts/python.exe -m pip install headroom llmlingua
```

**Verification:**
1. `headroom wrap python scripts/llm_analyst.py` — runs without timeout
2. `python -c "from llmlingua import PromptCompressor; print('OK')"` — LLMLingua loads
3. `headroom mcp install` — MCP server registered

**Benefits for Hermes:**
| Problem | Solution |
|---------|----------|
| llm_analyst timeout (120s) | Headroom compresses context → fits in free model limits |
| Free model context limits | LLMLingua compresses prompts 4-20x |
| Token costs | 60-95% + 4-20x = massive savings |
| RAG quality | LLMLingua improves RAG +21.4% at 1/4 tokens |

## Procedure

### 1. Prepare the Task Description
   - Clearly state what you want the agent to accomplish.
   - Include any specific constraints (e.g., language, frameworks, output format).
   - Example: "Create a Python script that reads a CSV file and calculates the average of a column."

### 2. Run OpenCode Zen in One-Shot Mode (for bounded tasks)
   Use `opencode run` for tasks that should finish after a single prompt.
   ```bash
   set OPENCODE_API_KEY=your_key_here
   set HTTP_PROXY=http://127.0.0.1:10806  # if needed
   set HTTPS_PROXY=http://127.0.0.1:10806  # if needed
   opencode run "Your task description here" --model opencode/mimo-v2.5-free
   ```
   - The `--model opencode/mimo-v2.5-free` specifies the free mimo-v2.5-free model.
   - If you want to think aloud, add `--thinking`.
   - To attach files, use `-f path/to/file`.

### 3. Run OpenCode Zen in Interactive Mode (for iterative work)
   For tasks requiring multiple exchanges:
   ```bash
   opencode --model opencode/mimo-v2.5-free  # starts TUI in foreground
   # Or for background monitoring:
   opencode --model opencode/mimo-v2.5-free --background --pty
   ```
   - In the TUI, enter your prompt and press Enter to submit.
   - Use `Ctrl+C` to exit the TUI (not `/exit`).
   - To send follow-up input in background mode:
     ```bash
     process(action="submit", session_id="<id>", data="Next instructions...")
     process(action="poll", session_id="<id>")  # check progress
     ```

### 4. Verify Results
   - Check that the agent produced the expected output (files changed, tests passed, etc.).
   - For code tasks, run any relevant tests or linters.
   - Summarize what was accomplished.

### 5. Emit Completion Event for Knowledge Capture
   After verifying success, trigger Hermes' self-evolution to capture the knowledge:
   ```python
   from scripts.event_evolution import on_task_complete
   on_task_complete(
       content="Brief description of what was accomplished and the result",
       tags=["opencode", "zen", "coding", "specific-topic"],
       source="agent"
   )
   ```
   - This will be processed by the event system and, if not in cooldown, captured as a LEARNED entry in the knowledge cube.
   - The knowledge will then be available via `auto_recall` in future sessions.

### 6. Optional: Process Pending Events Immediately
   If you want to force processing (e.g., for testing or if you know cooldowns have passed):
   ```python
   from scripts.event_evolution import process_pending_events
   result = process_pending_events()
   print(f"Processed {result['processed']} events, {result['errors']} errors")
   ```

## Pitfalls

- **Model Availability**: Ensure the model `mimo-v2.5-free` is available in the OpenCode Zen provider. Check with `opencode models opencode`.
- **Proxy Issues**: If behind a proxy, set `HTTP_PROXY` and `HTTPS_PROXY` environment variables before running opencode.
- **Interactive Exit**: Do not use `/exit` in the OpenCode TUI — it opens an agent selector. Use `Ctrl+C` to exit.
- **Cooldowns**: The event system has cooldowns (default 4h for task_complete) to prevent flooding. If you emit an event too soon after a similar one, it will not trigger knowledge capture until the cooldown expires.
- **Background Sessions**: When using background mode, always pair with `notify_on_complete=true` or monitor with `process(action="poll|log")` to know when the task finishes.
- **Working Directory**: Scope OpenCode sessions to a specific directory to avoid collisions. Use the `workdir` parameter in Hermes terminal calls or cd before running.

## Verification

Smoke test:
```bash
opencode run "Respond with exactly: OPENVENICE_TEST_OK" --model opencode/mimo-v2.5-free
```
Success criteria:
- Output includes `OPENVENICE_TEST_OK`
- Command exits without provider/model errors

## Example Usage via Hermes

Here's how you might orchestrate this from within Hermes:

```python
# 1. Ensure opencode is available
terminal(command="opencode --version")

# 2. Set up environment (if not already set)
terminal(command="set OPENCODE_API_KEY=***")
terminal(command="set HTTP_PROXY=http://127.0.0.1:10806")
terminal(command="set HTTPS_PROXY=http://127.0.0.1:10806")

# 3. Run the coding task
terminal(
    command="opencode run 'Write a Python function that calculates factorial using recursion' --model opencode/mimo-v2.5-free",
    workdir="/tmp/opencode_test"
)

# 4. Check the result
terminal(command="cat /tmp/opencode_test/factorial.py")  # adjust path as needed

# 5. Emit completion event
from scripts.event_evolution import on_task_complete
on_task_complete(
    content="Created recursive factorial function in Python",
    tags=["opencode", "zen", "python", "recursion"],
    source="agent"
)
```

## Integration with Hermes Systems

- **Auto-Recall**: After knowledge capture, the learned pattern will be searchable via `recall_for_session()` or `auto_recall_with_lavra()`.
- **Event Evolution**: The `task_complete` event triggers `capture_knowledge` (respecting cooldowns).
- **Knowledge Cube**: Captured entries are stored in `knowledge_cube.db` and can be fused with Lavra knowledge.
- **Memory System**: Durable facts (e.g., "OpenCode Zen is configured with mimo-v2.5-free model") can be saved to MEMORY.md via the memory tool.

## Working HTTP API (No subprocess needed)

**The opencode-zen provider is accessible via direct HTTP API.** No subprocess, no TTY, no CLI needed.

**Endpoint:** `https://opencode.ai/zen/v1/chat/completions`
**Auth:** None for free models (no API key header needed)
**Models:** mimo-v2.5-free, deepseek-v4-flash-free, nemotron-3-ultra-free, qwen3.6-plus-free, minimax-m3-free

```python
import requests

API_URL = "https://opencode.ai/zen/v1/chat/completions"

def call_llm(prompt, model="mimo-v2.5-free", max_tokens=2000):
    r = requests.post(API_URL, json={
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3
    }, timeout=60)
    if r.status_code == 200:
        msg = r.json()["choices"][0]["message"]
        return msg.get("content") or msg.get("reasoning") or ""
    return None
```

**CRITICAL quirk:** Some models return `content: null` with reasoning in a separate `reasoning` field. Always check both:
```python
content = msg.get("content") or msg.get("reasoning") or ""
```

**Rate limiting:** Add 3-5 second delays between consecutive calls. Faster → HTTP 401/429.

**FORBIDDEN:** OpenRouter (no credits, user explicitly forbids it). Do NOT use OpenRouter keys.

## Troubleshooting

- If `opencode` command not found: check installation path and ensure global npm bin is in PATH.
- If model not found: verify the model name with `opencode models opencode`.
- If authentication fails: run `opencode auth login` or check `OPENCODE_API_KEY`.
- If the agent seems stuck: inspect logs with `process(action="log", session_id="<id>")` in background mode.
- If knowledge capture fails: check that the event evolution system is functioning and that cooldowns have elapsed.
- **If ALL opencode models return "Unexpected server error"**: dialagram.me is down. Switch to OpenRouter API fallback above.

### Free Model Auto-Rotation Pattern (Critical for Autonomous Operation)

When running autonomous services (cron jobs, background agents), **always use free models with auto-rotation**. Paid models hit rate limits and stop the pipeline.

### Windows Executable Path Fix (Critical)

On Windows, the `opencode` command from npm global is a `.cmd` wrapper that fails with **WinError 193** (%1 is not a valid Win32 application). **Always use the direct executable:**

```bash
# WRONG - fails with WinError 193
opencode run "task" --model opencode/nemotron-3-ultra-free

# CORRECT - direct executable path
D:/npm-global/node_modules/opencode-ai/bin/opencode.exe run "task" --model opencode/nemotron-3-ultra-free
```

The `.cmd` wrapper calls `opencode.exe` internally but the PATH resolution fails in subprocess calls. The direct `.exe` path works reliably.

### Node.js Subprocess Hang on Windows (CRITICAL)

**opencode.exe hangs indefinitely when called from Python `subprocess.run()` on Windows.** This is NOT a timeout — the process never starts. Root cause: Node.js CLIs detect TTY and behave differently in subprocess; on Windows, `subprocess.Popen` doesn't create a proper TTY.

**What works:**
- `terminal` tool directly → ✅ works
- `terminal(background=true)` → ✅ works
- Python `subprocess.run(["opencode.exe", ...])` → ❌ hangs forever
- Batch wrapper → ❌ still hangs (uses subprocess internally)

**Workaround:** Always use Hermes `terminal` tool for opencode invocations. Do NOT wrap in Python subprocess. The `terminal` tool creates a proper PTY environment.

**If you must call from Python:** Use `pty=True` in terminal tool, or use `execute_code` which inherits the session's terminal context.

### Configuration (in `config.yaml`)

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

### Implementation Pattern

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
        # Model exhausted retries -> rotate to next
    return None  # All models failed
```

### Rotation Triggers
- **Timeout**: > 120s no response
- **Error**: Non-zero exit code, stderr contains error
- **Rate Limit**: HTTP 429 or "FreeUsageLimitError"
- **Empty Response**: Valid exit code but no usable output

---

## References

- Proactive Executor + LLM Analyst autonomous loop: `references/proactive-executor-llm-analyst.md`
- Windows opencode.exe subprocess fix: `references/windows-opencode-subprocess-fix.md`
- Lightweight Prompt Compression (no heavy deps): `references/lightweight-prompt-compression.md`
- OpenCode Zen Documentation: https://opencode.ai/docs/zen
- Hermes Event-Driven Self-Evolution: see `scripts/event_evolution.py`
- Lavra Knowledge Capture Pattern: see `plugins/self-evolution/evolution/core/knowledge.py`
- Auto-Recall System: see `scripts/auto_recall.py`

---

## Autonomous Analysis Service Pattern

This pattern enables a **continuous background service** that:
1. Polls `pending_analysis.json` (written by proactive_executor)
2. Calls LLM with free model rotation
3. Writes structured `suggested_fixes.json`
4. Proactive executor picks up fixes, applies, verifies, captures knowledge

### Files
- **Input**: `cache/pending_analysis.json` — issues from proactive_executor Phase 2.5
- **Output**: `cache/suggested_fixes.json` — structured fixes for proactive_executor
- **Service**: `scripts/llm_analyst.py` (runs via cron every 30s)

### Fix Schema (LLM Output) - Production Version

```json
{
  "fix_type": "patch|command|investigation",
  "description": "What this fix does",
  "patch_or_action": "Unified diff patch OR shell command OR investigation description",
  "confidence": 0.0-1.0,
  "target_file": "path/to/file.py"
}
```

**Critical**: For `fix_type: "patch"`, the `patch_or_action` MUST be a valid **unified diff** that `git apply` can parse:

```diff
--- a/scripts/proactive_executor.py
+++ b/scripts/proactive_executor.py
@@ -1150,7 +1150,7 @@
                 )
 
-    if not errors:
+    if not errors:
         report("  No cron jobs with errors detected — all green")
```

### Description-to-Patch Generation

When LLM returns a description instead of a patch, auto-generate for known patterns:

```python
def generate_patch_from_description(target_file: str, description: str) -> str | None:
    """Generate unified diff from natural language for known fix patterns."""
    # Pattern: IndentationError after 'if' statement
    if 'indentation' in description.lower() and ('if' in description.lower() or 'line 1154' in description.lower()):
        # Read file, find unindented line after 'if:', generate diff
        ...
    return None  # Unknown pattern
```

### Supermemory Integration for Verified Knowledge

When a fix is **verified** (tests pass, syntax OK), store it in Supermemory for future retrieval:

```python
# In hermes_hooks.py -> on_task_complete()
async def _store_in_supermemory(self, task_description: str, result: str, tags: list[str], evidence: str):
    """Store verified fix in Supermemory vector database."""
    try:
        import httpx
        payload = {
            "content": f"VERIFIED FIX: {task_description}\\nResult: {result}\\nEvidence: {evidence}",
            "metadata": {
                "tags": tags or [],
                "verified": True,
                "evidence": evidence,
                "source": f"session:{self.session_id}",
                "type": "proactive_fix"
            }
        }
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(f"{SUPERMEMORY_URL}/memories", json=payload)
    except Exception as e:
        print(f"[EventHook] Supermemory store failed: {e}")
```

Then in `proactive_executor.py` after `verify_fix_result()` passes:

```python
if verified:
    hooks.on_task_complete(
        task_description=f"Applied fix: {fix['description']}",
        result="Patch applied and verified",
        tags=["proactive", "verified", fix.get('fix_type')],
        verified=True,
        evidence="py_compile passed + pytest passed"
    )
```

This closes the **Information → Knowledge loop**: verified fixes become searchable vector memories.

### Autonomous Analysis Service Pattern - Complete Loop

```diff
--- a/scripts/proactive_executor.py
+++ b/scripts/proactive_executor.py
@@ -1150,7 +1150,7 @@
                 )
 
-    if not errors:
+    if not errors:
         report("  No cron jobs with errors detected — all green")
```

### Description-to-Patch Generation

When LLM returns a description instead of a patch, auto-generate for known patterns:

```python
def generate_patch_from_description(target_file: str, description: str) -> str | None:
    """Generate unified diff from natural language for known fix patterns."""
    # Pattern: IndentationError after 'if' statement
    if 'indentation' in description.lower() and ('if' in description.lower() or 'line 1154' in description.lower()):
        # Read file, find unindented line after 'if:', generate diff
        ...
    return None  # Unknown pattern
```

### Verification Loop

After applying fixes, **always verify**:

```python
def verify_fix_result(fix_result: dict, target_file: str) -> bool:
    # 1. Syntax check (py_compile for .py)
    # 2. Run related pytest tests
    # 3. Pattern-specific verification (e.g., indentation fixed)
    return True/False
```

Only `verified=true` fixes get written to Knowledge Cube as **knowledge** (not just information).

---

### Cron Job for Continuous Operation

Run the analyst as a background cron job via Hermes (no_agent=True, stdout delivered):

```bash
# Create the cron job
hermes cron create --name llm-analyst --script scripts/llm_analyst.py --no-agent --deliver local "every 1m"

# Start it
hermes cron run llm-analyst  # or wait for scheduler tick

# List to verify
hermes cron list
```

**Key Hermes cron parameters:**
- `--no-agent` — the script IS the job, stdout delivered verbatim
- `--script` — path under `~/.hermes/scripts/`
- `--deliver local` — capture output locally (not sent to chat)
- Schedule: `"every 1m"`, `"every 15m"`, `"30m"`, or cron expression

### Exit Code Handling for Cron Compatibility

**Critical:** Cron jobs in Hermes mark non-zero exit as "error" status. For autonomous services that should run continuously without alerting on "issues found but no fix needed", **always return 0**:

```python
# In your script's main()
def main() -> int:
    # ... do work ...
    # Issues detected but no auto-fix possible is NORMAL, not an error
    return 0  # Script ran successfully = no unhandled exception
```

This prevents the cron system from marking successful runs as "error" when the proactive executor finds knowledge gaps but can't auto-fix them (which is expected behavior).

### Fix Schema (LLM Output) - Production Version

---

## LLM Analyst + Proactive Executor: Autonomous Proactivity Loop

This is the **complete production pattern** for autonomous proactivity built in this session:

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  proactive_executor.py (cron every 15m)                        │
│  ├── Phase 1: Knowledge Cube Analysis → gaps                   │
│  ├── Phase 2: Cron Error Scan → errors                         │
│  ├── Phase 2.5: LLM Analysis                                   │
│  │     ├── Read suggested_fixes.json (from LLM Analyst)        │
│  │     ├── Apply fixes via apply_llm_suggested_fixes()         │
│  │     ├── verify_fix_result() → syntax + pytest               │
│  │     └── hooks.on_task_complete(verified=True, evidence=...) │
│  ├── Phase 3: Standard Fixes                                   │
│  └── Phase 4: Knowledge-Driven Task Generation                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  llm_analyst.py (cron every 1m, no_agent=True)                 │
│  ├── Poll pending_analysis.json                                │
│  ├── Call FREE models with auto-rotation                       │
│  │     nemotron-3-ultra-free → deepseek-v4-flash-free          │
│  │     → mimo-v2.5-free → qwen3.6-plus → qwen3.5-plus         │
│  ├── Write suggested_fixes.json                                │
│  └── Loop                                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Supermemory (vector DB)                                       │
│  └── Verified fixes stored with verified=true + evidence       │
└─────────────────────────────────────────────────────────────────┘
```

### Key Files Created

| File | Purpose |
|------|---------|
| `scripts/llm_analyst.py` | Background service polling pending_analysis.json, calling free models with auto-rotation |
| `scripts/proactive_executor.py` | Enhanced with Phase 2.5 LLM Analysis, detailed fix application, verification |
| `scripts/hermes_hooks.py` | Supermemory integration for verified fixes |
| `scripts/event_evolution.py` | Extended `on_task_complete()` with `verified`/`evidence` params |
| `cron/llm_analyst.yaml` | Cron job config (Hermes native) |
| `config.yaml` | `llm_analyst.free_models` with auto-rotation config |

### Verification Loop (Closing the Knowledge Gap)

```python
# In proactive_executor.py
fix_results = apply_llm_suggested_fixes(suggested_fixes)
for applied_fix in fix_results["applied"]:
    if verify_fix_result(applied_fix, target_file):
        hooks.on_task_complete(
            task_description=f"Applied fix: {applied_fix['fix']['description']}",
            result="Patch applied and verified",
            tags=["proactive", "verified", applied_fix['fix'].get('fix_type')],
            verified=True,
            evidence="py_compile passed + pytest passed"
        )
```

**Only `verified=true` fixes become Knowledge.** Everything else stays Information.

---

## References

- Supermemory integration details: `references/supermemory-integration.md`
- Proactive executor + LLM Analyst loop: `references/proactive-executor-llm-analyst.md`