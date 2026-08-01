#!/usr/bin/env python3
"""
Hermes Self-Improvement Loop
Runs after monitoring, learns from findings, updates skills.

> Revisit: when self-upgrade logic, upgrade safety, or version management changes. Last touched: 2026-07-02.

Workflow:
1. Read latest monitoring report
2. Extract upgrade signals
3. Update relevant skills/files
4. Log learnings

Usage:
    python hermes_self_upgrade.py
"""

import os
import json
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes'))
CACHE_DIR = HERMES_HOME / 'cache' / 'telegram_monitor'
LEARNINGS_DIR = HERMES_HOME / 'cache' / 'self_learnings'
SKILLS_DIR = HERMES_HOME / 'skills'

# What to learn from each type of news
LEARNING_RULES = {
    'new_model': {
        'check': ['model', 'release', 'launch', 'gpt', 'claude', 'gemini', 'llama'],
        'action': 'Add to model registry or update provider-model-management skill',
        'file': 'skills/mlops/provider-model-management/SKILL.md',
    },
    'api_change': {
        'check': ['api', 'endpoint', 'deprecated', 'migration'],
        'action': 'Update API integration skill',
        'file': 'skills/software-development/api-integration/SKILL.md',
    },
    'security': {
        'check': ['security', 'vulnerability', 'hack', 'patch', 'update'],
        'action': 'Check if we need to update dependencies',
        'file': 'skills/software-development/code-review/SKILL.md',
    },
    'new_tool': {
        'check': ['tool', 'library', 'framework', 'open source'],
        'action': 'Evaluate for integration',
        'file': 'skills/trend-scout/SKILL.md',
    },
    'pricing': {
        'check': ['price', 'cost', 'free', 'discount', 'cheap'],
        'action': 'Update cost optimization in model selection',
        'file': 'skills/mlops/provider-model-management/SKILL.md',
    },
}


def read_latest_report():
    """Read the latest monitoring report."""
    report_path = CACHE_DIR / 'latest_report.md'
    if not report_path.exists():
        return None
    return report_path.read_text(encoding='utf-8')


def extract_signals(report_text):
    """Extract upgrade signals from report text."""
    signals = []
    lines = report_text.split('\n')
    
    for line in lines:
        line_lower = line.lower()
        
        for signal_type, rules in LEARNING_RULES.items():
            for keyword in rules['check']:
                if keyword in line_lower:
                    signals.append({
                        'type': signal_type,
                        'line': line.strip()[:200],
                        'action': rules['action'],
                        'file': rules['file'],
                        'timestamp': datetime.now().isoformat(),
                    })
                    break  # One signal per line per type
    
    return signals


def save_signals(signals):
    """Save signals to learnings file."""
    LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
    learnings_file = LEARNINGS_DIR / 'upgrade_signals.jsonl'
    
    with open(learnings_file, 'a', encoding='utf-8') as f:
        for signal in signals:
            f.write(json.dumps(signal, ensure_ascii=False) + '\n')
    
    return len(signals)


def generate_actions(signals):
    """Generate concrete actions from signals."""
    actions = []
    
    # Group by file
    by_file = {}
    for s in signals:
        f = s.get('file', 'unknown')
        if f not in by_file:
            by_file[f] = []
        by_file[f].append(s)
    
    for file_path, file_signals in by_file.items():
        full_path = HERMES_HOME / file_path
        if full_path.exists():
            actions.append({
                'file': file_path,
                'signals_count': len(file_signals),
                'action': f"Review {file_path} for updates",
                'priority': 'high' if len(file_signals) > 2 else 'medium',
            })
    
    return actions


def main():
    print(f"[{datetime.now():%H:%M:%S}] Running self-upgrade loop...")
    
    # Read report
    report = read_latest_report()
    if not report:
        print("No report found. Run telegram-monitor first.")
        return
    
    print(f"Report loaded: {len(report)} chars")
    
    # Extract signals
    signals = extract_signals(report)
    print(f"Found {len(signals)} upgrade signals")
    
    # Save signals
    saved = save_signals(signals)
    print(f"Saved {saved} signals to learnings")
    
    # Generate actions
    actions = generate_actions(signals)
    print(f"\nActions needed:")
    for a in actions:
        print(f"  [{a['priority']}] {a['action']}")
        print(f"         File: {a['file']}")
        print(f"         Signals: {a['signals_count']}")
    
    # Save actions
    actions_file = CACHE_DIR / 'pending_actions.json'
    actions_file.write_text(json.dumps(actions, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nActions saved to: {actions_file}")
    
    print(f"\n[{datetime.now():%H:%M:%S}] Self-upgrade scan complete.")


if __name__ == '__main__':
    main()
