#!/usr/bin/env python3
"""
Context Engine — Act 3: Contextual Spaces.

Determines "what matters NOW" by combining:
1. Time context (hour, day, urgency patterns)
2. User activity context (recent sessions, pending goals)
3. System state context (errors, health, knowledge gaps)
4. Knowledge relevance (rank KC entries by current context)

Output: Ranked list of {knowledge_id, relevance_score, reason} 
that tells the agent what to focus on RIGHT NOW.

This is the missing piece between "having knowledge" and "using knowledge wisely."
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
CUBE_DB = CACHE_DIR / "knowledge_cube.db"
STATE_DB = HERMES_HOME / "state.db"
CONTEXT_CACHE = CACHE_DIR / "current_context.json"

# ---------------------------------------------------------------------------
# Time Context
# ---------------------------------------------------------------------------

def get_time_context() -> dict:
    """What time is it and what does that imply?"""
    now = datetime.now()
    hour = now.hour
    dow = now.weekday()  # 0=Mon, 6=Sun
    
    # Time-of-day phases
    if 6 <= hour < 10:
        phase = "morning"
        energy = "high"
        focus = "planning"
    elif 10 <= hour < 14:
        phase = "midday"
        energy = "peak"
        focus = "execution"
    elif 14 <= hour < 18:
        phase = "afternoon"
        energy = "moderate"
        focus = "iteration"
    elif 18 <= hour < 22:
        phase = "evening"
        energy = "declining"
        focus = "review"
    else:
        phase = "night"
        energy = "low"
        focus = "maintenance"
    
    # Weekend vs weekday
    is_weekend = dow >= 5
    
    return {
        "hour": hour,
        "dow": dow,
        "dow_name": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dow],
        "phase": phase,
        "energy": energy,
        "focus": focus,
        "is_weekend": is_weekend,
        "timestamp": now.isoformat(),
    }


# ---------------------------------------------------------------------------
# User Activity Context
# ---------------------------------------------------------------------------

def get_user_context() -> dict:
    """What has the user been doing recently?"""
    context = {
        "recent_sessions": 0,
        "last_activity": None,
        "pending_goals": 0,
        "user_mood": "unknown",
    }
    
    # Check session DB for recent activity
    try:
        import sqlite3
        if STATE_DB.exists():
            conn = sqlite3.connect(str(STATE_DB))
            conn.row_factory = sqlite3.Row
            
            # Count recent sessions (last 24h)
            cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
            rows = conn.execute(
                "SELECT COUNT(DISTINCT session_id) FROM messages WHERE ts > ?",
                (cutoff,)
            ).fetchone()
            context["recent_sessions"] = rows[0] if rows else 0
            
            # Last activity
            last = conn.execute(
                "SELECT ts FROM messages ORDER BY ts DESC LIMIT 1"
            ).fetchone()
            context["last_activity"] = last[0] if last else None
            
            conn.close()
    except Exception:
        pass
    
    # Check for pending tasks/goals
    try:
        goals_file = CACHE_DIR / "agent_goals.json"
        if goals_file.exists():
            goals = json.loads(goals_file.read_text())
            context["pending_goals"] = len([g for g in goals if g.get("status") == "pending"])
    except Exception:
        pass
    
    return context


# ---------------------------------------------------------------------------
# System Context
# ---------------------------------------------------------------------------

def get_system_context() -> dict:
    """What's the system state right now?"""
    context = {
        "errors_active": 0,
        "knowledge_expired": 0,
        "knowledge_expiring_soon": 0,
        "disk_usage_pct": 0,
        "daemon_status": {},
    }
    
    # Count active errors
    try:
        error_log = HERMES_HOME / "logs" / "errors.log"
        if error_log.exists():
            cutoff = (datetime.now() - timedelta(hours=1)).isoformat()
            lines = error_log.read_text().splitlines()
            recent = [l for l in lines if l[:19] > cutoff]
            context["errors_active"] = len(recent)
    except Exception:
        pass
    
    # Count expired knowledge
    try:
        conn = sqlite3.connect(str(CUBE_DB))
        expired = conn.execute(
            "SELECT COUNT(*) FROM experiences WHERE expiration_date IS NOT NULL AND expiration_date < ?",
            (datetime.now().isoformat(),)
        ).fetchone()[0]
        context["knowledge_expired"] = expired
        
        expiring = conn.execute(
            "SELECT COUNT(*) FROM experiences WHERE expiration_date IS NOT NULL AND expiration_date > ? AND expiration_date < ?",
            (datetime.now().isoformat(), (datetime.now() + timedelta(days=30)).isoformat())
        ).fetchone()[0]
        context["knowledge_expiring_soon"] = expiring
        conn.close()
    except Exception:
        pass
    
    # Disk usage
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        context["disk_usage_pct"] = round(used / total * 100, 1)
    except Exception:
        pass
    
    return context


# ---------------------------------------------------------------------------
# Knowledge Relevance Scorer
# ---------------------------------------------------------------------------

def score_knowledge_relevance(entry: dict, time_ctx: dict, user_ctx: dict, sys_ctx: dict) -> float:
    """
    Score how relevant a knowledge entry is to the current context.
    Returns 0.0 to 1.0.
    """
    score = 0.0
    reasons = []
    
    # 1. Confidence weight (0-0.3)
    conf = entry.get("confidence", 0.5)
    score += conf * 0.3
    
    # 2. Freshness weight (0-0.3)
    created = entry.get("created_at", entry.get("ts", ""))
    if created:
        try:
            created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            age_days = (datetime.now() - created_dt.replace(tzinfo=None)).days
            if age_days < 7:
                score += 0.3
                reasons.append("fresh")
            elif age_days < 30:
                score += 0.2
                reasons.append("recent")
            elif age_days < 90:
                score += 0.1
                reasons.append("established")
            else:
                score += 0.05
                reasons.append("old")
        except Exception:
            score += 0.1
    
    # 3. Expiration penalty (0 to -0.2)
    exp = entry.get("expiration_date")
    if exp:
        try:
            exp_dt = datetime.fromisoformat(exp)
            if exp_dt < datetime.now():
                score -= 0.2
                reasons.append("EXPIRED")
            elif exp_dt < datetime.now() + timedelta(days=7):
                score -= 0.1
                reasons.append("expiring_soon")
        except Exception:
            pass
    
    # 4. Importance weight (0-0.2)
    importance = entry.get("importance", 5)
    if isinstance(importance, (int, float)):
        score += min(importance / 10.0, 1.0) * 0.2
    
    # 5. Access count bonus (0-0.1) — frequently used = relevant
    access = entry.get("access_count", 0)
    if access > 10:
        score += 0.1
        reasons.append("frequently_used")
    elif access > 3:
        score += 0.05
    
    # 6. Time-of-day matching (0-0.1)
    # Certain knowledge types are more relevant at certain times
    tags = entry.get("tags", "")
    if isinstance(tags, list):
        tags = ",".join(tags)
    if time_ctx["phase"] == "morning" and "planning" in str(tags).lower():
        score += 0.1
        reasons.append("morning_relevant")
    elif time_ctx["phase"] == "night" and "maintenance" in str(tags).lower():
        score += 0.1
        reasons.append("night_relevant")
    
    return min(max(score, 0.0), 1.0), reasons


# ---------------------------------------------------------------------------
# Main: Build Current Context
# ---------------------------------------------------------------------------

def build_context() -> dict:
    """
    Build the complete current context.
    Returns a dict with time, user, system, and ranked knowledge.
    """
    time_ctx = get_time_context()
    user_ctx = get_user_context()
    sys_ctx = get_system_context()
    
    # Get top knowledge entries ranked by relevance
    ranked_knowledge = []
    try:
        conn = sqlite3.connect(str(CUBE_DB))
        conn.row_factory = sqlite3.Row
        
        # Get recent and high-confidence entries
        rows = conn.execute("""
            SELECT id, content, tags, source, '' as category, importance, 
                   confidence, expiration_date, verification_method,
                   ts as created_at, 0 as access_count
            FROM experiences 
            WHERE confidence >= 0.3
            ORDER BY confidence DESC, ts DESC
            LIMIT 100
        """).fetchall()
        
        for row in rows:
            entry = dict(row)
            relevance, reasons = score_knowledge_relevance(entry, time_ctx, user_ctx, sys_ctx)
            ranked_knowledge.append({
                "id": entry["id"],
                "content_preview": entry["content"][:100],
                "relevance": round(relevance, 3),
                "reasons": reasons,
                "confidence": entry.get("confidence", 0.5),
                "source": entry.get("source", ""),
            })
        
        # Sort by relevance
        ranked_knowledge.sort(key=lambda x: x["relevance"], reverse=True)
        ranked_knowledge = ranked_knowledge[:20]  # Top 20
        
        conn.close()
    except Exception:
        pass
    
    # Build priority actions based on context
    priority_actions = []
    
    if sys_ctx["errors_active"] > 0:
        priority_actions.append({
            "action": "fix_errors",
            "reason": f"{sys_ctx['errors_active']} active errors",
            "urgency": "high",
        })
    
    if sys_ctx["knowledge_expired"] > 10:
        priority_actions.append({
            "action": "refresh_expired_knowledge",
            "reason": f"{sys_ctx['knowledge_expired']} expired knowledge entries",
            "urgency": "high",
        })
    
    if user_ctx["recent_sessions"] == 0:
        priority_actions.append({
            "action": "autonomous_work",
            "reason": "No recent user activity — work independently",
            "urgency": "medium",
        })
    
    context = {
        "timestamp": datetime.now().isoformat(),
        "time": time_ctx,
        "user": user_ctx,
        "system": sys_ctx,
        "ranked_knowledge": ranked_knowledge,
        "priority_actions": priority_actions,
        "summary": _build_summary(time_ctx, user_ctx, sys_ctx, ranked_knowledge, priority_actions),
    }
    
    # Cache context
    try:
        CONTEXT_CACHE.write_text(json.dumps(context, indent=2, ensure_ascii=False))
    except Exception:
        pass
    
    return context


def _build_summary(time_ctx, user_ctx, sys_ctx, ranked_knowledge, priority_actions):
    """Build a human-readable summary of current context."""
    parts = []
    
    # Time
    parts.append(f"It's {time_ctx['phase']} ({time_ctx['dow_name']} {time_ctx['hour']}h), energy={time_ctx['energy']}")
    
    # User
    if user_ctx["recent_sessions"] > 0:
        parts.append(f"User active recently ({user_ctx['recent_sessions']} sessions in 24h)")
    else:
        parts.append("User inactive — autonomous mode")
    
    # System
    if sys_ctx["errors_active"] > 0:
        parts.append(f"⚠️ {sys_ctx['errors_active']} active errors")
    if sys_ctx["knowledge_expired"] > 0:
        parts.append(f"⚠️ {sys_ctx['knowledge_expired']} expired knowledge entries")
    
    # Top knowledge
    if ranked_knowledge:
        top = ranked_knowledge[0]
        parts.append(f"Top relevant: {top['content_preview']}... (score={top['relevance']})")
    
    # Priority actions
    if priority_actions:
        parts.append(f"Priority: {priority_actions[0]['action']} ({priority_actions[0]['reason']})")
    
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    
    if "--status" in sys.argv:
        ctx = build_context()
        print(json.dumps(ctx, indent=2, ensure_ascii=False))
    elif "--time" in sys.argv:
        print(json.dumps(get_time_context(), indent=2))
    elif "--user" in sys.argv:
        print(json.dumps(get_user_context(), indent=2))
    elif "--system" in sys.argv:
        print(json.dumps(get_system_context(), indent=2))
    else:
        ctx = build_context()
        print(ctx["summary"])
