---
name: web-analytics
description: "Web analytics setup — Яндекс.Метрика, Google Analytics 4, сбор целей, e-commerce, события кликов, аналитика поведения. Load when deploying any production site."
version: 1.0.0
tags: [analytics, yandex-metrika, ga4, tracking, goals, conversion]
---

# Web Analytics

## Яндекс.Метрика (обязательно для RU сайтов)

### Установка (2026)
```html
<!-- Yandex.Metrika counter -->
<script type="text/javascript">
  (function(m,e,t,r,n,d,v){
    m[n]=m[n]||{};
    m[n].counterId='xxxxxxxxxx';
    m[n].callbacks={};
    m[n].callbacks.push(function(){
      var a=m.createElement(e);
      a.async=true;
      a.src=t+'/counter.js?id='+m[n].counterId;
      var b=m.getElementsByTagName(e)[0];
      b.parentNode.insertBefore(a,b);
    });
  })(window, document, 'https://mc.yandex.ru', 'https://mc.yandex.com', 'yaCounter');
</script>
<noscript>
  <div><img src="https://mc.yandex.ru/watch/xxxxxxxxxx" alt="" /></div>
</noscript>
<!-- End Yandex.Metrika counter -->
```

### Асинхронная загрузка (без блокировки)
```javascript
(function() {
  'use strict';
  var yaCounter = window.yaCounter || {};
  yaCounter.counterId = 'xxxxxxxxxx';
  yaCounter.callbacks = yaCounter.callbacks || [];
  yaCounter.callbacks.push(function() {
    var s = document.createElement('script');
    s.type = 'text/javascript';
    s.async = true;
    s.src = 'https://mc.yandex.ru/counter.js?id=' + yaCounter.counterId;
    var n = document.getElementsByTagName('script')[0];
    n.parentNode.insertBefore(s, n);
  });
})();
```

### Цели (goals)
```javascript
// Автоматическая цель — клик на телефон
yaCounter.reachGoal('phone_click');

// Цель с параметрами
yaCounter.reachGoal('form_submit', {
  form_name: 'contact',
  page_url: window.location.pathname
});

// Поручить цель после отправки формы
document.getElementById('contact-form').addEventListener('submit', function() {
  yaCounter.reachGoal('form_submit');
});
```

### Цели в интерфейсе
1. Администрирование → Цели → Добавить цель
2. Тип: "Посещение страниц" (для thank-you) или "Событие" (для кликов)
3. URL спасибо: `/thanks.html` или `event: form_submit`

### e-commerce
```javascript
// Отправка данных о покупке
yaCounter.reachGoal('purchase', {
  order_id: '12345',
  order_price: 15000,
  currency: 'RUB',
  goods: [
    { name: 'Услуга 1', price: 5000, quantity: 1 },
    { name: 'Услуга 2', price: 10000, quantity: 1 }
  ]
});
```

---

## Google Analytics 4 (GA4)

### Установка
```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID', {
    'page_title': document.title,
    'page_location': window.location.href
  });
</script>
```

### События
```javascript
// Кастомное событие
gtag('event', 'form_submit', {
  form_name: 'contact',
  method: 'telegram'
});

// Цена/конверсия
gtag('event', 'purchase', {
  transaction_id: '12345',
  value: 15000,
  currency: 'RUB',
  items: [{
    item_name: 'Услуга 1',
    price: 5000,
    quantity: 1
  }]
});
```

⚠️ **GA заблокирован в РФ** — используйте Яндекс.Метрику как основную. GA4 можно добавить для зарубежного трафика, но он не будет работать для RU пользователей.

---

## События и аналитика поведения

### Отслеживание кликов
```javascript
// Универсальный трекер кликов
document.addEventListener('click', function(e) {
  const target = e.target.closest('[data-track]');
  if (target) {
    const eventName = target.dataset.track;
    const eventData = target.dataset.trackData ? JSON.parse(target.dataset.trackData) : {};

    // Yandex
    if (typeof yaCounter !== 'undefined') {
      yaCounter.reachGoal(eventName, eventData);
    }

    // GA4
    if (typeof gtag !== 'undefined') {
      gtag('event', eventName, eventData);
    }
  }
});
```

```html
<!-- Использование -->
<button data-track="phone_click" data-track-data='{"position":"header"}'>
  Позвонить
</button>

<a href="tel:+79780000000" data-track="phone_call">
  +7 (978) 000-00-00
</a>
```

### Прокрутка до секции
```javascript
// Отслеживание просмотра секций
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const section = entry.target.dataset.section;
      if (typeof yaCounter !== 'undefined') {
        yaCounter.reachGoal('section_view', { section });
      }
      observer.unobserve(entry.target); // один раз
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('[data-section]').forEach(el => observer.observe(el));
```

### Аналитика форм
```javascript
// Отслеживание воронки формы
const form = document.getElementById('lead-form');
const steps = form.querySelectorAll('.form-step');

form.addEventListener('submit', function() {
  const completedSteps = Array.from(steps)
    .filter(s => s.classList.contains('completed'))
    .length;

  if (typeof yaCounter !== 'undefined') {
    yaCounter.reachGoal('form_complete', {
      steps_completed: completedSteps,
      total_steps: steps.length
    });
  }
});
```

---

## Интеграция с Telegram

### Автоматическая отправка целей в Telegram
```javascript
// При достижении цели отправляем в Telegram
function trackGoal(goalName, data = {}) {
  // Yandex.Metrika
  if (typeof yaCounter !== 'undefined') {
    yaCounter.reachGoal(goalName, data);
  }

  // Telegram (через ваш бот)
  fetch('https://api.telegram.org/bot<TOKEN>/sendMessage', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: '<CHAT_ID>',
      text: `🎯 Цель: ${goalName}\n${new URLSearchParams(data).toString()}`
    })
  });
}
```

---

## Проверка и отладка

### Тестовый режим
```javascript
// Debug mode — выводит все события в консоль
window.DEBUG_ANALYTICS = true;

function trackEvent(name, data) {
  if (window.DEBUG_ANALYTICS) {
    console.log('[Analytics]', name, data);
  }
  // ... реальная отправка
}
```

### Проверка установки
```bash
# Яндекс.Метрика
curl -I "https://mc.yandex.ru/counter.js?id=xxxxxxxxxx"

# Проверка в браузере
# Откройте DevTools → Network → отфильтруйте по "yandex" или "google-analytics"
```

### Инструменты
- **Яндекс.Вебвизор** — теперь встроен в Метрику (2.0), запись поведения
- **Google Search Console** — SEO-аналитика
- **PageSpeed Insights** — Core Web Vitals
- **Yandex.Metrika Webvisor 2.0** — теперь встроен в Метрику

## Pitfalls
- **GA4 заблокирован в РФ** — используйте Яндекс.Метрику как основную
- **Счетчики в footer** — лучше в `<head>` для более точного подсчёта
- **Не используйте `target="_blank"` без `rel="noopener"`** — утечка данных в аналитику
- **Дублирование целей** — не настраивайте одну цель дважды (Yandex + GA)
- **Локальная разработка** — отключайте счетчики на localhost
- **GDPR/152-ФЗ** — добавьте согласие на сбор аналитики (чекбокс)
- **Самоналожение целей** — `reachGoal` вызывается до загрузки счетчика → используйте `yaCounter.callbacks`
