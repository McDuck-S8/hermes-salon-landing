# Forge prompt, used to generate this Telegram Mini App

```bash
python scripts/forge.py "Generate a complete self-contained Telegram Mini App HTML file for cricket betting in India. The page must be a single .html file with embedded CSS/JS using Telegram WebApp SDK (tg-app.js via CDN). Requirements: 1) Integrates Telegram WebApp SDK (window.Telegram.WebApp), 2) Dark theme respecting Telegram theme params (tg.themeParams.bg_color, etc.), 3) Match list with live scores India vs Australia, 4) Betting slip (add/remove selections), 5) CTA that opens 1win partners URL in external browser via Telegram.WebApp.openLink, 6) Shows MainButton for primary action, 7) Responsive mobile-first design, 8) Expand to full height via Telegram.WebApp.expand(), 9) Haptic feedback on buttons via Telegram.WebApp.HapticFeedback, 10) Close button handling. Output ONLY the complete HTML string in the data field." --provider opencode-zen
```

Result: `projects/tg-india-app/index.html` (8.9KB)

To regenerate with different offers/colors: modify prompt's items 3, 4, 5.
