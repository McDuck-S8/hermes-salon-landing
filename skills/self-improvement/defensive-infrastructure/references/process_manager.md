# process_manager.py — Reference

## Purpose
Safe subprocess execution with heartbeat monitoring, timeout handling, graceful shutdown, and restart logic. Eliminates subprocess hangs, orphaned processes, and uncontrolled timeouts.

## Key Classes

### ProcessConfig
```python
@dataclass
class ProcessConfig:
    command: List[str]              # Command and args
    cwd: Optional[Path] = None      # Working directory
    env: Dict[str, str] = None      # Environment variables
    timeout: int = 300              # Seconds
    heartbeat_interval: int = 30    # Heartbeat interval (for future)
    restart_on_failure: bool = False
    max_restarts: int = 3
    capture_output: bool = True
    stdin_data: str = None
    env_vars: Dict[str, str] = None
```

### ProcessInfo
```python
@dataclass
class ProcessInfo:
    id: str
    config: ProcessConfig
    state: ProcessState  # STARTING, RUNNING, COMPLETED, FAILED, TIMEOUT, KILLED, ZOMBIE
    pid: Optional[int] = None
    returncode: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    started_at: float = 0
    ended_at: Optional[float] = None
    heartbeat_count: int = 0
    last_heartbeat: float = 0
    restart_count: int = 0
    error: str = ""
    metadata: Dict = None
```

### ProcessManager
```python
manager = ProcessManager()  # Singleton via get_process_manager()

# Start process
pid = manager.start_process(config, process_id="optional-id")

# Get info
info = manager.get_process(pid)
info = manager.wait_for_process(pid, timeout=10)  # Blocks until done

# List all
processes = manager.list_processes()

# Stats
stats = manager.get_stats()
# {'total': 5, 'by_state': {'completed': 3, 'failed': 1, 'timeout': 1}, 'running': 0, ...}

# Cleanup
removed = manager.cleanup_completed(max_age_hours=24)

# Kill
manager.kill_process(pid, force=False)
```

### ProcessState Enum
```
STARTING -> RUNNING -> COMPLETED (returncode=0)
                   -> FAILED (returncode!=0)
                   -> TIMEOUT (exceeded config.timeout)
                   -> KILLED (manual kill)
                   -> ZOMBIE (detected orphan)
```

## Features
- **Heartbeat monitoring**: Tracks last_heartbeat, heartbeat_count for running processes
- **Timeout enforcement**: Uses `subprocess.run(timeout=)` with kill on expiry
- **Graceful shutdown**: `kill_process()` marks state, process thread handles cleanup
- **Auto-restart**: `restart_on_failure=True` + `max_restarts` retries with 2s delay
- **Thread-safe**: All operations under `RLock`
- **Cross-platform**: Uses `CREATE_NO_WINDOW` on Windows, standard signals on Unix

## Convenience Function
```python
from scripts.process_manager import run_command

code, stdout, stderr = run_command(
    ["python", "-c", "print('hello')"],
    cwd=Path("/tmp"),
    timeout=30,
    env={"MY_VAR": "value"}
)
```

## Test Results (2026-07-29)
```
✅ Normal completion: rc=0, state=COMPLETED, stdout="DONE"
✅ Timeout handling: state=TIMEOUT, error="Timeout after 1s"
✅ Stats tracking: {'total': 2, 'by_state': {'completed': 1, 'timeout': 1}, 'running': 0}
```

## Integration
```python
# In any script needing reliable subprocess
from scripts.process_manager import get_process_manager, ProcessConfig

mgr = get_process_manager()
config = ProcessConfig(
    command=["python", "script.py"],
    timeout=60,
    capture_output=True
)
pid = mgr.start_process(config)
info = mgr.wait_for_process(pid, timeout=70)
if info.returncode != 0:
    handle_failure(info)
```