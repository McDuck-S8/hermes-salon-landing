# Money4Band Native — DEPRECATED (2026-06-28)

## Status: ❌ DEAD — Removed from goal queue (g-015)

**Reason:** Cost-benefit analysis showed net profit = $0-5/month (revenue $10-20 minus electricity $10-15). Not worth the hardware wear, privacy risk, and electricity cost. User confirmed: "не стоит".

**What replaced it:** Auto-microsites generator (see `references/auto-microsites-revenue.md`) — same time investment, 7K-25K rubles per sale vs $0-5/month passive.

---

## Historical Reference (for archival only)

# Money4Band Native — Bandwidth Sharing for Passive Income

## Overview
Run multiple bandwidth-sharing apps natively on Windows without Docker. Each app sells unused internet bandwidth for crypto/USD.

## Apps with Native Windows Support

| App | Monthly Earnings | Install |
|-----|-----------------|---------|
| Honeygain | $5-10 | honeygain.com/desktop |
| EarnApp | $5-10 | earnapp.com/download |
| PacketStream | $0.50-2 | packetstream.io/download |
| Repocket | $1-3 | repocket.com/download |
| Earnfm | $0.50-1 | earnfm.com/download |
| Bitping | $1-5 | bitping.com/download |
| PacketShare | $0.30-1 | packetshare.io/download |
| IPRoyal Pawns | $0.50-2 | pawns.app/download |
| Grass | points/crypto | grassfoundation.io |

**Total expected**: $10-20/month (single device, conservative)

## Architecture (No Docker)

```
money4band-native/
  config.yaml    — email, device_id, proxy for each app
  apps.py        — AppRunner subclasses per app (finds .exe, starts process)
  runner.py      — Base AppRunner class (status, start, stop, restart)
  manager.py     — ProcessManager (orchestrates all runners, health checks)
  cli.py         — CLI: status, start, stop, setup
  dashboard.py   — aiohttp web dashboard (port 8080)
```

## Key Pattern: Process Discovery

Each app has its own exe path pattern:
```python
class HoneygainRunner(AppRunner):
    name = "honeygain"
    # Windows: search common paths
    search_paths = [
        Path.home() / "AppData/Local/Honeygain",
        Path("C:/Program Files/Honeygain"),
        Path("C:/Program Files (x86)/Honeygain"),
    ]
    exe_names = ["Honeygain.exe"]
```

## Proxy Support

Most bandwidth apps support proxy configuration. For Russia/Crimea:
```yaml
global:
  proxy: "socks5://127.0.0.1:10806"
```

## CLI Usage
```bash
python cli.py status     # Check all apps
python cli.py start      # Start all available
python cli.py stop       # Stop all
python cli.py setup      # Interactive setup wizard
```

## Pitfalls
- Some apps require manual registration (email + password) before CLI can use them
- Proxy settings may need per-app configuration (not all support SOCKS5)
- Running too many apps simultaneously may throttle bandwidth
- Some apps need admin rights for network sniffing
- Grass is crypto-only (no direct USD withdrawal)
