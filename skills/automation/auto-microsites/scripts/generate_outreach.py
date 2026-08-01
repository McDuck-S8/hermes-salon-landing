#!/usr/bin/env python3
"""
Quick outreach message generator for Simferopol auto-microsites leads.
Usage: python scripts/generate_outreach.py <business_name> <demo_url> [phone] [niche]
"""

import sys
import json

TEMPLATE = """Здравствуйте, {owner_name}!

Я Алексей, веб-разработчик из Симферополя. Нашёл ваш {business_type} в {source} — выглядит отлично!

Заметил, что у вас нет сайта. Это теряет клиентов: люди ищут в Google/Яндекс → не находят → идут к конкуренту.

Я делаю профессиональные сайты для бизнеса:
— Лендинг с услугами и ценами
— Кнопка «Позвонить» (фиксированная, всегда видна)
— Мобильная версия (70% клиентов с телефона)
— Запись онлайн через Telegram
— SEO-оптимизация (чтобы находили в Яндексе)

Стоимость: от 7 000₽ (одностраничный сайт)
Срок: 3-5 дней. Без предоплаты.

Хотите — покажу пример за 2 минуты. Могу сделать демо-сайт именно для вашего бизнеса бесплатно.

{demo_url}

С уважением,
Алексей
+7 (978) XXX-XX-XX
"""

NICHE_PRICES = {
    "barbershop": "7 000–15 000₽",
    "dental": "15 000–25 000₽",
    "auto": "15 000–25 000₽",
    "legal": "15 000–25 000₽",
    "fitness": "10 000–20 000₽",
    "salon": "10 000–20 000₽",
    "cafe": "10 000–20 000₽",
}

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    business_name = sys.argv[1]
    demo_url = sys.argv[2]
    phone = sys.argv[3] if len(sys.argv) > 3 else "+7 (978) XXX-XX-XX"
    niche = sys.argv[4] if len(sys.argv) > 4 else "business"

    price_range = NICHE_PRICES.get(niche.lower(), "7 000–25 000₽")
    
    # Extract owner name from business name (simple heuristic)
    owner_name = business_name.split()[0] if business_name else "Владелец"
    
    message = TEMPLATE.format(
        owner_name=owner_name,
        business_type=niche,
        source="Яндекс.Картах",
        demo_url=demo_url,
    )
    
    # Replace price line
    message = message.replace("от 7 000₽", price_range)
    
    print(message)
    print("\n" + "="*50)
    print(f"Demo URL: {demo_url}")
    print(f"Phone to use: {phone}")
    print(f"Niche: {niche} → price: {price_range}")

if __name__ == "__main__":
    main()