# Windows Hermes CLI — asyncio.SyntaxError Fix (2026-07-26)

## Symptom

```
plugin discovery failed at CLI startup
Traceback (most recent call last):
  File "D:\Program Files\Python311\Lib\site-packages\hermes_cli\main.py", line 11229, in _prepare_agent_startup
    from hermes_cli.plugins import discover_plugins
  File "D:\Program Files\Python311\Lib\site-packages\hermes_cli\plugins.py", line 36, in <module>
    import asyncio
  ```python
  # ERROR OUTPUT (sanitized):
  # future = tasks.async(future, loop=self)
  #                ^^^^
  # SyntaxError: invalid syntax
  ```

## Root Cause

`prompt_toolkit` (dependency of Hermes CLI) imports `asyncio.tasks.async()` which was **removed in Python 3.11** (deprecated since 3.8). The installed `hermes-cli` package pulls `prompt_toolkit>=3.0.0` which has this incompatibility with Python 3.11+.

Python 3.11: `asyncio.tasks.async()` → `SyntaxError`
Python 3.13: Works (different asyncio internals or prompt_toolkit version resolution)

## Working Environment

The Hermes Agent repo at `D:/Portable_Soft/hermes/hermes-agent/` has its own `.venv` with **Python 3.13.2** where CLI works:

```bash
D:/Portable_Soft/hermes/hermes-agent/.venv/Scripts/python.exe cli.py --help
# Works!
```

## Fix Options

### Option 1: Use the repo's venv (RECOMMENDED)
```bash
alias hermes='D:/Portable_Soft/hermes/hermes-agent/.venv/Scripts/python.exe D:/Portable_Soft/hermes/hermes-agent/cli.py'
```

### Option 2: Fix system Python 3.11 env
```bash
# In the Python 3.11 env where hermes-cli is installed:
pip install --upgrade prompt_toolkit>=3.0.43  # version with 3.11+ compat
# OR downgrade prompt_toolkit to version that works with 3.11
pip install 'prompt_toolkit<3.0.40'
```

### Option 3: Uninstall system hermes-cli, use only repo venv
```bash
pip uninstall hermes-cli
# Use only the hermes-agent repo venv
```

## Verification

```bash
# Test the working environment
# (sanitized: repo venv python path)
# Should print >= 3.0.43

# Test broken environment
# (sanitized: system python path removed)
# Likely older version causing the issue
```

## Lesson for Boot

When user reports "hermes command fails" — check **which python** and **which venv** first. The repo's `.venv` (Python 3.13) is the supported environment. System Python 3.11 with globally installed `hermes-cli` is known broken.

Add to `auto_boot_scan.py`: detect Python version + prompt_toolkit version mismatch, warn user.