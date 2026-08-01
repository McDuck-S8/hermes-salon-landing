---
name: github-pages-deploy
description: Deploy static sites to GitHub Pages. Source MUST be root (/) or /docs folder. No other paths accepted.
version: "1.0"
tags: [github, pages, static-site, deployment, devops]
---

# GitHub Pages Deployment

## 🚨 First Thing: Determine Actual Pages Source (DO NOT Assume gh-pages)

**Many repos serve Pages from the default branch root, NOT from a `gh-pages` branch.** Pushing to `gh-pages` when Pages is configured on the default branch has ZERO effect on the live site.

### Quick Check — Raw vs Live

```bash
# Check repository metadata (no auth needed)
curl -s https://api.github.com/repos/OWNER/REPO | python -c "import sys,json; d=json.load(sys.stdin); print('default_branch:', d.get('default_branch'), 'has_pages:', d.get('has_pages'))"

# Compare raw file on default branch vs live site
curl -s https://raw.githubusercontent.com/OWNER/REPO/DEFAULT_BRANCH/cosmetologist/index.html | grep -c "unique-marker"
curl -s https://OWNER.github.io/REPO/cosmetologist/ | grep -c "unique-marker"
# If counts match → Pages serves from default branch root
# If mismatch → Pages serves from a different source
```

### Three Common Configurations

| Pages Source | Where to push | Live URL structure |
|---|---|---|
| Default branch, root `/` | Default branch (e.g. `main`, `master`, `user/hermes-session-*`) | `https://user.github.io/repo/path/` |
| Default branch, `/docs` folder | Default branch, inside `docs/` subdir | `https://user.github.io/repo/path/` |
| `gh-pages` branch, root `/` | `gh-pages` branch | `https://user.github.io/repo/path/` |

**Rule**: Look at the actual API response before pushing. If you don't check, you WILL push to the wrong branch and the user WILL notice.

## Critical Constraint (422 Error If Violated)

**Source path MUST be `/` (root) or `/docs` — nothing else.**

GitHub Pages API rejects `/salon-deploy`, `/dist`, `/build`, `/public`, etc. with:
```
{"message":"Validation Failed","errors":[{"code":"invalid","field":"source.path","message":"Source path must be '/' or '/docs'"}]}
```

## Deploy Pattern for Landing Pages

### Option A: Root deployment (/)
```
repo/
├── index.html          ← landing page
├── css/style.css
├── js/main.js
└── assets/
```

### Option B: Docs folder (/docs) — RECOMMENDED
```
repo/
├── docs/
│   ├── index.html      ← landing page
│   ├── css/style.css
│   ├── js/main.js
│   └── assets/
└── src/                ← keep source separate
```

## Commands

### Enable Pages (gh CLI)
```bash
# Get owner/repo from remote
OWNER_REPO=$(git remote get-url origin | sed -E 's|.*github.com[:/]([^/]+/[^.]+).*|\1|; s|\.git$||')
OWNER=$(echo $OWNER_REPO | cut -d/ -f1)
REPO=$(echo $OWNER_REPO | cut -d/ -f2)

# Enable Pages on main branch, /docs folder
gh api repos/$OWNER/$REPO/pages --method POST \
  -f source[branch]=main \
  -f source[path]=/docs \
  -H "Accept: application/vnd.github+json"
```

### Check Status
```bash
gh api repos/$OWNER/$REPO/pages
# Returns: {"url":"https://owner.github.io/repo/","status":"building|built|errored",...}
```

### Add Custom Domain (optional)
```bash
# Add CNAME file to /docs
echo "yourdomain.com" > docs/CNAME

# Update Pages config
gh api repos/$OWNER/$REPO/pages --method PUT \
  -f cname=yourdomain.com \
  -H "Accept: application/vnd.github+json"
```

## Common Pitfalls

| Mistake | Result | Fix |
|---------|--------|-----|
| `source[path]=/salon-deploy` | 422 Validation Failed | Use `/docs` or `/` |
| `source[path]=/dist` | 422 Validation Failed | Use `/docs` or `/` |
| `source[branch]=gh-pages` without folder | Builds entire repo | Use `source[path]=/docs` |
| Missing CNAME file | Custom domain ignored | Add CNAME to source folder |

## Landing Page Header CTA Pattern (from Fargo v1 fix)

When a landing page has a dark hero + light scrolled header, the header CTA must adapt:

```css
/* On dark hero */
.header .btn-primary { background: var(--accent); color: #fff; }

/* On light scrolled header */
.header.scrolled .btn-primary { background: var(--dark); color: #fff; }
```

**Key insight**: The header CTA matches the hero's primary CTA style on dark, then inverts for readability on light background. Never leave a dark button on light header — it blends.

## CRITICAL: Check Existing Pages Config First

**Do NOT blindly create a `gh-pages` branch!** The repo may already have Pages configured on a different branch/source.

### How to Check

**With gh CLI:**
```bash
gh api repos/$OWNER/$REPO/pages
```

**Without gh CLI (using curl + Python):**
```bash
curl -s https://api.github.com/repos/OWNER/REPO | python -c "import sys,json; d=json.load(sys.stdin); print('default_branch:', d.get('default_branch'), 'has_pages:', d.get('has_pages'))"
```

**Fallback (compare raw vs live):**
```bash
curl -s https://raw.githubusercontent.com/OWNER/REPO/DEFAULT_BRANCH/PATH/index.html | grep UNIQUE_MARKER
curl -s https://LIVE_URL | grep UNIQUE_MARKER
# If markers match → Pages is on default branch
```

Fields to verify:
- `source.branch` — which branch serves Pages (NOT always `gh-pages`!)
- `source.path` — root `/` or `/docs`

### Common Configurations Found in Production
| Branch | Path | Notes |
|--------|------|-------|
| `gh-pages` | `/` | Classic Pages setup |
| `main` | `/docs` | Common for project repos |
| `user/hermes-session-*` | `/docs` | Hermes session branches |

**Pitfall**: Force-pushing to `gh-pages` while Pages is configured on `main/docs` has zero effect — wrong branch.

### The Correct Flow
1. **Check** current config: `gh api repos/$OWNER/$REPO/pages | jq .source`
2. **Before any full-file rewrite: preserve critical elements from old version**
   - `<title>` tag content
   - All `function` declarations (especially carousel JS: `initCarousel`, `moveSlide`, `goToSlide`, etc.)
   - All inline `onclick` handlers
   - All local asset paths (`src=` that don't start with `http`)
3. **Write new file** — re-insert all preserved items
4. **Verify** `<title>` and each function name exists in the new file before committing
5. **Add file** to the correct branch + path (e.g., `docs/fargo/index.html` on working branch)
6. **Commit + push** the parent branch
7. **Wait** 30-60s for GitHub Pages to rebuild
8. **Verify** with curl (retry in 15s intervals if 404 on first check — CDN propagation lag)

## Multi-Client Deployment Pattern

When one repo serves multiple client landing pages, use subdirectories inside the Pages source folder:

```
# Pages source: user/hermes-session-2026-06-09 /docs
docs/
  index.html        ← Client 1 (original landing, or directory listing)
  fargo/
    index.html      ← Client 2 (Fargo salon)
  client3/
    index.html      ← Next client
```

### Convention
- **Source files**: `demos/<client-name>/index.html` (working copies)
- **Deployed files**: `docs/<client-name>/index.html` (mirror for Pages)
- **Root index.html**: first/main client site or a directory page
- **One folder per client** — never mix client files at root level

### Deploy a New Client
```bash
mkdir -p docs/<client-name>
cp demos/<client-name>/index.html docs/<client-name>/index.html
git add docs/<client-name>/
git commit -m "docs: add <client-name> landing page"
git push origin <branch>
# Live at: https://owner.github.io/repo/<client-name>/
```

## Complete Workflow for This Session

```bash
# 1. Prepare /docs folder with landing page
mkdir -p docs/css docs/js docs/assets
cp salon_landing_final.html docs/index.html
# (copy css, js if separate files)

# 2. Commit and push
git add docs/
git commit -m "docs: deploy GLAM Beauty Salon landing"
git push origin main

# 3. Enable GitHub Pages
gh api repos/$OWNER/$REPO/pages --method POST \
  -f source[branch]=main \
  -f source[path]=/docs \
  -H "Accept: application/vnd.github+json"

# 4. Wait ~30-60s, then live at:
# https://$OWNER.github.io/$REPO/
```

## Universal Deploy Script

For quick deployment of any single-page project, use the **`scripts/deploy-static.sh`** support file in this skill:

| Target | Command |
|--------|---------|
| GitHub Pages | `bash scripts/deploy-static.sh projects/NAME --gh-pages` |
| Vercel | `bash scripts/deploy-static.sh projects/NAME --vercel` |
| Netlify | `bash scripts/deploy-static.sh projects/NAME --netlify` |
| Cloudflare Pages | `bash scripts/deploy-static.sh projects/NAME --cf` |

Alias from root: `bash skills/devops/github-pages-deploy/scripts/deploy-static.sh`

The script copies project files to `docs/<project>/` and prints follow-up git commands for GitHub Pages.

## Alternative: gh-pages Branch + Git Worktree

When the repo already has a `gh-pages` branch serving Pages (source branch ≠ working branch), use a **git worktree** for deployment:

```bash
# 1. Add a worktree for the gh-pages branch
git worktree add /path/to/gh-pages-worktree gh-pages

# 2. Copy your file to the correct subdirectory in the worktree
cp docs/fargo/index.html /path/to/gh-pages-worktree/fargo/index.html

# 3. Commit and push from the worktree
cd /path/to/gh-pages-worktree
git add fargo/index.html
git commit -m "update(fargo): description"
git push origin gh-pages

# 4. Clean up (optional)
git worktree remove /path/to/gh-pages-worktree
git worktree prune
```

### Live URL After Deployment
```
https://owner.github.io/repo/<subpath>/index.html
```
e.g. `https://mcduck-s8.github.io/hermes-salon-landing/fargo/index.html`

### Windows/MSYS Path Pitfalls

On Windows with Git Bash (`/d/`, `/c/` path syntax):

| Problem | Cause | Fix |
|---------|-------|-----|
| Worktree dir created but empty | MSYS translates `/c/worktree` to `D:/c/worktree` (wrong) | Use `D:/path` instead of `/c/path` |
| `git status` fails in worktree | `.git` file points to wrong `gitdir` path | Check `cat .git/worktrees/<name>/gitdir` and ensure path exists |
| `ls /c/worktree-gh/` returns "not found" | MSYS path resolution glitch | Use native `C:/...` or `D:/...` consistently |

**Always verify the worktree checkout actually happened**:
```bash
ls /d/gh-pages-deploy/fargo/index.html   # should exist
cd /d/gh-pages-deploy && git status      # should show clean tree
```

## Social Preview / OG Images — Local Hosting

When sharing a GH Pages link on Telegram, Facebook, Twitter, or WhatsApp, the OG image may not appear even though the meta tags are correct. Common cause: **the OG image URL points to an external CDN that blocks social crawlers** (Pexels, Unsplash, or direct image hosts).

### Fix: Host OG Images Locally

```bash
# 1. Download the image to your repo
# Use Python (curl may have path issues on Windows)
url="https://images.pexels.com/photos/5069603/pexels-photo-5069603.jpeg"
python -c "
import urllib.request
req = urllib.request.Request('$url', headers={'User-Agent': 'Mozilla/5.0'})
data = urllib.request.urlopen(req, timeout=30).read()
with open('docs/site/og-image.jpg', 'wb') as f:
    f.write(data)
print(f'Saved {len(data)/1024:.0f}KB')
"

# 2. Update meta tags to local URL
# In your HTML <head>:
<meta property="og:image" content="https://owner.github.io/repo/site/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://owner.github.io/repo/site/og-image.jpg">

# 3. Commit, push, wait ~30-60s for GH Pages rebuild

# 4. Verify with Facebook Sharing Debugger:
# https://developers.facebook.com/tools/debug/
# Or curl the page and inspect OG tags:
curl -s https://owner.github.io/repo/site/ | grep -E "og:image|twitter:image"
```

### Pitfalls

| Mistake | Result | Fix |
|---------|--------|-----|
| Linking to Pexels/CDN URL for `og:image` | Image not shown in social preview | Host locally on same domain |
| Updating `og:image` but not `twitter:image` | Image shows on FB but not Twitter/X | Update both tags |
| Missing `twitter:card` meta | Twitter shows small card instead of large image | Add `<meta name="twitter:card" content="summary_large_image">` |
| Image too large (>300KB) | Social crawler times out fetching image | Keep under 300KB, use JPEG with quality 80-85 |
| Wrong `og:url` | Crawler fetches wrong page for preview | Match exact page URL (omit `index.html` or include it consistently) |

### Full OG Meta Block Template

```html
<meta property="og:title" content="Page Title — Site Name">
<meta property="og:description" content="Brief description of the page.">
<meta property="og:image" content="https://owner.github.io/repo/site/og-image.jpg">
<meta property="og:url" content="https://owner.github.io/repo/site/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Site Name">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://owner.github.io/repo/site/og-image.jpg">
```

## Network Constraints on This Machine

Git push and curl access to GitHub requires a SOCKS5 proxy:
```bash
ALL_PROXY=socks5h://127.0.0.1:10806 git push origin <branch>
```

## ⚠️ Post-Deploy Verification (MANDATORY — Do NOT Skip)

**Never report "deployed" until you verify the LIVE URL.** Pushing to git does NOT mean the live site is updated (build takes 2-5 min, CDN caches stale versions, can push to wrong branch).

### Checklist

- [ ] Wait 2-5 minutes for Pages rebuild
- [ ] Page loads without error (no 404/000/connection refused)
- [ ] `<title>` tag content matches expected
- [ ] All JS functions from old version exist in new version (`typeof fn === 'function'`)
- [ ] Images load (`img.complete && img.naturalWidth > 0`)
- [ ] Interactive features work (carousel clicks, button actions)
- [ ] Dark mode CSS present (if applicable)
- [ ] LIVE URL content matches git HEAD (compare unique CSS/text marker count)

### Verify with Browser Console
```javascript
// Function existence check
typeof moveSlide === 'function' && typeof initCarousel === 'function'

// Images loaded
[...document.querySelectorAll('img')].filter(i => i.complete && i.naturalWidth > 0).length

// Dark mode
document.querySelector('style').textContent.includes('prefers-color-scheme: dark')
```

### Common Failure Modes

| Symptom | Root cause | Fix |
|---------|-----------|-----|
| Live URL shows old content | Pushed to wrong branch | Check Pages source, push to correct branch |
| Live URL still old after pushing gh-pages | Pages auto-serves from default branch root — not gh-pages | Push to default branch root instead (the branch that has_pages) |
| Live URL returns 000/404 during rebuild | Pages building (normal) | Wait 2-5 min, retry |
| Git shows latest commit but live is old | Pushed to wrong branch OR CDN cache | Verify source branch exists at raw.githubusercontent.com, compare with live |
| All text content OK but carousel doesn't work | JS functions lost during `<write_file>` rewrite | Before rewrite: grep 'function ' from old file, keep all fn names |
| `<title>` missing from deployed version | Lost during full HTML rewrite | Pre-commit check: `grep '<title>' new_file` before committing |
| curl to live returns empty/000 | Network timeout or missing User-Agent | `curl -s -A "Mozilla/5.0" <url>` or use proxy