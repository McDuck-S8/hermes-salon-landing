# NicheForge — генератор уникальных дизайнов под нишу

NicheForge — методология и инструмент для генерации визуально различных дизайнов
в зависимости от ниши. Вместо шаблона каждая ниша получает свой **визуальный язык**
с уникальной метафорой, палитрой, шрифтами, layout и signature-элементом.

## Инструмент

`tools/niche_designer.py` — CLI-генератор.

```bash
python tools/niche_designer.py --niche "AI Tutorials" --out result.html
python tools/niche_designer.py --list
python tools/niche_designer.py --niche "True Crime" --format describe
```

## Каталог визуальных языков (10)

| Язык | Метафора | Ниши | Акцент |
|------|----------|------|--------|
| laboratory | Лаборатория | AI, tech, science, devtools | #22c55e |
| editorial | Журнал | self-improvement, образование, блог | #dc2626 |
| terminal | Терминал | programming, devops, tools | #00ff41 |
| dashboard | Дашборд | finance, crypto, аналитика | #3b82f6 |
| journal | Дневник | lifestyle, творчество, психология | #d97706 |
| nature | Природа | wildlife, travel, экология | #84a98c |
| luxury | Премиум | consulting, real estate, premium | #d4a373 |
| brutalist | Брутализм | art, portfolio, дизайн | #ff0000 |
| playlist | Плейлист | youtube, media, entertainment | #e11d48 |
| cinema | Кино/нуар | true crime, storytelling | #f97316 |

## Как работает

1. **Ниша → язык.** Поиск ключевых слов в названии → ближайший визуальный язык.
2. **Язык → уникальная комбинация.** Цвет (вариация 30%), шрифты (15%), layout, signature.
3. **Воспроизводимость.** Seed = hash(niche) → стабильный дизайн. Разный seed → новый.

## Теоретическое число комбинаций

10 языков × 6 акцентов × 4 layout × 3 плотности × 5 signature ≈ **60,000+**

## Правила

1. Каждая ниша — свой визуальный язык. Не один язык на всё.
2. Меняй не только цвет — layout + типографика + метафора должны быть другими.
3. Signature-элемент — единственная смелость. Остальное сдержанно.
4. Палитра: 4 цвета (bg, fg, accent, muted).
5. Шрифты: 2 роли — display (характерный) + body (читаемый).

## Примеры из этого проекта

`cache/nicheforge_demo/` — сгенерированные примеры для 5 ниш.
`tools/niche_designer.py` — сам инструмент (650 строк, Python 3.11+).
