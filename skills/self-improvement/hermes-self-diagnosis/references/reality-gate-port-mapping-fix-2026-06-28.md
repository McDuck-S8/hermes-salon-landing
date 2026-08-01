# Reality Gate Port Mapping Fix — 2026-06-28

## Problem
`reality_gate.py` checked wrong ports for gateway and cron_scheduler:
- Port 3264 labeled "gateway" → actually FreeQwenApi (third-party proxy, DEAD)
- Port 3265 labeled "cron_scheduler" → no service on this port

## Reality
- Gateway: port **9003** (confirmed via `netstat -ano | grep 9003`, PID 14256→34416)
- Cron scheduler: runs **inside gateway process** (same PID), checked via `hermes cron status`
- FreeQwenApi: port **3264** (third-party, can be dead without affecting system)
- FreeDeepseekAPI: port **9655** (RUNNING)
- Ollama: port **11434** (RUNNING)

## Evidence Chain
1. `reality_gate.py --json` → gateway=DEAD, cron_scheduler=DEAD
2. `hermes gateway status` → "✓ Gateway process running (PID: 34416)"
3. `hermes cron status` → "✓ Gateway is running — cron jobs will fire automatically, 12 active job(s)"
4. `netstat -ano | grep 9003` → TCP 0.0.0.0:9003 LISTENING PID 14256
5. `action_executor.py` line: `"gateway": _is_port_alive(9003)` → correct port known elsewhere

## Fix Applied
reality_gate.py updated:
- Gateway check: `_check_port(9003)` (was `_check_port(3264)`)
- Cron check: new `_check_cron()` function using `hermes cron status` CLI + gateway_alive fallback
- FreeQwenApi: new separate check `_check_port(3264)` labeled `free_qwen_api`

## Impact
- Before: verdict=PARTIAL, gateway=DEAD, cron=DEAD (false negatives)
- After: verdict=PARTIAL, gateway=OK, cron=OK (12 jobs), only free_qwen_api=DEAD (expected)

## Cross-Reference Pattern
When health check reports service dead, verify port across ALL files:
1. `reality_gate.py` — what port does it check?
2. `action_executor.py` — what port does it use for restart?
3. `procedural_executor.py` — what port does it monitor?
4. `netstat -ano | grep <port>` — what process actually holds it?
5. `hermes <service> status` — what does the official CLI say?

## Files Modified
- `D:/Portable_Soft/hermes/scripts/reality_gate.py` — port fixes + _check_cron() function
- `D:/Portable_Soft/hermes/LOOPS.md` — loop analysis documented
- `D:/Portable_Soft/hermes/BOOT_SEQUENCE.md` — LOOPS.md added to boot sequence
