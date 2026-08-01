# Shame Counter Pattern — Replacing Duplicate Filter with Repetition Sensor

**Date:** 2026-07-18
**Context:** Operation "Resuscitation" — 17,631 self-improvement suggestions, 19 skills created (0.11% conversion)

## Problem

The Crystal pipeline had a deduplication filter in `run_full_cycle()` that silently dropped proposals with similar descriptions:

```python
# OLD (wrong): filters out "duplicates"
seen_keys = set()
for p in fresh_proposals:
    key = (p.action, p.department, keywords)
    if key not in seen_keys:
        seen_keys.add(key)
        unique_proposals.append(p)
```

**Why this is wrong:** If a proposal repeats across cycles, it means the problem WASN'T SOLVED. Filtering it hides the signal. The user said: "Если предложение повторяется — это не спам. Это сигнал. Значит, оно НЕ БЫЛО применено. Значит, ты должен его ПРИМЕНИТЬ, а не отфильтровать."

## Solution: Shame Counter

Track how many times each proposal appeared WITHOUT producing an artifact. When count > 3, force execution.

```python
# SHAME COUNTER: Track repetitions, don't filter
shame_file = Path(CACHE_DIR) / "proposal_shame_counter.json"
shame_counter = load_json(shame_file) or {}

# Count each proposal appearance
for p in fresh_proposals:
    key_str = f"{p.action}|{p.department}|{','.join(sorted(keywords[:5]))}"
    shame_counter[key_str] = shame_counter.get(key_str, 0) + 1

save_json(shame_file, shame_counter)

# ALL proposals pass through, but repeat offenders get tagged + forced auto
for i, p in enumerate(fresh_proposals):
    count = shame_counter[key_str]
    if count > 3:
        p.description = f"[REPEATED_{count}X] {p.description}"
        p.auto = True  # MUST EXECUTE
        print(f"⚠️ SHAME: '{p.description[:60]}' appeared {count} times without artifact!")
```

## Key Properties

| Property | Value |
|----------|-------|
| **Not a filter** | All proposals pass through |
| **Sensor, not gate** | Measures "how many cycles without artifact" |
| **Escalates** | count > 3 → forced auto=true |
| **Persistent** | Survives restarts (JSON file) |
| **Visible** | Logs `[REPEATED_NX]` prefix + console warning |

## PRINCIPLE/ARTIFACT Enforcement

**Law of Three Steps** now encoded in Crystal cycle:

```python
# Cycle START
log_principle("Закон Трёх Ступеней: Понимание→Действие, Действие→Артефакт, Действие←Принцип", "crystal_full_cycle", cycle_id)

# Cycle END
log_artifact(f"cache/crystal/cycle_{cycle_id}.json", "crystal_full_cycle", cycle_id, success)
```

**Compliance tracking:** `get_principle_artifact_stats()` → `{'principles': 2, 'artifacts': 2, 'matched': 2, 'unmatched': 0}`

## Metrics from This Session

| Metric | Before | After Fix |
|--------|--------|-----------|
| Suggestions → Skills | 0.11% | Target >1% (3 days) |
| Suggestions → Goal Tasks | — | 0.27% (47/17,631) |
| Understanding → Action gap | 55% | Enforced via PRINCIPLE log |
| Action → Artifact gap | 38% | Enforced via ARTIFACT log |
| Empty action (no principle) | 28% | 0% (every cycle logs principle) |
| PRINCIPLE/ARTIFACT match | — | 100% |

## Files Modified

- `scripts/crystal/core.py`:
  - Removed `seen_keys` deduplication (lines 557-567)
  - Added shame counter with JSON persistence (lines 557-595)
  - Added PRINCIPLE log at cycle start (line 496)
  - Added ARTIFACT log at cycle end (line 655)
  - Helper functions: `log_principle()`, `log_artifact()`, `get_principle_artifact_stats()`

- `scripts/crystal/executor.py`:
  - Added PRINCIPLE log before `_execute_one()`
  - Added ARTIFACT log after (success/failure)

- `scripts/crystal/config.py`:
  - Added `PRINCIPLE_LOG = CACHE_DIR / "principle_artifact_log.jsonl"`

## Anti-Patterns to Avoid

| ❌ Wrong | ✅ Right |
|----------|----------|
| Filter duplicates to "clean up" | Count repetitions, escalate |
| `seen.add(key)` → drop | `counter[key] += 1` → if >3 force execute |
| "I already saw this" | "I saw this 4 times and didn't act" |
| Silent deduplication | Loud shame warning + forced execution |

## Related Patterns

- **Procedural Reflexes** (closed-loop-autonomy §6): Trigger → Action → Record. Shame counter is a procedural reflex on proposal stream.
- **Threshold-Based Event Accumulation** (closed-loop-autonomy §7): Not cooldown, but count-based escalation.
- **Integration Audit** (closed-loop-autonomy): Check that producer (proposer) has consumer (executor) — shame counter ensures proposals eventually get consumed.

## Usage in Other Pipelines

This pattern applies anywhere a stream of recommendations/tasks/decisions might repeat without execution:

- Goal queue: count how many cycles a goal stays `pending` without `in_progress`
- Knowledge gaps: count how many cycles a white spot stays unfilled
- Alert rules: count how many times an alert fired without resolution
- Skill evolution: count how many times a skill improvement was proposed vs applied

The rule: **Repetition without artifact = system failure. Make it visible, then force it.**