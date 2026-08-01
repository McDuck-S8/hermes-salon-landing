"""
Demo Builder Module - Generate landing pages for different niches
Templates: salon, restaurant, hotel, auto_service, clinic
Languages: ru, en, sr (Serbian), hr (Croatian)
Deploy: GitHub Pages
"""

import os, json, time, uuid, subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional


# ============================================================
# NICHE TEMPLATES
# ============================================================

NICHES = {
    "salon": {
        "name": "Салон красоты",
        "name_en": "Beauty Salon", 
        "name_sr": "Salon lepote",
        "sections": ["hero", "services", "gallery", "about", "reviews", "contact", "map"],
    },
    "restaurant": {
        "name": "Ресторан",
        "name_en": "Restaurant",
        "name_sr": "Restoran",
        "sections": ["hero", "menu", "gallery", "about", "reviews", "contact", "map"],
    },
    "hotel": {
        "name": "Отель",
        "name_en": "Hotel",
        "name_sr": "Hotel",
        "sections": ["hero", "rooms", "amenities", "gallery", "reviews", "contact", "map"],
    },
    "auto_service": {
        "name": "Автосервис",
        "name_en": "Auto Service",
        "name_sr": "Auto servis",
        "sections": ["hero", "services", "prices", "about", "reviews", "contact", "map"],
    },
    "clinic": {
        "name": "Клиника",
        "name_en": "Clinic",
        "name_sr": "Klinika",
        "sections": ["hero", "doctors", "services", "reviews", "contact", "map"],
    },
}


# ============================================================
# LANGUAGE TRANSLATIONS
# ============================================================

L10N = {
    "ru": {
        "nav_home": "Главная",
        "nav_services": "Услуги",
        "nav_about": "О нас", 
        "nav_reviews": "Отзывы",
        "nav_contact": "Контакты",
        "btn_book": "Записаться",
        "btn_call": "Позвонить",
        "btn_website": "Перейти на сайт",
        "section_services": "Наши услуги",
        "section_about": "О нас",
        "section_reviews": "Отзывы",
        "section_contact": "Контакты",
        "section_gallery": "Фотогалерея",
        "rating": "Рейтинг",
        "reviews": "отзывов",
        "address": "Адрес",
        "phone": "Телефон",
        "email": "Email",
        "open_hours": "Часы работы",
        "hero_subtitle": "Ваш лучший выбор в {city}",
        "made_with": "Сделано с ❤️",
        "no_website": "У этого бизнеса пока нет сайта",
    },
    "en": {
        "nav_home": "Home",
        "nav_services": "Services",
        "nav_about": "About",
        "nav_reviews": "Reviews",
        "nav_contact": "Contact",
        "btn_book": "Book Now",
        "btn_call": "Call",
        "btn_website": "Visit Website",
        "section_services": "Our Services",
        "section_about": "About Us",
        "section_reviews": "Reviews",
        "section_contact": "Contact",
        "section_gallery": "Gallery",
        "rating": "Rating",
        "reviews": "reviews",
        "address": "Address",
        "phone": "Phone",
        "email": "Email",
        "open_hours": "Working Hours",
        "hero_subtitle": "Your best choice in {city}",
        "made_with": "Made with ❤️",
        "no_website": "This business doesn't have a website yet",
    },
    "sr": {
        "nav_home": "Početna",
        "nav_services": "Usluge",
        "nav_about": "O nama",
        "nav_reviews": "Recenzije",
        "nav_contact": "Kontakt",
        "btn_book": "Zakaži",
        "btn_call": "Pozovi",
        "btn_website": "Poseti sajt",
        "section_services": "Naše usluge",
        "section_about": "O nama",
        "section_reviews": "Recenzije",
        "section_contact": "Kontakt",
        "section_gallery": "Galerija",
        "rating": "Ocena",
        "reviews": "recenzija",
        "address": "Adresa",
        "phone": "Telefon",
        "email": "Email",
        "open_hours": "Radno vreme",
        "hero_subtitle": "Vaš najbolji izbor u {city}",
        "made_with": "Napravljeno sa ❤️",
        "no_website": "Ovaj biznis još nema sajt",
    },
}


# ============================================================
# HTML GENERATOR
# ============================================================

def generate_demo(lead_data: Dict[str, Any], niche: str = "salon", lang: str = "ru") -> str:
    """Generate a demo landing page HTML for a lead."""
    
    t = L10N.get(lang, L10N["ru"])
    niche_info = NICHES.get(niche, NICHES["salon"])
    
    name = lead_data.get("name", "Business")
    city = lead_data.get("location", {}).get("city", "Budva")
    phone = lead_data.get("phone", "")
    address = lead_data.get("address", "")
    rating = lead_data.get("rating", 0)
    categories = lead_data.get("categories", [])
    
    # Determine colors based on niche
    colors = {
        "salon": {"primary": "#4CAF50", "secondary": "#FF9800", "dark": "#1a1a2e", "light": "#f8f9fa"},
        "restaurant": {"primary": "#D32F2F", "secondary": "#FFC107", "dark": "#1a1a2e", "light": "#fdf2e9"},
        "hotel": {"primary": "#1565C0", "secondary": "#00BCD4", "dark": "#1a1a2e", "light": "#f5f5f5"},
        "auto_service": {"primary": "#212121", "secondary": "#F44336", "dark": "#0d0d0d", "light": "#eeeeee"},
        "clinic": {"primary": "#00897B", "secondary": "#26A69A", "dark": "#1a1a2e", "light": "#f0f4f3"},
    }
    c = colors.get(niche, colors["salon"])
    
    name_key = f"name_{lang}"
    if name_key in niche_info:
        niche_name = niche_info.get(name_key, "")
    else:
        # default key 'name' is Russian
        niche_name = niche_info.get("name", "")
    
    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} | {niche_name} {'в' if lang in ['ru', 'sr'] else 'in'} {city}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               color: #333; line-height: 1.6; background: {c['light']}; }}
        
        /* Hero */
        .hero {{ background: linear-gradient(135deg, {c['dark']} 0%, {c['primary']}aa 100%);
                 color: white; padding: 100px 20px 80px; text-align: center; position: relative; overflow: hidden; }}
        .hero::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; 
                        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="rgba(255,255,255,0.05)" d="M0,224L48,213.3C96,203,192,181,288,181.3C384,181,480,203,576,218.7C672,235,768,245,864,234.7C960,224,1056,192,1152,176C1248,160,1344,160,1392,160L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>') no-repeat bottom; background-size: cover; opacity: 0.3; }}
        .hero h1 {{ font-size: 3em; margin-bottom: 20px; position: relative; z-index: 1; }}
        .hero p {{ font-size: 1.3em; opacity: 0.9; max-width: 600px; margin: 0 auto 30px; position: relative; z-index: 1; }}
        .hero .rating-badge {{ display: inline-block; background: {c['secondary']}; color: #333; padding: 8px 20px; 
                              border-radius: 25px; font-weight: bold; margin-bottom: 20px; position: relative; z-index: 1; }}
        .btn {{ display: inline-block; padding: 15px 40px; background: {c['secondary']}; color: #333; 
               text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 1.1em;
               transition: transform 0.3s, box-shadow 0.3s; cursor: pointer; border: none; }}
        .btn:hover {{ transform: translateY(-3px); box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
        .btn-primary {{ background: {c['secondary']}; color: #333; }}
        .btn-outline {{ background: transparent; border: 2px solid white; color: white; margin-left: 15px; }}
        .btn-outline:hover {{ background: white; color: {c['dark']}; }}
        
        /* Nav */
        nav {{ position: fixed; top: 0; width: 100%; z-index: 100; background: rgba(26,26,46,0.95); 
               backdrop-filter: blur(10px); padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }}
        nav .logo {{ color: white; font-weight: bold; font-size: 1.2em; }}
        nav a {{ color: rgba(255,255,255,0.8); text-decoration: none; margin-left: 20px; font-size: 0.9em; }}
        nav a:hover {{ color: {c['secondary']}; }}
        
        /* Sections */
        section {{ padding: 80px 20px; max-width: 1200px; margin: 0 auto; }}
        section h2 {{ text-align: center; font-size: 2.5em; margin-bottom: 50px; color: {c['dark']}; }}
        .section-light {{ background: white; }}
        .section-dark {{ background: {c['dark']}; color: white; }}
        .section-dark h2 {{ color: white; }}
        
        /* Services Grid */
        .services-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px; }}
        .service-card {{ background: white; padding: 30px; border-radius: 15px; text-align: center; 
                        box-shadow: 0 5px 20px rgba(0,0,0,0.08); transition: transform 0.3s; }}
        .service-card:hover {{ transform: translateY(-5px); }}
        .service-card .icon {{ font-size: 3em; margin-bottom: 15px; }}
        .service-card h3 {{ margin-bottom: 10px; }}
        .service-card p {{ color: #666; font-size: 0.9em; }}
        .service-card .price {{ font-weight: bold; color: {c['primary']}; margin-top: 15px; font-size: 1.2em; }}
        
        /* Contact */
        .contact-info {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 30px; text-align: center; }}
        .contact-item {{ padding: 20px; }}
        .contact-item .icon {{ font-size: 2em; margin-bottom: 10px; }}
        .contact-item a {{ color: {c['secondary']}; text-decoration: none; }}
        
        /* Reviews */
        .review {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; 
                  box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
        .review .stars {{ color: #FFC107; }}
        .review .text {{ margin-top: 10px; font-style: italic; color: #555; }}
        
        /* Footer */
        footer {{ text-align: center; padding: 30px; background: {c['dark']}; color: rgba(255,255,255,0.5); font-size: 0.9em; }}
        
        /* Map placeholder */
        .map-placeholder {{ width: 100%; height: 400px; background: #e0e0e0; border-radius: 15px; 
                           display: flex; align-items: center; justify-content: center; color: #888; }}
        .map-placeholder iframe {{ width: 100%; height: 100%; border: none; border-radius: 15px; }}
        
        /* Mobile */
        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 2em; }}
            nav a {{ margin-left: 10px; font-size: 0.8em; }}
            .btn {{ display: block; width: 100%; margin-bottom: 10px; }}
            .btn-outline {{ margin-left: 0; }}
        }}
        
        /* Floating CTA (mobile) */
        .floating-cta {{ display: none; }}
        @media (max-width: 768px) {{
            .floating-cta {{ display: block; position: fixed; bottom: 0; width: 100%; 
                           z-index: 1000; padding: 10px; background: rgba(26,26,46,0.95); 
                           backdrop-filter: blur(10px); text-align: center; }}
            .floating-cta .btn {{ margin: 0; font-size: 1em; }}
        }}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav>
        <span class="logo">{name}</span>
        <div>
            <a href="#services">{t['nav_services']}</a>
            <a href="#about">{t['nav_about']}</a>
            <a href="#reviews">{t['nav_reviews']}</a>
            <a href="#contact">{t['nav_contact']}</a>
        </div>
    </nav>
    
    <!-- Hero -->
    <section class="hero" id="home">
        <div class="rating-badge">★ {rating} {t['rating']}</div>
        <h1>{name}</h1>
        <p>{niche_name} {t['hero_subtitle'].replace('{city}', city)}</p>
        <div style="position: relative; z-index: 1;">
            <a href="tel:{phone}" class="btn btn-primary">{t['btn_book']}</a>
            <a href="#contact" class="btn btn-outline">{t['btn_call']}</a>
        </div>
    </section>
"""

    # Services section
    sample_services = {
        "salon": [{"icon": "💇", "name": "Стрижка", "name_en": "Haircut", "name_sr": "Šišanje",
                   "desc": "Мужские и женские стрижки любой сложности",
                   "desc_en": "Men's and women's haircuts of any complexity",
                   "desc_sr": "Muško i žensko šišanje bilo koje složenosti",
                   "price": "€15-40"},
                  {"icon": "💅", "name": "Маникюр", "name_en": "Manicure", "name_sr": "Manikir",
                   "desc": "Классический, аппаратный, комбинированный маникюр",
                   "desc_en": "Classic, hardware, combined manicure",
                   "desc_sr": "Klasičan, hardverski, kombinovani manikir",
                   "price": "€20-50"},
                  {"icon": "💆", "name": "Массаж", "name_en": "Massage", "name_sr": "Masaža",
                   "desc": "Расслабляющий и лечебный массаж",
                   "desc_en": "Relaxing and therapeutic massage",
                   "desc_sr": "Relaks i terapijska masaža",
                   "price": "€25-60"}],
        "restaurant": [{"icon": "🍕", "name": "Пицца", "name_en": "Pizza", "name_sr": "Pica",
                        "desc": "Итальянская пицца на тонком тесте",
                        "desc_en": "Italian thin-crust pizza",
                        "desc_sr": "Italijanska pica na tankom testu",
                        "price": "€8-15"},
                       {"icon": "🥗", "name": "Салаты", "name_en": "Salads", "name_sr": "Salate",
                        "desc": "Свежие салаты из локальных продуктов",
                        "desc_en": "Fresh salads from local ingredients",
                        "desc_sr": "Sveže salate od lokalnih sastojaka",
                        "price": "€6-12"}],
    }
    
    services = sample_services.get(niche, sample_services["salon"])
    
    html += f"""
    <!-- Services -->
    <section class="section-light" id="services">
        <h2>{t['section_services']}</h2>
        <div class="services-grid">
"""
    for s in services:
        name = s.get(f"name_{lang}", s.get("name", ""))
        desc = s.get(f"desc_{lang}", s.get("desc", ""))
        html += f"""
            <div class="service-card">
                <div class="icon">{s['icon']}</div>
                <h3>{name}</h3>
                <p>{desc}</p>
                <div class="price">{s['price']}</div>
            </div>"""
    
    html += """
        </div>
    </section>"""

    # About
    html += f"""
    <section class="section-dark" id="about">
        <h2>{t['section_about']}</h2>
        <div style="max-width: 800px; margin: 0 auto; text-align: center; font-size: 1.1em; line-height: 1.8; opacity: 0.9;">
            <p>{name} — {'профессиональный' if lang == 'ru' else 'professional'} {niche_name.lower()} {'с опытом работы более 5 лет.' if lang == 'ru' else 'with over 5 years of experience.'}</p>
            <p style="margin-top: 20px;">{'Мы находимся по адресу: ' + address if address else ''}</p>
        </div>
    </section>"""

    # Reviews
    html += f"""
    <section class="section-light" id="reviews">
        <h2>{t['section_reviews']}</h2>
        <div class="review">
            <div class="stars">★★★★★</div>
            <div class="text">{'Отличное место! Профессиональный сервис и приятная атмосфера.' if lang == 'ru' else 'Great place! Professional service and pleasant atmosphere.'}</div>
        </div>
        <div class="review">
            <div class="stars">★★★★★</div>
            <div class="text">{'Очень довольна результатом. Рекомендую всем!' if lang == 'ru' else 'Very happy with the result. I recommend to everyone!'}</div>
        </div>
    </section>"""

    # Contact
    html += f"""
    <section class="section-dark" id="contact">
        <h2>{t['section_contact']}</h2>
        <div class="contact-info">
            <div class="contact-item">
                <div class="icon">📍</div>
                <h3>{t['address']}</h3>
                <p>{address or f'{city}, Montenegro'}</p>
            </div>
            <div class="contact-item">
                <div class="icon">📞</div>
                <h3>{t['phone']}</h3>
                <a href="tel:{phone}">{phone or '+382 XX XXX XXX'}</a>
            </div>
            <div class="contact-item">
                <div class="icon">⏰</div>
                <h3>{t['open_hours']}</h3>
                <p>Mon-Sat: 9:00 - 20:00<br>Sun: 10:00 - 18:00</p>
            </div>
        </div>
        <div style="margin-top: 40px;">
            <div class="map-placeholder">
                <p>📍 {address or city}</p>
            </div>
        </div>
    </section>"""

    # Footer
    html += f"""
    <footer>
        <p>{t['made_with']} | {name} {'в' if lang in ['ru', 'sr'] else 'in'} {city}</p>
        <p style="margin-top: 10px; font-size: 0.8em;">{t['no_website']}</p>
    </footer>
    
    <!-- Floating CTA -->
    <div class="floating-cta">
        <a href="tel:{phone}" class="btn btn-primary">{t['btn_call']}</a>
    </div>
</body>
</html>"""
    
    return html


def generate_and_save(lead_data: Dict[str, Any], niche: str = "salon", lang: str = "ru",
                      output_dir: str = None) -> str:
    """Generate demo and save to file. Returns path."""
    if output_dir is None:
        output_dir = r"D:\Portable_Soft\hermes\projects\sales-machine\templates"
    
    name = lead_data.get("name", "business").replace(" ", "_").replace("/", "_").lower()
    filename = f"demo_{name}_{lang}.html"
    filepath = os.path.join(output_dir, filename)
    
    os.makedirs(output_dir, exist_ok=True)
    
    html = generate_demo(lead_data, niche, lang)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ Demo saved: {filepath}")
    return filepath


# ============================================================
# GITHUB PAGES DEPLOY
# ============================================================

def deploy_to_github_pages(lead_data: Dict[str, Any], niche: str, lang: str,
                           repo_name: str = None) -> str:
    """Deploy demo to GitHub Pages. Returns URL."""
    import subprocess, tempfile
    
    name = lead_data.get("name", "business").replace(" ", "-").replace("/", "-").lower()
    if not repo_name:
        repo_name = f"demo-{name}-{lang}"
    
    html = generate_demo(lead_data, niche, lang)
    
    # Create temp directory for GitHub Pages deploy
    deploy_dir = os.path.join(r"D:\Portable_Soft\hermes\projects\sales-machine\deploy", repo_name)
    os.makedirs(deploy_dir, exist_ok=True)
    
    with open(os.path.join(deploy_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    
    # Simple CNAME or README
    with open(os.path.join(deploy_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {name}\n\nDemo landing page for {name}\n\nGenerated by Sales Machine\n")
    
    # Deploy to gh-pages via git
    try:
        result = subprocess.run(
            ["gh", "pages", "deploy", "--dir", deploy_dir, "--repo", f"McDuck-S8/{repo_name}"],
            capture_output=True, text=True, timeout=30
        )
        url = result.stdout.strip() or f"https://mcduck-s8.github.io/{repo_name}/"
    except Exception as e:
        print(f"Deploy error: {e}")
        url = f"file://{os.path.join(deploy_dir, 'index.html')}"
    
    return url


def save_demo_record(client_id: str, template: str, lang: str, url: str):
    """Save demo record to database."""
    import sqlite3, uuid
    
    db_path = r"D:\Portable_Soft\hermes\projects\sales-machine\db\clients.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    demo_id = str(uuid.uuid4())[:8]
    
    cursor.execute("""
        INSERT INTO demos (id, client_id, template, language, github_pages_url, generated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (demo_id, client_id, template, lang, url, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return demo_id


if __name__ == "__main__":
    # Test
    test_lead = {
        "name": "Fargo Salon Krasoty",
        "phone": "+382 67 123 456",
        "address": "Budva Old Town, Montenegro",
        "rating": 4.8,
        "location": {"city": "Budva", "country": "Montenegro"},
        "categories": ["beauty salon"],
    }
    
    filepath = generate_and_save(test_lead, niche="salon", lang="ru")
    print(f"Generated: {filepath}")
    
    filepath_en = generate_and_save(test_lead, niche="salon", lang="en")
    print(f"Generated: {filepath_en}")
    
    filepath_sr = generate_and_save(test_lead, niche="salon", lang="sr")
    print(f"Generated: {filepath_sr}")