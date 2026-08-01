---
name: github-pages-deployment
category: devops
description: Debug and fix GitHub Pages deployment issues — 404s, source.path mismatches, build failures
trigger: Pages returns 404 but files exist in repo, or build fails
---

# GitHub Pages Deployment Debugging

## Root Cause Pattern (2026-07-22)

**Problem:** `https://mcduck-s8.github.io/hermes-salon-landing/cosmetologist/` returns 404, but:
- Files exist in `cosmetologist/` on default branch (`user/hermes-session-2026-06-09`)
- `gh-pages` branch also has the files
- Other paths (`/fargo/`, `/old-salon/`) work

**Root cause:** Pages config `source.path` was `/docs` but files in repo root `/`.

```bash
# Check Pages config
gh api /repos/{owner}/{repo}/pages

# If source.path is wrong:
gh api --method PUT /repos/{owner}/{repo}/pages \
  -f source[branch]={branch} \
  -f source[path]=/

# Trigger rebuild
gh api --method POST /repos/{owner}/{repo}/pages/builds
```

## Diagnostic Checklist

| Check | Command |
|-------|---------|
| Pages enabled? | `gh api /repos/{owner}/{repo}/pages` |
| Source branch correct? | Check `source.branch` |
| **Source path correct?** | **Check `source.path` — must match file location** |
| Files in source path? | `gh api /repos/{owner}/{repo}/contents/{path}?ref={branch}` |
| Build status | `gh api /repos/{owner}/{repo}/pages/builds/latest` |
| Cached 404? | Check `age` header — if >0, CDN caching old 404 |

## Common Fixes

1. **Wrong source.path** → `gh api --method PUT /repos/.../pages -f source[path]=/`
2. **Wrong branch** → `gh api --method PUT /repos/.../pages -f source[branch]=main`
3. **Stale CDN cache** → Wait (5-10 min) or trigger rebuild
4. **No .nojekyll** → Add empty `.nojekyll` file to repo root
5. **Build failing** → Check `gh api /repos/.../pages/builds/latest` for error

## Lesson Learned

> Never assume Pages config. Always verify `source.path` matches actual file location. Default branch ≠ Pages branch. Files in root ≠ source.path=/docs.

### Session 2026-07-25 — Additional Fixes

### Issue: Subdirectory 404 (e.g., `/smart-home-cpa/`)

**Root cause**: Pages configured on wrong branch (`gh-pages` branch exists but Pages serves from `main` with `source.path=/docs`), so files pushed to `gh-pages` branch had no effect.

**Fix**:
1. Check config: `gh api repos/$OWNER/$REPO/pages | jq .source`
2. Deploy to the **configured branch**, not assumed branch
3. If using subdirectories, ensure `_config.yml` has correct `baseurl`:
   ```yaml
   url: https://mcduck-s8.github.io
   baseurl: /hermes-salon-landing
   ```
4. Ensure `.nojekyll` is **empty** (not "trigger" or any content)

### Session 2026-07-26 — GitHub Pages Rebuild Process & Subdirectory Deployment

**Root cause discovered**: GitHub Pages **does not auto-rebuild on every push to gh-pages branch** when the Pages source is configured to a different branch. The Pages build only triggers on pushes to the **configured source branch** (in this case `main` with `source.path=/docs`).

**Key findings from 2026-07-26 session:**

1. **Pages build trigger**: Only triggers on pushes to the **configured source branch** (checked via `gh api repos/$OWNER/$REPO/pages | jq .source.branch`). Pushing to `gh-pages` branch does NOT trigger rebuild when source branch is `main`.

2. **Rebuild process takes 2-5 minutes**: After triggering rebuild, GitHub Pages returns 404/000 during rebuild. Must wait 2-5 minutes and retry with 15s intervals.

3. **Subdirectory deployment with baseurl**: When deploying to subdirectory (e.g., `/smart-home-cpa/`), the site must have correct `baseurl` in `_config.yml`:
   ```yaml
   url: https://mcduck-s8.github.io
   baseurl: /hermes-salon-landing
   ```
   And the site must be deployed to the configured source branch with the subdirectory structure preserved.

3. **Force rebuild methods that WORK**:
   - Push to the **configured source branch** (not assumed branch)
   - Use `gh api --method POST /repos/{owner}/{repo}/pages/builds` to manually trigger
   - Empty commit on source branch: `git commit --allow-empty -m "trigger rebuild" && git push`
   - Touch `.nojekyll`: `echo " " >> .nojekyll && git add .nojekyll && git commit -m "rebuild" && git push`

4. **Subdirectory path access**: For `https://mcduck-s8.github.io/hermes-salon-landing/smart-home-cpa/` to work:
   - `baseurl: /hermes-salon-landing` in `_config.yml`
   - File structure: `source.path/smart-home-cpa/index.html`
   - Pages must be deployed to the **configured source branch** (not `gh-pages` branch if source is `main`)

5. **CDN cache lag**: After successful rebuild, CDN may cache old 404 for 1-5 minutes. Test with `curl -H "Cache-Control: no-cache"` or wait 1-5 minutes.

### Complete Deployment Checklist (Updated 2026-07-26)

- [ ] Check Pages config: `gh api repos/$OWNER/$REPO/pages | jq .source`
- [ ] Ensure target branch matches `source.branch`
- [ ] Ensure file path matches `source.path` + subdirectory
- [ ] Copy files to target branch (use worktree for clean separation)
- [ ] Ensure `.nojekyll` exists and is **EMPTY** (not "trigger")
- [ ] Add `_config.yml` with `baseurl` if using subdirectories
- [ ] Push with proxy if needed: `git -c http.proxy=socks5://127.0.0.1:10806 push`
- [ ] **Trigger rebuild**: Push to SOURCE branch OR `gh api --method POST /repos/$OWNER/$REPO/pages/builds`
- [ ] Wait 2-5 minutes for rebuild
- [ ] Test with curl, retry on 000/404 with 15s intervals
- [ ] Verify OG images work (host locally, not CDN)

### Issue: SSL/Proxy errors during git push (corporate/firewall)

**Fix**: Use git with SOCKS5 proxy:
```bash
git -c http.proxy=socks5://127.0.0.1:10806 push origin gh-pages
```

### Issue: CDN propagation lag (000 HTTP codes during rebuild)

**Observation**: After push, GitHub Pages rebuilds for 2-5 minutes. During rebuild, requests return 000/connection refused.

**Fix**: Wait 2-5 minutes after push before testing. Retry with 15s intervals.

### ⚠️ Variant: Empty page (0 bytes) during rebuild

In some cases, Pages returns **0 bytes / empty response** instead of a 404 or error during rebuild. This is NOT a code issue — it's the build window.

**Detection:**
```bash
curl -s "https://YOURSITE.github.io/REPO/PATH/" | wc -c
# Returns 0 during rebuild, >0 after build completes
```

**Fix:** Wait 60-90 seconds, retry. Do NOT start debugging the code. If user reports "всё пропало" immediately after push — it's Pages rebuilding.

### ⚠️ Post-Push Verification (CRITICAL)

Pushing to gh-pages branch does NOT guarantee the live site is updated. You MUST verify the LIVE URL, not just git log.

```bash
# Instead of: git log (WRONG — shows local state, not live)
curl -s https://YOURSITE.github.io/REPO/PATH/ | head -5
```

**Wait 2-5 min after push** for GitHub Pages to rebuild. Test with:
```bash
for i in 1 2 3 4 5; do
  curl -sI "https://mcduck-s8.github.io/hermes-salon-landing/cosmetologist/" | head -5
  sleep 60
done
```

**Check content diff live vs committed:**
```bash
curl -s "https://LIVE_URL" | grep -c "container-type"   # Should match committed version
git show HEAD:cosmetologist/index.html | grep -c "container-type"
# Compare counts — if mismatch, Pages is serving stale version
```

**Failure mode (2026-07-29):** Agent pushed to gh-pages, git showed latest commit, but live URL served old version for several minutes.

**TWO root causes:**
1. **Wrong branch**: Pages was configured on the DEFAULT BRANCH root, NOT on `gh-pages`. The `gh-pages` worktree at `D:/gh-pages-deploy` was misleading — Pages serves from `user/hermes-session-2026-06-09` root.
2. **Rebuild delay**: Even after pushing to the correct branch, it takes 2-5 minutes for Pages to rebuild.

**Why I got it wrong:**
- Repo had a `gh-pages` branch + worktree → assumed that's the Pages source
- `_config.yml` on `gh-pages` had `url`/`baseurl` → looked like Pages config
- Didn't verify via `gh api repos/OWNER/REPO/pages` (API returned 404 without auth)
- Deployed without comparing live URL vs git HEAD content first

**Fix:**
1. Check Pages source WITHOUT gh CLI:
   ```bash
   # Method 1: Use repo API
   curl -s https://api.github.com/repos/OWNER/REPO | python -c "import sys,json; d=json.load(sys.stdin); print('default_branch:', d.get('default_branch'), 'has_pages:', d.get('has_pages'))"
   
   # Method 2: Compare raw file vs live URL
   curl -s https://raw.githubusercontent.com/OWNER/REPO/DEFAULT_BRANCH/PATH/ | grep UNIQUE_CSS_CLASS
   curl -s https://LIVE_URL | grep UNIQUE_CSS_CLASS
   # If markers match → Pages serves from default branch root
   ```
2. Deploy to the correct branch (the one matching the live URL content)
3. **Never report "deployed"** until LIVE URL content matches git HEAD

**Pre-deploy verification checklist (MANDATORY):**
- [ ] Verify Pages source branch via raw file comparison (not assumption)
- [ ] Push to CORRECT branch (the source branch, not necessarily `gh-pages`)
- [ ] Wait 2-5 min for rebuild
- [ ] Check LIVE URL loads without 404/000
- [ ] Check `<title>` matches
- [ ] Check all JS functions exist: `typeof moveSlide === 'function'`
- [ ] Check images load: `img.complete && img.naturalWidth > 0`
- [ ] Check interactive features work (carousel clicks, hamburger toggle)
- [ ] **Check hamburger HTML exists in DOM** — CSS alone is not enough. Verify `document.querySelector('.mobile-toggle')` is non-null on the LIVE URL.
- [ ] **Check carousel dots render** — `document.getElementById('carouselDots')?.children.length > 0` confirms `initCarousel()` executed
- [ ] Compare diff: live version vs git HEAD (unique CSS/text marker count)

**Carousel responsive pitfall:** `initCarousel()` with hardcoded `visibleCount=N` scrolls by N-th fraction regardless of viewport. If CSS changes slide width on mobile (e.g. `min-width:100%`), JS still scrolls by `100/N` percent. Fix: detect `window.innerWidth` at init, use `count = width < 481 ? 1 : 3`, and re-init on resize (debounced 400ms). Never use `location.reload()` in the resize handler — use a proper `reinit()` that clears clones and dots before calling `initCarousel()` again.

**Hamburger menu pitfall:** Having `.mobile-toggle{display:flex}` in CSS is useless if the `<button class="mobile-toggle">` does not exist in the HTML. Always check both CSS AND HTML exist before assuming a feature works.

**Inline grid pitfall:** `style="grid-template-columns:1fr 1fr 1fr"` cannot be overridden by a class-based media query without `!important` because inline styles beat class styles in specificity. Use CSS classes for layout, or use `!important` in media queries. Better: never use inline `grid-template-columns` — always define in the stylesheet.

### Complete Deployment Checklist (Updated)

- [ ] Check Pages config: `gh api repos/$OWNER/$REPO/pages | jq .source`
- [ ] Ensure target branch matches `source.branch`
- [ ] Ensure file path matches `source.path` + subdirectory
- [ ] Copy files to target branch (use worktree for clean separation)
- [ ] Ensure `.nojekyll` exists and is **EMPTY**
- [ ] Add `_config.yml` with `baseurl` if using subdirectories
- [ ] Push with proxy if needed: `git -c http.proxy=socks5://127.0.0.1:10806 push`
- [ ] Wait 2-5 minutes for rebuild
- [ ] Test with curl, retry on 000/404
- [ ] Verify OG images work (host locally, not CDN)

### Network Constraints on This Machine