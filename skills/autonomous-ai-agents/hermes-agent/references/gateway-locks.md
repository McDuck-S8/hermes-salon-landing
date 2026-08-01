# Gateway Scoped Lock Files — How They Work and How to Fix Stale Ones

## Purpose

The gateway uses scoped lock files to prevent multiple local instances from using the same external identity (e.g. Telegram bot token) simultaneously.

## Lock File Location

```
~/.local/state/hermes/gateway-locks/
```

Override via `HERMES_GATEWAY_LOCK_DIR` env var.

Format: `{scope}-{identity_hash}.lock`

Example: `telegram-bot-token-90e9f882c6aa7695.lock`

## Lock File Contents (JSON)

```json
{
  "pid": 50540,
  "kind": "hermes-gateway",
  "argv": ["D:\\path\\to\\hermes_cli\\main.py", "gateway", "run"],
  "start_time": null,
  "scope": "telegram-bot-token",
  "identity_hash": "90e9f882c6aa7695",
  "metadata": {"platform": "telegram"},
  "updated_at": "2026-06-24T05:47:14.410830+00:00"
}
```

## Stale Detection Logic

The gateway checks staleness via `gateway/status.py::acquire_scoped_lock()`:

1. If `existing_pid == os.getpid()` and start_time matches → self-lock, refresh
2. If PID doesn't exist (`_pid_exists()`) → stale
3. If PID exists but start_time differs → stale (process recycled)
4. On Windows/macOS (no `/proc`), fallback to `_looks_like_gateway_process()` and `_read_process_cmdline()` to check if the live PID is actually a gateway
5. If both oracles say "not a gateway" → stale

**Windows-specific pitfall**: `_pid_exists()` and `_get_process_start_time()` can behave differently on Windows (no `/proc`), making stale detection less reliable. Multiple stale locks can accumulate if the install was moved or HERMES_HOME changed.

## Fix: Stale Lock Files

```bash
# List locks
ls ~/.local/state/hermes/gateway-locks/

# Delete all
rm ~/.local/state/hermes/gateway-locks/*.lock

# Or delete specific scope
rm ~/.local/state/hermes/gateway-locks/telegram-bot-token-*.lock
```

## Multi-HERMES_HOME Conflicts

If you have multiple Hermes installations (e.g. portable + main), each writes locks to the SAME directory (`~/.local/state/hermes/gateway-locks/`). Different HERMES_HOME values sharing the same bot token will conflict.

Symptoms: "Telegram bot token already in use (PID XXXX)" where PID XXXX is from a DIFFERENT HERMES_HOME.

Fix: Delete the stale locks, ensure only ONE gateway uses each bot token.

## gateway_state.json (Separate Mechanism)

There's ALSO a `gateway_state.json` at `$HERMES_HOME/gateway_state.json` that tracks the gateway's lifecycle state. This is different from the scoped locks — it's per-HERMES_HOME, not per-bot-token. If the gateway gets into "startup_failed" state, you can reset it by writing clean JSON.

## Key Source Files

- `gateway/status.py:acquire_scoped_lock()` — lock acquisition + stale detection
- `gateway/status.py:_get_scope_lock_path()` — lock file path computation
- `gateway/status.py:_get_lock_dir()` — lock directory (XDG_STATE_HOME)
- `gateway/platforms/base.py:_acquire_platform_lock()` — called by each platform adapter
