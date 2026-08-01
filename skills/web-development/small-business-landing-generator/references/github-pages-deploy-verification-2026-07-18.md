# GitHub Pages Deploy Verification — 2026-07-18

## Problem
Deployed landing pages to GitHub Pages but need to verify they're actually live and rendering correctly before reporting to user.

## Verification Protocol

### 1. Privacy Scan (Pre-Deploy)
```bash
python scripts/approval_policies.py docs/portfolio/beauty-salon/
python scripts/approval_policies.py docs/arbitrage/
# Both must return: "✅ CLEAN — X files scanned, 0 violations"
```

### 2. Git Push
```bash
git add docs/portfolio/beauty-salon/ docs/arbitrage/
git commit -m "Deploy beauty salon landing + CPA landings"
git push origin user/hermes-session-2026-06-09
```

### 3. Wait for CDN Propagation
- GitHub Pages: 1-3 minutes typical
- Cloudflare/CDN edge: up to 5 minutes

### 4. Curl Verification (Automated)
```bash
# Check HTML structure
curl -s "https://mcduck-s8.github.io/hermes-salon-landing/portfolio/beauty-salon/" | head -100

# Verify nav structure
curl -s "https://mcduck-s8.github.io/hermes-salon-landing/portfolio/beauty-salon/" | grep -A 15 '<nav id="nav">'

# Verify master photos
curl -s "https://mcduck-s8.github.io/hermes-salon-landing/portfolio/beauty-salon/" | grep -A 3 'master-photo'

# Verify hero padding
curl -s "https://mcduck-s8.github.io/hermes-salon-landing/portfolio/beauty-salon/" | grep 'padding: 160px'
```

### 5. Browser Check (If curl looks good)
Open in browser for visual confirmation of:
- Preloader dismisses (no blinking dot)
- Logo visible (gold color)
- Nav solid background
- Hero headline not cut off
- Master photos load (placeholder images)

## Pitfalls
1. **Cached old version** — user sees old HTML. Fix: `Ctrl+Shift+R` or wait.
2. **Preloader flash** — inline script after preloader element dismisses immediately.
3. **Phone number masked in curl** — `tel:+380****4567` vs `tel:+380441234567` — check both.

## Success Criteria
- [ ] Privacy scan: 0 violations
- [ ] Git push: success
- [ ] Curl: returns 200, correct HTML structure
- [ ] Browser: renders correctly (no blink, no cutoff)
- [ ] All 4 landings accessible

## Applied This Session
- 4 landings deployed: 3 CPA + 1 Beauty Salon
- All privacy clean
- All curl-verified
- Beauty salon: nav/logo/hero/master-photo fixes confirmed live