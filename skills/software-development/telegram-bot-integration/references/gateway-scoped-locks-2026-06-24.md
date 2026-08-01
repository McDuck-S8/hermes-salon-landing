# Gateway Scoped Locks — Debugging Session 2026-06-24

## Problem
Gateway repeatedly failed with: `Telegram bot token already in use (PID 50540)`

## Investigation Path

### What DIDN'T work
1. `taskkill /PID 50540 /F` — PID doesn't exist (dead process)
2. Deleting `gateway.lock` in project root — wrong file
3. Resetting `gateway_state.json` in project root — separate state, not the lock

### What DID work
Found the actual lock in `~/.local/state/hermes/gateway-locks/`:
```
C:\Users\Asus\.local\state\hermes\gateway-locks\
├── telegram-bot-token-1d582f63bc0163cb.lock  (PID 4508, from hermes-usb-portable-main)
└── telegram-bot-token-90e9f882c6aa7695.lock  (PID 50540, from hermes-usb-portable-main)
```

Both lock files referenced `hermes-usb-portable-main` (old portable install), not the current `hermes` directory. The PIDs were dead but the lock files remained because the gateway's stale-detection couldn't confirm they were stale on Windows (no /proc filesystem).

### Lock mechanism (from gateway/status.py)
- `_get_lock_dir()` returns `~/.local/state/hermes/gateway-locks/`
- `_get_scope_lock_path(scope, identity)` returns `<lock_dir>/<scope>-<hash>.lock`
- `acquire_scoped_lock()` checks if PID is alive via `_pid_exists()`
- On Windows, falls back to `_looks_like_gateway_process()` and `_read_process_cmdline()`
- If the lock record's argv contains "gateway" and PID is alive → lock is NOT stale
- Problem: on Windows, `_get_process_start_time()` returns None (no /proc), so start_time comparison fails, and the fallback logic sometimes can't determine staleness

### Fix applied
```bash
rm ~/.local/state/hermes/gateway-locks/telegram-bot-token-*.lock
echo '{"pid":0}' > D:/Portable_Soft/hermes/gateway_state.json
```

### Result
Gateway started successfully, connected to Telegram via proxy (127.0.0.1:10806), 30 commands registered.

## Additional finding: salon bot token conflict
The salon bot (`salon_booking_bot.py`) and gateway share the same bot token (@HotelCrimeaBot). Both use long-polling. Telegram only allows ONE polling connection per token. They cannot run simultaneously.

Options documented in main skill SKILL.md.

## Python venv paths (this machine)
- hermes-agent venv: `D:/Portable_Soft/hermes/hermes-agent/venv/`
- System Python: `D:/Program Files/Python311/python.exe`
- salon bot needs system Python (has aiogram), not hermes venv
