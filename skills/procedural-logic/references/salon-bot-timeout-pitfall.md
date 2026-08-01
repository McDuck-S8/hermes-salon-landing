# python-telegram-bot — run_polling() Timeout Params

## Problem
`application.run_polling()` in python-telegram-bot v20+ does NOT accept `read_timeout`, `connect_timeout`, or `bootstrap_timeout` as keyword arguments. These were valid in v13/v14 but removed in v20+.

## Error
```
TypeError: run_polling() got an unexpected keyword argument 'read_timeout'
```

## Fix
Remove incompatible timeout parameters:
```python
# BEFORE (broken):
application.run_polling(
    read_timeout=30,
    connect_timeout=15,
    bootstrap_timeout=15,
    drop_pending_updates=True
)

# AFTER (fixed):
application.run_polling(
    drop_pending_updates=True
)
```

## 409 Conflict on getUpdates
If `getMe` returns 200 OK but `getUpdates` returns 409 Conflict:
- The bot token is being used by another process (e.g., Hermes gateway)
- Need a SEPARATE bot token via @BotFather for independent operation
- This is NOT a code bug — it is a token conflict

## Detection
```python
import urllib.request, json
token = "YOUR_TOKEN"
r = urllib.request.urlopen(f"https://api.telegram.org/bot{token}/getMe", timeout=5)
print(json.loads(r.read()))  # Should show bot info
```

## Reference
- python-telegram-bot v20+ changelog: removed deprecated timeout params
- Bot API: 409 = "terminated by other getUpdates request"
