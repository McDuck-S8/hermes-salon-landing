# Salon Website Design Patterns

> Concrete patterns from: salonfargo.com redesign (2026-07-11)
> Palette: Terracotta+Slate (anti-slop-compliant)
> Market: Ukraine, beauty salon, two locations

## Key Sections for Salon Sites

1. **Hero** — full-viewport, warm gradient overlay (terracotta gradient), salon photo at ~30% opacity, headline + subtext + CTA buttons
2. **About** — image left, text right. Use warm tone, end with italic signature
3. **Services** — 6-card grid (2x3 or 3x2). Feature one card with inverted colors (terracotta bg, white text) for top service
4. **Prices** — two-column price list. Items separated by dashed borders. Use serif font for amounts, sans-serif for names
5. **Promotions** — dark section (inverted mood). Cards with colored tag badges (terracotta), old price strikethrough, new price in amber
6. **Schedule** — cream bg (oklch(93% 0.01 70) — anti-slop compliant variant). Cards with left border accent. Slot rows with date/time alignment
7. **Gallery** — masonry grid with 2-span hero cell. 4-5 photos minimum. CTA to Instagram
8. **Locations** — two cards side by side. Each has emoji marker, address, hours, phone
9. **Contact/Booking** — two-column: contact info (icon+text items) + form (name, phone, service select, location select, date select, time select, comment). Date select populated by JS (30 days ahead, skip Sundays), time select with 30-min slots 09:00–20:30.

## Palette (Terracotta+Slate)

| Role | OKLCH | Hex | Usage |
|------|-------|-----|-------|
| Primary | oklch(58% 0.08 38) | #c46a4a | CTAs, accents, featured cards |
| Dark | oklch(25% 0.008 60) | #1a1814 | headings, hero bg |
| Slate | oklch(38% 0.01 60) | #4a4542 | body text |
| Slate Light | oklch(50% 0.01 60) | #6b6560 | secondary text |
| Warm bg | oklch(96% 0.005 70) | #f7f4f0 | page background |
| Cream alt | oklch(93% 0.01 70) | #f0ebe4 | schedule section bg |
| Amber | oklch(68% 0.08 78) | #c4954a | promo prices, secondary accent |

## Typography

- **Headings:** Cormorant Garamond (Google Fonts, serif — luxury/editorial feel)
- **Body:** Inter, system-ui (clean, readable)
- **Eyebrow section labels:** 0.75rem, uppercase, 0.12em tracking, terracotta color
- **Signature/quote:** Cormorant Garamond italic, 1.4rem, terracotta

## Single-File Approach

For quick demos (1 page, no backend), use **single HTML file** with:
- CSS in `<style>` block
- JS in `<script>` at end of body
- Removes the need for separate CSS/JS files
- Faster delivery to client as a single file
- Google Fonts via CDN `<link>` in head
- Pexels photos for real imagery (URL format: `https://images.pexels.com/photos/{ID}/pexels-photo-{ID}.jpeg?auto=compress&cs=tinysrgb&w={WIDTH}&h={HEIGHT}&fit=crop`)

## Pexels Photo IDs for Beauty Salon

⚠️ **HTTP 200 ≠ correct content.** Always verify BOTH: (1) URL returns 200, (2) photo actually shows beauty/hair/salon content. Some IDs return 200 but show unrelated content. User will reject mismatched photos immediately ("це не те фотки", "там природа").

### Two-Step Verification Process
```bash
# Step 1: HTTP status check (catches broken links only)
curl -sI "https://images.pexels.com/photos/{ID}/pexels-photo-{ID}.jpeg?auto=compress&cs=tinysrgb&fit=crop" | grep -i "HTTP/"
# Must return 200. 404/301 → find another ID.

# Step 2: Visual content check (catches wrong content — NEW, learned 2026-07-11)
# Use browser_vision to inspect what the photo actually shows
# HTTP 200 does NOT mean the content is contextually relevant!
```
```javascript
// Example visual check:
browser_navigate("https://images.pexels.com/photos/{ID}/pexels-photo-{ID}.jpeg")
browser_vision("Is this a beauty salon / hair / manicure / makeup photo? Describe the subject.")
```

### IDs That Return 200 BUT User Rejected as Wrong Content

| ID | Result | Lesson |
|----|--------|--------|
| 5069595 | HTTP 200, user said "не те фотки" | Content unrelated to salon context |
| 5069598 | HTTP 200, user said "не те фотки" | Content unrelated to salon context |

→ `curl` cannot catch these. Only `browser_vision` can verify content relevance.

### Verified Salon Photos (content confirmed by user)

| Content | Pexels Photo ID | Notes |
|---------|----------------|-------|
| Salon interior | 3997993 | General salon view |
| Woman getting haircut (cottonbro) | 3992875 | Haircutting scene |
| Woman haircut styling | 3993320 | Styling result |
| **Confirmed MISMATCH — DO NOT USE 5069601** | 5069601 | **User confirmed: shows a bird, not manicure. Replaced with 3997386 below** |
| Manicure | 3997386 | Manicure with UV lamp — safer alternative |**
| Hair styling / blow-dry | 5069603 | Gallery photo (verified from original index.html) |**
| Salon / beauty work | 5069604 | Gallery photo (verified from original index.html) |**
| Hair styling at salon | 29189945 | Styling session |
| Elderly haircut | 8834068 | Senior client |
| Hair styling / blow-dry | 5069603 | Good for gallery |
| Salon beauty work | 5069604 | General salon shot |

### Known Broken IDs (DO NOT USE)

| ID | Issue |
|----|-------|
| 5069606 | Returns 404 (broken link) |
| 3912581 | Returns 404 |
| 3997979 | UNVERIFIED — check before use |
| 3997991 | UNVERIFIED — check before use |

### URL Format
```
https://images.pexels.com/photos/{ID}/pexels-photo-{ID}.jpeg?auto=compress&cs=tinysrgb&w={WIDTH}&h={HEIGHT}&fit=crop
```
- `fit=crop` for consistent aspect ratios
- Match dimensions to container: `w=1920&h=1080` hero, `w=800&h=1000` about, `w=400&h=280` gallery thumbs

## Google Maps Integration (Two-Location Salon)

Use **clickable directions links with exact coordinates** — embedded iframe is optional.

### Directions Link
```html
<a href="https://www.google.com/maps/dir/?api=1&destination={LAT},{LNG}" target="_blank">
  🗺️ Прокласти маршрут
</a>
```

### Coordinates for Kyiv Locations
| Address | Latitude | Longitude |
|---------|----------|-----------|
| Княжий Затон, 2/30 | 50.40352 | 30.62927 |
| Анни Ахматової, 30 | 50.4081 | 30.62155 |

### Embed Map (optional, iframe)
```html
<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2543.5!2d30.625!3d50.405!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x40d4d3a0e50cbcf9%3A0xa4e1f4c4f4c4f4c4c!2z0JrQvdGP0LbQuNC5INCX0LDRgtC-0L0sIDIvMzAsINCa0LjRlNCy!5e0!3m2!1suk!2sua!4v1" width="100%" height="350" style="border:0;display:block" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
```
⚠️ Inline iframe is optional and shows a "For development purposes" watermark without API key. For clean map display, use a screenshot-based approach or OpenStreetMap embed.

## Complete Price List Extraction (CRITICAL)

**Do NOT abbreviate the price list.** Transfer EVERY single price from the original site. Users notice missing rows immediately ("не весь прайс перенес").

### Extraction Process
1. Use `web_extract` or `browser_navigate` + full snapshot to get the complete page content
2. Parse all price categories — the original site likely has 8+ blocks
3. Transfer every row, including sub-categories by hair length (I-VII)
4. For color services, include both "cheaper" and "premium" lines (e.g., Indola / Vibrance pricing)
5. Maintain the original structure: category headers, sub-category labels, lengths table

### Salon Price Categories (from salonfargo.com)
1. Перукарський зал — 14 rows (стрижка жін/чол/дитяча, кінчики, чубчик, борода, маски, пілінги)
2. Укладки та зачіски — 13 rows (браш I-VI довжин, накрутка, зачіски)
3. Фарбування волосся — 7 rows (корені, спецблонд, Vibrance, однотон 2 лінійки × I-VII довжин)
4. Техніки фарбування — 13 rows (омбре/шатуш/балаяж × II-VII, розтяжка кольору 2 лінійки × I-VII)
5. Мелірування / Блонд — 13 rows (тотал блонд, AirTouch, вихід з чорного, блонд-миття)
6. Догляд за волоссям — 9 rows (експрес Kristal Evo, Bond Yellow, VIART, Molecula, доповнення)
7. Манікюр — 17 rows (комплекс, чоловічий, покриття, дизайн, ремонт, зняття)
8. Педикюр — 12 rows (комплекс, френч, покриття)
9. Масаж — 15 rows (загальний, комбінований, зони, лімфодренаж, спортивний, антицелюліт, вагітні)
10. Татуаж / ламінування / макіяж / бровіст — 15 rows

### Price Format
- **Ukrainian**: ₴ after amount with space (e.g., "800 ₴" or "800–1 000 ₴")
- **Ranges**: use en-dash "–" for price ranges (e.g., "800–1 000 ₴")
- **Sub-labels**: italicized smaller text above sub-groups

### Pitfall: Incomplete Price List
User will notice missing rows immediately ("не весь прайс перенес"). Common omissions:
- Skipping sub-categories (hair length I–VII gradations)
- Only showing one price line when the salon has two (e.g., Indola AND Vibrance pricing)
- Omitting add-ons (prepigmentation, Fiberplex, znyattya)
- Forgetting men's/brow/massage sections that are separate from hair

**Fix:** Copy every visible row from the original site. Group into blocks by category. Use `web_extract` with full `char_limit=30000` to get complete content.

## Interactive Booking Pattern: Click Slot → Pre-Fill Form

### Problem
User wants: "при клике на время сразу бы в заявке проставлялась бы и услуга дата время сразу" — clicking a slot time should pre-fill the booking form with service, date, time, and location.

### Architecture
```
.slot-card
  ├── h3[data-service="Стрижка жіноча"]   ← service mapped to dropdown
  ├── .slot-date "📅 11 липня (субота)"   ← date text
  ├── .slot-times
  │   └── span.slot-time "10:30"          ← click target (cursor:pointer)
  └── .slot-date "📅 12 липня (неділя) — Княжий"  ← date +location
      └── .slot-times
          └── span.slot-time "10:00"
```

### Implementation (Vanilla JS, event delegation)
```javascript
// Single event listener on .slots-grid — handles ALL slot-time clicks
document.querySelector('.slots-grid')?.addEventListener('click', function(e) {
  const el = e.target.closest('.slot-time');
  if (!el) return;

  // Extract service from parent card h3 data-service attribute
  const card = el.closest('.slot-card');
  const service = card?.querySelector('h3')?.dataset?.service || '';

  // Walk backwards to nearest .slot-date sibling
  let dateEl = el.parentElement?.previousElementSibling;
  while (dateEl && !dateEl.classList.contains('slot-date')) {
    dateEl = dateEl.previousElementSibling;
  }
  const dateText = dateEl ? dateEl.textContent.replace('📅 ','').trim() : '';
  const time = el.textContent.trim();

  // Parse salon from date text (e.g., "— Княжий" or "— Ахматової")
  let salon = '';
  if (dateText.includes('— Княжий')) salon = 'Княжий Затон, 2/30';
  else if (dateText.includes('— Ахматової')) salon = 'Анни Ахматової, 30';

  // Fill form selects
  const svc = document.getElementById('service');
  if (svc) Array.from(svc.options).forEach(o => o.selected = o.text === service);
  const sln = document.getElementById('salon');
  if (sln) Array.from(sln.options).forEach(o => o.selected = o.text === salon);

  // ⚠️ Fill date+time into dedicated selects, NOT comment textarea
  const dt = document.getElementById('date');
  if (dt) Array.from(dt.options).forEach(o => o.selected = o.text === dateText);
  const tm = document.getElementById('time');
  if (tm) Array.from(tm.options).forEach(o => o.selected = o.text === time);

  // Scroll to form, focus name
  document.getElementById('booking')?.scrollIntoView({ behavior: 'smooth' });
  setTimeout(() => document.getElementById('name')?.focus(), 600);
});
```

### Key Requirements
1. **`data-service` on h3** — maps slot card to dropdown option text (exact match)
2. **`cursor:pointer` on .slot-time** — visual clickability cue
3. **Event delegation** — one listener, no per-slot onclick attributes
4. **Salon parsing from date text** — pattern "— Княжий" / "— Ахматової"
5. **Reset on missing service** — if service text doesn't match any option, fall back to default

### Service-to-Card Mapping
| Slot card heading | `data-service` value |
|-------------------|---------------------|
| 💇‍♀️ Стрижка, укладка, полірування | Стрижка жіноча |
| 🎨 Фарбування / Реконструкція | Фарбування волосся |
| 💅 Манікюр / Педикюр | Манікюр |
| ✨ Ламінування / Татуаж / Масаж / Макіяж | Ламінування |

### Date Text Format (for salon parsing)
- Without location: `📅 11 липня (субота)` → no salon selected
- With location: `📅 12 липня (неділя) — Княжий` → parse "— Княжий"
- With location: `📅 12 липня (неділя) — Ахматової` → parse "— Ахматової"

### Known Issues
- Service dropdown text must EXACTLY match `data-service` (case-sensitive)
- Date format with location suffix is fragile — any change to the text template breaks salon parsing
- For slots with no salon mention, the salon dropdown stays at default
- **DO NOT write date/time into .comment textarea** — user WILL object and demand dedicated `<select>` elements instead. User correction: *"форма записи менять не нужно было. верни как было. т е по клику выставлялись не в Коментар"*. Add `<select id="date">` and `<select id="time">` to the form and populate them on slot click.

## Verified Contact Info (salonfargo.com)

| Field | Value |
|-------|-------|
| Phones | +380 99 614 00 54, +380 67 665 46 46, +380 66 253 47 69 |
| Email | fargosalon@gmail.com |
| Telegram | @fargosalon |
| Instagram | @fargosalon |
| Hours | Щоденно 10:00–20:00 |
| Currency | ₴ (Ukrainian hryvnia) |

These were extracted from the actual live site. Always verify contact info by checking the original site — do not fabricate.

## Ukrainian Market Notes

- Use Ukrainian language (not Russian) for Kyiv-based salons
- Currency: ₴ (UAH) — use ₴ suffix after amount (e.g., "800 ₴")
- Phone format: +380 XX XXX XX XX
- Pexels works reliably in Ukraine (Unsplash may be slow/blocked)
- Google Maps integration for two-location display
- **Instagram is primary social platform** for Ukrainian salons — always link @handle
- **Gallery photos MUST match business context**: beauty/hair/salon shots, NOT nature/phones/random stock. Verify with browser_vision, not just curl. User will reject mismatched photos ("там природа", "не те фотки").
- **Price list must be COMPLETE** — copying a subset fails user review. Extract EVERY category and row from the original site.
- **Google Maps** requires two clickable directions links with exact coordinates (not just text addresses)

## Selling to Salon Owner

1. **Show "before/after"** — screenshot current site + live demo
2. **Online booking** — most urgent gap (no current booking form)
3. **Mobile-first** — current site likely not mobile-friendly
4. **Phone always visible** — click-to-call on mobile
5. **Instagram integration** — gallery + link to @handle
6. **Load time** — from minutes to < 3 seconds
7. **Price visibility** — prices on main page so clients don't leave