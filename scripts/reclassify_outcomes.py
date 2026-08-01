#!/usr/bin/env python3
"""
Reclassify Knowledge Cube outcomes based on verified data, not just keywords.

Rules:
- success: verified outcome > 0, or explicit "done/completed/fixed/resolved" with result
- partial: progress made, started, attempt, but no verification
- failure: actual crash/error/exception/traceback
- unknown: can't determine (default for ambiguous)
"""

import sqlite3
import json
import re
from pathlib import Path

HERMES_HOME = Path(__file__).resolve().parent.parent
DB_PATH = HERMES_HOME / "cache" / "knowledge_cube.db"

def classify_outcome_v2(text: str, source: str = "", tags: str = "[]") -> str:
    """Improved outcome classification using context."""
    t = (text or "").lower()
    src = (source or "").lower()
    
    # Parse tags for additional context
    try:
        tag_list = json.loads(tags) if tags else []
    except:
        tag_list = []
    
    # Strong success indicators (verified results)
    success_patterns = [
        r"successfully\s+(completed|finished|fixed|resolved|deployed|published|created|built|tested)",
        r"(completed|finished|done|resolved|fixed)\s+(and|with)\s+(result|output|verified|confirmed)",
        r"outcome\s*[>:]\s*\d+",  # outcome > 0
        r"verified.*true",
        r"deployed\s+to\s+(production|staging|server)",
        r"published\s+to\s+(github|pypi|npm|docker)",
        r"tests?\s+passed",
        r"all\s+checks?\s+passed",
        r"build\s+successful",
        r"merged\s+to\s+(main|master)",
        r"released\s+v?\d+\.\d+",
    ]
    
    for pattern in success_patterns:
        if re.search(pattern, t):
            return "success"
    
    # Strong failure indicators (actual crashes/errors)
    failure_patterns = [
        r"traceback\s*\(most recent call last\)",
        r"(exception|error):\s*\w+error",
        r"segmentation fault",
        r"out of memory",
        r"connection refused",
        r"timeout\s+after",
        r"failed\s+to\s+(connect|execute|load|parse|import)",
        r"module not found",
        r"import error",
        r"syntax error",
        r"permission denied",
        r"disk full",
        r"killed\s+signal",
        r"exit code\s+[1-9]",
        r"assertionerror",
        r"valueerror",
        r"keyerror",
        r"typeerror",
        r"attributeerror",
        r"filenotfounderror",
    ]
    
    for pattern in failure_patterns:
        if re.search(pattern, t):
            return "failure"
    
    # Partial/progress indicators
    partial_patterns = [
        r"(started|begin|beginning|in progress|working on|attempting|trying)\b",
        r"progress[:\s]+\d+%",
        r"step\s+\d+\s+(of|/)\s+\d+",
        r"partial\s+(result|success|completion)",
        r"pending\s+(review|approval|verification)",
        r"waiting\s+for",
        r"in\s+queue",
        r"scheduled\s+for",
    ]
    
    for pattern in partial_patterns:
        if re.search(pattern, t):
            return "partial"
    
    # Source-based heuristics
    if "agent_decisions" in src or "decision" in src:
        # Decisions are usually successful if they have a result
        if any(w in t for w in ["result", "applied", "implemented", "created", "updated"]):
            return "success"
    
    if "lavra_" in src:
        # Lavra items are usually decisions/learnings - check content
        if any(w in t for w in ["learned", "decision", "pattern", "fact", "investigation"]):
            # These are knowledge captures, not failures
            return "success"
    
    if "signal" in src:
        return "success"  # Signals are just data
    
    if "agent" in src or "cron" in src or "job" in src:
        # System actions - look for explicit results
        if any(w in t for w in ["completed", "ok", "passed", "healthy"]):
            return "success"
        if any(w in t for w in ["error", "failed", "crash", "timeout"]):
            return "failure"
    
    # Tags-based
    if "tool:terminal" in tag_list or "tool:execute_code" in tag_list:
        # Code execution - check for error patterns
        if re.search(r"(error|exception|traceback|failed)", t):
            return "failure"
        if re.search(r"(completed|done|success|ok)$", t.strip()):
            return "success"
    
    # Default: unknown for ambiguous
    return "unknown"


def reclassify():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # Get all experiences
    rows = conn.execute("SELECT id, raw_text, source, tags, axis_outcome FROM experiences").fetchall()
    
    stats = {"success": 0, "partial": 0, "failure": 0, "unknown": 0}
    changes = 0
    
    for row in rows:
        new_outcome = classify_outcome_v2(row["raw_text"], row["source"], row["tags"])
        old_outcome = row["axis_outcome"]
        
        if new_outcome != old_outcome:
            conn.execute(
                "UPDATE experiences SET axis_outcome = ? WHERE id = ?",
                (new_outcome, row["id"])
            )
            changes += 1
        
        stats[new_outcome] = stats.get(new_outcome, 0) + 1
    
    conn.commit()
    conn.close()
    
    print(f"Reclassified: {changes} changes")
    print(f"New distribution:")
    for k, v in stats.items():
        print(f"  {k}: {v} ({v/len(rows)*100:.1f}%)")
    
    return stats


if __name__ == "__main__":
    reclassify()