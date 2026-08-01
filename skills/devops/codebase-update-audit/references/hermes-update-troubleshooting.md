# Hermes Update Troubleshooting — Common Post-Update Failures

## hermes.exe / hermes_cli ModuleNotFoundError after git pull

When hermes-agent is updated via `git pull` without reinstalling venv dependencies, `hermes.exe` breaks:

```
ModuleNotFoundError: No module named 'hermes_cli'
```

### Cause
`git pull` updates the source code but the venv's installed package metadata (`hermes_cli.egg-info` or entry points) becomes stale. The `hermes.exe` wrapper imports `hermes_cli.main` which may not resolve correctly.

### Workaround (immediate fix — no venv reinstall needed)

```python
# Direct Python import bypasses hermes.exe
cd D:/Portable_Soft/hermes/hermes-agent
./venv/Scripts/python.exe -c "
from hermes_cli.main import main
import sys
sys.argv = ['hermes', 'config', 'set', 'telegram.proxy_url', 'socks5://127.0.0.1:10806']
main()
"
```

### Full Fix (reinstall venv)
```bash
cd D:/Portable_Soft/hermes/hermes-agent
./venv/Scripts/python.exe -m pip install -e ".[all]"
# NOTE: This may take 3-5 minutes on slow machines. Use timeout=300+.
```

### When this happens
- After `git pull origin main` without running `uv sync` or `pip install -e .`
- After `hermes update` on Windows where hermes.exe is locked
- When venv dependencies changed in pyproject.toml

## Cron Job Schedule Format

Valid formats (from `cronjob` tool):
- Duration: `"30m"`, `"2h"` (one-shot timer)
- Recurring: `"every 30m"`, `"every 2h"`, `"every 1m"`
- Cron expression: `"0 9 * * *"` (standard 5-field cron)
- ISO timestamp: `"2026-06-01T09:00:00"` (one-shot at time)

**INVALID:** `"60s"`, `"1m"`, `"30sec"` — these produce cryptic errors.

## Cron Script Paths

Script paths must be **relative to `~/.hermes/scripts/`**:
- ✅ `"network_watchdog.py"` → resolves to `~/.hermes/scripts/network_watchdog.py`
- ❌ `"D:/Portable_Soft/hermes/scripts/network_watchdog.py"` → error: "Script path must be relative"

For `no_agent=True` cron jobs (script-only, no LLM), the script's stdout becomes the message.

## Gateway Multi-Instance Cleanup (Windows)

When multiple gateway processes accumulate (stale from crashes):

```bash
# Nuclear option: kill ALL gateway python processes
wmic process where "name='python.exe' and commandline like '%hermes_cli%gateway%'" call terminate

# Then clean lock files
rm -f ~/.local/state/hermes/gateway-locks/*.lock

# Verify clean
wmic process where "name='python.exe'" get processid,commandline 2>/dev/null | grep -i gateway
# Should return empty
```

**Pitfall:** `taskkill /PID` via MSYS git-bash has encoding issues with Cyrillic process names. Use `wmic` instead.

**Pitfall:** `wmic` output is in cp1251 encoding on Russian Windows — grep patterns must be ASCII-safe.
