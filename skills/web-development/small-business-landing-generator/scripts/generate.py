#!/usr/bin/env python3
"""
Batch generate landing pages from CSV of leads.
Usage: python scripts/generate.py leads.csv
"""

import csv
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import generate, generate_from_json

def generate_from_csv(csv_path: str):
    """Generate landing pages from CSV file."""
    project_root = Path(__file__).parent.parent
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    print(f"Found {len(leads)} leads in {csv_path}")
    
    for i, lead in enumerate(leads, 1):
        # Skip rows with missing required fields
        if not lead.get('business_name') or not lead.get('phone'):
            print(f"  [{i}/{len(leads)}] ⚠️  Skipping {lead.get('business_name', 'unnamed')}: missing required fields")
            continue
        
        # Map CSV columns to JSON schema
        data = {
            "project_name": lead.get('project_name', lead['business_name'].lower().replace(' ', '-').replace('ё', 'e')),
            "business_name": lead['business_name'],
            "tagline": lead.get('tagline', 'Профессиональный сервис'),
            "phone": lead['phone'],
            "address": lead.get('address', 'г. Симферополь'),
            "working_hours": lead.get('working_hours', 'Пн-Вс: 09:00-21:00'),
            "color_primary": lead.get('color_primary', '#2563eb'),
            "color_accent": lead.get('color_accent', '#f59e0b'),
            "cta_text": lead.get('cta_text', 'Позвонить'),
            "about": lead.get('about', 'Мы предоставляем качественные услуги.'),
            "services": [],
            "seo_title": lead.get('seo_title', lead['business_name']),
            "seo_description": lead.get('seo_description', f"{lead['business_name']} — профессиональные услуги в Симферополе.")
        }
        
        # Parse services if provided
        services_text = lead.get('services', '')
        if services_text:
            for line in services_text.split('|'):
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 1:
                    service = {
                        "name": parts[0],
                        "price": parts[1] if len(parts) > 1 else "",
                        "description": parts[2] if len(parts) > 2 else ""
                    }
                    data["services"].append(service)
        
        # Generate
        try:
            path = generate(data['project_name'], data)
            print(f"  [{i}/{len(leads)}] ✅ {data['business_name']} → {path}")
        except Exception as e:
            print(f"  [{i}/{len(leads)}] ❌ {data['business_name']}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate.py leads.csv")
        sys.exit(1)
    
    generate_from_csv(sys.argv[1])