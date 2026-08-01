---
name: microsite-revenue-test
description: Zero-budget microsite generation and deployment workflow for local business outreach revenue testing. Uses auto-microsites generator + GitHub Pages + cold outreach templates.
category: finance
tags: [microsite, revenue-test, outreach, github-pages, auto-microsites, arbitrage]
---

# Microsite Revenue Test Workflow

## Purpose
End-to-end workflow for testing revenue via microsite sales to local businesses with $0 budget:
1. Generate demo microsites from JSON configs (auto-microsites project)
2. Deploy to GitHub Pages (free hosting)
3. Use as portfolio for cold outreach to businesses without websites
4. Track responses → first paid contract = revenue test passed

## Prerequisites
- `gh` CLI authenticated (`gh auth status` → ✓)
- auto-microsites project at `projects/auto-microsites/`
- GitHub repo for each microsite (created by deploy script)

## Workflow

### 1. Create Demo Config (JSON)
```json
{
  "project_name": "barin-barbershop",
  "business_name": "БАРИНЪ",
  "tagline": "Мужская классика и стиль",
  "phone": "+7 (978) 116-56-95",
  "address": "г. Симферополь, ул. Карла Маркса, 51",
  "working_hours": "Пн-Вс: 10:00-20:00, без выходных",
  "color_primary": "#1a1a2e",
  "color_accent": "#d4a574",
  "cta_text": "Записаться",
  "about": "...",
  "services": [...],
  "seo_title": "...",
  "seo_description": "..."
}
```
Save to `projects/auto-microsites/samples/<name>.json`

### 2. Generate Microsite
```bash
cd projects/auto-microsites
python main.py --from samples/<name>.json
# Output: generated/<project_name>/index.html
```

### 3. Deploy to GitHub Pages
```bash
python deploy.py <project_name> --repo <repo-name>
# Creates repo, pushes to gh-pages, enables Pages
# Live at: https://<user>.github.io/<repo-name>/
```

### 4. Outreach (see `projects/auto-microsites/OUTREACH.md`)
- Find businesses without websites (Яндекс.Карты, 2ГИС, Instagram)
- Send DM with demo link
- Price: 7,000-25,000₽ per landing page
- Target niches: стоматология, барбершоп, автосервис, юрист, фитнес

## Key Fixes & Pitfalls

### Fargo v1 Header Fix (Applied 2026-07-14)
**Problem**: On dark hero, nav links (slate-light) invisible. Header CTA button (btn-primary) didn't match hero buttons (btn-primary + btn-outline).
**Fix in `docs/fargo/index.html`**:
```css
/* Nav links: white on dark hero, slate on scrolled */
.header-nav a { color: var(--white); }
.header.scrolled .header-nav a { color: var(--slate-light); }
.header-nav a:hover { color: var(--terracotta); }

/* Header CTA: btn-outline on dark, btn-outline-dark on scrolled */
.header .btn-outline { color: var(--white); border-color: rgba(255,255,255,0.4); }
.header.scrolled .btn-outline { color: var(--terracotta); border-color: var(--terracotta); }
.header .btn-outline:hover { background: rgba(255,255,255,0.08); border-color: var(--white); color: var(--white); }
.header.scrolled .btn-outline:hover { background: var(--terracotta); border-color: var(--terracotta); color: var(--white); }
```
**HTML**: Change header CTA from `btn btn-primary` → `btn btn-outline`

### GitHub Pages Rebuild After Force Push
```bash
# Force push to update branch
git push -f origin <branch>
# Trigger rebuild
gh api repos/<owner>/<repo>/pages/builds -X POST
# Wait 30-60s, verify
gh api repos/<owner>/<repo>/pages
```

### Windows rmtree Permission Error (2026-07-28)
**Problem**: `shutil.rmtree()` fails on `.git/objects/` files with `PermissionError: [WinError 5]` when trying to clean deploy directory before re-cloning.
**Fix**: Delete the deploy directory manually first (`rm -rf deploy/<repo-name>`) before running deploy script, OR use the alternative deploy pattern below.

### Working Deploy Pattern (Verified 2026-07-28)
**When deploy.py fails on Windows**, use this manual pattern that works reliably:
```bash
cd projects/auto-microsites/generated/<project_name>
git init && git add . && git commit -m "Deploy <project_name>"
git branch -M gh-pages
gh repo create <repo-name> --public --source=. --push
# Then enable Pages on gh-pages branch:
gh api repos/<owner>/<repo>/pages -X POST -f source[branch]=gh-pages -f source[path]=/
# Wait 30-60s, verify:
curl -s -o /dev/null -w "%{http_code}" https://<owner>.github.io/<repo-name>/
```

### Verified Live Sites (2026-07-28)
| Project | Repo | Live URL | Status |
|---------|------|----------|--------|
| barin-barbershop | barin-barbershop-site | https://mcduck-s8.github.io/barin-barbershop-site/ | ✅ 200 OK |
| dental-smile | dental-smile-site | https://mcduck-s8.github.io/dental-smile-site/ | ✅ 200 OK |
| barbershop-akcent | barbershop-akcent-site | https://mcduck-s8.github.io/barbershop-akcent-site/ | ✅ 200 OK |

### v2 Dark Luxury Location
Real v2 (dark luxury, kinetic typography, Playfair Display, gold, particles) is at commit `cb6d309ed:docs/fargo/index.html`, NOT at current `demos/fargo/index.html`.
```bash
git show cb6d309ed:docs/fargo/index.html > /tmp/fargo_v2.html
# Update OG URL, copy to docs/fargo-v2/index.html
```

## References
- `projects/auto-microsites/` — generator project (main.py, deploy.py, templates/, samples/)
- `projects/auto-microsites/OUTREACH.md` — cold outreach templates
- `devops/github-pages-deploy` skill — deployment patterns
- `references/fargo-v1-header-fix.md` — detailed CSS fix notes
- `references/fargo-v2-location.md` — where to find real v2