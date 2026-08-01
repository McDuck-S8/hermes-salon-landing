---
name: form-handling
description: "Form handling for static sites — form backend services (Formspree, Web3Forms, Static Forms), spam protection, Telegram/email notifications, validation, file uploads. Load when adding ANY form to a page."
version: 1.0.0
tags: [forms, contact, static-site, lead-capture, spam-protection]
---

# Form Handling for Static Sites

## Form Backend Services

For static HTML/CSS sites with no backend, use a form processing service.

### Comparison

| Service | Free Tier | Paid | Spam | File Uploads | RU Access |
|---------|-----------|------|------|-------------|-----------|
| **Formspree** | 50/mo | $15/mo (1000) | Akismet + reCAPTCHA | Pro only | ✅ |
| **Web3Forms** | 250/mo | $12/mo (1000) | reCAPTCHA | $12/mo | ✅ |
| **Static Forms** | 500/mo | $9/mo (25000) | +AI Reply | Pro | ✅ |
| **FormSubmit** | ∞ | $0 | basic honeypot | ❌ | ✅ |
| **Formcarry** | 100/mo | $9/mo (500) | reCAPTCHA | ❌ | ✅ |
| **Basin** | 50/mo | $9/mo (2000) | honeypot + IP | ✅ | ✅ |

**Best free option:** Web3Forms (250/mo, no-fuss)
**Best paid:** Static Forms ($9/mo, 25k/mo, AI auto-reply)
**Best no-signup:** FormSubmit (unlimited, but no spam protection)

### Integration pattern (Web3Forms — simplest)

```html
<form action="https://api.web3forms.com/submit" method="POST">
  <input type="hidden" name="access_key" value="YOUR_KEY_HERE">

  <label for="name">Name</label>
  <input type="text" name="name" id="name" required>

  <label for="email">Email</label>
  <input type="email" name="email" id="email" required>

  <label for="message">Message</label>
  <textarea name="message" id="message" required></textarea>

  <!-- Honeypot (anti-spam, hidden from users) -->
  <input type="checkbox" name="botcheck" class="hidden" style="display:none">

  <button type="submit">Send</button>
</form>
```

## Spam Protection — Best Practices

### 1. Honeypot (hidden field)
```html
<!-- Invisible to users, bots auto-fill it -->
<input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">
```

### 2. Time-based (form filled too fast = bot)
```html
<input type="hidden" name="_timestamp" value="">
```
```javascript
document.querySelector('input[name="_timestamp"]').value = Date.now();
// Server: reject if age < 2 seconds
```

### 3. Turnstile (Cloudflare, privacy-first CAPTCHA)
```html
<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
<div class="cf-turnstile" data-sitekey="YOUR_SITE_KEY"></div>
```

### 4. Rate limiting on server (check service docs)

---

## Telegram Notification for Form Submissions

### Web3Forms + Telegram
```javascript
// Web3Forms webhook → your server → Telegram Bot API
fetch('https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    chat_id: '<CHAT_ID>',
    text: `New lead from ${name}: ${email}\n${message}`
  })
});
```

### Direct Telegram form (no backend)
```html
<form id="tgForm">
  <input type="text" name="name" required>
  <input type="tel" name="phone" required>
  <button type="submit">Send</button>
</form>
<script>
document.getElementById('tgForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const msg = Array.from(fd.entries()).map(([k,v]) => `${k}: ${v}`).join('\n');
  await fetch(`https://api.telegram.org/bot<TOKEN>/sendMessage`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ chat_id: '<CHAT_ID>', text: msg })
  });
});
</script>
```

⚠️ **Security:** Bot token is visible in client-side code. For production, proxy through Cloudflare Workers or use a form backend service.

### Better approach — Cloudflare Worker
```javascript
// workers.dev proxy
export default {
  async fetch(request) {
    if (request.method === 'POST') {
      const data = await request.formData();
      const text = [...data.entries()].map(([k,v]) => `${k}: ${v}`).join('\n');
      await fetch(`https://api.telegram.org/bot/${TG_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ chat_id: CHAT_ID, text })
      });
      return new Response('OK', { status: 200 });
    }
  }
}
```

### Cleaner — Cloudflare Workers + formbackend
```html
<form action="https://formbackend.example.workers.dev/lead" method="POST">
  <!-- ... fields ... -->
  <input type="hidden" name="_redirect" value="https://example.com/thanks.html">
  <button type="submit">Отправить</button>
</form>
```

### Test submission
```bash
curl -X POST https://formbackend.example.workers.dev/lead \
  -d "name=Test&phone=%2B79001234567&_redirect=https://example.com/thanks.html"
```

---

## Client-side Validation

```html
<form novalidate onsubmit="return validateForm(this)">
  <input type="email" id="email" required>
  <span class="error" id="emailError"></span>
  <button type="submit">Submit</button>
</form>

<script>
function validateForm(form) {
  let valid = true;
  const email = form.querySelector('#email');
  const err = form.querySelector('#emailError');
  
  if (!email.value.includes('@')) {
    err.textContent = 'Введите корректный email';
    email.classList.add('error');
    valid = false;
  } else {
    err.textContent = '';
    email.classList.remove('error');
  }
  
  return valid;
}
</script>
```

---

## Form UX Best Practices

- **Submit button text** — describe action, not label: "Send Message" ✓ vs "Submit" ✗
- **Loading state** — disable button + show spinner on submit
- **Success state** — green checkmark + "Message sent! We'll respond within 24h"
- **Error state** — inline errors per field, not alert() popup
- **No CAPTCHA for RU users** — Google reCAPTCHA blocked in Russia. Use Cloudflare Turnstile or honeypot
- **Phone input** — use `type="tel"` + `pattern="[\+\d\s\(\)-]+"` for RU format
- **Privacy checkbox** — "Я согласен на обработку персональных данных" (required by 152-ФЗ)
- **Focus management** — auto-focus first field, focus first error on validation fail

## Pitfalls
- Google reCAPTCHA blocked in Russia — use Cloudflare Turnstile instead
- Bot token in client-side JS is NOT secure — always proxy through server/worker
- Web3Forms access key in HTML is public — OK for forms, but don't use as your only spam defense
- FormSubmit has ZERO spam protection — expect spam within hours
- Formspree free tier (50/mo) is very limited — upgrade early if getting traffic
