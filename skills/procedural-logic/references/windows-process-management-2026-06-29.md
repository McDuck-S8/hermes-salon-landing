# Windows Process Management — Hermes Patterns

## Problem
`os.kill(pid, 0)` doesn't reliably check process liveness on Windows.
Returns WinError 87 (invalid parameter) for valid PIDs.

## Solution: tasklist + CP1251 decode

```python
def _is_process_alive(pid: int) -> bool:
    try:
        if os.name == 'nt':
            result = subprocess.run(
                ['tasklist', '/FI', f'PID eq {pid}', '/NH'],
                capture_output=True, timeout=5,
                creationflags=0x08000000  # CREATE_NO_WINDOW
            )
            output = result.stdout.decode('cp1251', errors='replace')
            return str(pid) in output
        else:
            os.kill(pid, 0)
            return True
    except Exception:
        return False
```

## Key Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| `text=True` + tasklist | UnicodeDecodeError (CP1251 bytes → UTF-8) | Use `capture_output=True` (no text), decode manually |
| No `creationflags` | tasklist window flashes | Add `0x08000000` (CREATE_NO_WINDOW) |
| `nohup` in Git Bash | Daemon dies with parent | Use `start_new_session=True` in Popen |
| `DETACHED_PROCESS` alone | Not enough on Windows | Combine with `start_new_session=True` |
| `time.sleep(3)` for PID check | Daemon hasn't written PID yet | Poll 6x with 2s intervals (12s total) |

## Daemon Start Pattern (Windows)

```python
subprocess.Popen(
    [sys.executable, "scripts/daemon.py", "start"],
    cwd=str(WORK_DIR),
    stdout=open(os.devnull, 'w'),
    stderr=open(os.devnull, 'w'),
    stdin=open(os.devnull, 'r'),
    start_new_session=True  # Critical for Windows daemon
)
```

## Verified on
- Windows 11 + Git Bash (MSYS2)
- Python 3.13.2
- tasklist output: CP1251 encoding on Russian locale
