# Eval Infrastructure Validation for Self-Improving Skills

## Problem Discovered (2026-07-24)

During a self-improvement cycle run via cron, 4 skills declared `self_improving: true` in their frontmatter:

| Skill | Eval Infra? | Status |
|-------|-------------|--------|
| self-improving-skills | ✅ Yes | 100% pass |
| advisor-orchestrator-worker | ✅ Yes (created this session) | 100% pass |
| ai-financial-coach | ❌ No | Cannot improve |
| always-on-agent | ❌ No | Cannot improve |

**Root cause**: Skills can declare `self_improving: true` without actually having the required eval infrastructure (`evals/cases.yaml`, `evals/rubric.md`, `evals/run_eval.py`, improvement scripts). The meta-skill had no validation step to catch this.

## Solution: Pre-Flight Validation

Added `scripts/validate_eval_infrastructure.py` that checks for required files before running improvement cycle. The validation checks:

1. `evals/cases.yaml` — test cases exist
2. `evals/rubric.md` — scoring criteria exist
3. `evals/run_eval.py` — runner exists and executable
4. `scripts/improve.py` — improvement script exists
5. `scripts/verify.py` — verification script exists
6. `scripts/patch_applier.py` — patch application script exists

## Integration into Improvement Loop

The loop now starts with validation:

```
1. VALIDATE eval infrastructure (NEW)
   └─ If missing → log warning, skip skill, report gap
2. SKILL LOADED
3. EVAL RUN
4. ANALYSIS (Gemini)
5. PATCH APPLICATION
6. VERIFICATION
```

## Usage

```python
# In self-improvement cron job or manual run:
from scripts.validate_eval_infrastructure import validate_skill

result = validate_skill(skill_path)
if not result["valid"]:
    print(f"Skipping {skill_path.name}: {result['missing']}")
    continue
# ... proceed with improvement cycle
```

## Pattern for Future Skills
## Pattern for Future Skills

When creating a new skill with `self_improving: true`, you MUST also create:

```
new-skill/
├── SKILL.md              # with self_improving: true + eval_schedule
├── evals/
│   ├── cases.yaml
│   ├── rubric.md
│   └── run_eval.py
├── scripts/
│   ├── improve.py
│   ├── verify.py
│   └── patch_applier.py
└── references/
    └── patterns.md
```

Use `templates/self-improving-skill-template/` as starting point (to be created).