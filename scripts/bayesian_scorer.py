#!/usr/bin/env python3
"""
Bayesian Scorer — вероятностная оценка каждого решения.


> Revisit: when scoring formula, priors, or usage contexts change. Last touched: 2026-07-02.
Формула: P(H|E) = P(E|H) * P(H) / P(E)
  H = гипотеза (сигнал приведёт к результату)
  E = Evidence (сигнал + контекст)

Используется:
  1. signal_scanner — оценка сигнала перед добавлением в workshop
  2. dev_processor — приоритет целей на тестирование
  3. daily metrics — P(поток иссяк) вместо простого порога
  4. SELF_IDENTITY.md — каждый отдел проверяет: "Оценено Bayesian?"

Usage:
    from bayesian_scorer import compute_score, score_signal, score_goal_priority, assess_flow_health
"""
import json
import math
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import Counter

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
HISTORY_FILE = CACHE_DIR / "scorer_history.json"
WORKSHOP_FILE = HERMES_HOME / "ARBITRAGE_WORKSHOP.md"
GOALS_FILE = CACHE_DIR / "goal_queue.json"


def _backup_file(path: Path):
    """Save current version of file to .bak before overwriting."""
    if path.exists():
        bak = path.with_suffix(path.suffix + ".bak")
        try:
            import shutil
            shutil.copy2(path, bak)
        except OSError:
            pass  # non-fatal


# ─── Prior Knowledge ──────────────────────────────────────────────
# Prior probabilities from historical data
DEFAULT_PRIORS = {
    "source_hacker_news": 0.4,     # HN signals: 40% historically useful
    "source_github": 0.35,          # GitHub repos: 35%
    "source_telegram": 0.25,        # TG channels: 25%
    "source_web": 0.2,              # Random web: 20%
    "category_ai": 0.5,            # AI-related: higher base rate
    "category_business": 0.35,
    "category_tools": 0.4,
    "category_security": 0.3,
    "category_arbitrage": 0.45,
    "category_automation": 0.4,
    "category_web": 0.3,
    "category_tech": 0.25,
    "category_finance": 0.35,
}

# Likelihood ratios: how much evidence shifts the prior
EVIDENCE_WEIGHTS = {
    "high_engagement": 1.5,        # High HN score or GitHub stars
    "freshness_new": 1.3,          # < 24h old
    "freshness_week": 1.0,         # < 7d old
    "freshness_stale": 0.6,        # > 7d old
    "related_to_success": 1.8,     # Similar signal worked before
    "related_to_failure": 0.4,     # Similar signal failed before
    "network_available": 1.1,      # Network is up
    "network_down": 0.7,           # Network degraded
    "department_available": 1.2,   # Target department is operational
    "department_overloaded": 0.6,  # Department has too many pending tasks
    "no_proxies": 0.5,            # No proxy available
    "has_proxies": 1.1,           # Proxies working
}


# ─── History tracking ─────────────────────────────────────────────
def _load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text("utf-8"))
        except:
            pass
    return {"signals": [], "outcomes": [], "daily_counts": {}}


def _save_history(history: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    # Keep only last 90 days
    cutoff = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
    history["signals"] = [s for s in history.get("signals", []) if s.get("ts", "") > cutoff]
    history["outcomes"] = [o for o in history.get("outcomes", []) if o.get("ts", "") > cutoff]
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2, default=str), "utf-8")


def record_outcome(signal_hash: str, success: bool, revenue: float = 0.0):
    """Record outcome of a signal for future Bayesian updates."""
    history = _load_history()
    history["outcomes"].append({
        "hash": signal_hash,
        "success": success,
        "revenue": revenue,
        "ts": datetime.now(timezone.utc).isoformat(),
    })
    _save_history(history)


# ─── Context gathering ────────────────────────────────────────────
def _get_context() -> dict:
    """Gather current system context for scoring."""
    ctx = {
        "network_ok": True,
        "departments_ok": 0,
        "departments_total": 13,
        "recent_successes": 0,
        "recent_failures": 0,
        "today_signals": 0,
        "week_signals": 0,
    }

    # Check network (quick DNS test)
    try:
        import subprocess
        r = subprocess.run(
            ["curl", "-s", "--connect-timeout", "3", "--max-time", "5",
             "https://httpbin.org/ip"],
            capture_output=True, timeout=8
        )
        ctx["network_ok"] = r.returncode == 0 and len(r.stdout) > 0
    except:
        ctx["network_ok"] = False

    # Check goals for department status
    if GOALS_FILE.exists():
        try:
            goals = json.loads(GOALS_FILE.read_text("utf-8")).get("goals", [])
            active = [g for g in goals if g.get("status") in ("active", "in_progress")]
            ctx["departments_overloaded"] = len(active) > 5
        except:
            pass

    # Check history for recent outcomes
    history = _load_history()
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).isoformat()
    day_ago = (now - timedelta(days=1)).isoformat()

    for outcome in history.get("outcomes", []):
        if outcome.get("ts", "") > week_ago:
            if outcome.get("success"):
                ctx["recent_successes"] += 1
            else:
                ctx["recent_failures"] += 1

    # Count today's signals
    today = now.strftime("%Y-%m-%d")
    ctx["today_signals"] = history.get("daily_counts", {}).get(today, 0)

    # Count week's signals
    for date_str, count in history.get("daily_counts", {}).items():
        if date_str >= week_ago[:10]:
            ctx["week_signals"] += count

    return ctx


# ─── Bayesian scoring ─────────────────────────────────────────────
def compute_score(signal: dict, context: dict = None) -> float:
    """
    Compute Bayesian posterior probability for a signal.
    
    P(H|E) = P(E|H) * P(H) / P(E)
    
    Returns: float [0.0, 1.0]
    """
    if context is None:
        context = _get_context()

    # Step 1: Prior P(H) — based on source and category
    prior = 0.25  # default prior

    source = signal.get("source", "unknown")
    source_key = f"source_{source}"
    if source_key in DEFAULT_PRIORS:
        prior = DEFAULT_PRIORS[source_key]

    category = signal.get("category", "tech")
    cat_key = f"category_{category}"
    if cat_key in DEFAULT_PRIORS:
        # Blend source and category priors
        prior = (prior + DEFAULT_PRIORS[cat_key]) / 2

    # Step 2: Likelihood P(E|H) — evidence adjustment
    likelihood = 1.0

    # Engagement signal
    score = signal.get("score", 0)
    stars = signal.get("stars", 0)
    if score > 100 or stars > 500:
        likelihood *= EVIDENCE_WEIGHTS["high_engagement"]
    elif score > 30 or stars > 100:
        likelihood *= 1.2

    # Freshness
    ts = signal.get("ts", "")
    if ts:
        try:
            sig_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            age_hours = (datetime.now(timezone.utc) - sig_time).total_seconds() / 3600
            if age_hours < 24:
                likelihood *= EVIDENCE_WEIGHTS["freshness_new"]
            elif age_hours < 168:  # 7 days
                likelihood *= EVIDENCE_WEIGHTS["freshness_week"]
            else:
                likelihood *= EVIDENCE_WEIGHTS["freshness_stale"]
        except:
            pass

    # Historical similarity
    history = _load_history()
    similar_outcomes = [
        o for o in history.get("outcomes", [])
        if o.get("category") == category or o.get("source") == source
    ]
    if similar_outcomes:
        success_rate = sum(1 for o in similar_outcomes if o.get("success")) / len(similar_outcomes)
        if success_rate > 0.6:
            likelihood *= EVIDENCE_WEIGHTS["related_to_success"]
        elif success_rate < 0.3:
            likelihood *= EVIDENCE_WEIGHTS["related_to_failure"]

    # Context: network
    if context.get("network_ok"):
        likelihood *= EVIDENCE_WEIGHTS["network_available"]
    else:
        likelihood *= EVIDENCE_WEIGHTS["network_down"]

    # Context: department load — REMOVED (queue handles load now)
    # if context.get("departments_overloaded"):
    #     likelihood *= EVIDENCE_WEIGHTS["department_overloaded"]

    # Step 3: Posterior P(H|E) = likelihood * prior (normalized)
    posterior = likelihood * prior

    # Normalize to [0, 1] using sigmoid
    # This prevents values > 1.0 and provides smooth scaling
    normalized = posterior / (posterior + (1 - prior))

    return round(min(max(normalized, 0.0), 1.0), 3)


def score_signal(signal: dict) -> dict:
    """Score a signal and return detailed breakdown."""
    context = _get_context()
    score = compute_score(signal, context)

    return {
        "score": score,
        "verdict": "accept" if score >= 0.3 else "reject",
        "reason": _explain_score(signal, score, context),
        "context": {
            "network": "ok" if context.get("network_ok") else "down",
            "today_signals": context.get("today_signals", 0),
            "week_signals": context.get("week_signals", 0),
            "recent_success_rate": (
                context["recent_successes"] /
                max(context["recent_successes"] + context["recent_failures"], 1)
            ),
        },
    }


def _explain_score(signal: dict, score: float, context: dict) -> str:
    """Generate human-readable explanation of the score."""
    parts = []

    source = signal.get("source", "unknown")
    category = signal.get("category", "tech")
    parts.append(f"source={source}({DEFAULT_PRIORS.get(f'source_{source}', 0.25):.2f})")
    parts.append(f"cat={category}({DEFAULT_PRIORS.get(f'category_{category}', 0.25):.2f})")

    if signal.get("score", 0) > 30 or signal.get("stars", 0) > 100:
        parts.append("high_engagement(+1.2x)")

    if not context.get("network_ok"):
        parts.append("network_down(0.7x)")

    if context.get("departments_overloaded"):
        parts.append("dept_overloaded(0.6x)")

    return f"score={score:.3f} [{', '.join(parts)}]"


# ─── Goal priority scoring ────────────────────────────────────────
def score_goal_priority(goal: dict, brick_context: dict = None) -> float:
    """
    Compute Bayesian priority for a goal.
    
    Replaces static: urgency * impact.
    Uses: P(success | context, history) * expected_value
    """
    if brick_context is None:
        brick_context = _get_context()

    # Base probability from goal attributes
    urgency = goal.get("urgency", 5) / 10.0
    impact = goal.get("impact", 5) / 10.0

    # Bayesian adjustment based on history
    history = _load_history()
    goal_type = goal.get("type", "unknown")
    related_outcomes = [
        o for o in history.get("outcomes", [])
        if o.get("type") == goal_type
    ]

    if related_outcomes:
        success_rate = sum(1 for o in related_outcomes if o.get("success")) / len(related_outcomes)
        # Update prior with historical success rate
        prior_adj = success_rate
    else:
        prior_adj = 0.3  # no history = neutral prior

    # Context adjustments
    context_mult = 1.0
    if brick_context.get("network_ok"):
        context_mult *= 1.1
    else:
        context_mult *= 0.7

    if brick_context.get("recent_successes") > brick_context.get("recent_failures"):
        context_mult *= 1.2  # momentum bonus

    # Bayesian priority = P(success) * expected_value
    p_success = prior_adj * context_mult
    expected_value = urgency * impact

    priority = p_success * expected_value * 10  # scale to 0-10
    return round(min(max(priority, 0.1), 10.0), 2)


def boost_goal(goal_id: str, boost: float = 2.0, duration_minutes: int = 15):
    """
    Boost a goal's priority temporarily.
    Called when negative event detected (cron_job_died, heartbeat_missed, etc.)
    """
    goals = _load_goals_from_file()
    for goal in goals:
        if goal.get("id") == goal_id:
            # Apply boost
            current_priority = goal.get("priority", 5)
            goal["priority"] = min(10, current_priority + boost)
            goal["boosted_until"] = (datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)).isoformat()
            goal["boost_reason"] = f"Auto-boost from event at {datetime.now(timezone.utc).isoformat()}"
            goal["updated_at"] = datetime.now(timezone.utc).isoformat()
            break
    
    _save_goals_to_file(goals)


def _load_goals_from_file() -> list:
    """Load goals from goal_queue.json."""
    if GOALS_FILE.exists():
        try:
            data = json.loads(GOALS_FILE.read_text("utf-8"))
            return data.get("goals", []) if isinstance(data, dict) else list(data)
        except Exception:
            pass
    return []


def _save_goals_to_file(goals: list):
    """Save goals to goal_queue.json."""
    GOALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _backup_file(GOALS_FILE)
    GOALS_FILE.write_text(
        json.dumps({"goals": goals, "updated_at": datetime.now(timezone.utc).isoformat()},
                   indent=2, ensure_ascii=False, default=str),
        "utf-8"
    )


# ─── Flow health assessment ───────────────────────────────────────
def assess_flow_health(history_days: int = 7) -> dict:
    """
    Bayesian assessment of signal flow health.
    
    Returns:
        status: "healthy" | "warning" | "critical"
        p_flow_alive: probability that signal flow is still active
        daily_rate: average signals per day
        alert_level: "none" | "warning" | "critical"
    """
    history = _load_history()
    now = datetime.now(timezone.utc)

    # Count signals per day for last N days
    daily_counts = {}
    for i in range(history_days):
        date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        daily_counts[date] = history.get("daily_counts", {}).get(date, 0)

    total = sum(daily_counts.values())
    avg = total / max(history_days, 1)
    today = daily_counts.get(now.strftime("%Y-%m-%d"), 0)

    # Bayesian: P(flow_alive | observed_data)
    # Likelihood: if flow is alive, signals follow Poisson distribution
    # P(data | alive) ~ Poisson(avg)^total
    # P(data | dead) = 0 for total > 0, 1 for total = 0

    if total == 0:
        # No signals at all — strong evidence flow is dead
        p_alive = 0.1
    elif today == 0 and avg > 0:
        # Day without signals, but week has some — moderate concern
        p_alive = 0.6
    elif today == 0 and avg == 0:
        # No signals at all — flow likely dead
        p_alive = 0.1
    else:
        # Signals present — flow likely alive
        # Boost if rate is consistent
        variance = sum((d - avg) ** 2 for d in daily_counts.values()) / len(daily_counts)
        consistency = 1.0 / (1.0 + variance / max(avg, 0.1))
        p_alive = min(0.95, 0.5 + 0.4 * consistency + 0.1 * min(avg / 5, 0.5))

    # Determine alert level
    if p_alive < 0.4:
        alert = "critical"
        status = "CRITICAL: Signal flow likely dead"
    elif p_alive < 0.7 or (today == 0 and avg > 2):
        alert = "warning"
        status = "WARNING: Signal flow degraded"
    else:
        alert = "none"
        status = "healthy"

    return {
        "status": status,
        "alert_level": alert,
        "p_flow_alive": round(p_alive, 3),
        "daily_rate": round(avg, 2),
        "today": today,
        "week_total": total,
        "history_days": history_days,
    }


# ─── CLI ──────────────────────────────────────────────────────────
def main():
    import sys

    if "--status" in sys.argv:
        health = assess_flow_health()
        print(f"Flow health: {health['status']}")
        print(f"  P(alive): {health['p_flow_alive']}")
        print(f"  Daily rate: {health['daily_rate']}")
        print(f"  Today: {health['today']}, Week: {health['week_total']}")

    elif "--score" in sys.argv:
        # Score a test signal
        test = {"source": "hacker_news", "category": "ai", "score": 50}
        result = score_signal(test)
        print(f"Test signal: {json.dumps(result, indent=2)}")

    elif "--history" in sys.argv:
        history = _load_history()
        print(f"Signals: {len(history.get('signals', []))}")
        print(f"Outcomes: {len(history.get('outcomes', []))}")
        print(f"Daily counts: {len(history.get('daily_counts', {}))} days")

    else:
        print("Usage: bayesian_scorer.py --status|--score|--history")


if __name__ == "__main__":
    main()
