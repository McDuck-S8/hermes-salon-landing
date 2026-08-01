"""Database layer — SQLite via aiosqlite."""
import aiosqlite
import os
from datetime import datetime, date, time

DB_PATH = os.path.join(os.path.dirname(__file__), "salon.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    duration_min INTEGER DEFAULT 60,
    price INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS masters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT DEFAULT "",
    active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS master_specializations (
    master_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    PRIMARY KEY (master_id, service_id),
    FOREIGN KEY (master_id) REFERENCES masters(id),
    FOREIGN KEY (service_id) REFERENCES services(id)
);

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_user_id INTEGER UNIQUE NOT NULL,
    name TEXT DEFAULT "",
    phone TEXT DEFAULT "",
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    master_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    booking_date TEXT NOT NULL,
    time_slot TEXT NOT NULL,
    status TEXT DEFAULT "confirmed",
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (master_id) REFERENCES masters(id),
    FOREIGN KEY (service_id) REFERENCES services(id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    master_id INTEGER NOT NULL,
    rating INTEGER DEFAULT 5,
    text TEXT DEFAULT "",
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);

CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_user_id INTEGER UNIQUE NOT NULL,
    role TEXT DEFAULT "admin"
);

CREATE TABLE IF NOT EXISTS master_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    master_id INTEGER NOT NULL,
    tg_user_id INTEGER UNIQUE NOT NULL,
    access_code TEXT NOT NULL,
    FOREIGN KEY (master_id) REFERENCES masters(id)
);
"""


async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.executescript(SCHEMA)
    return db


# ── Clients ──────────────────────────────────────────────
async def get_or_create_client(tg_user_id: int, name: str = ""):
    db = await get_db()
    try:
        row = await db.execute_fetchall(
            "SELECT * FROM clients WHERE tg_user_id=?", (tg_user_id,)
        )
        if row:
            return dict(row[0])
        await db.execute(
            "INSERT INTO clients (tg_user_id, name) VALUES (?, ?)",
            (tg_user_id, name),
        )
        await db.commit()
        row = await db.execute_fetchall(
            "SELECT * FROM clients WHERE tg_user_id=?", (tg_user_id,)
        )
        return dict(row[0])
    finally:
        await db.close()


async def update_client_phone(tg_user_id: int, phone: str):
    db = await get_db()
    try:
        await db.execute(
            "UPDATE clients SET phone=? WHERE tg_user_id=?", (phone, tg_user_id)
        )
        await db.commit()
    finally:
        await db.close()


# ── Services ─────────────────────────────────────────────
async def get_services(active_only=True):
    db = await get_db()
    try:
        q = "SELECT * FROM services" + (" WHERE active=1" if active_only else "")
        rows = await db.execute_fetchall(q)
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def add_service(name: str, duration: int, price: int):
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO services (name, duration_min, price) VALUES (?,?,?)",
            (name, duration, price),
        )
        await db.commit()
    finally:
        await db.close()


async def toggle_service(service_id: int):
    db = await get_db()
    try:
        await db.execute(
            "UPDATE services SET active = 1 - active WHERE id=?", (service_id,)
        )
        await db.commit()
    finally:
        await db.close()


# ── Masters ──────────────────────────────────────────────
async def get_masters(active_only=True):
    db = await get_db()
    try:
        q = "SELECT * FROM masters" + (" WHERE active=1" if active_only else "")
        rows = await db.execute_fetchall(q)
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def add_master(name: str, phone: str = ""):
    db = await get_db()
    try:
        cur = await db.execute(
            "INSERT INTO masters (name, phone) VALUES (?,?)", (name, phone)
        )
        await db.commit()
        return cur.lastrowid
    finally:
        await db.close()


async def get_master_services(master_id: int):
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            """SELECT s.* FROM services s
               JOIN master_specializations ms ON s.id = ms.service_id
               WHERE ms.master_id=? AND s.active=1""",
            (master_id,),
        )
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def set_master_services(master_id: int, service_ids: list):
    db = await get_db()
    try:
        await db.execute(
            "DELETE FROM master_specializations WHERE master_id=?", (master_id,)
        )
        for sid in service_ids:
            await db.execute(
                "INSERT INTO master_specializations (master_id, service_id) VALUES (?,?)",
                (master_id, sid),
            )
        await db.commit()
    finally:
        await db.close()


async def get_master_by_tg(tg_user_id: int):
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


async def link_master_tg(master_id: int, tg_user_id: int, code: str):
    db = await get_db()
    try:
        await db.execute(
            "INSERT OR REPLACE INTO master_users (master_id, tg_user_id, access_code) VALUES (?,?,?)",
            (master_id, tg_user_id, code),
        )
        await db.commit()
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


# ── Bookings ─────────────────────────────────────────────
async def create_booking(client_id, master_id, service_id, booking_date, time_slot):
    db = await get_db()
    try:
        # Check no conflict
        rows = await db.execute_fetchall(
            """SELECT id FROM bookings
               WHERE master_id=? AND booking_date=? AND time_slot=? AND status='confirmed'""",
            (master_id, booking_date, time_slot),
        )
        if rows:
            return None  # conflict
        cur = await db.execute(
            """INSERT INTO bookings (client_id, master_id, service_id, booking_date, time_slot)
               VALUES (?,?,?,?,?)""",
            (client_id, master_id, service_id, booking_date, time_slot),
        )
        await db.commit()
        return cur.lastrowid
    finally:
        await db.close()


async def get_booked_slots(master_id: int, booking_date: str):
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            """SELECT time_slot FROM bookings
               WHERE master_id=? AND booking_date=? AND status='confirmed'""",
            (master_id, booking_date),
        )
        return [r["time_slot"] for r in rows]
    finally:
        await db.close()


async def get_client_bookings(client_id: int):
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            """SELECT b.*, m.name as master_name, s.name as service_name, s.price
               FROM bookings b
               JOIN masters m ON b.master_id = m.id
               JOIN services s ON b.service_id = s.id
               WHERE b.client_id=? ORDER BY b.booking_date DESC, b.time_slot DESC""",
            (client_id,),
        )
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def get_master_bookings(master_id: int, booking_date: str = None):
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


async def cancel_booking(booking_id: int):
    db = await get_db()
    try:
        await db.execute(
            "UPDATE bookings SET status='cancelled' WHERE id=?", (booking_id,)
        )
        await db.commit()
    finally:
        await db.close()


async def get_booking(booking_id: int):
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            """SELECT b.*, m.name as master_name, s.name as service_name, s.price,
                      c.name as client_name, c.tg_user_id as client_tg
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


# ── Reviews ──────────────────────────────────────────────
async def add_review(booking_id, client_id, master_id, rating, text=""):
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO reviews (booking_id, client_id, master_id, rating, text) VALUES (?,?,?,?,?)",
            (booking_id, client_id, master_id, rating, text),
        )
        await db.commit()
    finally:
        await db.close()


async def get_master_rating(master_id: int):
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


# ── Admin ────────────────────────────────────────────────
async def is_admin(tg_user_id: int) -> bool:
    from config import SUPERADMIN_ID
    if tg_user_id == SUPERADMIN_ID:
        return True
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT id FROM admin_users WHERE tg_user_id=?", (tg_user_id,)
        )
        return len(rows) > 0
    finally:
        await db.close()


async def add_admin(tg_user_id: int):
    db = await get_db()
    try:
        await db.execute(
            "INSERT OR IGNORE INTO admin_users (tg_user_id) VALUES (?)", (tg_user_id,)
        )
        await db.commit()
    finally:
        await db.close()


async def get_all_bookings_today():
    today = date.today().isoformat()
    db = await get_db()
    try:
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


async def get_all_bookings_range(date_from: str, date_to: str):
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            """SELECT b.*, m.name as master_name, s.name as service_name,
                      c.name as client_name, s.price
               FROM bookings b
               JOIN masters m ON b.master_id = m.id
               JOIN services s ON b.service_id = s.id
               JOIN clients c ON b.client_id = c.id
               WHERE b.booking_date BETWEEN ? AND ? AND b.status='confirmed'
               ORDER BY b.booking_date, b.time_slot""",
            (date_from, date_to),
        )
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def get_stats():
    db = await get_db()
    try:
        today = date.today().isoformat()
        month_start = date.today().replace(day=1).isoformat()

        bookings_today = await db.execute_fetchall(
            "SELECT COUNT(*) as c FROM bookings WHERE booking_date=? AND status='confirmed'",
            (today,),
        )
        bookings_month = await db.execute_fetchall(
            "SELECT COUNT(*) as c FROM bookings WHERE booking_date>=? AND status='confirmed'",
            (month_start,),
        )
        revenue_month = await db.execute_fetchall(
            """SELECT SUM(s.price) as total FROM bookings b
               JOIN services s ON b.service_id=s.id
               WHERE b.booking_date>=? AND b.status='confirmed'""",
            (month_start,),
        )
        clients_total = await db.execute_fetchall("SELECT COUNT(*) as c FROM clients")

        return {
            "bookings_today": bookings_today[0]["c"],
            "bookings_month": bookings_month[0]["c"],
            "revenue_month": revenue_month[0]["total"] or 0,
            "clients_total": clients_total[0]["c"],
        }
    finally:
        await db.close()


# ── Seed demo data ───────────────────────────────────────
async def seed_demo():
    db = await get_db()
    try:
        existing = await db.execute_fetchall("SELECT COUNT(*) as c FROM services")
        if existing[0]["c"] > 0:
            return  # already seeded

        services = [
            ("Женская стрижка", 60, 1500),
            ("Мужская стрижка", 45, 800),
            ("Окрашивание", 120, 3000),
            ("Маникюр", 90, 1200),
            ("Педикюр", 90, 1500),
            ("Наращивание ногтей", 120, 2500),
            ("Укладка", 60, 1000),
            ("Ламинирование бровей", 60, 1500),
        ]
        for name, dur, price in services:
            await db.execute(
                "INSERT INTO services (name, duration_min, price) VALUES (?,?,?)",
                (name, dur, price),
            )

        masters = [
            ("Анна", "+79780001111"),
            ("Мария", "+79780002222"),
            ("Елена", "+79780003333"),
        ]
        for name, phone in masters:
            await db.execute(
                "INSERT INTO masters (name, phone) VALUES (?,?)", (name, phone)
            )

        # Link specializations
        specs = [(1, [1, 3, 7]), (2, [2, 1, 7]), (3, [4, 5, 6, 8])]
        for mid, sids in specs:
            for sid in sids:
                await db.execute(
                    "INSERT INTO master_specializations (master_id, service_id) VALUES (?,?)",
                    (mid, sid),
                )

        await db.commit()
        print("Demo data seeded!")
    finally:
        await db.close()
