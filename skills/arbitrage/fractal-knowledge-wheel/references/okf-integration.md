# Fractal Knowledge Wheel — OKF / Knowledge Cube Integration

## Overview

The Fractal Knowledge Wheel integrates with the OKF (Organized Knowledge Framework) and Knowledge Cube at multiple levels:

1. **Data Source** — reads recent findings from `knowledge_cube.db` (kc_entries + experiences tables)
2. **Entity Extraction** — parses traffic, offers, payments, withdrawals, geo, bridges, tools from unstructured text
3. **Existing Keys Check** — queries existing documented связки to avoid duplication
4. **Event Tracking** — uses `hermes_hooks.py` to log wheel runs as events
5. **Goal Queue** — creates research goals for red/yellow sectors automatically

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRACTAL KNOWLEDGE WHEEL                   │
├─────────────────────────────────────────────────────────────┤
│  MODE 1: ANALYSIS          MODE 2: SYNTHESIS                 │
│  ────────────────          ─────────────────                 │
│  build_wheel()             get_recent_findings(days=7)       │
│  assess_gaps()             extract_entities()                │
│  WheelAssessment           group_by_compatibility()          │
│  priority_tasks            find_novel_keys()                 │
│                                                              │
│  MODE 3: EULER CIRCLES                                        │
│  ─────────────────────                                        │
│  EulerCirclesEngine(sectors)                                  │
│  find_all_intersections()                                     │
│  get_golden_sections()        # 🟢🟢 intersections             │
│  get_critical_gaps()          # 🔴🔴 intersections             │
│  get_conflicts()              # 🟢🔴 intersections             │
│  get_growth_zones()           # 🟡🟡 intersections             │
│  synthesize_from_green_intersections()  # NEW KEYS            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE CUBE / OKF                      │
├─────────────────────────────────────────────────────────────┤
│  kc_entries (FTS5)          experiences (session learnings)  │
│  ─────────────────          ───────────────────────          │
│  content, tags, category    content, axis_domain,            │
│  source, importance,        axis_outcome, importance,        │
│  created_at                 tags, ts                         │
└─────────────────────────────────────────────────────────────┘
```

## Integration Points

### 1. Reading from Knowledge Cube (Synthesis Mode)

```python
from skills.arbitrage.fractal-knowledge-wheel.scripts.fractal_wheel import FractalWheel

wheel = FractalWheel(center="PWA-арбитраж Индия", domain="arbitrage")
# Mode 2: Synthesis reads from knowledge_cube.db
novel_keys = wheel.run_synthesis_mode(days=7)  # ← 7 days of findings
```

The `KnowledgeSource.get_recent_findings(days)` queries:
- `kc_entries` — main knowledge base (importance, tags, category, source)
- `experiences` — session learnings (axis_domain, axis_outcome, tags)

### 2. Writing Goals to Goal Queue (Analysis Mode)

```python
# Analysis mode auto-generates priority tasks
assessment = wheel.run_analysis_mode()
for task in assessment.priority_tasks:
    # task = {"type": "research", "target": "creatives", "priority": "critical", ...}
    # These should be pushed to goal_queue.json
    create_goal(
        title=f"Research: {task['sector_name']}",
        tier=TIER_SURVIVE if task['priority'] == 'critical' else TIER_LEARN,
        priority=10 if task['priority'] == 'critical' else 5,
        description=task['expected_outcome'],
        related_actions=["auto-research"],
    )
```

### 3. Event Tracking (Boot Integration)

```python
from hermes_hooks import get_hooks

hooks = get_hooks()
hooks.on_task_complete(
    task_id=f"fractal_wheel_{wheel.slug}",
    result=f"Analysis: {assessment.overall_percent}%, Synthesis: {len(novel_keys)} keys, Euler: {euler['golden_sections']} golden sections",
    tags=["fractal-wheel", wheel.domain, "analysis", "synthesis", "euler"]
)
```

### 4. Mandatory Boot Integration

The `fractal_wheel_boot.py` script is designed to be called from `session_boot.py`:

```python
# In session_boot.py, after gathering reality:
try:
    from fractal_wheel_boot import FractalWheelBoot
    boot = FractalWheelBoot()
    results = boot.run_all()
    # Results contain insights + priority_actions for immediate autonomous action
except Exception as e:
    log(f"[WARN] Fractal Wheel boot failed: {e}")
```

### 5. Auto-Recall for Next Session

```python
from auto_recall import recall_for_session

# Next session automatically gets relevant context
context = recall_for_session(
    "PWA-арбитраж Индия", 
    top_n=5
)
# Returns previous wheel runs, insights, priority actions
```

## Entity Extraction Patterns

The SynthesisEngine uses regex patterns to extract entities from KB text:

| Type | Patterns | Examples |
|------|----------|----------|
| traffic | TikTok, YouTube Shorts, Reels, UGC, native, push, pop, Facebook Ads, mini apps | "TikTok", "YouTube Shorts", "push" |
| offer | 1xBet, 1win, Mostbet, CPAGrip, OGAds, CPA, CPS, CPL, SOI, DOI, revshare, казино, беттинг, nutra | "1xBet", "CPAGrip", "CPA", "revenue share" |
| payment | USDT, USDC, BTC, ETH, TRC20, ERC20, BEP20, P2P, Bybit, Binance, KuCoin, OKX, T-Bank, Сбер, Тинькофф | "USDT", "Binance", "P2P" |
| withdrawal | вывод, withdrawal, payout, выплата, USDT→RUB, RUB→USDT, карта, счёт | "вывод", "USDT→RUB" |
| geo | Индия, India, RU, RF, Russia, Россия, Крым, Crimea, Турция, Turkey, BR, Brazil, VN, Vietnam, ID, Indonesia, TH, Thailand, PH, Philippines | "India", "RU", "Brazil" |
| bridge | PWA, PWA.Market, GitHub Pages, Cloudflare, Vercel, Netlify, Carrd, Webflow, landing, pre-lander | "PWA", "Carrd", "GitHub Pages" |
| tool | freqtrade, trading bot, telegram bot, scraper, parser, automation, docker, cloaking, Keitaro, Binom, Voluum, RedTrack | "Keitaro", "docker", "telegram bot" |

## Configuration

```python
# Domain sector definitions (scripts/fractal_wheel.py)
DOMAIN_SECTORS = {
    "arbitrage": [
        {"id": "traffic", "name": "Трафик", "weight": 1.0, "critical": True},
        {"id": "bridge", "name": "Прокладка", "weight": 1.0, "critical": True},
        {"id": "offer", "name": "Оффер", "weight": 1.0, "critical": True},
        {"id": "creatives", "name": "Креативы", "weight": 1.2, "critical": True},
        {"id": "payments", "name": "Платежи", "weight": 1.0, "critical": True},
        {"id": "withdrawal", "name": "Вывод", "weight": 1.0, "critical": True},
        {"id": "legal", "name": "Юридические риски", "weight": 0.8, "critical": False},
        {"id": "scaling", "name": "Масштабирование", "weight": 0.7, "critical": False},
    ],
    "ai-ofm": [...],
    "craft": [...],
    "default": [...],
}
```

## CLI Usage

```bash
# Full cycle (all 3 modes)
python fractal_wheel.py "PWA-арбитраж Индия" arbitrage all

# Single modes
python fractal_wheel.py "PWA-арбитраж Индия" arbitrage analysis
python fractal_wheel.py "PWA-арбитраж Индия" arbitrage synthesis
python fractal_wheel.py "PWA-арбитраж Индия" arbitrage euler

# Boot integration (auto from goal queue or manual topics)
python fractal_wheel_boot.py --topics "PWA-арбитраж Индия" --domain arbitrage --report
python fractal_wheel_boot.py --report  # auto from goal queue
```

## Output Reports

Reports saved to `reports/`:
- `fractal_wheel_boot_YYYYMMDD_HHMMSS.json` — structured results for autonomous agent
- HTML report via `wheel.generate_html_report()` — visual wheel + intersections

## Extending for New Domains

1. Add sector definition to `DOMAIN_SECTORS`
2. Add entity extraction patterns to `SynthesisEngine` if needed
3. Add compatibility rules to `check_compatibility()`
4. Test with `run_full_cycle(mode="all")`

---

*Last updated: 2026-07-16 — Integrated with session_boot.py, added Euler Circles mode, added fractal_wheel_boot.py*