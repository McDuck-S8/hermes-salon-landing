# Google Stitch MCP Setup

> Google Stitch is a free AI UI/UX design tool from Google (launched 2025, Stitch 2.0 March 2026).
> MCP integration allows Hermes Agent to generate UI designs directly via chat.

## Key Facts (as of 2026-07-27)

- **Free tier:** ~400 daily design credits (~12,450/month)
- **Output formats:** HTML, Tailwind, Vue, Angular, Flutter, SwiftUI
- **Capabilities:** text-to-UI, voice input, multi-screen (up to 5), infinite canvas, interactive prototyping
- **MCP Server:** `@google/stitch-mcp@latest` (npm package)

## MCP Config for Hermes

Add to Hermes config.yaml under `mcp_servers`:

```yaml
mcp_servers:
  stitch:
    command: "npx"
    args: ["-y", "@google/stitch-mcp@latest"]
    env:
      STITCH_API_TOKEN: "your-token-here"
    timeout: 120
```

## Where to Get API Token

1. Go to https://stitch.withgoogle.com/ → Settings → API Tokens → Generate New Token
2. Copy the token (format: `AQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
3. Token expires after 90 days (as of June 2026)

## Available MCP Tools

Once connected, Hermes sees these commands as `mcp_stitch_*` tools:
- `generate_design(prompt, format?)` — generate UI from text description
- `refine_design(design_id, prompt)` — refine existing design
- `export_design(design_id, format)` — export to HTML/Tailwind/Vue/etc.
- `get_design_metadata(design_id)` — palette, typography, components used
- `list_projects()` — list existing Stitch projects
- `update_project(project_id, changes)` / `delete_project(project_id)`

## Use Case

The killer workflow for Hermes: prompt Stitch via MCP to generate a reference UI for a landing page or component, review the design metadata, then implement it in the codebase — all in one session without switching to the web UI.

## Limitations

- Rate limit: ~350-400 generations/month on free tier
- AI-generated designs still need human review for quality
- Token expires every 90 days — regenerate and update config
