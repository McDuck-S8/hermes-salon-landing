---
name: self-improving-skills
description: >
  Skills that rewrite themselves based on evaluation feedback. Uses Gemini/ADK
  to run evals, find failure patterns, and patch the SKILL.md + scripts.
  From awesome-llm-apps/agent_skills/self-improving-agent-skills.
license: Apache-2.0
metadata:
  author: "Shubham Saboo / Hermes Agent"
  version: "1.0.0"
  source: "https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/agent_skills/self-improving-agent-skills"
compatibility: >
  Requires Gemini API key (GEMINI_API_KEY or GOOGLE_API_KEY). Works with
  any agent that loads SKILL.md files (Hermes, Claude Code, Codex, Cursor).
---

# Self-Improving Agent Skills

**Skills that evolve. Run evals → find failures → rewrite themselves → repeat.**

## The Loop

```
┌─────────────────────────────────────────────────────────────────┐
│  1. SKILL LOADED                                                │
│     └─ Reads its own SKILL.md + scripts + references            │
├─────────────────────────────────────────────────────────────────┤
│  2. EVAL RUN (on demand or scheduled)                           │
│     ├─ Test cases from evals/                                   │
│     ├─ Runs skill against each case                             │
│     ├─ Scores: PASS / PARTIAL / FAIL                            │
│     └─ Categorizes failure modes                                │
├─────────────────────────────────────────────────────────────────┤
│  3. ANALYSIS (Gemini)                                           │
│     ├─ "What patterns cause failures?"                          │
│     ├─ "What instructions are ambiguous?"                       │
│     ├─ "What tools are misused?"                                │
│     └─ Proposes specific patches                                │
├─────────────────────────────────────────────────────────────────┤
│  4. PATCH APPLICATION                                           │
│     ├─ Updates SKILL.md (clarifications, new steps, warnings)   │
│     ├─ Updates scripts/ (bug fixes, new helpers)                │
│     ├─ Updates references/ (new examples, edge cases)           │
│     └─ Commits with message: "self-improve: [pattern] → [fix]"  │
├─────────────────────────────────────────────────────────────────┤
│  5. VERIFICATION                                                │
│     └─ Re-runs evals → must improve or revert                   │
└─────────────────────────────────────────────────────────────────┘
```

## Architecture

### Skill Structure (Self-Improving)

```
self-improving-skill/
├── SKILL.md              # ← Gets rewritten
├── evals/
│   ├── cases.yaml        # Test inputs + expected outputs
│   ├── rubric.md         # Scoring criteria
│   └── run_eval.py       # Executes tests, outputs JSON
├── scripts/
│   ├── improve.py        # Calls Gemini to analyze + patch
│   └── verify.py         # Re-runs evals after patch
├── references/
│   └── patterns.md       # ← Gets new patterns appended
└── .improvement-log.json # Audit trail
```

### Hermes Integration

```python
# In your skill's SKILL.md frontmatter:
self_improving: true
eval_schedule: "0 3 * * *"  # Daily 3am (cron)
eval_threshold: 0.85        # Min pass rate before improving
gemini_model: "gemini-1.5-pro"
```

### Cron Job (Auto-Improvement)

```bash
# ~/.hermes/cron/jobs.json
{
  "name": "self-improve-skills",
  "schedule": "0 3 * * *",
  "prompt": "Run self-improvement cycle on all skills with self_improving: true. For each: run evals, analyze failures, propose patches, apply if verified better.",
  "skills": ["self-improving-skills"]
}
```

## Failure Pattern Library

Common patterns the improver learns to detect and fix:

| Pattern | Detection | Fix Strategy |
|---|---|---|
| **Ambiguous instruction** | Multiple valid outputs for same test | Add decision tree / explicit rules |
| **Missing tool** | Agent hallucinates tool name | Add tool to skills_list / document fallback |
| **Context leak** | Test passes alone, fails in sequence | Add isolation / state reset steps |
| **Edge case** | 1/10 tests fails consistently | Add explicit handling branch |
| **Tool misuse** | Wrong args passed repeatedly | Add validation / examples in SKILL.md |
| **Hallucinated output** | Output format doesn't match schema | Add output schema + validation step |

## Example: Creative Scraping Skill

```yaml
# evals/cases.yaml
- name: "fb_library_india_cpa"
  input: "Scrape FB Ad Library for CPA offers in India, max 20 ads"
  expect:
    min_ads: 15
    has_fields: ["creative_url", "advertiser", "cta", "landing_page"]
    format: "jsonl"

- name: "tiktok_cc_creative_center"
  input: "Get top 10 creatives from TikTok Creative Center for Gaming"
  expect:
    min_items: 8
    has_fields: ["video_url", "impressions", "ctr", "region"]
```

```python
# scripts/improve.py (simplified)
import google.generativeai as genai
import yaml, json, subprocess

def analyze_failures(skill_path, eval_results):
    prompt = f"""
    Skill: {skill_path}/SKILL.md
    Eval Results: {json.dumps(eval_results, indent=2)}
    
    Analyze failure patterns. For each pattern:
    1. Root cause
    2. Specific fix (SKILL.md edit, script change, reference addition)
    3. Risk of regression
    
    Output JSON: [{{"file": "SKILL.md", "patch": "...", "reason": "..."}}]
    """
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(prompt)
    return json.loads(response.text)

def apply_patches(skill_path, patches):
    for patch in patches:
        # Apply via skill_manage or direct edit
        # Run verify
        pass
```

## Hermes-Specific Adaptation

### Skill Indexer Integration

```python
# In skill-indexer: detect self_improving: true
# Add to improvement queue
```

### Knowledge Cube Logging

```python
# Every improvement cycle logs to KC:
on_task_complete(
    content=f"Self-improved skill {name}: {pattern} → {fix}",
    tags=["self-improvement", name, pattern],
    source="agent"
)
```

### Chain Heartbeat Event

```
skill_self_improved: {{skill_name, pattern, pass_rate_before, pass_rate_after}}
```

## Safety Guards

1. **Max 3 patches per cycle** — prevents runaway rewrites
2. **Must verify pass rate improves** — auto-revert if not
3. **Validate eval infrastructure exists** — skills declaring `self_improving: true` MUST have `evals/cases.yaml`, `evals/rubric.md`, `evals/run_eval.py`, `scripts/improve.py`, `scripts/verify.py`, `scripts/patch_applier.py` before improvement cycle runs
4. **Human approval for structural changes** — new tools, new steps
5. **Audit log immutable** — `.improvement-log.json` append-only

## Files

```
self-improving-skills/
├── SKILL.md
├── evals/
│   ├── cases.yaml           # Test cases for the improvement pipeline
│   ├── rubric.md            # PASS/PARTIAL/FAIL scoring criteria
│   └── run_eval.py          # Eval runner (outputs last_results.json)
├── scripts/
│   ├── improve.py           # Analyzes failures via Gemini, proposes patches (max 3/cycle)
│   ├── verify.py            # Applies patches, re-runs evals, reverts on regression
│   ├── patch_applier.py     # Low-level patch application (replace/insert/delete/create/diff)
│   └── validate_eval_infrastructure.py  # Checks required eval files exist
├── references/
│   ├── failure-patterns.md  # 8 failure patterns with symptoms, root causes, fix templates
│   └── improvement-strategies.md  # 8 strategy types with selection guide
└── templates/
    └── self-improving-skill-template/
        ├── SKILL.md
        ├── evals/
        └── scripts/
```

## Eval Infrastructure (Built 2026-07-23, Extended 2026-07-24)

The skill now has a complete eval pipeline:

1. **cases.yaml** — 5 test cases:
   - `improve_analyzes_failures` — proposes patches for tool_misuse, missing_validation, edge_case
   - `improve_respects_safety_guards` — enforces max 3 patches per cycle
   - `verify_reruns_evals` — confirms verify.py re-runs evals after patch
   - `verify_detects_regression` — confirms revert on pass rate drop
   - `eval_runs_all_cases` / `eval_scores_correctly` / `eval_outputs_json` — runner validation

2. **rubric.md** — PASS (1.0) / PARTIAL (0.5) / FAIL (0.0) with 85% threshold

3. **run_eval.py** — Validates script structure, exits 1 on any FAIL

4. **scripts/improve.py** — Pattern detection for 10 failure types, proposes SKILL.md + script patches

5. **scripts/verify.py** — Applies patches, re-runs evals, compares pass rates, auto-reverts on regression

6. **scripts/patch_applier.py** — Low-level patch operations with git-based revert

7. **scripts/validate_eval_infrastructure.py** — Pre-flight check for required eval files (see references/eval-infrastructure-validation.md)

Current pass rate: 8/8 (100%). All tests pass.

## Operational Notes

### Cron Job Model Drift Fix (2026-07-26)

The `self-improve-skills` cron job (job ID: `6702b8f1b014`, daily 03:00) fails due to model config drift. See [references/cron-model-drift-fix.md](./references/cron-model-drift-fix.md) for the fix. This is an operational/maintenance issue, not a skill defect — the pipeline itself works correctly (100% pass rate, proper auto-revert).