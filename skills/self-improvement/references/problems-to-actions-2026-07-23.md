# Problems → Actions (2026-07-23)

**User correction:** "Не список проблем. А список задач в goal_queue с конкретными сроками. Приступай."

## Rule
When the user asks you to analyze/find problems, the deliverable is ALWAYS:
1. A goal_queue task per problem (with deadline: today/tomorrow)
2. Immediate implementation — not a plan to implement later

## Bad format (before correction)
```
1. Я была слепа
2. 55% ресурсов на ошибки
3. 0.13% конверсии
```

## Good format (after correction)
```
| # | Проблема | → | Задача | Срок | Статус |
| g-005 | Порог 3→2 | → | Понизить threshold | today | ✅ DONE |
| g-001 | Слепа | → | Cross-cube audit | today | ✅ DONE |
```

## Anti-Pattern Detector
Added in self_improvement_loop.py: if same issue_type fixed >3 times across cycles, generate an **investigation finding** (not another fix). The finding says "stop patching, change approach" and suggests architectural review.

Implementation: `detect_anti_patterns()` returns investigations; they're appended to the suggestions list with severity="architecture" and tags=["anti-pattern"].

## Threshold Changes
- Skill auto-creation threshold: 3→2 (4 changes in self_improvement_loop.py)
- Severity levels: critical@5→4, high@3→2

## Cross-Cube Audit
Added in crystal.py as ФАЗА 1.5 (cross_audit()). Checks:
- EE entities with/without KC mentions
- Broken relationships (source or target entity missing)
- KC entries without axis_domain/axis_outcome
- Report saved to reports/cross-cube-audit/{date}.md

Run with: `python scripts/crystal.py --audit`
