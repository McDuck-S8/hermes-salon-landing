# Forge HTML Prompts — 2026-07-15

Real forge prompts used this session to generate three web artifacts instead of hand-coding.

## 1. PWA Landing Page (1win Cricket India)

**Target**: `projects/pwa-india/index.html`
**Result**: ✅ 9.6KB self-contained PWA with dark theme, match cards, install banner, service worker via blob URL, CTA to 1win Partners

```
python scripts/forge.py "Generate a complete self-contained PWA landing page HTML file for 1win cricket betting in India. The page must be a single .html file with embedded CSS and JS (no external dependencies). Requirements: 1) Dark theme (#0f0f23 background, #00ff88 accent green), 2) Cricket theme with match cards (India vs Australia live scores), 3) PWA install banner using beforeinstallprompt event, 4) manifest.json embedded as inline JSON-LD, 5) Service worker registered from within the same file using a blob URL or inline registration, 6) CTA button linking to 'https://1winpartners.in' 7) Offline-capable via cache API, 8) Push notification handler in service worker section, 9) Responsive mobile-first design, 10) Shortcuts for 'Live Scores' and 'Upcoming Matches'. Output ONLY the complete HTML as a single string in the data field of the JSON response." --provider opencode-zen
```

**Notes**:
- `--provider opencode-zen` was needed because cerebras/deepseek time out on large HTML generation
- Forge timeout needed ~60s due to ~10KB output
- Output had escaped newlines — extracted manually via `write_file`
- First attempt failed (triple-quote syntax error in generated Python), second succeeded

## 2. Telegram Mini App (Cricket Betting)

**Target**: `projects/tg-india-app/index.html`
**Result**: ✅ 8.9KB Telegram WebApp with theme variables, match list, odds grid, bet slip, MainButton, haptics

```
python scripts/forge.py "Generate a complete self-contained Telegram Mini App HTML file for cricket betting in India. The page must be a single .html file with embedded CSS/JS using Telegram WebApp SDK (tg-app.js via CDN). Requirements: 1) Integrates Telegram WebApp SDK (window.Telegram.WebApp), 2) Dark theme respecting Telegram theme params (tg.themeParams.bg_color, etc.), 3) Match list with live scores India vs Australia, 4) Betting slip (add/remove selections), 5) CTA that opens 1win partners URL in external browser via Telegram.WebApp.openLink, 6) Shows MainButton for primary action, 7) Responsive mobile-first design, 8) Expand to full height via Telegram.WebApp.expand(), 9) Haptic feedback on buttons via Telegram.WebApp.HapticFeedback, 10) Close button handling. Output ONLY the complete HTML string in the data field." --provider opencode-zen
```

**Notes**:
- One shot — first attempt succeeded
- The select/remove bet logic had a minor bug (selector reset on team switch) — fixed manually after generation
- Telegram WebApp SDK loaded from CDN (https://telegram.org/js/telegram-web-app.js)

## 3. SEO Article (IPL 2026 Preview)

**Target**: `projects/cricket-seo/index.html`
**Result**: ✅ 7.9KB SEO-optimized article with JSON-LD, Open Graph, dark theme, CTA

```
python scripts/forge.py "Generate an SEO-optimized HTML page for cricket betting tips India. Single .html file with embedded CSS/JS. Requirements: 1) Title: 'IPL 2026 Preview: Full Schedule, Teams Predictions & Betting Guide', 2) Dark cricket theme (#0d0d1a background, gold accents), 3) Article-style layout with H1, H2 sections, 4) SEO meta tags in head (description, keywords, og:title, og:description), 5) JSON-LD structured data for NewsArticle, 6) Internal links section to other articles, 7) CTA section with 1win partners link, 8) Footer with disclaimer '18+ Gamble Responsibly', 9) Mobile responsive, 10) Sitemap link in footer. Output ONLY the HTML string in the data field." --provider opencode-zen
```

**Notes**:
- One shot — first attempt succeeded
- Uses Unsplash background image (free, no API key)

## Common Pattern

All three prompts follow the same structure:

```
python scripts/forge.py "Generate a complete self-contained [TYPE] HTML file for [TOPIC]. Requirements: [numbered list of 8-10 specific features]. Output ONLY the [output format] string in the data field." --provider opencode-zen
```

**Key success factors**:
1. "complete self-contained" — single file, no external deps
2. "Output ONLY the X string in the data field" — forces forge to return HTML verbatim
3. Numbered requirements (8-12) — specific enough to produce working result
4. `--provider opencode-zen` — necessary for HTML output > 5KB

**Failure mode**: If forge returns Python code that wraps the HTML in triple-quoted strings, the Python may have syntax errors (unterminated strings). The sandbox captures the error and retries — second attempt usually succeeds.
