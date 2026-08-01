#!/usr/bin/env python3
"""
CPA Telegram Bot — Lead Magnet Funnel
Collects leads via free PDF, nurtures via sequence, redirects to CPA offers.
"""
import asyncio, json, os, sqlite3, logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Config
BOT_TOKEN = os.getenv("CPA_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID = int(os.getenv("CPA_ADMIN_ID", "0"))
DB_PATH = Path("cpa_bot.db")
LEAD_MAGNET_PATH = Path("lead_magnet.pdf")  # Your PDF here

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Database ──────────────────────────────────────────────
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                lead_magnet_sent BOOLEAN DEFAULT 0,
                sequence_step INTEGER DEFAULT 0,
                last_message_at TIMESTAMP,
                source TEXT,
                utm_data TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                url TEXT,
                description TEXT,
                category TEXT,
                payout REAL,
                active BOOLEAN DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                offer_id INTEGER,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Seed offers
        offers = [
            ("Smart Home DIY Guide", "https://your-cpa-link.com/smart-home", "Гайд по умному дому", "DIY", 2.50),
            ("Crypto Wallet Setup", "https://your-cpa-link.com/crypto-wallet", "Настройка крипто-кошелька", "Crypto", 5.00),
            ("VPN for Streaming", "https://your-cpa-link.com/vpn", "VPN для стриминга", "VPN", 3.00),
            ("Survey Panel", "https://your-cpa-link.com/survey", "Опросы за деньги", "Survey", 1.50),
            ("Gaming Skins", "https://your-cpa-link.com/gaming", "Бесплатные скины в играх", "Gaming", 0.80),
        ]
        conn.executemany("INSERT OR IGNORE INTO offers (name, url, description, category, payout) VALUES (?,?,?,?,?)", offers)

# ── FSM States ────────────────────────────────────────────
class LeadState(StatesGroup):
    waiting_start = State()
    got_lead_magnet = State()
    in_sequence = State()

# ── Keyboards ─────────────────────────────────────────────
def get_start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Получить чек-лист «Умный дом за вечер»", callback_data="get_lead_magnet")],
        [InlineKeyboardButton(text="💰 Лучшие офферы сейчас", callback_data="show_offers")],
        [InlineKeyboardButton(text="📖 Как это работает", callback_data="how_it_works")]
    ])

def get_offers_kb(offers: List[Dict]):
    buttons = []
    for o in offers:
        buttons.append([InlineKeyboardButton(text=f"{o['name']} — ${o['payout']}", url=o['url'])])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_start")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_after_lead_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Посмотреть офферы", callback_data="show_offers")],
        [InlineKeyboardButton(text="📚 Библиотека гайдов", callback_data="library")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="back_start")]
    ])

# ── Bot Setup ─────────────────────────────────────────────
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ── Handlers ──────────────────────────────────────────────
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    args = message.text.split(maxsplit=1)
    utm = args[1] if len(args) > 1 else ""
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT OR IGNORE INTO leads (user_id, username, first_name, source, utm_data)
            VALUES (?, ?, ?, 'telegram', ?)
        """, (message.from_user.id, message.from_user.username, message.from_user.first_name, utm))
        if utm:
            conn.execute("UPDATE leads SET utm_data=? WHERE user_id=?", (utm, message.from_user.id))
    
    await state.set_state(LeadState.waiting_start)
    await message.answer(
        "👋 Привет! Я бот с бесплатными гайдами и проверенными способами заработка.\n\n"
        "🎁 Мой лучший материал — **чек-лист «Умный дом своими руками за один вечер»**:\n"
        "— 7 готовых схем подключения\n"
        "— Список деталей за $50\n"
        "— MQTT + Home Assistant настройка\n\n"
        "Нажми кнопку ниже — пришлю PDF прямо в чат.",
        reply_markup=get_start_kb(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "get_lead_magnet")
async def send_lead_magnet(callback: types.CallbackQuery, state: FSMContext):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE leads SET lead_magnet_sent=1, sequence_step=1, last_message_at=CURRENT_TIMESTAMP WHERE user_id=?", 
                     (callback.from_user.id,))
    
    if LEAD_MAGNET_PATH.exists():
        await callback.message.answer_document(
            FSInputFile(LEAD_MAGNET_PATH),
            caption="📎 Твой чек-лист! Изучай, собирай, делись результатом.\n\n"
                    "А пока читаешь — вот **топ офферы этой недели** 👇",
            reply_markup=get_after_lead_kb()
        )
    else:
        await callback.message.answer(
            "📎 Чек-лист в подготовке. А пока — **топ офферы** 👇",
            reply_markup=get_after_lead_kb(),
            parse_mode="Markdown"
        )
    
    await state.set_state(LeadState.got_lead_magnet)
    await callback.answer()

@dp.callback_query(F.data == "show_offers")
async def show_offers(callback: types.CallbackQuery):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        offers = conn.execute("SELECT * FROM offers WHERE active=1 ORDER BY payout DESC").fetchall()
        offers = [dict(o) for o in offers]
    
    text = "💰 **Проверенные офферы на этой неделе:**\n\n"
    for o in offers:
        text += f"• **{o['name']}** — ${o['payout']}/лид\n  {o['description']}\n\n"
    text += "👇 Нажми на кнопку — перейдёшь на лендинг."
    
    await callback.message.edit_text(text, reply_markup=get_offers_kb(offers), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "back_start")
async def back_start(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(LeadState.waiting_start)
    await callback.message.edit_text(
        "👋 Главное меню:",
        reply_markup=get_start_kb()
    )
    await callback.answer()

@dp.callback_query(F.data == "how_it_works")
async def how_it_works(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📖 **Как это работает:**\n\n"
        "1. Ты получаешь бесплатные гайды и чек-листы\n"
        "2. Я подбираю проверенные CPA-офферы (партнёрки платят за лиды)\n"
        "3. Ты переходишь по ссылке → выполняешь действие (рег/депозит/опрос)\n"
        "4. Партнёрка платит мне → я делюсь лучшими схемами с тобой\n\n"
        "Никаких вложений. Только твой трафик и время.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_start")]
        ]),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "library")
async def library(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📚 **Библиотека гайдов** (скоро):\n\n"
        "• Умный дом за $50\n"
        "• Крипта без KYC\n"
        "• Pinterest трафик бесплатно\n"
        "• Telegram-боты для заработка\n\n"
        "Подпишись на канал @your_channel — новые гайды там первыми.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_start")]
        ]),
        parse_mode="Markdown"
    )
    await callback.answer()

# ── Admin ─────────────────────────────────────────────────
@dp.message(Command("stats"))
async def admin_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        total = conn.execute("SELECT COUNT(*) as c FROM leads").fetchone()['c']
        with_magnet = conn.execute("SELECT COUNT(*) as c FROM leads WHERE lead_magnet_sent=1").fetchone()['c']
        today = conn.execute("SELECT COUNT(*) as c FROM leads WHERE date(joined_at)=date('now')").fetchone()['c']
        clicks = conn.execute("SELECT COUNT(*) as c FROM clicks").fetchone()['c']
    await message.answer(f"📊 **Stats:**\nTotal: {total}\nGot magnet: {with_magnet}\nToday: {today}\nClicks: {clicks}")

# ── Sequence (n8n-style but built-in) ─────────────────────
SEQUENCE = [
    {"delay_h": 2, "text": "💡 Совет: начни с ESP8266 + DHT22 — это $3 и 15 минут настройки. MQTT в Home Assistant заработает сразу."},
    {"delay_h": 24, "text": "📈 Если собрал схему — залей фото в чат @your_channel. Лучшие получают приватный гайд по Zigbee."},
    {"delay_h": 48, "text": "🔥 Горячий оффер недели: **VPN для стриминга** — $3/лид. Регаешься по ссылке → качаешь приложение → платит партнёрка. Ссылка в меню 👉 /offers"},
    {"delay_h": 72, "text": "💡 Продвинутый уровень: Node-RED автоматизации. Преврати дом в умный за выходные. Гайд выйдет в пятницу."},
]

async def run_sequence():
    """Background task: send sequence messages"""
    while True:
        now = datetime.now()
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            leads = conn.execute("""
                SELECT * FROM leads 
                WHERE lead_magnet_sent=1 AND sequence_step > 0 AND sequence_step <= ?
                AND (last_message_at IS NULL OR datetime(last_message_at) < datetime('now', ?))
            """, (len(SEQUENCE), f"-{SEQUENCE[0]['delay_h']} hours")).fetchall()
            
            for lead in leads:
                step = lead['sequence_step']
                if step <= len(SEQUENCE):
                    msg = SEQUENCE[step - 1]
                    try:
                        await bot.send_message(lead['user_id'], msg['text'], parse_mode="Markdown")
                        conn.execute("UPDATE leads SET sequence_step=?, last_message_at=CURRENT_TIMESTAMP WHERE user_id=?",
                                     (step + 1, lead['user_id']))
                        conn.commit()
                    except Exception as e:
                        logger.warning(f"Failed to send sequence to {lead['user_id']}: {e}")
        
        await asyncio.sleep(300)  # Check every 5 min

# ── Main ──────────────────────────────────────────────────
async def main():
    init_db()
    # Start sequence runner
    asyncio.create_task(run_sequence())
    logger.info("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())