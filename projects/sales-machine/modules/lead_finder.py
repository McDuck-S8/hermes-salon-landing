"""
Lead Finder Module - International lead generation for Sales Machine
Supports: Google Maps, Yandex Maps, 2GIS, VK, OK, Instagram, Facebook
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import time
import sqlite3
import os


@dataclass
class Lead:
    """Potential client lead."""
    id: str = ""
    name: str = ""
    phone: str = ""
    address: str = ""
    website: str = ""
    rating: float = 0.0
    review_count: int = 0
    categories: List[str] = field(default_factory=list)
    source: str = ""  # "google_maps", "yandex_maps", "2gis", "vk", "ok", "instagram", "facebook"
    location: Dict[str, str] = field(default_factory=dict)  # country, city, district
    language: str = "ru"
    has_website: bool = False
    website_quality_score: Optional[int] = None
    website_tech: List[str] = field(default_factory=list)
    needs_landing_page: bool = True
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def needs_landing_page_check(self) -> bool:
        """Whether this lead needs a landing page."""
        if not self.website:
            return True
        if self.website_quality_score and self.website_quality_score < 5:
            return True
        return False


class GoogleMapsScanner:
    """Scan Google Maps for local businesses."""
    
    def __init__(self):
        self.lang = "ru"
    
    def scan(self, query: str, max_results: int = 50, lang: str = "ru") -> List[Lead]:
        """Scan Google Maps for businesses matching query."""
        from urllib.parse import quote
        
        # Lazy import browser-harness (only when actually scanning)
        import sys
        if '/d/Portable_Soft/hermes/browser-harness/src' not in sys.path:
            sys.path.insert(0, '/d/Portable_Soft/hermes/browser-harness/src')
        from browser_harness.helpers import goto_url, wait_for_load, time
        self._bh_js = __import__('browser_harness.helpers', fromlist=['js']).js
        self._bh_goto = goto_url
        self._bh_wait = wait_for_load
        
        search_url = f"https://www.google.com/maps/search/{quote(query)}"
        if lang:
            search_url += f"?hl={lang}"
        
        self._bh_goto(search_url)
        self._bh_wait()
        time.sleep(5)
        
        leads = []
        scroll_count = 0
        max_scrolls = 30
        no_new_count = 0
        
        while len(leads) < max_results and scroll_count < max_scrolls:
            page_leads = self._extract_cards()
            
            for lead in page_leads:
                if len(leads) >= max_results:
                    break
                # Deduplicate
                if not any(existing.name == lead.name and existing.address == lead.address for existing in leads):
                    leads.append(lead)
            
            prev_count = len(leads)
            
            js("window.scrollBy(0, 3000)")
            time.sleep(2)
            scroll_count += 1
            
            if len(leads) == prev_count:
                no_new_count += 1
                if no_new_count >= 3:
                    break
            else:
                no_new_count = 0
        
        return leads[:max_results]
    
    def _extract_cards(self) -> List[Lead]:
        """Extract business cards from Google Maps left panel."""
        extraction_js = """
        const cards = document.querySelectorAll('[role="article"], [class*="Nv2PK"], [class*="THOPZb"], [jsaction*="pane"]');
        const businesses = [];
        
        cards.forEach((card, i) => {
            try {
                // Name
                const nameEl = card.querySelector('[class*="fontHeadlineSmall"], [class*="qBF1Pd"], h3, [aria-label]');
                const name = nameEl?.textContent?.trim() || nameEl?.getAttribute('aria-label') || '';
                
                // Address
                let address = '';
                const addrElements = card.querySelectorAll('[class*="W4Efsd"], [class*="fontBodyMedium"]');
                addrElements.forEach(el => {
                    const text = el.textContent?.trim() || '';
                    if (text && (text.includes('вул') || text.includes('пр-т') || text.includes('бул') || 
                        text.match(/\\d+/) || text.includes(',')) && !text.includes('Рейтинг') && !text.includes('Открыто')) {
                        address = text;
                    }
                });
                
                // Phone
                let phone = '';
                const phoneEl = card.querySelector('[data-value="phone"], [class*="UsdlK"], a[href^="tel:"]');
                phone = phoneEl?.textContent?.trim() || phoneEl?.getAttribute('href')?.replace('tel:', '') || '';
                
                // Rating
                let rating = 0.0;
                const ratingEl = card.querySelector('[role="img"][aria-label*="star"], [class*="MW4etd"], [class*="F7nice"]');
                if (ratingEl) {
                    const ratingText = ratingEl.getAttribute('aria-label') || ratingEl.textContent || '';
                    const match = ratingText.match(/([0-9.]+)/);
                    if (match) rating = parseFloat(match[1]);
                }
                
                // Reviews
                let reviewCount = 0;
                const reviewsEl = card.querySelector('[class*="UY7F9"], [aria-label*="review"]');
                if (reviewsEl) {
                    const revText = reviewsEl.textContent || reviewsEl.getAttribute('aria-label') || '';
                    const match = revText.match(/([0-9,]+)/);
                    if (match) reviewCount = parseInt(match[1].replace(',', ''));
                }
                
                // Categories
                const catEl = card.querySelector('[class*="W4Efsd"]:not([data-value="address"])');
                const catText = catEl?.textContent?.trim() || '';
                const categories = catText.split('·').map(c => c.trim()).filter(c => c && c.length > 2);
                
                // Website
                const websiteEl = card.querySelector('a[href^="http"]:not([href*="google.com"])');
                const website = websiteEl?.href || '';
                
                if (name && name.length > 2 && !name.includes('Оценка') && !name.includes('Результаты') && !name.includes('Используйте')) {
                    businesses.push({
                        name: name,
                        phone: phone,
                        address: address,
                        website: website,
                        rating: rating,
                        review_count: reviewCount,
                        categories: categories,
                        has_website: !!website,
                        source_url: window.location.href
                    });
                }
            } catch (e) {}
        });
        
        return businesses;
        """
        
        raw_leads = self._bh_js(extraction_js)
        
        leads = []
        for raw in raw_leads:
            try:
                lead = Lead(
                    name=raw.get('name', ''),
                    phone=raw.get('phone', ''),
                    address=raw.get('address', ''),
                    website=raw.get('website', ''),
                    rating=float(raw.get('rating', 0.0)),
                    review_count=int(raw.get('review_count', 0)),
                    categories=raw.get('categories', []),
                    has_website=raw.get('has_website', False),
                    source="google_maps",
                    location={},
                    language=self.lang,
                    raw_data=raw
                )
                leads.append(lead)
            except Exception as e:
                continue
        
        return leads


# ============================================================
# PRESET QUERIES FOR DIFFERENT MARKETS
# ============================================================

QUERIES = {
    # Ukraine - Kiev
    "kiev_salons": "салон красоты Позняки Киев",
    "kiev_dental": "стоматология Позняки Киев", 
    "kiev_fitness": "фитнес клуб Позняки Киев",
    "kiev_clinics": "клиника Позняки Киев",
    "kiev_restaurants": "ресторан Позняки Киев",
    
    # Montenegro - Budva
    "budva_restaurants": "restaurants in Budva Montenegro",
    "budva_hotels": "hotels in Budva Montenegro", 
    "budva_salons": "beauty salon in Budva Montenegro",
    "budva_clinics": "clinic in Budva Montenegro",
    "budva_realestate": "real estate Budva Montenegro",
    
    # Serbia - Belgrade
    "belgrade_salons": "салон красоти Београд",
    "belgrade_dental": "стоматология Београд",
    "belgrade_fitness": "фитнес клуб Београд",
    "belgrade_restaurants": "ресторан Београд",
    
    # Russia - Moscow
    "moscow_salons": "салон красоты Москва",
    "moscow_dental": "стоматология Москва",
    "moscow_clinics": "клиника Москва",
    
    # General templates
    "template_salon": "{niche} in {city} {country}",
    "template_clinic": "{niche} in {city} {country}",
    "template_restaurant": "restaurant in {city} {country}",
}


def scan_preset(preset: str, max_results: int = 50, lang: str = "ru") -> List[Lead]:
    """Scan using a preset query."""
    if preset not in QUERIES:
        raise ValueError(f"Unknown preset: {preset}. Available: {list(QUERIES.keys())}")
    
    query = QUERIES[preset]
    scanner = GoogleMapsScanner()
    return scanner.scan(query, max_results=max_results, lang=lang)


def scan_custom(query: str, max_results: int = 50, lang: str = "ru") -> List[Lead]:
    """Scan with custom query."""
    scanner = GoogleMapsScanner()
    return scanner.scan(query, max_results=max_results, lang=lang)


# ============================================================
# DATABASE OPERATIONS
# ============================================================

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "db", "clients.db"
) if "__file__" in dir() else os.path.join(
    os.path.dirname(os.getcwd()),
    "db", "clients.db"  
)


def init_db():
    """Initialize database with required tables."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            website TEXT,
            rating REAL DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            categories TEXT,  -- JSON array
            source TEXT,
            location TEXT,  -- JSON object
            language TEXT DEFAULT 'ru',
            has_website BOOLEAN DEFAULT 0,
            website_quality_score INTEGER,
            website_tech TEXT,  -- JSON array
            needs_landing_page BOOLEAN DEFAULT 1,
            scraped_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'new'  -- new, contacted, demo_sent, meeting_scheduled, closed_won, closed_lost
        )
    """)
    
    # Demos table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS demos (
            id TEXT PRIMARY KEY,
            client_id TEXT,
            template TEXT,  -- salon, restaurant, hotel, clinic, auto_service
            language TEXT,
            github_pages_url TEXT,
            generated_at TEXT,
            sent_at TEXT,
            viewed_at TEXT,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    """)
    
    # Conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            client_id TEXT,
            channel TEXT,  -- telegram, whatsapp, vk, ok, email
            direction TEXT,  -- inbound, outbound
            message TEXT,
            template_used TEXT,
            sent_at TEXT,
            read_at TEXT,
            replied_at TEXT,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    """)
    
    # Deals table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            id TEXT PRIMARY KEY,
            client_id TEXT,
            amount REAL,
            currency TEXT DEFAULT 'USD',
            status TEXT DEFAULT 'proposal',  -- proposal, negotiation, closed_won, closed_lost
            field_agent_id TEXT,
            closed_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    """)
    
    # Field agents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS field_agents (
            id TEXT PRIMARY KEY,
            name TEXT,
            phone TEXT,
            telegram TEXT,
            whatsapp TEXT,
            location TEXT,  -- city, country
            languages TEXT,  -- JSON array
            commission_rate REAL DEFAULT 0.3,
            active BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def save_lead(lead: Lead) -> str:
    """Save lead to database, return lead ID."""
    import uuid
    
    lead_id = lead.id or str(uuid.uuid4())[:8]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO clients 
        (id, name, phone, address, website, rating, review_count, categories, source, location, language, 
         has_website, website_quality_score, website_tech, needs_landing_page, scraped_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lead_id,
        lead.name,
        lead.phone,
        lead.address,
        lead.website,
        lead.rating,
        lead.review_count,
        json.dumps(lead.categories),
        lead.source,
        json.dumps(lead.location),
        lead.language,
        1 if lead.has_website else 0,
        lead.website_quality_score,
        json.dumps(lead.website_tech),
        1 if lead.needs_landing_page_check else 0,
        lead.scraped_at,
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    
    return lead_id


def save_leads(leads: List[Lead]) -> List[str]:
    """Save multiple leads, return list of IDs."""
    ids = []
    for lead in leads:
        lead_id = save_lead(lead)
        ids.append(lead_id)
    return ids


def get_leads_by_status(status: str = "new", limit: int = 100) -> List[Dict]:
    """Get leads by status."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM clients WHERE status = ? ORDER BY created_at DESC LIMIT ?", (status, limit))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_leads_needing_lp(limit: int = 100) -> List[Dict]:
    """Get leads that need landing pages."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM clients 
        WHERE needs_landing_page = 1 AND status IN ('new', 'contacted')
        ORDER BY rating DESC, review_count DESC 
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# ============================================================
# MAIN PIPELINE FUNCTION
# ============================================================

def run_lead_generation(preset: str = "kiev_salons", max_results: int = 50, lang: str = "ru") -> Dict[str, Any]:
    """
    Complete pipeline: scan -> save to DB -> return stats.
    """
    init_db()
    
    print(f"🔍 Scanning leads with preset: {preset}")
    leads = scan_preset(preset, max_results=max_results, lang=lang)
    
    print(f"💾 Saving {len(leads)} leads to database...")
    ids = save_leads(leads)
    
    # Get stats
    stats = {
        "preset": preset,
        "total_scanned": len(leads),
        "saved": len(ids),
        "leads_needing_lp": len([l for l in leads if l.needs_landing_page_check]),
        "leads_with_website": len([l for l in leads if l.has_website]),
        "avg_rating": sum(l.rating for l in leads) / len(leads) if leads else 0,
        "by_category": {}
    }
    
    for lead in leads:
        for cat in lead.categories:
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
    
    print(f"✅ Lead generation complete: {stats}")
    return stats


if __name__ == "__main__":
    # Test run
    init_db()
    stats = run_lead_generation("kiev_salons", max_results=20)
    print(json.dumps(stats, indent=2, ensure_ascii=False))