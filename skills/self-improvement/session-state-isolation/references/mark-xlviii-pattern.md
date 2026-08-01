# Mark-XLVIII Session State Isolation Pattern

Source: `D:/Portable_Soft/hermes/Mark-XLVIII/main.py` (lines 1221-1227, 534-535, 1225-1227)

## The Pattern

In Mark-XLVIII `JarvisLive.run()` method, inside the `while True` connection loop:

```python
# Reset transient state that must not carry over from a previous session
self._pending_vision       = None
self._vision_cam_active    = False
self._vision_close_pending = False
self._vision_busy          = False
self._vision_last_time     = 0.0
self._interrupted          = False
```

This runs **on every new Gemini Live session connection** (after `client.aio.live.connect()` succeeds).

## State Variables in `__init__` (lines 534-535)

```python
self._vision_busy          = False   # True while a vision capture/inject cycle is in flight
self._interrupted          = False   # True while draining audio after user interrupt
self._vision_cam_active    = False   # Camera currently active
self._vision_close_pending = False   # Vision close requested
self._vision_last_time     = 0.0     # Timestamp for cooldown
self._pending_vision       = None    # Pending vision request
self._briefing_sent        = False   # Morning briefing sent
self._conn_backoff         = 3       # Connection backoff delay
```

## Why This Matters

1. **Crash recovery**: If session crashes mid-vision or mid-interrupt, flags stay set. On reconnect, they'd block new operations.

2. **Echo guard**: `_vision_busy` + `_vision_last_time` prevent microphone picking up JARVIS's own voice triggering recursive vision calls. Must reset on new session.

3. **Interrupt handling**: `_interrupted` drains audio queue. If set from previous session, new session starts "interrupted".

4. **Cooldown reset**: `_vision_last_time = 0.0` ensures first vision call on new session works immediately (no false 4s cooldown).

## Hermes Integration Points

| Hermes Component | Where to Apply |
|------------------|----------------|
| `autonomous_agent.py` | Start of each cron run: `start_new_session()` |
| `self_system.py` | `--heal`: `reset_session_transient()` |
| `procedural_executor.py` | Before each chain: clean transient state |
| `event_daemon.py` | New event chain = session boundary |
| `signal_daemon.py` | New signal processing = reset |
| `persona_system.py` | Persona switch = soft reset |

## Key Insight from Mark-XLVIII

> "Previously, state from a crashed session could carry over and leave JARVIS in a broken state until restart."

The fix is **not** better error handling — it's **architectural**: explicit state reset at session boundaries.