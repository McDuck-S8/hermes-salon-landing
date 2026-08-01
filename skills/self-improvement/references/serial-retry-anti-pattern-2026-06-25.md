# Serial Retry Anti-pattern (2026-06-25)

## What Happened
Agent tried to run salon bot via aiogram + SOCKS5 proxy. Failed 5 times with same error (ConnectionResetError). Each time said "this time it'll work." Same approach, same result.

## Why It Happens
Fear of admitting the approach is wrong. Trying again = "I'm persistent." But 5 identical failures = "I'm afraid to change."

## The Rule
After 2 failures with the SAME error:
1. STOP. Don't try again.
2. Diagnose: what's actually broken? (aiogram + aiohttp_socks + SOCKS5 on Windows)
3. Switch approach: python-telegram-bot instead of aiogram
4. The switch WORKED — getMe returned 200 OK on first try

## Decision Matrix
| Attempts | Action |
|----------|--------|
| 1 | Try |
| 2 | Try again (might be transient) |
| 3+ | STOP. Different approach. |
| Same error 2x | STOP. Root cause, not transient. |
