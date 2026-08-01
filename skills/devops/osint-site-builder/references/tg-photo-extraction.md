# Telegram Photo Extraction — BrowserClaw technique

**Використано:** 2026-07-22 для @alliccenncosmm

## Проблема
Telegram web (t.me) не використовує `<img>` фото постів. Фото — це CSS `background-image` на `<a>`. `querySelector('img')` нічого не знаходить.

## Рішення: embed сторінка

```javascript
// На t.me/channel/POST_ID?embed=1:
const imgs = Array.from(document.querySelectorAll('a[style*="background"]'));
return imgs.map(a => {
  const bg = a.style.backgroundImage;
  const match = bg.match(/url\(["']?([^"')]+)["']?\)/);
  return match ? match[1] : bg;
});
```

Повертає масив full-size JPG URL з `cdn4.telesco.pe`.

## Завантаження

```python
import urllib.request
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=20)
with open('assets/photo.jpg', 'wb') as f:
    f.write(resp.read())
```

User-Agent обов'язковий — без нього Telegram CDN віддає 403.

## Відомі помилки
- Деякі JPG URL з Telegram CDN повертають 404. Пробувати інший пост.
- WebP тумбнейли (маленькі) — ігнорувати, шукати JPG (>40KB).
- На одному пості може бути кілька фото (album) — кожне має свій `a[style*="background"]`.
