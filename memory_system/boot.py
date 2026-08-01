#!/usr/bin/env python3
"""
Hermes Agent — Memory Boot Script
Reads persistent memory files and outputs them for injection into session context.
Run at session start. No dependencies beyond stdlib.

Usage:
    python memory_boot.py          # Print learnings + goals for context injection
    python memory_boot.py --full   # Also print observations and recent logs
    python memory_boot.py --save   # Write today's log entry (call after task)
"""

import os
import sys
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path(__file__).parent
LEARNINGS = MEMORY_DIR / "learnings.md"
GOALS = MEMORY_DIR / "goals.md"
OBSERVATIONS = MEMORY_DIR / "observations.md"
DAILY_LOGS = MEMORY_DIR / "data" / "daily-logs"


def read_file(path: Path) -> str:
    """Read file content, return empty string if missing."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def get_today_log() -> str:
    """Get or create today's daily log."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = DAILY_LOGS / f"{today}.md"
    if not log_path.exists():
        log_path.write_text(
            f"# Daily Log — {today}\n\n## Tasks\n\n## Errors\n\n## Corrections\n\n## Discoveries\n",
            encoding="utf-8",
        )
    return str(log_path)


def append_to_log(section: str, content: str):
    """Append an entry to today's daily log."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = DAILY_LOGS / f"{today}.md"
    if not log_path.exists():
        get_today_log()
    timestamp = datetime.now().strftime("%H:%M")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"- [{timestamp}] {content}\n")


def boot(full: bool = False) -> dict:
    """
    Boot the memory system. Returns dict with all loaded context.
    In Hermes Agent, this output gets injected into the system prompt.
    """
    learnings = read_file(LEARNINGS)
    goals = read_file(GOALS)
    observations = read_file(OBSERVATIONS) if full else ""

    # Get recent daily logs (last 3)
    recent_logs = []
    if full and DAILY_LOGS.exists():
        log_files = sorted(DAILY_LOGS.glob("*.md"), reverse=True)[:3]
        for lf in log_files:
            recent_logs.append(read_file(lf))

    # Ensure today's log exists
    today_log = get_today_log()

    return {
        "learnings": learnings,
        "goals": goals,
        "observations": observations,
        "recent_logs": recent_logs,
        "today_log": today_log,
        "boot_time": datetime.now().isoformat(),
    }


def format_for_context(boot_data: dict) -> str:
    """Format boot data for injection into LLM context."""
    parts = []

    if boot_data["learnings"].strip():
        parts.append("## What I've Learned (loaded at session start):\n" + boot_data["learnings"])

    if boot_data["goals"].strip():
        parts.append("## Active Goals:\n" + boot_data["goals"])

    if boot_data["observations"].strip():
        # Only last 10 observations
        lines = boot_data["observations"].strip().split("\n")
        recent = lines[-10:] if len(lines) > 10 else lines
        parts.append("## Recent Observations:\n" + "\n".join(recent))

    if boot_data["recent_logs"]:
        parts.append("## Recent Session Logs:\n" + "\n---\n".join(boot_data["recent_logs"][:2]))

    return "\n\n".join(parts)


def save_task(task: str, outcome: str, tags: list = None):
    """Save a completed task to today's log and update learnings if needed."""
    tag_str = ", ".join(tags) if tags else "general"
    append_to_log("Tasks", f"[{tag_str}] {task} → {outcome}")
    print(f"Task saved: {task} → {outcome}")


def save_error(error: str, fix: str):
    """Save an error and its fix."""
    append_to_log("Errors", f"ERROR: {error} → FIX: {fix}")
    print(f"Error saved: {error} → {fix}")


def save_correction(correction: str, context: str = ""):
    """Save a user correction."""
    entry = f"CORRECTION: {correction}"
    if context:
        entry += f" (context: {context})"
    append_to_log("Corrections", entry)
    print(f"Correction saved: {correction}")


def save_discovery(discovery: str):
    """Save a new discovery."""
    append_to_log("Discoveries", f"DISCOVERY: {discovery}")
    print(f"Discovery saved: {discovery}")


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--save" in args:
        # Interactive save mode
        idx = args.index("--save")
        task = args[idx + 1] if idx + 1 < len(args) else input("Task: ")
        outcome = args[idx + 2] if idx + 2 < len(args) else input("Outcome: ")
        save_task(task, outcome)
    elif "--error" in args:
        idx = args.index("--error")
        error = args[idx + 1] if idx + 1 < len(args) else input("Error: ")
        fix = args[idx + 2] if idx + 2 < len(args) else input("Fix: ")
        save_error(error, fix)
    elif "--correction" in args:
        idx = args.index("--correction")
        correction = args[idx + 1] if idx + 1 < len(args) else input("Correction: ")
        save_correction(correction)
    elif "--discovery" in args:
        idx = args.index("--discovery")
        discovery = args[idx + 1] if idx + 1 < len(args) else input("Discovery: ")
        save_discovery(discovery)
    else:
        # Default: boot and print context
        full = "--full" in args
        data = boot(full=full)
        print(format_for_context(data))
