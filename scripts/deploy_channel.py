#!/usr/bin/env python3
"""Deploy Telegram Channel — Psychology / Self-development
Запуск: python scripts/deploy_channel.py
Вывод: пошаговая инструкция + ссылки на всё, что нужно

Никаких API, никаких токенов. Полная ручная упаковка.
"""

import os, glob, json
from datetime import datetime

CHANNEL_NAME = "🧠 Insight — психология простыми словами"
CHANNEL_USERNAME = "@InsightPsych"
POSTS_DIR = "reports/tg_psychology_channel/posts"
ASSETS_DIR = "assets"

print("""
╔════════════════════════════════════════════════╗
║   DEPLOY: Telegram Channel — Психология        ║
║   Всё готово. Твой шаг — создать канал.        ║
╚════════════════════════════════════════════════╝

────────────────────────────────────────────────────
""")

print(f"📌 Название:    {CHANNEL_NAME}")
print(f"📌 Юзернейм:    {CHANNEL_USERNAME}")
print(f"📌 Ниша:        Психология / Саморазвитие")
print(f"📌 Цена продажи: $80-200 за 500-1000 подп.")
print(f"📌 Постов:      45 вечнозелёных")
print(f"📌 Дата сборки: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print()

# ═══ ШАГ 1: АВАТАР ═══
print("═" * 55)
print("ШАГ 1: Аватар и обложка канала")
print("═" * 55)

avatar = f"{ASSETS_DIR}/tg_psych_avatar.png"
cover = f"{ASSETS_DIR}/tg_psych_cover.jpg"
growth = f"{ASSETS_DIR}/psych_visual_growth.jpg"

if os.path.exists(avatar):
    sz = os.path.getsize(avatar)
    print(f"  ✅ Аватар: {avatar} ({sz} байт)")
    print(f"     file:///D:/Portable_Soft/hermes/{avatar}")
else:
    print(f"  ❌ Аватар не найден. Создай сам через Pollinations")

if os.path.exists(cover):
    sz = os.path.getsize(cover)
    print(f"  ✅ Обложка: {cover} ({sz} байт)")
    print(f"     file:///D:/Portable_Soft/hermes/{cover}")

if os.path.exists(growth):
    sz = os.path.getsize(growth)
    print(f"  ✅ Доп.изобр.: {growth} ({sz} байт)")

print()

# ═══ ШАГ 2: ОПИСАНИЕ ═══
print("═" * 55)
print("ШАГ 2: Описание канала (скопируй в Telegram)")
print("═" * 55)
print()
print("🧠 Insight — психология простыми словами")
print()
print("Канал о том, как понять себя и других. Без сложных")
print("терминов, без воды, без нравоучений.")
print()
print("Каждый день:")
print("• Цитаты мудрецов — от стоиков до современных психологов")
print("• Практические советы — как перестать тревожиться,")
print("  найти мотивацию, полюбить себя")
print("• Книжные подборки — лучшие книги по психологии")
print("• Вопросы для саморефлексии — узнай себя лучше")
print()
print("Подписывайся и расти вместе с нами 🧠")
print()

# ═══ ШАГ 3: ПОСТЫ ═══
print("═" * 55)
print("ШАГ 3: 45 постов готовы к публикации")
print("═" * 55)
print()

posts = sorted(glob.glob(f"{POSTS_DIR}/post_*.html")) if os.path.exists(POSTS_DIR) else []
if posts:
    print(f"  Найдено {len(posts)} постов:")
    print()
    for i, p in enumerate(posts, 1):
        abspath = os.path.abspath(p)
        urlpath = f"file:///{abspath.replace(os.sep, '/')}"
        print(f"  [{i:2d}] {urlpath}")
    print()
    print(f"  Все посты: file:///{os.path.abspath('reports/tg_psychology_channel/index.html').replace(os.sep, '/')}")
else:
    print("  ❌ Посты не найдены.")

print()

# ═══ ШАГ 4: РОСТ ═══
print("═" * 55)
print("ШАГ 4: План роста 0→500 подписчиков")
print("═" * 55)
print()
print("  День 1-2:  Создать канал → выложить 10 постов")
print("             → пригласить 10 друзей → зарегистрировать")
print("             на tgstat.ru и tgram.ru")
print()
print("  День 3-5:  Mutual PR через pr-karusel, карусель обменов")
print("             Цель: 200 подписчиков")
print()
print("  День 5-7:  Кросс-постинг в чатах по саморазвитию")
print("             Цель: 350 подписчиков")
print()
print("  День 7-14: Органика + рекомендации + repost конкурсы")
print("             Цель: 500+ подписчиков → готов к продаже")
print()

# ═══ ШАГ 5: ПРОДАЖА ═══
print("═" * 55)
print("ШАГ 5: Продажа канала за USDT")
print("═" * 55)
print()
print("  1. Telega.io — выставить лот (5-10% комиссия)")
print("  2. SMM-FB.com — 0% с продавца, прямые сделки")
print("  3. Direct — найти покупателя в чатах, перевод USDT")
print("  4. Epicchange — обмен USDT на RUB/T-Bank")
print()
print("  Типичная цена: $80-150 за 500 подписчиков")
print("                 $150-300 за 1000 подписчиков")
print("                 (зависит от ER, живые/боты)")
print()

print("╔" + "═" * 50 + "╗")
print("║  ГОТОВО. 45 постов + аватар + описание + план.     ║")
print("║  Последний шаг — за тобой.                         ║")
print("║                                                     ║")
print("║  Настоящие изменения начинаются,                     ║")
print("║  когда ты сам принимаешь решение.                    ║")
print("╚" + "═" * 50 + "╝")
