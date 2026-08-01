# Goal Executor Fix (2026-07-28)

## Issue
Test `test_4_goal_executor_returns_action` failed because `execute_goal()` tried to run `python "D:/Portable_Soft/hermes/projects/salon-bot/main.py"` with `shell=False`, but the command string wasn't split into arguments. The salon-bot `main.py` also needed `aiogram` installed in the Hermes venv.

## Root Cause
1. `derive_action()` returned command strings like `python "D:/Portable_Soft/hermes/projects/salon-bot/main.py"` which `subprocess.run(cmd, shell=False)` treated as a single executable name
2. The salon-bot required `aiogram` which was only installed in system Python, not Hermes venv

## Fixes Applied

### 1. Fix Command Splitting (`goal_executor.py`)
```python
# Split command string into args for shell=False
import shlex
cmd_args = shlex.split(cmd)
result = subprocess.run(cmd_args, shell=False, ...)
```

### 2. Use Venv Python for Salon Bot (`goal_executor.py:derive_action()`)
```python
if "salon" in title or "demo site" in title:
    bot_dir = HERMES / "projects" / "salon-bot"
    if bot_dir.exists():
        venv_python = HERMES / "hermes-agent" / ".venv" / "Scripts" / "python.exe"
        return f'"{venv_python}" "{bot_dir / "main.py"}"'
```

### 3. Install Requirements
```bash
pip install -r projects/salon-bot/requirements.txt
# Installs aiogram, aiosqlite, python-dotenv in Hermes venv
```

## Test Result
`test_4_goal_executor_returns_action` now passes (after aiogram installed in venv and command splitting fixed).