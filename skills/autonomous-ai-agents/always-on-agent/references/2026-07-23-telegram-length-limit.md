# Telegram Message Length Limit — 2026-07-23

## Issue
`send_telegram_message()` returns **HTTP 400 Bad Request** for messages exceeding approximately 8 lines or containing certain character patterns.

## Test Results
| Message Length | Result |
|----------------|--------|
| 1-8 lines, plain text | ✅ Delivered |
| 9+ lines | ❌ HTTP 400 |
| Multi-line with special chars (`$`, `|`, `%`, `:`) | ❌ HTTP 400 |
| Short plain text (<8 lines) | ✅ Delivered |

## Root Cause
Telegram Bot API has message length limits and parsing issues with certain characters. The bridge uses `parse_mode: "Markdown"` which fails on:
- Unescaped `$` characters
- Multi-line messages with certain patterns
- Messages exceeding internal buffer

## Working Solution (2026-07-23)
**Split multi-line alerts into multiple single-line plain-text messages** — no markdown, no special formatting.

### Implementation
```python
# In send_critical_alerts.py
def send_alert(title, metrics, action, disclaimer):
    send_telegram_message(title)
    send_telegram_message(metrics)
    send_telegram_message(action)
    send_telegram_message(disclaimer)
```

### Results
- 2 CRITICAL alerts × 4 messages each = 8 messages sent ✅
- All delivered to chat 737433175 ✅
- No HTTP 400 errors ✅
- No Exfil-Guard blocks ✅

## Fix Applied to `fast_sensor_run.py`
Update `format_alert()` to return a **list of strings** (one per line) instead of a single multi-line string:

```python
def format_alert(gap: dict) -> List[str]:
    """Format a gap as a list of short Telegram messages (< 8 lines total)."""
    o = gap["offer"]
    t = gap["traffic"]
    return [
        f"CRITICAL: {o['name']} ({o['network']}) + {t['source']} {t['vertical']} {t['geo']}",
        f"ROI {gap['roi']:.1f}% | Profit {gap['projected_profit_per_day']:.0f}/day | Conf {gap['confidence']:.0%} | Score {gap['score']:.0f}",
        f"ACTION: Test {t['source']} {t['geo']} {o['vertical']} 50 USD",
        "MOCK DATA - Validate live before deploy"
    ]
```

Then in the calling code:
```python
for line in format_alert(gap):
    send_telegram_message(line)
```

## Files Modified
- `scripts/send_critical_alerts.py` — delivery script using split-message approach (WORKS)
- `skills/finance/arbitrage-sensors/scripts/fast_sensor_run.py` — needs `format_alert()` update
- `skills/finance/arbitrage-sensors/scripts/format_short_alert.py` — reference implementation

## Pattern for Future Alerts
1. **Use plain text** (no markdown parse_mode)
2. **Keep each message to 1 line** (or < 8 lines if combined)
3. **Escape `$`** as `\\$` or avoid entirely (use `profit:`)
4. **Send as multiple messages** rather than one multi-line message
5. **Test with `send_telegram_message("Test")`** first, then build up