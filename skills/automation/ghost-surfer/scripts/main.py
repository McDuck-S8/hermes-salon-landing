#!/usr/bin/env python3
"""
ghost-surfer — Main entry point for WorkflowSupervisor.
Anonymous browser automation: profile creation, expert comments, forum engagement.
"""
import sys
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SCRIPTS_DIR = Path(os.environ.get("HERMES_HOME", Path(__file__).parent.parent.parent.parent)) / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

def run_phase(phase: str, config: dict):
    print(f"[ghost-surfer] Phase: {phase}")
    print(f"[ghost-surfer] Config: {json.dumps(config, ensure_ascii=False)}")
    
    if phase == "create_profiles":
        return create_profiles(config)
    elif phase == "expert_comments":
        return expert_comments(config)
    elif phase == "find_topics":
        return find_topics(config)
    elif phase == "post_instagram_reels":
        return post_instagram_reels(config)
    else:
        return {"status": "unknown_phase", "phase": phase}


def create_profiles(config: dict):
    """Create browser profiles for different niches."""
    niches = config.get("niches", ["beauty", "education", "services"])
    proxy = config.get("proxy", "socks5://127.0.0.1:10806")
    
    results = {"profiles": []}
    for niche in niches:
        profile_name = f"{niche}_surfer"
        results["profiles"].append({
            "name": profile_name,
            "niche": niche,
            "proxy": proxy,
            "action": f"browser-harness new_profile --name {profile_name} --proxy {proxy}"
        })
    
    print(f"[ghost-surfer] Created {len(results['profiles'])} profiles")
    return {"status": "completed", "results": results}


def find_topics(config: dict):
    """Find relevant topics/questions on forums and social media."""
    sources = config.get("sources", 15)
    niches = config.get("niches", ["beauty", "small_business", "automation"])
    
    # Search queries for each niche
    queries = {
        "beauty": ["salon automation", "no-show clients beauty", "beauty salon CRM", "auto booking salon"],
        "small_business": ["small business automation", "CRM for small business", "client retention small business"],
        "automation": ["AI automation business", "no-code automation", "bot automation business"]
    }
    
    results = {"queries": [], "sources": []}
    
    for niche in niches:
        for query in queries.get(niche, []):
            results["queries"].append({
                "niche": niche,
                "query": query,
                "platforms": ["reddit", "telegram_chats", "vc.ru", "forums"]
            })
    
    print(f"[ghost-surfer] Generated {len(results['queries'])} search queries")
    return {"status": "completed", "results": results}


def expert_comments(config: dict):
    """Post expert comments on forums/social media."""
    comments_per_day = config.get("comments_per_day", 5)
    niches = config.get("niches", ["beauty", "small_business", "automation"])
    sources = config.get("sources", 15)
    
    # Comment templates
    templates = {
        "beauty": [
            "Настроил бесплатного бота в Телеграм за 15 минут. Теперь клиенты записываются сами 24/7, бот сам напоминает за сутки и за 2 часа (no-show упал с 25% до 5%), а через 21 день «спящим» клиентам уходит предложение со скидкой — возвращаются 10-15%. Инструменты: @Manybot (бесплатно) + Google Таблицы как CRM. Экономит ~5 часов в неделю админа.",
            "Проблема no-show в салонах решается не СМС-шлюзами, а бесплатным ботом. Настроил за 15 мин: напоминание 24ч/2ч + кнопки «Приду/Перенести/Отменить» + возврат через 21 день со скидкой. No-show 25% → 5%. Админ 0ч на звонки вместо 6ч/нед. Бесплатно, без программиста."
        ],
        "small_business": [
            "Для малого бизнеса не нужна дорогая CRM/СМС-шлюз. Бесплатный бот @Manybot + Google Таблицы = полноценная CRM: записи, напоминания, возвраты, апсейлы. Настройка 15 мин. Экономия 15-30к грн/мес на ПО + админ.",
            "Многие думают: «боты сложные, нужен программист». Неправда. @Manybot / @Chatfuel — конструкторы drag-and-drop. Создаёшь блоки: приветствие → календарь → подтверждение → напоминание → возврат. Без кода. 15 мин настройки."
        ],
        "automation": [
            "Автоматизация записи в салоне — не про «технологии», а про «клиент не ждёт». Бот принимает запись за 30 сек в 3 клика. Админ освобождается. No-show падает за счёт авто-напоминаний. ROI бесконечный — инструменты бесплатные."
        ]
    }
    
    results = {"comments_planned": 0, "by_niche": {}}
    
    for niche in niches:
        comments = []
        for i in range(min(comments_per_day, len(templates.get(niche, [])))):
            comments.append({
                "niche": niche,
                "text": templates[niche][i],
                "cta": "Хочешь повторить? Чек-лист + шаблоны в профиле @max_brain_chef_official"
            })
        results["by_niche"][niche] = comments
        results["comments_planned"] += len(comments)
    
    print(f"[ghost-surfer] Planned {results['comments_planned']} expert comments")
    return {"status": "completed", "results": results}


def post_instagram_reels(config: dict):
    """Generate and post Instagram Reels via BrowserOS."""
    return {
        "status": "ready",
        "action": "generate_images_via_pollinations_then_upload_via_browseros",
        "note": "Requires Instagram profile in browser-harness"
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    parser.add_argument("--config", default="{}")
    args = parser.parse_args()
    
    config = json.loads(args.config)
    result = run_phase(args.phase, config)
    print(json.dumps(result, ensure_ascii=False))