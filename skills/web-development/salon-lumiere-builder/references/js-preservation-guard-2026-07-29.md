# JS-Preservation Guard — Full-File Rewrite Protocol

**Date:** 2026-07-29  
**Symptom:** Full rewrite of `index.html` (for design upgrade) dropped the carousel JavaScript — `initCarousel()`, `moveSlide()`, `goToSlide()` functions were missing. HTML `onclick` handlers referenced undefined functions. Site appeared broken.

**Root Cause:** Replacing the entire `<style>` and `<script>` sections without cross-referencing `onclick` handlers against defined functions.

## Protocol (MANDATORY before every full-file rewrite)

### Step 1: Extract all `onclick` function names from the OLD file

```bash
grep -oP 'onclick="\K[^"]+' old.html | sed 's/([^)]*)//g' | sort -u
```

### Step 2: Extract all function definitions and assignments in the NEW file

```bash
# Named functions
grep -oP 'function \K\w+' new.html | sort -u

# Window assignments (e.g. window['moveSlide'] = ...)
grep -oP "window\['?\K\w+'?" new.html | sed "s/'//g" | sort -u
```

### Step 3: Compare

Every function from Step 1 MUST appear in Step 2. If any are missing, add them to the script section.

### Step 4: Also check event listeners

```bash
# DOM element IDs referenced in JS
grep -oP "getElementById\('\K[^']+" new.html | sort -u
# HTML element IDs
grep -oP 'id="\K[^"]+' new.html | sort -u
```
Every ID referenced in JS must exist as an `id=""` attribute in HTML and vice versa.

## Why This Happens

When doing a full `write_file` rewrite:
- The old `<style>` gets bulk-replaced with new CSS
- The old `<script>` gets bulk-replaced with new JS
- **Nothing preserves old JS** unless explicitly checked

The carousel is particularly vulnerable because it's:
- A single-purpose component (easy to forget in a design rewrite)
- Referenced in HTML as `onclick="moveSlide(1)"` (no DOM event listener to grep)
- Has both `moveSlide` (global) referenced in HTML AND `initCarousel()` called at script end

## Fixed Carousel Architecture (copy-paste safe)

For a carousel with `trackId`, `dotsId`, and `visibleCount`:

```javascript
function initCarousel(trackId, dotsId, visibleCount) {
  var track = document.getElementById(trackId);
  var dotsEl = document.getElementById(dotsId);
  if (!track || track.children.length === 0) return;
  var slides = Array.from(track.children);
  var totalReal = slides.length;
  var step = visibleCount;

  // Clone for seamless loop
  for (var i = 0; i < step; i++){ track.appendChild(slides[i].cloneNode(true)); }
  for (var i = totalReal - 1; i >= totalReal - step; i--){ track.insertBefore(slides[i].cloneNode(true), track.firstChild); }

  var current = step;
  var slideWidth = 100 / visibleCount;
  track.style.transform = 'translateX(-' + (current * slideWidth) + '%)';

  // Generate dots
  if (dotsEl) {
    for (var i = 0; i < totalReal; i++) {
      var dot = document.createElement('button');
      dot.className = 'carousel-dot' + (i === 0 ? ' active' : '');
      dot.onclick = (function(n){ return function(){ goTo(n); }; })(i);
      dotsEl.appendChild(dot);
    }
  }

  function goTo(n) { /* navigate to slide n */ }
  function move(n) { /* move by n slides with seamless wrap */ }

  window['goToSlide'] = goTo;
  window['moveSlide'] = move;
}

initCarousel('carouselTrack', 'carouselDots', 3);
```

## Key: `window['moveSlide'] = move`

This makes `moveSlide` accessible to `onclick="moveSlide(1)"` in HTML. Without the `window[]` assignment, inline event handlers can't find the function.
