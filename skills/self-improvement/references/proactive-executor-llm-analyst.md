# Proactive Executor + LLM Analyst Pattern

## Overview

This pattern implements a **fully autonomous proactive loop**:

```
proactive_executor (cron every 15m)
    │
    ├── Phase 1: Knowledge Cube Analysis → finds gaps
    ├── Phase 2: Cron Error Scan → finds broken jobs
    ├── Phase 2.5: LLM Analysis → writes pending_analysis.json
    │
    ▼
LLM Analyst Service (cron every 30s, opencode-zen free models)
    │
    ├── Reads pending_analysis.json
    ├── Calls LLM with auto-rotation (nemotron → deepseek → mimo → qwen)
    ├── Produces structured suggested_fixes.json
    │
    ▼
proactive_executor (next run)
    │
    ├── Reads suggested_fixes.json
    ├── Applies fixes (patches, commands, investigations)
    ├── Verifies fixes (syntax + pytest)
    ├── Records verified fixes to Knowledge Cube
```

## Files Created in This Session

| File | Purpose |
|------|---------|
| `scripts/llm_analyst.py` | Background service that polls pending_analysis.json, calls LLM, writes suggested_fixes.json |
| `scripts/test_llm_analyst.py` | Single-run test version |
| `scripts/proactive_executor.py` | Enhanced with Phase 2.5, apply_llm_suggested_fixes, verify_fix_result |
| `cron/llm_analyst.yaml` | Cron job config for LLM Analyst service |
| `config.yaml` | Added `llm_analyst.free_models` section |

## Key Implementation Details

### Free Model Auto-Rotation (Critical)

```python
FREE_MODELS = [
    "nemotron-3-ultra-free",  # Best reasoning
    "deepseek-v4-flash-free",  # Fast coding
    "mimo-v2.5-free",          # Quick responses
    "qwen3.6-plus",            # Complex reasoning
    "qwen3.5-plus",            # Alternative Qwen
]

# Rotation triggers: timeout, error, rate_limit, empty_response
# Max 2 retries per model before rotating
```

### Windows opencode.exe Path

The `.cmd` wrapper fails with WinError 193. Use direct executable:
```python
OPENCODE_CMD = "D:/npm-global/node_modules/opencode-ai/bin/opencode.exe"
```

### Fix Schema (LLM Output)

```json
{
  "fix_type": "patch|command|investigation",
  "description": "What this fix does",
  "patch_or_action": "Unified diff patch OR shell command OR investigation description",
  "confidence": 0.0-1.0,
  "target_file": "path/to/file.py"
}
```

**Critical**: For `fix_type: "patch"`, `patch_or_action` MUST be valid unified diff.

### Description-to-Patch Generator

When LLM returns description instead of patch, auto-generate for known patterns:

```python
def generate_patch_from_description(target_file: str, description: str) -> str | None:
    # Pattern: IndentationError after 'if' statement
    if 'indentation' in desc_lower and ('if' in desc_lower or 'line 1154' in desc_lower):
        # Read file, find unindented line after 'if:', generate unified diff
        ...
```

### Verification Loop

```python
def verify_fix_result(fix_result: dict, target_file: str) -> bool:
    # 1. Syntax check (py_compile for .py)
    # 2. Run related pytest tests
    # 3. Pattern-specific verification (e.g., indentation fixed)
    return True/False
```

Only `verified=true` fixes → Knowledge Cube as **knowledge** (not information).

## Beads Issues Created

Epic: `hermes-xjo` — Close LLM Analysis Feedback Loop

| Issue | Title | Status |
|-------|-------|--------|
| `hermes-xjo.1` | LLM Analyst Service | ✅ Claimed |
| `hermes-xjo.2` | Fix apply_llm_suggested_fixes return structure | ✅ Done |
| `hermes-xjo.3` | Post-fix verification mechanism | ✅ Done |
| `hermes-xjo.4` | Update hermes_hooks for verified knowledge capture | ⏳ Pending |
| `hermes-xjo.5` | Cron job for LLM Analyst | ✅ Done |

## Pitfalls (Discovered 2026-06-14)

### 1. LLM Hallucinates Non-Existent Commands

The LLM generates commands like `python scripts/auto_recall.py --fill-gaps --domain X` — but `auto_recall.py` has NO `--fill-gags` flag. It parsed them as keywords and returned unrelated KC entries. Exit code 0, so `apply_llm_suggested_fixes` marked it "succeeded" — false positive.

**Fix**: The llm_analyst prompt must list EXACT available scripts and their real flags. Never use generic suggestions like "run explore_domain or cube_feeder". Give concrete examples.

```python
# In build_prompt(), include:
AVAILABLE_SCRIPTS (use these commands only):
  python scripts/explore_domain.py <domain>
  python scripts/knowledge_gap_filler.py --domain <domain>
  python scripts/cube_feeder.py --domain <domain>
  python scripts/explore_white_spot.py
  python scripts/auto_tagger_v2.py
```

### 2. safe_patterns Must Stay in Sync

`proactive_executor.py` has a `safe_patterns` whitelist for auto-run. If a new script is added to llm_analyst prompt but not to safe_patterns, the fix gets logged as "Manual execution needed — not auto-running".

**Fix**: When adding a script to llm_analyst prompt, add it to safe_patterns in proactive_executor.py at the same time.

### 3. Empty Domains Need Explicit Handling

`knowledge_gap_filler.py --domain X` returns "No gaps found" when domain X has 0 entries — the domain doesn't exist in KC at all. The `find_gaps()` function only queries existing rows.

**Fix**: When `--domain` is specified and no gaps found, generate a fresh knowledge entry from scratch instead of returning silently. Added fallback in `main(filter_domain=...)`.

### 4. scripts/scripts/ Path Duplication

Cron jobs with `script: "scripts/trend_scout.py"` resolved to `D:/hermes/scripts/scripts/trend_scout.py` — double `scripts/`. The resolver assumes `scripts/` as base.

**Fix**: All script fields in `cron/jobs.json` must be bare filenames, e.g. `trend_scout.py --category all`, not `scripts/trend_scout.py --category all`.

## Status (2026-06-14)

- ✅ Pipeline: proactive_executor → pending_analysis.json → llm_analyst → suggested_fixes.json → proactive_executor (apply) → KC update
- ✅ KC grew from 3295 → 3320 (+20) in one cycle
- ✅ 6 fixes applied, 5 verified in one cycle
- ✅ `knowledge_gap_filler.py` now supports `--domain` with empty-domain fallback
- ✅ llm-analyst cron reactivated (was stuck at 2026-06-11)
- ✅ All cron script paths cleaned from `scripts/` prefix duplication
- ✅ safe_patterns expanded from 6 → 11 scripts

## Next Steps

1. **Start cron job** (if not running): `hermes cron start llm-analyst`
2. **Monitor end-to-end**: Run proactive_executor → verify fixes applied → check KC for new verified entries

## Testing Commands

```bash
# Test LLM Analyst single run
cd D:/Portable_Soft/hermes && python scripts/llm_analyst.py

# Test proactive_executor
cd D:/Portable_Soft/hermes && python scripts/proactive_executor.py

# Fill a specific domain gap
cd D:/Portable_Soft/hermes && python scripts/knowledge_gap_filler.py --domain <domain_name>

# Check cron status
cd D:/Portable_Soft/hermes && hermes cron list
```