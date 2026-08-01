# Salon Landing Fix — 2026-07-18

## Session Context
User requested beauty salon landing page for Kyiv (Fargo salon, Poznyaky). Applied user-perspective framework (4 questions) and fixed issues from screenshot feedback.

## User-Perspective 4 Questions Applied
| # | Question | Answer |
|---|----------|--------|
| 1 | Who sees it? | Woman 28-45, Kyiv (Poznyaky), needs haircut/coloring. Has job, limited time, wants to see master's portfolio BEFORE visit. |
| 2 | What understood in 5 sec? | "Fargo — salon in Poznyaky. Honest prices on site, master portfolios, online booking in 30 sec. No calls." |
| 3 | What will they do? | Click "Book online" (gold CTA in hero) → select service → date → time → submit form. |
| 4 | Why? | Tired of checkout surprises. Wants to see Olena's (colorist) work before visit, know price upfront, book without calling admin. |

## Issues Fixed (from screenshot + user feedback)

### 1. Logo Invisible on Transparent Nav
**Problem:** Nav background transparent initially, logo used white text → invisible on hero background.
**Fix:** Nav MUST have solid background from load:
```css
nav {
    background: rgba(10,10,10,0.85);  /* Solid from start */
    backdrop-filter: blur(20px) saturate(1.2);
    border-bottom: 1px solid var(--glass-border);
}
nav.scrolled { background: rgba(10,10,10,0.95); }
```
**Rule:** Never rely on scroll to add background. Hero content scrolls UNDER nav immediately.

### 2. Duplicate Nav Links
**Problem:** Nav had both `<li><a href="#booking">Booking</a></li>` in center list AND `<a href="#booking" class="nav-cta">Booking</a>` on right.
**Fix:** Center list = section anchors only (Services, Masters, Reviews, Contact). Right actions = CTA button + phone link ONLY.

### 3. Hero Padding Too Small → Title Cut Off
**Problem:** `padding-top: 120px` on hero not enough for fixed nav (80px) + breathing room → h1 clipped.
**Fix:** `padding-top: 160px` minimum for fixed nav layouts.

### 4. Master Photos with Placeholder Fallback
**Pattern:** Use real photo URLs with inline `onerror` fallback to emoji:
```html
<div class="master-photo">
  <img src="https://via.placeholder.com/300x300/1a1a1a/C9A96E?text=Olena" 
       alt="Олена Ковальчук" 
       onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
  <span class="placeholder" style="display:none;">👩‍🦰</span>
</div>
```
**CSS:** `.master-photo { aspect-ratio: 1; overflow: hidden; background: var(--bg2); } .master-photo img { width: 100%; height: 100%; object-fit: cover; } .placeholder { font-size: 3rem; color: var(--gold)44; }`

### 5. Phone Links — Full Number in href (No Masking)
**Problem:** Masked display (`+380****4567`) breaks click-to-call on mobile.
**Fix:** Full number in `href`, formatted display in text:
```html
<a href="tel:+380441234567" class="nav-phone">📞 +38 (044) 123-45-67</a>
```

### 6. Mobile Nav Must Also Be Solid
**Fix:** `@media(max-width:768px)` nav gets `background: rgba(10,10,10,0.95)` immediately — no transparent mobile nav ever.

### 7. Preloader Immediate Dismissal
**Problem:** Preloader visible for ~100ms before JS dismisses it.
**Fix:** Inline script right after element — runs before paint:
```html
<div id="preloader"><div class="preloader-glow"></div></div>
<script>
  const p = document.getElementById('preloader');
  if (p) p.classList.add('loaded');
</script>
```

### 8. Privacy Scan — Required Before Deploy
```bash
python scripts/approval_policies.py docs/portfolio/beauty-salon/
# Must return: ✅ CLEAN — 0 violations
```

## Deployed Result
- **Live URL:** https://mcduck-s8.github.io/hermes-salon-landing/portfolio/beauty-salon/
- **Path:** `docs/portfolio/beauty-salon/index.html`
- **Nav:** Logo (gold + text-shadow), 5 center links, 2 action buttons (CTA + phone)
- **Hero:** 160px top padding, badge (Poznyaky), headline, subtext, 2 CTAs, 3 trust pills
- **Services:** 6 cards with icons, descriptions, prices (from 350₴)
- **Masters:** 4 cards with `<img>` + emoji fallback, name, spec, bio, portfolio link
- **Reviews:** 3 cards with stars, text, author avatar + name + context
- **Booking:** Form with service, master, date, time, name, phone
- **Contact:** Address, hours, phone, Telegram, contact form
- **Footer:** Logo, nav links, copyright

## Key Takeaways for Future Salon/Beauty Landings
1. **Niche palette:** Terracotta/Slate for barbershops, Teal/Coral for clinics — rotate per anti-slop-design
2. **Real data:** Pull addresses, phones, services from Yandex Maps/Instagram — not placeholders
3. **User-perspective first:** 4 questions before ANY artifact
4. **Privacy scan mandatory:** `approval_policies.py` catches Crimea/USDT/No KYC patterns
5. **Deploy to `docs/{category}/{offer}/index.html`** — GitHub Pages from docs folder