#!/usr/bin/env python3
"""
Adaptive Event Classifier — the nervous system.


> Revisit: when event types, registry structure, or severity levels change. Last touched: 2026-07-02.
Not a lookup table. A classifier that:
1. Takes raw action/context as input
2. Classifies into event type + severity + chain
3. Returns ordered list of next actions (the chain)
4. Learns from outcomes which classifications worked

This is the BRAIN that event_bus.py lacked.
"""
import json
import time
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
CLASSIFIER_STATE = REPO_ROOT / "cache" / "classifier_state.json"
EVENT_LOG = REPO_ROOT / "cache" / "event_chains.jsonl"

# ─── CLASSIFICATION RULES (seed knowledge, grows over time) ───

# Each rule: (pattern_keywords, event_type, severity, chain_template)
# chain_template = list of action types to execute in order
# "→" means: each step checks if previous succeeded

SEED_RULES = [
    # === USER INTERACTION ===
    {
        "patterns": ["ну чего", "что делаем", "дальше", "продолжай"],
        "event_type": "user_frustration_idle",
        "severity": "high",
        "chain": ["check_pending_work", "execute_immediately", "report_concrete"],
        "learned": False,
    },
    {
        "patterns": ["пиздун", "чатбот", "ждешь пенделя"],
        "event_type": "user_distrust",
        "severity": "critical",
        "chain": ["stop_planning", "do_something_real", "verify_programmatic", "report_with_evidence"],
        "learned": False,
    },
    {
        "patterns": ["медитируй", "подумай", "что не так"],
        "event_type": "user_reflection_request",
        "severity": "medium",
        "chain": ["analyze_state", "find_root_cause", "propose_fix", "execute_fix"],
        "learned": False,
    },

    # === SYSTEM EVENTS ===
    {
        "patterns": ["error", "exception", "failed", "crash", "traceback"],
        "event_type": "error_logged",
        "severity": "high",
        "chain": ["diagnose_error", "attempt_fix", "verify_fix", "record_outcome"],
        "learned": False,
    },
    {
        "patterns": ["boot", "session_start", "startup"],
        "event_type": "boot_completed",
        "severity": "low",
        "chain": ["load_context", "check_health", "identify_next_action"],
        "learned": False,
    },
    {
        "patterns": ["goal", "задача", "цель", "задачу"],
        "event_type": "goal_updated",
        "severity": "medium",
        "chain": ["evaluate_progress", "check_completion_criteria", "advance_or_block"],
        "learned": False,
    },
    {
        "patterns": ["file_changed", "modified", "patch", "write_file"],
        "event_type": "file_changed",
        "severity": "low",
        "chain": ["verify_syntax", "check_impact"],
        "learned": False,
    },

    # === OUTPUT EVENTS ===
    {
        "patterns": ["success", "ok", "completed", "done", "работает"],
        "event_type": "action_completed",
        "severity": "low",
        "chain": ["verify_outcome_not_just_output", "record_to_manifest", "update_goal_progress"],
        "learned": False,
    },

    # === MEDITATION PATTERNS (from self-reflection) ===
    {
        "patterns": ["conscience", "совесть", "правда", "врёшь"],
        "event_type": "conscience_signal",
        "severity": "critical",
        "chain": ["stop_all_builds", "check_self_audit", "compare_claimed_vs_actual", "act_on_truth"],
        "learned": False,
    },
]


class AdaptiveClassifier:
    """
    Classifies raw input into typed events with severity and action chains.
    
    Learns from outcomes: when a chain succeeds, strengthen the rule.
    When it fails, weaken it. Over time, patterns that work survive.
    """

    def __init__(self):
        self.rules = list(SEED_RULES)
        self.history = []  # (event_type, chain, outcome, timestamp)
        self._load_state()

    def _load_state(self):
        if CLASSIFIER_STATE.exists():
            try:
                state = json.loads(CLASSIFIER_STATE.read_text(encoding="utf-8"))
                # Merge learned rules (don't overwrite seed rules)
                learned = state.get("learned_rules", [])
                existing_patterns = {
                    tuple(r["patterns"]) for r in self.rules
                }
                for lr in learned:
                    key = tuple(lr.get("patterns", []))
                    if key not in existing_patterns:
                        self.rules.append(lr)
                self.history = state.get("history", [])[-200:]
            except Exception:
                pass

    def save_state(self):
        learned = [r for r in self.rules if r.get("learned")]
        state = {
            "learned_rules": learned,
            "history": self.history[-200:],
            "total_rules": len(self.rules),
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        CLASSIFIER_STATE.parent.mkdir(parents=True, exist_ok=True)
        CLASSIFIER_STATE.write_text(
            json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def classify(self, text: str, context: Optional[dict] = None) -> dict:
        """
        Classify input text into an event with severity and chain.
        
        Returns:
            {
                "event_type": str,
                "severity": str (low/medium/high/critical),
                "chain": [str],  # ordered actions
                "matched_rule": int,  # index
                "confidence": float,  # 0.0-1.0
            }
        """
        text_lower = text.lower()
        context = context or {}

        best_match = None
        best_score = 0

        for i, rule in enumerate(self.rules):
            score = 0
            for pattern in rule["patterns"]:
                if pattern.lower() in text_lower:
                    # Longer patterns = more specific = higher score
                    score += len(pattern) / 10.0
                    # Exact match bonus
                    if pattern.lower() == text_lower.strip():
                        score += 1.0

            # Context boost: if context confirms the event type
            if context.get("is_error") and rule["event_type"] == "error_logged":
                score += 0.5
            if context.get("is_user_message") and "user" in rule["event_type"]:
                score += 0.3

            # History boost: rules that worked before
            past_successes = sum(
                1 for h in self.history
                if h[0] == rule["event_type"] and h[2] == "success"
            )
            score += past_successes * 0.1

            if score > best_score:
                best_score = score
                best_match = (i, rule)

        if best_match and best_score > 0:
            i, rule = best_match
            return {
                "event_type": rule["event_type"],
                "severity": rule["severity"],
                "chain": list(rule["chain"]),
                "matched_rule": i,
                "confidence": min(best_score / 2.0, 1.0),
            }

        # Default: unknown event
        return {
            "event_type": "unknown",
            "severity": "low",
            "chain": ["log_unknown", "investigate"],
            "matched_rule": -1,
            "confidence": 0.0,
        }

    def record_outcome(self, event_type: str, chain: list, outcome: str):
        """Record whether a classification+chain succeeded or failed.
        Auto-learn: if same event_type succeeds 3+ times with same chain,
        strengthen by recording a learned pattern from the input text."""
        self.history.append([
            event_type,
            chain,
            outcome,  # "success" or "failure"
            time.strftime("%Y-%m-%dT%H:%M:%S"),
        ])
        # Auto-learn: count successes for this event_type with same chain
        chain_key = tuple(chain)
        recent = [
            h for h in self.history[-50:]
            if h[0] == event_type and h[2] == "success" and tuple(h[1]) == chain_key
        ]
        if len(recent) >= 3:
            # Check if we already have a learned rule for this
            existing_chains = {
                tuple(r["chain"]) for r in self.rules if r.get("learned")
            }
            if chain_key not in existing_chains:
                # Extract the most common input texts that led to this
                input_texts = [h[1] for h in recent if isinstance(h[1], str)]
                patterns = list(set(input_texts))[:3] if input_texts else [event_type]
                self.learn_new_pattern(
                    patterns=patterns,
                    event_type=event_type,
                    severity="medium",
                    chain=chain,
                )
                print(f"  [LEARNED] New rule for {event_type} from {len(recent)} successes")
        self.save_state()

    def learn_new_pattern(self, patterns: list, event_type: str, 
                          severity: str, chain: list):
        """Add a new learned rule (from observation, not hardcoded)."""
        # Don't duplicate
        existing = {tuple(r["patterns"]) for r in self.rules}
        if tuple(patterns) not in existing:
            self.rules.append({
                "patterns": patterns,
                "event_type": event_type,
                "severity": severity,
                "chain": chain,
                "learned": True,
            })
            self.save_state()

    def get_stats(self) -> dict:
        return {
            "total_rules": len(self.rules),
            "seed_rules": sum(1 for r in self.rules if not r.get("learned")),
            "learned_rules": sum(1 for r in self.rules if r.get("learned")),
            "history_size": len(self.history),
            "recent_successes": sum(
                1 for h in self.history[-20:] if h[2] == "success"
            ),
            "recent_failures": sum(
                1 for h in self.history[-20:] if h[2] == "failure"
            ),
        }


def main():
    """CLI entry point for testing."""
    import sys
    classifier = AdaptiveClassifier()

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        result = classifier.classify(text)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # Show stats
        stats = classifier.get_stats()
        print(json.dumps(stats, indent=2))

        # Test with known patterns
        tests = [
            "ну чего стоим",
            "ты чатбот пиздун",
            "медитируй над собой",
            "ошибка в скрипте failed",
            "boot completed successfully",
            "сделал deposit на цель",
        ]
        print("\n--- CLASSIFICATION TESTS ---")
        for t in tests:
            r = classifier.classify(t)
            print(f"  \"{t}\"")
            print(f"    -> {r['event_type']} [{r['severity']}] conf={r['confidence']:.1f}")
            print(f"    chain: {' -> '.join(r['chain'])}")


if __name__ == "__main__":
    main()
