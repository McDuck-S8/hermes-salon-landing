#!/usr/bin/env python3
"""Site-Mapper: Разведчик AI-сайтов.
Скрипт-помощник для создания карт сайтов.

Запуск: python scripts/site_mapper.py <url> [name]
Пример: python scripts/site_mapper.py https://leonardo.ai leonardo-ai
"""

import os, sys, json, re, glob
from datetime import datetime

SKILLS_DIR = "skills/site-maps"
os.makedirs(SKILLS_DIR, exist_ok=True)

def sanitize_name(name):
    return re.sub(r'[^a-z0-9-]', '', name.lower().replace('https://','').replace('www.','').split('/')[0])

def create_skill(url, name, data):
    """Создаёт SKILL.md карту сайта."""
    path = f"{SKILLS_DIR}/{name}"
    os.makedirs(path, exist_ok=True)

    # Скриншоты
    screenshots = data.get("screenshots", [])
    ss_md = ""
    for i, ss in enumerate(screenshots, 1):
        ext = os.path.splitext(ss)[0].split('_')[-1] if '_' in ss else f"screen{i}"
        src = ss.replace("\\", "/")
        ss_md += f"- ![Скриншот {i}]({src})\n"

    content = f"""---
name: site-map-{name}
description: "Карта сайта {url} — как пользоваться бесплатно"
version: 1.0.0
type: site-map
site_url: {url}
category: {data.get('category', 'image')}
free_limits: "{data.get('free_limits', '')}"
requires_login: {data.get('requires_login', False)}
requires_vpn: {data.get('requires_vpn', False)}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
---

# {data.get('title', name)} — Карта использования

## Что делает
{data.get('description', '')}

## Лимиты бесплатного использования
{data.get('free_limits', 'Не указано')}

## Пошаговая инструкция

"""
    for i, step in enumerate(data.get("steps", []), 1):
        content += f"""### Шаг {i}: {step.get('title', '')}
- **Элемент:** {step.get('element', '')}
- **Что делать:** {step.get('action', '')}
- **Результат:** {step.get('result', '')}

"""

    if data.get("problems"):
        content += "## Известные проблемы\n"
        for p in data["problems"]:
            content += f"- {p}\n"
        content += "\n"

    if data.get("example"):
        content += "## Пример использования\n"
        content += data["example"] + "\n"

    if screenshots:
        content += "\n## Скриншоты\n" + ss_md

    with open(f"{path}/SKILL.md", "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Карта сохранена: file:///D:/Portable_Soft/hermes/{path}/SKILL.md")
    return path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python scripts/site_mapper.py <url> [name]")
        print("Пример: python scripts/site_mapper.py https://leonardo.ai leonardo-ai")
        sys.exit(1)

    url = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else sanitize_name(url)
    print(f"🎯 Цель: {url}")
    print(f"📁 Карта: skills/site-maps/{name}/")
    print()
    print("Запусти вручную:")
    print(f"  1. Открой браузер: browser_navigate(url='{url}')")
    print(f"  2. Изучи интерфейс: browser_snapshot() + browser_vision()")
    print(f"  3. Собери данные в словарь")
    print(f"  4. Запусти: python scripts/site_mapper.py --save {url} {name}")
    print()
