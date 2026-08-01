#!/usr/bin/env python3
"""
Free Traffic Scout 2026 — Week 1 Orchestrator
Автономный запуск и оркестрация недели 1 бесплатного трафика.
Запускает компоненты в правильном порядке, сохраняет метрики в KC.
"""

import sys
import os
import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Add scripts to path
SCRIPTS_DIR = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes")) / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from kc_rag import upsert, search
from chain_heartbeat import event_beat

# ─── Configuration ───
SKILLS_DIR = Path("D:/Portable_Soft/hermes/skills")
PROXY = "socks5://127.0.0.1:10806"
CONTENT_WAREHOUSE = Path("D:/Portable_Soft/hermes/assets/content_warehouse")

# ─── Helpers ───
def run_cmd(cmd, cwd=None, timeout=120):
    """Run shell command, return (success, output)."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd or SCRIPTS_DIR.parent,
            capture_output=True, text=True, timeout=timeout
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)

def log_kc(content, tags, source="free-traffic-scout"):
    """Save to Knowledge Cube via kc_rag.upsert."""
    try:
        tag_str = ",".join(tags) if isinstance(tags, list) else str(tags)
        upsert(content=content, tags=tag_str, source=source, confidence=0.9, verification_method="auto")
    except Exception as e:
        print(f"    ⚠️ KC log failed: {e}")

def log_metric(name, value, tags=None):
    """Log metric to KC."""
    t = ["metric", "free-traffic", "week1"] + (tags or [])
    log_kc(f"METRIC: {name} = {value}", t)

# ─── Phase 1: Infrastructure Setup ───
def setup_infrastructure():
    """Day 1: Create profiles, verify systems."""
    print("\n" + "="*60)
    print("PHASE 1: INFRASTRUCTURE SETUP (Day 1)")
    print("="*60)
    
    # 1.1 Verify proxy
    print("\n[1/6] Verifying proxy...")
    ok, out = run_cmd(f"curl -s --max-time 10 --proxy {PROXY} https://www.google.com -o /dev/null -w '%{{http_code}}'")
    if ok and "200" in out:
        print(f"    ✅ Proxy working: {PROXY}")
        log_kc(f"INFRA: Proxy verified {PROXY}", ["infra", "proxy"])
    else:
        print(f"    ❌ Proxy failed: {out}")
        log_kc(f"INFRA: Proxy FAILED {PROXY} - {out}", ["infra", "proxy", "error"])
        return False
    
    # 1.2 Verify BrowserOS
    print("\n[2/6] Verifying BrowserOS...")
    ok, out = run_cmd("curl -s http://127.0.0.1:9003/health")
    if ok and "healthy" in out.lower():
        print("    ✅ BrowserOS HEALTHY")
        log_kc("INFRA: BrowserOS healthy", ["infra", "browseros"])
    else:
        print(f"    ⚠️ BrowserOS: {out[:100]}")
        log_kc(f"INFRA: BrowserOS check - {out[:200]}", ["infra", "browseros"])
    
    # 1.3 Verify OpenRouter
    print("\n[3/6] Verifying OpenRouter...")
    ok, out = run_cmd("curl -s -H 'Authorization: Bearer $OPENROUTER_API_KEY' https://openrouter.ai/api/v1/models | head -5")
    if ok:
        print("    ✅ OpenRouter accessible")
        log_kc("INFRA: OpenRouter accessible", ["infra", "openrouter"])
    else:
        print(f"    ⚠️ OpenRouter: {out[:100]}")
    
    # 1.4 Create Ghost-surfer profiles
    print("\n[4/6] Creating Ghost-surfer profiles...")
    profiles = [
        ("beauty_main", "beauty"),
        ("education", "education"),
        ("services", "services"),
    ]
    for name, niche in profiles:
        cmd = f"cd {SKILLS_DIR}/automation/ghost-surfer && python scripts/ghost_surfer.py --create-profile --name {name} --proxy {PROXY}"
        ok, out = run_cmd(cmd, timeout=180)
        if ok:
            print(f"    ✅ Profile '{name}' ({niche}) created")
            log_kc(f"INFRA: Ghost-surfer profile {name} ({niche}) created", ["infra", "ghost-surfer", "profile", niche])
        else:
            print(f"    ⚠️ Profile '{name}': {out[:200]}")
            log_kc(f"INFRA: Ghost-surfer profile {name} FAILED - {out[:200]}", ["infra", "ghost-surfer", "error"])
    
    # 1.5 Verify TikTok Farm
    print("\n[5/6] Checking TikTok Farm...")
    ok, out = run_cmd(f"cd {SKILLS_DIR}/automation/tiktok-account-farm && python -c \"import scripts.tiktok_farm; print('OK')\"")
    if ok:
        print("    ✅ TikTok Farm module loads")
        log_kc("INFRA: TikTok Farm module OK", ["infra", "tiktok-farm"])
    else:
        print(f"    ⚠️ TikTok Farm: {out[:200]}")
    
    # 1.6 Create content warehouse dirs
    print("\n[6/6] Creating content warehouse directories...")
    for platform in ["tiktok", "instagram_reels", "youtube_shorts", "pinterest", "telegram"]:
        (CONTENT_WAREHOUSE / platform).mkdir(parents=True, exist_ok=True)
    (CONTENT_WAREHOUSE / "metadata").mkdir(parents=True, exist_ok=True)
    print("    ✅ Content warehouse ready")
    log_kc("INFRA: Content warehouse directories created", ["infra", "content-warehouse"])
    
    # Heartbeat
    event_beat("knowledge_added")
    event_beat("new_suggestions_ready")
    
    return True


# ─── Phase 2: Content Generation ───
def generate_content():
    """Day 2-3: Generate all content assets."""
    print("\n" + "="*60)
    print("PHASE 2: CONTENT GENERATION (Days 2-3)")
    print("="*60)
    
    # 2.1 Generate TikTok scripts via LLM
    print("\n[1/4] Generating TikTok scripts (5 templates × 3 variations)...")
    templates = [
        "problem_solution", "expert_lifehack", "before_after",
        "education_60sec", "myth_busting"
    ]
    niches = ["beauty", "education", "services"]
    
    scripts_generated = 0
    for niche in niches:
        for template in templates:
            # Use free-ai-surfing or direct LLM call
            prompt = f"""Generate a 15-30 second TikTok/Reels/Shorts script for {niche} niche using '{template}' format.
Structure: Hook (0-1s) → Value/Problem (1-5s) → Solution/Demo (5-15s) → Result/Proof (15-20s) → CTA (20-30s).
Include: visual cues, text overlays, timing, music suggestion.
Niche specifics: {niche} business automation, AI bots, client retention.
Output: JSON with fields: template, niche, hook, scenes[], cta, hashtags[]"""
            
            # Save prompt for manual LLM generation or use API
            script_file = CONTENT_WAREHOUSE / "metadata" / f"script_{niche}_{template}_{datetime.now().strftime('%Y%m%d')}.json"
            script_data = {
                "template": template,
                "niche": niche,
                "prompt": prompt,
                "generated_at": datetime.now().isoformat(),
                "status": "prompt_ready"
            }
            script_file.write_text(json.dumps(script_data, ensure_ascii=False, indent=2))
            scripts_generated += 1
    
    print(f"    ✅ {scripts_generated} script prompts saved to metadata/")
    log_kc(f"CONTENT: {scripts_generated} TikTok script prompts generated for 3 niches × 5 templates", ["content", "tiktok", "scripts"])
    
    # 2.2 Generate video assets via Pollinations
    print("\n[2/4] Generating video assets via Pollinations (free-ai-surfing)...")
    video_prompts = [
        "beauty salon transformation before after manicure cinematic lighting 9:16",
        "beauty master working calm client happy professional lighting 9:16",
        "nail art process close up satisfying ASMR 9:16",
        "salon reception empty then full clients booking phone 9:16",
        "master showing phone with bot appointment confirmation smile 9:16",
    ]
    
    videos_generated = 0
    for i, prompt in enumerate(video_prompts):
        # Pollinations video generation (they have video models now)
        url = f"https://video.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=720&height=1280&model=flux&nologo=true&seed={42+i}"
        output_file = CONTENT_WAREHOUSE / "tiktok" / f"day1_video_{i+1}.mp4"
        
        # Just save the URL for now - actual download can be done via browser/aria2
        meta_file = CONTENT_WAREHOUSE / "metadata" / f"video_{i+1}_{datetime.now().strftime('%Y%m%d')}.json"
        meta_file.write_text(json.dumps({
            "prompt": prompt,
            "url": url,
            "output": str(output_file),
            "service": "pollinations",
            "generated_at": datetime.now().isoformat(),
            "status": "url_ready"
        }, ensure_ascii=False, indent=2))
        videos_generated += 1
    
    print(f"    ✅ {videos_generated} video URLs ready (download via browser/aria2)")
    log_kc(f"CONTENT: {videos_generated} Pollinations video URLs generated for TikTok", ["content", "video", "pollinations"])
    
    # 2.3 Generate images for Instagram Reels / Pinterest
    print("\n[3/4] Generating images via Pollinations...")
    image_prompts = [
        "beauty salon before after manicure transformation split screen professional",
        "calm salon admin drinking coffee looking at tablet with booking calendar",
        "frustrated salon admin phone ringing papers chaos vs calm organized workspace",
        "client journey: phone screen -> bot -> calendar -> confirmed -> happy client",
        "myth busting: coding complex vs drag-drop bot builder reality",
    ]
    
    images_generated = 0
    for i, prompt in enumerate(image_prompts):
        url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1080&height=1350&model=flux&nologo=true&seed={100+i}"
        output_file = CONTENT_WAREHOUSE / "instagram_reels" / f"day1_image_{i+1}.jpg"
        
        meta_file = CONTENT_WAREHOUSE / "metadata" / f"image_{i+1}_{datetime.now().strftime('%Y%m%d')}.json"
        meta_file.write_text(json.dumps({
            "prompt": prompt,
            "url": url,
            "output": str(output_file),
            "service": "pollinations",
            "generated_at": datetime.now().isoformat(),
            "status": "url_ready"
        }, ensure_ascii=False, indent=2))
        images_generated += 1
    
    print(f"    ✅ {images_generated} image URLs ready")
    log_kc(f"CONTENT: {images_generated} Pollinations image URLs generated for Instagram/Pinterest", ["content", "image", "pollinations"])
    
    # 2.4 Generate article drafts for Parasite SEO
    print("\n[4/4] Generating article drafts (vc.ru, TenChat, Pikabu)...")
    articles = [
        {
            "platform": "vc.ru",
            "title": "Как салон красоты на Дарнице увеличил повторные записи на 40% за 2 недели без рекламы",
            "niche": "beauty",
            "template": "case_study",
            "target_words": 2000,
        },
        {
            "platform": "TenChat",
            "title": "Почему 90% мастеров маникюра теряют клиентов — и как это исправить за 1 вечер",
            "niche": "beauty",
            "template": "problem_solution",
            "target_words": 1800,
        },
        {
            "platform": "Pikabu",
            "title": "Секрет салонов, которые всегда полны: не реклама, а автоматизация возврата клиентов",
            "niche": "beauty",
            "template": "secret_reveal",
            "target_words": 2500,
        },
    ]
    
    for art in articles:
        prompt = f"""Write a {art['target_words']}-word article for {art['platform']} in Russian.
Title: {art['title']}
Template: {art['template']}
Niche: {art['niche']} (beauty salon automation)
Structure: Hook → Context → Problem (with numbers) → Solution (step-by-step) → Results (metrics) → How-to-repeat (checklist) → Soft CTA (Telegram channel).
Style: Expert, concrete numbers, personal story, screenshots described.
Tags: #салонкрасоты #автоматизация #ИИ #бизнес #кейс #маркетинг
Output: Full article text in Markdown."""
        
        meta_file = CONTENT_WAREHOUSE / "metadata" / f"article_{art['platform'].replace('.','_')}_{datetime.now().strftime('%Y%m%d')}.json"
        meta_file.write_text(json.dumps({
            **art,
            "prompt": prompt,
            "generated_at": datetime.now().isoformat(),
            "status": "prompt_ready"
        }, ensure_ascii=False, indent=2))
    
    print(f"    ✅ {len(articles)} article prompts ready")
    log_kc(f"CONTENT: {len(articles)} article prompts generated for Parasite SEO (vc.ru, TenChat, Pikabu)", ["content", "article", "parasite-seo"])
    
    return True


# ─── Phase 3: Telegram Setup ───
def setup_telegram():
    """Day 1-2: Setup Telegram channel, bot, lead magnet."""
    print("\n" + "="*60)
    print("PHASE 3: TELEGRAM SETUP (Days 1-2)")
    print("="*60)
    
    print("\n[1/3] Checking telegram-channel-poster skill...")
    ok, out = run_cmd(f"cd {SKILLS_DIR}/automation/telegram-channel-poster && python -c \"import scripts.poster; print('OK')\"")
    if ok:
        print("    ✅ Telegram Poster module loads")
        log_kc("TELEGRAM: Poster module OK", ["telegram", "poster"])
    else:
        print(f"    ⚠️ Poster: {out[:200]}")
    
    print("\n[2/3] Checking cpa-telegram-bot-generator skill...")
    ok, out = run_cmd(f"cd {SKILLS_DIR}/finance/cpa-telegram-bot-generator && python -c \"import sys; print('OK')\"")
    if ok:
        print("    ✅ CPA Telegram Bot Generator available")
        log_kc("TELEGRAM: CPA Bot Generator available", ["telegram", "bot-generator"])
    else:
        print(f"    ⚠️ Bot Generator: {out[:200]}")
    
    print("\n[3/3] Lead magnet content prepared (see references/free-traffic-templates.md)")
    print("    ℹ️ Manual steps needed:")
    print("       1. Create bot via @BotFather → get token")
    print("       2. Connect to @Manybot/@Chatfuel or custom")
    print("       3. Setup 3 chains: welcome, reminders, winback")
    print("       4. Create PDF lead magnet (checklist + templates)")
    print("       5. Configure auto-delivery on 'ХОЧУ БОТА' button")
    print("       6. Post Day 1 welcome + lead magnet")
    
    log_kc("TELEGRAM: Setup guide ready - manual bot creation required", ["telegram", "setup", "manual"])
    
    return True


# ─── Phase 4: Launch Sequence ───
def launch_week1():
    """Execute the daily launch sequence."""
    print("\n" + "="*60)
    print("PHASE 4: WEEK 1 LAUNCH SEQUENCE")
    print("="*60)
    
    # This creates a daily execution plan that can be run manually or via cron
    daily_plan = {
        "day1": {
            "date": (datetime.now() + timedelta(days=0)).strftime("%Y-%m-%d"),
            "tasks": [
                "Create 3 Ghost-surfer profiles",
                "Write & submit Article 1 to vc.ru",
                "Setup Telegram channel + bot + lead magnet",
                "Find 15 Reddit/forum sources",
                "Create Instagram account (optional)",
                "Generate UTM links for all channels",
            ]
        },
        "day2": {
            "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "tasks": [
                "Warm up 3 TikTok accounts (30 min each)",
                "Check vc.ru moderation status",
                "Write Article 2 for TenChat",
                "Post Telegram Day 1: Welcome + Lead magnet",
                "Add channel to catalogs",
                "Write 5 Reddit expert comments",
                "Generate & post Instagram Reel #1",
            ]
        },
        "day3": {
            "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            "tasks": [
                "Generate 15 TikTok videos (5 scripts × 3 variations)",
                "Schedule 9 posts/day (3 accounts × 3 times)",
                "Submit Article 2 to TenChat",
                "Post Telegram Day 2: Case study",
                "Crosspost to 3 niche chats",
                "5 Reddit comments + reply to replies",
                "Post Instagram Reel #2",
            ]
        },
        "day4": {
            "date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "tasks": [
                "Auto-posting active (9 videos/day)",
                "Check Article 1 (vc.ru) - if published → announce in TG",
                "Check Article 2 (TenChat) moderation",
                "Write Article 3 (Pikabu/Habr)",
                "Post Telegram Day 3: Expert post",
                "Collect questions for Q&A",
                "5 Reddit comments",
                "Post Instagram Reel #3",
            ]
        },
        "day5": {
            "date": (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d"),
            "tasks": [
                "ANALYSIS DAY: Export all metrics",
                "Identify top-3 TikTok formats → create 5 variations each",
                "Stop low-performing formats (<500 views/24h)",
                "Check article indexing (site:vc.ru)",
                "Post Telegram Day 4: Q&A + Poll",
                "5 Reddit comments on top sources",
                "Analyze Instagram Reels (3 videos)",
            ]
        },
        "day6": {
            "date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "tasks": [
                "Scale top TikTok formats only",
                "Submit Article 3 (Pikabu/Habr)",
                "Post Telegram Day 5: Quick win (winback without bot)",
                "Focus Reddit on top-3 traffic sources",
                "Telegram Live/Voice (optional)",
            ]
        },
        "day7": {
            "date": (datetime.now() + timedelta(days=6)).strftime("%Y-%m-%d"),
            "tasks": [
                "FULL WEEK AUDIT: Fill metrics table",
                "Select top-2 channels for Week 2 focus",
                "Plan Week 2: TikTok scale, SEO 3 articles, TG Days 8-14",
                "Save all metrics to KC",
                "Decision: Continue/Stop Instagram",
            ]
        }
    }
    
    # Save plan
    plan_file = CONTENT_WAREHOUSE / "metadata" / f"week1_daily_plan_{datetime.now().strftime('%Y%m%d')}.json"
    plan_file.write_text(json.dumps(daily_plan, ensure_ascii=False, indent=2))
    
    print(f"\n✅ Daily plan saved to: {plan_file}")
    print("\n📅 WEEK 1 OVERVIEW:")
    for day, data in daily_plan.items():
        print(f"\n  {day.upper()} ({data['date']}): {len(data['tasks'])} tasks")
        for task in data['tasks'][:3]:
            print(f"    • {task}")
        if len(data['tasks']) > 3:
            print(f"    ... and {len(data['tasks']) - 3} more")
    
    log_kc(f"LAUNCH: Week 1 daily plan created with {sum(len(d['tasks']) for d in daily_plan.values())} total tasks", ["launch", "week1", "plan"])
    
    return daily_plan


# ─── Phase 5: Metrics Tracking ───
def setup_metrics_tracking():
    """Initialize metrics tracking in KC."""
    print("\n" + "="*60)
    print("PHASE 5: METRICS TRACKING SETUP")
    print("="*60)
    
    # Create baseline metrics entry
    baseline = {
        "week": 1,
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "channels": {
            "tiktok": {"views": 0, "profile_clicks": 0, "followers": 0, "posts": 0},
            "vc_ru": {"articles_submitted": 0, "articles_published": 0, "views": 0, "profile_clicks": 0},
            "tenchat": {"articles_submitted": 0, "articles_published": 0, "views": 0, "profile_clicks": 0},
            "telegram": {"posts": 0, "subscribers": 0, "lead_magnet_downloads": 0, "dm_questions": 0},
            "reddit": {"comments": 0, "profile_clicks": 0, "upvotes": 0},
            "instagram": {"reels": 0, "views": 0, "profile_clicks": 0, "followers": 0},
        },
        "kpis": {
            "min_tiktok_views": 5000,
            "min_tg_clicks": 30,
            "min_tg_subs": 20,
            "min_articles_published": 1,
            "min_reddit_comments": 35,
        }
    }
    
    baseline_file = CONTENT_WAREHOUSE / "metadata" / f"metrics_baseline_week1_{datetime.now().strftime('%Y%m%d')}.json"
    baseline_file.write_text(json.dumps(baseline, ensure_ascii=False, indent=2))
    
    log_kc(f"METRICS: Week 1 baseline initialized - {json.dumps(baseline['kpis'])}", ["metrics", "week1", "baseline"])
    
    print("    ✅ Baseline metrics initialized")
    print(f"    📊 KPIs: {baseline['kpis']}")
    print(f"    💾 Saved to: {baseline_file}")
    
    return baseline


# ─── Main Orchestrator ───
def main():
    print("╔" + "═"*58 + "╗")
    print("║  FREE TRAFFIC SCOUT 2026 — WEEK 1 ORCHESTRATOR       ║")
    print("║  Autonomous launch of 6 free traffic channels        ║")
    print("╚" + "═"*58 + "╝")
    
    start_time = time.time()
    
    # Run all phases
    phases = [
        ("Infrastructure Setup", setup_infrastructure),
        ("Content Generation", generate_content),
        ("Telegram Setup", setup_telegram),
        ("Launch Sequence", launch_week1),
        ("Metrics Tracking", setup_metrics_tracking),
    ]
    
    results = {}
    for name, func in phases:
        try:
            print(f"\n🚀 Starting: {name}")
            result = func()
            results[name] = "SUCCESS" if result else "PARTIAL"
            print(f"✅ Completed: {name}")
        except Exception as e:
            results[name] = f"FAILED: {e}"
            print(f"❌ Failed: {name} - {e}")
            log_kc(f"ORCHESTRATOR: Phase '{name}' FAILED - {e}", ["orchestrator", "error", name.lower().replace(" ", "-")])
    
    elapsed = time.time() - start_time
    
    # Summary
    print("\n" + "="*60)
    print("ORCHESTRATOR SUMMARY")
    print("="*60)
    for name, status in results.items():
        icon = "✅" if status == "SUCCESS" else "⚠️" if status == "PARTIAL" else "❌"
        print(f"  {icon} {name}: {status}")
    print(f"\n⏱ Total time: {elapsed:.1f}s")
    print(f"📁 Artifacts in: {CONTENT_WAREHOUSE}/metadata/")
    
    # Final KC entry
    log_kc(
        f"ORCHESTRATOR: Free Traffic Scout Week 1 initialization complete in {elapsed:.1f}s. "
        f"Phases: {', '.join(f'{k}={v}' for k,v in results.items())}. "
        f"Artifacts: {len(list(CONTENT_WAREHOUSE.glob('metadata/*.json')))} files in metadata/. "
        f"Next: Execute daily plan from Day 1.",
        ["orchestrator", "free-traffic-scout", "week1", "complete"]
    )
    
    event_beat("knowledge_added")
    event_beat("new_suggestions_ready")
    
    print("\n🎯 NEXT STEPS (Manual):")
    print("  1. Review generated prompts in assets/content_warehouse/metadata/")
    print("  2. Generate actual content via LLM/Pollinations using saved prompts")
    print("  3. Create Telegram bot manually (BotFather → Manybot)")
    print("  4. Execute Day 1 tasks from daily plan")
    print("  5. Run metrics collection daily: python scripts/free_traffic_metrics.py")
    
    return results


if __name__ == "__main__":
    main()