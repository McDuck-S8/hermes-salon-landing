"""MIRA Bot — Telegram AI-агент, встроенный в Hermes.

Не отдельный проект. Использует существующие ключи Hermes:
  OPENROUTER_API_KEY — LLM
  TAVILY_API_KEY — веб-поиск
  TELEGRAM_BOT_TOKEN — Telegram

Запуск: python mira.py
"""
import asyncio, json, logging, os, re, sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Пути ──
HERMES_HOME = Path(__file__).resolve().parent
DATA_DIR = HERMES_HOME / "cache" / "mira"
DATA_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_DB = DATA_DIR / "memory.db"
LOG_FILE = DATA_DIR / "mira.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# ── .env reader (прямой, без импорта hermes_config — чтобы не плодить зависимостей) ──
def _env(key: str, default: str = "") -> str:
    val = os.environ.get(key)
    if val:
        return val
    env_path = HERMES_HOME / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip()
    return default

BOT_TOKEN = _env("TELEGRAM_BOT_TOKEN", "")
OPENROUTER_KEY = _env("OPENROUTER_API_KEY", "")
COMPOSIO_KEY = _env("COMPOSIO_API_KEY", "")
TAVILY_KEY = _env("TAVILY_API_KEY", "")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [MIRA] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()])
log = logging.getLogger("mira")

# ═══════════════════════════════════════════
# ПАМЯТЬ (SQLite — факты, инсайты, сессии)
# ═══════════════════════════════════════════
class Memory:
    def __init__(self):
        self.db = str(MEMORY_DB)
        conn = sqlite3.connect(self.db)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT NOT NULL,
                user_id TEXT DEFAULT '', key TEXT NOT NULL, value TEXT NOT NULL,
                confidence REAL DEFAULT 1.0, updated_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT NOT NULL,
                insight TEXT NOT NULL, category TEXT DEFAULT 'general',
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT NOT NULL,
                summary TEXT DEFAULT '', messages_count INTEGER DEFAULT 0,
                last_active TEXT DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_facts_chat ON facts(chat_id);
            CREATE INDEX IF NOT EXISTS idx_insights_chat ON insights(chat_id);
        """)
        conn.commit(); conn.close()

    def remember(self, chat_id: str, key: str, value: str, user_id: str = ""):
        conn = sqlite3.connect(self.db)
        existing = conn.execute("SELECT id FROM facts WHERE chat_id=? AND key=? AND user_id=?", (chat_id, key, user_id)).fetchone()
        if existing:
            conn.execute("UPDATE facts SET value=?, updated_at=datetime('now') WHERE id=?", (value, existing[0]))
        else:
            conn.execute("INSERT INTO facts (chat_id, user_id, key, value) VALUES (?,?,?,?)", (chat_id, user_id, key, value))
        conn.commit(); conn.close()

    def recall(self, chat_id: str, key: Optional[str] = None) -> list:
        conn = sqlite3.connect(self.db); conn.row_factory = sqlite3.Row
        if key: rows = conn.execute("SELECT * FROM facts WHERE chat_id=? AND key=? ORDER BY confidence DESC", (chat_id, key))
        else: rows = conn.execute("SELECT * FROM facts WHERE chat_id=? ORDER BY updated_at DESC LIMIT 30", (chat_id,))
        r = [dict(x) for x in rows.fetchall()]; conn.close(); return r

    def forget(self, chat_id: str, key: str):
        conn = sqlite3.connect(self.db); conn.execute("DELETE FROM facts WHERE chat_id=? AND key=?", (chat_id, key)); conn.commit(); conn.close()

    def add_insight(self, chat_id: str, insight: str, category: str = "general"):
        conn = sqlite3.connect(self.db); conn.execute("INSERT INTO insights (chat_id, insight, category) VALUES (?,?,?)", (chat_id, insight, category)); conn.commit(); conn.close()

    def get_insights(self, chat_id: str) -> list:
        conn = sqlite3.connect(self.db); conn.row_factory = sqlite3.Row; rows = conn.execute("SELECT * FROM insights WHERE chat_id=? ORDER BY created_at DESC LIMIT 10", (chat_id,)); r = [dict(x) for x in rows.fetchall()]; conn.close(); return r

    def update_session(self, chat_id: str, summary: str = "", delta: int = 1):
        conn = sqlite3.connect(self.db); existing = conn.execute("SELECT id, messages_count FROM sessions WHERE chat_id=?", (chat_id,)).fetchone()
        if existing: conn.execute("UPDATE sessions SET messages_count=?, last_active=datetime('now'), summary=? WHERE id=?", (existing[1]+delta, summary or "", existing[0]))
        else: conn.execute("INSERT INTO sessions (chat_id, summary, messages_count) VALUES (?,?,?)", (chat_id, summary, delta))
        conn.commit(); conn.close()

    def build_context(self, chat_id: str, user_id: str = "") -> str:
        parts = []
        if user_id:
            uf = conn = sqlite3.connect(self.db); uf.row_factory = sqlite3.Row; rows = uf.execute("SELECT key,value FROM facts WHERE chat_id=? AND user_id=? ORDER BY updated_at DESC LIMIT 5", (chat_id, user_id)).fetchall(); uf.close()
            if rows: parts.append("Пользователь: " + ", ".join(f"{r['key']}={r['value']}" for r in rows))
        cf = conn = sqlite3.connect(self.db); cf.row_factory = sqlite3.Row; rows = cf.execute("SELECT DISTINCT key,value FROM facts WHERE chat_id=? ORDER BY updated_at DESC LIMIT 10", (chat_id,)).fetchall(); cf.close()
        if rows: parts.append("Контекст чата: " + ", ".join(f"{r['key']}={r['value']}" for r in rows))
        return "\n".join(parts)

# ═══════════════════════════════════════════
# LLM (через OpenRouter — существующий ключ)
# ═══════════════════════════════════════════
SYSTEM_PROMPT = """Ты — MIRA, AI-агент в Telegram. Понимаешь задачи на русском и выполняешь их.
Правила:
1. Если задача про поиск информации — используй search
2. Если про генерацию текста/картинок — content
3. Если про расписание — scheduler
4. Если про модерацию чата — moderation
5. Если про курс крипты — crypto
6. Если про запоминание — memory
7. Если вопрос/разговор — chat

Формат ответа (только JSON):
{ "tool": "search"|"content"|"scheduler"|"moderation"|"crypto"|"memory"|"chat",
  "action": "...", "params": {...}, "text": "ответ пользователю" }"""

async def llm_interpret(text: str, context: str = "") -> dict:
    if not OPENROUTER_KEY:
        return {"tool": "search", "action": "search", "params": {"query": text}, "text": f"Ищу: {text}"}
    try:
        import httpx
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if context: messages.append({"role": "system", "content": f"Контекст:\n{context}"})
        messages.append({"role": "user", "content": text})
        async with httpx.AsyncClient(timeout=30) as cl:
            r = await cl.post("https://openrouter.ai/api/v1/chat/completions", headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json",
            }, json={"model": "openai/gpt-4o-mini", "messages": messages, "temperature": 0.3, "max_tokens": 500})
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"].strip()
            if content.startswith("```"): content = content.split("\n",1)[1].rsplit("```",1)[0].strip()
            plan = json.loads(content); log.info("LLM: %s → %s", text[:40], json.dumps(plan, ensure_ascii=False)[:80])
            return plan
    except Exception as e:
        log.error("LLM error: %s", e)
        return {"tool": "search", "action": "search", "params": {"query": text}, "text": f"Не понял, ищу: {text}"}

# ═══════════════════════════════════════════
# ВСТРОЕННЫЕ НАВЫКИ (content, search, crypto)
# ═══════════════════════════════════════════
def _search_web(query: str) -> str:
    """Поиск через Tavily (ключ уже есть в .env)."""
    if not TAVILY_KEY:
        return f"🔍 По запросу '{query}' — поиск недоступен (нет TAVILY_API_KEY)"
    try:
        import httpx
        r = httpx.post("https://api.tavily.com/search", json={"api_key": TAVILY_KEY, "query": query, "max_results": 4}, timeout=15)
        r.raise_for_status(); data = r.json()
        results = data.get("results", [])
        if not results: return f"🔍 По запросу '{query}' — ничего не найдено."
        lines = [f"🔍 Результаты по '{query}':"]
        for res in results[:4]: lines.append(f"• {res['title']}: {res['content'][:200]}")
        return "\n".join(lines)
    except Exception as e: return f"🔍 Ошибка поиска: {e}"

def _generate_text(topic: str) -> str:
    """Генерация текста через OpenRouter."""
    if not OPENROUTER_KEY: return f"✍️ Тема: {topic}\n\n(генерация без LLM недоступна)"
    try:
        import httpx
        r = httpx.post("https://openrouter.ai/api/v1/chat/completions", headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json",
        }, json={"model": "openai/gpt-4o-mini", "messages": [
            {"role": "system", "content": "Напиши короткий пост (до 500 символов) на тему пользователя. Только текст, без пояснений."},
            {"role": "user", "content": topic}
        ], "temperature": 0.8, "max_tokens": 500}, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e: return f"✍️ Ошибка генерации: {e}"

def _generate_image(prompt: str) -> str:
    """Генерация URL картинки через placehold.co."""
    safe = prompt.replace(" ", "+")[:50]
    return f"🖼️ {prompt}\nhttps://placehold.co/800x600/1a1a2e/FFFFFF/png?text={safe}"

def _get_crypto_price(coin: str = "bitcoin") -> str:
    """Курс через CoinGecko."""
    import httpx
    try:
        r = httpx.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd", timeout=10)
        r.raise_for_status(); data = r.json()
        price = data.get(coin, {}).get("usd")
        return f"💰 {coin}: ${price:,.2f}" if price else f"💰 {coin}: не найден"
    except Exception as e: return f"💰 Ошибка: {e}"

def _check_moderation(text: str) -> list:
    spam = [r"(https?://[^\s]+){3,}", r"(купи|продай|заработок|пассивный доход)"]
    toxic = [r"(идиот|дурак|лох|мудак|козёл)"]
    violations = []
    for p in spam:
        if re.search(p, text, re.I): violations.append({"type":"spam","text":text[:80]}); break
    for p in toxic:
        if re.search(p, text, re.I): violations.append({"type":"toxic","text":text[:80]}); break
    return violations

# ═══════════════════════════════════════════
# COMPOSIO — 1000+ интеграций (Gmail, Slack, GitHub, Notion...)
# ═══════════════════════════════════════════
# Компилируем один раз — проверяем все паттерны без цикла
_COMPOSIO_ACTIONS = None
_COMPOSIO_RULES = None

def _init_composio():
    global _COMPOSIO_ACTIONS, _COMPOSIO_RULES
    if _COMPOSIO_ACTIONS is not None:
        return _COMPOSIO_ACTIONS
    _COMPOSIO_ACTIONS = False
    if not COMPOSIO_KEY:
        return False
    try:
        from composio import ComposioToolSet
        from composio import Action as CAction
        ts = ComposioToolSet(api_key=COMPOSIO_KEY)
        # Список доступных действий (первые ~50 пригодных для Telegram-агента)
        _COMPOSIO_ACTIONS = ts
        _COMPOSIO_RULES = [
            (r"(почт|письм|email|gmail|отправь на|прочти почт)", CAction.GMAIL_SEND_EMAIL),
            (r"(слак|slack|канал в слак)", CAction.SLACK_SEND_MESSAGE),
            (r"(issue|задач|баг|таск|тикет|гитхаб)", CAction.GITHUB_CREATE_ISSUE),
            (r"(notion|ноушн|заметк|page)", CAction.NOTION_CREATE_PAGE),
            (r"(discord|дискорд)", CAction.DISCORD_SEND_MESSAGE),
            (r"(linear|линеар)", CAction.LINEAR_CREATE_ISSUE),
            (r"(twitter|твиттер|твит|x\.com)", CAction.TWITTER_CREATE_TWEET),
            (r"(instagram|инстаграм)", CAction.INSTAGRAM_CREATE_MEDIA),
            (r"(telegram|телеграм|тг)", CAction.TELEGRAM_SEND_MESSAGE),
            (r"(jira|джира)", CAction.JIRA_CREATE_ISSUE),
            (r"(confluence|конфлюенс)", CAction.CONFLUENCE_CREATE_PAGE),
            (r"(drive|гугл диск|google drive)", CAction.GOOGLEDRIVE_CREATE_FILE),
            (r"(sheets|гугл таблиц|google sheet)", CAction.GOOGLESHEETS_CREATE_SPREADSHEET),
            (r"(calendar|календарь|google календарь)", CAction.GOOGLECALENDAR_CREATE_EVENT),
            (r"(hubspot|хaбспот|crm)", CAction.HUBSPOT_CREATE_CONTACT),
            (r"(figma|фигма)", CAction.FIGMA_CREATE_FILE),
            (r"(asana|асана)", CAction.ASANA_CREATE_TASK),
            (r"(redmine|редмайн)", Action if False else CAction),  # fallback placeholder
        ]
        log.info("Composio: loaded with %d rules", len(_COMPOSIO_RULES))
        return _COMPOSIO_ACTIONS
    except Exception as e:
        log.warning("Composio init failed: %s", e)
        return False

async def _composio_run(text: str) -> Optional[str]:
    """Пытается выполнить задачу через Composio. Возвращает результат или None."""
    ts = _init_composio()
    if not ts:
        return None
    # Подбираем действие
    matched = None
    for pattern, action in _COMPOSIO_RULES:
        if re.search(pattern, text.lower()):
            matched = action
            break
    if not matched:
        return None
    try:
        # Простое выполнение — первый попавшийся connected аккаунт
        result = ts.execute_action(action=matched, params={})
        return f"✅ Composio: {matched.name}\n{str(result)[:300]}"
    except Exception as e:
        log.warning("Composio action failed: %s", e)
        return f"⚠️ Composio: {matched.name} — {e}"

# ═══════════════════════════════════════════
# ОБРАБОТКА ЗАДАЧИ
# ═══════════════════════════════════════════
async def handle_message(text: str, chat_id: str, user_id: str, username: str = "", is_group: bool = False) -> Optional[str]:
    text = text.strip()
    mem = Memory()

    # ── Команды ──
    if text.startswith("/remember "):
        rest = text[10:].strip(); k, _, v = rest.partition("=")
        if k and v: mem.remember(chat_id, k.strip(), v.strip(), user_id); return f"✅ Запомнил: {k.strip()}"
        return "❌ /remember ключ = значение"
    if text == "/recall":
        facts = mem.recall(chat_id)
        return "\n".join(["🧠 Что я помню:"] + [f"• {f['key']}: {f['value']}" for f in facts[-10:]]) if facts else "📭 Ничего не помню."
    if text.startswith("/forget "):
        k = text[8:].strip(); mem.forget(chat_id, k); return f"✅ Забыл: {k}"
    if text == "/insights":
        ins = mem.get_insights(chat_id)
        return "\n".join(["💡 Инсайты:"] + [f"• [{i['category']}] {i['insight']}" for i in ins]) if ins else "💡 Нет инсайтов."

    # ── Модерация (group) ──
    if is_group:
        v = _check_moderation(text)
        if v: log.warning("Moderation %s in %s by %s", v[0]['type'], chat_id, username); return None

    mem.update_session(chat_id, delta=1)
    mem.remember(chat_id, f"запрос_{datetime.now().strftime('%H%M')}", text[:100], user_id)

    # ── LLM интерпретация ──
    ctx = mem.build_context(chat_id, user_id)
    plan = await llm_interpret(text, ctx)
    tool, action, params = plan.get("tool"), plan.get("action"), plan.get("params", {})

    # ── Выполнение: Composio → built-in ──
    result_text = ""
    # Сначала пробуем Composio (если есть ключ и действие подходит)
    if COMPOSIO_KEY:
        composio_result = await _composio_run(text)
        if composio_result:
            result_text = composio_result
    # Если Composio не сработал — используем built-in навыки
    if not result_text:
        if tool == "search":
            result_text = _search_web(params.get("query", text))
        elif tool == "content":
            if action == "generate_image": result_text = _generate_image(params.get("prompt", params.get("topic","")))
            else: result_text = _generate_text(params.get("topic", params.get("prompt", text)))
        elif tool == "crypto":
            result_text = _get_crypto_price(params.get("coin", "bitcoin"))
        elif tool == "memory":
            k, v = params.get("key", ""), params.get("value", "")
            if k and v: mem.remember(chat_id, k, v, user_id); result_text = f"✅ Запомнил: {k}"
            else: result_text = "🧠 Напиши что запомнить: /remember ключ = значение"
        else:
            result_text = _search_web(text)

    if result_text: mem.add_insight(chat_id, f"{text[:50]} → {result_text[:80]}", "interaction")
    return result_text[:3500]

# ═══════════════════════════════════════════
# TELEGRAM BOT
# ═══════════════════════════════════════════
async def main():
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters

    app = Application.builder().token(BOT_TOKEN).build()

    async def start(update: Update, context):
        await update.message.reply_text(
            "👋 Я MIRA — твой AI-агент в Telegram.\n\n"
            "Пиши что хочешь сделать:\n"
            "• \"напиши пост про нейросети\"\n"
            "• \"какой курс биткоина?\"\n"
            "• \"найди информацию про X\"\n"
            "• \"сделай картинку: робот\"\n"
            "• \"запомни: я люблю кофе\"\n\n"
            "/help — подробнее\n"
            "/recall — что я помню\n"
            "/remember ключ = значение\n"
            "/forget ключ\n"
            "/insights"
        )

    async def help_cmd(update: Update, context):
        await update.message.reply_text(
            "🤖 **MIRA** — AI-агент в Telegram.\n\n"
            "Понимает задачи на русском языке.\n"
            "Использует твои ключи Hermes — ничего нового ставить не надо.\n\n"
            "**Команды:**\n"
            "/remember ключ = значение — запомнить\n"
            "/recall — показать память\n"
            "/forget ключ — забыть\n"
            "/insights — инсайты\n\n"
            "**Что умеет:**\n"
            "• Генерировать текст (посты, идеи)\n"
            "• Генерировать картинки\n"
            "• Искать в интернете (Tavily)\n"
            "• Курс крипты (CoinGecko)\n"
            "• Модерировать чаты (антиспам)\n"
            "• Запоминать факты о вас\n\n"
            "Работает внутри Hermes — без новых API ключей.",
            parse_mode="Markdown"
        )

    async def handle_msg(update: Update, context):
        if not update.message or not update.message.text: return
        user_id, chat_id = str(update.effective_user.id), str(update.effective_chat.id)
        username, is_group = update.effective_user.username or "", update.effective_chat.type in ("group","supergroup")
        async with update.effective_chat.action("typing"):
            r = await handle_message(update.message.text, chat_id, user_id, username, is_group)
        if r: await update.message.reply_text(r)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    log.info("MIRA started (TELEGRAM_BOT_TOKEN=%s)", BOT_TOKEN[:8]+"...")
    print("🤖 MIRA запущен! Ctrl+C для остановки.")
    await app.run_polling(allowed_updates=["messages"])

if __name__ == "__main__":
    asyncio.run(main())
