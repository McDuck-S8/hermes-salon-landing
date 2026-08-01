# Business Landing Page Pattern

## When to Use
You have a markdown business plan (business-plan.md) and need a professional visual landing page for client presentations, embeds, or sharing.

## Approach

### Structure (from top to bottom)
1. **Hero** — product name + tagline + CTA buttons, gradient background
2. **Stats bar** — key metrics (price, savings, ROI) as horizontal counter cards
3. **Problem/Solution** — pain vs promise side-by-side comparison (✕ / ✓ lists)
4. **Pricing** — 3-tier card grid: Basic / Featured (recommended) / Subscription
5. **Financial projection** — 6-month revenue table with totals row
6. **Competitor analysis** — 4-card grid (3 competitors + your solution highlighted)
7. **Roadmap** — vertical timeline with status tags (done/active/pending)
8. **Ecosystem** — project cards with color-coded status (green/yellow/red)
9. **Health metrics** — KPI cards (running code, money-making, etc.)
10. **Footer**

### Color System (Dark Theme)
```
--bg: #0a0a0f
--surface: #12121a
--surface2: #1a1a28
--border: #2a2a3e
--text: #e8e8f0
--text2: #8888a0
--accent: #6c5ce7 (purple)
--accent2: #a29bfe (light purple)
--green: #00b894
--orange: #fdcb6e
--red: #e17055
--gradient: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 50%, #00b894 100%)
```

### Key Components

#### Hero Section
```html
<h1>Product name — tagline</h1>
<p>Value proposition (1-2 sentences)</p>
<a href="#pricing" class="btn btn-primary">💰 Смотреть цены</a>
<a href="#roadmap" class="btn btn-secondary">📋 План запуска</a>
```

#### Pricing Card (Featured)
```html
<div class="pricing-card featured">
  <div class="pricing-name">Название тарифа</div>
  <div class="pricing-price">$2 500 <span>единоразово</span></div>
  <ul class="pricing-features"><li>✓ Feature</li></ul>
  <a href="#" class="btn btn-primary">Выбрать</a>
</div>
```
Use `featured` class for the recommended tier — adds purple border, subtle gradient, and a "Рекомендуем" badge.

#### Financial Table
```html
<table class="finance-table">
  <tr><th>Месяц</th><th>Новые установки</th><th>Выручка</th><th>Накопительно</th></tr>
  <tr><td>1</td><td>1</td><td>$1 500</td><td>$1 500</td></tr>
  <tr class="totals"><td colspan="3">Итого</td><td><strong>$18 880</strong></td></tr>
</table>
```

#### Roadmap Timeline
```html
<div class="roadmap">
  <div class="roadmap-item done">
    <div class="roadmap-day">Неделя 1 · сделано</div>
    <div class="roadmap-title">Заголовок</div>
    <div class="roadmap-desc">
      Пункт<span class="roadmap-tag tag-done">✓</span>
    </div>
  </div>
  <div class="roadmap-item active">...</div>
</div>
```

### Process
1. Extract all data from business-plan.md (pricing, projections, competitors, roadmap)
2. Build HTML with embedded CSS (no external files)
3. Use Google Fonts (Inter) via CDN for typography
4. Set viewport meta for mobile responsiveness
5. Add hash-links for anchor navigation (#pricing, #roadmap, #market, #finance)
6. Test: open in browser, verify all sections render, check mobile layout

### Pitfalls
- Don't use markdown tables — convert to styled HTML tables with hover states
- Don't use JS framework — pure CSS is faster and portable
- Financial numbers: use $ prefix, thousand separators, bold for totals
- Roadmap: every item needs a status tag, not just text
- Competitor section: always highlight YOUR solution with a different background
- Stats bar numbers should be REAL metrics from the business plan, not filler
- Keep the file self-contained — single HTML file with embedded CSS, CDN font only

### File Location
Save as `projects/business-plan.html` alongside `projects/business-plan.md`.
The markdown stays as source of truth; HTML is the rendered sales page.
