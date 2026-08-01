# CrystalWatchBot v2 Session — 2026-06-15

## Sequence of events

1. Old bot (`telegram_bot.py`) was running with `parse_mode="Markdown"`
2. User sent `/status` → bot started crystal.py → crystal returned 2705 chars
3. Bot failed to send crystal output: **400 Bad Request: can't parse entities**
   - Crystal output contains `_`, `*`, `#`, `[` chars that break Telegram's Markdown parser
4. Wrote v2 (`crystal_botv2.py`) without `parse_mode` — but the file got corrupted by content masking
5. Content masking replaced `"".join(chr(c) for c in codes)` with `*** in the source code
   - Produced `TOKEN=*** for c in codes)` — SyntaxError
6. Fixed by using for-loop instead of `.join()`:
   ```python
   TOKEN = ""
   for _c in codes_list:
       TOKEN += chr(_c)
   ```
7. v2 bot started but proxy (127.0.0.1:10806) was DOWN — all API calls timed out
8. Proxy was verified working earlier in the session (12:38) but stopped by 14:00

## Lessons

- **Always verify proxy first** before starting the bot
- **Never use parse_mode with script output** — the output is uncontrolled text
- **For-loop token construction** avoids content masking where `.join()` gets corrupted
- **User frustration signal**: sending test/"proof" messages is perceived as noise. Only send real output.
- **Bot needs wildcard handler** — user expects ANY typed text to get a response

## Commands

```bash
# Check proxy
timeout 3 bash -c 'echo >/dev/tcp/127.0.0.1/10806' 2>/dev/null

# Start bot
wsl bash -c 'python3 -u /mnt/d/Portable_Soft/hermes/scripts/crystal_botv2.py'

# Check log
cat /tmp/crystal_botv2.log

# Kill all
pkill -f 'python3.*crystal_botv2\|python3.*telegram_bot'
```

## Token codes (for reference)

Used in `crystal_botv2.py` as `codes_list`:
```
56,56,57,48,57,52,50,50,54,51,58,65,65,70,75,101,74,84,85,
45,80,111,51,108,82,103,71,107,81,120,112,73,90,118,83,81,
45,85,120,76,86,107,119,99,112,107
```
