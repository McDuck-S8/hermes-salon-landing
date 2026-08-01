# Карусель — 3 в ряд, нескінченне листування

## CSS

```css
.carousel{position:relative;overflow:hidden;border-radius:var(--radius);margin:0 -8px}
.carousel-track{display:flex;transition:transform 0.5s ease}
.carousel-slide{min-width:33.333%;padding:0 8px;position:relative;box-sizing:border-box}
.carousel-slide img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:var(--radius-sm)}
.carousel-label{position:absolute;bottom:8px;left:8px;right:8px;padding:12px;background:linear-gradient(0deg,rgba(0,0,0,.7),transparent);color:#fff;font-size:0.8rem;border-radius:0 0 var(--radius-sm) var(--radius-sm)}
.carousel-btn{position:absolute;top:50%;transform:translateY(-50%);z-index:2;width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,0.95);color:var(--dark);font-size:1.1rem;display:flex;align-items:center;justify-content:center;transition:0.3s;cursor:pointer;border:none;box-shadow:0 2px 8px rgba(0,0,0,0.1)}
.carousel-btn:hover{background:var(--white);box-shadow:0 4px 16px rgba(0,0,0,.15)}
.carousel-prev{left:4px}
.carousel-next{right:4px}
.carousel-dots{display:flex;justify-content:center;gap:6px;margin-top:12px}
.carousel-dot{width:8px;height:8px;border-radius:50%;background:var(--border);border:none;cursor:pointer;transition:0.3s;padding:0}
.carousel-dot.active{background:var(--teal);width:20px;border-radius:4px}
```

## HTML

```html
<div class="carousel">
  <div class="carousel-track" id="carouselTrack">
    <div class="carousel-slide"><img src="..." alt="..."><div class="carousel-label">...</div></div>
    <div class="carousel-slide"><img src="..." alt="..."><div class="carousel-label">...</div></div>
    <div class="carousel-slide"><img src="..." alt="..."><div class="carousel-label">...</div></div>
  </div>
  <button class="carousel-btn carousel-prev" onclick="moveSlide(-1)">‹</button>
  <button class="carousel-btn carousel-next" onclick="moveSlide(1)">›</button>
</div>
<div class="carousel-dots" id="carouselDots"></div>
```

## JS — ініціалізація

```javascript
function initCarousel(trackId, dotsId, visibleCount) {
  const track = document.getElementById(trackId);
  const dotsEl = document.getElementById(dotsId);
  if (!track) return;
  const slides = Array.from(track.children);
  if (slides.length === 0) return;
  const totalReal = slides.length;
  const step = visibleCount;

  // Clone for seamless loop
  for (let i = 0; i < step; i++) {
    const clone = slides[i].cloneNode(true);
    track.appendChild(clone);
  }
  for (let i = totalReal - 1; i >= totalReal - step; i--) {
    const clone = slides[i].cloneNode(true);
    track.insertBefore(clone, track.firstChild);
  }

  let current = step;
  const slideWidth = 100 / visibleCount;
  track.style.transform = 'translateX(-' + (current * slideWidth) + '%)';

  // Dots
  if (dotsEl) {
    for (let i = 0; i < totalReal; i++) {
      const dot = document.createElement('button');
      dot.className = 'carousel-dot' + (i === 0 ? ' active' : '');
      dot.onclick = () => goTo(i);
      dotsEl.appendChild(dot);
    }
  }

  function goTo(n) {
    const target = step + ((n % totalReal + totalReal) % totalReal);
    current = target;
    track.style.transition = 'transform 0.5s ease';
    track.style.transform = 'translateX(-' + (current * slideWidth) + '%)';
    if (dotsEl) {
      dotsEl.querySelectorAll('.carousel-dot').forEach((d, i) => d.classList.toggle('active', i === ((n % totalReal + totalReal) % totalReal)));
    }
    track.addEventListener('transitionend', function handler() {
      track.removeEventListener('transitionend', handler);
      if (current <= step - 1) {
        current = totalReal + step - 1;
        track.style.transition = 'none';
        track.style.transform = 'translateX(-' + (current * slideWidth) + '%)';
      } else if (current >= totalReal + step) {
        current = step;
        track.style.transition = 'none';
        track.style.transform = 'translateX(-' + (current * slideWidth) + '%)';
      }
    });
  }

  function move(n) {
    current += n;
    track.style.transition = 'transform 0.5s ease';
    track.style.transform = 'translateX(-' + (current * slideWidth) + '%)';
    if (dotsEl) {
      const realIdx = ((current - step) % totalReal + totalReal) % totalReal;
      dotsEl.querySelectorAll('.carousel-dot').forEach((d, i) => d.classList.toggle('active', i === realIdx));
    }
    track.addEventListener('transitionend', function handler() {
      track.removeEventListener('transitionend', handler);
      if (current <= step - 1) {
        current = totalReal + step - 1;
        track.style.transition = 'none';
        track.style.transform = 'translateX(-' + (current * slideWidth) + '%)';
      } else if (current >= totalReal + step) {
        current = step;
        track.style.transition = 'none';
        track.style.transform = 'translateX(-' + (current * slideWidth) + '%)';
      }
    });
  }

  if (trackId.includes('Review')) {
    window['goToReview'] = goTo;
    window['moveReview'] = move;
  } else {
    window['goToSlide'] = goTo;
    window['moveSlide'] = move;
  }
}

initCarousel('carouselTrack', 'carouselDots', 3);  // Photo carousel: 3 visible
initCarousel('reviewTrack', 'reviewDots', 2);      // Review carousel: 2 visible
```

## Ключові моменти

- **`min-width: 33.333%`** = 3 елементи в ряд. Для 2: `min-width: 50%`
- **cloneNode** копіює перші/останні слайди для безшовного переходу
- **transitionend** — момент, коли анімація закінчилась → перескок без transition
- **`transition: none`** на момент перескоку — щоб не було видно стрибка
- **dots** синхронізовані з реальним індексом (current - step) % totalReal
- Для review каруселі слайди мають `aspect-ratio:auto` (текст, а не фото)
