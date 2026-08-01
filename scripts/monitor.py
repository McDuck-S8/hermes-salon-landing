#!/usr/bin/env python3
"""
Telegram Bot API Monitor — Collect → Analyze → Report
Uses Bot API (HTTP) instead of MTProto (blocked in some regions).
# Proxy configuration
proxy_handler = urllib.request.ProxyHandler({
    'http': 'http://127.0.0.1:10809',
    'https': 'http://127.0.0.1:10809'
})
opener = urllib.request.build_opener(proxy_handler)


Usage:
    python bot_monitor.py --channels "channel1,channel2"
    python bot_monitor.py --preset ai_news
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import argparse
from datetime import datetime, timedelta
from pathlib import Path

HERMES_HOME = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes'))
CACHE_DIR = HERMES_HOME / 'cache' / 'telegram_monitor'
ENV_PATH = HERMES_HOME / '.env'

PRESETS = {
    'ai_news': ['openai', 'GoogleAI', 'anthropic', 'deepseek', 'hugging_face', 'nabormi_ai'],
    'crypto': ['binance', 'coinbase', 'crypto', 'whale_alert'],
    'ru_news': ['rt_russian', 'tass_agency', 'rianovosti', 'vcru', 'rbk_news'],
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


def bot_api(token, method, params=None):
    """Call Telegram Bot API."""
    url = f'https://api.telegram.org/bot{token}/{method}'
    if params:
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(url, data=data, method='POST')
    else:
        req = urllib.request.Request(url)

    try:
        with opener.open(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def get_updates(token, channel_username):
    """Try to get messages from channel via Bot API.
    Bot must be admin in the channel to read messages.
    For public channels, we can try getChat + getUpdates approach.
    """
    # First, try to get chat info
    chat_result = bot_api(token, 'getChat', {'chat_id': f'@{channel_username}'})
    if not chat_result.get('ok'):
        return {'error': chat_result.get('description', 'Cannot access chat')}

    return {'chat': chat_result.get('result', {})}


def search_messages_via_web(channel_username, limit=20):
    """Fallback: scrape public channel via t.me web preview."""
    url = f'https://t.me/s/{channel_username}'
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with opener.open(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')

        # Extract messages from HTML (simple regex)
        import re
        messages = []

        # Find message blocks
        msg_pattern = re.compile(
            r'<div class="tgme_widget_message_wrap[^"]*"[^>]*>.*?'
            r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>.*?'
            r'<div class="tgme_widget_message_views"[^>]*>([\d,KMk]*)</div>.*?'
            r'<a class="tgme_widget_message_date[^"]*" href="([^"]*)"[^>]*>',
            re.DOTALL
        )

        for match in msg_pattern.finditer(html):
            text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
            views_str = match.group(2).strip()
            link = match.group(3).strip()

            # Parse views
            views = 0
            if views_str:
                views_str = views_str.replace(',', '')
                if 'K' in views_str:
                    views = int(float(views_str.replace('K', '')) * 1000)
                elif 'M' in views_str:
                    views = int(float(views_str.replace('M', '')) * 1000000)
                else:
                    try:
                        views = int(views_str)
                    except ValueError:
                        views = 0

            if text:
                messages.append({
                    'text': text[:3000],
                    'views': views,
                    'link': f'https://t.me{link}' if link.startswith('/') else link,
                })

        return messages[:limit]

    except Exception as e:
        return []


def collect_from_channel(token, channel):
    """Collect messages from a channel using Bot API + web fallback."""
    result = {
        'url': f'https://t.me/{channel}',
        'messages': [],
        'error': None,
        'source': None,
    }

    # Method 1: Bot API (if bot is admin)
    bot_result = get_updates(token, channel)
    if bot_result.get('chat'):
        result['source'] = 'bot_api'
        # Bot API getUpdates only shows new messages, not history
        # For full history we need web scraping
        pass

    # Method 2: Web scraping (works for public channels)
    messages = search_messages_via_web(channel)
    if messages:
        result['messages'] = messages
        result['source'] = 'web'
        result['total'] = len(messages)
    elif bot_result.get('error'):
        result['error'] = bot_result['error']
    else:
        result['error'] = 'no_messages'

    return result


def find_interesting(data):
    """Find interesting/standout messages."""
    interesting = []

    for ch_name, ch_data in data['channels'].items():
        if ch_data.get('error') or not ch_data.get('messages'):
            continue

        messages = ch_data['messages']
        avg_views = sum(m.get('views', 0) for m in messages) / max(len(messages), 1)

        for msg in messages:
            score = 0
            reasons = []
            views = msg.get('views', 0)

            if avg_views > 0 and views > avg_views * 2:
                score += 3
                reasons.append(f"views {views:,} (2x avg)")

            if views > 50000:
                score += 5
                reasons.append('viral (50k+)')
            elif views > 10000:
                score += 3
                reasons.append('trending (10k+)')
            elif views > 5000:
                score += 2
                reasons.append('popular (5k+)')

            text_lower = msg.get('text', '').lower()
            hot_keywords = [
                'breaking', 'just launched', 'announcing', 'new release',
                'partnership', 'acquisition', 'funding', 'raised',
                'open source', 'free', 'banned', 'security', 'hack',
                'запуск', 'партнёрство', 'бесплатно', 'новый релиз',
                'обновление', 'обзор', 'сравнение', 'тест',
            ]
            for kw in hot_keywords:
                if kw in text_lower:
                    score += 1
                    reasons.append(f'keyword: {kw}')

            if score >= 3:
                interesting.append({
                    'channel': ch_name,
                    'message': msg,
                    'score': score,
                    'reasons': reasons,
                })

    interesting.sort(key=lambda x: x['score'], reverse=True)
    return interesting[:20]


def generate_report(data, interesting):
    """Generate markdown report."""
    lines = [
        f'# Telegram Monitor Report',
        f'**Date:** {data["collected_at"][:16]}',
        f'**Period:** {data["hours"]}h | **Messages:** {data["total_messages"]}',
        '',
    ]

    lines.append('## Channel Summary')
    lines.append('| Channel | Messages | Source | Status |')
    lines.append('|---------|----------|--------|--------|')
    for ch, ch_data in data['channels'].items():
        n = ch_data.get('total', 0)
        err = ch_data.get('error')
        src = ch_data.get('source', '?')
        status = f'ERROR: {err}' if err else 'OK'
        lines.append(f'| @{ch} | {n} | {src} | {status} |')
    lines.append('')

    if interesting:
        lines.append('## Interesting Findings')
        lines.append('')
        for i, item in enumerate(interesting[:10], 1):
            msg = item['message']
            reasons = ', '.join(item['reasons'])
            text_preview = msg.get('text', '')[:200].replace('\n', ' ')
            lines.append(f'### {i}. @{item["channel"]} (score: {item["score"]})')
            lines.append(f'**Views:** {msg.get("views", 0):,} | **Reasons:** {reasons}')
            lines.append(f'> {text_preview}...')
            lines.append(f'🔗 {msg.get("link", "")}')
            lines.append('')
    else:
        lines.append('## Interesting Findings')
        lines.append('No standout messages found.')
        lines.append('')

    lines.append('## Proposals')
    lines.append('')
    if interesting:
        for item in interesting[:5]:
            msg = item['message']
            ch = item['channel']
            views = msg.get('views', 0)
            text = msg.get('text', '').lower()
            if views > 10000:
                lines.append(f'- **@{ch}**: High-impact post ({views:,} views) — consider resharing')
            if 'release' in text or 'launch' in text:
                lines.append(f'- **@{ch}**: New launch detected — evaluate the product')
            if 'open source' in text:
                lines.append(f'- **@{ch}**: Open source — check repo')
    else:
        lines.append('- No high-signal content. Consider adding more channels.')

    lines.append('')
    lines.append('---')
    lines.append(f'*Generated by Hermes Telegram Monitor | {data["collected_at"][:19]}*')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Telegram Bot API Monitor')
    parser.add_argument('--channels', help='Comma-separated channel usernames')
    parser.add_argument('--preset', choices=list(PRESETS.keys()))
    parser.add_argument('--hours', type=int, default=24)
    parser.add_argument('--output', help='Output report path')
    args = parser.parse_args()

    env = load_env()
    token = env.get('TELEGRAM_BOT_TOKEN')
    if not token:
        print('ERROR: TELEGRAM_BOT_TOKEN not in .env', file=sys.stderr)
        sys.exit(1)

    channels = []
    if args.channels:
        channels = [c.strip() for c in args.channels.split(',') if c.strip()]
    elif args.preset:
        channels = PRESETS[args.preset]
    else:
        channels = PRESETS['ai_news']

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    print(f'[{datetime.now():%H:%M:%S}] Monitoring {len(channels)} channels via Bot API + web...')

    data = {
        'collected_at': datetime.now().isoformat(),
        'hours': args.hours,
        'channels': {},
        'total_messages': 0,
    }

    for ch in channels:
        print(f'  -> {ch}...', end=' ', flush=True)
        result = collect_from_channel(token, ch)
        data['channels'][ch] = result

        if result['error']:
            print(f'ERROR: {result["error"]}')
        else:
            n = result.get('total', 0)
            print(f'{n} msgs ({result.get("source", "?")})')
            data['total_messages'] += n

    # Save raw JSON
    json_path = str(CACHE_DIR / 'latest_raw.json')
    Path(json_path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    # Find interesting
    interesting = find_interesting(data)
    print(f'Found {len(interesting)} interesting messages')

    # Generate report
    report = generate_report(data, interesting)
    report_path = args.output or str(CACHE_DIR / 'latest_report.md')
    Path(report_path).write_text(report, encoding='utf-8')
    print(f'Report: {report_path}')

    # Save interesting
    interesting_path = str(CACHE_DIR / 'latest_interesting.json')
    Path(interesting_path).write_text(json.dumps(interesting, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'\n[{datetime.now():%H:%M:%S}] Done! {data["total_messages"]} messages.')
    print('\n' + report)


if __name__ == '__main__':
    main()
