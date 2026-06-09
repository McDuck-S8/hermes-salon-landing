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
    p = 'Analyze these code issues. Return ONLY a unified diff patch (--- a/ and +++ b/ format).\n'
    p += 'The patch must be a valid unified diff that can be applied with `git apply`.\n'
    p += 'If multiple fixes needed, combine them in one diff.\n\n'
    for i, issue in enumerate(issues[:MAX_ISSUES]):
        p += f'--- Issue {i+1} ---\n{json.dumps(issue, default=str)}\n'
    p += '\nReturn ONLY the unified diff, no markdown, no explanation.'
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


def extract_unified_diff(text):
    """Extract unified diff from LLM response."""
    # Look for unified diff markers
    if '--- a/' in text and '+++ b/' in text and '@@' in text:
        # Find the diff boundaries
        lines = text.split('\n')
        diff_lines = []
        in_diff = False
        for line in lines:
            if line.startswith('--- a/') or line.startswith('diff '):
                in_diff = True
            if in_diff:
                diff_lines.append(line)
        if diff_lines:
            return '\n'.join(diff_lines)
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
            diff = extract_unified_diff(response)
            if diff:
                data = {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "issues_analyzed": len(issues),
                    "patch": diff,
                    "model_used": model
                }
                tmp = FIXES_FILE.with_suffix('.tmp')
                with open(tmp, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
                tmp.replace(FIXES_FILE)
                print(f"[llm-analyst] Wrote unified diff from {model}")
                # Clear pending analysis
                try:
                    PENDING_FILE.unlink()
                except Exception:
                    pass
                return

    print("[llm-analyst] All models failed")


if __name__ == "__main__":
    main()
