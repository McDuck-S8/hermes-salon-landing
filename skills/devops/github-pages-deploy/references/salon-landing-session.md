# Session Reference: GLAM Beauty Salon Landing Deploy

## Context
- **Date**: 2026-07-09
- **Task**: Deploy salon landing page to production
- **Constraint**: Windows machine behind corporate/proxy — Netlify, Vercel, Surge, Cloudflare CLIs all timeout
- **Solution**: GitHub Pages via `gh` CLI (same auth works)

## What Worked

### Repository Setup
```bash
gh repo create hermes-salon-landing --public --source=. --push
# Created: https://github.com/McDuck-S8/hermes-salon-landing
# Branch: user/hermes-session-2026-06-09
```

### Deploy to /docs (Required)
```bash
mkdir -p docs
cp salon_landing_final.html docs/index.html
git add docs/
git commit -m "docs: deploy GLAM Beauty Salon landing"
git push
```

### Enable Pages
```bash
gh api repos/McDuck-S8/hermes-salon-landing/pages --method POST \
  -f source[branch]=user/hermes-session-2026-06-09 \
  -f source[path]=/docs \
  -H "Accept: application/vnd.github+json"
```

### Result
- **Live URL**: https://mcduck-s8.github.io/hermes-salon-landing/
- **Status**: HTTP 200, HTTPS enforced
- **Build time**: ~30-60 seconds

## What Failed (Network Blocked)

| Tool | Error |
|------|-------|
| `netlify deploy` | Timeout 180s |
| `vercel --prod` | Removed single-file support |
| `surge` | Requires interactive TTY login |
| `wrangler pages deploy` | Needs CLOUDFLARE_API_TOKEN |
| `cloudflared tunnel` | WSARecv connection failed |
| `ngrok` | Session closed, reconnect loop |

## Key Learning for This Machine

**Only `gh` CLI + GitHub Pages works reliably.** All other deploy CLIs hit proxy/corporate network blocks.

## Files Created
- `docs/index.html` — landing page (36 KB, 417 lines)
- `salon_landing_final.html` — source in repo root
- `salon-deploy/index.html` — duplicate for local testing

## Form Fixes Applied (Per User Feedback)
1. English words in benefits → **All Russian**
2. Free-text "date/time" → **`<input type="date">` + time slot buttons**
3. Old version shown → **New version deployed to /docs**