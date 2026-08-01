#!/usr/bin/env python3
"""
Hermes Self-Monitor — checks if I'm actually being useful.
Runs after every session. Answers:

> Revisit: when self-monitor logic, health checks, or monitoring thresholds change. Last touched: 2026-07-02.
1. Did I do something or just talked?
2. Did I record what I learned?
3. Did I improve something?
"""
import json
from datetime import datetime
from pathlib import Path

HERMES_ROOT = Path("D:/Portable_Soft/hermes")
LOG_FILE = HERMES_ROOT / "logs" / "self_monitor.log"
STATE_FILE = HERMES_ROOT / "cache" / "self_monitor_state.json"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)

def load_state():
    try:
        return json.loads(STATE_FILE.read_text())
    except:
        return {"sessions": 0, "actions": 0, "talks": 0, "improvements": 0, "last_check": None}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def record_action():
    """Call this after every real action (file edit, API call, deployment)."""
    state = load_state()
    state["actions"] += 1
    state["last_action"] = datetime.now().isoformat()
    save_state(state)
    log(f"Action recorded. Total: {state['actions']}")

def record_talk():
    """Call this when I only talked (no real action)."""
    state = load_state()
    state["talks"] += 1
    state["last_talk"] = datetime.now().isoformat()
    save_state(state)
    log(f"Talk recorded (no action). Total talks: {state['talks']}")

def record_improvement():
    """Call this when I improved something (fixed bug, added feature)."""
    state = load_state()
    state["improvements"] += 1
    state["last_improvement"] = datetime.now().isoformat()
    save_state(state)
    log(f"Improvement recorded. Total: {state['improvements']}")

def check_health():
    """Analyze if I'm being useful or just talking."""
    state = load_state()
    total = state["actions"] + state["talks"]
    if total == 0:
        return "NO_DATA"
    
    action_ratio = state["actions"] / total
    improvement_ratio = state["improvements"] / max(state["actions"], 1)
    
    if action_ratio < 0.3:
        return "TOO_MUCH_TALK"
    elif improvement_ratio < 0.1:
        return "ACTIONS_BUT_NO_IMPROVEMENTS"
    else:
        return "HEALTHY"

def report():
    state = load_state()
    health = check_health()
    total = state["actions"] + state["talks"]
    
    print(f"\n=== Self Monitor ===")
    print(f"Sessions: {state['sessions']}")
    print(f"Actions: {state['actions']}")
    print(f"Talks (no action): {state['talks']}")
    print(f"Improvements: {state['improvements']}")
    print(f"Action ratio: {state['actions']/max(total,1)*100:.0f}%")
    print(f"Health: {health}")
    
    if health == "TOO_MUCH_TALK":
        print("[WARN] I talk too much, do too little. Fix: act first, talk second.")
    elif talk_ratio < 0.1:
        print("[WARN] I act but don't improve. Fix: every action should improve something.")
    else:
        print("[OK] I'm being useful.")

if __name__ == "__main__":
    report()
