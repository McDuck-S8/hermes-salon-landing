"""
Closer Module - Multi-channel communication for Sales Machine
Channels: Telegram, WhatsApp, VK, OK, Email (via Composio)
Delivers demos to leads, tracks responses, hands off warm leads
"""

import os, json, time, uuid, requests
from datetime import datetime
from typing import Dict, Any, List, Optional
import sqlite3

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)).replace("modules", "db"),
    "clients.db"
) if "__file__" in dir() else r"D:\Portable_Soft\hermes\projects\sales-machine\db\clients.db"


# ============================================================
# COMPOSIO INTEGRATION
# ============================================================

COMPOSIO_API = "https://api.composio.dev/api/v1"
COMPOSIO_KEY = os.environ.get("COMPOSIO_API_KEY", "")

# Telegram bot (via Composio WhatsApp/Telegram toolkits or direct Bot API)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def composio_send(channel: str, to: str, message: str, image_url: str = None) -> Dict:
    """Send message via Composio channel integration."""
    headers = {
        "Authorization": f"Bearer {COMPOSIO_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "channel": channel,  # telegram, whatsapp, vk, ok, gmail
        "recipient": to,
        "message": message,
    }
    if image_url:
        payload["image_url"] = image_url
    
    try:
        resp = requests.post(
            f"{COMPOSIO_API}/send",
            json=payload,
            headers=headers,
            timeout=15
        )
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def send_telegram(chat_id: str, text: str, parse_mode: str = "HTML") -> Dict:
    """Send Telegram message via Bot API."""
    if not TELEGRAM_BOT_TOKEN:
        return {"error": "TELEGRAM_BOT_TOKEN not set"}
    
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=15)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def send_telegram_demo(chat_id: str, demo_url: str, business_name: str) -> Dict:
    """Send demo landing page link to lead via Telegram."""
    text = f"""👋 <b>Здравствуйте!</b>

Мы заметили, что у вашего бизнеса <b>{business_name}</b> пока нет сайта.

Мы сделали для вас бесплатный демо-сайт:
🔗 <a href="{demo_url}">Посмотреть демо</a>

Это одностраничный сайт-визитка для вашего бизнеса. 
Вы можете разместить его в интернете уже сегодня.

Хотите обсудить? Мы рядом! 😊"""
    
    return send_telegram(chat_id, text)


# ============================================================
# SALES SCRIPTS
# ============================================================

SCRIPTS = {
    "ru": {
        "intro": "👋 Здравствуйте! Мы заметили, что у вашего бизнеса {name} пока нет сайта. Сделали бесплатное демо: {url}",
        "follow_up_1": "Как вам демо? Можем обсудить детали и запустить сайт уже сегодня.",
        "follow_up_2": "У нас есть готовая страница для вашего бизнеса. Посмотрите, пожалуйста: {url}",
        "objection_price": "Стоимость от €50 за готовый сайт. Хостинг и домен на год — бесплатно.",
        "objection_time": "Весь процесс занимает 1 день. Мы уже сделали основную работу.",
        "objection_need": "Сайт-визитка — это ваша витрина в интернете. Клиенты ищут вас онлайн!",
        "close": "Отлично! Давайте обсудим детали по телефону {phone}. Когда вам удобно?",
        "handoff": "Отличные новости! С вами свяжется наш представитель. Он покажет все возможности лично.",
    },
    "en": {
        "intro": "👋 Hello! We noticed that {name} doesn't have a website yet. We made a free demo: {url}",
        "follow_up_1": "How do you like the demo? We can discuss details and launch the site today.",
        "follow_up_2": "We have a ready-made page for your business. Have a look: {url}",
        "objection_price": "From €50 for a complete site. Free hosting and domain for one year.",
        "objection_time": "The whole process takes 1 day. We've already done most of the work.",
        "objection_need": "A website is your storefront on the internet. Clients are searching for you online!",
        "close": "Great! Let's discuss the details on the phone {phone}. When is convenient for you?",
        "handoff": "Great news! Our representative will contact you to show all the possibilities in person.",
    },
    "sr": {
        "intro": "👋 Zdravo! Primetili smo da {name} još nema sajt. Napravili smo besplatni demo: {url}",
        "follow_up_1": "Kako vam se dopada demo? Možemo dogovoriti detalje i pokrenuti sajt danas.",
        "follow_up_2": "Imamo gotovu stranicu za vaš biznis. Pogledajte: {url}",
        "objection_price": "Od €50 za kompletan sajt. Besplatan hosting i domen na godinu dana.",
        "objection_time": "Ceo proces traje 1 dan. Već smo uradili glavni posao.",
        "objection_need": "Sajt je vaša izlog na internetu. Klijenti vas traže online!",
        "close": "Odlično! Dogovorimo detalje telefonom {phone}. Kada vam odgovara?",
        "handoff": "Odlične vesti! Naš predstavnik će vas kontaktirati da lično pokaže sve mogućnosti.",
    }
}


# ============================================================
# CAMPAIGN EXECUTION
# ============================================================

def run_campaign(lead: Dict, demo_url: str, channel: str = "telegram", lang: str = "ru"):
    """
    Run a full campaign: send demo, follow-up, track response.
    Returns conversation log.
    """
    script = SCRIPTS.get(lang, SCRIPTS["en"])
    name = lead.get("name", "Business")
    phone = lead.get("phone", "+382 XX XXX XXX")
    chat_id = lead.get("telegram_id", "")
    
    if not chat_id and channel == "telegram":
        # Try to find by phone
        chat_id = phone
    
    log = []
    
    # Step 1: Intro with demo
    print(f"📤 Sending intro to {name} via {channel}...")
    intro_msg = script["intro"].format(name=name, url=demo_url)
    
    if channel == "telegram" and chat_id:
        result = send_telegram(chat_id, intro_msg)
        log.append({"step": "intro", "result": result, "sent_at": datetime.now().isoformat()})
        
        if result.get("ok"):
            print(f"✅ Intro sent to {name}")
        else:
            print(f"❌ Failed: {result.get('description', 'Unknown error')}")
    elif channel == "composio":
        result = composio_send("telegram", chat_id, intro_msg)
        log.append({"step": "intro", "result": result, "sent_at": datetime.now().isoformat()})
    else:
        print(f"⚠️ No channel configured for {name} ({channel})")
    
    return log


def find_lead_contact(lead_id: str) -> Dict:
    """Find best contact channel for a lead."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM clients WHERE id = ?", (lead_id,))
    lead = cursor.fetchone()
    conn.close()
    
    if not lead:
        return {"error": "Lead not found"}
    
    lead = dict(lead)
    
    # Determine best channel
    channels = []
    if lead.get("phone"):
        channels.append({"channel": "telegram", "id": lead["phone"], "priority": 1})
        channels.append({"channel": "whatsapp", "id": lead["phone"], "priority": 2})
    if lead.get("website"):
        channels.append({"channel": "email", "id": lead.get("email", ""), "priority": 3})
    
    return {
        "lead": lead,
        "channels": channels,
        "best_channel": channels[0] if channels else None
    }


# ============================================================
# RESPONSE MONITORING
# ============================================================

def check_telegram_messages(offset: int = 0) -> List[Dict]:
    """Check for incoming Telegram messages (replies)."""
    if not TELEGRAM_BOT_TOKEN:
        return []
    
    url = f"{TELEGRAM_API}/getUpdates"
    params = {"offset": offset, "timeout": 5}
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if not data.get("ok"):
            return []
        
        messages = []
        for update in data.get("result", []):
            msg = update.get("message", {})
            messages.append({
                "update_id": update["update_id"],
                "chat_id": str(msg.get("chat", {}).get("id", "")),
                "text": msg.get("text", ""),
                "from": msg.get("from", {}).get("username", ""),
                "date": datetime.fromtimestamp(msg.get("date", 0)).isoformat()
            })
        
        return messages
    except Exception as e:
        print(f"Telegram check error: {e}")
        return []


# ============================================================
# CAMPAIGN MANAGER
# ============================================================

class CampaignManager:
    """Manage multi-step sales campaigns for leads."""
    
    def __init__(self):
        self.db_path = DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Ensure campaigns tracking table exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id TEXT PRIMARY KEY,
                client_id TEXT,
                channel TEXT,
                stage TEXT DEFAULT 'intro',
                lang TEXT DEFAULT 'ru',
                demo_url TEXT,
                status TEXT DEFAULT 'active',
                started_at TEXT,
                last_contact_at TEXT,
                next_contact_at TEXT,
                notes TEXT,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        """)
        conn.commit()
        conn.close()
    
    def start_campaign(self, client_id: str, demo_url: str, channel: str = "telegram", lang: str = "ru") -> str:
        """Start a new campaign for a lead."""
        campaign_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO campaigns (id, client_id, channel, stage, lang, demo_url, status, started_at, last_contact_at)
            VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?)
        """, (campaign_id, client_id, channel, 'intro', lang, demo_url, now, now))
        conn.commit()
        conn.close()
        
        return campaign_id
    
    def get_active_campaigns(self) -> List[Dict]:
        """Get all active campaigns."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, cl.name as client_name, cl.phone as client_phone
            FROM campaigns c
            LEFT JOIN clients cl ON c.client_id = cl.id
            WHERE c.status = 'active'
            ORDER BY c.started_at DESC
        """)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
    
    def advance_stage(self, campaign_id: str, new_stage: str):
        """Advance campaign to next stage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE campaigns 
            SET stage = ?, last_contact_at = ? 
            WHERE id = ?
        """, (new_stage, datetime.now().isoformat(), campaign_id))
        conn.commit()
        conn.close()


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_outreach(client_id: str, demo_url: str, channel: str = "telegram", lang: str = "ru") -> Dict:
    """
    Complete outreach pipeline for one lead.
    1. Find best contact channel
    2. Send intro with demo URL
    3. Start campaign tracking
    4. Return result
    """
    contact_info = find_lead_contact(client_id)
    if "error" in contact_info:
        return {"error": contact_info["error"]}
    
    lead = contact_info["lead"]
    
    # Start campaign
    mgr = CampaignManager()
    campaign_id = mgr.start_campaign(client_id, demo_url, channel, lang)
    
    # Send intro
    log = run_campaign(lead, demo_url, channel, lang)
    
    # Update client status
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE clients SET status = 'contacted', updated_at = ? WHERE id = ?", 
                   (datetime.now().isoformat(), client_id))
    conn.commit()
    conn.close()
    
    return {
        "campaign_id": campaign_id,
        "client_id": client_id,
        "channel": channel,
        "lang": lang,
        "demo_url": demo_url,
        "log": log,
        "status": "outreach_started"
    }


def process_incoming() -> List[Dict]:
    """Process incoming messages and route to appropriate campaign."""
    messages = check_telegram_messages()
    
    responses = []
    for msg in messages:
        chat_id = msg["chat_id"]
        text = msg.get("text", "").lower()
        
        # Categorize response
        if any(w in text for w in ["да", "ok", "yes", "хорошо", "sea", "da", "го", "let's", "интерес"]):
            sentiment = "positive"
        elif any(w in text for w in ["нет", "no", "не", "not", "дорог", "nije", "ne zanima"]):
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        responses.append({
            "chat_id": chat_id,
            "text": msg["text"],
            "sentiment": sentiment,
            "timestamp": msg["date"]
        })
    
    return responses


if __name__ == "__main__":
    # Test
    test_lead = {
        "name": "Test Business",
        "phone": "+38267123456",
        "telegram_id": "+38267123456",
        "rating": 4.5,
    }
    
    print("Testing Telegram send (dry-run):")
    script = SCRIPTS["ru"]
    intro = script["intro"].format(name=test_lead["name"], url="https://demo.example.com")
    print(f"  Would send: {intro}")
    
    print("\n=== Closer module loaded successfully ===")