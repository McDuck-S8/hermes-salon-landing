---
name: verification-gate
description: "Auto-generated from verification_gate.md"
trigger: "When user asks about verification_gate concepts"
usage: verification-gate
Revisit: 2026-07-31
---

# verification_gate.py — Барьер между теорией и фактом

Правило: НИ ОДНА запись о revenue/profit/result не попадает 
в Knowledge Cube / fabric / wheel без верификации.

## Уровни верификации

| Маркер | Значение | Пример |
|--------|----------|--------|
| ✅ confirmed | Есть внешнее подтверждение | Скриншот, API, скринкаст |
| 🟡 plausible | Логично, но не проверено | «Я знаю как это сделать» |
| ❌ speculative | Догадка | «Возможный ROI 3000%» |
| 🟢 estimated | Расчёт на реальных данных | CPC из API * CR из логов |
| 🔴 fabricated | Сгенерировано без основы | Любая сделка без P&L |

## Порог входа

Любая цифра revenue/profit/ROI:
- БЕЗ источника → попадает в `_speculative` домен
- С источником → попадает в `_verified` домен
- Без верификации → wheel НЕ читает

## Кто применяет

Я. Каждый раз когда хочу записать «результат».
Не жду пока меня поймают.
