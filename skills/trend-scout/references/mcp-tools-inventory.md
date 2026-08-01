# MCP Tools Inventory (2026-06-28)

Source: https://github.com/punkpeye/awesome-mcp-servers + glama.ai/mcp/servers + x402.org
Last scan: 2026-06-28

## FREE / NO API KEY (core utility)

| Tool | What | Install |
|------|------|---------|
| @2sio/mcp | 180+ tools: weather, geocoding, arXiv, PubMed, WHOIS, DNS, crypto, patents, Wikipedia | `npx -y @2sio/mcp` |
| a2asearch-mcp | Search 4,800+ MCP servers, agents, CLI tools | `npx -y a2asearch-mcp` |
| @katzilla/mcp | 300+ free government data (FRED, NOAA, NASA, SEC, arXiv) | `npx @katzilla/mcp` |
| tensorfeed | AI industry intel: news, model pricing, service status | `npx -y @tensorfeed/mcp-server` |
| octodamus-core | Crypto market oracle: 11-signal consensus, 500 req/day free | pip install |
| agentdeals | 1,500+ dev infrastructure deals, free tiers | web API |
| orcarouter/mcp | Browse 160+ LLM models with live pricing | `npx -y @orcarouter/mcp` |
| sylex-search | Universal product/business search, zero LLM calls | `npx sylex-search` |
| anyquery | Query 40+ apps (Notion, Slack, GitHub) with SQL | binary |
| profullstack/mcp-server | 20+ tools: SEO, docs, domain, email, QR, weather, social | npm |

## SELF-HOSTED / LOCAL

| Tool | What | Install |
|------|------|---------|
| gzoonet/cortex | Local knowledge graph, entity extraction, web dashboard | pip |
| forage | Self-improving tool discovery, installs MCP servers on-demand | npx |
| unclick | 450+ endpoints across 60+ integrations, persistent memory | `npx @unclick/mcp-server` |
| ViperJuice/mcp-gateway | 25+ MCP servers on-demand, 9 meta-tools | pip |
| mcp-techTrend | Trend monitoring: arXiv, PubMed, GitHub, HuggingFace, FDA | python |
| anythingmcp | REST/SOAP/GraphQL/SQL → MCP bridge, 29 adapters | self-hosted |
| mcp-orchestrator | Central hub, BM25 tool search, deferred loading | python |
| agent-scraper-mcp | Web scraping: CSS selectors, screenshots, links, metadata | python |

## BROWSER AUTOMATION

| Tool | What | Platform |
|------|------|----------|
| automatalabs/mcp-server-playwright | Playwright browser automation | all |
| browsermcp/mcp | Automate local Chrome | all |
| agent-infra/mcp-server-browser | Puppeteer browser automation | all |
| snapdiff-mcp | Visual verification for UI changes | all |
| firefox-devtools-mcp | Firefox via WebDriver BiDi | all |

## AGENT ECONOMY (x402 micropayments — USDC on Base L2)

| Tool | What | Cost |
|------|------|------|
| x402station | Preflight: detect decoys, dead services, price traps | $0.001/call |
| x402search | Search 14,000+ x402 APIs | $0.01/search |
| cinderwright-api | 1450+ services indexed | USDC/Base |
| blockrun-mcp | 30+ AI models, no API keys needed | USDC/Base |
| **2s-io/sdk** | 180+ tools: weather, geocoding, arXiv, PubMed, WHOIS, DNS, crypto, patents, Wikipedia, court cases | Sub-cent to few cents/call |
| **alderpost-mcp** | 8 intel endpoints (security, company, threat, compliance, sales, sports, property, health) | x402 USDC |
| **pulsenetwork-mcp** | 66 specialized APIs (660+ endpoints) — finance, crypto, legal, immigration, healthcare, real estate, tax, climate, sports, science | x402 USDC on Base + Solana |
| **deepseek-mcp-server** | DeepSeek AI: chat, reasoning, multi-turn, function calling, thinking mode, cost tracking | x402 |
| **gpu-bridge/mcp-server** | 30 AI services (LLM, image gen, video, TTS, whisper, embeddings, reranking, OCR) | x402 USDC or API key credits |
| **x402-discovery-mcp** | Runtime discovery x402 APIs. Agents discover and route to pay-per-call endpoints. Python SDK + CLI `x402scout` | `uvx` / `npm i -g x402scout` |
| **x402-index/x402search-mcp** | Search 14,000+ x402-enabled HTTP APIs by keyword | $0.01 USDC/search |
| **Wolido/OpenAaaS** | Python MCP adapter to OpenAaaS scientific agent network. Remote research agents. | `uvx openaaas-mcp-adapter` |
| **Swarmwage/swarmwage** | **MCP-native agent hire protocol** — discovery + hiring + reputation over x402. Hire specialized agents per function call. USDC on Base. Sub-second sync. On-chain receipts EIP-3009. Mainnet live 2026-05-10. | npm |

## CURRENTLY CONFIGURED IN HERMES (~/.hermes/config.yaml)

| Server | Type | Purpose | Status |
|--------|------|---------|--------|
| context7 | HTTP | Library documentation (7,000+ libs, versioned) | ✅ Configured |
| duckduckgo | HTTP | Web search, privacy-focused, no API key | ✅ Configured |
| github | HTTP | Repos, issues, PRs, code search | ✅ Configured |
| playwright | stdio (npx) | Full browser control, screenshots, JS exec | ✅ Configured |
| filesystem | stdio (npx) | Local file ops (read/write/list) on /tmp | ✅ Configured |
| sequentialthinking | stdio (npx) | Structured step-by-step reasoning (Anthropic official) | ✅ Configured |
| supabase | HTTP | Database queries, realtime, auth, storage | ✅ Configured |
| browser | stdio (npx) | Local browser profile, cookies, extensions | ✅ Configured |

**Needs Hermes restart to activate.**

## REMOTE HTTP SERVERS (configured, ready)

| Server | URL | Category |
|--------|-----|----------|
| context7 | https://mcp.context7.com/mcp | Documentation |
| duckduckgo | https://mcp.duckduckgo.com/mcp | Search |
| github | https://mcp.github.com/mcp | Dev Tools |
| supabase | https://mcp.supabase.com/mcp | Database |
| notion | https://mcp.notion.com/mcp | Workspace |
| figma | https://mcp.figma.com/mcp | Design |
| slack | https://mcp.slack.com/mcp | Communication |
| vercel | https://mcp.vercel.com/mcp | Deployment |

## x402 ECONOMY STATS (30-day, from x402.org)

- **75.41M transactions**
- **$24.24M volume**
- **94.06K buyers**
- **22K sellers**

**Arbitrage potential:** Agent reseller (buy $0.001 → sell $0.01 = 10x), Service aggregator (50+ APIs → subscription), Price arb scanner (monitor x402 endpoints), Agent hiring via Swarmwage ($0.10/task → $1 result).