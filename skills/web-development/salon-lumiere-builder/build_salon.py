#!/usr/bin/env python3
"""
Salon Lumiere Builder — Generate beauty salon landing page from template.

Usage:
    python build_salon.py --slug beauty-salon --name "Fargo" --location "Позняки, Київ" ...
    python build_salon.py --params params.json
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from jinja2 import Environment, FileSystemLoader
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    print("Warning: jinja2 not installed. Using simple string replacement.", file=sys.stderr)


class SalonLumiereBuilder:
    """Builds beauty salon landing pages from template."""

    def __init__(self, template_path: Path):
        self.template_path = template_path
        self.template_content = template_path.read_text(encoding='utf-8')
        if JINJA2_AVAILABLE:
            self.jinja_env = Environment(
                loader=FileSystemLoader(template_path.parent),
                autoescape=False
            )
            self.template = self.jinja_env.get_template(template_path.name)

    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate required parameters."""
        errors = []

        required = ['slug', 'salon_name', 'location', 'address', 'phone', 'hours']
        for field in required:
            if not params.get(field):
                errors.append(f"Missing required field: {field}")

        # Validate services (min 1, max 6)
        services = params.get('services', [])
        if not services or len(services) < 1:
            errors.append("At least 1 service required")
        if len(services) > 6:
            errors.append("Maximum 6 services allowed")

        # Validate masters (max 4)
        masters = params.get('masters', [])
        if len(masters) > 4:
            errors.append("Maximum 4 masters allowed")

        # Validate reviews (max 3)
        reviews = params.get('reviews', [])
        if len(reviews) > 3:
            errors.append("Maximum 3 reviews allowed")

        # Validate user_perspective (4 questions)
        up = params.get('user_perspective', {})
        required_up = ['who', 'five_sec', 'action', 'why']
        for q in required_up:
            if not up.get(q):
                errors.append(f"Missing user_perspective.{q}")

        return len(errors) == 0, errors

    def prepare_template_vars(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare variables for template rendering."""
        # Extract phone without formatting for tel: links
        phone_raw = re.sub(r'[^\d+]', '', params['phone'])

        # Default hero content from user_perspective
        up = params.get('user_perspective', {})

        trust_items = params.get('trust_items', [
            "50+ робіт у портфоліо кожного майстра",
            "Ціна на сайті = ціна в салоні",
            "Безкоштовна консультація колориста"
        ])

        return {
            'salon_name': params['salon_name'],
            'location': params['location'],
            'address': params['address'],
            'phone': params['phone'],
            'phone_raw': phone_raw,
            'telegram': params.get('telegram', '').lstrip('@'),
            'hours': params['hours'],
            'services': params['services'],
            'masters': params.get('masters', []),
            'reviews': params.get('reviews', []),
            'hero_badge': f"{params['location']} • {params['address']}",
            'hero_headline': params.get('hero_headline', up.get('five_sec', f'Салон краси <span class="gold">{params["salon_name"]}</span> — чесні ціни, портфоліо майстрів, запис за 30 секунд')),
            'hero_sub': params.get('hero_sub', up.get('why', 'Устали від сюрпризів у чеку? Тут бачите роботу майстра до візиту, знаєте ціну наперед і записуєтесь онлайн без дзвінків.')),
            'hero_cta_primary': params.get('hero_cta_primary', '📅 Записатися онлайн'),
            'hero_cta_secondary': params.get('hero_cta_secondary', f'📞 Подзвонити: {params["phone"]}'),
            'trust_items': trust_items,
        }

    def render(self, params: Dict[str, Any]) -> str:
        """Render template with parameters."""
        valid, errors = self.validate_params(params)
        if not valid:
            raise ValueError(f"Validation failed: {'; '.join(errors)}")

        template_vars = self.prepare_template_vars(params)

        if JINJA2_AVAILABLE:
            return self.template.render(**template_vars)
        else:
            # Simple string replacement fallback
            html = self.template_content
            for key, value in template_vars.items():
                if isinstance(value, (list, dict)):
                    # Handle loops manually for lists
                    continue
                placeholder = f"{{{{{key}}}}}"
                html = html.replace(placeholder, str(value))

            # Handle simple loops for services, masters, reviews
            html = self._render_loops(html, template_vars)
            return html

    def _render_loops(self, html: str, vars: Dict[str, Any]) -> str:
        """Render simple loops for services, masters, reviews."""
        # Services loop
        if 'services' in vars:
            services_html = []
            for s in vars['services']:
                svc = f'''<article class="service-card">
    <div class="service-icon">{s.get('icon', '✨')}</div>
    <h3 class="service-name">{s['name']}</h3>
    <p class="service-desc">{s['desc']}</p>
    <div class="service-price">від {s['price']}<span>₴</span></div>
</article>'''
                services_html.append(svc)
            html = re.sub(
                r'{%\s*for\s+service\s+in\s+services\s*%}.*?{%\s*endfor\s*%}',
                '\n'.join(services_html),
                html,
                flags=re.DOTALL
            )

        # Masters loop
        if 'masters' in vars:
            masters_html = []
            for m in vars['masters']:
                mstr = f'''<article class="master-card">
    <div class="master-photo">
        <img src="assets/masters/{m['photo']}" alt="{m['name']}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
        <span class="placeholder">{m.get('icon', '👤')}</span>
    </div>
    <div class="master-info">
        <h3 class="master-name">{m['name']}</h3>
        <p class="master-spec">{m['spec']}</p>
        <p class="master-bio">{m['bio']}</p>
        <a href="#" class="master-link">Переглянути портфоліо →</a>
    </div>
</article>'''
                masters_html.append(mstr)
            html = re.sub(
                r'{%\s*for\s+master\s+in\s+masters\s*%}.*?{%\s*endfor\s*%}',
                '\n'.join(masters_html),
                html,
                flags=re.DOTALL
            )

        # Reviews loop
        if 'reviews' in vars:
            reviews_html = []
            for r in vars['reviews']:
                stars = '★' * r.get('rating', 5)
                rev = f'''<article class="review-card">
    <div class="review-stars">{stars}</div>
    <p class="review-text">{r['text']}</p>
    <div class="review-author">
        <div class="review-avatar">{r['author'][0]}</div>
        <div>
            <div class="review-name">{r['author']}</div>
            <div class="review-meta">{r.get('service', '')} • {r.get('time', '')}</div>
        </div>
    </div>
</article>'''
                reviews_html.append(rev)
            html = re.sub(
                r'{%\s*for\s+review\s+in\s+reviews\s*%}.*?{%\s*endfor\s*%}',
                '\n'.join(reviews_html),
                html,
                flags=re.DOTALL
            )

        # Trust items loop
        if 'trust_items' in vars:
            trust_html = []
            for item in vars['trust_items']:
                trust_html.append(f'<span class="trust-item">✓ {item}</span>')
            html = re.sub(
                r'{%\s*for\s+item\s+in\s+trust_items\s*%}.*?{%\s*endfor\s*%}',
                '\n'.join(trust_html),
                html,
                flags=re.DOTALL
            )

        return html

    def build(self, params: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        """Build the landing page and return paths."""
        html = self.render(params)

        slug = params['slug']
        output_path = output_dir / slug / 'index.html'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding='utf-8')

        # Create assets directories
        (output_dir / slug / 'assets' / 'masters').mkdir(parents=True, exist_ok=True)

        return {
            'html_path': str(output_path),
            'slug': slug,
            'output_dir': str(output_dir / slug),
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Build beauty salon landing page')
    parser.add_argument('--slug', help='URL slug (e.g., beauty-salon)')
    parser.add_argument('--name', dest='salon_name', help='Salon name')
    parser.add_argument('--location', help='Area, city (e.g., Позняки, Київ)')
    parser.add_argument('--address', help='Street address')
    parser.add_argument('--phone', help='Phone for tel: links (+380441234567)')
    parser.add_argument('--telegram', default='', help='Telegram username (@salon)')
    parser.add_argument('--hours', help='Working hours (e.g., 10:00–20:00 щодня)')
    parser.add_argument('--params', type=Path, help='JSON file with all parameters (bypasses other args)')
    parser.add_argument('--output-dir', type=Path, default=Path('docs/portfolio'), help='Output directory')

    args = parser.parse_args()

    # Load params from file or CLI
    if args.params:
        with open(args.params) as f:
            params = json.load(f)
    else:
        # Validate required CLI args
        for arg in ['slug', 'salon_name', 'location', 'address', 'phone', 'hours']:
            if not getattr(args, arg):
                parser.error(f'--{arg} is required when --params not provided')
        params = {
            'slug': args.slug,
            'salon_name': args.salon_name,
            'location': args.location,
            'address': args.address,
            'phone': args.phone,
            'telegram': args.telegram,
            'hours': args.hours,
            'services': [],
            'masters': [],
            'reviews': [],
            'user_perspective': {}
        }

    # Template path
    template_path = Path(__file__).parent / 'template.html'
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}", file=sys.stderr)
        sys.exit(1)

    builder = SalonLumiereBuilder(template_path)

    try:
        result = builder.build(params, args.output_dir)
        print(f"✅ Landing page built: {result['html_path']}")
        print(f"   Slug: {result['slug']}")
        print(f"   Deploy: git add {result['output_dir']} && git commit -m \"Deploy {result['slug']}\" && git push")
        print(f"   Live URL: https://<user>.github.io/<repo>/portfolio/{result['slug']}/")
        return 0
    except ValueError as e:
        print(f"❌ Validation error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Build failed: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())