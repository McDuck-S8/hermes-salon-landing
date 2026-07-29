from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1200, 627
img = Image.new('RGB', (W, H), (26, 26, 46))
draw = ImageDraw.Draw(img)

font_dir = 'C:/Windows/Fonts'
font_bold = ImageFont.truetype(os.path.join(font_dir, 'arialbd.ttf'), 72)
font_reg = ImageFont.truetype(os.path.join(font_dir, 'arial.ttf'), 32)
font_small = ImageFont.truetype(os.path.join(font_dir, 'arial.ttf'), 22)
font_price = ImageFont.truetype(os.path.join(font_dir, 'arialbd.ttf'), 28)

# Accent bar on right
for i in range(H):
    c = int(108 - (i / H) * 30)
    for x in range(W-6, W):
        img.putpixel((x, i), (c, max(92 - int(i/H*20), 60), 231))

# Decorative circles
draw.ellipse([-40, -40, 120, 120], fill=(108, 92, 231, 60))
draw.ellipse([W-160, H-160, W-40, H-40], fill=(108, 92, 231, 40))
draw.rectangle([60, 140, 200, 142], fill=(108, 92, 231))

# Title
draw.text((60, 170), "HERMES", fill=(232, 232, 238), font=font_bold)
draw.text((60, 250), "STUDIO", fill=(139, 124, 247), font=font_bold)

# Subtitle
draw.text((60, 350), "web development \u00b7 AI \u00b7 design", fill=(136, 136, 154), font=font_reg)

# Separator
draw.rectangle([60, 410, 260, 412], fill=(80, 80, 100))

# Tagline (English to avoid encoding issues)
draw.text((60, 440), "Websites for small business", fill=(200, 200, 210), font=font_small)
draw.text((60, 470), "Price list \u00b7 Online booking \u00b7 SEO \u00b7 Turnkey", fill=(160, 160, 170), font=font_small)

# Price
draw.text((60, 530), "from $300", fill=(108, 92, 231), font=font_price)

path = 'docs/studio-preview.jpg'
img.save(path, 'JPEG', quality=88)
print(f"Saved: {path} ({os.path.getsize(path)} bytes)")
