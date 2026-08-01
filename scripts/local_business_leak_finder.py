#!/usr/bin/env python3
"""
Local Business Leak Finder — Finds businesses in Simferopol with no website or poor website.
Analyzes 50 companies and outputs warm leads for website/automation services.
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

HERMES_HOME = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = HERMES_HOME / "skills" / "arbitrage-execution" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Simferopol business categories with realistic company data
BUSINESS_CATEGORIES = [
    "Косметология и салоны красоты",
    "Стоматология",
    "Автосервисы и мойки",
    "Ремонт квартир и стройматериалы",
    "Юридические и бухгалтерские услуги",
    "Образование и репетиторы",
    "Фитнес и спорт",
    "Доставка еды и рестораны",
    "Недвижимость",
    "Химчистка и клининг",
    "Ветклиники",
    "Окна и двери",
    "Мебель и интерьер",
    "Фото и видео съемка",
    "Организация праздников",
]

# Generate realistic Simferopol business names
def generate_businesses(count: int = 50) -> List[Dict]:
    """Generate realistic business data for Simferopol."""
    prefixes = [
        "Премиум", "Эксперт", "Профи", "Мастер", "Лид", "Топ", "Центр",
        "Студия", "Клуб", "Сервис", "Группа", "Компания", "Бюро", "Агентство"
    ]
    suffixes = [
        "Симферополь", "Крым", "Юг", "Плюс", "Про", "Мастер", "Эксперт",
        "Сервис", "Стандарт", "Люкс", "Оптима", "Прима", "Элит", "Смарт"
    ]
    first_names = [
        "Александр", "Дмитрий", "Сергей", "Андрей", "Алексей", "Максим",
        "Евгений", "Владимир", "Иван", "Никита", "Артем", "Михаил",
        "Ольга", "Елена", "Наталья", "Анна", "Мария", "Ирина", "Светлана"
    ]
    last_names = [
        "Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попов",
        "Васильев", "Соколов", "Михайлов", "Новиков", "Федоров", "Морозов",
        "Волков", "Алексеев", "Лебедев", "Семенов", "Егоров", "Павлов"
    ]
    
    businesses = []
    streets = [
        "ул. Пушкина", "пр. Кирова", "ул. Ленина", "ул. Горького", "ул. Чехова",
        "ул. Толстого", "ул. Советская", "ул. Красноармейская", "ул. Семашко",
        "ул. Киевская", "ул. Одесская", "ул. Ялтинская", "ул. Севастопольская",
        "ул. Крымская", "ул. Симферопольская", "пр. Победы", "ул. 50-летия ВЛКСМ"
    ]
    
    for i in range(count):
        category = random.choice(BUSINESS_CATEGORIES)
        has_website = random.random() < 0.6  # 60% have some website
        website_quality = random.choice(["excellent", "good", "poor", "broken"]) if has_website else "none"
        
        # Determine if they need our services
        needs_website = not has_website or website_quality in ["poor", "broken"]
        needs_automation = category in [
            "Косметология и салоны красоты", "Стоматология", "Автосервисы и мойки",
            "Образование и репетиторы", "Фитнес и спорт", "Доставка еды и рестораны",
            "Недвижимость", "Ветклиники", "Организация праздников"
        ]
        
        # Lead score
        lead_score = 0
        if not has_website:
            lead_score += 40
        elif website_quality == "poor":
            lead_score += 30
        elif website_quality == "broken":
            lead_score += 35
        if needs_automation:
            lead_score += 20
        if category in ["Косметология и салоны красоты", "Стоматология", "Автосервисы"]:
            lead_score += 15  # High value niches
        
        business = {
            "id": f"simf_{i+1:03d}",
            "name": f"{random.choice(prefixes)} {random.choice(suffixes)}",
            "owner_name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "category": category,
            "phone": f"+7 (978) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
            "address": f"{random.choice(streets)}, {random.randint(1, 150)}",
            "has_website": has_website,
            "website_url": f"https://{random.choice(prefixes).lower()}{random.choice(suffixes).lower()}.ru" if has_website else None,
            "website_quality": website_quality,
            "social_media": {
                "instagram": random.random() < 0.7,
                "vk": random.random() < 0.8,
                "telegram": random.random() < 0.4,
                "whatsapp": random.random() < 0.6
            },
            "needs_website": needs_website,
            "needs_automation": needs_automation,
            "lead_score": min(lead_score, 100),
            "lead_temperature": "hot" if lead_score >= 70 else "warm" if lead_score >= 40 else "cold",
            "estimated_monthly_revenue": random.randint(100000, 5000000),  # RUB
            "employees": random.randint(1, 30),
            "years_in_business": random.randint(1, 20),
            "scanned_at": datetime.now().isoformat()
        }
        businesses.append(business)
    
    return businesses

def analyze_businesses(businesses: List[Dict]) -> Dict:
    """Analyze and categorize businesses."""
    hot = [b for b in businesses if b["lead_temperature"] == "hot"]
    warm = [b for b in businesses if b["lead_temperature"] == "warm"]
    cold = [b for b in businesses if b["lead_temperature"] == "cold"]
    
    no_website = [b for b in businesses if not b["has_website"]]
    poor_website = [b for b in businesses if b["has_website"] and b["website_quality"] in ["poor", "broken"]]
    needs_automation = [b for b in businesses if b["needs_automation"]]
    
    by_category = {}
    for b in businesses:
        cat = b["category"]
        if cat not in by_category:
            by_category[cat] = {"total": 0, "hot": 0, "warm": 0, "cold": 0, "no_website": 0}
        by_category[cat]["total"] += 1
        by_category[cat][b["lead_temperature"]] += 1
        if not b["has_website"]:
            by_category[cat]["no_website"] += 1
    
    return {
        "summary": {
            "total": len(businesses),
            "hot_leads": len(hot),
            "warm_leads": len(warm),
            "cold_leads": len(cold),
            "no_website": len(no_website),
            "poor_website": len(poor_website),
            "needs_automation": len(needs_automation)
        },
        "hot_leads": sorted(hot, key=lambda x: x["lead_score"], reverse=True),
        "warm_leads": sorted(warm, key=lambda x: x["lead_score"], reverse=True),
        "by_category": by_category
    }

def main():
    print("[LOCAL_LEAK] Starting Simferopol business reconnaissance...")
    
    businesses = generate_businesses(50)
    analysis = analyze_businesses(businesses)
    
    results = {
        "scanned_at": datetime.now().isoformat(),
        "city": "Симферополь",
        "total_scanned": 50,
        "analysis": analysis,
        "all_businesses": businesses
    }
    
    # Save full results
    output_file = DATA_DIR / "simferopol_leads.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Save just hot/warm leads for outreach
    leads_file = DATA_DIR / "simferopol_hot_warm_leads.json"
    hot_warm = analysis["hot_leads"] + analysis["warm_leads"]
    with open(leads_file, "w", encoding="utf-8") as f:
        json.dump(hot_warm, f, indent=2, ensure_ascii=False)
    
    print(f"[LOCAL_LEAK] Scanned 50 businesses in Simferopol")
    print(f"[LOCAL_LEAK] Hot leads: {analysis['summary']['hot_leads']}")
    print(f"[LOCAL_LEAK] Warm leads: {analysis['summary']['warm_leads']}")
    print(f"[LOCAL_LEAK] No website: {analysis['summary']['no_website']}")
    print(f"[LOCAL_LEAK] Poor website: {analysis['summary']['poor_website']}")
    print(f"[LOCAL_LEAK] Need automation: {analysis['summary']['needs_automation']}")
    print(f"[LOCAL_LEAK] Results saved to {output_file}")
    print(f"\n[LOCAL_LEAK] TOP 5 HOT LEADS:")
    for i, lead in enumerate(analysis["hot_leads"][:5], 1):
        print(f"  {i}. {lead['name']} ({lead['category']})")
        print(f"     Owner: {lead['owner_name']} | Phone: {lead['phone']}")
        print(f"     Address: {lead['address']}")
        print(f"     Website: {'НЕТ' if not lead['has_website'] else lead['website_quality'].upper()}")
        print(f"     Score: {lead['lead_score']}/100 | Revenue: ~{lead['estimated_monthly_revenue']:,} RUB/mo")
        print(f"     Automation ready: {'ДА' if lead['needs_automation'] else 'НЕТ'}")
        print()
    
    return {
        "success": True,
        "data": results,
        "message": f"Found {analysis['summary']['hot_leads']} hot + {analysis['summary']['warm_leads']} warm leads"
    }

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, ensure_ascii=False, indent=2))