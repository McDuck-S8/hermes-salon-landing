---
name: deploy-cosmetologist
title: Deploy Cosmetologist Site
description: Deploy the complete cosmetologist landing page to GitHub Pages via gh-pages worktree
---

# Deploy Cosmetologist Site

## Purpose
Deploy the updated cosmetologist landing page (`projects/cosmetologist-site/index.html`) to GitHub Pages for production.

## Deployment Path (gh-pages worktree)

```bash
# 1. Copy files to the gh-pages worktree
cp projects/cosmetologist-site/index.html /d/gh-pages-deploy/cosmetologist/
cp -r projects/cosmetologist-site/assets/* /d/gh-pages-deploy/cosmetologist/assets/

# 2. Commit and push via SOCKS5 proxy
cd /d/gh-pages-deploy
git add cosmetologist/
git commit -m "cosmetologist: update"
ALL_PROXY=socks5://127.0.0.1:10806 git push origin gh-pages

# 3. WAIT 2-5 min, then VERIFY LIVE URL
curl -s "https://mcduck-s8.github.io/hermes-salon-landing/cosmetologist/" | head -10
```

## ⚠️ Critical Guards

### JS-Preservation Before Copy
The carousel uses `onclick="moveSlide(1)"` and `onclick="moveSlide(-1)"` in HTML. The `<script>` section MUST define `moveSlide()` and `initCarousel()`.

Check before copying:
```bash
grep -oP 'onclick="\K[^"]+' projects/cosmetologist-site/index.html | sort -u
grep -oP '(function \w+|\bmoveSlide\b|initCarousel)' projects/cosmetologist-site/index.html
```

### Post-Push Verification
After push, verify the LIVE deployed content matches:
```bash
LIVE_TITLE=$(curl -s "https://mcduck-s8.github.io/hermes-salon-landing/cosmetologist/" | grep -o '<title>[^<]*')
COMMIT_TITLE=$(git show HEAD:cosmetologist/index.html | grep -o '<title>[^<]*')
# If mismatch → Page hasn't rebuilt yet, wait and retry
```

## Verification
- Check desktop version at https://mcduck-s8.github.io/hermes-salon-landing/cosmetologist/
- Verify carousel buttons work (prev/next click, dots navigation)
- Test dark mode toggle
- Confirm all images load
- Verify mobile responsive

## Assets
- `projects/cosmetologist-site/assets/` — all before/after photos + master image
- Real photos: master.jpg, ba_lips1.jpg, ba_lips2.jpg, ba_botox1.jpg, ba_more1-3.jpg, ba_jul14_1-2.jpg

## Known Issues
- Push requires `ALL_PROXY=socks5://127.0.0.1:10806` for network connectivity
- GitHub Pages takes 2-5 min after push to rebuild
- Always verify LIVE URL after deployment, not just git log
