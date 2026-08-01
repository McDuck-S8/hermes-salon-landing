# Crystal Self-Model Architecture
## Date: 2026-06-13
## Epic: hermes-vjw

## Core Concept

The crystal builds a MODEL OF ITSELF each cycle. Not strings — structured data.
Each cycle the model deepens. Output ≠ input = recursive self-improvement.

## self_model.json Schema (6 sections)

- **znayu**: KC by domains (count, depth, recency, coverage)
- **umeyu**: roles (AI Agent) + skills (skills/ directory)
- **ne_znayu**: gaps in KC, isolated entities, unused skills
- **gorizonty**: what I don't know → what I can learn → what it will give
- **istoriya**: action_id, count, last_outcome, effectiveness, pattern
- **sovest**: assessments: misunderstanding (Type A/B/C) + horizon_miss + learning_direction

## Conscience Algorithm

1. efficiency = result.count / source_data.count
   - < 20%: misunderstanding
   - 20-80%: partial
   - >= 80%: full

2. Classify blindness:
   - Type A: "didn't recognize pattern" → need skill
   - Type B: "didn't understand context" → need domain knowledge
   - Type C: "didn't see horizon" → need structural analysis

3. Connect to self-expansion:
   blindness → learning_direction → skill to learn → next cycle re-reads data

## Integration into will()

- Шаг 0: _self_reflect() [existing]
- Шаг 1: historical_ids [existing]
- Шаг 1.5: _load_self_model(snap) [NEW]
- Шаг 2: predefined actions [existing]
- Шаг 3: self-expansion [existing]
- Шаг 3.5: conscience(...) [NEW]
- Шаг 4: selection (boost x1.5) [modified]
- Шаг 5: execution [existing]
- Шаг 6: _save_self_model(...) [NEW]

## Known Issues (2026-06-13, updated)

### FIXED
1. ✅ tactical_research fallback loop — added `if 'tactical_research' not in historical_ids` guard
2. ✅ Conscience evaluates only last action — now evaluates last 5 actions from history
3. ✅ umeyu.roles counts all entities (14781) — now uses `ee_types.get('AI Agent', 0)` = 269
4. ✅ ne_znayu empty — now populated (state_db: 293, NULL: 4)
5. ✅ Conscience generates same learning_direction every cycle — now has diverse candidates per type (A: 5, B: 5, C: 5, H: 5)
6. ✅ learn_* candidates are labels, not actions — now mapped to real actions via LEARNING_TO_ACTION dict + _execute_conscience_action()
7. ✅ prev_learning exhausts all candidates — now limited to last 5 assessments (sliding window)
8. ✅ HIGH efficiency actions generate no learning — added candidates_high for deepening understanding

### REMAINING
9. **connect_isolated_agents is the only working action** — after extract_*, connect_isolated_agents is the sole action that actually does something. All other phases (understand_intents, refine_intents, etc.) are analysis, not action.
10. **Conscience diversity exhausts after ~15 unique directions** — 5 type-A + 5 type-B + 5 type-C + 5 horizon + 5 high = 25 candidates total. After ~15 cycles, all exhausted. Need dynamic candidate generation based on what was LEARNED, not what was MISSED.

## Conscience: Two Blindness Types (user insight)

User corrected: "мусор это не мусор, а только непонимание того что читаешь"
- **Непонимание** (misunderstanding): I see the data but don't understand it → need skill/knowledge
- **Невидение горизонтов** (horizon miss): I understand but don't see connections/potential → need structural analysis

These are NOT "trash data" — they are signals about the crystal's own limitations.

## Key Files

- cache/self_model.json
- cache/self_model_schema.md
- cache/conscience_spec.md
- cache/integration_plan.md
- scripts/crystal.py:961+ (will)
- scripts/crystal.py:845-958 (_execute_conscience_action — executes conscience decisions)
- scripts/crystal.py:560-655 (_load_self_model)
- scripts/crystal.py:656-810 (_conscience — diverse candidates per type + HIGH efficiency)
- scripts/crystal.py:812-843 (_save_self_model)

## Debugging Pattern: Candidate Flow Tracing

When will() produces "всё сделано" (candidates empty), trace the flow:

```python
# Add targeted stderr prints:
import sys
print(f"[DEBUG] step_name: candidates={len(candidates)}", file=sys.stderr)
```

Common causes:
1. All candidates in historical_ids (already executed)
2. prev_learning from ALL assessments exhausts candidate pool → fix: limit to last N
3. Mapping mismatch (LEARNING_TO_ACTION key doesn't match learning_direction text)
4. Condition guards block candidates (e.g., `if 'X' not in historical_ids` where X is already there)

## Pitfall: Accumulated State Blocks New Candidates

self_model.sovest.assessments accumulates ALL learning_directions. After N assessments,
ALL candidates in prev_learning → no new learning_direction generated.

Fix: limit prev_learning to last 5 assessments (sliding window):
```python
assessments = self_model.get('sovest', {}).get('assessments', [])[-5:]
```

## Pattern: LEARNING_TO_ACTION Mapping

Convert abstract learning_direction → executable action:

```python
LEARNING_TO_ACTION = {
    'добавить междоменный анализ': {
        'action': 'cross_domain_analysis',
        'target': 'all_domains',
        'desc': "[совесть→действие] Междоменный анализ",
    },
    # ... more mappings
}
```

Each mapping maps to _execute_conscience_action() which runs real KC queries.
