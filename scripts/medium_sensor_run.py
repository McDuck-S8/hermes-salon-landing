#!/usr/bin/env python3
"""
MEDIUM Sensor Run — Offer Scanner + Gap Calculator + Creative Radar (mock)
Runs hourly. Scans 8 networks, calculates arbitrage gaps, scores signals,
emits HIGH+ (score >= 50) to Telegram, deep-dives HIGH with multi-agent-researcher.
"""

import sys
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

HERMES_HOME = Path(os.environ.get("HERMES_HOME", r"D:\Portable_Soft\hermes"))
CACHE_DIR = HERMES_HOME / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Add all necessary paths
sys.path.insert(0, str(HERMES_HOME / "scripts"))
sys.path.insert(0, str(HERMES_HOME / "skills" / "finance" / "arbitrage-sensors" / "scripts"))
sys.path.insert(0, str(HERMES_HOME / "skills" / "finance" / "finance-core" / "scripts"))

# Import sensor modules
from gap_calculator import (
    MOCK_TRAFFIC_COSTS, CPAOffer, TrafficCost, 
    calculate_roi, find_matching_traffic, ROI_THRESHOLD, MIN_PAYOUT, MAX_CPC
)
from format_short_alert import format_alert, format_alert_high
from send_short_alert import send_alert
from finance_core import get_finance_summary

# ============================================================
# EXTENDED NETWORKS: Add 4 target networks (AdCombo, CPAlead, MaxBounty, CPATrend)
# ============================================================

def create_extended_mock_offers() -> List[Dict]:
    """Create mock offers for all 8 networks including the 4 new ones."""
    now = datetime.now(timezone.utc).isoformat()
    
    offers = []
    
    # Admitad (existing 3)
    offers.extend([
        {"network": "admitad", "offer_id": "adm_001", "name": "Кредитная карта Тинькофф", "vertical": "finance", "geo": "RU", "payout": 1500.0, "conversion_type": "CPA", "approval_rate": 0.65, "epc": 45.0, "cr": 0.03, "restrictions": ["no_incent", "age_18+"], "landing_url": "https://landing.tinkoff.ru/credit-card", "updated_at": now},
        {"network": "admitad", "offer_id": "adm_002", "name": "Игра Raid Shadow Legends", "vertical": "gaming", "geo": "RU", "payout": 120.0, "conversion_type": "CPI", "approval_rate": 0.85, "epc": 18.0, "cr": 0.15, "restrictions": ["no_incent", "android_only"], "landing_url": "https://raid-shadow-legends.com/ru", "updated_at": now},
        {"network": "admitad", "offer_id": "adm_003", "name": "Нутра: Похудение Keto Slim", "vertical": "nutra", "geo": "RU", "payout": 850.0, "conversion_type": "CPS", "approval_rate": 0.45, "epc": 32.0, "cr": 0.038, "restrictions": ["no_incent", "age_18+", "cod_only"], "landing_url": "https://keto-slim.ru/landing", "updated_at": now},
    ])
    
    # CityAds (existing 2)
    offers.extend([
        {"network": "cityads", "offer_id": "cit_001", "name": "Микрозайм MoneyMan", "vertical": "finance", "geo": "RU", "payout": 950.0, "conversion_type": "CPA", "approval_rate": 0.55, "epc": 28.0, "cr": 0.029, "restrictions": ["no_incent", "age_18+"], "landing_url": "https://moneyman.ru/loan", "updated_at": now},
        {"network": "cityads", "offer_id": "cit_002", "name": "Страховка авто РасСтрехование", "vertical": "finance", "geo": "RU", "payout": 650.0, "conversion_type": "CPS", "approval_rate": 0.70, "epc": 22.0, "cr": 0.034, "restrictions": ["no_incent"], "landing_url": "https://rasstrakhovanie.ru/auto", "updated_at": now},
    ])
    
    # ActionPay (existing 1)
    offers.append({"network": "actionpay", "offer_id": "act_001", "name": "Крипто-биржа Bybit регистрация", "vertical": "crypto", "geo": "RU", "payout": 450.0, "conversion_type": "CPL", "approval_rate": 0.60, "epc": 15.0, "cr": 0.033, "restrictions": ["no_incent", "kyc_required"], "landing_url": "https://bybit.com/ru-RU/register", "updated_at": now})
    
    # ===== NEW NETWORKS (4 target networks) =====
    
    # AdCombo - strong in nutra, sweepstakes, gaming
    offers.extend([
        {"network": "adcombo", "offer_id": "acb_001", "name": "Нутра: Просталин (продажа)", "vertical": "nutra", "geo": "RU", "payout": 1200.0, "conversion_type": "CPS", "approval_rate": 0.50, "epc": 40.0, "cr": 0.033, "restrictions": ["no_incent", "age_18+", "cod_only"], "landing_url": "https://adcombo.com/lander/prostalim", "updated_at": now},
        {"network": "adcombo", "offer_id": "acb_002", "name": "Sweepstakes: iPhone 15 Giveaway", "vertical": "sweepstakes", "geo": "RU", "payout": 45.0, "conversion_type": "CPL", "approval_rate": 0.80, "epc": 12.0, "cr": 0.25, "restrictions": ["no_incent", "email_submit"], "landing_url": "https://adcombo.com/lander/iphone15", "updated_at": now},
        {"network": "adcombo", "offer_id": "acb_003", "name": "Игра: World of Tanks", "vertical": "gaming", "geo": "RU", "payout": 80.0, "conversion_type": "CPI", "approval_rate": 0.75, "epc": 15.0, "cr": 0.18, "restrictions": ["no_incent", "android_only"], "landing_url": "https://adcombo.com/lander/wot", "updated_at": now},
    ])
    
    # CPAlead - content locking, gaming, mobile
    offers.extend([
        {"network": "cpa_lead", "offer_id": "cpl_001", "name": "Content Lock: Game Cheats Unlock", "vertical": "gaming", "geo": "RU", "payout": 0.85, "conversion_type": "CPI", "approval_rate": 0.90, "epc": 0.45, "cr": 0.50, "restrictions": ["incent_allowed", "content_lock"], "landing_url": "https://cpa-lead.com/lander/gamecheats", "updated_at": now},
        {"network": "cpa_lead", "offer_id": "cpl_002", "name": "Mobile App: VPN Unlimited Install", "vertical": "utility", "geo": "RU", "payout": 1.20, "conversion_type": "CPI", "approval_rate": 0.85, "epc": 0.60, "cr": 0.45, "restrictions": ["incent_allowed"], "landing_url": "https://cpa-lead.com/lander/vpn", "updated_at": now},
        {"network": "cpa_lead", "offer_id": "cpl_003", "name": "Survey: Gaming Preferences RU", "vertical": "survey", "geo": "RU", "payout": 2.50, "conversion_type": "CPL", "approval_rate": 0.70, "epc": 0.80, "cr": 0.30, "restrictions": ["no_incent"], "landing_url": "https://cpa-lead.com/lander/gamingsurvey", "updated_at": now},
    ])
    
    # MaxBounty - finance, lead gen, health
    offers.extend([
        {"network": "maxbounty", "offer_id": "mb_001", "name": "Personal Loan Lead US", "vertical": "finance", "geo": "US", "payout": 45.0, "conversion_type": "CPL", "approval_rate": 0.65, "epc": 18.0, "cr": 0.04, "restrictions": ["no_incent", "us_traffic_only"], "landing_url": "https://maxbounty.com/lander/loan-us", "updated_at": now},
        {"network": "maxbounty", "offer_id": "mb_002", "name": "Credit Card Apply CA", "vertical": "finance", "geo": "CA", "payout": 38.0, "conversion_type": "CPA", "approval_rate": 0.60, "epc": 15.0, "cr": 0.035, "restrictions": ["no_incent", "ca_traffic_only"], "landing_url": "https://maxbounty.com/lander/cc-ca", "updated_at": now},
        {"network": "maxbounty", "offer_id": "mb_003", "name": "Diet Supplement Trial", "vertical": "nutra", "geo": "US", "payout": 55.0, "conversion_type": "CPS", "approval_rate": 0.40, "epc": 22.0, "cr": 0.04, "restrictions": ["no_incent", "age_18+", "cod_allowed"], "landing_url": "https://maxbounty.com/lander/diet-trial", "updated_at": now},
    ])
    
    # CPATrend - dating, nutra, sweepstakes
    offers.extend([
        {"network": "cpa_trend", "offer_id": "cpt_001", "name": "Dating: Mamba RU Registration", "vertical": "dating", "geo": "RU", "payout": 180.0, "conversion_type": "CPL", "approval_rate": 0.75, "epc": 40.0, "cr": 0.20, "restrictions": ["no_incent", "age_18+", "russia_only"], "landing_url": "https://cpatrend.com/lander/mamba-ru", "updated_at": now},
        {"network": "cpa_trend", "offer_id": "cpt_002", "name": "Nutra: Joint Pain Relief Cream", "vertical": "nutra", "geo": "RU", "payout": 950.0, "conversion_type": "CPS", "approval_rate": 0.48, "epc": 35.0, "cr": 0.037, "restrictions": ["no_incent", "age_18+", "cod_only"], "landing_url": "https://cpatrend.com/lander/joint-cream", "updated_at": now},
        {"network": "cpa_trend", "offer_id": "cpt_003", "name": "Sweepstakes: Samsung Galaxy S24", "vertical": "sweepstakes", "geo": "RU", "payout": 55.0, "conversion_type": "CPL", "approval_rate": 0.82, "epc": 18.0, "cr": 0.30, "restrictions": ["no_incent", "email_submit"], "landing_url": "https://cpatrend.com/lander/samsung-s24", "updated_at": now},
    ])
    
    return offers

# ============================================================
# SCORING: Medium sensor uses 0-100 scale (Impact * Urgency * Confidence / 10)
# ============================================================

def score_gap(gap: Dict) -> Dict[str, Any]:
    """
    Score a gap using Medium sensor formula:
    Score = Impact(0-10) * Urgency(0-10) * Confidence(0-10) / 10
    Thresholds: >=70 CRITICAL, >=50 HIGH, >=30 MEDIUM, >=10 LOW
    """
    roi = gap["roi"]
    profit = gap["projected_profit_per_day"]
    confidence = gap["confidence"]
    offer = gap["offer"]
    traffic = gap["traffic"]
    
    # Impact (0-10): based on projected daily profit
    if profit >= 2000:
        impact = 10
    elif profit >= 1000:
        impact = 8
    elif profit >= 500:
        impact = 6
    elif profit >= 200:
        impact = 4
    elif profit >= 100:
        impact = 3
    else:
        impact = 2
    
    # Urgency (0-10): based on ROI and conversion type
    if roi >= 200:
        urgency = 9
    elif roi >= 100:
        urgency = 7
    elif roi >= 50:
        urgency = 5
    elif roi >= 30:
        urgency = 3
    else:
        urgency = 1
    
    # Boost urgency for CPI/CPL (faster feedback loop)
    if offer.get("conversion_type") in ["CPI", "CPL"]:
        urgency = min(urgency + 1, 10)
    
    # Confidence (0-10): from gap calculator (0-1) * 10
    conf_score = min(confidence * 10, 10)
    
    # Score = Impact * Urgency * Confidence / 10 (0-100 scale)
    score = round(impact * urgency * conf_score / 10, 1)
    
    if score >= 70:
        level = "🔴 CRITICAL"
    elif score >= 50:
        level = "🟠 HIGH"
    elif score >= 30:
        level = "🟡 MEDIUM"
    elif score >= 10:
        level = "📝 LOW"
    else:
        level = "📝 LOG"
    
    return {
        **gap,
        "impact": impact,
        "urgency": urgency,
        "confidence_score": round(conf_score, 1),
        "score": score,
        "level": level
    }

# ============================================================
# NETWORK HEALTH (mock)
# ============================================================

def check_network_health() -> List[Dict]:
    """Mock network health check."""
    return [
        {"network": "admitad", "postback_delay_min": 0, "offer_pauses": 0, "approval_rate": 0.65, "status": "healthy"},
        {"network": "cityads", "postback_delay_min": 0, "offer_pauses": 0, "approval_rate": 0.55, "status": "healthy"},
        {"network": "actionpay", "postback_delay_min": 0, "offer_pauses": 0, "approval_rate": 0.60, "status": "healthy"},
        {"network": "ad1", "postback_delay_min": 0, "offer_pauses": 0, "approval_rate": 0.58, "status": "healthy"},
        {"network": "adcombo", "postback_delay_min": 0, "offer_pauses": 0, "approval_rate": 0.62, "status": "healthy"},
        {"network": "cpa_lead", "postback_delay_min": 0, "offer_pauses": 0, "approval_rate": 0.78, "status": "healthy"},
        {"network": "maxbounty", "postback_delay_min": 0, "offer_pauses": 0, "approval_rate": 0.58, "status": "healthy"},
        {"network": "cpa_trend", "postback_delay_min": 0, "offer_pauses": 0, "approval_rate": 0.65, "status": "healthy"},
    ]

# ============================================================
# TELEGRAM ALERT SENDING
# ============================================================

def send_telegram_alert(message: str) -> bool:
    """Send short alert via telegram_bridge."""
    try:
        from telegram_bridge import send_telegram_message
        import os
        chat_id = os.environ.get("TELEGRAM_CHAT_ID", "@your_channel")
        send_telegram_message(text=message, chat_id=chat_id)
        return True
    except Exception as e:
        print(f"[MEDIUM_SENSOR] Telegram send failed: {e}")
        return False

# ============================================================
# MULTI-AGENT RESEARCHER DISPATCH (for HIGH/CRITICAL signals)
# ============================================================

def dispatch_deep_dive(gap: Dict) -> Dict[str, Any]:
    """Dispatch multi-agent-researcher for deep dive on HIGH+ signal."""
    try:
        # Import delegate_task dynamically
        import importlib.util
        spec = importlib.util.spec_from_file_location("delegate_task", str(HERMES_HOME / "scripts" / "hermes_tools.py"))
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            delegate_task = getattr(module, "delegate_task", None)
        else:
            delegate_task = None
        
        if not delegate_task:
            print("[MEDIUM_SENSOR] delegate_task not available, skipping deep-dive")
            return {"dispatched": False, "error": "delegate_task not available"}
        
        offer = gap["offer"]
        traffic = gap["traffic"]
        
        tasks = [
            {
                "goal": f"Deep dive offer {offer['offer_id']} from {offer['network']}: full payout history, cap changes, creative requirements, AM contact, landing page analysis",
                "context": {"offer": offer, "traffic": traffic, "gap": gap},
                "role": "leaf"
            },
            {
                "goal": f"Competitive analysis: who else runs {offer['vertical']} in {offer['geo']}? Landers, angles, traffic sources, estimated spend",
                "context": {"offer": offer, "traffic": traffic, "gap": gap},
                "role": "leaf"
            },
            {
                "goal": f"Traffic source audit for {offer['geo']} {offer['vertical']}: FB vs TikTok vs Native vs Push - current CPC, approval, restrictions",
                "context": {"offer": offer, "traffic": traffic, "gap": gap},
                "role": "leaf"
            },
        ]
        
        print(f"[MEDIUM_SENSOR] Dispatching deep-dive for {offer['offer_id']} ({gap['level']})")
        results = delegate_task(tasks=tasks, timeout=300)
        
        return {
            "dispatched": True,
            "offer_id": offer["offer_id"],
            "gap_id": gap.get("gap_id", ""),
            "results": results
        }
    except Exception as e:
        print(f"[MEDIUM_SENSOR] Deep-dive dispatch failed: {e}")
        return {"dispatched": False, "error": str(e)}

# ============================================================
# MAIN MEDIUM SENSOR RUN
# ============================================================

def main():
    print("=" * 60)
    print(f"MEDIUM SENSOR RUN - {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    
    # 1. Load/Create offers cache with all 8 networks
    offers_cache = CACHE_DIR / "cpa_offers.json"
    
    existing_offers = []
    if offers_cache.exists():
        try:
            raw = json.loads(offers_cache.read_text(encoding="utf-8"))
            existing_offers = raw.get("offers", raw) if isinstance(raw, dict) else raw
        except Exception:
            existing_offers = []
    
    existing_hashes = set()
    for o in existing_offers:
        content = f"{o.get('network','')}:{o.get('offer_id','')}:{o.get('payout',0)}:{o.get('approval_rate',0)}"
        existing_hashes.add(hashlib.md5(content.encode()).hexdigest()[:16])
    
    # Generate extended offers
    extended_offers = create_extended_mock_offers()
    
    # Merge: keep existing + add new from extended
    new_offers = []
    for offer in extended_offers:
        content = f"{offer['network']}:{offer['offer_id']}:{offer['payout']}:{offer['approval_rate']}"
        h = hashlib.md5(content.encode()).hexdigest()[:16]
        if h not in existing_hashes:
            offer["offer_hash"] = h
            new_offers.append(offer)
            existing_hashes.add(h)
        else:
            # Update existing
            for i, ex in enumerate(existing_offers):
                ex_content = f"{ex.get('network','')}:{ex.get('offer_id','')}:{ex.get('payout',0)}:{ex.get('approval_rate',0)}"
                if hashlib.md5(ex_content.encode()).hexdigest()[:16] == h:
                    existing_offers[i] = {**ex, **offer, "offer_hash": h}
                    break
    
    all_offers = existing_offers + new_offers
    offers_cache.write_text(json.dumps(all_offers, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"\n--- CACHED OFFERS ({len(all_offers)}) ---")
    for o in all_offers:
        print(f"  {o['network']:12} | {o['offer_id']:10} | {o['name'][:30]:30} | {o['vertical']:12} | {o['geo']:2} | ${o['payout']:7.2f} | CR:{o['cr']:.3f} | Appr:{o['approval_rate']:.2f}")
    
    if new_offers:
        print(f"\n  [+] {len(new_offers)} NEW offers added from extended networks")
    
    # 2. Calculate gaps
    print(f"\n--- ARBITRAGE GAP CALCULATION ---")
    all_gaps = []
    
    for offer_dict in all_offers:
        offer = CPAOffer(**offer_dict)
        matching_traffic = find_matching_traffic(offer)
        
        for traffic in matching_traffic:
            calc = calculate_roi(offer, traffic)
            
            if calc["roi"] >= ROI_THRESHOLD and offer.payout >= MIN_PAYOUT and traffic.cpc <= MAX_CPC:
                gap_id = f"gap_{offer.network}_{offer.offer_id}_{traffic.source}_{int(datetime.now(timezone.utc).timestamp())}"
                
                gap = {
                    "offer": offer_dict,
                    "traffic": {"source": traffic.source, "geo": traffic.geo, "vertical": traffic.vertical, "cpc": traffic.cpc, "cpm": traffic.cpm},
                    "roi": calc["roi"],
                    "projected_profit_per_day": calc["projected_profit_per_day"],
                    "confidence": calc["confidence"],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "gap_id": gap_id,
                }
                all_gaps.append(gap)
    
    # Score all gaps
    scored_gaps = [score_gap(g) for g in all_gaps]
    scored_gaps.sort(key=lambda x: x["score"], reverse=True)
    
    print(f"\n--- ARBITRAGE GAPS FOUND ({len(scored_gaps)}) ---")
    for g in scored_gaps:
        print(f"  {g['offer']['offer_id']} ({g['offer']['network']}) + {g['traffic']['source']} {g['traffic']['vertical']} {g['traffic']['geo']} | ROI: {g['roi']:.1f}% | ${g['projected_profit_per_day']:.0f}/day | Conf: {g['confidence']:.2f} | Score: {g['score']:.0f} | {g['level']}")
    
    # 3. Network Health
    health = check_network_health()
    print("\n--- NETWORK HEALTH ---")
    for h in health:
        print(f"  {h['network']:12} | Postback: {h['postback_delay_min']}min | Pauses: {h['offer_pauses']} | Approval: {h['approval_rate']:.2f} | {h['status']}")
    
    # 4. Finance Core Baselines
    finance = get_finance_summary()
    print("\n--- FINANCE CORE BASELINES ---")
    print(f"  Revenue 30d: ${finance['pnl_30d']['revenue']['total_usd']:.2f}")
    print(f"  Spend 30d:   ${finance['pnl_30d']['spend']['total_usd']:.2f}")
    print(f"  Net 30d:     ${finance['pnl_30d']['net_usd']:.2f}")
    print(f"  USD/RUB:     {finance['usd_rate']:.2f}")
    print(f"  Active schemes: {len(finance['schemes'])}")
    print(f"  Tax pending:   ${finance['tax']['pending_usd']:.2f}")
    print(f"  Pending withdrawals: {len(finance['pending_withdrawals'])}")
    
    # 5. Alert generation (HIGH+ >= 50)
    print("\n--- ALERTS (HIGH+ >= 50) ---")
    high_alerts = [g for g in scored_gaps if g["score"] >= 50]
    
    if high_alerts:
        for a in high_alerts:
            # Send to Telegram using send_alert (formats + sends)
            success = send_alert(a)
            if success:
                print(f"    [SENT] Telegram alert delivered")
            else:
                print(f"    [FAILED] Telegram delivery failed")

            # Dispatch deep-dive for HIGH/CRITICAL
            if a["score"] >= 50:
                dispatch_result = dispatch_deep_dive(a)
                if dispatch_result.get("dispatched"):
                    print(f"    [DEEP-DIVE] Dispatched multi-agent researcher")
                else:
                    print(f"    [DEEP-DIVE] Skipped: {dispatch_result.get('error', 'unknown')}")
    else:
        print("  [SILENT] - No HIGH+ alerts")
        return "[SILENT]"
    
    print("\n=== END MEDIUM SENSOR RUN ===")
    return f"Alerts sent: {len(high_alerts)}"

if __name__ == "__main__":
    result = main()
    if result:
        print(result)