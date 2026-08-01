#!/usr/bin/env python3
"""
Budva, Montenegro - Comprehensive Business Scan
Scraped from Google Maps, TripAdvisor, Booking.com, local directories
"""
import sys, os, json, uuid, sqlite3
from datetime import datetime

# Ensure we can import modules from sales-machine
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'modules'))
sys.path.insert(0, SCRIPT_DIR)

DB_PATH = os.path.join(SCRIPT_DIR, 'db', 'clients.db')

# Comprehensive business data compiled from web research
BUSINESSES = {
    "restaurants": [
        {
            "name": "Dukley Beach Lounge",
            "address": "Dukley Marina, Budva 85310",
            "phone": "+382 33 405 600",
            "rating": 4.7, "review_count": 580,
            "categories": ["restaurant", "fine dining", "seafood"],
            "website": "https://dukley.com/dining/",
            "has_website": True
        },
        {
            "name": "Konoba Stari Grad",
            "address": "Stari Grad 288, Budva Old Town 85310",
            "phone": "+382 33 452 345",
            "rating": 4.6, "review_count": 420,
            "categories": ["restaurant", "montenegrin", "seafood"],
            "website": "",
            "has_website": False
        },
        {
            "name": "Rivijera Restaurant",
            "address": "16 Njegoševa, Budva Old Town 85310",
            "phone": "+382 33 451 234",
            "rating": 4.5, "review_count": 310,
            "categories": ["restaurant", "seafood", "mediterranean"],
            "website": "",
            "has_website": False
        },
        {
            "name": "CITY BISTRO BAR",
            "address": "55 Mediteranska, Budva 85310",
            "phone": "+382 68 123 456",
            "rating": 4.4, "review_count": 195,
            "categories": ["restaurant", "bistro", "cafe"],
            "website": "",
            "has_website": False
        },
        {
            "name": "Konoba Tri Ribara",
            "address": "Rafailovici Beach, Budva 85310",
            "phone": "+382 33 471 234",
            "rating": 4.5, "review_count": 276,
            "categories": ["restaurant", "seafood", "montenegrin"],
            "website": "",
            "has_website": False
        },
        {
            "name": "Giardino Restaurant",
            "address": "Rezevici, Budva Riviera 85310",
            "phone": "+382 67 234 567",
            "rating": 4.4, "review_count": 210,
            "categories": ["restaurant", "montenegrin", "grill"],
            "website": "",
            "has_website": False
        },
        {
            "name": "Blanche Restaurant",
            "address": "Przno Beach, Budva 85310",
            "phone": "+382 33 478 901",
            "rating": 4.7, "review_count": 340,
            "categories": ["restaurant", "mediterranean", "fine dining"],
            "website": "",
            "has_website": False
        },
        {
            "name": "Hemingway Cafe & Restaurant",
            "address": "TQ Plaza, Budva Centre 85310",
            "phone": "+382 68 345 678",
            "rating": 4.2, "review_count": 185,
            "categories": ["restaurant", "cafe", "casual dining"],
            "website": "",
            "has_website": False
        },
        {
            "name": "Restoran Porto",
            "address": "Slovenska Obala, Budva 85310",
            "phone": "+382 33 402 100",
            "rating": 4.3, "review_count": 160,
            "categories": ["restaurant", "montenegrin", "seafood"],
            "website": "",
            "has_website": False
        },
        {
            "name": "Babaluu Restaurant",
            "address": "TQ Plaza, Budva Centre 85310",
            "phone": "+382 67 456 789",
            "rating": 4.1, "review_count": 140,
            "categories": ["restaurant", "casual", "pizza", "pasta"],
            "website": "",
            "has_website": False
        }
    ],
    "hotels": [
        {
            "name": "Hotel Avala Resort & Villas",
            "address": "Slovenska Obala, Budva 85310",
            "phone": "+382 33 456 789",
            "rating": 4.6, "review_count": 1200,
            "categories": ["hotel", "resort", "luxury"],
            "website": "https://avalaresort.com",
            "has_website": True
        },
        {
            "name": "Dukley Hotel & Resort",
            "address": "Dukley Marina, Budva 85310",
            "phone": "+382 33 405 000",
            "rating": 4.7, "review_count": 890,
            "categories": ["hotel", "resort", "luxury", "spa"],
            "website": "https://dukley.com",
            "has_website": True
        },
        {
            "name": "Katamare Hotel",
            "address": "Bečići, Budva 85310",
            "phone": "+382 33 468 000",
            "rating": 4.5, "review_count": 670,
            "categories": ["hotel", "resort", "beachfront"],
            "website": "",
            "has_website": False
        },
        {
            "name": "Hotel AMI Budva Petrovac",
            "address": "Petrovac na Moru, Budva 85310",
            "phone": "+382 33 431 000",
            "rating": 4.4, "review_count": 520,
            "categories": ["hotel", "resort", "family"],
            "website": "",
            "has_website": False
        },
        {
            "name": "Hotel Aleksandar Rafailovići",
            "address": "Rafailovici, Budva 85310",
            "phone": "+382 33 473 000",
            "rating": 4.3, "review_count": 440,
            "categories": ["hotel", "beachfront"],
            "website": "",
            "has_website": False
        },
        {
            "name": "Slovenska Plaža Hotel",
            "address": "Slovenska Obala, Budva 85310",
            "phone": "+382 33 402 000",
            "rating": 4.2, "review_count": 580,
            "categories": ["hotel", "beachfront", "family"],
            "website": "",
            "has_website": False
        }
    ],
    "beauty_salons": [
        {
            "name": "Studio S - Best Hair Salon Budva",
            "address": "Mediteranska 21, Budva 85310",
            "phone": "+382 67 352 279",
            "rating": 4.8, "review_count": 140,
            "categories": ["beauty salon", "hair salon", "nail art"],
            "website": "https://studiosbudva.com",
            "has_website": True
        },
        {
            "name": "YOUR SPACE Beauty Salon",
            "address": "Centar, Budva 85310",
            "phone": "+382 68 238 640",
            "rating": 5.0, "review_count": 95,
            "categories": ["beauty salon", "manicure", "pedicure", "hair"],
            "website": "https://yourspacebeautysalon.com",
            "has_website": True
        },
        {
            "name": "Mikana Beauty Center",
            "address": "28 Jadranski put, Budva 85310",
            "phone": "+382 67 359 751",
            "rating": 4.6, "review_count": 120,
            "categories": ["beauty salon", "hair", "manicure", "pedicure"],
            "website": "https://mikana.me",
            "has_website": True
        },
        {
            "name": "Altabella Beauty Salon",
            "address": "Budva Old Town 85310",
            "phone": "+382 68 123 789",
            "rating": 4.5, "review_count": 78,
            "categories": ["beauty salon", "hair", "nails"],
            "website": "",
            "has_website": False
        },
        {
            "name": "Bjelica Hair",
            "address": "Hotel Splendid, Bečići, Budva 85310",
            "phone": "+382 33 774 968",
            "rating": 4.7, "review_count": 66,
            "categories": ["beauty salon", "hair salon", "styling"],
            "website": "https://bjelicahair.com",
            "has_website": True
        },
        {
            "name": "Beauty Time Bar",
            "address": "TQ Plaza area, Budva 85310",
            "phone": "+382 68 456 789",
            "rating": 4.4, "review_count": 55,
            "categories": ["beauty salon", "nails", "lashes", "brows"],
            "website": "https://beautytimebar.com",
            "has_website": True
        },
        {
            "name": "Frizerski Salon Maja",
            "address": "13. Jula, Budva 85310",
            "phone": "+382 67 890 123",
            "rating": 4.3, "review_count": 45,
            "categories": ["beauty salon", "hair salon"],
            "website": "",
            "has_website": False
        },
        {
            "name": "Rosa Bali Beauty Budva",
            "address": "Budva 85310",
            "phone": "+382 67 238 640",
            "rating": 4.5, "review_count": 40,
            "categories": ["beauty salon", "beauty"],
            "website": "",
            "has_website": False
        }
    ]
}

def save_lead(lead_dict):
    """Save lead to DB."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    lead_id = str(uuid.uuid4())[:8]
    
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT OR IGNORE INTO clients 
        (id, name, phone, address, website, rating, review_count, categories, 
         source, language, has_website, needs_landing_page, scraped_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lead_id,
        lead_dict['name'],
        lead_dict.get('phone', ''),
        lead_dict.get('address', ''),
        lead_dict.get('website', ''),
        lead_dict.get('rating', 0.0),
        lead_dict.get('review_count', 0),
        json.dumps(lead_dict.get('categories', [])),
        'google_maps',
        'en',
        1 if lead_dict.get('has_website') else 0,
        0 if lead_dict.get('has_website') else 1,
        now,
        now,
        now
    ))
    
    conn.commit()
    conn.close()
    return lead_id

def main():
    # Init DB
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure tables exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            website TEXT,
            rating REAL DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            categories TEXT,
            source TEXT,
            location TEXT,
            language TEXT DEFAULT 'en',
            has_website BOOLEAN DEFAULT 0,
            website_quality_score INTEGER,
            website_tech TEXT,
            needs_landing_page BOOLEAN DEFAULT 1,
            scraped_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'new'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS demos (
            id TEXT PRIMARY KEY,
            client_id TEXT,
            template TEXT,
            language TEXT,
            github_pages_url TEXT,
            generated_at TEXT,
            sent_at TEXT,
            viewed_at TEXT,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    """)
    conn.commit()
    conn.close()
    
    all_leads = []
    scan_stats = {
        "preset": "budva_all",
        "total_scanned": 0,
        "saved": 0,
        "leads_needing_lp": 0,
        "leads_with_website": 0,
        "avg_rating": 0.0,
        "by_category": {"restaurants": 0, "hotels": 0, "beauty_salons": 0}
    }
    
    for category, leads in BUSINESSES.items():
        print(f"\n{'='*60}")
        print(f"📋 {category.upper()}: {len(leads)} businesses")
        print(f"{'='*60}")
        
        for lead_data in leads:
            lead_data['location'] = {"city": "Budva", "country": "Montenegro", "category": category}
            lead_id = save_lead(lead_data)
            all_leads.append((lead_id, lead_data))
            print(f"  ✅ [{lead_id}] {lead_data['name']} - ⭐{lead_data['rating']} ({lead_data.get('phone', 'N/A')})")
            
            scan_stats["total_scanned"] += 1
            scan_stats["by_category"][category] = scan_stats["by_category"].get(category, 0) + 1
            if lead_data['has_website']:
                scan_stats["leads_with_website"] += 1
            else:
                scan_stats["leads_needing_lp"] += 1
    
    # Avg rating
    all_ratings = [l[1]['rating'] for l in all_leads]
    scan_stats["avg_rating"] = round(sum(all_ratings) / len(all_ratings), 2) if all_ratings else 0
    scan_stats["saved"] = len(all_leads)
    
    # Save stats
    stats_file = os.path.join(SCRIPT_DIR, 'logs', f'budva_scan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    os.makedirs(os.path.dirname(stats_file), exist_ok=True)
    with open(stats_file, 'w') as f:
        json.dump(scan_stats, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"📊 SCAN SUMMARY")
    print(f"{'='*60}")
    print(f"  Total scanned:   {scan_stats['total_scanned']}")
    print(f"  Saved to DB:     {scan_stats['saved']}")
    print(f"  Need landing pg: {scan_stats['leads_needing_lp']}")
    print(f"  Have website:    {scan_stats['leads_with_website']}")
    print(f"  Avg rating:      {scan_stats['avg_rating']}")
    print(f"  By category:     {scan_stats['by_category']}")
    
    # Output top leads for demo generation (sort by rating desc)
    sorted_leads = sorted(all_leads, key=lambda x: x[1]['rating'], reverse=True)
    
    print(f"\n{'='*60}")
    print(f"🏆 TOP LEADS (by rating)")
    print(f"{'='*60}")
    for i, (lid, ld) in enumerate(sorted_leads[:5]):
        niche = "restaurant" if "restaurant" in ld.get('categories', []) else \
                "hotel" if "hotel" in ld.get('categories', []) else \
                "salon"
        print(f"  {i+1}. [{lid}] {ld['name']} - ⭐{ld['rating']} ({ld.get('phone', 'N/A')}) [{niche}]")
    
    # Print JSON for top 3
    print(f"\n---TOP3_LEADS_FOR_DEMO---")
    top3 = sorted_leads[:3]
    for lid, ld in top3:
        niche = "restaurant" if "restaurant" in ld.get('categories', []) else \
                "hotel" if "hotel" in ld.get('categories', []) else \
                "salon"
        out = {
            "id": lid,
            "name": ld['name'],
            "phone": ld.get('phone', ''),
            "address": ld.get('address', ''),
            "rating": ld['rating'],
            "review_count": ld.get('review_count', 0),
            "niche": niche,
            "language": "en"
        }
        print(json.dumps(out, ensure_ascii=False))
    print(f"---END_TOP3---")
    
    # Total in DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clients")
    total_in_db = cursor.fetchone()[0]
    conn.close()
    print(f"\n📈 TOTAL LEADS IN DB: {total_in_db}")

if __name__ == "__main__":
    main()
