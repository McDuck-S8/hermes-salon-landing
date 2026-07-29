"""demo_generator.py — Generate demo landing pages for potential clients

Usage:
  python scripts/demo_generator.py "Salon Name" --category salon --instagram @salon_ig

Output: creates demo at demos/<slug>/index.html and deploys
"""

import argparse, json, os, re, sys
from datetime import datetime

TEMPLATES = {
    "salon": """<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta property="og:title" content="{name} — демо-версія">
<meta property="og:description" content="Сайт для {name} від Hermes Studio — сучасний дизайн, адаптивна верстка">
<meta property="og:image" content="{og_image}">
<meta property="og:url" content="{og_url}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<title>{name} — демо-версія сайту</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f8f8fa;color:#1a1a1a;line-height:1.5}}
.hero{{background:linear-gradient(135deg,#{accent1},{accent2});color:#fff;padding:60px 24px;text-align:center}}
.hero h1{{font-size:36px;font-weight:800;margin-bottom:8px;letter-spacing:-1px}}
.hero .sub{{font-size:18px;opacity:.85;margin-bottom:20px}}
.hero .btn{{display:inline-block;padding:14px 32px;background:#fff;color:#{accent1};border-radius:8px;font-weight:700;text-decoration:none;font-size:16px;transition:transform .15s}}
.hero .btn:hover{{transform:translateY(-2px)}}
.container{{max-width:1000px;margin:0 auto;padding:40px 24px}}
.section-title{{font-size:22px;font-weight:700;margin-bottom:20px;color:#{accent1}}}
.features{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px;margin-bottom:40px}}
.feature{{background:#fff;border-radius:12px;padding:20px;border:1px solid #eee}}
.feature h3{{font-size:16px;font-weight:600;margin-bottom:6px}}
.feature p{{font-size:14px;color:#666;line-height:1.5}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-bottom:40px}}
.gallery-item{{background:#eee;border-radius:8px;height:150px;display:flex;align-items:center;justify-content:center;color:#999;font-size:13px}}
.cta{{background:linear-gradient(135deg,#{accent1},{accent2});color:#fff;padding:50px 24px;text-align:center;border-radius:16px;margin:40px 24px}}
.cta h2{{font-size:24px;font-weight:700;margin-bottom:12px}}
.cta p{{font-size:15px;opacity:.9;margin-bottom:20px}}
.cta .btn{{display:inline-block;padding:14px 32px;background:#fff;color:#{accent1};border-radius:8px;font-weight:700;text-decoration:none}}
.footer{{text-align:center;padding:24px;color:#999;font-size:13px}}
@media(max-width:768px){{.hero h1{{font-size:28px}}}}
</style>
</head>
<body>
<section class="hero">
<h1>{name}</h1>
<p class="sub">{tagline}</p>
<a class="btn" href="#contact">✎ Записатись онлайн</a>
</section>
<div class="container">
<h2 class="section-title">Наші послуги</h2>
<div class="features">
{services_html}
</div>
<h2 class="section-title">Галерея</h2>
<div class="gallery">
<div class="gallery-item">📸 Фото 1</div>
<div class="gallery-item">📸 Фото 2</div>
<div class="gallery-item">📸 Фото 3</div>
<div class="gallery-item">📸 Фото 4</div>
</div>
</div>
<section id="contact" class="cta">
<h2>Запишіться сьогодні</h2>
<p>{cta_text}</p>
<a class="btn" href="https://instagram.com/{instagram_slug}">✎ Написати в Instagram</a>
</section>
<div class="footer">
{name} &middot; Демо-версія від Hermes Studio &middot; {year}
</div>
</body>
</html>""",
    "medical": """<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta property="og:title" content="{name} — демо-версія">
<meta property="og:description" content="Сайт для {name} від Hermes Studio — сучасний дизайн, адаптивна верстка">
<meta property="og:image" content="{og_image}">
<meta property="og:url" content="{og_url}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<title>{name} — демо-версія сайту</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f8f8fa;color:#1a1a1a;line-height:1.5}}
.hero{{background:linear-gradient(135deg,#{accent1},{accent2});color:#fff;padding:60px 24px;text-align:center}}
.hero h1{{font-size:36px;font-weight:800;margin-bottom:8px;letter-spacing:-1px}}
.hero .sub{{font-size:18px;opacity:.85;margin-bottom:20px}}
.hero .btn{{display:inline-block;padding:14px 32px;background:#fff;color:#{accent1};border-radius:8px;font-weight:700;text-decoration:none;font-size:16px;transition:transform .15s}}
.hero .btn:hover{{transform:translateY(-2px)}}
.container{{max-width:1000px;margin:0 auto;padding:40px 24px}}
.section-title{{font-size:22px;font-weight:700;margin-bottom:20px;color:#{accent1}}}
.features{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;margin-bottom:40px}}
.feature{{background:#fff;border-radius:12px;padding:20px;border:1px solid #eee}}
.feature h3{{font-size:16px;font-weight:600;margin-bottom:6px}}
.feature p{{font-size:14px;color:#666;line-height:1.5}}
.doctors{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px;margin-bottom:40px}}
.doctor-card{{background:#fff;border-radius:12px;padding:20px;text-align:center;border:1px solid #eee}}
.doctor-card .avatar{{width:80px;height:80px;border-radius:50%;background:#eee;margin:0 auto 12px;display:flex;align-items:center;justify-content:center;color:#999;font-size:24px}}
.doctor-card h3{{font-size:15px;font-weight:600}}
.doctor-card p{{font-size:13px;color:#666}}
.cta{{background:linear-gradient(135deg,#{accent1},{accent2});color:#fff;padding:50px 24px;text-align:center;border-radius:16px;margin:40px 24px}}
.cta h2{{font-size:24px;font-weight:700;margin-bottom:12px}}
.cta p{{font-size:15px;opacity:.9;margin-bottom:20px}}
.cta .btn{{display:inline-block;padding:14px 32px;background:#fff;color:#{accent1};border-radius:8px;font-weight:700;text-decoration:none}}
.footer{{text-align:center;padding:24px;color:#999;font-size:13px}}
@media(max-width:768px){{.hero h1{{font-size:28px}}}}
</style>
</head>
<body>
<section class="hero">
<h1>{name}</h1>
<p class="sub">{tagline}</p>
<a class="btn" href="#contact">✎ Записатись на прийом</a>
</section>
<div class="container">
<h2 class="section-title">Медичні послуги</h2>
<div class="features">
{services_html}
</div>
<h2 class="section-title">Наші лікарі</h2>
<div class="doctors">
<div class="doctor-card"><div class="avatar">👨‍⚕️</div><h3>Лікар-терапевт</h3><p>Стаж 15 років</p></div>
<div class="doctor-card"><div class="avatar">👩‍⚕️</div><h3>Лікар-педіатр</h3><p>Стаж 12 років</p></div>
<div class="doctor-card"><div class="avatar">👨‍⚕️</div><h3>Лікар-кардіолог</h3><p>Стаж 20 років</p></div>
</div>
</div>
<section id="contact" class="cta">
<h2>Запишіться на прийом</h2>
<p>{cta_text}</p>
<a class="btn" href="https://instagram.com/{instagram_slug}">✎ Написати в Instagram</a>
</section>
<div class="footer">
{name} &middot; Демо-версія від Hermes Studio &middot; {year}
</div>
</body>
</html>""",
    "cafe": """<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta property="og:title" content="{name} — демо-версія">
<meta property="og:description" content="Сайт для {name} від Hermes Studio — сучасний дизайн, адаптивна верстка">
<meta property="og:image" content="{og_image}">
<meta property="og:url" content="{og_url}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<title>{name} — демо-версія сайту</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f8f8fa;color:#1a1a1a;line-height:1.5}}
.hero{{background:linear-gradient(135deg,#{accent1},{accent2});color:#fff;padding:60px 24px;text-align:center}}
.hero h1{{font-size:36px;font-weight:800;margin-bottom:8px;letter-spacing:-1px}}
.hero .sub{{font-size:18px;opacity:.85;margin-bottom:20px}}
.hero .btn{{display:inline-block;padding:14px 32px;background:#fff;color:#{accent1};border-radius:8px;font-weight:700;text-decoration:none;font-size:16px}}
.container{{max-width:1000px;margin:0 auto;padding:40px 24px}}
.section-title{{font-size:22px;font-weight:700;margin-bottom:20px;color:#{accent1}}}
.features{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;margin-bottom:40px}}
.feature{{background:#fff;border-radius:12px;padding:20px;border:1px solid #eee}}
.feature h3{{font-size:16px;font-weight:600;margin-bottom:6px}}
.feature p{{font-size:14px;color:#666;line-height:1.5}}
.menu{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-bottom:40px}}
.menu-item{{background:#fff;border-radius:8px;padding:16px;border:1px solid #eee;text-align:center}}
.menu-item .icon{{font-size:32px;margin-bottom:8px}}
.menu-item h3{{font-size:14px;font-weight:600}}
.menu-item .price{{color:#{accent1};font-weight:700;font-size:14px}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-bottom:40px}}
.gallery-item{{background:#eee;border-radius:8px;height:150px;display:flex;align-items:center;justify-content:center;color:#999;font-size:13px}}
.cta{{background:linear-gradient(135deg,#{accent1},{accent2});color:#fff;padding:50px 24px;text-align:center;border-radius:16px;margin:40px 24px}}
.cta h2{{font-size:24px;font-weight:700;margin-bottom:12px}}
.cta p{{font-size:15px;opacity:.9;margin-bottom:20px}}
.cta .btn{{display:inline-block;padding:14px 32px;background:#fff;color:#{accent1};border-radius:8px;font-weight:700;text-decoration:none}}
.footer{{text-align:center;padding:24px;color:#999;font-size:13px}}
@media(max-width:768px){{.hero h1{{font-size:28px}}}}
</style>
</head>
<body>
<section class="hero">
<h1>{name}</h1>
<p class="sub">{tagline}</p>
<a class="btn" href="#contact">✎ Забронювати стіл</a>
</section>
<div class="container">
<h2 class="section-title">Меню</h2>
<div class="menu">
<div class="menu-item"><div class="icon">☕</div><h3>Кава</h3><p class="price">від 45₴</p></div>
<div class="menu-item"><div class="icon">🥐</div><h3>Випічка</h3><p class="price">від 35₴</p></div>
<div class="menu-item"><div class="icon">🥗</div><h3>Салати</h3><p class="price">від 85₴</p></div>
<div class="menu-item"><div class="icon">🍝</div><h3>Гарячі страви</h3><p class="price">від 120₴</p></div>
</div>
<h2 class="section-title">Про нас</h2>
<div class="features">
{services_html}
</div>
<h2 class="section-title">Галерея</h2>
<div class="gallery">
<div class="gallery-item">📸 Інтер'єр</div>
<div class="gallery-item">📸 Страви</div>
<div class="gallery-item">📸 Атмосфера</div>
</div>
</div>
<section id="contact" class="cta">
<h2>Забронюйте стіл</h2>
<p>{cta_text}</p>
<a class="btn" href="https://instagram.com/{instagram_slug}">✎ Написати в Instagram</a>
</section>
<div class="footer">
{name} &middot; Демо-версія від Hermes Studio &middot; {year}
</div>
</body>
</html>""",
}

DEFAULT_SERVICES = {
    "salon": [
        ("💇‍♀️ Стрижки та укладки", "Професійні стрижки, укладки, догляд за волоссям"),
        ("🎨 Фарбування", "Омбрі, балаяж, мелірування, тонування"),
        ("💅 Манікюр та педикюр", "Класичний, апаратний, гель-лак, дизайн нігтів"),
        ("✨ Догляд за обличчям", "Чистка, маски, пілінг, масаж обличчя"),
    ],
    "medical": [
        ("👨‍⚕️ Консультація лікаря", "Терапевт, педіатр, кардіолог — попередній запис"),
        ("🩸 Аналізи", "Загальні та біохімічні аналізи крові, сечі"),
        ("💉 Вакцинація", "Планові щеплення за календарем та індивідуальні схеми"),
        ("🏥 Денний стаціонар", "Крапельниці, уколи, процедури під наглядом лікаря"),
    ],
    "cafe": [
        ("☕ Напої", "Кава, чай, смузі, лимонади — 20+ позицій"),
        ("🥐 Сніданки", "З 8:00 до 12:00 — круасани, тости, яєчня"),
        ("🍝 Обіди", "Бізнес-ланчі з 12:00 до 16:00"),
    ],
}

def slugify(name):
    # Simple transliteration for Cyrillic
    tr = {
        'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e',
        'ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m',
        'н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u',
        'ф':'f','х':'kh','ц':'ts','ч':'ch','ш':'sh','щ':'shch',
        'ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya',
        'і':'i','ї':'yi','є':'ye','ґ':'g',
    }
    s = name.lower()
    for cyr, lat in tr.items():
        s = s.replace(cyr, lat)
    s = re.sub(r"[^a-z0-9-]", "", s.replace(" ", "-"))
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:30]

def generate_demo(name, category="salon", instagram="", tagline="", 
                  accent1="6c5ce7", accent2="a29bfe", cta_text=""):
    slug = slugify(name)
    
    if category in DEFAULT_SERVICES:
        services = DEFAULT_SERVICES[category]
    else:
        services = DEFAULT_SERVICES["salon"]
    
    services_html = "\n".join(
        f'<div class="feature"><h3>{s[0]}</h3><p>{s[1]}</p></div>'
        for s in services
    )
    
    if not tagline:
        tagline = "Ваш ідеальний образ починається тут"
    if not cta_text:
        cta_text = "Запишіться онлайн або в Instagram — ми чекаємо на вас!"
    
    instagram_slug = instagram.replace("@", "").strip()
    
    html = TEMPLATES[category].format(
        name=name,
        tagline=tagline,
        services_html=services_html,
        accent1=accent1,
        accent2=accent2,
        cta_text=cta_text,
        instagram_slug=instagram_slug,
        year=datetime.now().year,
        og_url=f"https://mcduck-s8.github.io/hermes-salon-landing/demos/{slug}/",
        og_image="https://mcduck-s8.github.io/hermes-salon-landing/studio-preview.jpg",
    )
    
    return slug, html

def main():
    parser = argparse.ArgumentParser(description="Generate demo landing page")
    parser.add_argument("name", help="Business name")
    parser.add_argument("--category", default="salon", help="Business category")
    parser.add_argument("--instagram", default="", help="Instagram handle")
    parser.add_argument("--tagline", default="", help="Tagline for hero")
    parser.add_argument("--accent1", default="6c5ce7", help="Primary accent color")
    parser.add_argument("--accent2", default="a29bfe", help="Secondary accent color")
    
    args = parser.parse_args()
    slug, html = generate_demo(
        args.name, args.category, args.instagram, 
        args.tagline, args.accent1, args.accent2
    )
    
    out_dir = f"docs/demos/{slug}"
    os.makedirs(out_dir, exist_ok=True)
    out_path = f"{out_dir}/index.html"
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(json.dumps({
        "slug": slug,
        "path": out_path,
        "url": f"https://mcduck-s8.github.io/hermes-salon-landing/demos/{slug}/",
        "name": args.name,
    }, ensure_ascii=False))

if __name__ == "__main__":
    main()
