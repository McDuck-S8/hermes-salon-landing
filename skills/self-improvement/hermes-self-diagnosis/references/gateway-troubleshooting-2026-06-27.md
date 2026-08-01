# Gateway Troubleshooting — 2026-06-27 Session

## Problem
Gateway not running → 33 cron jobs never execute.

## Symptoms
- `hermes gateway list` shows "not running"
- `reality_gate.py --json` reports gateway and cron_scheduler as failed
- Port 9003 occupied by Chrome (false positive in reality_gate)
- Stale `gateway_state.json` from old installation (hermes-usb-portable-main)

## Root Causes Found

### 1. Cross-installation PID conflict
Old gateway process (PID 13916) from `hermes-usb-portable-main` was holding the Telegram bot token lock. Even after killing it, `gateway_state.json` retained stale state.

**Fix:** Kill old PID → delete gateway.pid, gateway.lock, gateway_state.json → restart.

### 2. YAML parse error in config.yaml
```yaml
# WRONG (single backslash — YAML error)
command: "D:\Program Files\LocalSynapse\localsynapse-mcp.exe"
# CORRECT (double backslash)
command: "D:\\Program Files\\LocalSynapse\\localsynapse-mcp.exe"
```
Error in gateway.log: `found unknown escape character 'l'` at line 26.
Gateway falls back to `.env` values silently — doesn't crash but loses config.

### 3. Missing `platforms:` section in config.yaml
config.yaml had only `model:`, `providers:`, `mcp_servers:` — no `platforms:`.
Gateway iterates `self.config.platforms.items()` → empty list → `enabled_platform_count = 0`.

**Fix:** Add to config.yaml:
```yaml
platforms:
  telegram:
    enabled: true
```

### 4. Multiple zombie gateway processes
After failed starts, 8+ bash/python processes accumulated. Each held lock files.
`wmic process where "CommandLine like '%gateway%run%'"` revealed them all.

**Fix:** `cmd.exe /c "taskkill /PID X /F"` for each (must use cmd.exe, not bash).

## Key Architecture Facts
- Gateway code: `hermes-agent/gateway/run.py` (17,962 lines)
- Cron ticker: `_start_cron_ticker()` at line 17386 → `InProcessCronScheduler().start()`
- Gateway starts cron even without platforms: "Gateway will continue running for cron job execution"
- PID file: `~/.hermes/gateway.pid`
- Lock file: `~/.hermes/gateway.lock` (device-locked while gateway runs)
- State file: `~/.hermes/gateway_state.json`
- Config: `~/.hermes/config.yaml` + `HERMES_HOME/.env`

## Diagnostic Commands
```bash
# Check gateway status
hermes-agent/.venv/Scripts/python.exe -m hermes_cli.main gateway list

# Check what process owns gateway PID
wmic process where "CommandLine like '%gateway%run%' and Name='python.exe'" get ProcessId,Name,CommandLine

# Find all gateway-related processes
wmic process where "CommandLine like '%gateway%run%'" get ProcessId,Name

# Check config for YAML errors
hermes-agent/.venv/Scripts/python.exe -c "import yaml; yaml.safe_load(open('$HOME/.hermes/config.yaml'))"

# Check platform config
hermes-agent/.venv/Scripts/python.exe -c "from hermes_cli.config import load_config; cfg=load_config(); print('platforms:', cfg.get('platforms', {}))"
```

## Verified Fix Sequence
1. Kill all gateway processes (cmd.exe /c taskkill)
2. Delete stale lock/pid/state files
3. Fix config.yaml YAML errors (escape backslashes)
4. Add platforms section if missing
5. Start gateway: `hermes-agent/.venv/Scripts/python.exe -m hermes_cli.main gateway run`
6. Verify: `hermes gateway list` → shows PID
