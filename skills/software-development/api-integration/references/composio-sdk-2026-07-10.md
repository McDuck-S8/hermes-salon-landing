# Composio SDK Integration (2026-07-10)

Composio integrates 200+ SaaS apps into AI agents via a Python SDK. No Docker, no separate services — just a pip package.

## Package: composio (NOT composio-core)

**`composio-core` IS DEPRECATED.** The old package hits v1 APIs that return HTTP 410 Gone.

| Aspect | Old (composio-core) | New (composio) |
|--------|-------------------|----------------|
| Package | `pip install composio-core` | `pip install composio` |
| Version | 0.7.21 (last) | 0.17.1+ |
| API version | v1 | v3/v3.1 |
| Python API | `ComposioToolSet()` | `Composio().tools`, `Composio().connected_accounts` |
| Status | Deprecated | Active |

**Migration:**
```bash
pip uninstall composio-core -y
pip install composio
```

## API Keys: Playground vs Project

**Playground keys** (from composio.dev "Create with Composio") are bound to a specific test user:
- `composio.create(user_id="<any>", ...)` → `403: user_id does not match the user this playground API key is locked to.`
- Error: `"A playground API key can only create sessions for its own bound playground user."`

**Project keys** (from https://app.composio.dev → Create Project) work for server-to-server:
- No user_id binding
- Can manage connections for any user_id
- Required for API usage from an agent/bot

## SDK API Structure (v0.17+)

```python
from composio import Composio

c = Composio()
# or: c = Composio(api_key="...")  # falls back to COMPOSIO_API_KEY env

# Resources available:
c.tools              # Tool management
c.connected_accounts  # Connected app accounts  
c.create()           # OAuth session to connect apps
c.toolkits           # Grouped tools
c.sessions           # Session management
c.mcp                # Model Context Protocol
c.triggers           # Trigger management
```

## Connect Apps via OAuth

```python
session = c.create(
    user_id="hermes-mira",
    manage_connections={"wait_for_connections": True},
)
# Opens browser URL for user to connect apps (Gmail, Slack, GitHub, etc.)
```

## Error: SSL / Backend unreachable

If `backend.composio.dev` returns 410 or SDK throws SSL errors:
- Likely using old `composio-core` package hitting v1 endpoints
- Update to `composio` (new package, same API surface, v3 endpoints)

On Windows with SSL issues, httpx works where requests fails:
```python
import httpx
r = httpx.get("https://backend.composio.dev/api/v3.1/tool_router/session", ...)
```

## Verification

```python
import composio
print(composio.__version__)  # 0.17.1+

from composio import Composio
c = Composio()
print(c.connected_accounts.get())  # empty list if no apps connected yet
```

## Example: Keyword-to-Action Bridge (MIRA pattern)

```python
_COMPOSIO_RULES = [
    (r"(почт|письм|email|gmail)", Action.GMAIL_SEND_EMAIL),
    (r"(слак|slack)", Action.SLACK_SEND_MESSAGE),
    (r"(github|issue|гитхаб)", Action.GITHUB_CREATE_ISSUE),
    (r"(notion|ноушн)", Action.NOTION_CREATE_PAGE),
    (r"(discord|дискорд)", Action.DISCORD_SEND_MESSAGE),
    (r"(calendar|календарь)", Action.GOOGLECALENDAR_CREATE_EVENT),
    (r"(drive|гугл диск)", Action.GOOGLEDRIVE_CREATE_FILE),
    (r"(sheets|таблиц)", Action.GOOGLESHEETS_CREATE_SPREADSHEET),
    (r"(twitter|твиттер|твит)", Action.TWITTER_CREATE_TWEET),
]

async def composio_run(text: str, ts) -> Optional[str]:
    for pattern, action in _COMPOSIO_RULES:
        if re.search(pattern, text.lower()):
            try:
                result = ts.execute_action(action=action, params={})
                return f"✅ {action.name}: {str(result)[:300]}"
            except Exception as e:
                return f"⚠️ {action.name}: {e}"
    return None
```

## Pitfalls

1. **Playground key fails with 403** → use project API key from app.composio.dev
2. **Old composio-core hits 410** → migrate to `composio` package
3. **No connected accounts** → if apps aren't connected via OAuth, `execute_action` fails
4. **SSL errors on Windows** → httpx may work where requests fails
