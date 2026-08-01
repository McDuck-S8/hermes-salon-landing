#!/usr/bin/env python3
"""
Telegram Channel Monitor — Collect → Analyze → Report
Monitors channels, finds interesting content, generates reports with proposals.

Usage:
    python monitor.py --channels "ch1,ch2" --hours 24
    python monitor.py --config channels.json
    python monitor.py --preset ai_news

Output: cache/telegram_monitor/latest_report.md
"""

import os
import sys
import json
import asyncio
import argparse
from datetime import datetime, timedelta
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from telethon import TelegramClient
from telethon.errors import ChannelPrivateError, ChatAdminRequiredError

HERMES_HOME = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes'))
CACHE_DIR = HERMES_HOME / 'cache' / 'telegram_monitor'
SESSION_DIR = HERMES_HOME / 'sessions'
ENV_PATH = HERMES_HOME / '.env'

# Channel presets
PRESETS = {
    'ai_news': [
        'openai', 'GoogleAI', 'anthropic', 'deepseek',
        'hugging_face', 'nabormi_ai', 'peraboratory',
    ],
    'crypto': [
        'binance', 'coinbase', 'crypto', 'whale_alert',
    ],
    'tech_news': [
        'techcrunch', 'producthunt', 'news_ycombinator',
    ],
    'ru_news': [
        'rt_russian', 'tass_agency', 'rianovosti',
        'vcru', 'rbk_news',
    ],
    'all': [],  # will be filled from config
}


def load_env():
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())


def get_client(session_name='hermes_monitor'):
    load_env()
    api_id = os.environ.get('TELEGRAM_API_ID')
    api_hash = os.environ.get('TELEGRAM_API_HASH')
    if not api_id or not api_hash:
        print('ERROR: TELEGRAM_API_ID/HASH not set', file=sys.stderr)
        sys.exit(1)

    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    session_path = SESSION_DIR / session_name
    return TelegramClient(str(session_path), int(api_id), api_hash)


async def collect_channel(client, channel, hours):
    """Collect messages from a single channel."""
    result = {
        'url': f'https://t.me/{channel}',
        'messages': [],
        'error': None,
    }

    try:
        entity = await client.get_entity(channel)
        since = datetime.now() - timedelta(hours=hours)

        async for msg in client.iter_messages(entity, offset_date=since, reverse=True):
            if msg.text:
                result['messages'].append({
                    'id': msg.id,
                    'date': msg.date.isoformat(),
                    'text': msg.text[:3000],
                    'views': msg.views or 0,
                    'forwards': msg.forwards or 0,
                    'has_media': msg.media is not None,
                    'link': f'https://t.me/{channel}/{msg.id}',
                })

        result['total'] = len(result['messages'])

    except ChannelPrivateError:
        result['error'] = 'private_channel'
    except ChatAdminRequiredError:
        result['error'] = 'admin_required'
    except Exception as e:
        result['error'] = str(e)[:200]

    return result


async def collect_all(channels, hours, session_name='hermes_monitor'):
    """Collect from all channels."""
    client = get_client(session_name)
    await client.start()

    output = {
        'collected_at': datetime.now().isoformat(),
        'hours': hours,
        'channels': {},
        'total_messages': 0,
    }

    for ch in channels:
        ch = ch.strip()
        if not ch:
            continue
        print(f'  -> {ch}...', end=' ', flush=True)
        result = await collect_channel(client, ch, hours)
        output['channels'][ch] = result

        if result['error']:
            print(f'ERROR: {result["error"]}')
        else:
            n = result['total']
            print(f'{n} msgs')
            output['total_messages'] += n

    await client.disconnect()
    return output


def find_interesting(data):
    """Find interesting/standout messages across all channels."""
    interesting = []

    for ch_name, ch_data in data['channels'].items():
        if ch_data.get('error') or not ch_data.get('messages'):
            continue

        messages = ch_data['messages']
        avg_views = sum(m['views'] for m in messages) / max(len(messages), 1)

        for msg in messages:
            score = 0
            reasons = []

            # High views relative to channel average
            if avg_views > 0 and msg['views'] > avg_views * 2:
                score += 3
                reasons.append(f"views {msg['views']:,} (2x avg)")

            # Viral threshold
            if msg['views'] > 50000:
                score += 5
                reasons.append('viral (50k+)')
            elif msg['views'] > 10000:
                score += 3
                reasons.append('trending (10k+)')

            # High forwards = being shared
            if msg['forwards'] > 100:
                score += 3
                reasons.append(f"{msg['forwards']} forwards")

            # Keywords that signal importance
            text_lower = msg['text'].lower()
            hot_keywords = [
                'breaking', 'just launched', 'announcing', 'new release',
                'partnership', 'acquisition', 'funding', 'raised',
                'open source', 'free', 'limit', 'banned',
                'security', 'hack', 'vulnerability',
                'г鸟成长', 'запуск', 'партнёрство', 'покупка',
                'бесплатно', 'новый релиз', 'обновление',
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

    # Sort by score descending
    interesting.sort(key=lambda x: x['score'], reverse=True)
    return interesting[:20]  # top 20


def generate_report(data, interesting):
    """Generate markdown report."""
    lines = [
        f'# Telegram Monitor Report',
        f'**Date:** {data["collected_at"][:16]}',
        f'**Period:** {data["hours"]}h | **Messages:** {data["total_messages"]}',
        '',
    ]

    # Channel summary
    lines.append('## Channel Summary')
    lines.append('| Channel | Messages | Status |')
    lines.append('|---------|----------|--------|')
    for ch, ch_data in data['channels'].items():
        n = ch_data.get('total', 0)
        err = ch_data.get('error')
        status = f'ERROR: {err}' if err else f'{n} msgs'
        lines.append(f'| @{ch} | {n} | {status} |')
    lines.append('')

    # Interesting findings
    if interesting:
        lines.append('## Interesting Findings')
        lines.append('')

        for i, item in enumerate(interesting[:10], 1):
            msg = item['message']
            reasons = ', '.join(item['reasons'])
            text_preview = msg['text'][:200].replace('\n', ' ')

            lines.append(f'### {i}. @{item["channel"]} (score: {item["score"]})')
            lines.append(f'**Views:** {msg["views"]:,} | **Forwards:** {msg["forwards"]} | **Reasons:** {reasons}')
            lines.append(f'')
            lines.append(f'> {text_preview}...')
            lines.append(f'')
            lines.append(f'🔗 {msg["link"]}')
            lines.append('')
    else:
        lines.append('## Interesting Findings')
        lines.append('No standout messages found in this period.')
        lines.append('')

    # Proposals
    lines.append('## Proposals')
    lines.append('')

    if interesting:
        lines.append('Based on the analysis, here are suggested actions:')
        lines.append('')

        for item in interesting[:5]:
            msg = item['message']
            ch = item['channel']

            if msg['views'] > 10000:
                lines.append(f'- **High-impact post in @{ch}**: Consider resharing or commenting ({msg["views"]:,} views)')
            if msg['forwards'] > 50:
                lines.append(f'- **Viral content in @{ch}**: Worth analyzing what made it spread ({msg["forwards"]} forwards)')

            # Content-type proposals
            text = msg['text'].lower()
            if 'release' in text or 'launch' in text:
                lines.append(f'- **New release/launch in @{ch}**: Test or evaluate the announced product')
            if 'open source' in text:
                lines.append(f'- **Open source announcement in @{ch}**: Check repo, consider integration')
            if 'security' in text or 'hack' in text:
                lines.append(f'- **Security alert in @{ch}**: Review for personal/system impact')
    else:
        lines.append('- No high-signal content detected. Consider expanding channel list or adjusting thresholds.')
        lines.append('')

    lines.append('---')
    lines.append(f'*Generated by Hermes Telegram Monitor | {data["collected_at"][:19]}*')

    return '\n'.join(lines)


async def main():
    parser = argparse.ArgumentParser(description='Telegram Channel Monitor')
    parser.add_argument('--channels', help='Comma-separated channel usernames')
    parser.add_argument('--preset', choices=list(PRESETS.keys()), help='Channel preset')
    parser.add_argument('--config', help='JSON config file with channels list')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back')
    parser.add_argument('--session', default='hermes_monitor', help='Telethon session name')
    parser.add_argument('--output', help='Output report path (default: cache/telegram_monitor/latest_report.md)')
    parser.add_argument('--json', help='Save raw JSON')
    args = parser.parse_args()

    # Resolve channels
    channels = []
    if args.channels:
        channels = [c.strip() for c in args.channels.split(',') if c.strip()]
    elif args.preset:
        channels = PRESETS.get(args.preset, [])
    elif args.config:
        cfg = json.loads(Path(args.config).read_text())
        channels = cfg.get('channels', [])
    else:
        channels = PRESETS['ai_news']  # default

    if not channels:
        print('ERROR: No channels specified', file=sys.stderr)
        sys.exit(1)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    print(f'[{datetime.now():%H:%M:%S}] Monitoring {len(channels)} channels ({args.hours}h)...')

    data = await collect_all(channels, args.hours, args.session)

    # Save raw JSON
    json_path = args.json or str(CACHE_DIR / 'latest_raw.json')
    Path(json_path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'JSON saved: {json_path}')

    # Find interesting
    interesting = find_interesting(data)
    print(f'Found {len(interesting)} interesting messages')

    # Generate report
    report = generate_report(data, interesting)
    report_path = args.output or str(CACHE_DIR / 'latest_report.md')
    Path(report_path).write_text(report, encoding='utf-8')
    print(f'Report saved: {report_path}')

    # Also save interesting as JSON for further processing
    interesting_path = str(CACHE_DIR / 'latest_interesting.json')
    Path(interesting_path).write_text(json.dumps(interesting, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'\n[{datetime.now():%H:%M:%S}] Done! {data["total_messages"]} messages from {len(channels)} channels.')

    # Print report summary to stdout (for cron delivery)
    print('\n' + report)


if __name__ == '__main__':
    asyncio.run(main())
