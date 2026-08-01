# Mini App Self-Contained Demo Pattern

## Why

Building a Telegram Mini App normally requires:
- A running web server
- Bot API integration
- Database backend

For development and review, build a **self-contained HTML file** with hardcoded demo data. Opens in any browser, shows the full UX, requires zero backend.

## Architecture

```
bot/webapp/
└── index.html           ← Single file, everything inline
    ├── CSS              ← Design system (gradients, cards, shadows)
    ├── HTML             ← Step-based UI (service → master → date → time)
    └── JavaScript       ← Demo data + UI logic + tg.sendData()
```

## Demo Data Pattern

```javascript
// Fallback demo data when API not available
services = [
  { id: 1, emoji: '💇', name: 'Service Name', price: 1500, duration: 60, category: 'стрижки' },
  // ...
];
masters = [
  { id: 1, name: 'Master Name', bio: 'Specialist', rating: 4.8 },
  // ...
];

// Try API first
async function init() {
  try {
    const resp = await fetch('https://api.example.com/services');
    services = await resp.json();
  } catch (e) {
    // Use hardcoded data — works offline
  }
  renderUI();
}
```

## Telegram Integration

- `tg.sendData(JSON.stringify({...}))` — sends booking data to bot
- `window.Telegram.WebApp.expand()` — full-screen mode
- `tg.ready()` — signal readiness

## UI Patterns (2026)

- **Card-based layout** — rounded cards with shadows, emoji icons
- **Step progression** — service → master → date → time (with back buttons)
- **Calendar grouping** — утро (9-12) / день (12-17) / вечер (17-20)
- **Smart date labels** — "Сегодня", "Завтра" instead of day numbers
- **Progress indicator in button** — "1/4 Выберите услугу" → "2/4 Выберите мастера" → "✅ Подтвердить — 1500₽"
- **Success screen** on `tg.sendData()`

## Working Example

- `D:/Portable_Soft/hermes/projects/salon-bot/bot/webapp/index.html`
- Opens directly in Chrome/Edge via `file:///` path
- All services (6 items in 4 categories), 3 masters, 14-day calendar, time slot grid
- Submit button shows progress, calls `tg.sendData()` for real Telegram integration
