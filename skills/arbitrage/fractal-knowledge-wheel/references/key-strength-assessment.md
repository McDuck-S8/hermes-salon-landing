# Key Strength Assessment — Оценка силы ключа (гипотезы)

## Зачем это нужно

Система оценивала **аспекты** (зелёный/жёлтый/красный), но не оценивала сам **ключ** — исток, гипотезу, которая порождает эти аспекты.

> «Мы научили систему оценивать аспекты, но сам ключ остаётся без оценки. Система может показать что «Креативы — 15%, проблема», но она не говорит: стоит ли вообще заниматься этим ключом?»

## Метрики

### 1. Viability (Жизнеспособность) — вес 0.4
Насколько сам ключ перспективен, независимо от готовности аспектов.

```
Viability = market_demand × 0.4 + (1 - entry_barrier) × 0.3 + margin_potential × 0.3
```

**Доменные профили (базовые значения):**
- `arbitrage`: demand=0.75, barrier=0.55, margin=0.70
- `ai-ofm`: demand=0.85, barrier=0.30, margin=0.80
- `craft`: demand=0.65, barrier=0.60, margin=0.55
- `default`: 0.5 / 0.5 / 0.5

**Корректировки по ключу (keywords):**
- `pwa` / `progressive web`: demand ≥ 0.7, barrier ≤ 0.6
- `youtube shorts` / `shorts`: demand ≥ 0.8, barrier ≤ 0.4
- `tiktok`: demand ≥ 0.85, barrier ≤ 0.45
- `cpa` / `content lock`: demand ≥ 0.75, margin ≥ 0.75
- `telegram mini app` / `mini app`: demand ≥ 0.8, barrier ≤ 0.5, margin ≥ 0.8
- `india` / `индия`: demand ≥ 0.8, barrier ≥ 0.6
- `betting` / `беттинг` / `gambling`: demand ≥ 0.85, margin ≥ 0.85, barrier ≥ 0.7

### 2. Cohesion (Связанность) — вес 0.3
Насколько аспекты зависят друг от друга. Если один красный аспект блокирует все зелёные — ключ хрупкий.

```
Cohesion = 1 - (blocking_red_count / total_sectors)
```

**Blocking red** — уникальные красные аспекты, которые находятся в конфликте (intersection_type == "conflict") с зелёными аспектами. Считается через пересечения Эйлеровых кругов.

### 3. Growth Potential (Потенциал роста) — вес 0.3
Потолок масштабирования в $/мес, нормированный через log10.

```
Growth = min(1.0, log10(max_ceiling) / 4.0)  # 4 = log10(10000)
```

**Потолки по типам ключей:**
- `pwa betting`: $10,000
- `youtube shorts`: $5,000
- `tiktok`: $8,000
- `cpa content lock`: $3,000
- `telegram mini app`: $15,000
- `native ads`: $12,000
- `push traffic`: $8,000
- `email marketing`: $5,000
- `seo`: $3,000
- `default`: $2,000

**Модификаторы:**
- `scale` / `масштаб` в ключе: ×2
- `auto` / `авто` в ключе: ×1.5

## Итоговая формула

```
Key Strength = Viability × 0.4 + Cohesion × 0.3 + Growth × 0.3
```

## API

```python
from fractal_wheel import FractalWheel, KeyStrengthEstimator, EulerCirclesEngine

wheel = FractalWheel(center="PWA-арбитраж беттинга на Индию", domain="arbitrage")
sectors = wheel.build_wheel()
sectors = wheel.assess_gaps(sectors)

engine = EulerCirclesEngine(sectors)
intersections = engine.find_all_intersections()

estimator = KeyStrengthEstimator(domain="arbitrage")

# Оценка одного ключа
ks = estimator.estimate("PWA-арбитраж беттинга на Индию", sectors, intersections)
print(f"Key Strength: {ks.key_strength:.3f}")
print(f"Viability: {ks.viability:.3f}, Cohesion: {ks.cohesion:.3f}, Growth: {ks.growth_potential:.3f}")
print(f"Details: {ks.to_dict()}")

# Сравнение ключей
keys = ["PWA-арбитраж на Индию", "YouTube Shorts → CPAGrip (RU)", "TikTok → Telegram Mini App"]
comparison = estimator.compare_keys(keys, {k: sectors for k in keys}, {k: intersections for k in keys})
for i, ks in enumerate(comparison, 1):
    print(f"{i}. {ks.key_name}: {ks.key_strength:.3f}")
```

## Пример результатов

| Key | Viability | Cohesion | Growth | **Strength** |
|-----|-----------|----------|--------|--------------|
| TikTok → Telegram Mini App Betting | 0.685 | 0.750 | 1.000 | **0.799** |
| YouTube Shorts → CPAGrip (RU) | 0.725 | 0.750 | 0.925 | **0.792** |
| PWA-арбитраж беттинга на Индию | 0.685 | 0.750 | 0.825 | **0.747** |

**Вывод:** PWA на Индии имеет высший потолок ($10k), но YouTube Shorts и TikTok Mini App — более сильные ключи *прямо сейчас* из-за низкого барьера входа и доказанного спроса.

## Интеграция с байесовской оценкой

Key Strength оценивает **ключ целиком**. Байесовская оценка (v3.0) оценивает **пересечения** внутри ключа. Два уровня:
1. **Key Strength** — стоит ли начинать этот ключ?
2. **Bayesian P(success)** — вероятность успеха конкретной связки аспектов внутри ключа?