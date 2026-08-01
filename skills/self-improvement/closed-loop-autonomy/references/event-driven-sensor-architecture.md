# Event-Driven Sensor Architecture (2026-06-22)

## Files Created This Session

| File | Lines | Purpose |
|------|-------|---------|
| `scripts/event_registry.py` | ~450 | 26 real-world events, 4 levels, detect_event(), react() |
| `scripts/event_sense.py` | ~370 | fire(), sweep(), on_user_message() — THE living nervous system |
| `scripts/sensor_array.py` | ~350 | 7 sensors: time, system, processes, files, cron, knowledge, user |
| `scripts/event_classifier.py` | ~280 | AdaptiveClassifier — handles UNKNOWN raw input only |
| `scripts/chain_executor.py` | ~570 | 40+ actions, execute_chain(), severity-based breaking |

## Key User Corrections (verbatim)

1. "Событие это как пуля попадающая в мишень. а ты предлагаешь мишени искать отверстие от пули."
   → Don't put known events into classifier patterns. Sense emits them directly.

2. "всегда что нибудь происходит!!! если ничего не происходит....это ты так думаешь...а значит ты просто умер для всех событий"
   → If sweep says "ALL QUIET", sensors are dead. Something is ALWAYS happening.

3. "МНОГОПОТОЧНО И МНОГОУРОВНЕВО И МНОГОАГЕНТНО"
   → Multi-level (L0-L3), multi-agent (spawn subagents), multi-threaded reactions.

4. "ЭТО ВСЁ СОБЫТИЯ!!! НУЖНО ТОЛЬКО ПРАВИЛЬНО РЕАГИРОВАТЬ!!!"
   → The system needs to DETECT and REACT, not classify and wait.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                    SENSOR ARRAY                       │
│  time │ system │ procs │ files │ cron │ KC │ user    │
│  (always active — something ALWAYS happens)           │
└──────────────┬──────────────────────────────────────┘
               │ event detected
               ▼
┌─────────────────────────────────────────────────────┐
│                  EVENT SENSE                          │
│  fire("disk 95%") → emit → chain → agents            │
│  sweep() → run ALL sensors → fire everything          │
│  on_user_message() → classify + fire                  │
└──────────────┬──────────────────────────────────────┘
               │ known event?
    ┌──────────┴──────────┐
    │ YES                 │ NO
    ▼                     ▼
┌──────────┐      ┌──────────────┐
│ REGISTRY │      │ CLASSIFIER   │
│ 26 events│      │ unknown input│
│ 4 levels │      │ → event type │
└────┬─────┘      └──────┬───────┘
     │                    │
     ▼                    ▼
┌─────────────────────────────────────────────────────┐
│              CHAIN EXECUTOR                           │
│  L0: block, alert, lockdown (immediate)              │
│  L1: restart, install, process (fast)                │
│  L2: analyze, assess, store (background)             │
│  L3: plan, maintain, report (periodic)               │
└─────────────────────────────────────────────────────┘
```

## CLI Commands

```bash
# Full sweep — all sensors, all events
python scripts/event_sense.py sweep

# Fire a specific event
python scripts/event_sense.py fire "заказ на стрижку"

# User message (resets silence + classifies)
python scripts/event_sense.py message "ты чатбот пиздун"

# List all events by level
python scripts/event_registry.py levels

# Detect what event this is
python scripts/event_registry.py detect "не работает прокси"

# React to an event
python scripts/event_registry.py react "скам обнаружен"

# Individual sensors
python scripts/sensor_array.py time
python scripts/sensor_array.py system
python scripts/sensor_array.py sweep
```

## Testing Results (2026-06-22)

- 9/9 chain_executor test cases pass
- 26 events in registry, all detected correctly
- 7 sensors in array, all active
- sweep() detects: time phase changes, file changes, user silence, disk/RAM issues
- fire() chains: order→5/5, scam→4/4, breakdown→ops_agent→restart
