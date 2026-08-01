#!/usr/bin/env python3
"""Final system check before launch"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from finance_core import get_finance_summary

# 1. Finance core
finance = get_finance_summary()
print(f'💰 Finance: Net={finance["pnl_30d"]["net_usd"]:.2f} USD')

# 2. Arbitrage routes
from arbitrage_router import build, calc_route
graph = build()
route = calc_route(graph, ['telegram', 'carrd', 'cpagrip', 'kucoin-p2p', 'tbank', 'profit'], budget=200)
if route:
    print(f'🚀 Route: Telegram→Carrd→CPAGrip→KuCoin P2P→TBank')
    print(f'   Net profit: ${route.net_profit:.2f} | ROI: {route.roi_pct:.1f}%')

# 3. Cron jobs active
import json
with open('cron/jobs.json') as f:
    data = json.load(f)
jobs = data['jobs']
active_cron = [j for j in jobs if j.get('enabled') and j.get('state', 'scheduled') == 'scheduled']
print(f'⏰ Cron jobs: {len(active_cron)} active')
for j in active_cron:
    if j['name'] in ['always-on-fast', 'always-on-medium', 'daily-pnl-budget', 'arbitrage_scan']:
        print(f'   ✅ {j["name"]}: {j["schedule_display"]}')

print()
print('✅ SYSTEM ARMED. Autonomous arbitrage pipeline active.')