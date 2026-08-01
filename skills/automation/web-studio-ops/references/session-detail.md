# Web Studio Kickoff — Session Reference

## Research (from YouTube "Every Local AI I Run Now Shares ONE Memory")

Video: https://www.youtube.com/watch?v=IwN-eK1s8og (Codacus)
Repo: https://github.com/thecodacus/understory

Understory is a shared memory layer for AI agents using plain markdown files following Google's OKF (Open Knowledge Format) spec. Key concepts:
- **OKF**: Markdown files with YAML frontmatter, cross-linked, git-diffable
- **MCP server**: memory_query/memory_add/memory_update/memory_status/memory_maintain tools
- **Graph visualization**: Force-directed graph showing how memories connect
- **Query-path replay**: Every agent run records its traversal as compact notation

### How Hermes Maps (already have, just differently)
| Understory | Hermes Equivalent |
|-----------|------------------|
| OKF markdown files | Knowledge Cube + skills (SKILL.md with YAML frontmatter) |
| MCP memory server | memory tool + session_search |
| Force-directed graph | Missing—could add D3.js visualization |
| Query-path replay | session_search (FTS5) |

### Integration Opportunity
Understory runs as Docker container alongside Hermes. Could:
1. Run Understory container that points at Knowledge Cube directory
2. Add MCP tools to Hermes for cross-agent memory
3. Or just adopt OKF format for new knowledge entries

## Web Studio Architecture

### Tech Stack
- **Hosting**: GitHub Pages (free) + Cloudflare/Vercel for advanced
- **Domains**: Namecheap or nic.ua
- **Deploy**: `docs/` folder → auto-deploy to GH Pages
- **Demo sites**: `docs/demos/{slug}/`
- **Source sites**: `demos/{client}/`

### Studio Landing Page
`docs/index.html` is the studio landing page:
- Built with single HTML + inline CSS/JS
- Multi-language (RU/UK/EN) via JS translation object
- Dark/light theme toggle
- Portfolio with category filter
- Services, process, and CTA sections

### Client Outreach Workflow
1. Find salon/cafe/medcenter with bad/no site
2. Run `python scripts/pipeline.py --name "Name" --instagram @handle`
3. This creates demo at `docs/demos/{slug}/` and prints DM text
4. Open Instagram, find the business, send the DM
5. If interested → discuss package → close

### DM Strategy Lessons
- **Do NOT send generic pitch** — reference their Instagram content specifically
- **Show, don't promise** — send a live working demo, not a mockup
- **Casual tone** — "не хотел навязываться, просто показал как может выглядеть"
- **Follow up once after 3-4 days** if no reply, then move on

## OG Image Strategy (v2 — 2026-07-13)

For Telegram preview cards on demo pages:
- **DO NOT use Instagram CDN URL in og:image** — Telegram shows the Instagram profile pic instead of studio branding
- **Always use studio-preview.jpg** as og:image for all demo sites: `https://mcduck-s8.github.io/hermes-salon-landing/studio-preview.jpg`
- **All demo templates now auto-include OG tags** (og:title, og:description, og:image, og:url, og:type, twitter:card) generated via `demo_generator.py`
- **Fargo fix**: replaced Instagram CDN og:image with studio-preview.jpg + og:image:width/height + Hermes Studio site_name
- **Telegram caches OG for ~24h** — use `?v=N` query param on URL to bust cache, or @WebpageBot
