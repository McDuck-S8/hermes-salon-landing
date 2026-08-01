#!/usr/bin/env python3
"""Pinterest Auto-Pinner - генерация пинов через Fal.ai (Flux/Nano Banana) + типографика ai2play.net"""
import json, os, time, hashlib, random, sqlite3, logging, sys, asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
import httpx

HERMES_HOME = Path("D:/Portable_Soft/hermes")
PIN_DIR = HERMES_HOME / "cache" / "pins"
PIN_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR = HERMES_HOME / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_DIR / "pinterest.log", encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger("pinner")

FAL_API_KEY = os.environ.get("FAL_API_KEY", "")
FAL_BASE = "https://fal.run"

TYPOGRAPHY_STYLES = [
    "clean minimalist sans-serif, high contrast, Swiss design, Helvetica",
    "bold retro serif, 70s vintage, warm colors, textured paper grain",
    "neon cyberpunk, glowing outlines, dark background, synthwave aesthetic",
    "handwritten brush script, organic, imperfect edges, watercolor texture",
    "3D extruded letters, volumetric lighting, glass material, octane render",
    "kinetic typography, motion blur, dynamic composition, italic lean",
    "brutalist raw typography, monospace, high contrast black white",
    "art nouveau decorative, floral ornaments, flowing curves, elegant",
    "glitch distorted text, digital artifacts, RGB split, VHS aesthetic",
    "luxury editorial serif, high fashion magazine, golden foil accents",
    "graffiti street art, spray paint, drips, urban wall texture",
    "isometric 3D letters, voxel style, bright pastel colors",
    "paper cutout layered typography, shadow depth, craft aesthetic",
    "liquid fluid letters, mercury chrome, reflective metallic surface",
    "embroidery stitch text, fabric texture, thread detail, cozy",
    "pixel art bitmap font, 8-bit retro gaming, crisp edges",
    "neon tube glass, gas discharge lighting, night city reflection",
    "wood carved letters, natural grain, rustic handcrafted feel",
    "ice frozen typography, crystalline, translucent, cold blue tones",
    "fire burning letters, flames, embers, heat distortion",
    "morphing blob letters, organic shapes, claymation style",
    "typography as architecture, building letters, structural",
    "origami folded paper letters, geometric facets, clean shadows",
    "holographic iridescent text, rainbow prism, futuristic UI",
    "stamp press printed, ink bleed, vintage letterpress texture",
    "chalkboard handwritten, dusty texture, classroom aesthetic",
    "light painting long exposure, light trails in dark void",
    "magnetic ferrofluid letters, spikes, surreal physics",
    "candy sweet typography, gumdrop, lollipop, bright saturated",
    "marble stone carved, classical sculpture, eternal elegance",
    "cosmic galaxy letters, nebula clouds, stars, deep space",
    "liquid gold molten metal, viscous, luxurious reflective",
    "moss grass organic, living typography, nature reclaiming",
    "neon sign glass tubes, mounted on brick wall, night atmosphere",
    "vinyl record groove text, analog audio aesthetic",
    "circuit board traces, PCB green, tech futuristic",
    "cloud fluffy letters, soft white, sky blue background",
    "crystal gemstone facets, diamond cut, prismatic refraction",
    "duct tape letters, industrial, rough adhesive texture",
    "etched metal industrial, brushed aluminum, precision CNC",
    "feather quill calligraphy, ink splatter, classical script",
    "gingerbread cookie icing, holiday festive, delicious",
    "hammered copper metal, warm patina, artisanal craft",
    "inflatable balloon letters, shiny plastic, party fun",
    "jigsaw puzzle pieces, interlocking, problem solving",
    "knitted wool yarn, cozy sweater texture, hygge",
    "laser cut acrylic layers, precision engineering, modern",
    "magnetic poetry fridge words, casual arrangement",
    "newspaper collage ransom note, mixed fonts, urgent",
    "origami crane folded, paper art, Japanese aesthetic",
    "porcelain china delicate, blue white pattern, fragile",
    "quilling paper filigree, rolled strips, intricate detail",
    "rope twisted fibers, nautical, tensile strength",
    "sand written beach, tide marks, ephemeral temporary",
    "tape cassette labels, retro analog, handwritten marker",
    "ukiyo-e woodblock, Japanese print, flat color areas",
    "velvet flocked letters, soft tactile, luxurious depth",
    "wax seal impressed, royal emblem, historical authority",
    "xerox photocopy degradation, generational loss, gritty",
    "yarn bomb colorful, street art knitting, community",
    "zen garden raked sand, meditative, minimal patterns",
]

NICHES = {
    "ai_tools": {
        "keywords": ["AI technology", "artificial intelligence", "neural network", "machine learning"],
        "topics": ["ChatGPT", "Midjourney", "Claude AI", "GitHub Copilot", "Gemini", "Stable Diffusion", "Runway ML", "Perplexity", "Cursor IDE", "Fal.ai"],
        "desc_templates": [
            "Best AI tool for {topic} in 2025 - try it free ->",
            "How to use {topic} for 10x productivity boost",
            "Top 10 {topic} alternatives you need to know",
            "{topic} tutorial: step by step guide for beginners",
            "Why {topic} is changing everything for creators",
        ],
    },
    "finance": {
        "keywords": ["money", "finance", "investment", "passive income", "crypto", "trading"],
        "topics": ["passive income", "crypto trading", "affiliate marketing", "freelancing", "digital products", "print on demand", "dropshipping", "stock dividends"],
        "amounts": ["$500", "$1000", "$2000", "$5000", "$10000", "$50/mo", "$100/day"],
        "desc_templates": [
            "How to earn {amount} per month with {topic}",
            "{topic} for beginners: complete 2025 guide",
            "Best {topic} strategies that actually work",
            "Why {topic} is the future of online income",
            "5 {topic} mistakes that cost you money",
        ],
    },
    "tech_reviews": {
        "keywords": ["technology", "gadget", "software", "digital tools", "productivity"],
        "topics": ["Apple Vision Pro", "Meta Quest 3", "Samsung Galaxy S25", "Notion AI", "GitHub Copilot", "VS Code", "Figma", "Docker", "Obsidian", "Raycast"],
        "desc_templates": [
            "{topic} review 2025: worth the money?",
            "{topic} vs competitors: which is better?",
            "How to set up {topic} for maximum results",
            "{topic} hidden features nobody talks about",
            "Is {topic} still relevant in 2025?",
        ],
    },
}

PIN_SCHEDULE = ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "22:00"]

PIN_DB = HERMES_HOME / "cache" / "pinterest.db"

def init_db():
    conn = sqlite3.connect(str(PIN_DB))
    conn.execute("""CREATE TABLE IF NOT EXISTS pins (
        id TEXT PRIMARY KEY, niche TEXT, image_url TEXT, title TEXT,
        description TEXT, link TEXT, style TEXT, status TEXT DEFAULT 'pending',
        created_at TEXT, posted_at TEXT, error TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS metrics (
        date TEXT PRIMARY KEY, pins_posted INTEGER DEFAULT 0,
        impressions INTEGER DEFAULT 0, clicks INTEGER DEFAULT 0, saves INTEGER DEFAULT 0
    )""")
    conn.commit()
    return conn

async def generate_pin_image(prompt: str, style: str) -> Optional[str]:
    if not FAL_API_KEY:
        log.warning("FAL_API_KEY not set, using placehold.co fallback")
        return fallback_image(prompt)

    full_prompt = f"""
Pinterest pin, vertical 2:3 ratio, {prompt}
Typography: {style}, text hierarchy clear, readable at thumbnail size,
professional design, high visual hierarchy, eye-catching, viral potential,
clean composition, balanced negative space, brandable aesthetic.
""".strip()

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{FAL_BASE}/fal-ai/flux-pro",
                headers={"Authorization": f"Key {FAL_API_KEY}", "Content-Type": "application/json"},
                json={
                    "prompt": full_prompt,
                    "image_size": "portrait_2_3",
                    "num_inference_steps": 28,
                    "guidance_scale": 3.5,
                    "num_images": 1,
                    "enable_safety_checker": True,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("images"):
                return data["images"][0]["url"]
    except Exception as e:
        log.error(f"Fal.ai generation failed: {e}")

    return fallback_image(prompt)

def fallback_image(keyword: str) -> str:
    seed = hashlib.md5(keyword.encode()).hexdigest()[:8]
    colors = ["1E40AF", "7C3AED", "059669", "DC2626", "D97706", "2563EB", "9333EA", "0891B2"]
    color = colors[int(seed[:2], 16) % len(colors)]
    label = keyword.replace(" ", "+")[:20]
    return f"https://placehold.co/600x900/{color}/FFFFFF/png?text={label}"

def pick_niche() -> tuple:
    niches = list(NICHES.items())
    weights = [0.4, 0.35, 0.25]
    return random.choices(niches, weights=weights, k=1)[0]

def generate_pin(niche_name: str, niche: dict) -> dict:
    topic = random.choice(niche["topics"])
    keyword = random.choice(niche["keywords"])
    template = random.choice(niche["desc_templates"])
    style = random.choice(TYPOGRAPHY_STYLES)

    if niche_name == "finance":
        amount = random.choice(niche.get("amounts", ["$1000"]))
        description = template.format(topic=topic, amount=amount, method=topic)
    else:
        description = template.format(topic=topic)

    title = f"{topic}: {description[:60]}..." if len(description) > 60 else f"{topic}: {description}"

    return {
        "niche": niche_name,
        "topic": topic,
        "keyword": keyword,
        "title": title[:100],
        "description": description[:500],
        "style": style,
        "link": f"https://t.me/max_brain_chef_official",
    }

async def run_cycle():
    if not FAL_API_KEY:
        log.error("FAL_API_KEY not set - set env var to enable AI generation")
        return 0

    conn = init_db()
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")

    if current_time not in PIN_SCHEDULE:
        next_slots = [s for s in PIN_SCHEDULE if s > current_time]
        if next_slots:
            log.debug(f"Next pin at {next_slots[0]}")
        return 0

    existing = conn.execute("SELECT COUNT(*) FROM pins WHERE date(created_at)=?", (today,)).fetchone()[0]
    slot_index = PIN_SCHEDULE.index(current_time)
    if existing > slot_index:
        log.debug(f"Slot {current_time} already filled")
        conn.close()
        return 0

    niche_name, niche = pick_niche()
    pin_data = generate_pin(niche_name, niche)

    log.info(f"Generating pin for {niche_name}/{pin_data['topic']} with style: {pin_data['style'][:50]}...")
    image_url = await generate_pin_image(f"{pin_data['keyword']}, {pin_data['topic']}", pin_data["style"])

    pin_id = hashlib.md5(f"{pin_data['title']}{now.isoformat()}".encode()).hexdigest()[:16]

    conn.execute(
        "INSERT INTO pins (id, niche, image_url, title, description, link, style, status, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (pin_id, niche_name, image_url, pin_data["title"], pin_data["description"], pin_data["link"], pin_data["style"], "generated", now.isoformat()),
    )
    conn.commit()

    log.info(f"Generated pin {pin_id}: {pin_data['title']}")
    log.info(f"  Image: {image_url}")
    log.info(f"  Style: {pin_data['style'][:60]}...")

    conn.execute("UPDATE pins SET status='ready', posted_at=? WHERE id=?", (now.isoformat(), pin_id))
    conn.commit()
    conn.close()
    return 1

def status():
    conn = init_db()
    conn.row_factory = sqlite3.Row
    total = conn.execute("SELECT COUNT(*) FROM pins").fetchone()[0]
    ready = conn.execute("SELECT COUNT(*) FROM pins WHERE status='ready'").fetchone()[0]
    posted = conn.execute("SELECT COUNT(*) FROM pins WHERE status='posted'").fetchone()[0]
    recent = conn.execute("SELECT niche, title, style, created_at FROM pins ORDER BY created_at DESC LIMIT 5").fetchall()
    conn.close()

    print(f"Pinterest Auto-Pinner")
    print(f"{'='*40}")
    print(f"  Total:   {total}")
    print(f"  Ready:   {ready}")
    print(f"  Posted:  {posted}")
    print(f"  Schedule: {', '.join(PIN_SCHEDULE)} (MSK)")
    print(f"\n  Recent:")
    for r in recent:
        style_preview = r["style"][:50] + "..." if len(r["style"]) > 50 else r["style"]
        print(f"    [{r['niche']}] {r['title'][:50]}...")
        print(f"      Style: {style_preview}")

def gen_preview(count: int = 3):
    for _ in range(count):
        niche_name, niche = pick_niche()
        pin = generate_pin(niche_name, niche)
        print(f"\n[{niche_name}] {pin['title']}")
        print(f"  Topic: {pin['topic']}")
        print(f"  Desc: {pin['description'][:100]}...")
        print(f"  Style: {pin['style'][:80]}...")
        print(f"  Fallback img: {fallback_image(pin['keyword'])}")

if __name__ == "__main__":
    init_db()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "cycle"

    if cmd == "cycle":
        asyncio.run(run_cycle())
    elif cmd == "status":
        status()
    elif cmd == "gen":
        gen_preview(int(sys.argv[2]) if len(sys.argv) > 2 else 3)
    elif cmd == "test-fal":
        if not FAL_API_KEY:
            print("FAL_API_KEY not set")
            sys.exit(1)
        test_prompt = "AI tools for productivity, modern clean design"
        test_style = random.choice(TYPOGRAPHY_STYLES)
        url = asyncio.run(generate_pin_image(test_prompt, test_style))
        print(f"Generated: {url}")
    else:
        print(f"Usage: {sys.argv[0]} [cycle|status|gen|test-fal]")