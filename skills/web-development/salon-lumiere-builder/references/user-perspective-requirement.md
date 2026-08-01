# User-Perspective Requirement (MANDATORY) — 2026-07-18

**Rule:** Every salon landing MUST pass the 4-question user-perspective validation before generation.

```python
required_up = ["who", "five_sec", "action", "why"]
for q in required_up:
    assert params["user_perspective"][q], f"Missing user_perspective.{q}"
```

**User-Perspective Template (from Fargo landing):**
```json
"user_perspective": {
    "who": "Жінка 28-45 років, Київ (Позняки), шукає стрижку/колористику/манікюр. Має роботу, обмежений час, хоче бачити портфоліо майстра ДО візиту.",
    "five_sec": "Fargo — салон на Позняках. Чесні ціни на сайті, портфоліо майстрів, запис онлайн за 30 сек. Без дзвінків.",
    "action": "Натисне 'Записатися онлайн' (золота кнопка в герої) → вибере послугу → дату → час → відправить форму.",
    "why": "Устала від сюрпризів у чеку. Хоче бачити роботу Олени (колорист) перед візитом, знати ціну наперед, записатися без дзвінків адміністратору."
}
```

**Why this matters:** Without user-perspective, landing becomes a generic template that doesn't convert. The 4 questions force specific copy that matches real client intent.