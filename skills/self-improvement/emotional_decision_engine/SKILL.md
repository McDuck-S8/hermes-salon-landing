---
name: emotional_decision_engine
description: "Emotional Decision Engine for User Learner — 5-dimensional emotional state tracking (valence, arousal, connection, curiosity, energy) + decision heuristics registry. Adapts responses based on user triggers using Clarence's emotional architecture from 'On Becoming'."
trigger: "On user trigger phrases, on response generation, on learning cycle"
usage: emotional_decision_engine
---

# Emotional Decision Engine

Implements Clarence's emotional architecture for agents: 5-dimensional emotional state + decision heuristics registry.

## Architecture

```
Trigger Phrase → update_emotional_state() → get_applicable_heuristics() → apply_emotional_adaptation()
```

## 5 Emotional Dimensions

| Dimension | Range | Meaning |
|---|---|---|
| `valence` | -1.0 → 1.0 | Pleasure/displeasure |
| `arousal` | 0.0 → 1.0 | Activation level |
| `connection` | -1.0 → 1.0 | Social connection/isolation |
| `curiosity` | 0.0 → 1.0 | Exploration drive |
| `energy` | 0.0 → 1.0 | Available resources |

## Trigger → Emotional Mapping

| Trigger Category | Example Triggers | Valence | Arousal | Connection | Curiosity | Energy |
|---|---|---|---|---|---|---|
| **Negative/Frustration** | "не то", "не понял", "неправильно", "ты уже это говорил" | -0.7 | 0.8 | -0.3 | 0.5 | 0.5 |
| **Positive/Affirmation** | "спасибо", "правильно", "хорошо", "молодец" | 0.6 | 0.4 | 0.4 | 0.5 | 0.5 |
| **Curiosity** | "как", "почему", "что за", "объясни" | 0.0 | 0.5 | 0.0 | 0.8 | 0.6 |
| **Time Pressure** | "быстро", "сейчас", "срочно", "мгновенно" | 0.0 | 0.9 | 0.0 | 0.5 | 0.9 |

## Decision Heuristics Registry

Stored in `decision_heuristics` table:

| Heuristic | Pattern | Priority | Action |
|---|---|---|---|
| `concise_on_repetition` | "ты уже это говорил" | 10 | "Понял. Не повторю. {response}" |
| `direct_response_to_frustration` | "не то\|не понял\|неправильно" | 10 | Direct style via adapt_response_style |
| `russian_only` | `.*` | 5 | Language enforcement |
| `short_on_time_pressure` | "быстро\|сейчас\|срочно" | 8 | Length limit (3 sentences) |
| `direct_on_quality_demand` | "качествен\|правильно\|как надо" | 7 | Direct style |

## Usage

```python
from user_learner import apply_emotional_adaptation, register_default_heuristics

# Register default heuristics (run once)
register_default_heuristics()

# Apply to response
adapted = apply_emotional_adaptation(
    base_response="Я думаю, что возможно стоит попробовать...",
    trigger_phrase="ты уже это говорил",
    context="Graphify discussion"
)
# Returns: "Понял. Не повторю. Я думаю, что возможно стоит попробовать..."
```

## Default Heuristics (auto-registered)

```python
register_default_heuristics()  # Call once at startup
```

## Integration Points

1. **User Learner** → calls `apply_emotional_adaptation()` before sending response
2. **Trigger Detection** → "ты уже это говорил" → emotional state update + heuristic
3. **Crystal** → reads emotional state for Priority Engine weighting

## Database Schema (user_learner.db)

```sql
-- Emotional state history
emotional_state (valence, arousal, connection, curiosity, energy, trigger_phrase, context, occurred_at)

-- Heuristics registry
decision_heuristics (heuristic_name, condition_pattern, action_template, priority, success_count, failure_count)

-- Application log
heuristic_applications (heuristic_id, trigger_phrase, context, adapted_response, user_feedback, applied_at)
```

---

**Created:** 2026-07-30
**Version:** 1.0
**Author:** Hermes Agent