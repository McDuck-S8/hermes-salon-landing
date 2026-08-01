"""
Salon Bot — Database Module (2026)
Backend Architect: connection pool, indexed schema, migration support.
"""

import aiosqlite
import os
import json
from pathlib import Path
from datetime import datetime, date, time, timedelta
from dataclasses import dataclass

DB_PATH = None  # set in get_db()


# ══════════════════════════════════════════════════════════
# SCHEMA v2 — 2026 edition
# ══════════════════════════════════════════════════════════

SCHEMA_V2 = """
-- Salons (multi-salon ready)
CREATE TABLE IF NOT EXISTS salons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT DEFAULT '',
    address TEXT DEFAULT '',
    tg_channel TEXT DEFAULT '',
    instagram TEXT DEFAULT '',
    work_start_hour INTEGER DEFAULT 9,
    work_end_hour INTEGER DEFAULT 20,
    slot_duration INTEGER DEFAULT 30,
    timezone TEXT DEFAULT 'Europe/Simferopol',
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Services
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salon_id INTEGER NOT NULL DEFAULT 1,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    duration_min INTEGER DEFAULT 60,
    price INTEGER DEFAULT 0,
    category TEXT DEFAULT '',
    color TEXT DEFAULT '#6C5CE7',
    emoji TEXT DEFAULT '💇',
    is_active INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (salon_id) REFERENCES salons(id)
);

-- Masters
CREATE TABLE IF NOT EXISTS masters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salon_id INTEGER NOT NULL DEFAULT 1,
    name TEXT NOT NULL,
    phone TEXT DEFAULT '',
    photo_url TEXT DEFAULT '',
    bio TEXT DEFAULT '',
    is_active INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (salon_id) REFERENCES salons(id)
);

-- Master-Service link
CREATE TABLE IF NOT EXISTS master_services (
    master_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    PRIMARY KEY (master_id, service_id),
    FOREIGN KEY (master_id) REFERENCES masters(id),
    FOREIGN KEY (service_id) REFERENCES services(id)
);

-- Clients
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_user_id INTEGER UNIQUE NOT NULL,
    name TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    birth_date TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    referral_source TEXT DEFAULT '',
    total_visits INTEGER DEFAULT 0,
    total_spent INTEGER DEFAULT 0,
    last_visit_date TEXT DEFAULT '',
    is_blocked INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Bookings
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salon_id INTEGER NOT NULL DEFAULT 1,
    client_id INTEGER NOT NULL,
    master_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    booking_date TEXT NOT NULL,
    time_slot TEXT NOT NULL,
    duration_min INTEGER DEFAULT 60,
    price INTEGER DEFAULT 0,
    status TEXT DEFAULT 'confirmed',  -- confirmed, cancelled, completed, no_show
    reminder_sent INTEGER DEFAULT 0,
    payment_status TEXT DEFAULT 'none', -- none, pending, paid, refunded
    payment_amount INTEGER DEFAULT 0,
    payment_id TEXT DEFAULT '',
    cancel_reason TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (salon_id) REFERENCES salons(id),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (master_id) REFERENCES masters(id),
    FOREIGN KEY (service_id) REFERENCES services(id)
);

-- Reviews
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    master_id INTEGER NOT NULL,
    rating INTEGER DEFAULT 5 CHECK(rating BETWEEN 1 AND 5),
    text TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (booking_id) REFERENCES bookings(id),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (master_id) REFERENCES masters(id)
);

-- Admin users
CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salon_id INTEGER NOT NULL DEFAULT 1,
    tg_user_id INTEGER UNIQUE NOT NULL,
    role TEXT DEFAULT 'admin',  -- admin, superadmin
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (salon_id) REFERENCES salons(id)
);

-- Master Telegram links
CREATE TABLE IF NOT EXISTS master_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    master_id INTEGER NOT NULL,
    tg_user_id INTEGER UNIQUE NOT NULL DEFAULT 0,
    access_code TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (master_id) REFERENCES masters(id)
);

-- Notifications log
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    type TEXT NOT NULL,  -- reminder, confirm, cancel, review_request
    channel TEXT DEFAULT 'telegram',
    status TEXT DEFAULT 'pending',  -- pending, sent, failed
    sent_at TEXT DEFAULT '',
    error_text TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT (datetime('now'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(booking_date);
CREATE INDEX IF NOT EXISTS idx_bookings_master_date ON bookings(master_id, booking_date);
CREATE INDEX IF NOT EXISTS idx_bookings_client ON bookings(client_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_reminder ON bookings(reminder_sent, booking_date);
CREATE INDEX IF NOT EXISTS idx_clients_tg ON clients(tg_user_id);
CREATE INDEX IF NOT EXISTS idx_services_salon ON services(salon_id);
CREATE INDEX IF NOT EXISTS idx_masters_salon ON masters(salon_id);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
CREATE INDEX IF NOT EXISTS idx_reviews_master ON reviews(master_id);
"""


# ══════════════════════════════════════════════════════════
# CORE CONNECTION
# ══════════════════════════════════════════════════════════

_db_pool = {}  # simple cache per path


async def get_db() -> aiosqlite.Connection:
    """Get a connection, creating schema on first use."""
    global DB_PATH
    if DB_PATH is None:
        # Default path relative to this file
        base = Path(__file__).parent
        DB_PATH = str(base / "data" / "salon.db")

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row

    # Enable WAL mode for concurrent reads
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")

    # Apply schema if needed
    has_schema = await db.execute_fetchall(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
    )
    if not has_schema:
        await db.executescript(SCHEMA_V2)
        await db.execute("INSERT OR IGNORE INTO schema_version (version) VALUES (2)")
        await db.commit()

    return db


# ══════════════════════════════════════════════════════════
# CLIENTS
# ══════════════════════════════════════════════════════════

async def get_or_create_client(tg_user_id: int, name: str = "") -> dict:
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT * FROM clients WHERE tg_user_id=?", (tg_user_id,)
        )
        if rows:
            return dict(rows[0])
        await db.execute(
            "INSERT INTO clients (tg_user_id, name) VALUES (?, ?)",
            (tg_user_id, name),
        )
        await db.commit()
        rows = await db.execute_fetchall(
            "SELECT * FROM clients WHERE tg_user_id=?", (tg_user_id,)
        )
        return dict(rows[0])
    finally:
        await db.close()


async def update_client(tg_user_id: int, **kwargs):
    db = await get_db()
    try:
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [tg_user_id]
        await db.execute(
            f"UPDATE clients SET {sets} WHERE tg_user_id=?", vals
        )
        await db.commit()
    finally:
        await db.close()


# ══════════════════════════════════════════════════════════
# SERVICES
# ══════════════════════════════════════════════════════════

async def get_services(active_only=True, salon_id=1):
    db = await get_db()
    try:
        q = "SELECT * FROM services WHERE salon_id=?" + (" AND is_active=1" if active_only else "")
        q += " ORDER BY sort_order, name"
        rows = await db.execute_fetchall(q, (salon_id,))
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def get_service(service_id: int):
    db = await get_db()
    try:
        rows = await db.execute_fetchall("SELECT * FROM services WHERE id=?", (service_id,))
        return dict(rows[0]) if rows else None
    finally:
        await db.close()


async def add_service(name: str, duration: int, price: int, category="", emoji="💇", color="#6C5CE7", salon_id=1):
    db = await get_db()
    try:
        cur = await db.execute(
            "INSERT INTO services (salon_id, name, duration_min, price, category, emoji, color) VALUES (?,?,?,?,?,?,?)",
            (salon_id, name, duration, price, category, emoji, color),
        )
        await db.commit()
        return cur.lastrowid
    finally:
        await db.close()


async def toggle_service(service_id: int):
    db = await get_db()
    try:
        await db.execute("UPDATE services SET is_active = 1 - is_active WHERE id=?", (service_id,))
        await db.commit()
    finally:
        await db.close()


# ══════════════════════════════════════════════════════════
# MASTERS
# ══════════════════════════════════════════════════════════

async def get_masters(active_only=True, salon_id=1):
    db = await get_db()
    try:
        q = "SELECT * FROM masters WHERE salon_id=?" + (" AND is_active=1" if active_only else "")
        q += " ORDER BY sort_order, name"
        rows = await db.execute_fetchall(q, (salon_id,))
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def get_master(master_id: int):
    db = await get_db()
    try:
        rows = await db.execute_fetchall("SELECT * FROM masters WHERE id=?", (master_id,))
        return dict(rows[0]) if rows else None
    finally:
        await db.close()


async def add_master(name: str, phone="", salon_id=1):
    db = await get_db()
    try:
        cur = await db.execute(
            "INSERT INTO masters (salon_id, name, phone) VALUES (?,?,?)",
            (salon_id, name, phone),
        )
        await db.commit()
        return cur.lastrowid
    finally:
        await db.close()


async def toggle_master(master_id: int):
    db = await get_db()
    try:
        await db.execute("UPDATE masters SET is_active = 1 - is_active WHERE id=?", (master_id,))
        await db.commit()
    finally:
        await db.close()


async def get_master_services(master_id: int):
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            """SELECT s.* FROM services s
               JOIN master_services ms ON s.id = ms.service_id
               WHERE ms.master_id=? AND s.is_active=1 ORDER BY s.sort_order""",
            (master_id,),
        )
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def set_master_services(master_id: int, service_ids: list):
    db = await get_db()
    try:
        await db.execute("DELETE FROM master_services WHERE master_id=?", (master_id,))
        for sid in service_ids:
            await db.execute("INSERT INTO master_services (master_id, service_id) VALUES (?,?)", (master_id, sid))
        await db.commit()
    finally:
        await db.close()


# ══════════════════════════════════════════════════════════
# BOOKINGS
# ══════════════════════════════════════════════════════════

async def get_available_slots(master_id: int, booking_date: str, duration: int) -> list:
    """Get free time slots for a master on a given date."""
    db = await get_db()
    try:
        # Get master's schedule (default: 9-20)
        mrow = await db.execute_fetchall("SELECT * FROM masters WHERE id=?", (master_id,))
        if not mrow:
            return []
        # Get booked slots
        rows = await db.execute_fetchall(
            "SELECT time_slot, duration_min FROM bookings WHERE master_id=? AND booking_date=? AND status='confirmed'",
            (master_id, booking_date),
        )
        booked = [(r["time_slot"], r["duration_min"]) for r in rows]

        # Generate all slots
        slots = []
        start_hour = 9
        end_hour = 20
        for h in range(start_hour, end_hour):
            for m in [0, 30]:
                t = f"{h:02d}:{m:02d}"
                t_sec = h * 3600 + m * 60
                end_sec = t_sec + duration * 60

                # Check if overlaps with any booked slot
                conflict = False
                for bt, bd in booked:
                    bh, bmin = map(int, bt.split(":"))
                    b_start = bh * 3600 + bmin * 60
                    b_end = b_start + bd * 60
                    if t_sec < b_end and end_sec > b_start:
                        conflict = True
                        break

                if not conflict:
                    slots.append(t)
        return slots
    finally:
        await db.close()


async def create_booking(client_id: int, master_id: int, service_id: int,
                         booking_date: str, time_slot: str, duration: int, price: int) -> int | None:
    db = await get_db()
    try:
        # Check conflict
        rows = await db.execute_fetchall(
            """SELECT id FROM bookings
               WHERE master_id=? AND booking_date=? AND time_slot=? AND status='confirmed'""",
            (master_id, booking_date, time_slot),
        )
        if rows:
            return None

        cur = await db.execute(
            """INSERT INTO bookings (client_id, master_id, service_id, booking_date, time_slot, duration_min, price)
               VALUES (?,?,?,?,?,?,?)""",
            (client_id, master_id, service_id, booking_date, time_slot, duration, price),
        )
        await db.commit()

        # Update client stats
        await db.execute(
            "UPDATE clients SET total_visits=total_visits+1, last_visit_date=? WHERE id=?",
            (booking_date, client_id),
        )
        await db.commit()

        return cur.lastrowid
    finally:
        await db.close()


async def cancel_booking(booking_id: int, reason=""):
    db = await get_db()
    try:
        await db.execute(
            "UPDATE bookings SET status='cancelled', cancel_reason=?, updated_at=datetime('now') WHERE id=?",
            (reason, booking_id),
        )
        await db.commit()
    finally:
        await db.close()


async def get_booking(booking_id: int) -> dict | None:
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            """SELECT b.*, m.name as master_name, s.name as service_name, s.price as svc_price,
                      c.name as client_name, c.tg_user_id as client_tg, c.phone as client_phone
               FROM bookings b
               JOIN masters m ON b.master_id = m.id
               JOIN services s ON b.service_id = s.id
               JOIN clients c ON b.client_id = c.id
               WHERE b.id=?""",
            (booking_id,),
        )
        return dict(rows[0]) if rows else None
    finally:
        await db.close()


async def get_client_bookings(client_id: int, limit=20) -> list:
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            """SELECT b.*, m.name as master_name, s.name as service_name, s.emoji, s.color
               FROM bookings b
               JOIN masters m ON b.master_id = m.id
               JOIN services s ON b.service_id = s.id
               WHERE b.client_id=? ORDER BY b.booking_date DESC, b.time_slot DESC LIMIT ?""",
            (client_id, limit),
        )
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def get_master_bookings(master_id: int, booking_date: str = None) -> list:
    db = await get_db()
    try:
        if booking_date:
            rows = await db.execute_fetchall(
                """SELECT b.*, c.name as client_name, c.phone as client_phone, s.name as service_name
                   FROM bookings b
                   JOIN clients c ON b.client_id = c.id
                   JOIN services s ON b.service_id = s.id
                   WHERE b.master_id=? AND b.booking_date=? AND b.status='confirmed'
                   ORDER BY b.time_slot""",
                (master_id, booking_date),
            )
        else:
            rows = await db.execute_fetchall(
                """SELECT b.*, c.name as client_name, s.name as service_name
                   FROM bookings b
                   JOIN clients c ON b.client_id = c.id
                   JOIN services s ON b.service_id = s.id
                   WHERE b.master_id=? AND b.status='confirmed'
                   ORDER BY b.booking_date, b.time_slot""",
                (master_id,),
            )
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def get_todays_bookings() -> list:
    db = await get_db()
    try:
        today = date.today().isoformat()
        rows = await db.execute_fetchall(
            """SELECT b.*, m.name as master_name, s.name as service_name,
                      c.name as client_name, c.phone as client_phone
               FROM bookings b
               JOIN masters m ON b.master_id = m.id
               JOIN services s ON b.service_id = s.id
               JOIN clients c ON b.client_id = c.id
               WHERE b.booking_date=? AND b.status='confirmed'
               ORDER BY b.time_slot""",
            (today,),
        )
        return [dict(r) for r in rows]
    finally:
        await db.close()


# ══════════════════════════════════════════════════════════
# REVIEWS
# ══════════════════════════════════════════════════════════

async def add_review(booking_id: int, client_id: int, master_id: int, rating: int, text=""):
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO reviews (booking_id, client_id, master_id, rating, text) VALUES (?,?,?,?,?)",
            (booking_id, client_id, master_id, rating, text),
        )
        await db.commit()
    finally:
        await db.close()


async def get_master_rating(master_id: int) -> tuple:
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT AVG(rating) as avg_r, COUNT(*) as cnt FROM reviews WHERE master_id=?",
            (master_id,),
        )
        if rows and rows[0]["cnt"] > 0:
            return round(rows[0]["avg_r"], 1), rows[0]["cnt"]
        return 0, 0
    finally:
        await db.close()


# ══════════════════════════════════════════════════════════
# ADMIN / MASTER LINKS
# ══════════════════════════════════════════════════════════

async def is_admin(tg_user_id: int) -> bool:
    from config import config
    if tg_user_id == config.SUPERADMIN_ID:
        return True
    db = await get_db()
    try:
        rows = await db.execute_fetchall("SELECT id FROM admin_users WHERE tg_user_id=?", (tg_user_id,))
        return len(rows) > 0
    finally:
        await db.close()


async def add_admin(tg_user_id: int):
    db = await get_db()
    try:
        await db.execute("INSERT OR IGNORE INTO admin_users (tg_user_id) VALUES (?)", (tg_user_id,))
        await db.commit()
    finally:
        await db.close()


async def get_master_by_tg(tg_user_id: int) -> dict | None:
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            """SELECT m.* FROM masters m
               JOIN master_users mu ON m.id = mu.master_id
               WHERE mu.tg_user_id=?""",
            (tg_user_id,),
        )
        return dict(rows[0]) if rows else None
    finally:
        await db.close()


async def generate_master_code(master_id: int) -> str:
    import random, string
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    db = await get_db()
    try:
        await db.execute(
            "INSERT OR REPLACE INTO master_users (master_id, tg_user_id, access_code) VALUES (?,0,?)",
            (master_id, code),
        )
        await db.commit()
        return code
    finally:
        await db.close()


async def link_master_tg(master_id: int, tg_user_id: int, code: str) -> bool:
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT id FROM master_users WHERE master_id=? AND access_code=?",
            (master_id, code),
        )
        if not rows:
            return False
        await db.execute(
            "UPDATE master_users SET tg_user_id=? WHERE master_id=? AND access_code=?",
            (tg_user_id, master_id, code),
        )
        await db.commit()
        return True
    finally:
        await db.close()


# ══════════════════════════════════════════════════════════
# STATISTICS
# ══════════════════════════════════════════════════════════

async def get_stats():
    db = await get_db()
    try:
        today = date.today().isoformat()
        month_start = date.today().replace(day=1).isoformat()
        now_dt = datetime.now()
        week_ago = (now_dt - timedelta(days=7)).isoformat()

        b_today = await db.execute_fetchall(
            "SELECT COUNT(*) as c FROM bookings WHERE booking_date=? AND status='confirmed'", (today,)
        )
        b_month = await db.execute_fetchall(
            "SELECT COUNT(*) as c FROM bookings WHERE booking_date>=? AND status='confirmed'", (month_start,)
        )
        rev_month = await db.execute_fetchall(
            """SELECT COALESCE(SUM(price),0) as total FROM bookings
               WHERE booking_date>=? AND status='completed'""",
            (month_start,),
        )
        clients_total = await db.execute_fetchall("SELECT COUNT(*) as c FROM clients")
        masters_active = await db.execute_fetchall("SELECT COUNT(*) as c FROM masters WHERE is_active=1")
        bookings_week = await db.execute_fetchall(
            "SELECT COUNT(*) as c FROM bookings WHERE created_at>=? AND status='confirmed'",
            (week_ago,),
        )
        new_clients = await db.execute_fetchall(
            "SELECT COUNT(*) as c FROM clients WHERE created_at>=?", (week_ago,)
        )

        return {
            "bookings_today": b_today[0]["c"],
            "bookings_month": b_month[0]["c"],
            "revenue_month": rev_month[0]["total"],
            "clients_total": clients_total[0]["c"],
            "masters_active": masters_active[0]["c"],
            "bookings_week": bookings_week[0]["c"],
            "new_clients_week": new_clients[0]["c"],
        }
    finally:
        await db.close()


# ══════════════════════════════════════════════════════════
# NOTIFICATIONS LOG
# ══════════════════════════════════════════════════════════

async def log_notification(booking_id: int, ntype: str, status="pending"):
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO notifications (booking_id, type, status) VALUES (?,?,?)",
            (booking_id, ntype, status),
        )
        await db.commit()
    finally:
        await db.close()


# ══════════════════════════════════════════════════════════
# SEED
# ══════════════════════════════════════════════════════════

async def seed_demo():
    db = await get_db()
    try:
        existing = await db.execute_fetchall("SELECT COUNT(*) as c FROM services")
        if existing[0]["c"] > 0:
            return

        # Ensure default salon exists
        salons = await db.execute_fetchall("SELECT id FROM salons LIMIT 1")
        if not salons:
            await db.execute(
                "INSERT INTO salons (name, phone, address) VALUES (?,?,?)",
                ("Салон Красоты", "+7 (978) 000-00-00", "г. Симферополь"),
            )

        services_data = [
            ("💇", "Женская стрижка", 60, 1500, "#6C5CE7", "стрижки"),
            ("✂️", "Мужская стрижка", 45, 800, "#00B894", "стрижки"),
            ("🎨", "Окрашивание", 120, 3000, "#E17055", "окрашивание"),
            ("💅", "Маникюр", 90, 1200, "#FD79A8", "ногти"),
            ("🦶", "Педикюр", 90, 1500, "#A29BFE", "ногти"),
            ("💪", "Наращивание ногтей", 120, 2500, "#FDCB6E", "ногти"),
            ("🌸", "Укладка", 60, 1000, "#00CEC9", "укладка"),
            ("✨", "Ламинирование бровей", 45, 1500, "#E17055", "брови"),
        ]
        for emoji, name, dur, price, color, cat in services_data:
            await db.execute(
                "INSERT INTO services (name, duration_min, price, category, emoji, color) VALUES (?,?,?,?,?,?)",
                (name, dur, price, cat, emoji, color),
            )

        masters_data = [
            ("Анна", "+7 (978) 111-11-11"),
            ("Елена", "+7 (978) 222-22-22"),
            ("Мария", "+7 (978) 333-33-33"),
        ]
        for name, phone in masters_data:
            cur = await db.execute("INSERT INTO masters (name, phone) VALUES (?,?)", (name, phone))

        # Link masters to all services
        m_ids = [r["id"] for r in await db.execute_fetchall("SELECT id FROM masters")]
        s_ids = [r["id"] for r in await db.execute_fetchall("SELECT id FROM services")]
        for mid in m_ids:
            for sid in s_ids:
                await db.execute("INSERT OR IGNORE INTO master_services (master_id, service_id) VALUES (?,?)", (mid, sid))

        await db.commit()
    finally:
        await db.close()
