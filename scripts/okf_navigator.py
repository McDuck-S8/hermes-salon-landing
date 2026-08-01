#!/usr/bin/env python3
"""
OKF Navigator — event-driven domain maturity monitor.

Not a cron job. Reacts to knowledge_added events in real time.

When a concept is added/updated:
  → Maturity check: domain with avg confidence > 0.7 and 3+ verified offers
  → Expiration check: 50%+ concepts expired in domain
  → If threshold hit: creates a beads task automatically

Registration (done once at boot):
    from okf_navigator import register
    register()
"""

import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
HERMES_HOME = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = HERMES_HOME / "scripts"
DB_PATH = HERMES_HOME / "cache" / "knowledge_cube.db"
BD_BIN = HERMES_HOME / "bin" / "bd"
LOG_PATH = HERMES_HOME / "logs" / "okf_navigator.log"
COOLDOWN_FILE = HERMES_HOME / "cache" / "okf_navigator_cooldown.json"

DOMAIN_COOLDOWN_HOURS = 6  # Don't re-check same domain within 6 hours

# ── Helpers ─────────────────────────────────────────────────────────────────


def log(msg: str):
    """Append to navigator log."""
    os.makedirs(str(LOG_PATH.parent), exist_ok=True)
    with open(str(LOG_PATH), "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    print(f"  [OKF-NAV] {msg}")


# Import enrichment module
try:
    from okf_enrichment import (
        get_domain_concepts,
        get_experience_concepts,
        build_en_query,
        enrich_concept,
        write_enrichment_tasks,
    )
    ENRICHMENT_AVAILABLE = True
except ImportError as e:
    log(f"Enrichment module not available: {e}")
    ENRICHMENT_AVAILABLE = False


def get_db() -> sqlite3.Connection:
    os.makedirs(str(DB_PATH.parent), exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def load_cooldowns() -> dict:
    if COOLDOWN_FILE.exists():
        try:
            return json.loads(COOLDOWN_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_cooldowns(data: dict):
    COOLDOWN_FILE.parent.mkdir(parents=True, exist_ok=True)
    COOLDOWN_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def is_on_cooldown(domain: str) -> bool:
    """Check if a domain is still on cooldown (recently checked)."""
    cd = load_cooldowns()
    last = cd.get(domain)
    if not last:
        return False
    elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(last)).total_seconds()
    return elapsed < DOMAIN_COOLDOWN_HOURS * 3600


def set_cooldown(domain: str):
    """Mark domain as checked now."""
    cd = load_cooldowns()
    cd[domain] = datetime.now(timezone.utc).isoformat()
    save_cooldowns(cd)


# ── Domain Analysis ────────────────────────────────────────────────────────

def analyze_domain(domain: str) -> dict:
    """
    Analyze a single domain/category.

    Returns dict with:
      - domain: the domain name
      - total: total concepts in domain
      - avg_confidence: average confidence across all concepts
      - verified_offers: count of entries with source like 'offer' or high confidence
      - expired_count: count of expired concepts
      - expired_pct: percentage of concepts that are expired
      - ready: True if domain is mature enough to monetize
      - needs_recheck: True if 50%+ concepts expired
    """
    conn = get_db()
    result = {
        "domain": domain,
        "total": 0,
        "avg_confidence": 0.0,
        "verified_offers": 0,
        "expired_count": 0,
        "expired_pct": 0.0,
        "ready": False,
        "needs_recheck": False,
    }

    # Check both tables: experiences (by axis_domain) and kc_entries (by category)
    now_iso = datetime.now().isoformat()

    # ── kc_entries ──
    try:
        rows = conn.execute(
            "SELECT confidence, source, verification_method, expiration_date "
            "FROM kc_entries WHERE category = ?", (domain,)
        ).fetchall()
    except Exception:
        rows = []

    # ── experiences ──
    try:
        xp_rows = conn.execute(
            "SELECT confidence, source, verification_method, expiration_date "
            "FROM experiences WHERE axis_domain = ?", (domain,)
        ).fetchall()
    except Exception:
        xp_rows = []

    all_rows = list(rows) + list(xp_rows)
    if not all_rows:
        conn.close()
        result["total"] = 0
        return result

    result["total"] = len(all_rows)

    confidence_sum = 0.0
    verified_count = 0
    expired_count = 0

    for r in all_rows:
        # Confidence
        conf = float(r["confidence"]) if r["confidence"] else 0.5
        confidence_sum += conf

        # Verified offers: high confidence OR verification_method == automated/official
        vmethod = (r["verification_method"] or "").lower()
        source = (r["source"] or "").lower()
        if conf > 0.7 or vmethod in ("automated", "verified", "official-source", "cross-reference"):
            verified_count += 1

        # Expired?
        try:
            exp_val = r["expiration_date"] if "expiration_date" in r.keys() else None
        except (IndexError, KeyError):
            exp_val = None
        if exp_val and str(exp_val).strip() and str(exp_val) < now_iso:
            expired_count += 1

    result["avg_confidence"] = round(confidence_sum / len(all_rows), 3)
    result["verified_offers"] = verified_count
    result["expired_count"] = expired_count
    result["expired_pct"] = round(expired_count / len(all_rows) * 100, 1)

    # Maturity: avg confidence > 0.7 AND 3+ verified offers
    result["ready"] = result["avg_confidence"] > 0.7 and result["verified_offers"] >= 3

    # Expiration: 50%+ expired
    result["needs_recheck"] = result["expired_pct"] >= 50.0

    conn.close()
    return result

# ── Beads Task Creation ────────────────────────────────────────────────────
BD_BIN = "D:/npm-global/node_modules/@beads/bd/bin/bd.js"

def create_beads_task(title: str, description: str, label: str = "navigator"):
    """Create a beads issue via `bd create`."""
    try:
        log(f"Creating beads task: {title}")
        result = subprocess.run(
            ["node", BD_BIN, "create", title,
             "-d", description, "-l", label],
            capture_output=True, text=True, timeout=15,
            cwd=str(HERMES_HOME),
            encoding="utf-8", errors="replace",
        )
        if result.returncode == 0:
            # Parse issue ID from output: "✓ Created issue: hermes-7f6 — ..."
            task_id = ""
            for line in result.stdout.splitlines():
                if "Created issue:" in line:
                    task_id = line.split("Created issue:")[-1].split("—")[0].strip()
                    break
            log(f"  → Created: {task_id or 'unknown'}")
            return task_id
        else:
            log(f"  → Failed: {result.stderr.strip()[:200]}")
            return None
    except Exception as e:
        log(f"  → Error: {e}")
        return None


# ── Event Handler ──────────────────────────────────────────────────────────

def on_knowledge_added(event: dict):
    """
    Handle knowledge_added event from event_bus.

    Event payload expected keys:
      - content: text of the added/updated concept
      - domain: domain/category (derived from category or axis_domain)
      - category: fallback domain name
      - tags: optional tags string
      - source: knowledge source
      - confidence: float
      - verification_method: string
      - expiration_date: optional
    """
    payload = event.get("payload", {})
    domain = payload.get("domain", "") or payload.get("category", "")

    if not domain:
        log("No domain in event payload, skipping")
        return

    # Normalise domain
    domain = domain.lower().replace(" ", "_").replace("/", "_")[:40]

    # Cooldown check — don't re-analyse the same domain too often
    if is_on_cooldown(domain):
        log(f"Domain '{domain}' on cooldown, skipping")
        return

    log(f"Event received: domain='{domain}', source={payload.get('source','?')}")

    # Analyse domain health
    analysis = analyze_domain(domain)

    if analysis["total"] == 0:
        log(f"Domain '{domain}' is empty — nothing to do")
        return

    log(f"Domain '{domain}': total={analysis['total']}, "
        f"avg_conf={analysis['avg_confidence']:.3f}, "
        f"verified={analysis['verified_offers']}, "
        f"expired={analysis['expired_pct']:.1f}%")

    # ── ENRICHMENT — event-driven queue: write task, consume happens asynchronously ──
    if ENRICHMENT_AVAILABLE:
        try:
            concepts = get_domain_concepts(domain)
            exp_concepts = get_experience_concepts(domain)
            all_concepts = concepts + exp_concepts
            if all_concepts:
                tasks_written = write_enrichment_tasks(domain, all_concepts[:10])
                log(f"Enrichment queue: {tasks_written} tasks written for domain '{domain}'")
        except Exception as e:
            log(f"Enrichment queue error for domain '{domain}': {e}")

    # ── Maturity check: ready to monetise ──
    if analysis["ready"]:
        title = f"Домен {domain} готов к монетизации"
        description = (
            f"OKF Navigator обнаружил зрелый домен.\n\n"
            f"**Домен**: {domain}\n"
            f"**Всего концептов**: {analysis['total']}\n"
            f"**Средний confidence**: {analysis['avg_confidence']:.3f}\n"
            f"**Проверенных офферов**: {analysis['verified_offers']}\n"
            f"**Просрочено**: {analysis['expired_pct']:.1f}%\n\n"
            f"Порог: confidence > 0.7 и 3+ проверенных оффера — пройден.\n"
            f"Источник: событие knowledge_added от {payload.get('source','?')}"
        )
        beads_id = create_beads_task(title, description, label="navigator")
        if beads_id:
            log(f"✅ Создана задача: {title} → {beads_id}")
        set_cooldown(domain)

    # ── Expiration check: needs re-verification ──
    if analysis["needs_recheck"]:
        title = f"Перепроверить домен {domain}"
        description = (
            f"OKF Navigator обнаружил устаревший домен.\n\n"
            f"**Домен**: {domain}\n"
            f"**Всего концептов**: {analysis['total']}\n"
            f"**Просрочено**: {analysis['expired_count']} ({analysis['expired_pct']:.1f}%)\n"
            f"**Текущий confidence**: {analysis['avg_confidence']:.3f}\n\n"
            f"Порог: 50%+ просроченных концептов — пройден.\n"
            f"Требуется ручная верификация."
        )
        beads_id = create_beads_task(title, description, label="navigator")
        if beads_id:
            log(f"✅ Создана задача: {title} → {beads_id}")
        set_cooldown(domain)


# ── Registration ───────────────────────────────────────────────────────────

def register():
    """Register OKF Navigator as a DIRECT_EVENT_HANDLER for knowledge_added."""
    try:
        # ensure scripts dir is on path
        sys.path.insert(0, str(SCRIPTS_DIR))
        from event_bus import DIRECT_EVENT_HANDLERS

        if "knowledge_added" not in DIRECT_EVENT_HANDLERS:
            DIRECT_EVENT_HANDLERS["knowledge_added"] = []
        DIRECT_EVENT_HANDLERS["knowledge_added"].append(on_knowledge_added)
        log("Registered as DIRECT_EVENT_HANDLER for knowledge_added")
        return True
    except Exception as e:
        log(f"Failed to register: {e}")
        return False


# ── Manual invokation (for testing / admin) ──────────────────────────────

def run_for_domain(domain: str):
    """Manually analyse a domain and show/handle result."""
    import json
    analysis = analyze_domain(domain)
    print(json.dumps(analysis, indent=2, ensure_ascii=False))
    return analysis


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "check":
        domain = sys.argv[2] if len(sys.argv) > 2 else input("Domain: ")
        result = run_for_domain(domain)
        if result.get("ready"):
            print(f"\n✅ Domain '{domain}' is READY for monetization!")
        if result.get("needs_recheck"):
            print(f"\n⚠ Domain '{domain}' needs RE-CHECK ({result['expired_pct']:.0f}% expired)")
    elif len(sys.argv) >= 2 and sys.argv[1] == "register":
        register()
        print("OKF Navigator registered for future events.")
    else:
        print("Usage:")
        print("  okf_navigator.py check <domain>    — analyse domain maturity")
        print("  okf_navigator.py register           — register as event handler")
        print("\nOr import and call register() from your boot script.")
