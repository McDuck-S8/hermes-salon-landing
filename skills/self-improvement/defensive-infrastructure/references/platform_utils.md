# platform_utils.py — Reference

## Purpose
Cross-platform abstractions for shell, paths, memory, disk, processes, and environment. Eliminates Windows-specific blindness and "works on my machine" bugs.

## PlatformInfo
```python
@dataclass
class PlatformInfo:
    platform: Platform        # WINDOWS, LINUX, MACOS, UNKNOWN
    system: str               # "Windows", "Linux", "Darwin"
    release: str              # e.g., "11", "6.8.0-...", "23.5.0"
    version: str              # Full version string
    machine: str              # "AMD64", "x86_64", "arm64"
    processor: str            # CPU description
    python_version: str       # "3.13.2"
    is_windows: bool
    is_linux: bool
    is_macos: bool
    is_64bit: bool
    shell: str                # "cmd.exe", "/bin/bash"
    path_separator: str       # ";" or ":"
    line_separator: str       # "\r\n" or "\n"
```

## Quick Checks
```python
from scripts.platform_utils import get_platform, is_windows, is_linux, is_macos

if is_windows():
    # Windows-specific logic
elif is_linux():
    # Linux-specific logic
```

## Directory Conventions (XDG / Windows)
```python
get_temp_dir()                    # tempfile.gettempdir()
get_home_dir()                    # Path.home()
get_config_dir(app_name)          # %APPDATA%/app, ~/.config/app, ~/Library/Application Support/app
get_data_dir(app_name)            # %LOCALAPPDATA%/app, ~/.local/share/app, ~/Library/Application Support/app
get_cache_dir(app_name)           # %LOCALAPPDATA%/app, ~/.cache/app, ~/Library/Caches/app
```

## Path Utilities
```python
expand_path(path)                 # Expands ~ and $VARS, returns resolved Path
ensure_dir(path, mode=0o755)      # Creates parents, returns Path
atomic_write(path, content)       # Temp + rename (cross-platform)
safe_read_text(path, encoding="utf-8", default="")
safe_read_json(path, default=None)
safe_write_text(path, content, encoding="utf-8") -> bool
safe_write_json(path, data, indent=2) -> bool
```

## Process Execution
```python
run_command(
    command: List[str],
    cwd: Optional[Path] = None,
    env: Dict[str, str] = None,
    timeout: int = 60,
    capture: bool = True,
    input_data: str = None,
    shell: bool = False
) -> Tuple[int, str, str]  # returncode, stdout, stderr

run_async(command, cwd, env, callback) -> subprocess.Popen
```

## Process Management
```python
kill_process(pid, force=False) -> bool
kill_process_tree(pid, force=False) -> bool  # Windows: taskkill /T, Unix: psutil
```

## Port & Network
```python
is_port_free(port, host="127.0.0.1") -> bool
find_free_port(start=8000, max_tries=100) -> int
```

## System Info
```python
get_cpu_count() -> int
get_memory_info() -> Dict  # total, available, used, percent (bytes)
get_disk_usage(path=".") -> Dict  # total, used, free (bytes)
```

## Environment
```python
get_environment() -> Dict[str, str]
set_env_var(name, value, persistent=False) -> bool  # Windows: registry if persistent
```

## CPU Affinity
```python
get_cpu_affinity() -> List[int]
set_cpu_affinity(cpus: List[int]) -> bool
```

## UI Integration
```python
open_in_browser(url) -> bool
open_file(path) -> bool  # Windows: os.startfile, macOS: open, Linux: xdg-open
```

## Test Results (2026-07-29, Windows 11)
```
Platform: Platform.WINDOWS
Is Windows: True
Shell: C:\Windows\system32\cmd.exe
Temp dir: D:\Users\Asus\AppData\Local\Temp
Home dir: C:\Users\Asus
Config dir: C:\Users\Asus\AppData\Roaming\test
Cache dir: C:\Users\Asus\AppData\Local\test
CPU count: 4
Memory: {'total': 34222538752, 'available': 20669120512, 'used': 13553418240, 'percent': 39.6}
Disk: {'total': 616589324288, 'used': 382399062016, 'free': 234190262272}
✅ run_command: rc=0, out="cross-platform works"
```

## Integration
```python
# Instead of os.chdir(), subprocess.run(), platform.system()
from scripts.platform_utils import (
    run_command, get_config_dir, get_cache_dir,
    ensure_dir, atomic_write, kill_process_tree,
    is_windows, find_free_port, get_memory_info
)

# Session start: pre-flight
config_dir = get_config_dir("myapp")
cache_dir = get_cache_dir("myapp")
ensure_dir(config_dir)
ensure_dir(cache_dir)

# Run external tool safely
code, out, err = run_command(["yt-dlp", "--version"], timeout=10)

# Kill stuck process tree
kill_process_tree(stuck_pid, force=True)

# Find free port for HTTP server
port = find_free_port(8000)
```