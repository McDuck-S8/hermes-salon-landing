# Web Search Provider Architecture

## Resolution Logic (web_search_registry.py)

The active web search provider is resolved with this precedence:

1. `web.search_backend` in config.yaml (per-capability override)
2. `web.backend` in config.yaml (shared fallback)
3. Single-provider shortcut — if only one registered provider supports the capability AND `is_available()` is True, use it
4. Legacy preference order (filtered by availability):
   `firecrawl → parallel → tavily → exa → searxng → brave-free → ddgs`
5. Otherwise `None` — tool surfaces "set up a provider" error

## Where API Keys Live

| Provider | Required Env Var | Where to Find |
|----------|-----------------|---------------|
| tavily | `TAVILY_API_KEY` | Often in `plugins/web-search-plus/.env` |
| brave-free | `BRAVE_SEARCH_API_KEY` | Must be in main `.env` |
| ddgs | none (needs `ddgs` pip package) | — |
| searxng | `SEARXNG_URL` | Must be in main `.env` |
| parallel | `PARALLEL_API_KEY` | Must be in main `.env` |
| exa | `EXA_API_KEY` | Must be in main `.env` |
| firecrawl | `FIRECRAWL_API_KEY` | Must be in main `.env` |

**Critical:** Keys in `plugins/web-search-plus/.env` are NOT visible to the core
web_search_registry. That plugin uses its own routing system. For the core
`web_search` / `web_extract` tools to work, keys MUST be in the main `.env`.

## Post-Update Desync Bug

After `hermes update`, the main `.env` may not contain keys that were previously
configured in plugin `.env` files. This causes web_search to silently fail (returns
no results with no error). Diagnosis: `web.search_backend` in config.yaml is empty.

Fix:
```python
# 1. Copy keys from plugin .env to main .env
# 2. Set backend in config.yaml via Python:
import yaml
with open('config.yaml') as f:
    cfg = yaml.safe_load(f)
cfg['web']['search_backend'] = 'tavily'
cfg['web']['extract_backend'] = 'tavily'
with open('config.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)
```

**Note:** Cannot use the `patch` tool on config.yaml — it refuses to write
Hermes config files. Use Python yaml.dump or `hermes config set` instead.

## Built-in Web Provider Plugins

These are registered at import time by the plugin system:
- `plugins/web/tavily/provider.py` — Tavily search + extract
- `plugins/web/brave_free/provider.py` — Brave free search only
- `plugins/web/ddgs/provider.py` — DuckDuckGo (no key needed, needs `ddgs` package)
- `plugins/web/searxng/provider.py` — Self-hosted SearXNG
- `plugins/web/parallel/provider.py` — Parallel.ai
- `plugins/web/exa/provider.py` — Exa semantic search
- `plugins/web/firecrawl/provider.py` — Firecrawl scrape + search

Enabled plugins listed in config.yaml `plugins.enabled` — e.g. `web-brave-free`, `web-ddgs`, etc.
