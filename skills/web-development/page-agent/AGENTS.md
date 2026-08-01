# page-agent — AGENTS.md

## Purpose
Embed alibaba/page-agent into your own web application — a pure-JavaScript in-page GUI agent that ships as a single `<script>` tag or npm package and lets end-users of your site drive the UI with natural language ("click login, fill username as John"). No Python, no headless browser, no extension required. Use this skill when the user is a web developer who wants to add an AI copilot to their SaaS / admin panel / B2B tool, make a legacy web app accessible via natural language, or evaluate page-agent against a local (Ollama) or cloud (Qwen / OpenAI / OpenRouter) LLM. NOT for server-side browser automation — point those users to Hermes' built-in browser tool instead.

## Ownership
Owner: Hermes Agent (web-development category)
Managed via: skill-forge system

## Local Contracts

### Triggers (from SKILL.md triggers)
- User wants to ship an AI copilot inside their own web app (SaaS, admin panel, B2B tool, ERP, CRM)
- User wants to modernize a legacy web app without rewriting the frontend — page-agent drops on top of existing DOM
- User wants to add accessibility via natural language — voice / screen-reader users drive the UI by describing what they want
- User wants to demo or evaluate page-agent against a local (Ollama) or hosted (Qwen, OpenAI, OpenRouter) LLM
- User wants to build interactive training / product demos — let an AI walk a user through "how to submit an expense report" live in the real UI

### Required Tools
- Node.js 22.13+ or 24+, npm 10+
- An OpenAI-compatible LLM endpoint: Qwen (DashScope), OpenAI, Ollama, OpenRouter, or anything speaking `/v1/chat/completions`
- Browser with devtools (for debugging)

### Configuration (from SKILL.md)
Key config fields passed to `new PageAgent({...})`:
- `model`, `baseURL`, `apiKey` — LLM connection
- `language` — UI language (`en-US`, `zh-CN`, etc.)
- Allowlist and data-masking hooks for locking down what the agent can touch — see https://alibaba.github.io/page-agent/ for full option list

**Security:** Don't put your `apiKey` in client-side code for a real deployment — proxy LLM calls through your backend and point `baseURL` at your proxy. The demo CDN exists because alibaba runs that proxy for evaluation.

### Paths (3 integration paths)
1. **Path 1 — 30-second demo via CDN (no install)**: Add `<script src="https://cdn.jsdelivr.net/npm/page-agent@1.8.0/dist/iife/page-agent.demo.js" crossorigin="true"></script>` to any HTML page. Uses alibaba's free testing LLM proxy — **for evaluation only**.
2. **Path 2 — npm install into your own web app (production use)**: `npm install page-agent`, wire it up with your own LLM endpoint.
3. **Path 3 — clone the source repo** (contributing, or hacking on it): `git clone https://github.com/alibaba/page-agent.git`, `npm ci`, create `.env` with LLM endpoint.

### Repo Layout (Path 3)
Monorepo with npm workspaces. Key packages:
| Package | Path | Purpose |
|---------|------|---------|
| `page-agent` | `packages/page-agent/` | Main entry with UI panel |
| `@page-agent/core` | `packages/core/` | Core agent logic, no UI |
| `@page-agent/mcp` | `packages/mcp/` | MCP server (beta) |
| — | `packages/llms/` | LLM client |
| — | `packages/page-controller/` | DOM ops + visual feedback |
| — | `packages/ui/` | Panel + i18n |
| — | `packages/extension/` | Chrome/Firefox extension |
| — | `packages/website/` | Docs + landing site |

## Work Guidance

### When to use this skill
- User asks "how do I add an AI copilot to my SaaS dashboard?"
- User wants to add natural-language control to an existing admin panel without rewriting it
- User wants to evaluate alibaba/page-agent against their own LLM endpoint
- User is building interactive product demos / onboarding flows driven by an LLM

### When NOT to use this skill
- User wants **Hermes itself to drive a browser** → use Hermes' built-in browser tool (Browserbase / Camofox)
- User wants **cross-tab automation without embedding** → use Playwright, browser-use, or the page-agent Chrome extension
- User needs **visual grounding / screenshots** → page-agent is text-DOM only; use a multimodal browser agent instead

### Common patterns from description
- **Path 1 (CDN demo)** — fastest evaluation, 30 seconds, uses alibaba's free proxy
- **Path 2 (npm install)** — production integration, user provides their own LLM endpoint
- **Path 3 (clone repo)** — contributing, customizing page-agent itself, or testing against arbitrary sites via local IIFE bundle

### Security reminders (from skill)
- **Never ship the demo CDN to real users** — rate-limited, uses alibaba's free proxy, their terms forbid production use
- **API key exposure** — any key passed to `new PageAgent({apiKey: ...})` ships in your JS bundle. Always proxy through your own backend for real deployments
- **Non-OpenAI-compatible endpoints** fail silently or with cryptic errors. If your provider needs native Anthropic/Gemini formatting, use an OpenAI-compatibility proxy (LiteLLM, OpenRouter) in front
- **CSP blocks** — sites with strict Content-Security-Policy may refuse to load the CDN script or disallow inline eval. Self-host from your origin in that case

## Verification

### How to test / verify
After Path 1 or Path 2:
1. Open the page in a browser with devtools open
2. You should see a floating panel. If not, check console for errors (most common: CORS on the LLM endpoint, wrong `baseURL`, or a bad API key)
3. Type a simple instruction matching something visible on the page ("click the Login link")
4. Watch the Network tab — you should see a request to your `baseURL`

After Path 3:
1. `npm run dev:demo` prints `Accepting connections at http://localhost:5174`
2. `curl -I http://localhost:5174/page-agent.demo.js` returns `HTTP/1.1 200 OK` with `Content-Type: application/javascript`
3. Click the bookmarklet on any site; panel appears

### Testing infrastructure in skill directory
This skill directory contains:
- `SKILL.md` — skill definition (this file's source)
- No `scripts/`, `tests/`, or `evals/` directories present
- No `references/`, `templates/`, or `scripts/` subdirectories present

Verification is manual via browser devtools as described above. No automated test suite exists in this skill directory.

## Child DOX Index

| Directory | Purpose | Notes |
|-----------|---------|-------|
| (none) | — | This skill directory contains only `SKILL.md` and this `AGENTS.md`. No child DOX directories exist. |

---

*Generated from SKILL.md frontmatter and content following DOX framework.*