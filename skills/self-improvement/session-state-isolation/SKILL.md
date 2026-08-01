---
name: session-state-isolation
description: "Session State Isolation - full reset of transient flags on new session connection. Pattern from Mark-XLVIII: _interrupted, _vision_busy, _pending_vision etc reset completely, preventing state leakage between sessions."
tags: [session, state, isolation, transient-flags, mark-xlviii, self-healing]
version: 1.0.0
---

# Session State Isolation

## Overview
Implements session state isolation pattern from **Mark-XLVIII** (v48): "All transient vision and interrupt flags are fully reset whenever a new Gemini session connects. Previously, state from a crashed session could carry over and leave JARVIS in a broken state until restart."

## Problem
On reconnect/restart, state flags (`_interrupted`, `_vision_busy`, `_pending_vision`, `_vision_cam_active`, `_vision_close_pending`, `_vision_last_time`, `_briefing_sent`, `_conn_backoff`, `_turn_done_event`, `_api_call_count`) can leak from old session to new, leaving agent broken.

## Solution
Full reset of **transient state** on every new session connection. **Persistent state** (config, memory, logs) preserved.

## Transient Flags (always reset)

| Flag | Purpose | Default |
|------|---------|---------|
| `_interrupted` | Draining audio after user interrupt | `False` |
| `_vision_busy` | Vision capture/inject cycle in flight | `False` |
| `_pending_vision` | Pending vision request object | `None` |
| `_vision_cam_active` | Camera currently active | `False` |
| `_vision_close_pending` | Vision close requested | `False` |
| `_vision_last_time` | Last vision call timestamp (cooldown) | `0.0` |
| `_briefing_sent` | Morning briefing sent this session | `False` |
| `_conn_backoff` | Connection backoff delay | `3` |
| `_turn_done_event` | asyncio Event for turn completion | `None` |
| `_api_call_count` | API call counter for rate limiting | `0` |

## Persistent State (survives restarts)
- Configuration settings
- Memory (Knowledge Cube, USER.md, workshop, logs)
- Active persona (`cache/active_persona.json`)
- Verified fixes database
- Cron job state

## Architecture

```
New Session Connect
       |
SessionStateManager.new_session()
       |
Reset ALL transient flags to defaults
       |
Preserve persistent_state
       |
Save to cache/session_state.json (persistent only)
       |
Agent ready with clean slate
```

## Files
- `scripts/session_state_isolation.py` - Main implementation (12KB)
  - `SessionState` dataclass with transient/persistent separation
  - `SessionStateManager` singleton with thread-safe operations
  - Convenience functions: `start_new_session()`, `reset_session_transient()`, `get_session()`, `is_interrupted()`, `set_interrupted()`, `is_vision_busy()`, `can_vision()`, `mark_vision_start()`, `mark_vision_end()`
- `cache/session_state.json` - Persisted state (transient flags NOT saved)

## Usage

### Python API
```python
from scripts.session_state_isolation import (
    start_new_session, reset_session_transient, get_session,
    is_interrupted, set_interrupted, is_vision_busy, can_vision,
    mark_vision_start, mark_vision_end
)

# Start new isolated session (call at agent startup)
session = start_new_session("my_session_id")

# During work
set_interrupted(True)
set_vision_busy(True)

# On new connection / reconnect - FULL RESET
reset_session_transient()  # All transient flags to defaults

# Vision cooldown check
if can_vision(cooldown=4.0):
    mark_vision_start()
    # ... do vision ...
    mark_vision_end()

# Persistent state (survives reset)
set_persistent("user_preference", "dark_mode")
get_persistent("user_preference")  # "dark_mode"
```

### CLI
```bash
python scripts/session_state_isolation.py
# Runs demo showing transient reset behavior
```

## Integration with Mark-XLVIII Pattern
Mark-XLVIII `main.py` lines 1221-1227:
```python
# Reset transient state that must not carry over from a previous session
self._pending_vision       = None
self._vision_cam_active    = False
self._vision_close_pending = False
self._vision_busy          = False
self._vision_last_time     = 0.0
self._interrupted          = False
```

This skill generalizes that pattern for Hermes Agent.

## Integration with Persona System
- Persona switch triggers `reset_session_transient()` (soft context reset)
- Active persona persisted in `persistent_state` - survives full reset
- Persona's `temperature`, `tools_priority` applied after reset

## Integration with Forge-lite
- Forge sandbox execution runs with clean transient state
- Each `forge()` call can start with `reset_session_transient()` if needed
- Persistent forge cache (`cache/forge/`) separate from session state

## Integration with Autonomous Agent (this session)
- `autonomous_agent.py` should call `start_new_session()` at start of each cron run
- Decision matrix evaluation needs clean `_api_call_count`, `_turn_done_event`
- Error recovery: on repeated errors, call `reset_session_transient()` before retry

## Integration with Self-System (this session)
- `self_system.py --heal` should call `reset_session_transient()` 
- Proactive engine: vision cooldown pattern via `can_vision(cooldown=4.0)`
- Procedural executor: resource cooldowns use same `_vision_last_time` pattern

## Integration with Event System (this session)
- `event_daemon.py`: new event chain = `reset_session_transient()`
- Sensor array connections = new session boundary
- Kill switch triggers = immediate `reset_session_transient()` + `end_session()`

## Pitfalls & Lessons

### 1. Don't Save Transient Flags
**Problem**: Early version saved entire state including transient flags.
**Fix**: `_persist()` only saves `persistent_state` + metadata.
**Lesson**: Transient = ephemeral by definition; never serialize.

### 2. Vision Cooldown Must Reset
**Problem**: `_vision_last_time` carried over - false cooldown trigger on new session.
**Fix**: Include `_vision_last_time` in transient reset.
**Lesson**: Time-based state is transient.

### 3. Thread Safety
**Problem**: Concurrent access from async tasks and sync code.
**Fix**: `threading.RLock` on all manager operations.
**Lesson**: Singleton state manager needs locking.

### 4. Cooldown Configurable
**Problem**: Hardcoded 4s cooldown didn't work for all use cases.
**Fix**: `can_vision(cooldown_seconds=4.0)` parameter with default.
**Lesson**: Make timing parameters configurable.

## Related Skills
- `persona-system` - soft reset on persona switch
- `forge-dynamic-tools` - clean state for sandbox execution
- `procedural_executor` - deterministic chains need clean state
- `autonomous_agent` - decision matrix needs fresh transient state