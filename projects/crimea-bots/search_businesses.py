#!/usr/bin/env python3
"""
Search for hotels and restaurants in Crimea for cold outreach.
Uses 2GIS API and web scraping.
"""

import requests
import json
import csv
from datetime import datetime

# Crimea cities to search
CITIES = [
    "Ялта",
    "Алушта", 
    "Судак",
    "Евпатория",
    "Феодосия",
    "Симферополь",
    "Керчь",
    "Севастополь",
]

# Search queries
QUERIES = [
    "гостиница",
    "отель",
    "хостел",
    "гостевой дом",
    "ресторан",
    "кафе",
    "пиццерия",
]

def search_2gis(city, query):
    """Search 2GIS for businesses."""
    # Note: This is a template. In production, use official 2GIS API
    print(f"Searching: {city} - {query}")
    
    # Simulated results for demo
    results = []
    
    # In production:
    # url = f"https://catalog.api.2gis.com/3.0/items?q={query} {city}&region_id=..."
    # response = requests.get(url, headers={"Authorization": "Bearer YOUR_KEY"})
    # data = response.json()
    
    return results

def save_to_csv(results, filename):
    """Save results to CSV."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['city', 'type', 'name', 'phone', 'address', 'website'])
        writer.writeheader()
        writer.writerows(results)

def main():
    all_results = []
    
    for city in CITIES:
        for query in QUERIES[:2]:  # Just hotels for now
            results = search_2gis(city, query)
            all_results.extend(results)
    
    # Save results
    filename = f"crimea_businesses_{datetime.now().strftime('%Y%m%d')}.csv"
    save_to_csv(all_results, filename)
    
    print(f"\nFound {len(all_results)} businesses")
    print(f"Saved to {filename}")

if __name__ == "__main__":
    main()
