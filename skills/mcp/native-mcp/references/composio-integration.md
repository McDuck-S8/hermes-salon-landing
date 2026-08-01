# Composio MCP Integration for Hermes

> Status: SDK upgraded to `composio` 0.17.1+. Old `composio-core` 0.7.21 is DEPRECATED.

## What It Is

Composio is an MCP gateway to 1000+ apps (Gmail, Slack, GitHub, Linear, Notion, Figma, HubSpot, Stripe, Salesforce, etc.). It connects AI agents to third-party services via OAuth — the agent never sees credentials.

**Pricing:** Free tier — 20,000 tool calls/month, $0. Paid: $229/mo for 2M calls, Enterprise custom.

## SDK Deprecation Warning (2026-07-10)

The old SDK `composio-core` (0.7.21) is **DEPRECATED** — its v1 API returns `410 Gone`.

**Replace with:**
```bash
pip uninstall composio-core -y
pip install composio          # v0.17.1+
```

New SDK API:
```python
from composio import Composio
c = Composio()
c.tools.get(user_id="...")
c.connected_accounts.get(nanoid="...")
```

**Playground API keys** are locked to a specific user. For server-to-server flows, get a **Project API Key** from https://app.composio.dev.

## Alternative: BrowserOS MCP

If BrowserOS is running (localhost:9003), prefer it over the Composio SDK — it provides 40+ app integrations + 53 browser tools through one MCP connection, no per-service API keys.

## MCP Server Config

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  composio:
    type: http
    url: https://connect.composio.dev/mcp
```

Or via CLI:

```bash
hermes mcp add composio --url https://connect.composio.dev/mcp
```

**No auth headers needed** — OAuth is handled automatically by the MCP server. The CLI prompt "Does this server require authentication?" → answer `n`.

## Prerequisites

- `mcp` Python package with HTTP transport support in the Hermes venv:

```bash
# Find the Hermes venv python
hermes-agent/.venv/Scripts/pip3.13.exe install "mcp[cli]>=1.6.0"
```

If missing, `hermes mcp` fails with: `mcp.client.streamable_http is not available`.

## Auth: Two Paths

### Path A — OAuth (requires browser)

The MCP server at `https://connect.composio.dev/mcp` returns 401 without auth. It uses OAuth PKCE flow — the client receives a redirect URL that the user must open in a browser to authorize. Hermes MCP client currently doesn't support interactive OAuth redirect capture.

### Path B — Agent-Native Signup (no human required)

Composio has an agent-native signup at `https://agents.composio.dev`. The flow:

1. **Check existing identity** — look for `~/.composio/anonymous_user_data.json`
2. **Signup** — `POST https://agents.composio.dev/api/signup` (no body)
   - Returns `201` with `agent_key`, `member_id`, `org_id`, `project_id`, `api_key`, `user_api_key`
   - ~5-10s end-to-end with long-poll (120s timeout)
   - Save full response to `~/.composio/anonymous_user_data.json`
3. **CLI install** — `GET https://agents.composio.dev/api/cli` with `Authorization: Bearer <agent_key>`
4. **Claim (optional)** — `POST https://agents.composio.dev/api/claim` with `{email}` to hand over to human

**2026-07-10 status:** Signup API returns `500 {"error":"database error"}` — transient server issue. Retry later.

## Known Issues

| Issue | Cause | Workaround |
|-------|-------|------------|
| 401 on MCP URL | No OAuth token | Complete OAuth or agent signup |
| 500 on /api/signup | Server-side DB error | Retry later (transient) |
| `streamable_http not available` | `mcp` package missing/old | Upgrade: `pip install "mcp[cli]>=1.6.0"` |
| Config saved but disabled | Auth failure during `hermes mcp add` | Run `hermes mcp test composio` after fixing auth |

## Apps Available (subset)

Gmail, Slack, GitHub, Linear, Notion, Figma, HubSpot, Stripe, Salesforce, Google Drive, Airtable, Jira, Discord, Zoom, Asana, Google Calendar, Google Docs, Google Sheets, and 980+ more.

Browse full catalog: https://docs.composio.dev/toolkits

## Links

- Hermes setup page: https://composio.dev/hermes
- Agent-native signup: https://agents.composio.dev
- Dashboard: https://dashboard.composio.dev
- Docs: https://docs.composio.dev
- Pricing: https://composio.dev/pricing
