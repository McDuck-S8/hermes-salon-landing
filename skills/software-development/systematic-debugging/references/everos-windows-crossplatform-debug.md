# Debugging Session: EverOS on Windows — Multi-Layer Investigation

## Summary

A Linux-native Python project (EverOS) refused to run on Windows. The debugging
session traced through **4 layers**: code incompatibility, process management,
lock contention, and provider API routing. Each layer revealed a new failure mode.

## Layer-by-Layer Investigation

### Layer 1: Code — `import fcntl` on Windows

**Symptom:** ModuleNotFoundError: No module named 'fcntl'

**Root Cause:** `fcntl` is POSIX-only (Linux/macOS). The project used it for
file locking without a Windows fallback.

**Fix:** Replace with `msvcrt.locking` on Windows:
```python
import platform, os

if platform.system() == "Windows":
    import msvcrt
    def _acquire_lock(fd):
        msvcrt.locking(fd.fileno(), msvcrt.LK_NBLCK, 1)
    def _release_lock(fd):
        msvcrt.locking(fd.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl
    def _acquire_lock(fd):
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    def _release_lock(fd):
        fcntl.flock(fd, fcntl.LOCK_UN)
```

**Alternative:** Use `portalocker` (cross-platform, pip-installable) — wraps
both fcntl and msvcrt internally.

### Layer 2: Process — Server won't port-bind

**Symptom:** Uvicorn fails silently or port 500 error.

**Root cause:** Previous server instance still holds the port (TIME_WAIT) or
the OME (Offline Engine) lock file persists from a killed instance.

**Diagnosis on Windows:**
```bash
# Find process on port
netstat -ano | grep 8111 | grep LISTEN

# Kill by PID
taskkill //F //PID <pid>

# Clean lock file
rm -f "C:/Users/<user>/.everos/.index/sqlite/ome.db.lock"
```

**Key difference from Linux:** `kill -9 <pid>` from git-bash on Windows does
NOT reliably kill Python processes. Always use `taskkill //F //PID`.

### Layer 3: Network — OpenRouter returns 404

**Symptom:** All API calls to OpenRouter fail with 404 "No allowed providers
are available".

**Root cause:** The `openai` Python SDK sends `x-stainless-*` headers that
OpenRouter uses for provider routing. If the routing group doesn't include
providers hosting the model, OpenRouter rejects the request.

**Fix:** Bypass OpenRouter — use the model provider's direct API:
```python
# Mistral API works with OpenAI-compatible endpoint
base_url = "https://api.mistral.ai/v1"
model = "mistral-small-latest"
# Supports function calling
```

### Layer 4: Restart loops — OME Lock contention

**Symptom:** New server instance dies immediately after starting; port is free
but lock file still exists from killed instance.

**Root cause:** OfflineMemoryEngine (OME) uses portalocker on the lock file.
A killed Python process doesn't release file locks.

**Fix:** Always clean the lock file before restarting:
```bash
rm -f ~/.everos/.index/sqlite/ome.db.lock
```

## Methodology Applied

This session followed the systematic-debugging 4-phase methodology:

- **Phase 1 (Root Cause)**: Read error message → `import fcntl` → traced to
  `locking.py` → confirmed Windows-only issue
- **Phase 2 (Pattern)**: Found `msvcrt` pattern (well-known POSIX→Windows)
- **Phase 3 (Hypothesis)**: Patched locking → tested import → worked
- **Then new Layer emerged** (process/network) → repeated Phase 1-3 at each layer

**Key lesson:** Multi-layer failures require solving each layer in sequence.
The earlier fix revealed the next layer's problem.

## Commands Quick Reference

| Task | Windows Command |
|------|----------------|
| Find process on port | `netstat -ano \| grep <port>` |
| Kill process | `taskkill //F //PID <pid>` |
| Clean OME lock | `rm -f ~/.everos/.index/sqlite/ome.db.lock` |
| Start server in bg | Python script with `.venv/Scripts/python.exe run_server.py` |
| Check health | `curl -s http://127.0.0.1:<port>/health` |
