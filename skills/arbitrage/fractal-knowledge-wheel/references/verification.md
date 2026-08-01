# Verification Suite for Fractal Knowledge Wheel

## Overview
This document describes the verification tests for all 3 modes of the Fractal Knowledge Wheel skill.

## Test Coverage

### Mode 1: Analysis (Режим 1 — Анализ)
**File:** `scripts/verify.py` → `test_analysis_mode()`

| Check | Expected |
|-------|----------|
| Sectors built | 8 (arbitrage domain) |
| Overall percentage | 56% |
| Green sectors | 4 (Traffic, Bridge, Payments, Withdrawal) |
| Yellow sectors | 2 (Offer, Legal) |
| Red sectors | 2 (Creatives, Scaling) |
| Critical red sectors | 1 (Creatives) |
| Priority tasks | 4 (Critical → High → Medium → Medium) |
| First task | Critical: Creatives |

### Mode 2: Synthesis (Режим 2 — Синтез)
**File:** `scripts/verify.py` → `test_synthesis_mode()`

| Check | Expected |
|-------|----------|
| Novel keys synthesized | ≥ 10 |
| Key name format | Contains `→` (traffic → bridge → offer) |
| Compatibility score | 0-1 |
| Novelty score | 0-1 |
| Components present | traffic, bridge, offer, geo, payment, withdrawal |
| Sorting | By compatibility × novelty descending |

### Mode 3: Euler Circles (Режим 3 — Круги Эйлера)
**File:** `scripts/verify.py` → `test_euler_mode()` (NEW)

| Check | Expected |
|-------|----------|
| Total intersections | ≥ 50 |
| Golden sections | ≥ 10 |
| Critical gaps | ≥ 0 (depends on red sectors) |
| Conflicts | ≥ 20 |
| Growth zones | ≥ 10 |
| Golden sections include 3-circle intersections | Yes |
| Conflicts include green+red pairs | Yes |
| New keys from green intersections | ≥ 5 |

### Domain Support
**File:** `scripts/verify.py` → `test_domains()`

| Domain | Min sectors |
|--------|-------------|
| arbitrage | 8 |
| ai-ofm | 8 |
| craft | 8 |
| default | 6 |

### Knowledge Source Integration
**File:** `scripts/verify.py` → `test_knowledge_source()`

| Check | Expected |
|-------|----------|
| Findings from last 7 days | > 0 |
| Required fields | id, content, tags, source, category, importance, created_at, type |
| Types present | kc_entry, experience |

### Entity Extraction
**File:** `scripts/verify.py` → `test_entity_extraction()`

| Entity Type | Min Count |
|-------------|-----------|
| traffic | 10 |
| offer | 5 |
| payment | 3 |
| geo | 1 |
| bridge | 1 |
| tool | 1 |

### CLI Compatibility
**File:** `scripts/verify.py` → `test_cli_compatibility()`

| Mode | Exit Code | Output Contains |
|------|-----------|-----------------|
| analysis | 0 | "ANALYSIS", "Overall:" |
| synthesis | 0 | "SYNTHESIS", "novel keys" |
| euler | 0 | "EULER" or "golden" |

---

## Self-Analysis Pattern Verification (Hermes Architecture)

### Sectors (10)
1. Саморазвитие и Обучение — 85% 🟢 (weight 1.3, critical)
2. Инструментальная Экосистема — 90% 🟢 (weight 1.2, critical)
3. Память и Контекст — 80% 🟢 (weight 1.2, critical)
4. Безопасность и Одобрения — 85% 🟢 (weight 1.3, critical)
4. Автономные Операции — 75% 🟡 (weight 1.2, critical)
5. Система Навыков — 70% 🟡 (weight 1.1, critical)
6. Самодиагностика и Здоровье — 60% 🟡 (weight 1.1, critical)
7. Интеграции и Расширения — 55% 🟡 (weight 0.9)
8. Качество Кода и Рефакторинг — 45% 🟡 (weight 1.0)
9. Голос и Коммуникация — 40% 🟡 (weight 0.8)

### Intersections
- **Golden Sections**: 11 (6 pairs + 4 triples + 1 system core)
- **Critical Gaps**: 0 (no red-red pairs)
- **Conflicts**: 24 (green + yellow/red)
- **Growth Zones**: 15 (yellow + yellow)

### Key Conflicts (Green + Red/Yellow)
- Саморазвитие(85%) ∩ Автономные Операции(75%) — 85%
- Инструменты(90%) ∩ Автономные Операции(75%) — 90% ⚡ CRITICAL
- Безопасность(85%) ∩ Автономные Операции(75%) — 85%
- Инструменты(90%) ∩ Система Навыков(70%) — 90%

### New Keys from Green Intersections (11)
- Саморазвитие + Инструменты + Безопасность (87%)
- Саморазвитие + Инструменты + Память (85%)
- Инструменты + Память + Безопасность (85%)
- Саморазвитие + Память + Безопасность (83%)

---

## Verification Script for Self-Analysis

```bash
# Run self-analysis verification
python -c "
import sys, importlib.util
from pathlib import Path

HERMES_HOME = Path('D:/d/Portable_Soft/hermes')
fractal_wheel_path = HERMES_HOME / 'skills/arbitrage/fractal-knowledge-wheel/scripts/fractal_wheel.py'
spec = importlib.util.spec_from_file_location('fractal_wheel', fractal_wheel_path)
fractal_wheel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fractal_wheel)

EulerCirclesEngine = fractal_wheel.EulerCirclesEngine
Sector = fractal_wheel.Sector

sectors = [
    Sector(id='self_improvement', name='Саморазвитие и Обучение', weight=1.3, critical=True, fill_percent=85, status='🟢', facts=[], gaps=[]),
    Sector(id='tool_ecosystem', name='Инструментальная Экосистема', weight=1.2, critical=True, fill_percent=90, status='🟢', facts=[], gaps=[]),
    Sector(id='memory_context', name='Память и Контекст', weight=1.2, critical=True, fill_percent=80, status='🟢', facts=[], gaps=[]),
    Sector(id='approval_safety', name='Безопасность и Одобрения', weight=1.3, critical=True, fill_percent=85, status='🟢', facts=[], gaps=[]),
    Sector(id='autonomous_ops', name='Автономные Операции', weight=1.2, critical=True, fill_percent=75, status='🟡', facts=[], gaps=[]),
    Sector(id='skill_system', name='Система Навыков', weight=1.1, critical=True, fill_percent=70, status='🟡', facts=[], gaps=[]),
    Sector(id='self_diagnosis', name='Самодиагностика и Здоровье', weight=1.1, critical=True, fill_percent=60, status='🟡', facts=[], gaps=[]),
    Sector(id='integration_ext', name='Интеграции и Расширения', weight=0.9, critical=False, fill_percent=55, status='🟡', facts=[], gaps=[]),
    Sector(id='code_quality', name='Качество Кода и Рефакторинг', weight=1.0, critical=False, fill_percent=45, status='🟡', facts=[], gaps=[]),
    Sector(id='voice_comm', name='Голос и Коммуникация', weight=0.8, critical=False, fill_percent=40, status='🟡', facts=[], gaps=[]),
]

engine = EulerCirclesEngine(sectors)
intersections = engine.find_all_intersections()
golden = engine.get_golden_sections()
critical = engine.get_critical_gaps()
conflicts = engine.get_conflicts()
growth = engine.get_growth_zones()
new_keys = engine.synthesize_from_green_intersections()

print(f'Sectors: {len(sectors)}')
print(f'Intersections: {len(intersections)}')
print(f'Golden: {len(golden)}')
print(f'Critical: {len(critical)}')
print(f'Conflicts: {len(conflicts)}')
print(f'Growth: {len(growth)}')
print(f'New keys: {len(new_keys)}')

# Verify system core
core_green = [s for s in sectors if s.fill_percent >= 80]
print(f'System core aspects: {len(core_green)}')
for s in core_green:
    print(f'  {s.name} ({s.fill_percent}%)')
"
```

---

## Expected Outputs for Self-Analysis

### System Core (4 green aspects = platform)
```
Саморазвитие (85%) ∩ Инструменты (90%) ∩ Память (80%) ∩ Безопасность (85%)
→ "Это твоя платформа — можно строить любые навыки/фичи внутри этого ядра"
```

### Golden Core (3-way intersections)
- Саморазвитие + Инструменты + Безопасность (87%)
- Саморазвитие + Инструменты + Память (85%)
- Саморазвитие + Память + Безопасность (83%)
- Инструменты + Память + Безопасность (85%)

### Critical Conflicts (Green + Yellow/Red)
```
Инструменты(90%) ∩ Автономные Операции(75%) → "Мощные инструменты, но нестабильный рантайм" ⚡
Саморазвитие(85%) ∩ Автономные Операции(75%) → "Саморазвитие готово, но авто-опс держит"
Саморазвитие(85%) ∩ Система Навыков(70%) → "Нет версионирования, deps не разрешаются"
Инструменты(90%) ∩ Система Навыков(70%) → "Skills не интегрированы в tool ecosystem"
```

### New Keys for Self-Evolution
1. **Саморазвитие + Инструменты + Безопасность (87%)** — "Автономный агент с guardrails"
2. **Саморазвитие + Инструменты + Память (85%)** — "Knowledge-driven evolution"
3. **Инструменты + Память + Безопасность (85%)** — "Trusted execution platform"
4. **Саморазвитие + Память + Безопасность (83%)** — "Self-auditing memory"

---

## Files Verified

- `scripts/fractal_wheel.py` — core implementation (1244 lines)
- `scripts/fractal_wheel_boot.py` — mandatory boot integration
- `scripts/verify.py` — verification suite for all 3 modes
- `templates/wheel_template.html` — HTML template
- `references/okf-integration.md` — Knowledge Cube integration guide
- `references/self-analysis-pattern.md` — self-analysis pattern documentation
- `references/verification.md` — this file
- `SKILL.md` — documentation (v2.0.0)

---

## Known Limitations

1. `assess_gaps()` uses mock data — needs full Knowledge Cube integration
2. `generate_html()` requires Jinja2 (falls back to basic template)
3. `recurse_on_critical_red()` creates sub-wheels but doesn't auto-run them
4. HTML template uses Jinja2 syntax not yet rendered by current implementation
5. `fractal_wheel_boot.py` `_get_pending_topics()` could pull from more sources (intake, active research, user requests)

---

## Last Verified
- **Date:** 2026-07-16
- **Session:** Hermes self-analysis via Fractal Knowledge Wheel
- **All Tests:** ✅ PASS