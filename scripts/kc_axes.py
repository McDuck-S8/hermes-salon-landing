#!/usr/bin/env python3
"""
kc_axes.py — The 8 angles of the Knowledge Cube.

Every experience in KC should have structured dynamic_axes with these 8 fields.
This replaces the chaotic {} that was there before.

The 8 angles answer:
  1. essence    — What is this? (category)
  2. origin     — Where did it come from? (structured source)
  3. temporal   — When in the work cycle? (context)
  4. confidence — How sure are we? (verification level)
  5. value      — How important for the user? (business value)
  6. applicability — When can this be used? (actionability)
  7. action     — What should happen next? (next step)
  8. related    — What else connects to this? (links)
"""
import json
from datetime import datetime

# ── Schema constants ──────────────────────────────────────────────

ESSENCE_VALUES = {
    "error_fix",        # A fix for a specific error
    "pattern",          # A recurring pattern observed
    "user_feedback",    # Direct user message (correction, frustration, praise)
    "research",         # External knowledge (RSS, web, video)
    "skill_usage",      # A skill was used successfully
    "skill_failure",    # A skill failed or was insufficient
    "architecture",     # System design observation
    "metric",           # Quantitative measurement
    "decision",         # A decision was made and why
    "lesson",           # Something learned from experience
}

CONFIDENCE_VALUES = {
    "verified",         # Fix confirmed working (user said OK or test passed)
    "pattern",          # Recurring 3+ times (statistical)
    "observed",         # Seen once, not confirmed
    "speculated",       # Inferred, not directly observed
    "user_confirmed",   # User explicitly confirmed this is correct
}

VALUE_VALUES = {
    "critical",         # Blocks all work if not addressed
    "high",             # Directly improves output quality or speed
    "medium",           # Nice to have, incremental improvement
    "low",              # Cosmetic or theoretical
    "noise",            # Should be filtered out
}

APPLICABILITY_VALUES = {
    "now",              # Can apply immediately, no blockers
    "needs_context",    # Requires specific conditions to apply
    "reference",        # Informational only, no direct action
    "future",           # Will be useful later, not now
    "expired",          # No longer relevant
}

ACTION_VALUES = {
    "apply_fix",        # Apply a concrete fix
    "create_skill",     # Persist as reusable skill
    "update_doc",       # Update documentation
    "investigate",      # Needs more research
    "alert_user",       # User should see this
    "ignore",           # Not worth acting on
    "record_only",      # Store for future reference
}


# ── Builder ───────────────────────────────────────────────────────

def build_axes(
    essence: str = "pattern",
    origin: str = "unknown",
    temporal: str = "post_session",
    confidence: str = "observed",
    value: str = "medium",
    applicability: str = "reference",
    action: str = "record_only",
    related: list = None,
    extra: dict = None,
) -> dict:
    """
    Build a structured dynamic_axes dict with the 8 angles.

    Usage:
        axes = build_axes(
            essence="error_fix",
            origin="self_improvement_loop",
            confidence="pattern",
            value="high",
            action="apply_fix",
        )
        # Write to KC: json.dumps(axes)
    """
    axes = {
        "essence": essence if essence in ESSENCE_VALUES else "pattern",
        "origin": origin,
        "temporal": temporal,
        "confidence": confidence if confidence in CONFIDENCE_VALUES else "observed",
        "value": value if value in VALUE_VALUES else "medium",
        "applicability": applicability if applicability in APPLICABILITY_VALUES else "reference",
        "action": action if action in ACTION_VALUES else "record_only",
        "related": related or [],
    }
    if extra:
        axes["_extra"] = extra
    return axes


# ── Classification helpers ────────────────────────────────────────

def classify_essence(text: str, source: str = "") -> str:
    """Auto-classify essence from text content and source."""
    t = text.lower()
    # user_feedback: explicit user reactions
    if any(w in t for w in ["user said", "user command", "user correct", "user frust", "this is garbage", "это говно"]):
        return "user_feedback"
    if source == "user_voice" or source == "user_correction":
        return "user_feedback"
    # error_fix: concrete fixes
    if any(w in t for w in ["error", "fix", "broke", "crash", "traceback", "exception"]):
        return "error_fix"
    if any(w in t for w in ["appeared", "recurring", "cluster"]):
        return "pattern"
    if any(w in t for w in ["rss", "video", "article", "paper", "research"]):
        return "research"
    if any(w in t for w in ["skill", "created", "applied"]):
        return "skill_usage"
    if any(w in t for w in ["learned", "lesson", "discovered", "realized"]):
        return "lesson"
    if any(w in t for w in ["architecture", "singleton", "connection", "schema"]):
        return "architecture"
    if any(w in t for w in ["metric", "conversion", "count", "ratio"]):
        return "metric"
    if any(w in t for w in ["decision", "chose", "decided", "reason"]):
        return "decision"
    if any(w in t for w in ["learned", "lesson", "discovered", "realized"]):
        return "lesson"
    if any(w in t for w in ["pattern", "times"]):
        return "pattern"
    return "pattern"


def classify_confidence(text: str, count: int = 1) -> str:
    """Auto-classify confidence from recurrence count and content."""
    if count >= 5:
        return "verified"
    if count >= 3:
        return "pattern"
    if count >= 2:
        return "observed"
    return "speculated"


def classify_value(text: str, source: str = "") -> str:
    """Auto-classify value for user."""
    t = text.lower()
    if any(w in t for w in ["blocks", "critical", "urgent", "all work"]):
        return "critical"
    if any(w in t for w in ["improves", "faster", "quality", "important"]):
        return "high"
    if any(w in t for w in ["pattern", "observed", "appeared"]):
        return "medium"
    if any(w in t for w in ["theoretical", "cosmetic", "minor"]):
        return "low"
    return "medium"


def classify_applicability(text: str) -> str:
    """Auto-classify when this can be used."""
    t = text.lower()
    if any(w in t for w in ["apply", "fix", "now", "immediately"]):
        return "now"
    if any(w in t for w in ["if", "when", "condition", "needs"]):
        return "needs_context"
    if any(w in t for w in ["reference", "info", "note", "fyi"]):
        return "reference"
    if any(w in t for w in ["future", "later", "eventually"]):
        return "future"
    return "reference"


def classify_action(text: str) -> str:
    """Auto-classify what should happen next."""
    t = text.lower()
    if any(w in t for w in ["fix", "patch", "apply", "change"]):
        return "apply_fix"
    if any(w in t for w in ["skill", "persist", "save", "reusable"]):
        return "create_skill"
    if any(w in t for w in ["doc", "document", "readme", "update"]):
        return "update_doc"
    if any(w in t for w in ["investigate", "research", "find out"]):
        return "investigate"
    if any(w in t for w in ["alert", "notify", "user should"]):
        return "alert_user"
    if any(w in t for w in ["ignore", "skip", "noise"]):
        return "ignore"
    return "record_only"


def auto_build_axes(text: str, source: str = "", count: int = 1) -> dict:
    """
    Build axes automatically from text content.
    Best-effort classification — not perfect, but structured.
    """
    return build_axes(
        essence=classify_essence(text, source),
        origin=source or "unknown",
        temporal="post_session",
        confidence=classify_confidence(text, count),
        value=classify_value(text, source),
        applicability=classify_applicability(text),
        action=classify_action(text),
    )


# ── Backfill helper ───────────────────────────────────────────────

def backfill_axes(text: str, source: str, existing_axes: dict = None) -> dict:
    """
    Merge new 8-angle axes into existing dynamic_axes.
    Preserves existing fields, fills missing ones.
    """
    existing = existing_axes or {}
    new_axes = auto_build_axes(text, source)

    # Don't overwrite fields that already have meaningful values
    for key in ["essence", "origin", "temporal", "confidence", "value", "applicability", "action", "related"]:
        if key in existing and existing[key] and existing[key] != "unknown":
            new_axes[key] = existing[key]

    # Preserve _extra from old data
    if "_extra" in existing:
        new_axes["_extra"] = existing["_extra"]

    return new_axes


# ── Validation ────────────────────────────────────────────────────

def validate_axes(axes: dict) -> list:
    """Return list of validation errors. Empty = valid."""
    errors = []
    if axes.get("essence") not in ESSENCE_VALUES:
        errors.append(f"invalid essence: {axes.get('essence')}")
    if axes.get("confidence") not in CONFIDENCE_VALUES:
        errors.append(f"invalid confidence: {axes.get('confidence')}")
    if axes.get("value") not in VALUE_VALUES:
        errors.append(f"invalid value: {axes.get('value')}")
    if axes.get("applicability") not in APPLICABILITY_VALUES:
        errors.append(f"invalid applicability: {axes.get('applicability')}")
    if axes.get("action") not in ACTION_VALUES:
        errors.append(f"invalid action: {axes.get('action')}")
    return errors


if __name__ == "__main__":
    # Demo
    sample = "Self-improvement pattern: 'command' appeared 15 times. Latest fix: patch knowledge_cube.py"
    axes = auto_build_axes(sample, source="self_improvement_loop", count=15)
    print(json.dumps(axes, indent=2))
    print(f"Validation: {validate_axes(axes)}")
