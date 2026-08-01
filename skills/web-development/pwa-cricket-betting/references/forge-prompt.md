# Forge prompt, used to generate this PWA

```bash
python scripts/forge.py "Generate a complete self-contained PWA landing page HTML file for 1win cricket betting in India. The page must be a single .html file with embedded CSS and JS (no external dependencies). Requirements: 1) Dark theme (#0f0f23 background, #00ff88 accent green), 2) Cricket theme with match cards (India vs Australia live scores), 3) PWA install banner using beforeinstallprompt event, 4) manifest.json embedded as inline JSON-LD, 5) Service worker registered from within the same file using a blob URL or inline registration, 6) CTA button linking to 'https://1winpartners.in' 7) Offline-capable via cache API, 8) Push notification handler in service worker section, 9) Responsive mobile-first design, 10) Shortcuts for 'Live Scores' and 'Upcoming Matches'. Output ONLY the complete HTML as a single string in the data field of the JSON response." --provider opencode-zen
```

Result: `projects/pwa-india/index.html` (9.6KB)

To regenerate with different brand/colors: modify the prompt's requirements 1, 4, 6.
