#!/usr/bin/env python3
"""
R&D Processor — event-driven обработка сигналов для мастерской.
Считывает новые сигналы из signals.jsonl,

> Revisit: when brick validation, workshop integration, or goal creation logic changes. Last touched: 2026-07-02.
проверяет ARBITRAGE_WORKSHOP.md,
добавляет новые кирпичи с пометкой «требует проверки».

Usage:
    python scripts/rd_processor.py           # process new signals
    python scripts/rd_processor.py --status  # show brick count
"""
import json
import re
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
SIGNALS_FILE = CACHE_DIR / "signals.jsonl"
PROCESSED_RD = CACHE_DIR / "rd_processed.json"
WORKSHOP_FILE = HERMES_HOME / "ARBITRAGE_WORKSHOP.md"
FINDS_FILE = HERMES_HOME / "ARBITRAGE_FINDS.md"
BRICKS_LOG = CACHE_DIR / "bricks_log.jsonl"


def load_rd_processed():
    if PROCESSED_RD.exists():
        try:
            return set(json.loads(PROCESSED_RD.read_text("utf-8")).get("hashes", []))
        except Exception:
            return set()
    return set()


def save_rd_processed(hashes: set):
    hashes = sorted(hashes)[-300:]
    PROCESSED_RD.write_text(
        json.dumps({"hashes": sorted(hashes), "updated": datetime.now().isoformat()}, ensure_ascii=False),
        encoding="utf-8"
    )


def workshop_contains(title: str) -> bool:
    """Check if ARBITRAGE_WORKSHOP.md already contains this."""
    if not WORKSHOP_FILE.exists():
        return False
    content = WORKSHOP_FILE.read_text("utf-8").lower()
    # Check if core words from title are in workshop
    words = [w.lower() for w in title.split() if len(w) > 4]
    if not words:
        return False
    found = sum(1 for w in words if w in content)
    return found >= len(words) * 0.5  # 50%+ words match


def add_to_workshop(signal: dict):
    """Add signal to ARBITRAGE_WORKSHOP.md as new brick."""
    title = signal.get("title", "Unknown")
    url = signal.get("url", "")
    source = signal.get("source", "unknown")
    category = signal.get("category", "unknown")

    brick = f"""
### {title} [{category.upper()}]

**Источник:** {source}
**URL:** {url}
**Статус:** требует проверки
**Добавлено:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

**Что это:**
- (описание — заполнить при проверке)

**Математика:**
- Стоимость: ?
- Доход: ?
- ROI: ?%
- Риски: ?

**Целевая аудитория:**
- Кто: ?
- Боль: ?
- Где искать: ?

**Действия:**
- [ ] Проверить URL
- [ ] Заполнить математику
- [ ] Заполнить ЦА
- [ ] Протестировать

---
"""
    if WORKSHOP_FILE.exists():
        with open(WORKSHOP_FILE, "a", encoding="utf-8") as f:
            f.write(brick)
    else:
        WORKSHOP_FILE.write_text(f"# ARBITRAGE_WORKSHOP\n\n{brick}", encoding="utf-8")


def log_brick(signal: dict, action: str):
    """Log brick action to bricks_log.jsonl."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "action": action,
        "title": signal.get("title", ""),
        "source": signal.get("source", ""),
        "hash": signal.get("hash", ""),
    }
    with open(BRICKS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def process_signals():
    """Process all new signals from signal_scanner."""
    if not SIGNALS_FILE.exists():
        print("No signals file.")
        return 0

    processed = load_rd_processed()
    lines = SIGNALS_FILE.read_text("utf-8").strip().split("\n")
    new_count = 0
    skip_count = 0

    for line in lines:
        if not line.strip():
            continue
        try:
            signal = json.loads(line)
        except json.JSONDecodeError:
            continue

        h = signal.get("hash", "")
        if h in processed:
            continue

        title = signal.get("title", "")

        if workshop_contains(title):
            log_brick(signal, "skip_exists")
            processed.add(h)
            skip_count += 1
            continue

        # Bayesian score check — reject noise
        try:
            from bayesian_scorer import compute_score
            score = compute_score(signal)
            signal["bayesian_score"] = score
            if score < 0.3:
                log_brick(signal, "reject_noise")
                processed.add(h)
                skip_count += 1
                continue
        except Exception:
            signal["bayesian_score"] = 0.5  # fallback if scorer fails

        # New brick — add to workshop
        add_to_workshop(signal)
        log_brick(signal, "added")
        processed.add(h)
        new_count += 1

    save_rd_processed(processed)
    return new_count


def status():
    """Show brick count and recent additions."""
    if BRICKS_LOG.exists():
        lines = BRICKS_LOG.read_text("utf-8").strip().split("\n")
        added = sum(1 for l in lines if '"added"' in l)
        skipped = sum(1 for l in lines if '"skip_exists"' in l)
        print(f"Bricks added: {added}")
        print(f"Bricks skipped (exists): {skipped}")
        print(f"Total actions: {len(lines)}")
        # Last 5
        print("\nRecent:")
        for l in lines[-5:]:
            try:
                e = json.loads(l)
                print(f"  [{e.get('action')}] {e.get('title','')[:50]}")
            except Exception:
                pass
    else:
        print("No bricks yet.")


def main():
    if "--status" in sys.argv:
        status()
        return

    count = process_signals()
    if count:
        print(f"NEW BRICKS: {count}")
    else:
        print("No new bricks (all exist or no signals).")


if __name__ == "__main__":
    import sys
    main()
