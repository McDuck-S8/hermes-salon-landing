#!/usr/bin/env python3
"""
Feedback Store — persistent storage for action outcomes.


> Revisit: when feedback storage logic, feedback evaluation, or feedback store schema changes. Last touched: 2026-07-02.
Every action result is recorded with outcome score, context, and timestamp.
Used by compute_score() to adjust weights dynamically.

Outcome scale: -1.0 (complete failure) to 1.0 (complete success)
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

HERMES_HOME = Path(__file__).resolve().parent.parent
FEEDBACK_DB = HERMES_HOME / "cache" / "feedback_store.json"
WEIGHTS_CACHE = HERMES_HOME / "cache" / "action_weights.json"

# Exponential decay for recent actions (more recent = higher weight)
DECAY_HALF_LIFE = 50  # actions


def _hash_context(context: str) -> str:
    """Hash context string for dedup."""
    return hashlib.md5(context.encode()).hexdigest()[:8]


def load_feedback() -> list:
    """Load all feedback entries."""
    if FEEDBACK_DB.exists():
        try:
            data = json.loads(FEEDBACK_DB.read_text(encoding="utf-8"))
            return data.get("entries", [])
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_feedback(entries: list):
    """Save feedback entries (keep last 1000)."""
    CACHE_DIR = HERMES_HOME / "cache"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if len(entries) > 1000:
        entries = entries[-1000:]
    FEEDBACK_DB.write_text(
        json.dumps({"entries": entries, "updated": datetime.now().isoformat()},
                    indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def record_outcome(action_id: str, outcome: float, context: str = "", evidence: str = ""):
    """Record action outcome. outcome: -1.0 (fail) to 1.0 (success)."""
    entries = load_feedback()
    entries.append({
        "action_id": action_id,
        "outcome": max(-1.0, min(1.0, outcome)),
        "context": context[:200],
        "context_hash": _hash_context(context),
        "evidence": evidence[:300],
        "timestamp": datetime.now().isoformat(),
    })
    save_feedback(entries)
    # ponytail: mirror to action_log.jsonl (same format as action_executor._log_action)
    try:
        CACHE_DIR = HERMES_HOME / "cache"
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(CACHE_DIR / "action_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "action_id": action_id,
                "event": "outcome",
                "status": "success" if outcome > 0 else "failed",
                "outcome": max(-1.0, min(1.0, outcome)),
                "timestamp": datetime.now().isoformat(),
            }, ensure_ascii=False) + "\n")
    except OSError:
        pass


def get_action_history(action_id: str, last_n: int = 50) -> list:
    """Get recent outcomes for a specific action."""
    entries = load_feedback()
    action_entries = [e for e in entries if e.get("action_id") == action_id]
    return action_entries[-last_n:]


def compute_weight(action_id: str) -> float:
    """Compute weight for an action based on outcome history.
    
    Uses exponential decay: recent outcomes matter more.
    Returns weight from 0.5 (never works) to 1.5 (always works).
    """
    history = get_action_history(action_id, last_n=50)
    if not history:
        return 1.0  # Neutral weight for unknown actions

    total_weight = 0.0
    weight_sum = 0.0

    for i, entry in enumerate(history):
        # Exponential decay: most recent has weight 1.0, oldest has ~0.01
        decay = 2 ** (-i / DECAY_HALF_LIFE)
        outcome = entry.get("outcome", 0.0)
        total_weight += outcome * decay
        weight_sum += decay

    if weight_sum == 0:
        return 1.0

    avg_outcome = total_weight / weight_sum  # Range: -1.0 to 1.0

    # Map to weight: -1.0 -> 0.5, 0.0 -> 1.0, 1.0 -> 1.5
    weight = 1.0 + (avg_outcome * 0.5)
    return max(0.5, min(1.5, weight))


def get_all_weights() -> dict:
    """Compute weights for all known actions."""
    entries = load_feedback()
    action_ids = set(e.get("action_id", "") for e in entries)
    weights = {}
    for aid in action_ids:
        if aid:
            weights[aid] = {
                "weight": compute_weight(aid),
                "attempts": len(get_action_history(aid)),
            }
    return weights


def save_weights():
    """Compute and save weights to file."""
    weights = get_all_weights()
    CACHE_DIR = HERMES_HOME / "cache"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    WEIGHTS_CACHE.write_text(
        json.dumps({"weights": weights, "updated": datetime.now().isoformat()},
                    indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    return weights


def get_context_signature(action_id: str) -> str:
    """Get the most common context for an action (for pattern matching)."""
    history = get_action_history(action_id, last_n=20)
    contexts = [e.get("context_hash", "") for e in history if e.get("context_hash")]
    if not contexts:
        return ""
    # Most common context hash
    from collections import Counter
    return Counter(contexts).most_common(1)[0][0]


def get_by_type(action_type: str) -> list:
    """
    Возвращает все исходы для данного типа действия.
    Нужно для BayesianScorer.
    """
    entries = load_feedback()
    return [e for e in entries if e.get("action_id", "").startswith(action_type)]


def record_failure(action_id: str, outcome: float, evidence: str = ""):
    """
    Явная запись провала.
    outcome должен быть отрицательным: -1.0 (полный провал), -0.5 (частичный).
    """
    if outcome > 0:
        raise ValueError("record_failure expects outcome < 0, got %s" % outcome)
    record_outcome(action_id, outcome, evidence=evidence)


def report():
    """Print weight report."""
    weights = save_weights()
    if not weights:
        print("No outcomes recorded yet.")
        return

    print("=== Action Weight Report ===\n")
    print("%-40s %8s %8s %8s" % ("Action", "Weight", "Attempts", "Success%"))
    print("-" * 70)
    for aid, w in sorted(weights.items(), key=lambda x: -x[1].get("weight", 1.0)):
        weight = w["weight"]
        attempts = w["attempts"]
        history = get_action_history(aid, last_n=attempts)
        successes = sum(1 for e in history if e.get("outcome", 0) > 0)
        rate = (successes / attempts * 100) if attempts > 0 else 0
        print("%-40s %8.3f %8d %7.0f%%" % (aid[:40], weight, attempts, rate))


if __name__ == "__main__":
    report()
