# Install vs Check Pattern (2026-06-23)

## Problem
Agent keeps reinstalling packages that are already installed, wasting time.

## Example
```python
# WRONG — reinstalling aiogram that's already in salon-bot venv
pip install aiogram==3.29.0

# RIGHT — check first
python -c "import aiogram; print(aiogram.__version__)"
# Only install if ModuleNotFoundError
```

## Rule
Before `pip install X`:
1. `python -c "import X"` — works? DONE.
2. `pip list | grep X` — found? DONE.
3. Only then: `pip install X`

## Why It Happens
Agent doesn't check existing state before acting. Fresh session = "nothing installed" assumption.

## Fix
SELF_IDENTITY.md tracks department status. Auto-repair checks status before installing.