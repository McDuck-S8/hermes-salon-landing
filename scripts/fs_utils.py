#!/usr/bin/env python3
"""
Filesystem Utilities — Safe, atomic, cross-platform file operations.
Implements: defensive file I/O, atomic writes, path resolution, directory management.
"""
import os
import json
import shutil
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Optional, Union, List, Dict
from contextlib import contextmanager
from datetime import datetime

try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))


class PathError(Exception):
    """Filesystem path related errors."""
    pass


class WriteError(Exception):
    """File write related errors."""
    pass


def resolve_path(path: Union[str, Path], base: Optional[Path] = None) -> Path:
    """Resolve path to absolute, creating parents if needed."""
    p = Path(path)
    if not p.is_absolute():
        base = base or Path.cwd()
        p = (base / p).resolve()
    else:
        p = p.resolve()
    return p


def ensure_dir(path: Union[str, Path], mode: int = 0o755) -> Path:
    """Ensure directory exists, create parents if needed."""
    p = resolve_path(path)
    p.mkdir(parents=True, exist_ok=True, mode=mode)
    return p


def safe_read_text(path: Union[str, Path], encoding: str = "utf-8", errors: str = "ignore") -> str:
    """Safely read text file, returning empty string if not found."""
    p = resolve_path(path)
    try:
        return p.read_text(encoding=encoding, errors=errors)
    except FileNotFoundError:
        return ""
    except Exception:
        return ""


def safe_read_json(path: Union[str, Path], default: Any = None) -> Any:
    """Safely read JSON file, returning default if not found or invalid."""
    content = safe_read_text(path)
    if not content:
        return default
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return default


def safe_write_text(path: Union[str, Path], content: str, encoding: str = "utf-8", atomic: bool = True) -> Path:
    """
    Safely write text file with atomic operation.
    Uses temp file + rename for atomicity.
    """
    p = resolve_path(path)
    ensure_dir(p.parent)
    
    if atomic:
        # Write to temp file in same directory, then atomic rename
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=p.parent,
            delete=False,
            prefix=f".{p.name}.",
            suffix=".tmp"
        ) as tf:
            tf.write(content)
            temp_path = Path(tf.name)
        
        # Atomic rename (POSIX) or replace (Windows)
        try:
            temp_path.replace(path)
        except Exception:
            # Fallback for Windows
            if os.path.exists(path):
                os.remove(path)
            shutil.move(str(temp_path), str(path))
    else:
        p.write_text(content, encoding='utf-8')
    
    return resolve_path(path)


def safe_write_json(path: Union[str, Path], data: Any, indent: int = 2, atomic: bool = True) -> Path:
    """Safely write JSON file with atomic operation."""
    content = json.dumps(data, indent=indent, ensure_ascii=False)
    return safe_write_text(path, content, atomic=atomic)


def safe_write_bytes(path: Union[str, Path], data: bytes, atomic: bool = True) -> Path:
    """Safely write binary file with atomic operation."""
    p = resolve_path(path)
    ensure_dir(p.parent)
    
    if atomic:
        with tempfile.NamedTemporaryFile(
            mode='wb',
            dir=p.parent,
            delete=False,
            prefix=f".{p.name}.",
            suffix=".tmp"
        ) as tf:
            tf.write(data)
            temp_path = Path(tf.name)
        
        try:
            temp_path.replace(path)
        except Exception:
            if os.path.exists(path):
                os.remove(path)
            shutil.move(str(temp_path), str(path))
    else:
        p.write_bytes(data)
    
    return resolve_path(path)


def atomic_write(path: Union[str, Path], writer_fn, *args, **kwargs) -> Path:
    """
    Atomic write using a writer function.
    writer_fn(temp_path, *args, **kwargs) should write to temp_path.
    """
    p = resolve_path(path)
    ensure_dir(p.parent)
    
    with tempfile.NamedTemporaryFile(
        mode='w',
        encoding='utf-8',
        dir=p.parent,
        delete=False,
        prefix=f".{p.name}.",
        suffix=".tmp"
    ) as tf:
        temp_path = Path(tf.name)
    
    try:
        writer_fn(temp_path, *args, **kwargs)
        temp_path.replace(path)
    except Exception:
        if os.path.exists(path):
            os.remove(path)
        raise
    
    return resolve_path(path)


@contextmanager
def file_lock(path: Union[str, Path], timeout: float = 10.0, mode: str = 'w'):
    """
    File-based locking with timeout (cross-platform).
    Usage:
        with file_lock("config.json") as f:
            json.dump(data, f)
    """
    p = resolve_path(path)
    ensure_dir(p.parent)
    
    lock_path = p.with_suffix(p.suffix + ".lock")
    start = time.time()
    
    while True:
        try:
            # Try to create lock file exclusively
            # Use 'x' mode for exclusive creation (cross-platform)
            with open(lock_path, 'x') as _:
                pass
            break
        except FileExistsError:
            if time.time() - start > timeout:
                raise TimeoutError(f"Could not acquire lock on {lock_path} within {timeout}s")
            time.sleep(0.1)
    
    try:
        with open(lock_path, mode) as f:
            yield f
    finally:
        try:
            os.remove(str(lock_path))
        except:
            pass


def list_files(path: Union[str, Path], pattern: str = "*", recursive: bool = False) -> List[Path]:
    """List files matching pattern."""
    p = resolve_path(path)
    if recursive:
        return list(p.rglob(pattern))
    return list(p.glob(pattern))


def find_files(path: Union[str, Path], patterns: List[str], recursive: bool = True) -> List[Path]:
    """Find files matching any of the patterns."""
    p = resolve_path(path)
    results = []
    for pattern in patterns:
        if recursive:
            results.extend(p.rglob(pattern))
        else:
            results.extend(p.glob(pattern))
    return sorted(set(results))


def copy_tree(src: Union[str, Path], dst: Union[str, Path], overwrite: bool = False) -> Path:
    """Copy directory tree."""
    src_p = resolve_path(src)
    dst_p = resolve_path(dst)
    
    if not src_p.exists():
        raise FileNotFoundError(f"Source not found: {src_p}")
    
    if dst_p.exists():
        if overwrite:
            shutil.rmtree(dst_p)
        else:
            raise FileExistsError(f"Destination exists: {dst_p}")
    
    shutil.copytree(src_p, dst_p)
    return dst_p


def remove_tree(path: Union[str, Path], force: bool = False) -> bool:
    """Remove directory tree."""
    p = resolve_path(path)
    if not p.exists():
        return False
    
    try:
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=force)
        else:
            p.unlink()
        return True
    except Exception as e:
        if force:
            # Try harder on Windows
            try:
                subprocess.run(["rmdir", "/S", "/Q", str(p)], shell=True, check=False)
            except:
                    pass
        return False
    return False


def get_file_info(path: Union[str, Path]) -> Dict[str, Any]:
    """Get comprehensive file info."""
    p = resolve_path(path)
    if not p.exists():
        return {"exists": False}
    
    stat = p.stat()
    return {
        "exists": True,
        "path": str(p),
        "absolute": str(p.resolve()),
        "name": p.name,
        "parent": str(p.parent),
        "is_dir": p.is_dir(),
        "is_file": p.is_file(),
        "size": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "mode": oct(stat.st_mode),
    }


def atomic_json_update(path: Union[str, Path], updater_fn) -> Any:
    """
    Atomically update JSON file using a function.
    updater_fn(current_data) -> new_data
    """
    p = resolve_path(path)
    ensure_dir(p.parent)
    
    lock_path = p.with_suffix(p.suffix + ".lock")
    
    # Simple file lock
    lock_fd = None
    for _ in range(100):
        try:
            fd = os.open(str(p.with_suffix(p.suffix + ".lock")), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.close(fd)
            break
        except FileExistsError:
            time.sleep(0.05)
    else:
        raise TimeoutError("Could not acquire lock")
    
    try:
        # Read current
        current = {}
        if path.exists():
            try:
                current = json.loads(path.read_text())
            except:
                current = {}
        
        # Apply update
        new_data = updater_fn(current)
        
        # Write atomically
        safe_write_json(path, new_data)
        
        return new_data
    finally:
        try:
            os.remove(str(p.with_suffix(p.suffix + ".lock")))
        except:
            pass


def cleanup_temp_files(pattern: str = "*.tmp", max_age_hours: int = 24) -> int:
    """Clean up temporary files older than max_age_hours."""
    import time
    count = 0
    cutoff = time.time() - (max_age_hours * 3600)
    
    for tmp_file in Path("/tmp").glob("*.tmp"):
        try:
            if tmp_file.stat().st_mtime < cutoff:
                tmp_file.unlink()
                count += 1
        except:
            pass
    
    # Also clean our temp files
    for tmp_dir in [Path("/tmp"), HERMES_HOME / "tmp"]:
        if tmp_dir.exists():
            for tmp_file in tmp_dir.glob("*.tmp"):
                try:
                    if tmp_file.stat().st_mtime < cutoff:
                        tmp_file.unlink()
                        count += 1
                except:
                    pass
    
    return count


# Import time at module level
import time
import subprocess