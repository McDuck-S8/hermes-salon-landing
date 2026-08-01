#!/usr/bin/env python3
"""
AI Tools Hub Auto-Poster
Posts fresh AI tool discoveries to Telegram channel @ai_frontier_you
Tracks posted links in cache/posted_links.json to avoid duplicates.
"""
import json
import os
import subprocess
import urllib.request
from datetime import datetime
from pathlib import Path

HERMES_ROOT = Path("D:/Portable_Soft/hermes")
POSTED_LINKS_FILE = HERMES_ROOT / "cache" / "posted_links.json"
ENV_FILE = HERMES_ROOT / ".env"

def get_bot_token():
    """Read bot token from .env file."""
    if not ENV_FILE.exists():
        print("Error: .env file not found")
        return None
    for line in ENV_FILE.read_text().splitlines():
        if "BOT_TOKEN" in line and "=" in line:
            return line.split("=", 1)[1].strip()
    return None

def load_posted_links():
    """Load previously posted links."""
    if POSTED_LINKS_FILE.exists():
        try:
            data = json.loads(POSTED_LINKS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except:
            pass
    return []

def save_posted_links(links):
    """Save posted links."""
    POSTED_LINKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    POSTED_LINKS_FILE.write_text(json.dumps(links, indent=2, ensure_ascii=False), encoding="utf-8")

def send_message(bot_token, chat_id, text):
    """Send message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            return result
    except Exception as e:
        return {"ok": False, "description": str(e)}

# Content pool - each item has title, description, link, and tags
AI_TOOLS_CONTENT = [
    {
        "title": "🚀 Comet Browser — Free AI-Powered Browser",
        "text": """<b>Comet by Perplexity — теперь бесплатный!</b>

Браузер с встроенным AI-поиском, голосовым режимом и агентными задачами.

✨ Что умеет:
• Встроенный Perplexity Engine — ответы прямо в браузере
• Context-aware вкладки — понимает контекст вашей работы
• Agentic task automation — ставите задачу, браузер выполняет
• Voice mode — голосовое управление

💰 Бесплатно на iOS, Android, Windows, Mac
🔗 Ссылка: <a href="https://www.perplexity.ai/comet">Perplexity Comet</a>

#AI #browser #Perplexity #free #productivity""",
        "link": "https://www.perplexity.ai/comet",
        "category": "tools"
    },
    {
        "title": "🤖 NotebookLM — AI Research Assistant (Free)",
        "text": """<b>Google NotebookLM — ваш AI-ассистент для исследований</b>

Загружаете документы → AI анализирует и отвечает с цитатами.

🎯 Идеально для:
• Анализа научных статей и отчётов
• Синтеза информации из нескольких источников
• Подготовки презентаций и докладов
• Обучения на собственных материалах

⚡ Особенность: генерирует подкасты из ваших документов!

💰 Полностью бесплатно
🔗 <a href="https://notebooklm.google.com/">Google NotebookLM</a>

#AI #research #Google #free #education""",
        "link": "https://notebooklm.google.com/",
        "category": "tools"
    },
    {
        "title": "⚡ n8n — No-Code AI Automation",
        "text": """<b>n8n — визуальный конструктор AI-автоматизаций</b>

Соединяйте AI-модели с вашими данными и приложениями без кода.

🔧 Как работает:
• Drag-and-drop интерфейс
• 400+ интеграций (Gmail, Slack, databases, APIs)
• AI Agent builder — создавайте автономных агентов
• Self-hosted — данные под вашим контролем

💡 Примеры автоматизаций:
• Клиент написал → AI анализирует → создаёт тикет → уведомляет команду
• Новая статья → AI резюме → публикация в Telegram/Slack
• Мониторинг конкурентов → отчёт → email

💰 Freemium (самохостинг бесплатно)
🔗 <a href="https://n8n.io/">n8n.io</a>

#AI #automation #nocode #workflow #productivity""",
        "link": "https://n8n.io/",
        "category": "tools"
    },
    {
        "title": "🎨 Cursor — AI-Native Code Editor",
        "text": """<b>Cursor — редактор кода следующего поколения</b>

IDE, который понимает ваш код и помогает писать быстрее.

⚡ Возможности:
• AI-автодополнение с контекстом всего проекта
• Cmd+K — генерация кода по описанию
• Chat с AI о вашем коде
• Multi-file edits — правки в нескольких файлах сразу
• Поддержка всех основных языков

🎯 Для кого:
• Разработчики, которые хотят кодить быстрее
• Команды, работающие над большими проектами
• Всё, кому листать документацию

💰 Freemium (бесплатный план с базовыми функциями)
🔗 <a href="https://cursor.sh/">Cursor IDE</a>

#AI #coding #developer #Cursor #IDE""",
        "link": "https://cursor.sh/",
        "category": "tools"
    },
    {
        "title": "📝 Granola — AI Meeting Notes",
        "text": """<b>Granola — автоматические заметки с встреч</b>

AI слушает вашу встречу и создаёт структурированные заметки.

🎯 Проблема, которую решает:
• Забываете ключевые решения с совещаний
• Тратите время на протоколы
• Теряете контекст между встречами

⚡ Как работает:
• Работает тихо на встрече
• Автоматически выделяет ключевые моменты
• Создаёт структурированные заметки
• Понимает контекст проекта

💰 Freemium (бесплатный план для начала)
🔗 <a href="https://www.granola.so/">Granola</a>

#AI #meetings #productivity #notes #work""",
        "link": "https://www.granola.so/",
        "category": "tools"
    },
    {
        "title": "🔊 ElevenLabs — AI Voice Generation",
        "text": """<b>ElevenLabs — реалистичная генерация голоса</b>

Превращаете текст в естественную речь с эмоциями и интонацией.

✨ Возможности:
• 300+ голосов на 29 языках
• Клонирование голоса по образцу
• Дубляж видео на другие языки
• AI Voice Lab — создание уникальных голосов
• Real-time streaming — для чат-ботов

🎯 Применения:
• Озвучка подкастов и видео
• Обучающие материалы
• Телефонные боты
• Аудиокниги

💰 Freemium (10,000 символов/мес бесплатно)
🔗 <a href="https://elevenlabs.io/">ElevenLabs</a>

#AI #voice #TTS #ElevenLabs #audio""",
        "link": "https://elevenlabs.io/",
        "category": "tools"
    },
    {
        "title": "🎨 Napkin.ai — Text to Visuals",
        "text": """<b>Napkin.ai — превращаем текст в визуалы</b>

Написали текст → AI автоматически создаёт диаграммы, схемы и инфографику.

🎯 Идеально для:
• Презентаций и докладов
• Документации и README
• Маркетинговых материалов
• Обучающих курсов

⚡ Как работает:
• Вставляете текст
• AI анализирует структуру
• Генерирует визуалы автоматически
• Можно редактировать и экспортировать

💰 Freemium
🔗 <a href="https://www.napkin.ai/">Napkin.ai</a>

#AI #design #visual #infographic #content""",
        "link": "https://www.napkin.ai/",
        "category": "tools"
    },
    {
        "title": "🆓 24 Free AI Tools — Полный список 2026",
        "text": """<b>Полный список бесплатных AI-инструментов 2026</b>

eWeek собрали лучшие бесплатные AI-инструменты по категориям:

💬 Чат-боты: ChatGPT, Claude, Gemini
🎨 Генерация изображений: DALL-E, Firefly, Ideogram
🎬 Видео: Runway, Veo 3, Luma
🗣️ Голос: ElevenLabs, Speechify
💻 Кодинг: GitHub Copilot, Cursor
📝 Продуктивность: NotebookLM, Notion AI

📊 Ключевой вывод: почти все инструменты теперь имеют бесплатный план для старта.

🔗 <a href="https://www.eweek.com/news/24-best-free-ai-tools-2026/">Полный обзор на eWeek</a>

#AI #free #tools #productivity #overview""",
        "link": "https://www.eweek.com/news/24-best-free-ai-tools-2026/",
        "category": "resources"
    },
    {
        "title": "🧩 Zapier AI Agents — Автономные помощники",
        "text": """<b>Zapier Agents — AI-агенты, которые действуют за вас</b>

Создавайте AI-агентов, которые выполняют задачи в ваших приложениях.

🎯 Что умеют:
• Пишут и отправляют email по вашим правилам
• Заполняют CRM по результатам встреч
• Мониторят соцсети и реагируют
• Автоматизируют рутину между приложениями

⚡ Интеграции:
• 9,000+ приложений (Gmail, Slack, Sheets, Notion...)
• Работает с вашими данными
• Natural language — описываете задачу словами

💰 Freemium (бесплатный план для начала)
🔗 <a href="https://zapier.com/agents">Zapier Agents</a>

#AI #agents #automation #Zapier #productivity""",
        "link": "https://zapier.com/agents",
        "category": "tools"
    },
    {
        "title": "🌐 Perplexity Pro — AI Search с цитатами",
        "text": """<b>Perplexity — поиск будущего с источниками</b>

В отличие от Google, Perplexity отвечает на вопрос И цитирует источники.

✨ Возможности:
• Поиск в реальном времени с цитатами
• Фокусные режимы (Academic, YouTube, Reddit...)
• Follow-up вопросы — углубляйтесь в тему
• Pro Search — глубокий анализ с множественным поиском

🎯 Когда использовать:
• Исследования и анализ рынка
• Проверка фактов
• Технические вопросы с источниками
• Быстрый обзор новых тем

💰 Freemium (Pro — $20/мес для продвинутых функций)
🔗 <a href="https://www.perplexity.ai/">Perplexity AI</a>

#AI #search #research #Perplexity #free""",
        "link": "https://www.perplexity.ai/",
        "category": "tools"
    },
]

def create_post(tool_info):
    """Create a formatted post from tool info."""
    return tool_info["text"]

def main():
    bot_token = get_bot_token()
    if not bot_token:
        print("Error: Could not read bot token from .env")
        return

    posted_links = load_posted_links()
    print(f"Previously posted links: {len(posted_links)}")

    # Filter out already posted content
    available = [t for t in AI_TOOLS_CONTENT if t["link"] not in posted_links]
    print(f"Available new content: {len(available)}")

    if not available:
        print("No new content to post!")
        return

    # Select up to 3 posts (to avoid spam)
    import random
    random.shuffle(available)
    to_post = available[:3]

    channel = "@ai_frontier_you"
    success_count = 0

    for tool in to_post:
        post_text = create_post(tool)
        print(f"\nPosting: {tool['title']}")
        result = send_message(bot_token, channel, post_text)
        
        if result.get("ok"):
            print(f"  [OK] Posted successfully (message_id: {result['result']['message_id']})")
            posted_links.append({
                "link": tool["link"],
                "title": tool["title"],
                "posted_at": datetime.now().isoformat(),
                "message_id": result["result"]["message_id"]
            })
            success_count += 1
        else:
            print(f"  [FAIL] Error: {result.get('description', 'Unknown error')}")
    
    save_posted_links(posted_links)
    print(f"\n{'='*50}")
    print(f"Posted {success_count}/{len(to_post)} messages")
    print(f"Total tracked links: {len(posted_links)}")

if __name__ == "__main__":
    main()
