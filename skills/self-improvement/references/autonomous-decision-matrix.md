# Autonomous Agent Decision Matrix

## 3-Tier Priority System

The autonomous agent evaluates all possible actions and picks the best one
using a priority tier + urgency × impact scoring.

### Tier 1: SURVIVE (highest priority)
System health, error resolution, critical failures.
Actions: system health check, error investigation, dependency repair.
**Always evaluated first.** If system is broken, nothing else matters.

### Tier 2: LEARN (medium priority)
Knowledge growth, gap filling, skill evolution.
Actions: Knowledge Cube expansion, gap analysis, pattern extraction.
**Evaluated when system is healthy.**

### Tier 3: PRODUCE (user-facing priority)
Content generation, reports, user-valuable outputs.
Actions: daily reports, Telegram content, business analysis.
**Evaluated when knowledge is sufficient.**

## Scoring Formula

```
score = (urgency × 0.4) + (impact × 0.6)
```

- **urgency** (1-5): How time-sensitive is this? Errors=5, gaps=3, reports=1
- **impact** (1-10): How much value does this produce? KC growth=6, error fix=8

The agent picks the highest-scoring action across ALL tiers.
SURVIVE actions get a tier bonus: `score += 2` if system has errors.

## Context Signals That Adjust Scores

- **4 Telegram channels detected** → PRODUCE content scores +1
- **Beauty salon business detected** → PRODUCE business analysis scores +2
- **KC white spots > 50%** → LEARN gap-filling scores +2
- **Recent errors > 3 unique** → SURVIVE scores +3
- **All cron jobs healthy** → SURVIVE scores -2 (deprioritize)

## Implementation (autonomous_agent.py)

```python
# Candidate actions evaluated:
candidates = []

# Tier: SURVIVE
if errors:
    candidates.append({"action": "fix_errors", "tier": "SURVIVE",
                        "urgency": 5, "impact": 8})
else:
    candidates.append({"action": "health_check", "tier": "SURVIVE",
                        "urgency": 1, "impact": 1})

# Tier: LEARN
if white_spots > 0.5:
    candidates.append({"action": "explore_gaps", "tier": "LEARN",
                        "urgency": 3, "impact": 6})
candidates.append({"action": "grow_cube", "tier": "LEARN",
                    "urgency": 2, "impact": 5})

# Tier: PRODUCE
if user_has_channels:
    candidates.append({"action": "telegram_content", "tier": "PRODUCE",
                        "urgency": 1, "impact": 3})
if user_has_business:
    candidates.append({"action": "business_analysis", "tier": "PRODUCE",
                        "urgency": 1, "impact": 4})

# Pick best
best = max(candidates, key=lambda c: c["urgency"] * 0.4 + c["impact"] * 0.6)
```

## Key Design Principles

1. **System always checks itself first** — SURVIVE before everything
2. **User context adjusts priorities** — channels/business detected = produce more
3. **Knowledge gaps drive learning** — white spots in KC = learn more
4. **Score-based, not rule-based** — any action can win if score is highest
5. **Logged to agent_decisions.json** — every decision recorded for audit

## Log File Performance (Critical)

When reading logs for error detection:
- **NEVER read entire log file** — can be 14K+ lines, hangs Python
- **ALWAYS use `tail -n 50`** via subprocess — reads only last 50 lines
- **Deduplicate by fingerprint** — same error repeating = 1 unique error

```python
# WRONG — hangs on large files:
with open("errors.log") as f:
    lines = f.readlines()  # 14,856 lines = DEATH

# RIGHT — fast, last 50 lines only:
import subprocess
result = subprocess.run(["tail", "-n", "50", "errors.log"],
                        capture_output=True, text=True, timeout=5)
lines = result.stdout.splitlines()
```
