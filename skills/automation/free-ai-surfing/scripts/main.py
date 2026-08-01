#!/usr/bin/env python3
"""
free-ai-surfing — Main entry point for WorkflowSupervisor.
Free AI content generation via Pollinations, HuggingFace, etc. No API keys needed.
"""
import sys
import json
import os
import urllib.request
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SCRIPTS_DIR = Path(os.environ.get("HERMES_HOME", Path(__file__).parent.parent.parent.parent)) / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

def run_phase(phase: str, config: dict):
    print(f"[free-ai-surfing] Phase: {phase}")
    print(f"[free-ai-surfing] Config: {json.dumps(config, ensure_ascii=False)}")
    
    if phase == "generate_video":
        return generate_video(config)
    elif phase == "generate_image":
        return generate_image(config)
    elif phase == "generate_reels":
        return generate_reels(config)
    elif phase == "generate_article":
        return generate_article(config)
    else:
        return {"status": "unknown_phase", "phase": phase}


def generate_video(config: dict):
    """Generate video via Pollinations AI."""
    count = config.get("count", 1)
    templates = config.get("templates", ["problem_solution", "expert_lifehack", "before_after", "education_60sec", "myth_busting"])
    
    results = {"videos": []}
    
    prompts = {
        "problem_solution": "beauty salon transformation before after manicure cinematic lighting 9:16",
        "expert_lifehack": "beauty master working calm client happy professional lighting 9:16",
        "before_after": "nail art process close up satisfying ASMR 9:16",
        "education_60sec": "salon reception empty then full clients booking phone 9:16",
        "myth_busting": "master showing phone with bot appointment confirmation smile 9:16",
    }
    
    for i in range(count):
        template = templates[i % len(templates)]
        prompt = prompts.get(template, "beauty salon automation cinematic 9:16")
        encoded = urllib.parse.quote(prompt)
        url = f"https://video.pollinations.ai/prompt/{encoded}?width=720&height=1280&model=flux&nologo=true&seed={42+i}"
        
        results["videos"].append({
            "template": template,
            "prompt": prompts[template],
            "url": url,
            "seed": 42+i
        })
    
    print(f"[free-ai-surfing] Generated {len(results['videos'])} video URLs")
    return {"status": "completed", "results": results}


def generate_image(config: dict):
    """Generate image via Pollinations AI."""
    count = config.get("count", 1)
    styles = config.get("styles", ["process", "pov_admin", "client_journey", "myth_busting", "results"])
    
    results = {"images": []}
    
    prompts = {
        "process": "beauty salon before after manicure transformation split screen professional",
        "pov_admin": "calm salon admin drinking coffee looking at tablet with booking calendar",
        "client_journey": "client journey: phone screen -> bot -> calendar -> confirmed -> happy client",
        "myth_busting": "myth busting: coding complex vs drag-drop bot builder reality",
        "results": "beauty salon before after manicure transformation split screen professional",
    }
    
    for i in range(count):
        style = styles[i % len(styles)]
        prompt = prompts.get(style, "beauty salon automation professional")
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1350&model=flux&nologo=true&seed={100+i}"
        
        results["images"].append({
            "style": style,
            "prompt": prompts[style],
            "url": url,
            "seed": 100+i
        })
    
    print(f"[free-ai-surfing] Generated {len(results['images'])} image URLs")
    return {"status": "completed", "results": results}


def generate_reels(config: dict):
    """Generate Instagram Reels assets."""
    count = config.get("count", 3)
    prompts_file = config.get("prompts", "references/free-traffic-templates.md")
    
    # Use the same generate_image logic for Reels (vertical 9:16)
    config["count"] = count
    config["styles"] = ["process", "pov_admin", "client_journey", "myth_busting", "results"][:count]
    
    return generate_image(config)


def generate_article(config: dict):
    """Generate article for Parasite SEO platforms."""
    platform = config.get("platform", "vc_ru")
    template = config.get("template", "case_study")
    
    articles = {
        "vc_ru": {
            "case_study": {
                "title": "Как салон красоты на Дарнице увеличил повторные записи на 40% за 2 недели без рекламы",
                "template": "case_study",
                "tags": ["салонкрасоты", "автоматизация", "ИИ", "бизнес", "кейс", "маркетинг"],
                "content": """Вчера мастер Аня сказала: "Раньше я теряла 3-4 клиента в неделю просто потому что забывала перезвонить. Теперь бот делает это за меня."

Ситуация:
- Салон: «Эстетика», район Дарница
- Мастеров: 3
- Записей в месяц: 150
- Проблема: нет напоминаний / теряют лиды / нет CRM

Что было (цифры):
- Потеря клиентов: 25% в месяц
- LTV клиента: 800 грн
- Ручная работа администратора: 6 ч/нед

Решение (что внедрили за 1 вечер):
1. Подключили ИИ-бота для записи в Telegram (бесплатно, 15 мин настройки)
2. Настроили авто-напоминания за 24ч и 2ч
3. Добавили "Возвращающее" сообщение через 3 недели: "Привет! Давно не виделись, скидка 15% на любое покрытие"

Инструменты:
- Бот: @manybot (бесплатно)
- Шаблон сообщений: [ССЫЛКА НА ГУГЛ-ДОК]
- Настройка за 15 мин: [ССЫЛКА НА ВИДЕО/СТАТЬЮ]

Результат (через 2 недели):
✅ Повторки: +38%
✅ No-show: -80%
✅ Время админа: -6 ч/нед
✅ Доп. выручка: +42 000 грн/мес

Хочешь то же? Забирай готовый бот + шаблоны сообщений в профиле: @твой_тг_канал

P.S. Никакого спама — только лайфхаки для салонов 2-3 раза в неделю."""
            }
        },
        "tenchat": {
            "problem_solution": {
                "title": "Почему 90% мастеров маникюра теряют клиентов — и как это исправить за 1 вечер",
                "template": "problem_solution",
                "tags": ["маникюр", "бизнес", "автоматизация", "клиенты", "CRM"],
                "content": """..."""
            }
        },
        "pikabu": {
            "secret_reveal": {
                "title": "Секрет салонов, которые всегда полны: не реклама, а автоматизация возврата клиентов",
                "template": "secret_reveal",
                "tags": ["бизнес", "салоны", "автоматизация", "клиенты", "деньги"],
                "content": """..."""
            }
        }
    }
    
    platform_articles = articles.get(platform, {})
    article = platform_articles.get(template, {})
    
    return {"status": "completed", "results": {"article": article}}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    parser.add_argument("--config", default="{}")
    args = parser.parse_args()
    
    config = json.loads(args.config)
    result = run_phase(args.phase, config)
    print(json.dumps(result, ensure_ascii=False))