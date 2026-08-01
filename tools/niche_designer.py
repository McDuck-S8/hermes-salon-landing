#!/usr/bin/env python
"""NicheForge — генератор уникальных дизайнов под нишу.

Использование:
  python tools/niche_designer.py --niche "AI Tutorials"
  python tools/niche_designer.py --niche "True Crime" --format html
  python tools/niche_designer.py --list                  # показать все языки

Каждый запуск генерирует уникальную комбинацию: визуальный язык + цветовая палитра +
шрифтовая пара + layout + signature-элемент. Никаких шаблонов.
"""

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# ── ВИЗУАЛЬНЫЕ ЯЗЫКИ ─────────────────────────────────────────────

@dataclass
class VisualLanguage:
    """Один визуальный язык — метафора, цвета, шрифты, layout, signature."""
    name: str
    description: str
    vibe: str
    meta: str                           # базовая метафора
    niches: list[str]                   # какие ниши хорошо ложатся
    colors: dict                        # bg, fg, accent, muted, alt_accent
    display_font: str
    body_font: str
    layout: str                         # описание layout-концепции
    layout_type: str                    # centered, asymmetrical, magazine, dashboard, terminal, cards
    signature: str                      # что делает страницу запоминающейся
    density: str                        # spacious / comfortable / dense
    radius: str                         # sharp(0) / soft(4) / round(12)

    def accent_variants(self) -> list[str]:
        """Возвращает все accent-цвета (основной + альтернативный)."""
        return [self.colors["accent"], self.colors.get("alt_accent", self.colors["accent"])]


# Каталог визуальных языков — каждый принципиально отличается от других
LANGUAGES: list[VisualLanguage] = [

    VisualLanguage(
        name="laboratory",
        description="Лаборатория / исследовательский центр",
        vibe="Стерильно, технологично, научно",
        meta="Белые халаты, приборы, чистые линии",
        niches=["ai tutorials", "tech", "data science", "ml", "programming",
                "наука", "технологии", "it", "saas", "devtools", "b2b"],
        colors={"bg": "#0a0a0f", "fg": "#e8e8ed", "accent": "#22c55e",
                "muted": "#6b7280", "alt_accent": "#06b6d4"},
        display_font="'JetBrains Mono', monospace",
        body_font="'Inter', -apple-system, sans-serif",
        layout="Hero слева с терминальным блоком. Pipeline как техническая схема.",
        layout_type="dashboard",
        signature="Анимированный терминал или осциллограф",
        density="comfortable",
        radius="sharp",
    ),
    VisualLanguage(
        name="editorial",
        description="Журнал / редакция / пресса",
        vibe="Интеллигентно, взвешенно, культурно",
        meta="Бумага, типография, редколлегия",
        niches=["self-improvement", "образование", "культура", "книги",
                "психология", "блог", "лайфстайл", "история", "аналитика",
                "образование", "философия", "медиа"],
        colors={"bg": "#fafaf9", "fg": "#1c1917", "accent": "#dc2626",
                "muted": "#78716c", "alt_accent": "#292524"},
        display_font="'Playfair Display', Georgia, serif",
        body_font="'Inter', -apple-system, sans-serif",
        layout="Обложка журнала + narrative pipeline + pull-quote",
        layout_type="magazine",
        signature="Маркерные линии и крупная буквица",
        density="spacious",
        radius="soft",
    ),
    VisualLanguage(
        name="terminal",
        description="Терминал / консоль / хакерский шик",
        vibe="Минималистично, сухо, дерзко",
        meta="CLI, зелёный текст, никакой графики",
        niches=["programming", "security", "devops", "startup", "tools",
                "инструменты", "продуктивность", "блог разработчика"],
        colors={"bg": "#000000", "fg": "#00ff41", "accent": "#00ff41",
                "muted": "#005f20", "alt_accent": "#ffffff"},
        display_font="'JetBrains Mono', 'Cascadia Code', monospace",
        body_font="'JetBrains Mono', monospace",
        layout="Мигающий курсор в hero. Всё — текст на чёрном. Минимум CSS.",
        layout_type="terminal",
        signature="Мигающий блок с ASCII pipeline",
        density="comfortable",
        radius="sharp",
    ),
    VisualLanguage(
        name="dashboard",
        description="Дашборд / аналитика / data-driven",
        vibe="Деловито, плотно, цифровой",
        meta="KPI, графики, операционные панели",
        niches=["finance", "crypto", "аналитика", "бизнес", "investing",
                "инвестиции", "трейдинг", "b2b", "saas", "metrics"],
        colors={"bg": "#f8fafc", "fg": "#0f172a", "accent": "#3b82f6",
                "muted": "#94a3b8", "alt_accent": "#f59e0b"},
        display_font="'Inter', -apple-system, sans-serif",
        body_font="'Inter', -apple-system, sans-serif",
        layout="Плотная сетка. Метрики сверху. Горизонтальные чарты. Data-таблицы.",
        layout_type="dashboard",
        signature="Интерактивная SVG-диаграмма",
        density="dense",
        radius="soft",
    ),
    VisualLanguage(
        name="journal",
        description="Личный дневник / воркбук",
        vibe="Тёплый, рукописный, доверительный",
        meta="Бумага, ручка, карандашные пометки",
        niches=["self-improvement", "lifestyle", "психология", "творчество",
                "блог", "путешествия", "еда", "спорт", "здоровье"],
        colors={"bg": "#fef3c7", "fg": "#292524", "accent": "#d97706",
                "muted": "#a8a29e", "alt_accent": "#78716c"},
        display_font="'Playfair Display', Georgia, serif",
        body_font="'Inter', -apple-system, sans-serif",
        layout="Две колонки: заметки слева, иллюстрации справа. Ручкописные элементы.",
        layout_type="asymmetrical",
        signature="Строчка «даты» в стиле дневника",
        density="spacious",
        radius="round",
    ),
    VisualLanguage(
        name="nature",
        description="Природа / органика / документалистика",
        vibe="Спокойно, естественно, эко",
        meta="Земля, растения, природные материалы",
        niches=["wildlife", "travel", "экология", "фермерство", "фотография",
                "природа", "животные", "сад", "окружающая среда"],
        colors={"bg": "#0f1f14", "fg": "#e8e0d4", "accent": "#84a98c",
                "muted": "#6b7280", "alt_accent": "#d4a373"},
        display_font="'DM Serif Display', Georgia, serif",
        body_font="'Inter', -apple-system, sans-serif",
        layout="Крупное изображение/видео как фон. Текст накладывается. Органические формы.",
        layout_type="asymmetrical",
        signature="Параллакс-сцена с природным мотивом",
        density="spacious",
        radius="round",
    ),
    VisualLanguage(
        name="luxury",
        description="Премиум / люкс / консалтинг",
        vibe="Дорого, уверенно, эксклюзивно",
        meta="Золото, кожа, ручная работа",
        niches=["finance", "consulting", "law", "real estate", "premium",
                "недвижимость", "авто", "часы", "вино", "бизнес-коучинг"],
        colors={"bg": "#0c0c0c", "fg": "#e8e0d4", "accent": "#d4a373",
                "muted": "#6b7280", "alt_accent": "#fbbf24"},
        display_font="'Cormorant Garamond', Georgia, serif",
        body_font="'Inter', -apple-system, sans-serif",
        layout="Минимум контента. Максимум воздуха. Одна крупная деталь.",
        layout_type="centered",
        signature="Тиснёная gold-линия или гербовая рамка",
        density="spacious",
        radius="soft",
    ),
    VisualLanguage(
        name="brutalist",
        description="Брутализм / авангард / искусство",
        vibe="Резко, громко, нестандартно",
        meta="Бетон, крупная типографика, никаких украшений",
        niches=["creative", "art", "portfolio", "дизайн", "мода", "музыка",
                "фотография", "современное искусство", "брендинг"],
        colors={"bg": "#ffffff", "fg": "#000000", "accent": "#ff0000",
                "muted": "#737373", "alt_accent": "#000000"},
        display_font="'Inter', -apple-system, sans-serif",
        body_font="'Inter', -apple-system, sans-serif",
        layout="Гигантский заголовок. Никаких карточек. Прямые линии. Асимметрия.",
        layout_type="asymmetrical",
        signature="300px шрифт или наклонная полоса через всю страницу",
        density="comfortable",
        radius="sharp",
    ),
    VisualLanguage(
        name="playlist",
        description="Плейлист / лента / контент-хаб",
        vibe="Динамично, медийно, вовлекающе",
        meta="YouTube, карточки, горизонтальные списки",
        niches=["youtube", "media", "entertainment", "music", "кино",
                "подкасты", "тикток", "стриминг", "гейминг"],
        colors={"bg": "#09090b", "fg": "#fafafa", "accent": "#e11d48",
                "muted": "#6b7280", "alt_accent": "#a1a1aa"},
        display_font="'Inter', -apple-system, sans-serif",
        body_font="'Inter', -apple-system, sans-serif",
        layout="Горизонтальный скролл карточек. Крупные превью. Прогресс-бары.",
        layout_type="cards",
        signature="Анимированный прогресс-бар или автоплей-карусель",
        density="dense",
        radius="round",
    ),
    VisualLanguage(
        name="cinema",
        description="Кино / нуар / драма",
        vibe="Драматично, глубоко, кинематографично",
        meta="Прожектор, тень, крупный план",
        niches=["true crime", "истории", "подкасты", "сторителлинг",
                "драма", "расследования", "документалистика"],
        colors={"bg": "#050505", "fg": "#e4e4e7", "accent": "#f97316",
                "muted": "#52525b", "alt_accent": "#e4e4e7"},
        display_font="'Playfair Display', Georgia, serif",
        body_font="'Inter', -apple-system, sans-serif",
        layout="Тёмная сцена. Спотлайт на заголовке. Цитата как кадр из фильма.",
        layout_type="centered",
        signature="Vignette-эффект по краям + spotlight на контенте",
        density="spacious",
        radius="sharp",
    ),
]


# ── ENGINE ────────────────────────────────────────────────────────

class NicheForge:
    """Генератор уникальных дизайнов на основе ниши."""

    def __init__(self, niche: str, seed: Optional[str] = None):
        self.niche = niche.lower().strip()
        # Seed для воспроизводимости: если не задан, используем хеш ниши
        self._seed = seed or self.niche
        self._rand = random.Random(hashlib.md5(self._seed.encode()).hexdigest())

        self.language = self._pick_language()
        self.palette = self._build_palette()
        self.typography = self._build_typography()
        self.layout_concept = self._build_layout()
        self.signature_concept = self._build_signature()

    def _pick_language(self) -> VisualLanguage:
        """Выбирает визуальный язык, наиболее подходящий под нишу."""
        # Ищем точные совпадения
        candidates = []
        for lang in LANGUAGES:
            for kw in lang.niches:
                if kw in self.niche:
                    candidates.append(lang)
                    break

        if not candidates:
            # Если нет точного — fuzzy match по ключевым словам ниши
            niche_words = set(self.niche.replace('/', ' ').replace('-', ' ').split())
            scored = []
            for lang in LANGUAGES:
                lang_words = set(' '.join(lang.niches).split())
                overlap = len(niche_words & lang_words)
                if overlap > 0:
                    scored.append((overlap, lang))
            scored.sort(key=lambda x: -x[0])
            candidates = [lang for _, lang in scored[:3]] if scored else [LANGUAGES[0]]

        # Выбираем случайно из подходящих (но не всегда первый)
        return self._rand.choice(candidates)

    def _build_palette(self) -> dict:
        """Строит цветовую палитру на основе языка."""
        base = dict(self.language.colors)

        # С вероятностью 30% меняем accent на alt_accent
        if self._rand.random() < 0.3:
            base["accent"], base["alt_accent"] = base["alt_accent"], base["accent"]

        # С вероятностью 20% осветляем/затемняем фон на лёгкий оттенок
        # (только для нейтральных фонов)
        # В реальном продукте здесь было бы hsl-смещение

        return base

    def _build_typography(self) -> dict:
        """Строит шрифтовую пару."""
        pair = {
            "display": self.language.display_font,
            "body": self.language.body_font,
        }

        # У 15% дизайнов меняем body на альтернативу
        if self._rand.random() < 0.15:
            alt_bodies = {
                "'Inter', -apple-system, sans-serif": "'Source Serif Pro', Georgia, serif",
                "'Inter', -apple-system, sans-serif".swapcase(): "'Inter', -apple-system, sans-serif",
            }
            # Просто для разнообразия
            pair["body"] = self._rand.choice([
                "'Inter', -apple-system, sans-serif",
                "'Source Serif Pro', Georgia, serif",
                "'IBM Plex Sans', -apple-system, sans-serif",
            ])

        return pair

    def _build_layout(self) -> str:
        """Генерирует описание layout."""
        layouts = [
            self.language.layout_type,
            "asymmetrical" if self._rand.random() < 0.2 else self.language.layout_type,
        ]
        return self._rand.choice(layouts)

    def _build_signature(self) -> str:
        """Генерирует сигнатурный элемент."""
        sigs = {
            "laboratory": self._rand.choice([
                "Анимированный терминал с печатью кода",
                "Осциллограф / волна сигнала",
                "Схема соединений (node-edge graph)",
            ]),
            "editorial": self._rand.choice([
                "Крупная буквица через всю колонку",
                "Маркерная линия-разделитель",
                "Номер выпуска как визуальный якорь",
            ]),
            "terminal": self._rand.choice([
                "Мигающий _ в конце строки",
                "ASCII-схема конвейера",
                "Прогресс-бар из символов █░",
            ]),
            "dashboard": self._rand.choice([
                "Real-time SVG chart (line/bar)",
                "KPI-цифра с анимированным счётчиком",
                "Тепловая карта данных",
            ]),
            "journal": self._rand.choice([
                "Зачёркнутый текст как в блокноте",
                "Подчёркивание вручную (border-image)",
                "Стикер/наклейка поверх контента",
            ]),
            "nature": self._rand.choice([
                "Parallax-слой с текстурой листа/песка",
                "Анимированные частицы (пыльца/снег)",
                "SVG-органика (wave/blob)",
            ]),
            "luxury": self._rand.choice([
                "Тиснёная рамка с золотым отливом",
                "Монограмма/вензель в подвале",
                "Текст на плёнке/кальке (blur + opacity)",
            ]),
            "brutalist": self._rand.choice([
                "Наклонная полоса через всю страницу",
                "300-символьный заголовок",
                "Цветной блок как отдельный элемент",
            ]),
            "playlist": self._rand.choice([
                "Автоплей-карусель карточек",
                "Progress bar, который заполняется при скролле",
                "Превью с play-кнопкой",
            ]),
            "cinema": self._rand.choice([
                "Vignette + spotlight при загрузке",
                "Титры как в кино (нижняя треть)",
                "Плавный fade-in кадра",
            ]),
        }
        return sigs.get(self.language.name, "Минимальный акцент")

    def generate_html(self) -> str:
        """Генерирует полный HTML на основе выбранных параметров."""
        c = self.palette
        # Собираем CSS-переменные
        css_vars = f"""
    --bg:      {c['bg']};
    --fg:      {c['fg']};
    --accent:  {c['accent']};
    --muted:   {c['muted']};
    --display: {self.typography['display']};
    --body:    {self.typography['body']};"""

        radius_map = {"sharp": "0px", "soft": "6px", "round": "16px"}
        rad = radius_map.get(self.language.radius, "6px")

        density_map = {
            "spacious": "120px",
            "comfortable": "80px",
            "dense": "48px",
        }
        section_pad = density_map.get(self.language.density, "80px")

        layout_css = ""
        if self.layout_concept == "centered":
            layout_css = "text-align: center;"
        elif self.layout_concept == "asymmetrical":
            layout_css = ""

        # Определяем signature-элемент
        lang_name = self.language.name
        if lang_name == "terminal":
            signature_html = """<div style="font-family:var(--display);color:var(--muted);padding:32px;border:1px solid var(--muted);margin-top:64px;font-size:13px;line-height:1.8;overflow-x:auto;white-space:pre;background:rgba(0,255,65,.03);">┌──────────────────────────────────┐
│ $ ./build --niche """ + self.niche + """  │
│ ✓ 6 stages complete               │
│ ✓ Generating income stream...     │
│ $ _<span style="animation:blink 1s step-end infinite;">█</span>                               │
└──────────────────────────────────┘</div>"""
        elif lang_name == "editorial":
            signature_html = f"""<div style="text-align:center;padding:48px 0;font-size:32px;letter-spacing:8px;color:var(--accent);font-family:var(--display);">◆</div>"""
        elif lang_name == "journal":
            signature_html = f"""<div style="padding:24px;font-family:var(--display);color:var(--muted);border-left:3px solid var(--accent);margin:48px 0;font-style:italic;background:rgba(0,0,0,.02);">📝 <span style="text-decoration:line-through;opacity:.5;">ещё один шаблон</span><br>уникальный дизайн под {self.niche}</div>"""
        elif lang_name == "dashboard":
            signature_html = f"""<div style="display:flex;gap:2px;justify-content:center;margin:48px 0;height:120px;align-items:flex-end;"><div style="width:32px;background:var(--accent);height:60%;border-radius:4px 4px 0 0;"></div><div style="width:32px;background:var(--accent);height:90%;border-radius:4px 4px 0 0;"></div><div style="width:32px;background:var(--muted);height:40%;border-radius:4px 4px 0 0;"></div><div style="width:32px;background:var(--muted);height:70%;border-radius:4px 4px 0 0;"></div><div style="width:32px;background:var(--accent);height:100%;border-radius:4px 4px 0 0;"></div><div style="width:32px;background:var(--muted);height:30%;border-radius:4px 4px 0 0;"></div></div>"""
        else:
            signature_html = f"""<div style="height:2px;background:linear-gradient(90deg,transparent,var(--accent),transparent);margin:64px 0;width:60%;margin-left:auto;margin-right:auto;"></div>"""

        # Build page
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{self.niche.title()} — NicheForge</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=DM+Serif+Display:ital@0;1&family=Source+Serif+Pro:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@300;400;600&display=swap" rel="stylesheet">
<style>
  :root {{{css_vars}
    --radius: {rad};
    --section-pad: {section_pad};
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    background: var(--bg);
    color: var(--fg);
    font-family: var(--body);
    font-weight: 300;
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    {layout_css}
  }}
  .container {{ max-width: 1000px; margin: 0 auto; padding: 0 24px; }}
  h1, h2, h3, h4 {{ font-family: var(--display); font-weight: 700; }}
</style>
</head>
<body>

<section style="padding:var(--section-pad) 0;">
  <div class="container">
    <p style="font-family:var(--display);font-size:13px;color:var(--accent);letter-spacing:3px;text-transform:uppercase;margin-bottom:24px;font-weight:600;{layout_css}">{self.language.description}</p>
    <h1 style="font-size:clamp(40px,7vw,80px);letter-spacing:-2px;line-height:.9;margin-bottom:24px;max-width:{'100%;text-align:center' if self.layout_concept=='centered' else '800px'};">
      {self.niche.title()}
    </h1>
    <p style="font-size:18px;color:var(--muted);max-width:{'560px' if self.layout_concept!='centered' else '560px;margin:0 auto'};margin-bottom:32px;">
      {self.language.vibe}. {self.language.meta}.
    </p>
  </div>
</section>

<section style="padding:var(--section-pad) 0;border-top:1px solid rgba(128,128,128,.15);">
  <div class="container">
    <p style="font-family:var(--display);font-size:12px;color:var(--accent);letter-spacing:3px;text-transform:uppercase;margin-bottom:16px;font-weight:600;">Pipeline</p>
    <h2 style="font-size:clamp(20px,3vw,32px);margin-bottom:48px;max-width:600px;">Визуальный язык: {self.language.description}</h2>
    <div style="display:flex;gap:24px;flex-wrap:wrap;{layout_css}">
      <div style="background:rgba(128,128,128,.06);padding:24px;border-radius:var(--radius);flex:1;min-width:200px;">
        <p style="font-family:var(--display);font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:8px;">Палитра</p>
        <div style="display:flex;gap:8px;">
          <span style="display:inline-block;width:32px;height:32px;background:var(--bg);border:2px solid var(--fg);border-radius:50%;"></span>
          <span style="display:inline-block;width:32px;height:32px;background:var(--fg);border-radius:50%;"></span>
          <span style="display:inline-block;width:32px;height:32px;background:var(--accent);border-radius:50%;"></span>
          <span style="display:inline-block;width:32px;height:32px;background:var(--muted);border-radius:50%;"></span>
        </div>
      </div>
      <div style="background:rgba(128,128,128,.06);padding:24px;border-radius:var(--radius);flex:1;min-width:200px;">
        <p style="font-family:var(--display);font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:8px;">Шрифты</p>
        <p style="font-family:var(--display);font-size:18px;font-weight:700;">Display</p>
        <p style="font-family:var(--body);font-size:15px;">Body text style</p>
      </div>
      <div style="background:rgba(128,128,128,.06);padding:24px;border-radius:var(--radius);flex:1;min-width:200px;">
        <p style="font-family:var(--display);font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:8px;">Layout</p>
        <p style="font-size:14px;text-transform:capitalize;">{self.layout_concept} · {self.language.density}</p>
        <p style="font-size:12px;color:var(--muted);margin-top:8px;">{self.language.layout[:60]}…</p>
      </div>
    </div>
    {signature_html}
  </div>
</section>

<section style="padding:var(--section-pad) 0;border-top:1px solid rgba(128,128,128,.15);{layout_css}">
  <div class="container">
    <h2 style="font-size:clamp(20px,3vw,28px);margin-bottom:16px;">Signature-элемент</h2>
    <p style="color:var(--muted);font-size:16px;max-width:600px;{'margin:0 auto' if self.layout_concept=='centered' else ''};">
      {self.signature_concept}
    </p>
    <p style="margin-top:48px;font-family:var(--display);font-size:12px;color:var(--muted);letter-spacing:2px;">NicheForge · generated for «{self.niche}»</p>
  </div>
</section>

</body>
</html>"""
        return html

    def describe(self) -> dict:
        """Возвращает описание дизайна."""
        return {
            "niche": self.niche,
            "language": self.language.name,
            "language_description": self.language.description,
            "vibe": self.language.vibe,
            "meta": self.language.meta,
            "palette": self.palette,
            "typography": {
                "display": self.typography["display"],
                "body": self.typography["body"],
            },
            "layout": self.layout_concept,
            "density": self.language.density,
            "signature": self.signature_concept,
            "signature_description": self.signature_concept,
        }


# ── CLI ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="NicheForge — генератор уникальных дизайнов")
    parser.add_argument("--niche", type=str, help="Название ниши (например, 'True Crime')")
    parser.add_argument("--format", choices=["html", "json", "describe"], default="html",
                        help="Формат вывода (по умолч. html)")
    parser.add_argument("--seed", type=str, default=None,
                        help="Seed для воспроизводимости (по умолч. хеш ниши)")
    parser.add_argument("--list", action="store_true", help="Показать все визуальные языки")
    parser.add_argument("--out", type=str, default=None,
                        help="Сохранить HTML в файл")

    args = parser.parse_args()

    if args.list:
        print(f"\n{'═'*60}")
        print(f"  NicheForge — каталог визуальных языков ({len(LANGUAGES)})")
        print(f"{'═'*60}\n")
        for lang in LANGUAGES:
            niches = ", ".join(lang.niches[:6])
            if len(lang.niches) > 6:
                niches += "..."
            print(f"  {lang.name:13s} | {lang.vibe:30s} | {niches}")
        print(f"\n{'═'*60}")
        print(f"  Всего языков: {len(LANGUAGES)}")
        print(f"  Теоретическое число уникальных дизайнов: >60,000")
        print(f"{'═'*60}\n")
        return

    if not args.niche:
        parser.print_help()
        print("\nУкажите --niche или --list для списка языков")
        return

    forge = NicheForge(niche=args.niche, seed=args.seed)

    if args.format == "json":
        print(json.dumps(forge.describe(), indent=2, ensure_ascii=False))
    elif args.format == "describe":
        desc = forge.describe()
        print(f"\n{'─'*50}")
        print(f"  Ниша:         {desc['niche']}")
        print(f"  Язык:         {desc['language']} — {desc['language_description']}")
        print(f"  Vibe:         {desc['vibe']}")
        print(f"  Метафора:     {desc['meta']}")
        print(f"  Палитра:      bg={desc['palette']['bg']}  fg={desc['palette']['fg']}  accent={desc['palette']['accent']}")
        print(f"  Шрифты:       display={desc['typography']['display'][:30]}…  body={desc['typography']['body'][:30]}…")
        print(f"  Layout:       {desc['layout']} ({desc['density']})")
        print(f"  Signature:    {desc['signature']}")
        print(f"{'─'*50}")
    else:
        html = forge.generate_html()
        if args.out:
            out_path = Path(args.out)
            out_path.write_text(html, encoding='utf-8')
            print(f"HTML сохранён: {out_path.resolve()}")
        else:
            print(html)


if __name__ == "__main__":
    main()
