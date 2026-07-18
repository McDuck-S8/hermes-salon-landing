# Salon Landing: Pexels + Booking Date/Time Pattern

## Context
Session 2026-07-10: Built beauty salon landing page for Russian market.
User rejected: (1) picsum random photos, (2) placehold.co colored blocks, (3) form without date/time selectors.

## Image Source Resolution
| Source | Works in RU? | Context | Verdict |
|--------|-------------|---------|---------|
| Unsplash | ❌ times out | - | Blocked |
| Pexels | ✅ 200 | Beauty/salon/hair | ✅ Use |
| picsum.photos | ✅ loads | Random (nature, phones) | ❌ Irrelevant |
| placehold.co | ✅ loads | Colored blocks | ❌ User: "заглушки" |

## Pexels URLs Used
- Hero (salon interior): `7750114` → 800x900
- Service card (haircut): `3992875` → 400x400
- About (interior): `3736520` → 600x500
- Gallery: `8834077` (hair coloring), `3997997` (haircut), `5069605` (hairstyle), `4974566` (styling)
- Format: `https://images.pexels.com/photos/{ID}/pexels-photo-{ID}.jpeg?auto=compress&cs=tinysrgb&w={W}&h={H}&fit=crop`

## Booking Form Implementation
### Date Selector (30 days from today)
```js
const today = new Date();
for (let i = 0; i < 30; i++) {
  const d = new Date(today);
  d.setDate(today.getDate() + i);
  const opt = document.createElement('option');
  opt.value = d.toISOString().split('T')[0];
  opt.textContent = d.toLocaleDateString('ru-RU', {
    weekday: 'short', day: 'numeric', month: 'short'
  });
  dateSelect.appendChild(opt);
}
```

### Time Selector (populated on date change)
- Range: 09:00-20:30 every 30min
- Sunday: show "Воскресенье - выходной" disabled
- Occupied: show "slot (занято)" with disabled=true
- Pre-populated example: `const booked = ['10:00', '14:30', '18:00'];`

### Phone Mask (+7 Russia)
```js
phoneInput.addEventListener('input', function() {
  let v = this.value.replace(/\D/g, '');
  if (v.length > 0) {
    let f = '+7 (';
    if (v.length > 1) f += v.substring(1, 4); else { f += v.substring(1); this.value = f; return; }
    f += ') ';
    if (v.length > 4) f += v.substring(4, 7); else { f += v.substring(4); this.value = f; return; }
    f += '-';
    if (v.length > 7) f += v.substring(7, 9); else { f += v.substring(7); this.value = f; return; }
    f += '-';
    f += v.substring(9, 11);
    this.value = f;
  }
});
```

## Avatar Approach
Instead of external photo avatars for testimonials → CSS-only initial circles:
```css
.testimonial-avatar {
  width: 40px; height: 40px; border-radius: 100px;
  background: var(--accent); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font: 600 13px/1 var(--font-body);
}
```
HTML: `<div class="testimonial-avatar">ЕК</div>`

## Deployment
- GitHub Pages via `/docs` directory
- Branch: user/hermes-session-YYYY-MM-DD
- Live URL: https://{owner}.github.io/{repo}/
