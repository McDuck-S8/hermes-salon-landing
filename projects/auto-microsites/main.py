#!/usr/bin/env python3
"""
Auto Microsites Generator — генератор лендингов для малого бизнеса.
Вход: JSON с данными бизнеса → Выход: готовый index.html
"""
import json
import sys
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("auto-microsites")

BASE = Path(__file__).resolve().parent
TEMPLATES = BASE / "templates"
GENERATED = BASE / "generated"


def load_template(name: str = "business") -> str:
    tpl = TEMPLATES / f"{name}.html"
    if not tpl.exists():
        raise FileNotFoundError(f"Template not found: {tpl}")
    return tpl.read_text(encoding="utf-8")


def generate(project_name: str, data: dict, template_name: str = "business") -> str:
    """Generate a microsite for a business.
    
    data keys:
        business_name: str
        tagline: str
        phone: str
        address: str
        working_hours: str
        services: list[dict]  # [{name, price, description}]
        about: str
        color_primary: str   # hex color, default #2563eb
        color_accent: str    # hex color, default #f59e0b
        cta_text: str        # call-to-action button text
        seo_title: str
        seo_description: str
    """
    log.info(f"Generating microsite for {project_name}...")

    # Defaults
    data.setdefault("business_name", project_name)
    data.setdefault("tagline", "Лучший сервис в городе")
    data.setdefault("phone", "+7 (XXX) XXX-XX-XX")
    data.setdefault("address", "г. Симферополь")
    data.setdefault("working_hours", "Пн-Вс: 09:00-21:00")
    data.setdefault("services", [])
    data.setdefault("about", "Мы работаем для вас!")
    data.setdefault("color_primary", "#2563eb")
    data.setdefault("color_accent", "#f59e0b")
    data.setdefault("cta_text", "Позвонить")
    data.setdefault("seo_title", data["business_name"])
    data.setdefault("seo_description", f"{data['business_name']} — {data['tagline']}")

    # Build services HTML
    services_html = ""
    for s in data["services"]:
        price = s.get("price", "")
        price_str = f"<span class='price'>{price}</span>" if price else ""
        services_html += f"""
        <div class="service-card">
            <h3>{s.get('name', 'Услуга')}</h3>
            <p>{s.get('description', '')}</p>
            {price_str}
        </div>"""

    if not services_html:
        services_html = "<p class='placeholder'>Услуги скоро будут добавлены</p>"

    # Load and fill template
    template = load_template(template_name)

    replacements = {
        "{{BUSINESS_NAME}}": data["business_name"],
        "{{TAGLINE}}": data["tagline"],
        "{{PHONE}}": data["phone"],
        "{{PHONE_RAW}}": data["phone"].replace(" ", "").replace("(", "").replace(")", "").replace("-", ""),
        "{{ADDRESS}}": data["address"],
        "{{WORKING_HOURS}}": data["working_hours"],
        "{{SERVICES}}": services_html,
        "{{ABOUT}}": data["about"],
        "{{COLOR_PRIMARY}}": data["color_primary"],
        "{{COLOR_ACCENT}}": data["color_accent"],
        "{{CTA_TEXT}}": data["cta_text"],
        "{{SEO_TITLE}}": data["seo_title"],
        "{{SEO_DESCRIPTION}}": data["seo_description"],
        "{{YEAR}}": str(datetime.now().year),
        "{{GENERATED_AT}}": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    html = template
    for key, value in replacements.items():
        html = html.replace(key, value)

    # Write output
    out_dir = GENERATED / project_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "index.html"
    out_file.write_text(html, encoding="utf-8")

    log.info(f"✅ Generated: {out_file} ({len(html)} chars)")
    return str(out_file)


def generate_from_json(json_path: str) -> str:
    """Generate from a JSON config file."""
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    name = data.pop("project_name", Path(json_path).stem)
    return generate(name, data)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py <project_name>       # generate sample")
        print("  python main.py --from <config.json>  # generate from config")
        print("  python main.py --list                # list generated sites")
        return

    if sys.argv[1] == "--list":
        if GENERATED.exists():
            for d in sorted(GENERATED.iterdir()):
                if d.is_dir() and (d / "index.html").exists():
                    size = (d / "index.html").stat().st_size
                    print(f"  {d.name}/  ({size} bytes)")
        else:
            print("No generated sites yet.")
        return

    if sys.argv[1] == "--from" and len(sys.argv) > 2:
        path = generate_from_json(sys.argv[2])
        print(f"Generated: {path}")
        return

    # Generate sample for named project
    project = sys.argv[1]
    sample_data = {
        "business_name": project,
        "tagline": "Профессиональный сервис",
        "phone": "+7 (978) 123-45-67",
        "address": "г. Симферополь, ул. Примерная, 1",
        "working_hours": "Пн-Пт: 09:00-18:00",
        "services": [
            {"name": "Услуга 1", "price": "от 1 000 ₽", "description": "Описание услуги"},
        ],
        "about": "Мы предоставляем качественные услуги.",
    }
    path = generate(project, sample_data)
    print(f"Generated: {path}")


if __name__ == "__main__":
    main()
