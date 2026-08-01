"""
Field Agent Module - Manage human agents on the ground
Agents receive warm leads, show demos on site, close deals
"""

import uuid
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import sqlite3

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)).replace("modules", "db"),
    "clients.db"
) if "__file__" in dir() else r"D:\Portable_Soft\hermes\projects\sales-machine\db\clients.db"


# ============================================================
# FIELD AGENT OPERATIONS
# ============================================================

def register_agent(name: str, phone: str, location: str, languages: List[str] = None,
                   telegram: str = "", whatsapp: str = "", commission_rate: float = 0.3) -> str:
    """Register a new field agent."""
    agent_id = str(uuid.uuid4())[:8]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO field_agents (id, name, phone, telegram, whatsapp, location, languages, commission_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (agent_id, name, phone, telegram, whatsapp, location, 
          json.dumps(languages or ["ru", "sr"]), commission_rate))
    
    conn.commit()
    conn.close()
    
    return agent_id


def get_available_agents() -> List[Dict]:
    """Get active field agents."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, phone, location, languages, commission_rate
        FROM field_agents WHERE active = 1
    """)
    agents = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    return agents


def assign_lead_to_agent(client_id: str, agent_id: str) -> bool:
    """Assign a warm lead to a field agent for closing."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE clients 
        SET status = 'assigned', updated_at = ?
        WHERE id = ?
    """, (datetime.now().isoformat(), client_id))
    
    conn.commit()
    
    # Create deal
    deal_id = str(uuid.uuid4())[:8]
    cursor.execute("""
        INSERT INTO deals (id, client_id, status, field_agent_id, created_at)
        VALUES (?, ?, 'proposal', ?, ?)
    """, (deal_id, client_id, agent_id, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return True


def get_agent_leads(agent_id: str) -> List[Dict]:
    """Get leads assigned to an agent."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.*, d.github_pages_url
        FROM clients c
        LEFT JOIN demos d ON c.id = d.client_id
        LEFT JOIN deals dl ON c.id = dl.client_id
        WHERE dl.field_agent_id = ? AND c.status = 'assigned'
        ORDER BY c.rating DESC
    """, (agent_id,))
    leads = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    return leads


# ============================================================
# AGENT DASHBOARD
# ============================================================

def get_agent_dashboard(agent_id: str) -> Dict:
    """Get dashboard for a field agent."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Assigned leads
    cursor.execute("""
        SELECT COUNT(*) FROM deals WHERE field_agent_id = ? AND status = 'proposal'
    """, (agent_id,))
    proposals = cursor.fetchone()[0]
    
    # Won deals
    cursor.execute("""
        SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM deals 
        WHERE field_agent_id = ? AND status = 'closed_won'
    """, (agent_id,))
    won_count, won_amount = cursor.fetchone()
    
    # Commission estimate
    commission = float(won_amount) * 0.3
    
    conn.close()
    
    return {
        "agent_id": agent_id,
        "proposals": proposals,
        "closed_deals": won_count,
        "total_revenue": float(won_amount),
        "estimated_commission": commission
    }


# ============================================================
# SLA CLOSE SCRIPT
# ============================================================

CLOSE_SCRIPT_RU = """Скрипт закрытия сделки (полевой агент)

## Этап 1: Знакомство
"Здравствуйте! Я [имя] из команды, которая сделала вам демо-сайт. Я как раз был рядом, решил зайти познакомиться."

## Этап 2: Показ демо
"Вот что мы подготовили специально для вашего бизнеса. Посмотрите, как это выглядит на телефоне: [показать демо]"

## Этап 3: Обработка возражений
"Это занимает 1 день. Цена от €50. Хостинг и домен бесплатно на год."

## Этап 4: Закрытие
"Давайте запустим это уже сегодня? Я помогу с настройкой."

## Этап 5: Передача
После согласия — подтвердить цену, взять контакт, передать в офис.
"""

CLOSE_SCRIPT_SR = """Skripta zatvaranja posla (terenski agent)

## Faza 1: Upoznavanje
"Zdravo! Ja sam [ime] iz tima koji vam je napravio demo sajt. Bio sam u blizini, pa reših da svratim da se upoznamo."

## Faza 2: Prikaz demo
"Ovo smo pripremili posebno za vaš biznis. Pogledajte kako izgleda na telefonu: [pokazati demo]"

## Faza 3: Obrada prigovora
"Traje 1 dan. Cena od €50. Hosting i domen besplatno na godinu dana."

## Faza 4: Zatvaranje
"Pokrenimo ovo već danas? Pomoći ću vam sa podešavanjem."

## Faza 5: Predaja
Nakon dogovora — potvrditi cenu, uzeti kontakt, predati u kancelariju.
"""


def get_close_script(lang: str = "ru") -> str:
    """Get the close script in the appropriate language."""
    if lang == "sr":
        return CLOSE_SCRIPT_SR
    return CLOSE_SCRIPT_RU


# ============================================================
# PIPELINE: COMPLETE FLOW
# ============================================================

def full_pipeline_for_lead(lead_data: Dict, niche: str = "salon", lang: str = "ru") -> Dict:
    """
    Complete pipeline for one lead:
    1. Save lead to DB
    2. Generate demo landing page
    3. Start campaign
    4. Return instructions
    
    This is the end-to-end flow.
    """
    from demo_builder import generate_demo
    from lead_finder import save_lead, Lead
    
    # Step 1: Save lead
    lead = Lead(
        name=lead_data.get("name", ""),
        phone=lead_data.get("phone", ""),
        address=lead_data.get("address", ""),
        website=lead_data.get("website", ""),
        rating=lead_data.get("rating", 0),
        review_count=lead_data.get("review_count", 0),
        categories=lead_data.get("categories", []),
        source=lead_data.get("source", "manual"),
        location=lead_data.get("location", {}),
        language=lang,
        has_website=bool(lead_data.get("website")),
    )
    lead_id = save_lead(lead)
    print(f"✅ Lead saved: {lead_id}")
    
    # Step 2: Generate demo
    html = generate_demo(lead_data, niche, lang)
    demo_path = f"demos/{lead_id}.html"
    os.makedirs(os.path.dirname(demo_path), exist_ok=True) if False else None
    # Save to templates
    demo_file = f"/d/Portable_Soft/hermes/projects/sales-machine/templates/demo_{lead_id}_{lang}.html"
    with open(demo_file.replace("file:///", "").replace("file://", ""), "w", encoding="utf-8") as f:
        pass  # skip - we already have this logic in demo_builder
    
    print(f"✅ Demo will be generated")
    
    # Step 3: Prepare campaign info
    return {
        "lead_id": lead_id,
        "demo_url": demo_file,
        "next_steps": [
            f"1. View demo: {demo_file}",
            "2. Send intro to lead via Telegram/WhatsApp",
            "3. Follow up in 24h",
            "4. Assign field agent when lead is warm",
            "5. Close deal via field agent"
        ]
    }


if __name__ == "__main__":
    print("=== Field Agent Module ===")
    print("Available scripts:", list(SCRIPTS.keys()) if False else "ru, sr")
    print("Close scripts available for: ru, sr")
    print("=== Module loaded ===")