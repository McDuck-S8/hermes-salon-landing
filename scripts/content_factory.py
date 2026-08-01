#!/usr/bin/env python3
"""
Content Factory — автоматическая генерация контента через бесплатные AI сервисы.
Использует ghost-surfer (Playwright + stealth) для веб-автоматизации.
"""
import asyncio
import json
import os
import random
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

# ─── Config ────────────────────────────────────────────────────────────────
HERMES_HOME = Path("D:/Portable_Soft/hermes")
WAREHOUSE = HERMES_HOME / "assets" / "content_warehouse"
WAREHOUSE_IMG = WAREHOUSE / "images"
WAREHOUSE_VID = WAREHOUSE / "video"
WAREHOUSE_IMG.mkdir(parents=True, exist_ok=True)
WAREHOUSE_VID.mkdir(parents=True, exist_ok=True)

DB_PATH = HERMES_HOME / "cache" / "content_factory.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Сервисы для генерации
SERVICES = {
    "images": [
        {
            "name": "bing_create",
            "url": "https://www.bing.com/create",
            "model": "DALL-E 3",
            "daily_limit": 100,
            "selectors": {
                "prompt_input": "textarea[id='prompt']",
                "generate_btn": "button[type='submit']",
                "images": "div.cimg img",
                "download_btn": "a[download]",
            }
        },
        {
            "name": "leonardo",
            "url": "https://leonardo.ai/app/generation",
            "model": "Phoenix/Lightning XL",
            "daily_limit": 150,
            "selectors": {
                "prompt_input": "textarea[placeholder*='prompt']",
                "generate_btn": "button:has-text('Generate')",
                "images": "div.generated-image img",
                "download_btn": "button[aria-label='Download']",
            }
        },
        {
            "name": "playground",
            "url": "https://playgroundai.com/create",
            "model": "Playground v2 / SDXL",
            "daily_limit": 500,
            "selectors": {
                "prompt_input": "textarea[data-testid='prompt-input']",
                "generate_btn": "button:has-text('Generate')",
                "images": "div.image-grid img",
                "download_btn": "button[aria-label='Download image']",
            }
        },
    ],
    "video": [
        {
            "name": "pika",
            "url": "https://pika.art/create",
            "model": "Pika 1.5",
            "daily_limit": 10,
            "selectors": {
                "prompt_input": "textarea[placeholder*='Describe']",
                "generate_btn": "button:has-text('Generate')",
                "video": "video",
                "download_btn": "a[download]",
            }
        },
        {
            "name": "runway",
            "url": "https://runwayml.com/generate",
            "model": "Gen-3 Alpha Turbo",
            "daily_limit": 5,  # кредиты
            "selectors": {
                "prompt_input": "textarea[placeholder*='prompt']",
                "generate_btn": "button:has-text('Generate')",
                "video": "video",
                "download_btn": "button[aria-label='Download']",
            }
        },
    ]
}

# Промпты по нишам
PROMPTS = {
    "ai_tools": [
        "Professional screenshot of {tool} interface, clean UI, modern dark mode, high resolution, 16:9 aspect ratio",
        "Isometric 3D illustration of AI workflow: {tool} processing data, futuristic style, vibrant colors, Blender render",
        "Minimalist infographic: '{tool} features' - icons, bullet points, tech blue color scheme, white background",
    ],
    "finance_crypto": [
        "Crypto trading dashboard screenshot: Bitcoin chart, green candles, professional Bloomberg terminal style, 4K",
        "3D isometric illustration: passive income stream, money flowing from laptop to wallet, crypto symbols, bright lighting",
        "Clean infographic: 'How to earn $1000/month with {method}' - steps, icons, money symbols, green/white theme",
    ],
    "tech_reviews": [
        "Product photography: {product} on reflective surface, studio lighting, 8K, commercial quality",
        "Split comparison: {product} vs competitor, side by side, specs highlighted, tech blog style",
        "Lifestyle shot: person using {product} in modern office, natural lighting, authentic, high-end",
    ],
    "motivation": [
        "Minimalist typography poster: '{quote}' - {author}, clean sans-serif, centered, high contrast, 2:3 ratio",
        "Abstract geometric background with motivational quote overlay, modern design, Pinterest style",
    ]
}

TOOLS = ["ChatGPT", "Claude", "Midjourney", "Cursor", "Leonardo AI", "Runway", "Perplexity", "Notion AI"]
METHODS = ["crypto trading", "affiliate marketing", "AI content creation", "freelancing", "digital products"]
PRODUCTS = ["iPhone 16 Pro", "MacBook Pro M4", "Sony A7R V", "DJI Mini 5", "Meta Quest 3"]
QUOTES = [
    ("The best way to predict the future is to create it.", "Peter Drucker"),
    ("Code is poetry that runs.", "Anonymous"),
    ("Automation amplifies leverage.", "Naval Ravikant"),
]


# ─── Database ──────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identity_id TEXT,
            service TEXT,
            niche TEXT,
            prompt TEXT,
            file_path TEXT,
            file_hash TEXT,
            status TEXT,  -- success, failed, pending
            created_at TEXT DEFAULT (datetime('now')),
            metadata TEXT  -- JSON
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS identities (
            id TEXT PRIMARY KEY,
            email TEXT,
            password TEXT,
            fingerprint TEXT,
            proxy TEXT,
            services TEXT,  -- JSON: service -> {cookies, localStorage}
            created_at TEXT,
            last_used TEXT,
            reputation REAL DEFAULT 1.0
        )
    """)
    conn.commit()
    return conn


def log_generation(conn, identity_id: str, service: str, niche: str, prompt: str,
                   file_path: str, status: str, metadata: dict = None):
    import hashlib
    file_hash = ""
    if file_path and Path(file_path).exists():
        file_hash = hashlib.md5(Path(file_path).read_bytes()).hexdigest()[:16]
    conn.execute("""
        INSERT INTO generations (identity_id, service, niche, prompt, file_path, file_hash, status, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (identity_id, service, niche, prompt, file_path, file_hash, status, json.dumps(metadata or {})))
    conn.commit()


# ─── Browser / Identity ────────────────────────────────────────────────────
async def create_browser_context(playwright, proxy: str = None):
    """Создаёт stealth браузер с уникальным фингерпринтом."""
    browser = await playwright.chromium.launch(
        headless=False,  # видно для дебага
        proxy={"server": proxy} if proxy else None,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ]
    )
    context = await browser.new_context(
        viewport={"width": 1366, "height": 768},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        locale="en-US",
        timezone_id="America/New_York",
    )
    await stealth_async(context)
    return browser, context


async def human_type(page, selector: str, text: str, wpm: int = 60):
    """Человекоподобный ввод с опечатками и коррекциями."""
    await page.click(selector)
    await page.fill(selector, "")  # clear
    for char in text:
        if random.random() < 0.02:  # 2% шанс опечатки
            wrong = random.choice("abcdefghijklmnopqrstuvwxyz")
            await page.type(selector, wrong, delay=random.randint(50, 150))
            await page.keyboard.press("Backspace")
            await asyncio.sleep(random.uniform(0.1, 0.3))
        await page.type(selector, char, delay=random.randint(50, 200))
    await asyncio.sleep(random.uniform(0.5, 1.5))


async def human_click(page, selector: str):
    """Человекоподобный клик с движением мыши."""
    element = await page.wait_for_selector(selector, timeout=10000)
    box = await element.bounding_box()
    if box:
        # Безье-кривая к элементу
        await page.mouse.move(
            box["x"] + box["width"] / 2 + random.uniform(-5, 5),
            box["y"] + box["height"] / 2 + random.uniform(-5, 5),
            steps=random.randint(10, 20)
        )
        await asyncio.sleep(random.uniform(0.1, 0.3))
        await element.click()
        await asyncio.sleep(random.uniform(0.5, 1.0))


# ─── Generation ────────────────────────────────────────────────────────────
async def generate_on_service(context, service: dict, prompt: str, niche: str, identity_id: str) -> List[str]:
    """Генерирует контент на одном сервисе. Возвращает список путей к файлам."""
    page = await context.new_page()
    saved_files = []

    try:
        print(f"  → Opening {service['name']}...")
        await page.goto(service["url"], wait_until="networkidle", timeout=60000)
        await asyncio.sleep(random.uniform(2, 4))

        # Ввод промпта
        sel = service["selectors"]
        await human_type(page, sel["prompt_input"], prompt)

        # Клик Generate
        await human_click(page, sel["generate_btn"])

        # Ждём генерацию (адаптивно)
        print(f"  → Waiting for generation...")
        await asyncio.sleep(random.uniform(15, 30))  # базовое ожидание

        # Пытаемся найти изображения/видео
        images = await page.query_selector_all(sel["images"])
        print(f"  → Found {len(images)} results")

        for i, img in enumerate(images[:3]):  # максимум 3 на генерацию
            try:
                # Клик для открытия/скачивания
                await img.click()
                await asyncio.sleep(random.uniform(1, 2))

                # Ищем кнопку скачивания
                download_btn = await page.query_selector(sel["download_btn"])
                if download_btn:
                    # Ожидаем скачивание
                    async with page.expect_download() as download_info:
                        await download_btn.click()
                    download = await download_info.value
                    ext = ".mp4" if "video" in service.get("model", "").lower() else ".png"
                    filename = f"{identity_id}_{service['name']}_{niche}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}{ext}"
                    save_path = (WAREHOUSE_VID if ext == ".mp4" else WAREHOUSE_IMG) / filename
                    await download.save_as(str(save_path))
                    saved_files.append(str(save_path))
                    print(f"  ✓ Saved: {save_path.name}")

                # Закрываем модалку если есть
                await page.keyboard.press("Escape")
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"  ✗ Failed to save item {i}: {e}")

    except Exception as e:
        print(f"  ✗ Error on {service['name']}: {e}")
    finally:
        await page.close()

    return saved_files


# ─── Main Cycle ────────────────────────────────────────────────────────────
async def run_cycle(identity_id: str = "factory_001", proxy: str = None):
    """Один цикл генерации по всем нишам и сервисам."""
    conn = init_db()

    async with async_playwright() as playwright:
        browser, context = await create_browser_context(playwright, proxy)

        try:
            for niche, prompt_templates in PROMPTS.items():
                print(f"\n=== Niche: {niche} ===")

                # Выбираем 1-2 промпта на нишу
                templates = random.sample(prompt_templates, min(2, len(prompt_templates)))

                for template in templates:
                    # Подстановка переменных
                    prompt = template.format(
                        tool=random.choice(TOOLS),
                        method=random.choice(METHODS),
                        product=random.choice(PRODUCTS),
                        quote=random.choice(QUOTES)[0],
                        author=random.choice(QUOTES)[1],
                    )

                    # Генерация изображений
                    for service in SERVICES["images"]:
                        print(f"\n--- {service['name']} | {niche} ---")
                        files = await generate_on_service(context, service, prompt, niche, identity_id)
                        for f in files:
                            log_generation(conn, identity_id, service["name"], niche, prompt, f, "success",
                                         {"template": template, "model": service["model"]})

                        # Пауза между сервисами
                        await asyncio.sleep(random.uniform(5, 10))

                    # Генерация видео (редже)
                    if random.random() < 0.3:  # 30% шанс видео
                        for service in SERVICES["video"]:
                            print(f"\n--- VIDEO: {service['name']} | {niche} ---")
                            files = await generate_on_service(context, service, prompt, niche, identity_id)
                            for f in files:
                                log_generation(conn, identity_id, service["name"], niche, prompt, f, "success",
                                             {"template": template, "model": service["model"]})
                            await asyncio.sleep(random.uniform(10, 20))

        finally:
            await browser.close()
            conn.close()

    print("\n✅ Cycle complete. Check warehouse:", WAREHOUSE)


# ─── CLI ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    identity = sys.argv[1] if len(sys.argv) > 1 else "factory_001"
    proxy = sys.argv[2] if len(sys.argv) > 2 else None
    asyncio.run(run_cycle(identity, proxy))