#!/usr/bin/env python3
"""
Hermes Self-Improvement from Telegram Channels
Monitors AI channels AND learns from them for self-upgrade.

> Revisit: when self-improve from channels logic, Telegram monitoring, or channel processing changes. Last touched: 2026-07-02.
# Proxy configuration
proxy_handler = urllib.request.ProxyHandler({
    'http': 'http://127.0.0.1:10809',
    'https': 'http://127.0.0.1:10809'
})
opener = urllib.request.build_opener(proxy_handler)


Usage:
    python self_improve_from_channels.py
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes'))
CACHE_DIR = HERMES_HOME / 'cache' / 'telegram_monitor'
LEARNING_DIR = HERMES_HOME / 'cache' / 'self_learnings'
ENV_PATH = HERMES_HOME / '.env'

# Channels most relevant for Hermes upgrade
UPGRADE_CHANNELS = {
    'openai': {
        'focus': ['API changes', 'new models', 'tools', 'function calling', 'assistants'],
        'apply_to': ['hermes-agent', 'skills', 'cron jobs'],
    },
    'anthropic': {
        'focus': ['Claude updates', 'MCP', 'tool use', 'computer use'],
        'apply_to': ['hermes-agent', 'skills', 'browser tools'],
    },
    'deepseek': {
        'focus': ['open-source models', 'pricing', 'API endpoints'],
        'apply_to': ['model selection', 'cost optimization'],
    },
    'hugging_face': {
        'focus': ['new models', 'transformers updates', 'diffusers', 'tools'],
        'apply_to': ['skills', 'mlops', 'model integration'],
    },
    'GoogleAI': {
        'focus': ['Gemini', 'agents', 'multimodal', 'context window'],
        'apply_to': ['hermes-agent', 'browser tools', 'vision'],
    },
}


def load_env():
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env


def search_channel_news(channel, focus_topics):
    """Search for recent news from a channel."""
    query = f"{channel} AI news {' '.join(focus_topics[:2])} 2026"
    
    # Use web search via urllib (simplified)
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with opener.open(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        # Simple extraction - get titles and snippets
        import re
        results = []
        
        # Find result blocks
        title_pattern = re.compile(r'class="result__a"[^>]*>(.*?)</a>')
        snippet_pattern = re.compile(r'class="result__snippet">(.*?)</div>')
        
        titles = title_pattern.findall(html)
        snippets = snippet_pattern.findall(html)
        
        for i, (title, snippet) in enumerate(zip(titles[:5], snippets[:5])):
            title = re.sub(r'<[^>]+>', '', title).strip()
            snippet = re.sub(r'<[^>]+>', '', snippet).strip()
            if title:
                results.append({
                    'title': title,
                    'snippet': snippet[:200],
                    'channel': channel,
                })
        
        return results
    except Exception as e:
        return [{'error': str(e), 'channel': channel}]


def analyze_for_upgrade(search_results, channel_config):
    """Analyze search results for Hermes upgrade opportunities."""
    learnings = []
    
    for result in search_results:
        if 'error' in result:
            continue
        
        text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
        
        # Check for relevant keywords
        upgrade_signals = {
            'api': 'New API endpoint or change',
            'model': 'New model available',
            'tool': 'New tool or function',
            'agent': 'Agent capability update',
            'mcp': 'MCP protocol update',
            'function calling': 'Function calling improvement',
            'context': 'Context window change',
            'pricing': 'Cost change - optimize model selection',
            'open source': 'Open source - can integrate',
            'transformers': 'Library update - check compatibility',
            'security': 'Security update - may need action',
        }
        
        for keyword, meaning in upgrade_signals.items():
            if keyword in text:
                learnings.append({
                    'channel': result.get('channel', '?'),
                    'title': result.get('title', '')[:100],
                    'keyword': keyword,
                    'meaning': meaning,
                    'apply_to': channel_config.get('apply_to', []),
                    'timestamp': datetime.now().isoformat(),
                })
    
    return learnings


def save_learnings(learnings):
    """Save learnings to persistent file."""
    LEARNING_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load existing learnings
    learnings_file = LEARNING_DIR / 'upgrade_learnings.jsonl'
    existing = []
    if learnings_file.exists():
        existing = learnings_file.read_text(encoding='utf-8').strip().split('\n')
    
    # Append new learnings
    with open(learnings_file, 'a', encoding='utf-8') as f:
        for learning in learnings:
            f.write(json.dumps(learning, ensure_ascii=False) + '\n')
    
    return len(learnings)


def generate_upgrade_report(all_learnings):
    """Generate report of upgrade opportunities."""
    lines = [
        "# HERMES SELF-LEARN — Upgrade Opportunities",
        f"Date: {datetime.now().isoformat()[:16]}",
        "",
    ]
    
    if not all_learnings:
        lines.append("No new upgrade signals found.")
        return '\n'.join(lines)
    
    # Group by apply_to
    by_target = {}
    for l in all_learnings:
        for target in l.get('apply_to', ['unknown']):
            if target not in by_target:
                by_target[target] = []
            by_target[target].append(l)
    
    for target, items in by_target.items():
        lines.append(f"## {target}")
        for item in items[:3]:
            lines.append(f"- [{item['channel']}] {item['meaning']}")
            lines.append(f"  → {item['title'][:80]}")
        lines.append("")
    
    lines.append(f"Total: {len(all_learnings)} upgrade signals")
    return '\n'.join(lines)


def main():
    print(f"[{datetime.now():%H:%M:%S}] Self-improvement scan from channels...")
    
    all_learnings = []
    
    for channel, config in UPGRADE_CHANNELS.items():
        print(f"  -> {channel}...", end=' ', flush=True)
        results = search_channel_news(channel, config['focus'])
        learnings = analyze_for_upgrade(results, config)
        all_learnings.extend(learnings)
        print(f"{len(learnings)} signals")
    
    # Save learnings
    saved = save_learnings(all_learnings)
    print(f"\nSaved {saved} learnings to {LEARNING_DIR}")
    
    # Generate report
    report = generate_upgrade_report(all_learnings)
    report_path = CACHE_DIR / 'self_learn_report.md'
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding='utf-8')
    print(f"Report: {report_path}")
    
    print(f"\n[{datetime.now():%H:%M:%S}] Done! {len(all_learnings)} upgrade signals found.")
    print('\n' + report)


if __name__ == '__main__':
    main()
