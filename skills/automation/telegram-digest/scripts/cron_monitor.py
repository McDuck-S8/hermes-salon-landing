#!/usr/bin/env python3
"""
Telegram Monitor Cron Wrapper
Runs monitor.py and outputs report for cron delivery.
"""
import subprocess  # SAFE: subprocess.run with fixed args (SCRIPT path + known flags), no user input or shell=True
import sys
from pathlib import Path
from datetime import datetime

SCRIPT = Path(__file__).parent / 'monitor.py'
CACHE_DIR = Path(__file__).parent.parent.parent / 'cache' / 'telegram_monitor'

def main():
    # SAFE: subprocess.run with hardcoded SCRIPT path and known flags — no shell=True, no user-supplied args
    result = subprocess.run(
        [sys.executable, str(SCRIPT),
         '--config', str(CACHE_DIR / 'channels.json'),
         '--hours', '6',
         '--output', str(CACHE_DIR / 'latest_report.md'),
         '--json', str(CACHE_DIR / 'latest_raw.json')],
        capture_output=True,
        text=True,
        timeout=120,
    )

    report_path = CACHE_DIR / 'latest_report.md'

    if result.returncode != 0:
        # Check if it's auth error
        if 'session' in (result.stderr or '').lower() or 'NO_SESSION' in (result.stdout or ''):
            print('AUTH_REQUIRED: Run python skills/automation/telegram-digest/scripts/auth.py once')
            sys.exit(1)
        print(f'ERROR: Monitor failed\n{result.stderr[:500]}')
        sys.exit(1)

    # Read and output report
    if report_path.exists():
        report = report_path.read_text(encoding='utf-8')
        # Truncate if too long for cron delivery
        if len(report) > 4000:
            report = report[:4000] + '\n\n... [truncated, full report in cache/telegram_monitor/latest_report.md]'
        print(report)
    else:
        print('No report generated')


if __name__ == '__main__':
    main()
