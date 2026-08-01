# Before/After Split-Screen Comparison Page

> Neutral redesign showcase: current site vs updated version, side by side with synced scrolling.
> **No value judgments.** No red/green. No checkmarks/crosses. No "better/worse".
> Purpose: let clients see the visual difference, not be told their site is "bad".

## Core Principles

1. **NEVER make up placeholder content.** Use the REAL current site URL or a live screenshot.
2. **Zero evaluation.** Left panel = "Текущий сайт" (neutral), Right panel = "Обновлённая версия". No badges, no colors.
3. **Sync scroll must work.** Cross-origin iframes CANNOT sync scroll. Use the technique below.

## Architecture (Cross-Origin Safe)

When the "current" site is on a different domain (cross-origin), you CANNOT use an iframe for it — sync scroll will silently fail. Use this pattern:

```
┌──────────────────────────────────────────────┐
│  Редизайн сайта: Fargo — салон краси …       │ ← neutral header
├─────────────────────┬────────────────────────┤
│ [Текущий сайт] 🔗   │ [Обновлённая версия]    │ ← no colors
│                     │                         │
│ <div.scroll-wrap>   │ <iframe>                │ ← same-origin div
│   <img screenshot>  │   fargo/                │ ← same-origin iframe
│                     │                         │
├─────────────────────┴────────────────────────┤
│  ✏️ Обсудить проект → Telegram               │ ← single CTA
└──────────────────────────────────────────────┘
```

## Files

```
docs/
  portfolio.html                 ← comparison page
  {client}-screenshot.png        ← full-page screenshot of current site
  {client}/                      ← "after" site (the new landing page)
```

## Step-by-Step

### 1. Get the Real Current Site

```bash
# Check if it even loads
curl -s -o /dev/null -w "%{http_code}" "https://www.salonfargo.com/"
# Check frame-ability
curl -sI "https://www.salonfargo.com/" | grep -i "x-frame-options" || echo "OK to embed"
```

### 2. Take a Full-Page Screenshot

Use the browser tool to navigate to the site, then the screenshot is saved automatically:

```js
// The browser_vision() call captures a screenshot even when vision analysis fails
// The file is at: cache/screenshots/browser_screenshot_<hash>.png
```

Copy it to `docs/{client}-screenshot.png`.

If the site blocks screenshots, use `web_extract` or `browser_console` to get page text, and create a clean informational stub instead.

### 3. Build the Comparison Page

**Left panel**: `<div class="scroll-wrap">` with `<img>` of the screenshot + `<a>` link to the real site in header.

**Right panel**: `<iframe>` with the new landing page (same-origin, relative path).

**Sync scroll**: Both containers are same-origin, so fully controllable.

```js
// Sync: left div (scrollable content) ↔ right iframe (same-origin)
const lw = document.getElementById('leftWrap');
const rf = document.getElementById('rightFrame');
let syncing = false;

// left → right
lw.addEventListener('scroll', () => {
  if(syncing) return; syncing = true;
  const rw = rf.contentWindow;
  const lPct = lw.scrollTop / (lw.scrollHeight - lw.clientHeight);
  if(rw && isFinite(lPct)){
    const rMax = rw.document.documentElement.scrollHeight - rw.document.documentElement.clientHeight;
    rw.scrollTo({top: lPct * rMax, behavior: 'instant'});
  }
  requestAnimationFrame(() => { syncing = false; });
}, {passive: true});

// right → left
rw.addEventListener('scroll', () => {
  if(syncing) return; syncing = true;
  const rEl = rw.document.documentElement;
  const rPct = rEl.scrollTop / (rEl.scrollHeight - rEl.clientHeight);
  if(isFinite(rPct)){
    lw.scrollTop = rPct * (lw.scrollHeight - lw.clientHeight);
  }
  requestAnimationFrame(() => { syncing = false; });
}, {passive: true});
```

**Draggable divider** (optional but nice):

```js
const divider = document.getElementById('divider');
divider.addEventListener('mousedown', (e) => { /* ... */ });
document.addEventListener('mousemove', (e) => {
  let pct = (e.clientX - rect.left) / rect.width;
  pct = Math.max(0.15, Math.min(0.85, pct));
  panels[0].style.flex = pct;
  panels[1].style.flex = 1 - pct;
});
```

Clamp range: 15%–85% so neither panel disappears.

### 4. Neutral Design

| Element | Style |
|---------|-------|
| Panel headers | `#18181a` bg, `#e0e0e0` text, `#2a2a2d` border |
| Left header | `strong "Текущий сайт"` + `a` link to real site ↗ |
| Right header | `strong "Обновлённая версия"` |
| Panel separator | `1px solid #222` |
| Divider handle | Dark circle `#222` with `#444` border, no color accents |
| Footer CTA | Dark button `#2c2c2e`, text "✏️ Обсудить проект" |
| Title | `h1 "Редизайн сайта: {Client} — {tagline}"` |
| Subtitle | `p "Обновили дизайн и сделали сайт удобным для записи клиентов"` |

**DO NOT use:**
- ❌ Red borders, green borders, or any colored panel accents
- ❌ Checkmarks (✅) or crosses (❌)
- ❌ Badges saying "старый", "устаревший", "проблема", "плохой"
- ❌ Words like "лучше", "хуже", "vs", "before/after", "было/стало"
- ❌ "Наш продукт" — just state facts

### 5. Mobile

```css
@media(max-width:768px){
  .viewport{flex-direction:column}
  .panel-left{border-right:none;border-bottom:1px solid #222}
  .panel{min-height:40vh}
  .divider{display:none}
}
```

Panels stack vertically on mobile. Divider hidden. Independent scroll (not synced).

## Why Not Iframe for the Current Site?

Cross-origin iframes (= loading a different domain) have **two fatal problems**:

1. **Cannot read scroll position** — `contentWindow.document` throws a security error
2. **Cannot set scroll position** — same security restriction

Tools that promise `postMessage` scroll sync require modifying BOTH sites. For client demos, you only control one side. The screenshot-in-div approach solves this cleanly.

If the current site IS same-origin (hosted on same GitHub Pages / subfolder), you CAN use an iframe. But for real client sites (different domain), use the screenshot approach.

## When Screenshot Is Blocked

If the site blocks browser screenshots or fails to load:
1. Try `browser_console(expression=...)` to inspect the page via DOM
2. Create a clean informational stub page with: business name, address, phone, services list
3. Add a prominent link: "Открыть оригинальный сайт → {url}"
4. Label it "Текущий сайт — базовая информация" — transparent about it being a stub

## Verification Checklist

- [ ] Screenshot shows the REAL current site, not a made-up stub
- [ ] Both panels load without errors (check browser console)
- [ ] Sync scroll works: scrolling left → right moves; scrolling right → left moves
- [ ] Divider drags smoothly (desktop)
- [ ] Mobile: panels stack, no divider, both scroll independently
- [ ] No red/green/colored elements
- [ ] No value-judgment words or symbols
- [ ] Telegram link is correct
- [ ] All relative paths resolve (no 404s on iframes/images)
