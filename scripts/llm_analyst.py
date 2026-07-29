#!/usr/bin/env python3
"""
LLM Analyst — one-shot: check pending_analysis.json, call opencode.ai/zen, write suggested_fixes.json.
Designed for cron no_agent mode (runs once, exits).
"""
import json
import sys
import os
import random
import time
import requests as req
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict

sys.path.insert(0, str(Path(__file__).parent))
from prompt_compressor import compress_prompt

HERMES_HOME = Path(__file__).parent.parent
CACHE_DIR = HERMES_HOME / "cache"
PENDING_FILE = CACHE_DIR / "pending_analysis.json"
FIXES_FILE = CACHE_DIR / "suggested_fixes.json"

API_URL = "https://opencode.ai/zen/v1/chat/completions"
MAX_ISSUES = 5
TIMEOUT = 60

FREE_MODELS = [
    "mimo-v2.5-free",
    "deepseek-v4-flash-free",
    "nemotron-3-ultra-free",
    "qwen3.6-plus-free",
    "minimax-m3-free",
]


def load_pending():
    if not PENDING_FILE.exists():
        return None
    try:
        with open(PENDING_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data.get('issue_count', 0) == 0:
            return None
        return data
    except Exception:
        return None


def build_prompt(issues):
    p = 'You are fixing a Hermes AI agent system. Issues are either:\n'
    p += '  1) KNOWLEDGE GAPS — domains with few entries in the Knowledge Cube\n'
    p += '  2) CRON ERRORS — cron jobs that failed (script errors, timeouts, path issues)\n\n'
    p += 'For each issue, output a JSON array of fixes. Each fix is a dict:\n'
    p += '{\n'
    p += '  "fix_type": "command" | "investigation",\n'
    p += '  "description": "what this fix does",\n'
    p += '  "patch_or_action": "shell command to run",\n'
    p += '  "confidence": 0.0-1.0,\n'
    p += '  "target_file": "relevant file if any"\n'
    p += '}\n\n'
    p += 'AVAILABLE SCRIPTS (use these commands only):\n'
    p += '  python scripts/explore_domain.py <domain_name>\n'
    p += '  python scripts/knowledge_gap_filler.py --domain <domain_name>\n'
    p += '  python scripts/cube_feeder.py --domain <domain_name>\n'
    p += '  python scripts/explore_white_spot.py\n'
    p += '  python scripts/dimension_discovery.py\n'
    p += '  python scripts/auto_tagger_v2.py\n\n'
    p += 'RULES:\n'
    p += '- For KNOWLEDGE GAPS: fix_type="command", use explore_domain.py or knowledge_gap_filler.py\n'
    p += '- For CRON ERRORS like "Script not found": fix_type="investigation"\n'
    p += '  — the script path was fixed, suggest waiting for next cron cycle\n'
    p += '- NEVER generate placeholder content like "entry1, entry2"\n'
    p += '- NEVER suggest patching files that do not exist\n'
    p += '- NEVER suggest auto_recall.py or non-existent flags\n'
    p += '- Return ONLY valid JSON array, no markdown, no extra text\n\n'
    for i, issue in enumerate(issues[:MAX_ISSUES]):
        p += f'--- Issue {i+1} ---\n{json.dumps(issue, default=str)}\n'
    p += '\nReturn ONLY the JSON array.'
    return p


def call_api(prompt, model):
    compressed = compress_prompt(prompt, target_tokens=3000, rate=0.4)
    payload = {"model": model, "messages": [{"role": "user", "content": compressed}], "max_tokens": 2000, "temperature": 0.3}
    for attempt in range(3):
        try:
            r = req.post(API_URL, json=payload, timeout=TIMEOUT)
            if r.status_code == 200:
                msg = r.json().get("choices", [{}])[0].get("message", {})
                return msg.get("content") or msg.get("reasoning") or ""
            elif r.status_code == 429:
                time.sleep(2 + random.random() * 3)
            else:
                return None
        except Exception:
            return None
    return None


def extract_json_fixes(text):
    """Extract JSON fixes array from LLM response."""
    import re
    # Try to find a JSON array in the response
    json_match = re.search(r'\[[\s\S]*\]', text)
    if json_match:
        try:
            fixes = json.loads(json_match.group(0))
            if isinstance(fixes, list):
                return fixes
        except json.JSONDecodeError:
            pass
    # Try JSON object with fixes key
    obj_match = re.search(r'\{"fixes":[\s\S]*\}', text)
    if obj_match:
        try:
            data = json.loads(obj_match.group(0))
            if isinstance(data, dict) and "fixes" in data:
                return data["fixes"]
        except json.JSONDecodeError:
            pass
    return None


def main():
    pending = load_pending()
    if not pending:
        print("[llm-analyst] No pending analysis")
        return

    issues = pending.get('issues', [])
    if not issues:
        print("[llm-analyst] Empty issues")
        return

    print(f"[llm-analyst] Processing {len(issues)} issues")

    for model in FREE_MODELS:
        print(f"[llm-analyst] Trying {model}")
        response = call_api(build_prompt(issues), model)
        if response:
            fixes = extract_json_fixes(response)
            if fixes:
                data = {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "issues_analyzed": len(issues),
                    "fixes": fixes,
                    "model_used": model
                }
                tmp = FIXES_FILE.with_suffix('.tmp')
                with open(tmp, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
                tmp.replace(FIXES_FILE)
                print(f"[llm-analyst] Wrote {len(fixes)} fix suggestions from {model}")
                # Clear pending analysis
                try:
                    PENDING_FILE.unlink()
                except Exception:
                    pass
                return

    print("[llm-analyst] All models failed")


if __name__ == "__main__":
    main()
