# Graceful Import Fallback Pattern

## Problem
Python module imports types/classes that don't exist in the installed version.
Crashes at import time, killing the entire module.

## Pattern
```python
# 1. Try import, set flag
try:
    from some_lib import FancyType, FancyHelper
    HAS_FANCY = True
except ImportError:
    HAS_FANCY = False

# 2. Functions return None when unavailable
def build_fancy_thing(data) -> "FancyType | None":
    if not HAS_FANCY:
        return None
    return FancyHelper(data)

# 3. Callers check before using
try:
    from my_module import build_fancy_thing, available  # or HAS_FANCY
    if available:
        thing = build_fancy_thing(data)
        if thing:
            use_fancy(thing)
            return
except Exception:
    pass
# Fallback to plain text / simple behavior
send_plain_message(data)
```

## Real Example: salon-bot rich.py
aiogram 3.29 rich messages (RichMessage, InputRichMessage, etc.) don't exist
in all installed versions. Fixed by wrapping import in try/except, setting
`HAS_RICH = False`, having all functions return None, and checking in handlers.

## Rules
- NEVER let an optional dependency crash the whole module
- Always export the flag (HAS_X or `available`) so callers can check
- Functions return None, not raise — let callers decide fallback
- Callers: check flag AND check for None (double guard)
