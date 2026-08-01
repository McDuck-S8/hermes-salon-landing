# OG Image Guide for Social Sharing

> Telegram/Facebook/Twitter link previews. Applies to every demo/landing site.

## Critical Requirement: Landscape Ratio

Telegram **rejects** portrait or square OG images. The link preview shows title + description but NO image when the crawler finds a non-compliant image.

| Platform | Required Ratio | Recommended Size |
|----------|---------------|------------------|
| Telegram | ≥ 1.91:1 landscape | 1200×627 |
| Facebook (og) | 1.91:1 | 1200×630 |
| Twitter (twitter:image) | 2:1 or 1.91:1 | 1200×600 or 1200×628 |

**Verify**: `python3 -c "from PIL import Image; img=Image.open('og-image.jpg'); print(f'{img.size[0]/img.size[1]:.2f}:1')"` — must show ≥ 1.87:1.

## What Image to Use

**RULE: Use the brand's actual logo, not a stock photo.**

- The brand's logo/profile picture (Instagram, Facebook) is the right OG image
- Generic Pexels/stock photos → the brand loses recognition in the Telegram preview
- User will immediately correct this: *"должно быть их логотип"*, *"не то пальто"*

### Option A: Logo from Instagram (preferred)

Instagram profile pics are on Instagram CDN (`scontent-*.cdninstagram.com`).

```html
<meta property="og:image" content="https://scontent-...cdninstagram.com/...">
```

**Troubleshooting**: Instagram CDN often **blocks** direct download from servers (Python `requests.get()` times out, `curl` returns exit code 35 SSL error). This is expected — the URL still works for Telegram's crawler. **Use the raw Instagram URL directly as og:image** — don't download-and-rehost.

### Option B: Generate a text-branded card

When no brand image is available, create a 1200×627 text card:

```python
from PIL import Image, ImageDraw, ImageFont
W, H = 1200, 627
img = Image.new("RGB", (W, H), (45, 45, 58))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("C:/Windows/Fonts/times.ttf", 80)
draw.text(((W - draw.textlength("Fargo.", font)) // 2, 175), "Fargo.",
          font=font, fill=(245, 240, 235))
sub_font = ImageFont.truetype("C:/Windows/Fonts/times.ttf", 32)
draw.text(((W - draw.textlength("салон краси", sub_font)) // 2, 275),
          "салон краси", font=sub_font, fill=(207, 117, 95))
img.save("og-image.jpg", quality=92)
```

### Option C: Old site's Wix logo

If the site was built on Wix, the logo may be at:
```
https://static.wixstatic.com/media/{UUID}~mv2.jpg
```
⚠️ Wix stores square logos (1254×1254 mostly). Placing a dark square logo on a dark canvas results in an **invisible image** — verify visibility before using.

## HTML Meta Tags (Required)

Both `og:image` AND `twitter:image` MUST be set:

```html
<meta property="og:image" content="https://...">
<meta name="twitter:image" content="https://...">
<meta name="twitter:card" content="summary_large_image">
```

## Telegram Cache

Telegram **caches** OG previews for ~24+ hours. Changing the image won't affect existing shares.

**To force-refresh:**
1. Send the link to `@WebpageBot` — it fetches fresh OG data
2. Add a cache-busting query param: `https://example.com/page?v=2`
3. Both methods work — Telegram treats the URL as new

## Full OG Tag Template

```html
<meta property="og:title" content="Fargo — салон краси на Позняках">
<meta property="og:description" content="Стрижки, фарбування, манікюр, педикюр, масаж, макіяж у салоні Fargo на Позняках. ✂️ Запис онлайн.">
<meta property="og:image" content="https://...">
<meta property="og:url" content="https://...">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Fargo Salon">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://...">
```

## Verification

After deploying, verify the live page:

```bash
curl -sL "https://live-url.com/page" | grep -E "og:image|twitter:image"
```

The URL should return 200:

```bash
curl -sI "https://...og-image.jpg" | head -3
# Must show: HTTP/2 200, content-type: image/jpeg
```
