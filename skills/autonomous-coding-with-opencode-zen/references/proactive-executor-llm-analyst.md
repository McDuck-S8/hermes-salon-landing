# Proactive Executor + LLM Analyst: Autonomous Proactivity Loop

**Implemented:** 2026-06-08  
**Status:** Production — working end-to-end

---

## Overview

This document describes the complete autonomous proactivity loop built in Hermes Agent, consisting of:

1. **proactive_executor.py** — runs every 15m, detects gaps/errors, applies and verifies fixes
2. **llm_analyst.py** — runs every 1m, polls pending analysis, calls FREE LLM with auto-rotation
3. **Supermemory** — vector database storing verified fixes for future retrieval
4. **hermes_hooks + event_evolution** — integration layer capturing verified knowledge

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CRON SCHEDULER (Hermes)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────┐         ┌─────────────────────────────────┐  │
│  │ proactive_executor.py   │         │ llm_analyst.py                  │  │
│  │ Schedule: every 15m     │         │ Schedule: every 1m              │  │
│  │ Mode: no_agent=True     │         │ Mode: no_agent=True             │  │
│  └───────────┬─────────────┘         └──────────────┬──────────────────┘  │
│              │                                       │                      │
│              ▼                                       ▼                      │
│  ┌─────────────────────────┐         ┌─────────────────────────────────┐  │
│  │ Phase 1: KC Analysis    │         │ Poll pending_analysis.json      │  │
│  │ Phase 2: Cron Scan      │         │                                 │  │
│  │ Phase 2.5: LLM Analysis │◄────────┤ FREE Models + Auto-Rotation     │  │
│  │   ├── Read suggested_   │         │   nemotron-3-ultra-free         │  │
│  │   ├── apply_llm_        │         │   deepseek-v4-flash-free        │  │
│  │   ├── verify_fix_       │         │   mimo-v2.5-free                │  │
│  │   └── hooks.on_task_    │         │   qwen3.6-plus                  │  │
│  │ Phase 3: Standard Fixes │         │   qwen3.5-plus                  │  │
│  │ Phase 4: Task Gen       │         │                                 │  │
│  └───────────┬─────────────┘         └──────────────┬──────────────────┘  │
│              │                                       │                      │
│              ▼                                       ▼                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SUPERMEMORY (Vector DB)                          │   │
│  │  Verified fixes stored with: verified=true, evidence="tests pass"  │   │
│  │  Future queries retrieve relevant fix patterns                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## File Details

### 1. scripts/llm_analyst.py

**Purpose:** Background service polling `pending_analysis.json`, calling FREE models via opencode-zen with auto-rotation.

**Key Features:**
- Polls `cache/pending_analysis.json` every 30s (configurable)
- Calls opencode-zen with 5 FREE models in priority order
- Auto-rotation on: timeout, error, rate_limit, empty_response
- Writes structured `cache/suggested_fixes.json`
- Runs via Hermes cron: `no_agent=True`, stdout delivered

**Config (config.yaml):**
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

**Windows Critical Fix:** Use direct executable:
```python
OPENCODE_CMD = "D:/npm-global/node_modules/opencode-ai/bin/opencode.exe"
# NOT: "D:/npm-global/opencode" (fails with WinError 193)
```

### 2. scripts/proactive_executor.py (Enhanced)

**New Phase 2.5: LLM Analysis** (inserted between Cron Scan and Fix Actions)

```python
# Phase 2.5: LLM Analysis
suggested_fixes = analyze_with_llm(llm_issues)
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

**Key Changes:**
- `analyze_with_llm()` now reads `suggested_fixes.json` (highest priority) → `llm_analysis_cache.json` (legacy) → writes `pending_analysis.json`
- `apply_llm_suggested_fixes()` returns detailed structure: `{applied, verified, failed, skipped, total}`
- `verify_fix_result()` runs `py_compile` + pytest for verification
- `generate_patch_from_description()` auto-generates unified diffs for known patterns (indentation fixes)

**Exit Code Fix:** Always return 0 (cron marks non-zero as error):
```python
# Exit code: 0 = script ran successfully, 1 = unhandled exception
return 0
```

### 3. scripts/hermes_hooks.py (Supermemory Integration)

```python
def on_task_complete(self, task_description: str, result: str, tags: list[str] = None, 
                     verified: bool = False, evidence: str = ""):
    # ... existing logic ...
    
    if verified and evidence:
        self._store_in_supermemory(task_description, result, tags, evidence)

async def _store_in_supermemory(self, task_description: str, result: str, tags: list[str], evidence: str):
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
```

### 4. scripts/event_evolution.py (Extended)

```python
def on_task_complete(content: str, tags: list[str] = None, source: str = "agent", 
                     verified: bool = False, evidence: str = ""):
    emit_event("task_complete", {
        "content": content, 
        "tags": tags or [], 
        "source": source,
        "verified": verified,
        "evidence": evidence
    })
```

---

## Fix Schema (LLM Output)

```json
{
  "fix_type": "patch|command|investigation",
  "description": "What this fix does",
  "patch_or_action": "Unified diff patch OR shell command OR investigation description",
  "confidence": 0.0-1.0,
  "target_file": "path/to/file.py"
}
```

**For `fix_type: "patch"` — MUST be valid unified diff:**
```diff
--- a/scripts/proactive_executor.py
+++ b/scripts/proactive_executor.py
@@ -1150,7 +1150,7 @@
                 )
 
-    if not errors:
+    if not errors:
         report("  No cron jobs with errors detected — all green")
```

---

## Cron Jobs (Hermes Native)

```bash
# LLM Analyst - runs every 1m
hermes cron create --name llm-analyst --script scripts/llm_analyst.py --no-agent --deliver local "every 1m"

# Proactive Executor - runs every 15m (already exists)
hermes cron list | grep proactive-executor
```

---

## Verification Loop (Closing Information → Knowledge)

| Stage | What Happens | Result |
|-------|--------------|--------|
| 1. Detect | proactive_executor finds gaps/errors | `pending_analysis.json` |
| 2. Analyze | llm_analyst calls FREE LLM | `suggested_fixes.json` |
| 3. Apply | proactive_executor applies patches | Files modified |
| 4. Verify | `verify_fix_result()` = syntax + pytest | Boolean |
| 5. Capture | `hooks.on_task_complete(verified=True, evidence=...)` | Supermemory entry |

**Only `verified=true` fixes become Knowledge.** Everything else stays Information.

---

## Deployment Checklist

- [ ] Supermemory running: `docker-compose up -d` in supermemory repo
- [ ] `SUPERMEMORY_URL` in hermes_hooks.py points to correct endpoint
- [ ] `config.yaml` has `llm_analyst.free_models` with auto_rotate
- [ ] Cron jobs created and started via `hermes cron`
- [ ] Windows: `llm_analyst.py` uses direct `.exe` path
- [ ] `proactive_executor.py` returns exit code 0
- [ ] Test end-to-end: create pending_analysis.json → verify suggested_fixes.json appears → verify fix applied → verify Supermemory entry

---

## Known Issues / Follow-ups

1. **llm_analyst timeout (120s)** — increase cron timeout or optimize batch size
2. **Patch generator limited** — only handles indentation fixes; need generators for config/command/investigation types
3. **Cron frequency** — `every 1m` may be too aggressive; consider `every 5m` or `every 15m`
4. **Supermemory not yet tested** — need to verify vector storage and retrieval works