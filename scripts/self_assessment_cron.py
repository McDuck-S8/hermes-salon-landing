#!/usr/bin/env python3
"""Self-Assessment Cron — analyzes recent sessions for improvement patterns.
Runs as a no_agent cron, outputs actionable insights.
"""
import json, os, sqlite3, sys
from pathlib import Path
from datetime import datetime, timedelta

HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
SESSIONS_DB = HERMES_HOME / "state.db"
STATE_FILE = HERMES_HOME / "cache" / "self_assessment_state.json"
OUTPUT_FILE = HERMES_HOME / "cache" / "self_assessment_latest.md"

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"last_check": None, "patterns": {}}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

def get_recent_sessions(hours=24):
    """Get sessions from last N hours."""
    if not SESSIONS_DB.exists():
        return []
    
    conn = sqlite3.connect(str(SESSIONS_DB))
    cutoff = (datetime.now() - timedelta(hours=hours)).timestamp()
    
    try:
        cursor = conn.execute(
            "SELECT id, title, started_at FROM sessions WHERE started_at > ? ORDER BY started_at DESC LIMIT 20",
            (cutoff,)
        )
        return cursor.fetchall()
    except:
        return []
    finally:
        conn.close()

def analyze_session_patterns(sessions):
    """Analyze sessions for common failure patterns."""
    patterns = {
        "tool_errors": 0,
        "retries": 0,
        "long_sessions": 0,
        "short_sessions": 0,
        "total": len(sessions),
    }
    
    for sid, title, started in sessions:
        title_lower = (title or "").lower()
        if any(w in title_lower for w in ["error", "ошибка", "failed", "не удалось"]):
            patterns["tool_errors"] += 1
        if any(w in title_lower for w in ["retry", "попыт", "снова"]):
            patterns["retries"] += 1
    
    return patterns

def generate_report(patterns, sessions):
    """Generate self-assessment report."""
    report = []
    report.append("# Self-Assessment Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"Sessions analyzed: {patterns['total']}")
    report.append("")
    
    if patterns['total'] == 0:
        report.append("No recent sessions to analyze.")
        return "\n".join(report)
    
    report.append("## Patterns Detected")
    report.append(f"- Error sessions: {patterns['tool_errors']}")
    report.append(f"- Retry patterns: {patterns['retries']}")
    report.append("")
    
    # Recommendations
    report.append("## Recommendations")
    if patterns['tool_errors'] > 2:
        report.append("- HIGH: Multiple error sessions detected. Consider:")
        report.append("  - Adding better error handling to tools")
        report.append("  - Improving tool descriptions for correct usage")
    if patterns['retries'] > 3:
        report.append("- HIGH: Many retry patterns. Consider:")
        report.append("  - Adding retry logic to tools")
        report.append("  - Improving first-attempt success rate")
    if patterns['total'] > 10:
        report.append("- MEDIUM: High session volume. Consider:")
        report.append("  - Consolidating similar tasks")
        report.append("  - Creating skills for recurring patterns")
    
    report.append("")
    report.append("## Recent Sessions")
    for sid, title, started in sessions[:10]:
        ts = datetime.fromtimestamp(started).strftime('%Y-%m-%d %H:%M') if started else '?'
        report.append(f"- [{ts}] {title or 'Untitled'}")
    
    return "\n".join(report)

def main():
    try:
        from chain_heartbeat import beat
        beat("self_assessment_cron")
    except ImportError:
        pass
    
    state = load_state()
    
    sessions = get_recent_sessions(hours=24)
    patterns = analyze_session_patterns(sessions)
    report = generate_report(patterns, sessions)
    
    # Save report
    OUTPUT_FILE.write_text(report, encoding="utf-8")
    
    # Update state
    state["last_check"] = datetime.now().isoformat()
    state["patterns"] = patterns
    save_state(state)
    
    print(report)

if __name__ == "__main__":
    main()
