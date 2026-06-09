#!/usr/bin/env python3
"""
Knowledge Gap Filler — one-shot: find gaps in Knowledge Cube, generate
knowledge entries via LLM, write back to KC.

Designed for cron no_agent mode (runs once, exits).

Flow:
  1. Read white spots + pending clusters from KC
  2. Pick top N gaps
  3. For each gap, ask LLM to generate a concise knowledge entry
  4. Write generated entries back to KC as experiences
  5. Update white_spot_clusters status to 'filled'
"""

import json
import os
import random
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

import requests as req

# ── Paths ────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
HERMES_HOME = SCRIPT_DIR.parent
CACHE_DIR = HERMES_HOME / "cache"
DB_PATH = CACHE_DIR / "knowledge_cube.db"
FIXES_LOG = CACHE_DIR / "gap_fills.json"

sys.path.insert(0, str(SCRIPT_DIR))
import knowledge_cube as kc

# ── LLM Config ───────────────────────────────────────────────────────────────

API_URL = "https://opencode.ai/zen/v1/chat/completions"
TIMEOUT = 60
MAX_GAPS = 5
FREE_MODELS = [
    "deepseek-v4-flash-free",
    "mimo-v2.5-free",
    "nemotron-3-ultra-free",
]
API_KEY = os.environ.get("OPENCODE_ZEN_KEY", "")

# ── Helpers ──────────────────────────────────────────────────────────────────

def pick_model():
    return random.choice(FREE_MODELS)


def call_llm(prompt, model):
    """Call OpenCode Zen API, return text or None."""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500,
        "temperature": 0.5,
    }
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    for attempt in range(3):
        try:
            r = req.post(API_URL, json=payload, headers=headers, timeout=TIMEOUT)
            if r.status_code == 200:
                msg = r.json().get("choices", [{}])[0].get("message", {})
                return msg.get("content") or msg.get("reasoning_content") or msg.get("reasoning") or ""
            elif r.status_code == 429:
                time.sleep(2 + random.random() * 3)
            else:
                return None
        except Exception:
            time.sleep(1)
    return None


def build_gap_prompt(domain, cluster_text, outcome="unknown"):
    """Build a prompt asking LLM to generate a knowledge entry for this gap."""
    return (
        f"Generate a concise knowledge entry for the domain '{domain}'.\n"
        f"This is a known gap (white spot) in an AI agent's Knowledge Cube.\n"
        f"Context from related session:\n{cluster_text[:600]}\n\n"
        f"Return a single JSON object (no markdown, no code fences) with:\n"
        f'  "domain": "{domain}",\n'
        f'  "outcome": "success",\n'
        f'  "content": "<2-4 sentence actionable knowledge summary>",\n'
        f'  "tags": ["<tag1>", "<tag2>"]\n\n'
        f"Keep it practical and specific to AI agent operations."
    )


def parse_llm_response(text):
    """Try to extract JSON from LLM response."""
    if not text:
        return None
    # Strip markdown fences if present
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[-1]
        if t.endswith("```"):
            t = t[:-3]
        t = t.strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        # Try to find JSON object in text
        start = t.find("{")
        end = t.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(t[start:end])
            except json.JSONDecodeError:
                pass
    return None


# ── Main ─────────────────────────────────────────────────────────────────────

def find_gaps():
    """Find white spots and pending clusters."""
    conn = kc.get_db()
    gaps = []

    # 1. White spot experiences
    rows = conn.execute(
        "SELECT axis_domain, COUNT(*) as cnt FROM experiences "
        "WHERE is_white_spot = 1 GROUP BY axis_domain"
    ).fetchall()
    for row in rows:
        gaps.append({
            "type": "white_spot",
            "domain": row["axis_domain"],
            "count": row["cnt"],
            "text": f"White spot in domain '{row['axis_domain']}' with {row['cnt']} experiences",
        })

    # 2. Pending clusters
    clusters = conn.execute(
        "SELECT cluster_id, size, representative_text, proposed_dimension "
        "FROM white_spot_clusters WHERE status = 'pending' ORDER BY size DESC LIMIT ?",
        (MAX_GAPS * 2,),
    ).fetchall()
    for cl in clusters:
        # Classify domain from representative text
        domain = kc.classify_domain(cl["representative_text"] or "")
        gaps.append({
            "type": "pending_cluster",
            "cluster_id": cl["cluster_id"],
            "domain": domain,
            "count": cl["size"],
            "text": cl["representative_text"] or "",
        })

    # 3. Underpopulated domains (< 5 experiences)
    all_domains = conn.execute(
        "SELECT axis_domain, COUNT(*) as cnt FROM experiences "
        "GROUP BY axis_domain ORDER BY cnt ASC"
    ).fetchall()
    for row in all_domains:
        if row["cnt"] < 5 and row["axis_domain"] not in ("uncategorized", None):
            gaps.append({
                "type": "underpopulated",
                "domain": row["axis_domain"],
                "count": row["cnt"],
                "text": f"Domain '{row['axis_domain']}' has only {row['cnt']} experiences — critically low",
            })

    conn.close()
    return gaps


def fill_gap(gap):
    """Generate a knowledge entry for one gap via LLM."""
    model = pick_model()
    prompt = build_gap_prompt(gap["domain"], gap["text"], "unknown")
    response = call_llm(prompt, model)
    entry = parse_llm_response(response)

    if not entry or "content" not in entry:
        return None

    # Ensure required fields
    entry.setdefault("domain", gap["domain"])
    entry.setdefault("outcome", "success")
    entry.setdefault("tags", ["gap-filled", gap["domain"]])

    return entry


def write_to_kc(entry):
    """Write a generated knowledge entry back to Knowledge Cube."""
    text = entry.get("content", "")
    if not text or len(text) < 10:
        return False

    domain = entry.get("domain", "uncategorized")
    outcome = entry.get("outcome", "success")
    tags = entry.get("tags", [])

    try:
        kc.add_experience(
            text=text,
            tools=[],
            source="gap_filler",
            dynamic_axes={"domain": domain, "outcome": outcome},
        )
        return True
    except Exception as e:
        print(f"  [WARN] Failed to write: {e}")
        return False


def mark_cluster_filled(cluster_id):
    """Mark a pending cluster as filled."""
    conn = kc.get_db()
    conn.execute(
        "UPDATE white_spot_clusters SET status = 'filled' WHERE cluster_id = ?",
        (cluster_id,),
    )
    conn.commit()
    conn.close()


def main():
    print(f"[GapFiller] {datetime.now().isoformat()} — starting")
    gaps = find_gaps()

    if not gaps:
        print("[GapFiller] No gaps found. All clear.")
        return

    # Prioritize: white spots first, then clusters, then underpopulated
    priority = {"white_spot": 0, "pending_cluster": 1, "underpopulated": 2}
    gaps.sort(key=lambda g: priority.get(g["type"], 9))
    gaps = gaps[:MAX_GAPS]

    print(f"[GapFiller] Processing {len(gaps)} gaps")
    filled = 0
    results = []

    for i, gap in enumerate(gaps):
        print(f"  [{i+1}/{len(gaps)}] {gap['type']}: {gap['domain']} "
              f"(count={gap['count']}, cluster={gap.get('cluster_id', '-')})")

        entry = fill_gap(gap)
        if not entry:
            print(f"    -> LLM returned nothing, skipping")
            continue

        success = write_to_kc(entry)
        if success:
            filled += 1
            print(f"    -> OK: {entry['content'][:80]}...")
            if gap.get("cluster_id"):
                mark_cluster_filled(gap["cluster_id"])
            results.append({
                "gap": gap,
                "entry": entry,
                "filled_at": datetime.now(timezone.utc).isoformat(),
            })
        else:
            print(f"    -> Write failed")

    # Log results
    FIXES_LOG.parent.mkdir(parents=True, exist_ok=True)
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gaps_found": len(gaps),
        "filled": filled,
        "results": results,
    }
    with open(FIXES_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, default=str) + "\n")

    print(f"[GapFiller] Done: {filled}/{len(gaps)} gaps filled")


if __name__ == "__main__":
    main()
