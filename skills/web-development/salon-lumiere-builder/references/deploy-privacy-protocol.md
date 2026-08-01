# Deploy & Privacy Verification Protocol — 2026-07-18

**Rule:** Every salon landing MUST pass both checks before being considered "deployed".

## 1. Build Output
```bash
python skills/web-development/salon-lumiere-builder/build_salon.py \
  --params params-example.json \
  --output-dir docs/portfolio
```

**Expected output:**
```
✅ Landing page built: docs/portfolio/beauty-salon/index.html
   Slug: beauty-salon
   Deploy: git add docs/portfolio/beauty-salon && git commit -m "Deploy beauty-salon" && git push
   Live URL: https://<user>.github.io/<repo>/portfolio/beauty-salon/
```

## 2. Privacy Scan (MANDATORY)
```bash
python scripts/approval_policies.py docs/portfolio/beauty-salon/
```

**Must output:** `✅ CLEAN — 1 files scanned, 0 violations`

**Patterns checked (from approval_policies.py):**
- `Crimea`, `Крым` (geo)
- `no KYC`, `no kyc`, `USDT payout`, `USDT вывод` (finance)
- `Тбанк`, `Тинькофф` (banking)
- `crypto wallet`, `крипта кошелек` (crypto)

**If violations found:** Fix in params or template BEFORE deploy. Do not deploy with violations.

## 3. HTML Structure Validation
```bash
python -c "
from bs4 import BeautifulSoup
soup = BeautifulSoup(open('docs/portfolio/beauty-salon/index.html'), 'html.parser')
assert soup.find('h1'), 'Missing H1'
assert soup.find('form', id='booking-form'), 'Missing booking form'
assert soup.select('.master-photo img'), 'Missing master photos'
assert soup.find(id='preloader'), 'Missing preloader'
print('✅ Structure OK')
"
```

## 4. Git Deploy
```bash
git add docs/portfolio/beauty-salon/
git commit -m "Deploy beauty-salon landing"
git push origin <branch>
```

## 5. Live Verification
```bash
curl -s "https://mcduck-s8.github.io/hermes-salon-landing/portfolio/beauty-salon/" | grep -c '<nav id="nav">'
# Should return 1
curl -s "..." | grep -c 'master-photo.*img'
# Should return 4
```

## Fargo Landing — Verified Checklist (2026-07-18)
- [x] Build: `build_salon.py` with params-example.json → `docs/portfolio/beauty-salon/index.html`
- [x] Privacy: `approval_policies.py` → CLEAN (0 violations)
- [x] Structure: H1, nav#nav, 4 master-photo img, booking-form, preloader all present
- [x] Git: committed `d5537f098` "Add salon-lumiere-builder skill..."
- [x] Live: https://mcduck-s8.github.io/hermes-salon-landing/portfolio/beauty-salon/ — renders correctly
- [x] User-perspective: 4 questions answered in params-example.json