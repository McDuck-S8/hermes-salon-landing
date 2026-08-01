# Gateway Proxy Propagation — 2026-06-27

## Problem
Telegram adapter fails with `httpx.ConnectError` + `RemoteProtocolError: Server disconnected without sending a response` even when:
- Bot token is valid (`getMe` → 200 OK)
- SOCKS5 proxy works (`curl -x socks5://... https://api.telegram.org` → 302)
- httpx with socks5 transport works manually

## Root Cause
Gateway's `_apply_yaml_config()` (`gateway/config.py:1049-1062`) only runs when config.yaml has a `telegram:` section. If absent:
- Function is skipped (line 1062: `if not isinstance(platform_cfg, dict): continue`)
- `os.environ["TELEGRAM_PROXY"]` never gets set
- Adapter's `resolve_proxy_url("TELEGRAM_PROXY")` returns None
- Adapter connects directly → blocked in censored regions → ConnectError

## The Two-Section Requirement
config.yaml needs TWO separate sections for Telegram to work:

```yaml
# Section 1: Platform enablement (gateway discovers this)
platforms:
  telegram:
    enabled: true

# Section 2: Config propagation (apply_yaml_config reads this)
telegram:
  proxy_url: "socks5://127.0.0.1:10806"
  extra:
    rich_messages: true
```

- `platforms:` → controls whether adapter is created at all
- `telegram:` → controls proxy, env vars, feature flags
- Both are needed; one without the other = partial failure

## Verification Chain
```python
# 1. Check token validity
curl -x socks5://127.0.0.1:10806 "https://api.telegram.org/bot<TOKEN>/getMe"
# → {"ok":true,...} = token works

# 2. Check proxy works with httpx
python -c "
import httpx, asyncio
async def t():
    async with httpx.AsyncClient(proxy='socks5://127.0.0.1:10806', timeout=10) as c:
        r = await c.get('https://api.telegram.org')
        print(f'status={r.status_code}')
asyncio.run(t())
"
# → status=302 = httpx+proxy OK

# 3. Check if config.yaml has telegram section
python -c "
import yaml
with open('$HOME/.hermes/config.yaml') as f:
    cfg = yaml.safe_load(f)
print('telegram:', cfg.get('telegram', 'MISSING'))
print('proxy_url:', cfg.get('telegram', {}).get('proxy_url', 'MISSING'))
"
# If MISSING → that's the bug

# 4. Check env propagation at runtime
python -c "
import os; os.environ['HERMES_HOME']='D:/Portable_Soft/hermes'
from dotenv import load_dotenv; from pathlib import Path
load_dotenv(Path('D:/Portable_Soft/hermes/.env'), override=True)
print('TELEGRAM_PROXY:', os.environ.get('TELEGRAM_PROXY', 'NOT SET'))
"
# If NOT SET → proxy not propagating
```

## Fix
Add `telegram:` section to `~/.hermes/config.yaml` with `proxy_url`:

```yaml
telegram:
  proxy_url: "socks5://127.0.0.1:10806"
  extra:
    rich_messages: true
```

Restart gateway after fix. Verify with `hermes gateway list` → shows PID.
