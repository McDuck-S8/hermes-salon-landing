# Social Preview & Icon Fixes for Salon Landing Pages

## Problem

After deploying a salon landing page on GitHub Pages, the user reported:

1. **Social preview (snippet)** showed `mcduck-s8.github.io` as the title — no OG tags, so GitHub Pages defaulted to the raw domain
2. **Footer icons** used generic emojis (📷✈️💬) instead of branded SVG icons for Instagram, Telegram, Viber

## Fix: OG Meta Tags

Add to `<head>` after `<meta name="description">`:

```html
<meta property="og:title" content="Название салона — описание">
<meta property="og:description" content="Короткое привлекательное описание, 50-160 символов">
<meta property="og:image" content="URL фото для превью (1200×630 рекомендуется)">
<meta property="og:url" content="https://yourdomain.com/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Название салона">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="URL того же фото">
```

### OG Image Selection

**PRIORITY 1: Use the salon's LOGO, NOT a stock photo.** Users consistently reject Pexels/stock images — they want their brand visible in link previews. "должно быть их логотип" is a common complaint.

- First, check if the salon has an **existing website** — extract the logo from there (see "How to extract logo from old Wix site" below)
- Only if no existing branding exists, use a gallery photo (interior or service shot)
- **NEVER use a Pexels/Unsplash stock photo as OG image** — it doesn't represent the brand and users will complain
- **Host OG images locally, NOT on Pexels CDN** (crawlers block Pexels URLs)

**Aspect ratio: CRITICAL — 1.91:1 landscape (1200×627).** Telegram and most social platforms require landscape. Portrait/square images (e.g. 1200×1800) will NOT render in link previews, even if the URL is accessible.

- If the logo is square/portrait, create a proper OG canvas: 1200×627 with the salon's brand color background, logo centered at ~280px max dimension
- Tool: Python PIL (`Image.new("RGB", (1200, 627), brand_dark_color)`, paste resized logo centered)
- JPEG quality 85, keep under 300KB

**Hosting:**
- Download: use Python/curl to fetch the logo into the repo
- Path: `<project-dir>/og-image.jpg` (commit to GH Pages source)
- URL: `https://{owner}.github.io/{repo}/{project}/og-image.jpg`
- Update BOTH `og:image` and `twitter:image` to the local URL
- With `og:site_name` and proper `og:title`, the preview no longer shows the raw GitHub Pages URL as the primary text

#### How to Extract Logo from Old Wix Site

When the salon has an existing Wix site (e.g. `salonfargo.com`), the logo is hosted on Wix's CDN:

1. Extract the page content via `web_extract` or `browser_navigate`
2. Find the logo `<img>` tag — Wix URLs look like:
   `https://static.wixstatic.com/media/{hash}~mv2.jpg`
3. Download via **curl** in terminal (Python requests may fail with SSL errors on Wix CDN):
   ```bash
   curl -sL -o /tmp/logo.jpg "https://static.wixstatic.com/media/{hash}~mv2.jpg" -w "HTTP %{http_code}, size %{size_download}\\n"
   ```
4. Python requests with Wix CDN often gives `SSLError(SSLEOFError)` — always fall back to curl
5. **CRITICAL: Check image content, not just size.** Wix CDN may return a 1254×1254 near-black placeholder square with no visible logo:
   ```python
   from PIL import Image
   from collections import Counter
   img = Image.open("/tmp/logo.jpg")
   print(f"Size: {img.size}")
   # Sample pixels to detect dark placeholder
   pixels = list(img.getdata())[:5000]
   top_colors = Counter(pixels).most_common(5)
   for color, count in top_colors:
       print(f"  {color}: {count}")
   # If top colors are all near-black (RGB < 30), the image is a placeholder - do NOT use
   ```
6. If the logo is usable, create a 1200×627 OG canvas with branding background, center the logo:
   ```python
   canvas = Image.new("RGB", (1200, 627), (45, 45, 58))  # brand dark
   w, h = logo.size
   max_dim = 280
   nw = int(w * max_dim / max(w, h)) if w > max_dim or h > max_dim else w
   nh = int(h * max_dim / max(w, h)) if w > max_dim or h > max_dim else h
   logo_resized = logo.resize((nw, nh), Image.LANCZOS)
   x, y = (1200 - nw) // 2, (627 - nh) // 2
   canvas.paste(logo_resized, (x, y))
   canvas.save("og-image.jpg", quality=92)
   ```
7. **If logo is a dark placeholder (step 5), fall back to branded text card** (see section below)
8. Copy to both `demos/<project>/og-image.jpg` and `docs/<project>/og-image.jpg`

#### Branded Text Card OG Image (fallback when logo unavailable)

When the salon has no usable logo file (Wix placeholder, no image provided, format too strange), create a clean text-based branded card:

```python
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1200, 627
img = Image.new("RGB", (W, H), (45, 45, 58))  # brand dark background
draw = ImageDraw.Draw(img)

# Use serif font for elegance
font_paths = ["C:/Windows/Fonts/times.ttf", "C:/Windows/Fonts/georgia.ttf",
              "C:/Windows/Fonts/constan.ttf"]
title_font = ImageFont.truetype(font_paths[0], 80) if os.path.exists(font_paths[0]) else ImageFont.load_default()
sub_font = ImageFont.truetype(font_paths[0], 32) if os.path.exists(font_paths[0]) else ImageFont.load_default()
addr_font = ImageFont.truetype(font_paths[0], 18) if os.path.exists(font_paths[0]) else ImageFont.load_default()

# Decorative accent line at top (terracotta)
for i in range(5):
    y = 140 + i * 2
    draw.rectangle([(W//2 - 60 + i*2, y), (W//2 + 60 - i*2, y+1)], fill=(207, 117, 95))

# Salon name (large, centered, cream colored)
title = "Fargo."
tw = draw.textlength(title, font=title_font)
draw.text(((W - tw) // 2, 175), title, font=title_font, fill=(245, 240, 235))

# Tagline (terracotta)
sub = "салон краси"
sw = draw.textlength(sub, font=sub_font)
draw.text(((W - sw) // 2, 285), sub, font=sub_font, fill=(207, 117, 95))

# Address line at bottom
addr = "Address 1  ·  Address 2"
aw = draw.textlength(addr, font=addr_font)
draw.text(((W - aw) // 2, H - 80), addr, font=addr_font, fill=(160, 155, 150))

# Bottom accent line
for i in range(3):
    y = H - 55 + i * 2
    draw.rectangle([(W//2 - 40 + i*3, y), (W//2 + 40 - i*3, y+1)], fill=(207, 117, 95))

img.save("og-image.jpg", quality=92)
```

This produces a professional OG card with the salon's brand colors and identity, visible on any platform.

**Telegram caches old OG data for ~24 hours.** After updating OG tags:
- Test with: paste the URL in Telegram search (empty chat), wait for preview to load
- Or use `@WebpageBot` to clear cache (type the URL there)
- Or append `?v=2` to the og:image URL to force re-fetch
- No immediate way to clear Telegram's link preview cache programmatically

#### Double-Check Before Deployment

```bash
# Verify image is accessible
curl -sI "https://{owner}.github.io/{repo}/{project}/og-image.jpg" | head -10
# Expect: HTTP/2 200, content-type: image/jpeg, content-length > 20KB

# Verify aspect ratio
python3 -c "from PIL import Image; img=Image.open('og-image.jpg'); print(f'{img.size[0]}×{img.size[1]}, ratio={img.size[0]/img.size[1]:.2f}')"
# Expect: 1200×627, ratio=1.91
```

### Instagram — Collecting Gallery Images from Their Profile

## Fix: SVG Social Icons in Footer

### CSS for icon container (in footer-section CSS):

```css
.footer-social svg{width:18px;height:18px}
```

### HTML — inline SVGs for each platform:

**Instagram** (camera outline):
```html
<a href="https://www.instagram.com/..." target="_blank" aria-label="Instagram">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <rect x="2" y="2" width="20" height="20" rx="5"/>
    <circle cx="12" cy="12" r="5"/>
    <circle cx="17.5" cy="6.5" r="1.5"/>
  </svg>
</a>
```

**Telegram** (paper plane):
```html
<a href="https://t.me/..." target="_blank" aria-label="Telegram">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M22 2L11 13"/>
    <path d="M22 2L15 22L11 13L2 9L22 2Z"/>
  </svg>
</a>
```

**Viber** (phone with waves):
```html
<a href="viber://chat?number=%2B380..." aria-label="Viber">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
  </svg>
</a>
```

### Hover behavior

The `stroke="currentColor"` in SVGs means icons inherit the parent's `color`. With CSS:
```css
.footer-social a:hover{background:var(--terracotta);color:var(--white)}
```
the icon stroke turns white on hover automatically. No extra styling needed.

## Dual Deploy Check

When a landing page exists in both `demos/` (development) and `docs/` (GH Pages source), both copies must be updated. Use `patch` or `write_file` on both paths:
- `demos/<project>/index.html`
- `docs/<project>/index.html`
