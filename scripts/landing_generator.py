#!/usr/bin/env python3
"""Generate CPA landing pages from templates. Unblocks 25 income schemes."""

import re
import json
from pathlib import Path
from datetime import datetime

HERMES = Path("D:/Portable_Soft/hermes")
TEMPLATES = {
    "fintech": {
        "title": "Быстрый займ онлайн — одобрение 99%",
        "h1": "Нужны деньги до зарплаты?",
        "subtitle": "Заявка за 2 минуты. Без справок и поручителей.",
        "cta": "ПОЛУЧИТЬ ДЕНЬГИ",
        "bullet1": "Сумма до 100 000 руб",
        "bullet2": "Ставка от 0% в день",
        "bullet3": "На карту за 5 минут",
        "bullet4": "Без проверки КИ",
        "footer": "Услуги предоставляются партнерами. Требуется паспорт РФ."
    },
    "vpn": {
        "title": "VPN для доступа к заблокированным сайтам",
        "h1": "Интернет без границ",
        "subtitle": "Быстрый и надежный VPN. 30 дней бесплатно.",
        "cta": "ПОПРОБОВАТЬ БЕСПЛАТНО",
        "bullet1": "50+ стран для подключения",
        "bullet2": "Netflix, YouTube, Instagram — без ограничений",
        "bullet3": "Без логов. Работает в РФ",
        "bullet4": "Поддержка 24/7",
        "footer": "30-дневная гарантия возврата."
    },
    "coupons": {
        "title": "Промокоды и скидки — экономь до 70%",
        "h1": "Лучшие скидки в твоем городе",
        "subtitle": "Более 500 проверенных промокодов",
        "cta": "ПОЛУЧИТЬ СКИДКУ",
        "bullet1": "AliExpress, Wildberries, Ozon",
        "bullet2": "Скидки до 70%",
        "bullet3": "Новые купоны каждый день",
        "bullet4": "Бесплатно",
        "footer": "Партнерские ссылки. Не является офертой."
    },
    "dating": {
        "title": "Знакомства без границ — найди свою любовь",
        "h1": "Миллионы людей уже нашли пару",
        "subtitle": "Регистрация бесплатно. Проверенные анкеты.",
        "cta": "НАЙТИ ПАРУ",
        "bullet1": "Проверка анкет — никаких ботов",
        "bullet2": "Умный алгоритм подбора",
        "bullet3": "Чат, подарки, видео",
        "bullet4": "Конфиденциально",
        "footer": "18+. Сервис предназначен для поиска серьезных отношений."
    },
    "survey": {
        "title": "Зарабатывай на опросах — до 5000 руб/день",
        "h1": "Платим за твое мнение",
        "subtitle": "Пройди опрос и получи деньги на карту",
        "cta": "НАЧАТЬ ЗАРАБАТЫВАТЬ",
        "bullet1": "Выплаты от 50 руб за опрос",
        "bullet2": "Мгновенный вывод на карту",
        "bullet3": "Без вложений",
        "bullet4": "Работай из дома",
        "footer": "Регистрируясь, вы соглашаетесь с условиями"
    },
    "gaming": {
        "title": "Читы и бонусы для твоих игр",
        "h1": "Получи преимущество в игре",
        "subtitle": "Бесплатные скины, V-Bucks и Robux",
        "cta": "ЗАБРАТЬ БОНУС",
        "bullet1": "Fortnite, Roblox, GTA V",
        "bullet2": "Работает на ПК и телефоне",
        "bullet3": "Без вирусов",
        "bullet4": "Бесплатно",
        "footer": "Требуется подтверждение возраста. Не нарушайте правила игр."
    }
}


def generate_landing(template_name: str, offer_link: str = "#", output_name: str = None):
    """Generate a complete HTML landing page from a template."""
    t = TEMPLATES.get(template_name)
    if not t:
        available = ", ".join(TEMPLATES.keys())
        print(f"Unknown template: {template_name}. Available: {available}")
        return None

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{t['title']}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }}
.card {{ background: white; border-radius: 20px; padding: 40px; max-width: 450px; width: 100%; box-shadow: 0 20px 60px rgba(0,0,0,0.3); text-align: center; }}
h1 {{ font-size: 28px; color: #1a1a2e; margin-bottom: 10px; }}
.sub {{ color: #666; margin-bottom: 30px; font-size: 16px; }}
.bullets {{ text-align: left; margin-bottom: 30px; }}
.bullet {{ padding: 10px 0; border-bottom: 1px solid #eee; color: #444; }}
.bullet:before {{ content: "✓ "; color: #667eea; font-weight: bold; }}
.bullet:last-child {{ border-bottom: none; }}
.cta {{ display: block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; padding: 16px 40px; border-radius: 50px; font-size: 18px; font-weight: bold; margin: 20px 0; transition: transform 0.2s; }}
.cta:hover {{ transform: scale(1.05); }}
.footer {{ color: #999; font-size: 12px; margin-top: 20px; }}
.offer {{ margin-top: 25px; }}
.offer a {{ color: #667eea; font-size: 14px; }}
</style>
</head>
<body>
<div class="card">
  <h1>{t['h1']}</h1>
  <p class="sub">{t['subtitle']}</p>
  <div class="bullets">
    <div class="bullet">{t['bullet1']}</div>
    <div class="bullet">{t['bullet2']}</div>
    <div class="bullet">{t['bullet3']}</div>
    <div class="bullet">{t['bullet4']}</div>
  </div>
  <a href="{offer_link}" class="cta">{t['cta']}</a>
  <p class="footer">{t['footer']}</p>
</div>
</body>
</html>"""

    name = output_name or f"landing_{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    output_dir = HERMES / "reports"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / name
    output_path.write_text(html, encoding="utf-8")
    return str(output_path)


def list_templates():
    """Print available templates."""
    print("Available CPA landing templates:")
    print(f"  {'Name':<15} {'Topic':<25} {'CTA':<25}")
    print(f"  {'-'*15} {'-'*25} {'-'*25}")
    for name, t in TEMPLATES.items():
        print(f"  {name:<15} {t['title'][:25]:<25} {t['cta'][:25]:<25}")
    print(f"\nTotal: {len(TEMPLATES)} templates")


def batch_generate(offer_urls: dict = None):
    """Generate one page per template, optionally with specific offer URLs."""
    results = []
    for name in TEMPLATES:
        link = (offer_urls or {}).get(name, "#")
        path = generate_landing(name, link)
        if path:
            results.append((name, path))
    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            list_templates()
        elif cmd == "generate" and len(sys.argv) >= 3:
            template = sys.argv[2]
            link = sys.argv[3] if len(sys.argv) > 3 else "#"
            path = generate_landing(template, link)
            if path:
                print(f"Generated: {path}")
        elif cmd == "batch":
            urls_file = sys.argv[2] if len(sys.argv) > 2 else None
            urls = {}
            if urls_file:
                import json
                urls = json.loads(Path(urls_file).read_text())
            results = batch_generate(urls)
            print(f"Generated {len(results)} landing pages:")
            for name, path in results:
                print(f"  {name}: {path}")
        else:
            print("Usage: python landing_generator.py [list|generate|batch]")
    else:
        list_templates()
