# Forge-lite Integration with Mark-XLVIII

## Mark-XLVIII Relevant Patterns

### 1. CREATE_NO_WINDOW Subprocess Patch (main.py lines 4-16)
```python
if _platform.system() == "Windows":
    _OrigPopen = _subprocess.Popen
    class _Popen(_OrigPopen):
        def __init__(self, args, **kw):
            kw["creationflags"] = kw.get("creationflags", 0) | _subprocess.CREATE_NO_WINDOW
            kw.pop("startupinfo", None)
            super().__init__(args, **kw)
    _subprocess.Popen = _Popen
```

**Forge-lite Application**: Our `run_in_sandbox()` uses `subprocess.run()` — should apply this patch on Windows to avoid terminal flash.

### 2. Session State Reset Pattern (main.py lines 1221-1227)
```python
# Reset transient state that must not carry over from a previous session
self._pending_vision       = None
self._vision_cam_active    = False
self._vision_close_pending = False
self._vision_busy          = False
self._vision_last_time     = 0.0
self._interrupted          = False
```

**Forge-lite Application**: Each `forge()` call should start with clean transient state via `reset_session_transient()`.

### 3. Vision Cooldown / Echo Guard (main.py lines 706, 711, 938, 942)
```python
if self._vision_busy or (_now - self._vision_last_time) < _cooldown:
    return  # blocked
self._vision_busy = True
# ... vision work ...
self._vision_busy = False
```

**Forge-lite Application**: Not directly applicable, but pattern of "busy flag + cooldown timestamp" could be used for forge rate limiting.

### 4. Parallel News Search (actions/web_search.py lines 165-211)
```python
# Runs Gemini grounded search AND DDG news in parallel
# Whichever delivers a valid result first wins; cancels the other
threading.Thread(target=_try_gemini, daemon=True).start()
threading.Thread(target=_try_ddg, daemon=True).start()
done_evt.wait(timeout=10.0)
```

**Forge-lite Application**: Could run multiple LLM providers in parallel for forge (DeepSeek + local fallback), first valid result wins.

## Integration Status

| Pattern | Forge-lite Status |
|---------|-------------------|
| CREATE_NO_WINDOW | ❌ Not applied (should add to `scripts/forge.py` top) |
| Session state reset | ✅ Via `session-state-isolation` skill |
| Vision cooldown | ⚠️ Not needed for forge |
| Parallel LLM | ❌ Single provider (DeepSeek) |

## Recommended Updates to `scripts/forge.py`

1. **Add CREATE_NO_WINDOW patch at top** (like Mark-XLVIII main.py)
2. **Call `reset_session_transient()` at start of `forge()`**
3. **Consider parallel provider fallback** (DeepSeek + local model)