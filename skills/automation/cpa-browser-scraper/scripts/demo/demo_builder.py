"""
Sales Machine - Demo Builder
Generates landing pages for different niches from templates.
Supports multiple languages and auto-deploys to GitHub Pages.
"""

import sys
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from string import Template

import subprocess


@dataclass
class BusinessData:
    """Business data for demo generation."""
    name: str
    phone: str
    address: str
    website: str = ""
    rating: float = 0.0
    review_count: int = 0
    categories: List[str] = None
    services: List[str] = None
    photos: List[str] = None
    city: str = ""
    country: str = ""
    language: str = "ru"
    niche: str = "beauty"
    contact_email: str = ""
    social_media: Dict[str, str] = None
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = []
        if self.services is None:
            self.services = []
        if self.photos is None:
            self.photos = []
        if self.social_media is None:
            self.social_media = {}


class DemoBuilder:
    """Builds landing pages from templates."""
    
    TEMPLATES_DIR = Path(__file__).parent / "templates"
    OUTPUT_DIR = Path("/tmp/sales_machine_demos")
    
    # Niche-specific configurations
    NICHE_CONFIG = {
        "beauty": {
            "title_template": "{name} — {city} салон красоты",
            "hero_subtitle": "Стиль, уют, профессионализм. Ваша красота — наша работа.",
            "cta_primary": "Записаться онлайн",
            "cta_secondary": "Позвонить",
            "features": [
                {"icon": "✂️", "title": "Стрижки и укладки", "desc": "Трендовые техники, лучшие мастера"},
                {"icon": "💅", "title": "Маникюр и педикюр", "desc": "Гель-лак, дизайн, уход"},
                {"icon": "🧴", "title": "Уходовые процедуры", "desc": "Маски, пилинги, массаж головы"},
                {"icon": "🎨", "title": "Фарбувание и мелирование", "desc": "Сложные техники, натуральные краски"}
            ],
            "gallery_placeholder": "Наши работы",
            "testimonials": [
                {"text": "Лучший салон в городе! Мастера настоящие профи, атмосфера уютная.", "author": "Анна К."},
                {"text": "Всегда записываюсь только сюда. Качество и сервис на высоте.", "author": "Мария П."}
            ]
        },
        "restaurant": {
            "title_template": "{name} — ресторан в {city}",
            "hero_subtitle": "Вкусная еда, уютная атмосфера, отличный сервис.",
            "cta_primary": "Забронировать столик",
            "cta_secondary": "Меню",
            "features": [
                {"icon": "🍽️", "title": "Авторское меню", "desc": "Свежие ингредиенты, уникальные рецепты"},
                {"icon": "🍷", "title": "Карта вин", "desc": "Лучшие вина мира по адекватным ценам"},
                {"icon": "🎉", "title": "Банкеты и события", "desc": "Организация праздников под ключ"},
                {"icon": "🚗", "title": "Удобная парковка", "desc": "Бесплатная для гостей ресторана"}
            ],
            "gallery_placeholder": "Наши блюда",
            "testimonials": [
                {"text": "Невероятно вкусно! Придем снова обязательно.", "author": "Дмитрий С."},
                {"text": "Лучший ужин в городе. Рекомендую всем!", "author": "Елена В."}
            ]
        },
        "hotel": {
            "title_template": "{name} — отель в {city}",
            "hero_subtitle": "Комфорт, уют, лучшее соотношение цена/качество.",
            "cta_primary": "Забронировать номер",
            "cta_secondary": "Узнать цены",
            "features": [
                {"icon": "🛏️", "title": "Уютные номера", "desc": "Современный ремонт, ортопедические матрасы"},
                {"icon": "🍳", "title": "Завтрак включен", "desc": "Шведский стол, свежая выпечка, натуральный кофе"},
                {"icon": "🏊", "title": "Бассейн и СПА", "desc": "Релакс после долгого дня"},
                {"icon": "📍", "title": "Центральное расположение", "desc": "Пешком до главных достопримечательностей"}
            ],
            "gallery_placeholder": "Номера и 영토",
            "testimonials": [
                {"text": "Идеальное место для отдыха. Всё чисто, персонал внимательный.", "author": "Сергей М."},
                {"text": "Отличное соотношение цена/качество. Рекомендую!", "author": "Ольга Т."}
            ]
        },
        "auto": {
            "title_template": "{name} — автосервис в {city}",
            "hero_subtitle": "Качественный ремонт, честные цены, гарантия на все работы.",
            "cta_primary": "Записаться на диагностику",
            "cta_secondary": "Позвонить",
            "features": [
                {"icon": "🔧", "title": "Двигатель и КПП", "desc": "Ремонт любой сложности, оригинальные запчасти"},
                {"icon": "🛞", "title": "Подвеска и тормоза", "desc": "Диагностика на стенде, замена за 1 день"},
                {"icon": "⚡", "title": "Электрика и диагностика", "desc": "Сканеры всех марок, поиск утечек тока"},
                {"icon": "🛢️", "title": "Замена масел и жидкостей", "desc": "Только качественные масла, работа по стандартам дилера"}
            ],
            "gallery_placeholder": "Наши работы",
            "testimonials": [
                {"text": "Единственный сервис, которому доверяю свою машину. Честно и качественно.", "author": "Андрей К."},
                {"text": "Цены адекватные, работу делают быстро. Рекомендую!", "author": "Иван П."}
            ]
        },
        "clinic": {
            "title_template": "{name} — клиника в {city}",
            "hero_subtitle": "Профессиональная медицина, современное оборудование, забота о пациентах.",
            "cta_primary": "Записаться к врачу",
            "cta_secondary": "Позвонить",
            "features": [
                {"icon": "👨‍⚕️", "title": "Опытные врачи", "desc": "Специалисты высшей категории, стаж от 10 лет"},
                {"icon": "🔬", "title": "Современная диагностика", "desc": "МРТ, КТ, УЗИ, лаборатория экспертного уровня"},
                {"icon": "💊", "title": "Лечение по протоколам", "desc": "Международные стандарты, доказательная медицина"},
                {"icon": "🕐", "title": "Удобное время приема", "desc": "Работаем без выходных, запись онлайн 24/7"}
            ],
            "gallery_placeholder": "Наша клиника",
            "testimonials": [
                {"text": "Врачи настоящие профи. Объяснили всё понятно, лечение помогло.", "author": "Наталья С."},
                {"text": "Очень внимательный персонал, чистота, уют. Спасибо!", "author": "Михаил Р."}
            ]
        }
    }
    
    def __init__(self):
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self._create_templates()
    
    def _create_templates(self):
        """Create default templates if not exist."""
        self.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
        
        # Main HTML template
        main_template = '''<!DOCTYPE html>
<html lang="{{language}}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <meta name="description" content="{{description}}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; line-height: 1.6; color: #1a1a2e; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        
        /* Header */
        header { background: #fff; box-shadow: 0 2px 20px rgba(0,0,0,0.08); position: sticky; top: 0; z-index: 100; }
        .header-inner { display: flex; justify-content: space-between; align-items: center; height: 70px; }
        .logo { font-weight: 700; font-size: 1.5rem; color: #1a1a2e; text-decoration: none; }
        .nav { display: flex; gap: 30px; }
        .nav a { color: #4a4a6a; text-decoration: none; font-weight: 500; transition: color 0.2s; }
        .nav a:hover { color: #6366f1; }
        .btn { padding: 12px 24px; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; }
        .btn-primary { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: #fff; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(99,102,241,0.4); }
        .btn-secondary { background: #fff; color: #6366f1; border: 2px solid #6366f1; }
        .btn-secondary:hover { background: #f5f3ff; }
        
        /* Hero */
        .hero { padding: 100px 0; background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%); }
        .hero h1 { font-size: 3rem; font-weight: 700; line-height: 1.2; margin-bottom: 16px; color: #1a1a2e; }
        .hero .subtitle { font-size: 1.25rem; color: #4a4a6a; margin-bottom: 32px; max-width: 600px; }
        .hero-buttons { display: flex; gap: 16px; flex-wrap: wrap; }
        
        /* Features */
        .features { padding: 100px 0; background: #fff; }
        .section-header { text-align: center; margin-bottom: 60px; }
        .section-header h2 { font-size: 2.5rem; font-weight: 700; color: #1a1a2e; margin-bottom: 12px; }
        .section-header p { font-size: 1.125rem; color: #4a4a6a; max-width: 600px; margin: 0 auto; }
        .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; }
        .feature-card { padding: 40px 30px; background: #fafbff; border-radius: 16px; border: 1px solid #eef2ff; transition: all 0.3s; }
        .feature-card:hover { transform: translateY(-4px); box-shadow: 0 20px 40px rgba(99,102,241,0.1); border-color: #c7d2fe; }
        .feature-icon { font-size: 2.5rem; margin-bottom: 16px; display: block; }
        .feature-card h3 { font-size: 1.25rem; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }
        .feature-card p { color: #4a4a6a; }
        
        /* Gallery */
        .gallery { padding: 100px 0; background: #f8fafc; }
        .gallery-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .gallery-item { aspect-ratio: 4/3; border-radius: 12px; overflow: hidden; background: #eef2ff; display: flex; align-items: center; justify-content: center; color: #6366f1; font-weight: 500; }
        
        /* Testimonials */
        .testimonials { padding: 100px 0; background: #fff; }
        .testimonials-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; }
        .testimonial-card { padding: 40px; background: #fafbff; border-radius: 16px; border: 1px solid #eef2ff; }
        .testimonial-text { font-size: 1.1rem; line-height: 1.7; color: #1a1a2e; margin-bottom: 20px; font-style: italic; }
        .testimonial-author { font-weight: 600; color: #6366f1; }
        
        /* Contact/CTA */
        .contact { padding: 100px 0; background: linear-gradient(135deg, #1a1a2e 0%, #312e81 100%); color: #fff; text-align: center; }
        .contact h2 { font-size: 2.5rem; font-weight: 700; margin-bottom: 16px; }
        .contact p { font-size: 1.125rem; color: #c7d2fe; margin-bottom: 32px; max-width: 600px; margin-left: auto; margin-right: auto; }
        .contact-info { display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; margin-top: 40px; }
        .contact-item { display: flex; align-items: center; gap: 8px; font-size: 1.1rem; }
        
        /* Footer */
        footer { background: #0f0f1a; color: #94a3b8; padding: 40px 0; text-align: center; }
        .footer-links { display: flex; justify-content: center; gap: 30px; margin-bottom: 20px; }
        .footer-links a { color: #94a3b8; text-decoration: none; transition: color 0.2s; }
        .footer-links a:hover { color: #fff; }
        
        /* Mobile */
        @media (max-width: 768px) {
            .hero h1 { font-size: 2rem; }
            .hero .subtitle { font-size: 1rem; }
            .section-header h2 { font-size: 1.75rem; }
            .nav { display: none; }
            .contact-info { flex-direction: column; gap: 16px; }
        }
    </style>
</head>
<body>
    <header>
        <div class="container header-inner">
            <a href="#" class="logo">{{business_name}}</a>
            <nav class="nav">
                <a href="#features">Услуги</a>
                <a href="#gallery">Галерея</a>
                <a href="#reviews">Отзывы</a>
                <a href="#contact" class="btn btn-secondary">{{cta_secondary}}</a>
            </nav>
        </div>
    </header>
    
    <section class="hero">
        <div class="container">
            <h1>{{hero_title}}</h1>
            <p class="subtitle">{{hero_subtitle}}</p>
            <div class="hero-buttons">
                <a href="#contact" class="btn btn-primary">{{cta_primary}}</a>
                <a href="#features" class="btn btn-secondary">{{cta_secondary}}</a>
            </div>
        </div>
    </section>
    
    <section id="features" class="features">
        <div class="container">
            <div class="section-header">
                <h2>Наши услуги</h2>
                <p>{{features_intro}}</p>
            </div>
            <div class="features-grid">
                {% for feature in features %}
                <div class="feature-card">
                    <span class="feature-icon">{{feature.icon}}</span>
                    <h3>{{feature.title}}</h3>
                    <p>{{feature.desc}}</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>
    
    <section id="gallery" class="gallery">
        <div class="container">
            <div class="section-header">
                <h2>{{gallery_title}}</h2>
            </div>
            <div class="gallery-grid">
                {% for i in range(gallery_count) %}
                <div class="gallery-item">Фото {{loop.index}}</div>
                {% endfor %}
            </div>
        </div>
    </section>
    
    <section id="reviews" class="testimonials">
        <div class="container">
            <div class="section-header">
                <h2>Отзывы клиентов</h2>
            </div>
            <div class="testimonials-grid">
                {% for testimonial in testimonials %}
                <div class="testimonial-card">
                    <p class="testimonial-text">"{{testimonial.text}}"</p>
                    <p class="testimonial-author">— {{testimonial.author}}</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>
    
    <section id="contact" class="contact">
        <div class="container">
            <h2>{{contact_title}}</h2>
            <p>{{contact_subtitle}}</p>
            <a href="tel:{{phone}}" class="btn btn-primary" style="background: #fff; color: #1a1a2e;">{{cta_primary}}</a>
            <div class="contact-info">
                <div class="contact-item">📍 {{address}}</div>
                <div class="contact-item">📞 {{phone}}</div>
                {% if email %}<div class="contact-item">✉️ {{email}}</div>{% endif %}
            </div>
        </div>
    </section>
    
    <footer>
        <div class="container">
            <div class="footer-links">
                <a href="#">Политика конфиденциальности</a>
                <a href="#">Условия использования</a>
            </div>
            <p>&copy; {{year}} {{business_name}}. Все права защищены.</p>
        </div>
    </footer>
    
    <script>
        // Smooth scroll
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({behavior: 'smooth'});
            });
        });
        
        // Phone click tracking
        document.querySelectorAll('a[href^="tel:"]').forEach(link => {
            link.addEventListener('click', () => {
                if (window.gtag) gtag('event', 'phone_click', {'phone': link.href});
            });
        });
    </script>
</body>
</html>'''
        
        (self.TEMPLATES_DIR / "main.html").write_text(main_template, encoding='utf-8')
    
    def generate_demo(self, business: BusinessData, output_name: str = None) -> Path:
        """Generate a landing page for a business."""
        
        # Get niche config
        niche_cfg = self.NICHE_CONFIG.get(business.niche, self.NICHE_CONFIG["beauty"])
        
        # Prepare template variables
        title = niche_cfg["title_template"].format(name=business.name, city=business.city)
        hero_title = f"{business.name} — {business.city}"
        hero_subtitle = niche_cfg["hero_subtitle"]
        cta_primary = niche_cfg["cta_primary"]
        cta_secondary = niche_cfg["cta_secondary"]
        
        # Features
        features = niche_cfg["features"]
        features_intro = "Мы предлагаем широкий спектр качественных услуг для вашего комфорта и красоты."
        
        # Gallery
        gallery_title = niche_cfg["gallery_placeholder"]
        gallery_count = 6
        
        # Testimonials
        testimonials = niche_cfg["testimonials"]
        
        # Contact
        contact_title = "Свяжитесь с нами"
        contact_subtitle = "Мы всегда на связи. Запишитесь онлайн или позвоните — ответим на все вопросы."
        
        # Render template
        template = self.TEMPLATES_DIR / "main.html"
        from jinja2 import Template as JinjaTemplate
        template_str = template.read_text(encoding='utf-8')
        jinja_template = JinjaTemplate(template_str)
        
        html = jinja_template.render(
            language=business.language,
            title=title,
            description=f"{business.name} в {business.city} — {niche_cfg['hero_subtitle']}",
            business_name=business.name,
            hero_title=hero_title,
            hero_subtitle=hero_subtitle,
            cta_primary=cta_primary,
            cta_secondary=cta_secondary,
            features_intro=features_intro,
            features=features,
            gallery_title=gallery_title,
            gallery_count=gallery_count,
            testimonials=testimonials,
            contact_title=contact_title,
            contact_subtitle=contact_subtitle,
            phone=business.phone,
            address=business.address,
            email=business.contact_email,
            year=datetime.now().year,
            cta_primary=cta_primary
        )
        
        # Save
        if output_name is None:
            output_name = f"{business.name.lower().replace(' ', '_')}_{business.city.lower()}"
        
        output_path = self.OUTPUT_DIR / f"{output_name}.html"
        output_path.write_text(html, encoding='utf-8')
        
        return output_path
    
    def deploy_to_github_pages(self, demo_path: Path, repo_name: str, branch: str = "gh-pages") -> str:
        """Deploy demo to GitHub Pages."""
        # This would push to a GitHub repo
        # For now, return the local path
        return f"Demo ready at: {demo_path}"
    
    def batch_generate(self, businesses: List[BusinessData]) -> List[Path]:
        """Generate demos for multiple businesses."""
        paths = []
        for biz in businesses:
            path = self.generate_demo(biz)
            paths.append(path)
            print(f"✅ Generated: {path}")
        return paths


# Jinja2 template engine (simplified)
class Template:
    """Simple template engine fallback if jinja2 not available."""
    def __init__(self, template_str: str):
        self.template_str = template_str
    
    def render(self, **kwargs):
        result = self.template_str
        for key, value in kwargs.items():
            if isinstance(value, list):
                # Handle loops
                result = self._render_loops(result, key, value)
            else:
                placeholder = f"{{{{{key}}}}}"
                result = result.replace(placeholder, str(value))
        return result
    
    def _render_loops(self, text: str, key: str, items: List):
        # Simple loop handling for {% for item in items %}...{% endfor %}
        import re
        pattern = rf"{{% for (\w+) in {key} %}}(.*?){{% endfor %}}"
        def replace_loop(match):
            var_name = match.group(1)
            loop_content = match.group(2)
            results = []
            for i, item in enumerate(items):
                loop_result = loop_content
                if isinstance(item, dict):
                    for k, v in item.items():
                        loop_result = loop_result.replace(f"{{{{{var_name}.{k}}}}}", str(v))
                loop_result = loop_result.replace(f"{{{{loop.index}}}}", str(i+1))
                results.append(loop_result)
            return "".join(results)
        return re.sub(pattern, replace_loop, text, flags=re.DOTALL)


if __name__ == "__main__":
    # Test generation
    builder = DemoBuilder()
    
    biz = BusinessData(
        name="Эстетика",
        phone="+382 69 123 456",
        address="Будва, Черногория, ул. Славянская 15",
        city="Будва",
        country="ME",
        language="ru",
        niche="beauty",
        services=["Стрижки", "Маникюр", "Педикюр", "Уход"],
        contact_email="info@estetika.me",
        social_media={"instagram": "https://instagram.com/estetika_budva"}
    )
    
    path = builder.generate_demo(biz)
    print(f"Demo generated: {path}")