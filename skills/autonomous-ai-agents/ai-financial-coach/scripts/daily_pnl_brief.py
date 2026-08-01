#!/usr/bin/env python3
"""
Daily P&L Reconciliation Brief Generator
Used by cron job: ai-financial-coach + finance-core + arbitrage-sensors

Generates Telegram-formatted daily brief combining:
- finance_core ledger state (P&L, schemes, tax, withdrawals)
- arbitrage sensor gaps (top opportunities from gap_calculator)
- Scheme viability scoring (1-10) with SCALE/MAINTAIN/FIX/KILL tags
- Budget allocation recommendations per rules
"""

import json
import os
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))

# Import finance core
import sys
sys.path.insert(0, str(HERMES_HOME / "scripts"))
from scripts.finance_core import FinanceCore, get_finance_summary

# Import arbitrage sensors gap data
sys.path.insert(0, str(HERMES_HOME / "skills" / "finance" / "arbitrage-sensors" / "scripts"))
try:
    from gap_calculator import load_gaps_cache
except ImportError:
    load_gaps_cache = None

fc = FinanceCore()

def score_scheme(scheme):
    """Score scheme 1-10 on profitability sustainability."""
    roi = scheme.get('roi_pct', 0)
    spend = scheme.get('total_spend_usd', 0)
    revenue = scheme.get('total_revenue_usd', 0)
    status = scheme.get('status', 'testing')
    
    score = 5  # baseline
    if roi > 100 and revenue > 0:
        score += 3
    elif roi > 50 and revenue > 0:
        score += 2
    elif roi > 0 and revenue > 0:
        score += 1
    elif roi < 0:
        score -= 2
    if roi < -50:
        score -= 2
    if spend > 0 and revenue > 0:
        if spend < 100:
            score += 1
        elif spend > 1000:
            score -= 1
    if status == 'scaling':
        score += 1
    elif status == 'testing':
        score = min(score, 6)
    elif status == 'killed':
        score = 1
    return max(1, min(10, score))

def tag_scheme(scheme, score):
    """Return scale/maintain/kill tag."""
    roi = scheme.get('roi_pct', 0)
    spend = scheme.get('total_spend_usd', 0)
    if roi < 0 and spend >= 10:
        return "🔴 KILL"
    elif roi > 100 and spend > 0:
        return "🟢 SCALE"
    elif roi > 0:
        return "🟡 MAINTAIN"
    elif spend == 0:
        return "⚪ TEST"
    else:
        return "🟠 FIX"

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Finance core data
    summary = get_finance_summary()
    pnl = fc.get_pnl(30)
    schemes = fc.get_scheme_economics()
    tax = fc.get_tax_liability()
    withdrawals = fc.get_pending_withdrawals()
    
    # Balance (mock - would come from wallet in production)
    balance_usd = 1247
    daily_spend_30d = sum(s['total_spend_usd'] for s in schemes)
    days_runway = balance_usd / max(daily_spend_30d / 30, 1) if daily_spend_30d > 0 else 99999
    
    # Score schemes
    scored = []
    for s in schemes:
        sc = score_scheme(s)
        tag = tag_scheme(s, sc)
        s['viability_score'] = sc
        s['action_tag'] = tag
        scored.append(s)
    scored.sort(key=lambda x: x['viability_score'], reverse=True)
    
    # Budget allocation
    total_balance = balance_usd
    reserve_testing = total_balance * 0.20
    available = total_balance - reserve_testing
    
    recommendations = []
    for s in scored:
        name = s['scheme_name']
        roi = s['roi_pct']
        spend = s['total_spend_usd']
        tag = s['action_tag']
        
        if 'KILL' in tag:
            rec = "pause all traffic"
            alloc = 0
        elif 'SCALE' in tag:
            proposed = min(spend * 1.5, available * 0.5)
            alloc = round(proposed, 2)
            rec = f"increase to ${alloc}/day"
        elif 'MAINTAIN' in tag:
            alloc = round(spend, 2)
            rec = f"hold at ${alloc}/day"
        elif 'FIX' in tag:
            alloc = round(min(spend * 0.5, 50), 2)
            rec = f"reduce to ${alloc}/day + audit"
        else:
            alloc = 0
            rec = "no spend until validated"
        recommendations.append({
            'scheme': name, 'current_spend': round(spend, 2),
            'recommended_spend': alloc, 'roi': round(roi, 1),
            'tag': tag, 'action': rec
        })
    
    # Risk alerts
    alerts = []
    if days_runway < 7:
        alerts.append(f"⚠️ CASH FLOW CRUNCH: <7 days runway (${total_balance:.0f})")
    for s in schemes:
        if s['total_revenue_usd'] == 0 and s['total_spend_usd'] > 0:
            alerts.append(f"⚠️ {s['scheme_name']}: ${s['total_spend_usd']:.2f} spend, $0 revenue (ROI: {s['roi_pct']:.0f}%)")
    for w in withdrawals:
        if w.get('status') == 'pending':
            alerts.append(f"⚠️ Withdrawal pending: {w['network']} ${w['amount_usd']:.0f} via {w['withdrawal_method']}")
    if tax['pending_usd'] > 50:
        alerts.append(f"⚠️ Tax liability ${tax['pending_usd']:.0f} pending")
    
    # Top arbitrage gaps
    top_gaps = []
    if load_gaps_cache:
        gaps = load_gaps_cache()
        seen = set()
        for g in sorted(gaps, key=lambda x: x.get('projected_profit_per_day', 0), reverse=True):
            key = f"{g['offer']['network']}:{g['offer']['offer_id']}"
            if key not in seen:
                seen.add(key)
                top_gaps.append(g)
            if len(top_gaps) >= 5:
                break
    
    # Build output
    lines = [
        f"=== DAILY P&L === {today} ===",
        f"BALANCE: ${total_balance:,.0f} | {days_runway:.0f}-day runway",
        "",
        "ACTIVE SCHEMES:",
        "┌──────────────────┬────────┬────────┬────────┬──────┬────────┬────────────┐",
        "│ Scheme           │ Spend  │ Revenue│ Profit │ ROI  │ Status │ Action     │",
        "├──────────────────┼────────┼────────┼────────┼──────┼────────┼────────────┤"
    ]
    
    for s in scored:
        name = s['scheme_name'][:16]
        spend = f"${s['total_spend_usd']:>6.2f}"
        revenue = f"${s['total_revenue_usd']:>6.2f}"
        profit = f"${s['total_revenue_usd'] - s['total_spend_usd']:>+6.2f}"
        roi = f"{s['roi_pct']:>+5.0f}%"
        status = s.get('status', 'testing')[:6]
        action = s['action_tag']
        lines.append(f"│ {name:<16} │ {spend} │ {revenue} │ {profit} │ {roi} │ {status:<6} │ {action:<10} │")
    
    lines.append("└──────────────────┴────────┴────────┴────────┴──────┴────────┴────────────┘")
    
    if alerts:
        lines.append("")
        lines.append("ALERTS:")
        for a in alerts:
            lines.append(f"  {a}")
    
    if top_gaps:
        lines.append("")
        lines.append("TOP NEW OPPORTUNITIES (from arbitrage sensors):")
        for g in top_gaps[:3]:
            o = g['offer']
            t = g['traffic']
            lines.append(f"  • {o['name'][:30]} ({o['network']}) + {t['source']} → ROI {g['roi']:.0f}% | ${g['projected_profit_per_day']:.0f}/day")
    
    lines.append("")
    lines.append("RECOMMENDATION:")
    total_rec = sum(r['recommended_spend'] for r in recommendations)
    lines.append(f"  Reallocate ${total_rec:.0f}/day across active schemes")
    lines.append(f"  Reserve ${reserve_testing:.0f} for testing new offers")
    lines.append("")
    lines.append("NEXT REVIEW: 07:00 tomorrow")
    
    output = "\n".join(lines)
    print(output)
    
    # Save to outputs/finance/
    out_dir = Path(__file__).parent.parent.parent.parent / "outputs" / "finance"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"daily_pnl_{today}.txt"
    out_file.write_text(output, encoding="utf-8")
    print(f"\n[Saved to {out_file}]")

if __name__ == "__main__":
    main()