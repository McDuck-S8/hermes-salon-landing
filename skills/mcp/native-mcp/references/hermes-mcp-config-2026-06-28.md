# Hermes MCP Configuration — Session 2026-06-28

## Config Applied (~/.hermes/config.yaml)

```yaml
mcp_servers:
  context7:
    type: http
    url: https://mcp.context7.com/mcp
  duckduckgo:
    type: http
    url: https://mcp.duckduckgo.com/mcp
  github:
    type: http
    url: https://mcp.github.com/mcp
  playwright:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-playwright"]
  filesystem:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
  sequentialthinking:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-sequentialthinking"]
  supabase:
    type: http
    url: https://mcp.supabase.com/mcp
  browser:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-browser"]
  browseros:
    type: http
    url: http://127.0.0.1:9003/mcp

## Expected Tools After Restart
## Expected Tools After Restart

| Server | Transport | Expected Tools (prefix) |
|--------|-----------|------------------------|
| context7 | HTTP | `mcp_context7_resolve_library_id`, `mcp_context7_get_library_docs` |
| duckduckgo | HTTP | `mcp_duckduckgo_search`, `mcp_duckduckgo_fetch` |
| github | HTTP | `mcp_github_search_repos`, `mcp_github_get_file`, `mcp_github_list_issues`, `mcp_github_create_issue` |
| playwright | stdio (npx) | `mcp_playwright_navigate`, `mcp_playwright_click`, `mcp_playwright_screenshot`, `mcp_playwright_evaluate` |
| filesystem | stdio (npx) | `mcp_filesystem_read_file`, `mcp_filesystem_write_file`, `mcp_filesystem_list_directory`, `mcp_filesystem_create_directory` |
| sequentialthinking | stdio (npx) | `mcp_sequentialthinking_sequential_thinking` |
| supabase | HTTP | `mcp_supabase_execute_sql`, `mcp_supabase_list_tables`, `mcp_supabase_get_schema` |
| browser | stdio (npx) | `mcp_browser_navigate`, `mcp_browser_click`, `mcp_browser_type`, `mcp_browser_snapshot` |
| browseros | HTTP (localhost) | `mcp_browseros_take_snapshot`, `mcp_browseros_click`, `mcp_browseros_gmail_search_messages`, `mcp_browseros_slack_post_message`, +40+ apps |

## Session Findings

### 1. HTTP vs stdio transport
- **HTTP servers** (context7, duckduckgo, github, supabase): No local process, direct HTTPS. Faster startup, no Node.js dependency for these.
- **stdio servers** (playwright, filesystem, sequentialthinking, browser): Require `npx` and Node.js. Auto-install packages on first run via `-y` flag.

### 2. Remote HTTP servers available (pre-configured in trend-scout references)
```
notion:  https://mcp.notion.com/mcp
figma:   https://mcp.figma.com/mcp
slack:   https://mcp.slack.com/mcp
vercel:  https://mcp.vercel.com/mcp
```
Can be added to config without API keys for basic access.

### 3. Firecrawl requires API key
```yaml
firecrawl:
  command: npx
  args: ["-y", "firecrawl-mcp"]
  env:
    FIRECRAWL_API_KEY: "fc-xxxx"
```

### 4. GitHub requires PAT for write operations
```yaml
github:
  type: http
  url: https://mcp.github.com/mcp
  headers:
    Authorization: "Bearer ghp_xxxx"
```

### 5. Verification commands after restart
```bash
# Check MCP tools loaded
hermes --list-tools | grep mcp_

# Test context7
mcp_context7_resolve_library_id --library "react"

# Test duckduckgo
mcp_duckduckgo_search --query "AI agents 2026"

# Test playwright
mcp_playwright_navigate --url "https://example.com"
```

### 6. Troubleshooting applied
- Config file location: `~/.hermes/config.yaml` (NOT project config.yaml)
- Empty file initially — wrote full mcp_servers section
- Need Hermes restart for pickup (no hot-reload)
- `mcp` Python package already installed (bundled with Hermes)

### 7. x402 servers for future (agent economy)
```yaml
# x402-enabled servers (pay-per-call via USDC on Base)
2sio:
  command: npx
  args: ["-y", "@2sio/mcp"]
swarmwage:
  command: npx
  args: ["swarmwage"]
x402search:
  command: command: npx
 args: ["-y", "x402-index/x402search-mcp"]
```