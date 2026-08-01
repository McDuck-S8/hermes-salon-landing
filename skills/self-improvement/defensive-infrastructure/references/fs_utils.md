# fs_utils.py — Reference

## Purpose
Atomic, safe, cross-platform file I/O. Eliminates partial writes, corruption, race conditions.

## Key Functions

### Path Resolution
```python
resolve_path(path, base=None) -> Path
ensure_dir(path, mode=0o755) -> Path
```

### Safe Reads
```python
safe_read_text(path, encoding="utf-8", errors="ignore") -> str
safe_read_json(path, default=None) -> Any
```

### Atomic Writes
```python
safe_write_text(path, content, encoding="utf-8", atomic=True) -> Path
safe_write_json(path, data, indent=2, atomic=True) -> Path
safe_write_bytes(path, data, atomic=True) -> Path
atomic_write(path, writer_fn, *args, **kwargs) -> Path
```

### Atomic JSON Update (read-modify-write atomically)
```python
atomic_json_update(path, updater_fn) -> Any
# Usage: atomic_json_update("config.json", lambda d: {**d, "new": "value"})
```

### File Locking (cross-platform)
```python
@contextmanager
def file_lock(path, timeout=10.0, mode="w"):
    # Uses exclusive-create ('x' mode) for portability
    yield file_handle
```

### Listing & Finding
```python
list_files(path, pattern="*", recursive=False) -> List[Path]
find_files(path, patterns, recursive=True) -> List[Path]
```

### File Info
```python
get_file_info(path) -> Dict
cleanup_temp_files(pattern="*.tmp", max_age_hours=24) -> int
```

## Windows Notes
- Uses `open(path, 'x')` for exclusive locking (no `fcntl`)
- `atomic_write` uses temp file + `replace()` (POSIX) / `shutil.move()` fallback (Windows)
- All paths resolved via `Path.resolve()` for consistency

## Test Results (2026-07-29)
```
✅ Atomic write: SUCCESS
✅ Atomic JSON update: SUCCESS (counter 0→3)
✅ File lock + data persist: SUCCESS
✅ Safe read/write text/JSON: SUCCESS
```