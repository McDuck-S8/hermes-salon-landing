# Price Accordion Pattern

Collapse/expand price categories by clicking the heading. Reduces scrolling on long price lists.

## Markup (before JS runs)

```html
<div class="price-block">
  <h3>💇‍♀️ Перукарський зал</h3>
  <div class="price-item">...</div>
  <div class="price-item">...</div>
</div>
```

## JS (on page load — wraps h3 siblings into `.price-content` + adds `collapsed`)

```js
document.querySelectorAll('.price-block').forEach(function(block) {
  const items = [];
  let child = block.querySelector('h3').nextElementSibling;
  while (child) {
    const next = child.nextElementSibling;
    items.push(child);
    child = next;
  }
  const wrap = document.createElement('div');
  wrap.className = 'price-content';
  items.forEach(function(el) { wrap.appendChild(el); });
  block.appendChild(wrap);
  block.classList.add('collapsed');
});
```

## Click handler — basic (single block toggle)

```js
document.querySelector('.price-grid')?.addEventListener('click', function(e) {
  const h3 = e.target.closest('.price-block h3');
  if (!h3) return;
  h3.parentElement.classList.toggle('collapsed');
});
```

## CSS

```css
.price-block h3{cursor:pointer;user-select:none;position:relative;padding-right:28px}
.price-block h3::after{content:'+';position:absolute;right:8px;top:0;font-size:1.2rem;font-weight:400;transition:transform .25s}
.price-block:not(.collapsed) h3::after{content:'+';transform:rotate(45deg)} /* + → × */
.price-content{overflow:hidden;transition:max-height 0.35s ease,opacity 0.3s ease;max-height:5000px;opacity:1}
.price-block.collapsed .price-content{max-height:0;opacity:0}
```

**Prefer `::after` with `rotate(45deg)` over `::before` content swap** (`'+'` → `'−'`). The rotation animation is smoother than a hard content swap. The `+` at rest becomes `×` when rotated 45°.

## Key details

- **JS runs AFTER DOM ready** — at bottom of `<script>` or in `DOMContentLoaded`
- **`max-height: 5000px`** — must be larger than any price block's natural height. If a block has 25+ items, increase it
- **`max-height` animation** — CSS cannot animate `max-height` to `auto`. Using a generous fixed value (5000px) gives a smooth transition
- **`opacity` also transitions** — prevents visual flicker while max-height animates
- **`overflow:hidden`** — clips content during collapse
- **Event delegation on `.price-grid`** — works even if `.price-block` elements change
- **All blocks start collapsed** — `block.classList.add('collapsed')` on init

## Variant: Keep first block expanded

```js
blocks.forEach(function(block, i) {
  // ... wrap content ...
  if (i > 0) block.classList.add('collapsed');
});
```

## Variant: Paired-block sync in 2-column grids

When the price grid uses `grid-template-columns: 1fr 1fr`, blocks flow left→right in pairs (0,1), (2,3), (4,5) etc. Clicking one should toggle BOTH so the user doesn't see an empty column.

```js
(function initPriceAccordion() {
  var blocks = document.querySelectorAll('.price-block');

  // Wrap content as above
  blocks.forEach(function(block) {
    var items = [];
    var child = block.querySelector('h3').nextElementSibling;
    while (child) {
      var next = child.nextElementSibling;
      items.push(child);
      child = next;
    }
    if (items.length) {
      var wrap = document.createElement('div');
      wrap.className = 'price-content';
      items.forEach(function(el) { wrap.appendChild(el); });
      block.appendChild(wrap);
    }
  });

  function openHash() {
    var id = window.location.hash;
    if (!id) return;
    var target = document.querySelector(id);
    if (!target) return;
    target.classList.remove('collapsed');
    var idx = Array.prototype.indexOf.call(blocks, target);
    if (idx >= 0) {
      var partner = idx % 2 === 0 ? blocks[idx + 1] : blocks[idx - 1];
      if (partner) partner.classList.remove('collapsed');
    }
    setTimeout(function() { target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 100);
  }

  var grid = document.querySelector('.price-grid');
  grid.addEventListener('click', function(e) {
    var h3 = e.target.closest('.price-block h3');
    if (!h3) return;

    if (window.innerWidth <= 768) {
      // Mobile (1 column) — toggle single block
      h3.parentElement.classList.toggle('collapsed');
      return;
    }

    // Desktop (2 column) — toggle both in pair
    var block = h3.parentElement;
    var idx = Array.prototype.indexOf.call(blocks, block);
    if (idx < 0) return;
    var isCollapsing = !block.classList.contains('collapsed');
    block.classList.toggle('collapsed');
    var partnerIdx = idx % 2 === 0 ? idx + 1 : idx - 1;
    var partner = blocks[partnerIdx];
    if (partner) {
      if (isCollapsing) partner.classList.add('collapsed');
      else partner.classList.remove('collapsed');
    }
  });

  blocks.forEach(function(b) { b.classList.add('collapsed'); });
  openHash();
  window.addEventListener('hashchange', openHash);
})();
```

### How pairing works

| Grid index | Column 1 (even) | Column 2 (odd) |
|-----------|----------------|----------------|
| 0, 1 | Перукарський зал | Укладки та зачіски |
| 2, 3 | Фарбування волосся | Техніки фарбування |
| 4, 5 | Мелірування / Блонд | Догляд за волоссям |
| 6, 7 | Манікюр | Педикюр |
| 8, 9 | Масаж | Татуаж, ламінування |

`partnerIdx = idx % 2 === 0 ? idx + 1 : idx - 1`

This relies on price blocks being in DOM order matching grid flow. If blocks are reordered, the pair logic breaks.

### Mobile vs desktop behavior

- **Desktop (>768px)**: both paired blocks toggle — the `+` indicator rotates on both
- **Mobile (≤768px)**: only the clicked block toggles (single-column grid, no pair concept)
- Check `window.innerWidth` at click time, NOT at page load — resizing between portrait/landscape should re-evaluate

### Hash-based auto-open (footer/sidebar navigation)

Add `id` attributes to each `.price-block`:

```html
<div class="price-block" id="price-haircut">...</div>
<div class="price-block" id="price-color">...</div>
```

Then link from footer:

```html
<a href="#price-haircut">Стрижки</a>
<a href="#price-color">Фарбування</a>
```

The `openHash()` function above:
1. Reads `window.location.hash`
2. Finds the matching `.price-block` by `id`
3. Removes `.collapsed` on it AND its partner
4. Scrolls to it after 100ms (let the browser settle)
5. Listens for `hashchange` to handle in-page clicks

### CSS for the `+` indicator (paired sync variant)

```css
.price-block h3{cursor:pointer;position:relative;padding-right:32px;user-select:none}
.price-block h3::after{content:'+';position:absolute;right:8px;top:0;font-size:1.2rem;font-weight:400;color:var(--terracotta);transition:transform .25s;line-height:1.4}
.price-block:not(.collapsed) h3::after{transform:rotate(45deg);color:var(--terracotta-dark)}
.price-content{overflow:hidden;transition:max-height .3s ease}
.price-block.collapsed .price-content{display:none}
```

Using `display:none` (not `max-height:0`) for the collapsed state simplifies the CSS — no need for a magic `5000px` number. The trade-off: no smooth _collapse_ animation (the content disappears instantly). Use `max-height` animation when a folding effect matters; use `display:none` when simplicity matters more.

## Pitfalls

- **`#price` hash is NOT a price-block ID**: if the page has `<section id="price">`, linking `#price` captures the section, not a specific block. Use `#price-haircut` granular IDs for footer links.
- **Partner index assumes 10 blocks in 2-col grid**: if the grid has an odd number of blocks, the last block's partner will be `undefined`. Guard with `if (partner)`.
- **`window.innerWidth` at click time**, not on load: a user may rotate their phone or resize the window after page load.
- **Footer link must match the price-block ID exactly**: `href="#price-haircut"` matches `id="price-haircut"`. No prefix, no extra hash.
- **`scrollIntoView` may overscroll with sticky header**: if the header is `position:fixed`, add `scroll-margin-top: 80px` to the target element or use `scrollIntoView({block:'start'})`.
