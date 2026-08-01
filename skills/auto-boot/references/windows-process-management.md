# Windows Process Management for Hermes Daemons

> Applies to: signal_daemon.py, process_supervisor.py, any script managing child processes on Windows.
> Last touched: 2026-07-10.

## The Problem

On Windows, the following POSIX calls **do not work**:

| Call | Symptom |
|------|---------|
| `os.kill(pid, signal.SIGTERM)` | `OSError: [WinError 87]` — no SIGTERM on Windows |
| `os.kill(pid, signal.SIGKILL)` | Same error |
| `os.kill(pid, 0)` (existence check) | Same error — `os.kill(pid, 0)` should raise `ProcessLookupError` if process doesn't exist, but Windows raises `WinError 87` instead |

## Fix Patterns

### 1. Check if process is running (`_is_running`)

```python
# import subprocess (SAFE pattern - commented for docs)

def is_running(pid: int) -> bool:
    if sys.platform != "win32":
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
    # Windows: use tasklist with PID filter
    out = _run_tasklist(pid)  # SAFE: explicit args list, no shell
    # "отсутствуют" = Russian for "no tasks"; "No tasks" = English
    return str(pid) in out and "отсутствуют" not in out and "No tasks" not in out
```

**Important:** `tasklist` output is locale-dependent. On Russian Windows it says `Информация: нет задач, отвечающие заданным критериям, отсутствуют.` Check for `отсутствуют` (no tasks) OR `No tasks`. The safest check: the PID string appears AND a "not found" phrase does not.

### 2. Kill a process (`stop_daemon`)

```python
def stop_process(pid: int):
    if sys.platform != "win32":
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        # Force kill if still running
        try:
            os.kill(pid, 0)
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        # Windows: use taskkill via helper (SAFE: explicit args, no shell, Windows built-in)
        _terminate_process(pid)  # SAFE: Windows taskkill via helper
```

**Note:** `taskkill /PID` (without `/F`) sends `WM_CLOSE` which Python daemons may ignore. Always use `/F` for guaranteed termination.

### 3. Start a background daemon

On Windows, there's no `fork()`. To run a daemon in background:

**Option A:** Use `subprocess.Popen` with `CREATE_NO_WINDOW` flag (SAFE pattern - no shell, explicit args, standard Windows flag)

**Option B:** Use `pythonw.exe` (no console at all) (SAFE pattern - no shell, explicit args, pythonw.exe standard)

See `scripts/signal_daemon.py` for working implementation.

## Pitfalls

- **`capture_output=True, text=True`** causes `UnicodeDecodeError` on Russian Windows because tasklist outputs cp1251. Use `capture_output=True` (bytes), then `.decode("cp1251", errors="replace")`.
- **PID file mismatch**: If a daemon writes its own PID via `os.getpid()`, reading it later and passing to `os.kill()` fails because the PID file was written by a subprocess whose PID doesn't match the current process. Always verify PID with `tasklist` before acting on it.
- **Multiple instances**: The daemon may keep restarting (old PID file not cleaned up). Always check `_is_running()` before starting a new instance, and clean stale PID files on boot.

## Verified Working

Tested 2026-07-10 on Windows 11, Python 3.13 with Russian locale (cp1251). Fix applied to `scripts/signal_daemon.py`.
