# User Voice Proactivity Pattern (2026-07-23)

**Source 1 of 3 proactivity sources — User Voice (principal).**

## Concept

Every user message carries signal: satisfaction, correction, demand, frustration, or neutral.
The system scans each message immediately after recording and adjusts agent behavior.

## Detection: `scripts/proactive_voice.py`

| Signal | Keywords | Action |
|--------|----------|--------|
| **Positive** | огонь, круто, отлично, молодец, супер, класс | Continue, increase autonomy |
| **Correction** | не X, а Y, неправильно, стоп, исправь, переделай, не то | Record commitment, switch approach |
| **Preference** | я предпочитаю, мне нравится, всегда делай X | Save as durable rule |
| **Demand** | сделай сейчас, срочно, начинай, немедленно | Auto-prioritize, execute |
| **Frustration** | блять, херня, опять, снова, ничего не работает | Log as high importance, escalate |

## Signal → Behavior Adjustment

Every session start, `auto_boot_scan.py` reads the signal and adjusts behavior:

| Signal | Agent Instruction |
|--------|------------------|
| `positive` | "Продолжаю. Усилить автономность." |
| `correction` | "Двойная проверка перед действиями. Не спешить." |
| `frustration` | "Извиниться. Объяснить что исправлено. Ускорить." |
| `demand` | "Выполнить без вопросов. Немедленно." |
| `neutral` | "Стандартный режим. Следовать контракту." |

The adjustment is stored in `cache/session_bridge.json` under `behavior_adjustment`:

```json
{
  "behavior_adjustment": {
    "signal": "correction",
    "instruction": "Двойная проверка перед действиями. Не спешить.",
    "applied_at": "2026-07-23T16:24:35"
  }
}
```

## Integration

```python
# record_user_to_kc.py — after recording message to KC:
from proactive_voice import process_user_message
result = process_user_message(msg)

# auto_boot_scan.py — at every session start:
signal, adjustment = read_voice_signal_and_adjust()
print(f"🎯 VOICE SIGNAL: {signal}")
print(f"   {adjustment}")
```

## Files

- `scripts/proactive_voice.py` — detection logic (corrections, preferences, demands, frustrations)
- `scripts/auto_boot_scan.py` — behavior adjustment application via `read_voice_signal_and_adjust()`
- `scripts/record_user_to_kc.py` — triggers proactive_voice on every user message
- `scripts/morning_report.py` — aggregate user voice stats per 24h

## Principle

Signal → storage is NOT a closed loop. Signal → storage → consumption → behavior change IS.
Every session starts with the behavior instruction from the last user interaction.
