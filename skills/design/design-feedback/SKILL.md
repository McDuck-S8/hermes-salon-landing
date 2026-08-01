---
name: design-feedback
description: "Collects feedback on design projects, learns from successes/failures, feeds signals to pattern learning system."
version: "1.0.0"
author: "Hermes Agent"
tags:
  - design
  - feedback
  - learning
  - ab-testing
  - user-testing
category: design
triggers:
  - collect feedback
  - record design outcome
  - ab test result
  - user testing
related_skills:
  - design-quality-check
  - design-critic
  - feedback-store
  - pattern-merger
---

# design-feedback

Collects feedback on design projects, learns from successes/failures, feeds signals to pattern learning system.

## Feedback Types

| Type | Source | Weight |
|------|--------|--------|
| **Automated** | Lighthouse, axe, ESLint scores | High |
| **Expert** | Design critic LLM evaluation | High |
| **User Testing** | Real user sessions, heatmaps | Very High |
| **A/B Test** | Conversion metrics, engagement | Very High |
| **Stakeholder** | Client/team approval | Medium |

## Feedback Loop

```
Design Created → Quality Check → Deploy/Deploy A/B → Collect Feedback → Record in Feedback Store → Pattern Learning
     ↑                                                                                              │
     └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Feedback Signals

| Signal | Meaning | Action |
|--------|---------|--------|
| Lighthouse score > 90 | Pattern works well | Promote to Strategic DB |
| A/B test winner | Variant outperforms | Merge winning patterns |
| axe violations > 0 | Accessibility issues | Fix → Re-evaluate |
| Conversion lift | Design drives action | Extract winning patterns |
| User drop-off | UX friction | Identify & fix weak points |

## Integration Points

| Component | Role |
|-----------|------|
| `design-quality-check` | Provides automated scores |
| `design-critic` | Provides expert evaluation |
| `feedback-store` | Stores all signals |
| `pattern-merger` | Promotes winning patterns |
| `strategic-db` | Stores promoted patterns |

## Usage

```python
from scripts.design_evaluator import DesignEvaluator
from autonomy.feedback_store import record_outcome

# Evaluate and record
evaluator = DesignEvaluator()
result = evaluator.evaluate_project(Path("project"), "my-project")

# Record outcome
record_outcome(
    pattern_id="design-pattern-123",
    outcome="success",
    confidence=0.85,
    evidence={"lighthouse": 92, "conversion_lift": 0.15}
)
```

## Learning from Feedback

- **Positive signals** → Pattern promotion (Tactical → Strategic)
- **Negative signals** → Pattern demotion or archive
- **A/B results** → Pattern variant selection
- **Expert critique** → Trend alignment scoring

---

## DOX Compliance

This skill follows the DOX framework. See AGENTS.md for contracts.