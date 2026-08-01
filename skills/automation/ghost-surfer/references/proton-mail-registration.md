# Proton Mail Registration via BrowserOS MCP — 2026-07-16

## Working URL
```
https://account.proton.me/mail/signup?plan=free&billing=12&currency=EUR
```

## Form Structure (Snapshot Elements)

| Element | Snapshot Ref | Type | Notes |
|---------|--------------|------|-------|
| Free Plan Button | 36350 | button | Must click to select Free tier |
| Username Input | 37489 | textbox | `id="username"` |
| Password Input | 36918 | textbox | `id="password"` |
| Confirm Password | 38155 | textbox | `id="password-confirm"` |
| Submit Button | 38017 | button | Text: "Начать использовать Proton Mail сейчас" |

## Registration Flow

1. **Navigate to signup URL** — loads multi-step form
2. **Select Free plan** — click button 36350 (Free 0€)
3. **Fill username** — evaluate_script: `document.getElementById('username').value = '...'`
4. **Fill password** — evaluate_script: `document.getElementById('password').value = '...'`
5. **Fill confirm** — evaluate_script: `document.getElementById('password-confirm').value = '...'`
6. **Dispatch events** — `input`, `change`, `blur` on each field
7. **Click submit** — evaluate_script clicks button[type="submit"] with text "Начать использовать Proton Mail сейчас"

## Challenge System (Proton's Custom Anti-Bot)

**IFrames loaded on page:**
| Index | Name | Src Pattern | Position |
|-------|------|-------------|----------|
| 0 | unauth | `challenge/v4/html?Type=0&Name=unauth` | Hidden (-1000px) |
| 1 | email | `challenge/v4/html?Type=0&Name=email` | Visible (~80px height) |
| 2 | login | `challenge/v4/html?Type=0&Name=login` | Hidden (-1000px) |

**Behavior:**
- Challenges are cross-origin (`account-api.proton.me`) — cannot access via `evaluate_script`
- Email challenge (iframe 1) is visible and likely requires user interaction
- No hCaptcha/reCAPTCHA scripts detected
- Challenge completion appears to be async — form stays on same URL

**Observed after submit:**
- URL remains `https://account.proton.me/signup?plan=mail&free=1&language=ru`
- `loading: true` detected in page state
- No "email sent" or "verification code" text appeared within 10s
- Username "taken" validation works (`aria-invalid="true"` on username field)

## Automation Strategy

```python
# 1. Fresh page
page_id = new_page("about:blank")

# 2. Inject fingerprint spoofing (for same-doc verification)
evaluate_script(page_id, SPOOFING_JS)

# 3. Navigate to signup
navigate_page(page_id, "https://account.proton.me/mail/signup?plan=free&billing=12&currency=EUR")

# 4. Wait for challenge iframe to load (visible one)
time.sleep(5)

# 5. Select Free plan
click(page_id, 36350)

# 6. Fill form via JS (bypasses fill tool which needs snapshot)
evaluate_script(page_id, f"document.getElementById('username').value = '{username}'")
evaluate_script(page_id, "document.getElementById('username').dispatchEvent(new Event('input', {bubbles:true}))")
# ... same for password, confirm

# 7. Submit
evaluate_script(page_id, '''document.querySelector('button[type="submit"]').click()''')

# 8. Wait for challenge completion / redirect
# Poll for URL change or success indicators
for _ in range(30):
    result = evaluate_script(page_id, "window.location.href")
    if "mail.proton.me" in result or "dashboard" in result:
        break
    time.sleep(2)

# 9. If challenge blocks — need human or specialized solver
# No standard CAPTCHA API works for Proton's custom challenge
```

## Known Issues

| Issue | Severity | Workaround |
|-------|----------|------------|
| Challenge iframe cross-origin | High | Cannot automate via evaluate_script; may need manual click or CDP |
| Username taken validation | Medium | Generate unique usernames (timestamp/random suffix) |
| No CAPTCHA API support | High | Proton uses proprietary challenge; 2captcha/anticaptcha won't work |
| Form stays on same URL after submit | Medium | Poll for redirect to `mail.proton.me` or `account.proton.me/dashboard` |

## Tested Identity
- **Username:** `alisa_morozova_ru_2024_xyz` (unique)
- **Password:** `Kx9#mP2$vL7!qR4@`
- **Status:** Form submitted, challenge active, no redirect yet

## Files
- `scripts/ghost_browser.py` — IdentityDB, GhostIdentity
- `scripts/account_registration.py` — AccountProfile, ProfileGenerator
- `identities.db` — Encrypted storage