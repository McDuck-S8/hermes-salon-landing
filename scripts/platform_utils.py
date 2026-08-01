#!/usr/bin/env python3
"""
Platform Abstraction Layer — Cross-platform utilities for Hermes.
Provides: process management, file operations, environment detection, path handling.
"""

import os
import sys
import platform
import shutil
import subprocess
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass
from enum import Enum


class Platform(Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "darwin"
    UNKNOWN = "unknown"


@dataclass
class PlatformInfo:
    platform: Platform
    system: str
    release: str
    version: str
    machine: str
    processor: str
    python_version: str
    is_windows: bool
    is_linux: bool
    is_macos: bool
    is_64bit: bool
    shell: str
    path_separator: str
    line_separator: str


def get_platform_info() -> PlatformInfo:
    """Get comprehensive platform information."""
    system = platform.system().lower()
    
    if system == "windows":
        plat = Platform.WINDOWS
    elif system == "linux":
        plat = Platform.LINUX
    elif system == "darwin":
        plat = Platform.MACOS
    else:
        plat = Platform.UNKNOWN
    
    is_64bit = sys.maxsize > 2**32
    
    # Determine default shell
    if plat == Platform.WINDOWS:
        shell = os.environ.get("COMSPEC", "cmd.exe")
    else:
        shell = os.environ.get("SHELL", "/bin/bash")
    
    return PlatformInfo(
        platform=plat,
        system=platform.system(),
        release=platform.release(),
        version=platform.version(),
        machine=platform.machine(),
        processor=platform.processor(),
        python_version=platform.python_version(),
        is_windows=(plat == Platform.WINDOWS),
        is_linux=(plat == Platform.LINUX),
        is_macos=(plat == Platform.MACOS),
        is_64bit=is_64bit,
        shell=shell,
        path_separator=os.pathsep,
        line_separator=os.linesep,
    )


PLATFORM_INFO = get_platform_info()


def get_platform() -> Platform:
    """Get current platform enum."""
    return PLATFORM_INFO.platform


def is_windows() -> bool:
    return PLATFORM_INFO.is_windows


def is_linux() -> bool:
    return PLATFORM_INFO.is_linux


def is_macos() -> bool:
    return PLATFORM_INFO.is_macos


def get_shell() -> str:
    """Get default shell for current platform."""
    return PLATFORM_INFO.shell


def which(command: str) -> Optional[str]:
    """Cross-platform which/where command."""
    return shutil.which(command)


def find_executable(name: str, paths: List[str] = None) -> Optional[Path]:
    """Find executable in PATH or custom paths."""
    if paths is None:
        paths = os.environ.get("PATH", "").split(os.pathsep)
    
    exts = [".exe", ".cmd", ".bat", ".ps1"] if PLATFORM_INFO.is_windows else [""]
    
    for path in paths:
        p = Path(path)
        if not p.exists():
            continue
        for ext in exts:
            candidate = p / f"{name}{ext}"
            if candidate.exists() and candidate.is_file():
                if os.access(candidate, os.X_OK):
                    return candidate
    return None


def get_temp_dir() -> Path:
    """Get platform-appropriate temp directory."""
    return Path(tempfile.gettempdir())


def get_home_dir() -> Path:
    """Get user home directory."""
    return Path.home()


def get_config_dir(app_name: str = "hermes") -> Path:
    """Get platform-appropriate config directory."""
    if PLATFORM_INFO.is_windows:
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif PLATFORM_INFO.is_macos:
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / app_name


def get_data_dir(app_name: str = "hermes") -> Path:
    """Get platform-appropriate data directory."""
    if PLATFORM_INFO.is_windows:
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif PLATFORM_INFO.is_macos:
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / app_name


def get_cache_dir(app_name: str = "hermes") -> Path:
    """Get platform-appropriate cache directory."""
    if PLATFORM_INFO.is_windows:
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif PLATFORM_INFO.is_macos:
        base = Path.home() / "Library" / "Caches"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return base / app_name


def expand_path(path: Union[str, Path]) -> Path:
    """Expand user and environment variables in path."""
    path_str = str(path)
    path_str = os.path.expanduser(path_str)
    path_str = os.path.expandvars(path_str)
    return Path(path_str).resolve()


def ensure_dir(path: Union[str, Path], mode: int = 0o755) -> Path:
    """Ensure directory exists."""
    p = Path(path).expanduser().resolve()
    p.mkdir(parents=True, exist_ok=True, mode=mode)
    return p


def atomic_write(path: Union[str, Path], content: Union[str, bytes], mode: str = 'w') -> Path:
    """Atomically write file using temp + rename."""
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Determine if content is bytes or text
    is_bytes = isinstance(content, bytes)
    mode_suffix = 'b' if 'b' not in mode and is_bytes else ''
    
    with tempfile.NamedTemporaryFile(
        mode=mode + mode_suffix,
        dir=path.parent,
        delete=False,
        prefix=f".{Path(mode).name}.",
        suffix=".tmp"
    ) as tf:
        tf.write(content)
        temp_path = Path(tf.name)
    
    try:
        temp_path.replace(Path(path))
    except Exception:
        # Fallback for Windows
        target = Path(mode)
        if target.exists():
            target.unlink()
        shutil.move(str(temp_path), str(path))
    
    return Path(mode)


def safe_read_text(path: Union[str, Path], encoding: str = "utf-8", default: str = "") -> str:
    """Safely read text file, returning default on error."""
    try:
        return Path(path).read_text(encoding=encoding)
    except Exception:
        return default


def safe_read_json(path: Union[str, Path], default: Any = None) -> Any:
    """Safely read JSON file."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default


def safe_write_text(path: Union[str, Path], content: str, encoding: str = "utf-8") -> bool:
    """Safely write text file."""
    try:
        Path(path).write_text(content, encoding=encoding)
        return True
    except Exception:
        return False


def safe_write_json(path: Union[str, Path], data: Any, indent: int = 2) -> bool:
    """Safely write JSON file."""
    try:
        Path(path).write_text(json.dumps(data, indent=indent, ensure_ascii=False))
        return True
    except Exception:
        return False


def run_command(
    command: List[str],
    cwd: Optional[Path] = None,
    env: Dict[str, str] = None,
    timeout: int = 60,
    capture: bool = True,
    input_data: str = None,
    shell: bool = False
) -> Tuple[int, str, str]:
    """
    Run command with cross-platform handling.
    Returns: (returncode, stdout, stderr)
    """
    if isinstance(command, str):
        # On Windows, shell=True may be needed for built-ins
        if PLATFORM_INFO.is_windows and not isinstance(command, list):
            shell = True
    
    env_vars = os.environ.copy()
    if env:
        env_vars.update(env)
    
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            env=env,
            capture_output=capture,
            text=True,
            timeout=timeout,
            shell=shell,
            input=input_data if input_data else None,
            creationflags=subprocess.CREATE_NO_WINDOW if PLATFORM_INFO.is_windows else 0
        )
        return result.returncode, result.stdout or "", result.stderr or ""
    except subprocess.TimeoutExpired:
        return -1, "", f"Timeout after {timeout}s"
    except FileNotFoundError:
        return -1, "", "Command not found"
    except Exception as e:
        return -1, "", str(e)


def run_async(
    command: List[str],
    cwd: Optional[Path] = None,
    env: Dict[str, str] = None,
    callback: Callable[[int, str, str], None] = None
) -> subprocess.Popen:
    """Run command asynchronously with callback."""
    env_vars = os.environ.copy()
    if env:
        env_vars.update(env)
    
    proc = subprocess.Popen(
        command,
        cwd=str(cwd) if cwd else None,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        creationflags=subprocess.CREATE_NO_WINDOW if PLATFORM_INFO.is_windows else 0
    )
    
    if callback:
        def reader():
            stdout, stderr = proc.communicate()
            callback(proc.returncode, stdout or "", stderr or "")
        threading.Thread(target=reader, daemon=True).start()
    
    return proc


def kill_process(pid: int, force: bool = False) -> bool:
    """Kill process by PID cross-platform."""
    try:
        if PLATFORM_INFO.is_windows:
            flags = "/F" if force else ""
            subprocess.run(["taskkill", "/PID", str(pid), "/T", flags], capture_output=True)
        else:
            os.kill(pid, signal.SIGKILL if force else signal.SIGTERM)
        return True
    except Exception:
        return False


def kill_process_tree(pid: int, force: bool = False) -> bool:
    """Kill process and all children."""
    try:
        if PLATFORM_INFO.is_windows:
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F" if force else ""], capture_output=True)
        else:
            import psutil
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                child.kill() if force else child.terminate()
            parent.kill() if force else parent.terminate()
        return True
    except Exception:
        return False


def is_port_free(port: int, host: str = "127.0.0.1") -> bool:
    """Check if TCP port is free."""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            return s.connect_ex((host, port)) != 0
    except Exception:
        return False


def find_free_port(start: int = 8000, max_tries: int = 100) -> int:
    """Find a free TCP port."""
    for port in range(start, start + max_tries):
        if is_port_free(port):
            return port
    raise RuntimeError(f"No free port found in range {start}-{start + max_tries}")


def get_cpu_count() -> int:
    """Get CPU core count."""
    return os.cpu_count() or 1


def get_memory_info() -> Dict[str, int]:
    """Get memory info in bytes."""
    try:
        import psutil
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent,
        }
    except ImportError:
        return {"total": 0, "available": 0, "used": 0, "percent": 0}


def get_disk_usage(path: Union[str, Path] = ".") -> Dict[str, int]:
    """Get disk usage for path."""
    try:
        usage = shutil.disk_usage(path)
        return {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
        }
    except Exception:
        return {"total": 0, "used": 0, "free": 0}


def open_in_browser(url: str) -> bool:
    """Open URL in default browser."""
    try:
        import webbrowser
        return webbrowser.open(url)
    except Exception:
        return False


def open_file(path: Union[str, Path]) -> bool:
    """Open file with default application."""
    try:
        if PLATFORM_INFO.is_windows:
            os.startfile(path)
        elif PLATFORM_INFO.is_macos:
            subprocess.run(["open", path], check=True)
        else:
            subprocess.run(["xdg-open", path], check=True)
        return True
    except Exception:
        return False


def get_environment() -> Dict[str, str]:
    """Get environment variables."""
    return dict(os.environ)


def set_env_var(name: str, value: str, persistent: bool = False) -> bool:
    """Set environment variable."""
    try:
        os.environ[name] = value
        if persistent and PLATFORM_INFO.is_windows:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
            winreg.CloseKey(key)
        return True
    except Exception:
        return False


def get_cpu_affinity() -> List[int]:
    """Get CPU affinity mask."""
    try:
        import psutil
        p = psutil.Process()
        return p.cpu_affinity()
    except:
        return list(range(os.cpu_count() or 1))


def set_cpu_affinity(cpus: List[int]) -> bool:
    """Set CPU affinity for current process."""
    try:
        import psutil
        p = psutil.Process()
        p.cpu_affinity(cpus)
        return True
    except:
        return False


# Singleton platform info
PLATFORM_INFO = get_platform_info()


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python platform_utils.py <command>")
        print("Commands: info, which <cmd>, shell, temp, home, config, cache, run <cmd...>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "info":
        info = get_platform_info()
        print(json.dumps(asdict(info), indent=2))
    
    elif cmd == "which":
        if len(sys.argv) < 3:
            print("Usage: which <command>")
            sys.exit(1)
        result = which(sys.argv[2])
        print(result or "Not found")
    
    elif cmd == "shell":
        print(get_shell())
    
    elif cmd == "temp":
        print(get_temp_dir())
    
    elif cmd == "home":
        print(get_home_dir())
    
    elif cmd == "config":
        app = sys.argv[2] if len(sys.argv) > 2 else "hermes"
        print(get_config_dir(app))
    
    elif cmd == "cache":
        app = sys.argv[2] if len(sys.argv) > 2 else "hermes"
        print(get_cache_dir(app))
    
    elif cmd == "run":
        if len(sys.argv) < 3:
            print("Usage: run <command> [args...]")
            sys.exit(1)
        code, out, err = run_command(sys.argv[2:])
        print(f"Exit: {code}")
        if out: print(f"OUT:\n{out}")
        if err: print(f"ERR:\n{err}")
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()