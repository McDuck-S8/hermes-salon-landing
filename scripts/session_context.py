#!/usr/bin/env python3
"""
Session Context Builder — assembles rich context from multiple sources.


> Revisit: when session context building, context slots, or context loading changes. Last touched: 2026-07-02.
Called at session start to give the agent immediate awareness of:
- What happened last session (session_bridge)
- Recent decisions and their outcomes (agent_decisions.json)
- Fix success rates (verification_state.json)
- Active goals (goal_queue.json — WP-5)
- Relevant knowledge from KC/Lavra (auto_recall)

Usage:
    python scripts/session_context.py "user message here"
    python scripts/session_context.py --status
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
DATA_DIR = HERMES_HOME / "data"

DECISIONS_FILE = CACHE_DIR / "agent_decisions.json"
VERIFICATION_FILE = DATA_DIR / "verification_state.json"
GOAL_QUEUE_FILE = CACHE_DIR / "goal_queue.json"
ACTION_WEIGHTS_FILE = CACHE_DIR / "action_weights.json"
OUTCOMES_FILE = CACHE_DIR / "action_outcomes.json"


def _load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def get_session_bridge_context() -> str:
    """Load last session state from session_bridge."""
    sys.path.insert(0, str(HERMES_HOME / "scripts"))
    try:
        from session_bridge import load_bridge
        state = load_bridge()
    except Exception:
        return ""

    if not state.get("last_session_end") and not state.get("last_session_ts"):
        return ""

    lines = []
    # ponytail: bridge stores last_session_ts, not last_session_end
    last_ts = state.get("last_session_end") or state.get("last_session_ts")
    lines.append(f"Last session: {last_ts}")
    if state.get("last_task"):
        lines.append(f"Last task: {state['last_task']}")
    if state.get("focus"):
        lines.append(f"Focus: {state['focus']}")
    if state.get("focus_history"):
        recent = state["focus_history"][-3:]
        history_str = " -> ".join(f["focus"] for f in recent if f.get("focus"))
        if history_str:
            lines.append(f"Focus history: {history_str}")
    if state.get("tags"):
        lines.append(f"Tags: {', '.join(state['tags'][-5:])}")

    return "\n".join(lines)


def get_recent_decisions_context(limit: int = 5) -> str:
    """Load last N decisions with outcomes."""
    data = _load_json(DECISIONS_FILE)
    if not data:
        return ""

    decisions = data.get("decisions", [])
    if not decisions:
        return ""

    lines = []
    for d in decisions[-limit:]:
        ts = d.get("timestamp", "?")[:16]
        title = d.get("title", "?")
        result = d.get("result", "")[:80]
        lines.append(f"[{ts}] {title}")
        if result:
            lines.append(f"  -> {result}")

    return "\n".join(lines)


def get_fix_success_rate() -> str:
    """Read fix verification success rates."""
    data = _load_json(VERIFICATION_FILE)
    if not data:
        return ""

    total = data.get("total_verified", 0)
    success = data.get("total_success", 0)
    if total == 0:
        return ""

    rate = (success / total) * 100
    return f"Fix success rate: {success}/{total} ({rate:.0f}%)"


def get_active_goals_context() -> str:
    """Load active goals from goal queue (WP-5)."""
    data = _load_json(GOAL_QUEUE_FILE)
    if not data:
        return ""

    goals = data.get("goals", [])
    active = [g for g in goals if g.get("status") == "active"]
    if not active:
        return ""

    lines = []
    for g in sorted(active, key=lambda x: -x.get("priority", 0))[:5]:
        progress = g.get("progress", 0) * 100
        lines.append(f"- [{g.get('priority', '?')}] {g.get('title', '?')} ({progress:.0f}%)")

    return "\n".join(lines)


def get_action_weights_context() -> str:
    """Read action weight learning results (WP-3)."""
    data = _load_json(ACTION_WEIGHTS_FILE)
    if not data:
        return ""

    weights = data.get("weights", {})
    if not weights:
        return ""

    high = [(k, v) for k, v in weights.items() if v.get("success_rate", 0) > 0.8]
    low = [(k, v) for k, v in weights.items() if v.get("success_rate", 0) < 0.3 and v.get("attempts", 0) >= 3]

    lines = []
    if high:
        lines.append(f"Top performing: {', '.join(k for k, _ in high[:3])}")
    if low:
        lines.append(f"Needs improvement: {', '.join(k for k, _ in low[:3])}")

    return "\n".join(lines)


def get_knowledge_graph_context() -> str:
    """Check if graphify graph exists and return summary."""
    graph_json = HERMES_HOME / "graphify-out" / "graph.json"
    if not graph_json.exists():
        return ""
    try:
        data = json.loads(graph_json.read_text(encoding="utf-8"))
        nodes = len(data.get("nodes", []))
        edges = len(data.get("links", []))
        return f"Knowledge graph available: {nodes} nodes, {edges} edges (query with /graphify query)"
    except Exception:
        return ""


def get_tool_catalog_context() -> str:
    """Summarize available tools from catalog."""
    catalog_path = HERMES_HOME / "skills" / "tool-catalog" / "SKILL.md"
    if not catalog_path.exists():
        return ""
    try:
        content = catalog_path.read_text(encoding="utf-8")
        # Count tools
        import re
        tool_count = len(re.findall(r"\| `[^`]+` \|", content))
        skill_count = content.count("### ")  # Approximate skill sections
        return f"Tool catalog: {tool_count} tools, {skill_count} categories loaded"
    except Exception:
        return ""


def get_feedback_store_context() -> str:
    """Summarize action history from feedback store."""
    try:
        from feedback_store import get_all_weights
        weights = get_all_weights()
        if not weights:
            return "No action outcomes recorded yet"
        total = sum(w.get("attempts", 0) for w in weights.values())
        return f"Action history: {len(weights)} actions tracked, {total} total attempts"
    except ImportError:
        return ""


def build_context(user_message: str = "") -> str:
    """Assemble full session context from all sources."""
    sections = []

    # 1. Session bridge
    bridge = get_session_bridge_context()
    # ponytail: required section — always present, fallback text instead of skipping
    sections.append(("Previous Session", bridge or "No previous session data"))

    # 2. Recent decisions
    decisions = get_recent_decisions_context()
    if decisions:
        sections.append(("Recent Decisions", decisions))

    # 3. Fix success rate
    fixes = get_fix_success_rate()
    if fixes:
        sections.append(("System Health", fixes))

    # 4. Active goals
    goals = get_active_goals_context()
    sections.append(("Active Goals", goals or "No active goals"))

    # 5. Action weights (learning feedback)
    weights = get_action_weights_context()
    if weights:
        sections.append(("Learning Feedback", weights))

    # 6. Knowledge graph (graphify) — required section
    graph = get_knowledge_graph_context()
    sections.append(("Knowledge Graph", graph or "No knowledge graph available"))

    # 7. Tool catalog summary (WP-1) — required section
    tool_summary = get_tool_catalog_context()
    sections.append(("Available Tools", tool_summary or "Tool catalog unavailable"))

    # 8. Feedback store status (WP-3)
    feedback = get_feedback_store_context()
    if feedback:
        sections.append(("Action History", feedback))

    if not sections:
        return ""

    # Build formatted block
    parts = ["=== SESSION CONTEXT ==="]
    for title, content in sections:
        parts.append(f"\n--- {title} ---")
        parts.append(content)
    parts.append("\n=== END SESSION CONTEXT ===")

    return "\n".join(parts)


def status():
    """Print context status for debugging."""
    print("=== Session Context Builder ===\n")

    bridge = get_session_bridge_context()
    print(f"[Session Bridge] {'OK' if bridge else 'EMPTY'}")
    if bridge:
        print(f"  {bridge[:200]}")

    decisions = get_recent_decisions_context()
    print(f"\n[Recent Decisions] {'OK' if decisions else 'EMPTY'}")

    fixes = get_fix_success_rate()
    print(f"\n[Fix Success] {fixes or 'NO DATA'}")

    goals = get_active_goals_context()
    print(f"\n[Active Goals] {'OK' if goals else 'EMPTY'}")

    weights = get_action_weights_context()
    print(f"\n[Action Weights] {'OK' if weights else 'NO DATA'}")

    print(f"\n--- Combined Context ---")
    ctx = build_context()
    if ctx:
        print(ctx)
    else:
        print("(empty)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "--status":
        status()
    else:
        msg = " ".join(args)
        ctx = build_context(msg)
        if ctx:
            print(ctx)
        else:
            print("(no context available)")
