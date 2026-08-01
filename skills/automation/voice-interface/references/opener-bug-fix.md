# `opener` Bug Fix (2026-07-15)

## Symptom

Voice loop (jarvis_voice_loop.py) captures speech correctly, but LLM response fails with:

```
name 'opener' is not defined
```

## Root Cause

The docstring (lines 2-20) shows example proxy configuration code:

```python
"""
JARVIS Voice Loop — VAD (Voice Activity Detection) режим.
...
proxy_handler = urllib.request.ProxyHandler({
    'http': 'http://127.0.0.1:10809',
    'https': 'http://127.0.0.1:10809'
})
opener = urllib.request.build_opener(proxy_handler)
"""
```

Line 425 (`JarvisLLM.chat()`) uses `opener.open(req, timeout=timeout)` to make HTTP requests.

Since `opener` is defined ONLY inside the docstring (as documentation/example), it's never created in runtime scope. Python correctly raises `NameError`.

## Fix

Replace `opener.open()` with `urllib.request.urlopen()` — the standard library function that's already imported locally in the method (line 397).

```python
# Before (line 425)
with opener.open(req, timeout=timeout) as resp:

# After
with urllib.request.urlopen(req, timeout=timeout) as resp:
```

## Verification

- `import urllib.request` already exists on line 397 (inside `JarvisLLM.chat()`)
- Syntax check: `python -m py_compile scripts/_deprecated/jarvis_voice_loop.py` ✅
- After fix: voice loop LLM works (rate limit permitting)

## Prevention

When copying proxy/HTTP configuration examples into docstrings, never use the same variable names as real code, or ensure real code doesn't reference docstring-only variables. Better: use placeholder variable names in examples (`_handler`, `_client`, etc.) so collisions are impossible.
