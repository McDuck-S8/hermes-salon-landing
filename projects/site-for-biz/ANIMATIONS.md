# АНИМАЦИИ — Копилка из React Bits / Svelte Bits

Паттерны адаптированные под vanilla HTML/CSS/JS. Не требуют фреймворков.

---

## 1. ShinyText (блистающий sweep)

**Оригинал:** react-bits/ShinyText
**Использование:** `<span class="shiny-text">Текст</span>`

```css
.shiny-text {
    background-image: linear-gradient(
        120deg,
        var(--text-color, #fff) 0%,
        var(--text-color, #fff) 35%,
        #ffffff 50%,
        var(--text-color, #fff) 65%,
        var(--text-color, #fff) 100%
    );
    background-size: 200% auto;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shiny-sweep 3s linear infinite;
}
@keyframes shiny-sweep {
    to { background-position: -200% center; }
}
```

---

## 2. GradientText (анимированный градиент)

**Оригинал:** react-bits/GradientText
**Использование:** `<span class="gradient-text">Текст</span>`

```css
.gradient-text {
    background: linear-gradient(270deg, #f97316, #fb923c, #f59e0b, #f97316);
    background-size: 600% 600%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradient-shift 6s ease infinite;
}
@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
```

---

## 3. ScrollReveal (появление при скролле)

**Оригинал:** react-bits/ScrollReveal
**Использование:** `<div class="scroll-reveal">Секция</div>`

```css
.scroll-reveal {
    opacity: 0;
    transform: translateY(40px);
    transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1),
                transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
.scroll-reveal.visible {
    opacity: 1;
    transform: translateY(0);
}
.scroll-reveal.delay-1 { transition-delay: 0.1s; }
.scroll-reveal.delay-2 { transition-delay: 0.2s; }
.scroll-reveal.delay-3 { transition-delay: 0.3s; }
.scroll-reveal.delay-4 { transition-delay: 0.4s; }
```

```js
const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
        if (e.isIntersecting) {
            e.target.classList.add('visible');
            observer.unobserve(e.target);
        }
    });
}, { threshold: 0.15 });
document.querySelectorAll('.scroll-reveal').forEach(el => observer.observe(el));
```

---

## 4. BlurText (слова с блюром)

**Оригинал:** react-bits/BlurText
**Использование:** `<p class="blur-text">Каждое слово появляется</p>`

```css
.blur-word {
    display: inline-block;
    filter: blur(10px);
    opacity: 0;
    transform: translateY(15px);
    transition: filter 0.6s, opacity 0.6s, transform 0.6s;
    transition-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
}
.blur-text-active .blur-word {
    filter: blur(0);
    opacity: 1;
    transform: translateY(0);
}
```

```js
document.querySelectorAll('.blur-text').forEach(el => {
    const words = el.textContent.trim().split(' ');
    const delay = parseInt(el.dataset.delay || '120');
    el.innerHTML = words.map((w, i) =>
        `<span class="blur-word" style="transition-delay:${i * delay}ms">${w}</span>`
    ).join(' ');
    new IntersectionObserver(([e]) => {
        if (e.isIntersecting) { el.classList.add('blur-text-active'); }
    }, { threshold: 0.1 }).observe(el);
});
```

---

## 5. CountUp (счётчик чисел)

**Оригинал:** react-bits/CountUp
**Использование:** `<span class="count-up" data-target="885">0</span>`

```js
document.querySelectorAll('.count-up').forEach(el => {
    const target = parseInt(el.dataset.target);
    const duration = parseInt(el.dataset.duration || '2000');
    new IntersectionObserver(([e]) => {
        if (!e.isIntersecting) return;
        const start = performance.now();
        const animate = now => {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(target * eased);
            if (progress < 1) requestAnimationFrame(animate);
        };
        requestAnimationFrame(animate);
    }, { threshold: 0.1 }).observe(el);
});
```
