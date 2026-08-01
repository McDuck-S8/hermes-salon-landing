#!/usr/bin/env python3
"""
Action Feedback — bridges autonomous_agent with feedback_store.


> Revisit: when action feedback logic, feedback storage, or feedback evaluation changes. Last touched: 2026-07-02.
Records outcomes and provides weight-adjusted scoring.
This is the LEARNING LOOP: every action → outcome → weight → next decision.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from feedback_store import record_outcome as _record, compute_weight, save_weights


def record_outcome(action_id: str, success: bool, evidence: str = ""):
    """Record action outcome. Maps success/failure to outcome score."""
    outcome = 1.0 if success else -0.5
    _record(action_id, outcome, evidence=evidence)


def get_adjusted_score(action: dict, base_score: float) -> float:
    """Apply learned weight to base score."""
    action_id = action.get("id", "")
    if not action_id or action_id.startswith("goal-"):
        return base_score  # Goals don't have weights yet

    weight = compute_weight(action_id)
    return base_score * weight


def report_weights():
    """Print current weights."""
    from feedback_store import report
    report()


if __name__ == "__main__":
    report_weights()
