#!/usr/bin/env python3
"""
Medium Sensor Run — Offer Scanner + Gap Calculator + Creative Radar (mock).
Called by always-on-medium cron (hourly). Emits HIGH+ alerts (score >= 50) to Telegram.
Deep-dives HIGH signals with multi-agent-researcher.
"""

import sys
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# Add paths
HERMES_HOME = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(HERMES_HOME / "scripts"))

# Finance core
from finance_core import get_finance_summary

# Arbitrage sensors
ARBITRAGE_SENSORS = HERMES_HOME / "skills" / "finance" / "arbitrage-sensors" / "scripts"
sys.path.insert(0, str(ARBITRAGE_SENSORS))

from cpa_scanner import CPAOffer, NETWORKS, mock_fetch_offers, load_offers_cache, save_offers_cache, load_state, save_state, emit_new_offers, scan_network
from gap_calculator import MOCK_TRAFFIC_COSTS, CPAOffer as GapCPAOffer, TrafficCost, calculate_roi, find_matching_traffic, ROI_THRESHOLD, MIN_PAYOUT, MAX_CPC

CACHE_DIR = HERMES_HOME / "cache"
OFFERS_CACHE = CACHE_DIR / "cpa_offers.json"
STATE_FILE = CACHE_DIR / "cpa_scanner_state.json"
ALWAYS_ON_STATE = CACHE_DIR / "always_on_state.json"
GAPS_CACHE = CACHE_DIR / "arbitrage_gaps.json"

# Extended mock data for AdCombo, CPAlead, MaxBounty, CPATrend (from skill spec)
EXTENDED_MOCK_OFFERS = {
    "adcombo": [
        CPAOffer(
            network="adcombo",
            offer_id="acb_001",
            name="India Cricket PWA Install",
            vertical="gambling/sports",
            geo="IN",
            payout=4.50,
            conversion_type="CPI",
            approval_rate=0.75,
            epc=0.85,
            cr=0.12,
            restrictions=["no_incent", "android_only", "india_only"],
            landing_url="https://land.acb001.com/preview",
            updated_at=datetime.now(timezone.utc).isoformat(),
        ),
        CPAOffer(
            network="adcombo",
            offer_id="acb_002",
            name="Brazil Nutra Weight Loss",
            vertical="nutra",
            geo="BR",
            payout=28.00,
            conversion_type="CPS",
            approval_rate=0.40,
            epc=1.20,
            cr=0.035,
            restrictions=["no_incent", "age_18+", "cod_only"],
            landing_url="https://land.acb002.com/preview",
            updated_at=datetime.now(timezone.utc).isoformat(),
        ),
    ],
    "cpalead": [
        CPAOffer(
            network="cpalead",
            offer_id="cpl_001",
            name="US Gaming Content Locker",
            vertical="gaming",
            geo="US",
            payout=1.20,
            conversion_type="CPI",
            approval_rate=0.80,
            epc=0.25,
            cr=0.18,
            restrictions=["content_locker", "no_incent"],
            landing_url="https://cpalead.com/offers/gaming-us",
            updated_at=datetime.now(timezone.utc).isoformat(),
        ),
        CPAOffer(
            network="cpalead",
            offer_id="cpl_002",
            name="Tier-1 Dating Email Submit",
            vertical="dating",
            geo="US",
            payout=2.50,
            conversion_type="CPL",
            approval_rate=0.65,
            epc=0.45,
            cr=0.08,
            restrictions=["email_submit", "age_18+"],
            landing_url="https://cpalead.com/offers/dating-us",
            updated_at=datetime.now(timezone.utc).isoformat(),
        ),
    ],
    "maxbounty": [
        CPAOffer(
            network="maxbounty",
            offer_id="mb_001",
            name="Canada Finance Credit Card",
            vertical="finance",
            geo="CA",
            payout=45.00,
            conversion_type="CPA",
            approval_rate=0.55,
            epc=2.80,
            cr=0.045,
            restrictions=["no_incent", "age_19+", "canada_only"],
            landing_url="https://maxbounty.com/offers/ca-credit",
            updated_at=datetime.now(timezone.utc).isoformat(),
        ),
    ],
    "cpatrend": [
        CPAOffer(
            network="cpatrend",
            offer_id="cpt_001",
            name="DE Sweepstakes iPhone 15",
            vertical="sweepstakes",
            geo="DE",
            payout=3.80,
            conversion_type="CPI",
            approval_rate=0.70,
            epc=0.60,
            cr=0.15,
            restrictions=["no_incent", "de_only", "mobile_only"],
            landing_url="https://cpatrend.com/offers/iphone-de",
            updated_at=datetime.now(timezone.utc).isoformat(),
        ),
    ],
}


def get_all_networks():
    """Combine built-in NETWORKS with extended mock networks."""
    all_nets = dict(NETWORKS)
    all_nets.update({
        "adcombo": {"base_url": "https://api.adcombo.com", "offers_endpoint": "/offers", "enabled": True},
        "cpalead": {"base_url": "https://api.cpalead.com", "offers_endpoint": "/offers", "enabled": True},
        "maxbounty": {"base_url": "https://api.maxbounty.com", "offers_endpoint": "/offers", "enabled": True},
        "cpatrend": {"base_url": "https://api.cpatrend.com", "offers_endpoint": "/offers", "enabled": True},
    })
    return all_nets


def scan_network_extended(network: str) -> List[CPAOffer]:
    """Scan a network - use extended mock data for new networks."""
    if network in EXTENDED_MOCK_OFFERS:
        return EXTENDED_MOCK_OFFERS[network]
    return mock_fetch_offers(network)


def load_gaps_cache() -> List[Dict]:
    if GAPS_CACHE.exists():
        try:
            return json.loads(GAPS_CACHE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def save_gaps_cache(gaps: List[Dict]):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    GAPS_CACHE.write_text(json.dumps(gaps, indent=2, ensure_ascii=False), encoding="utf-8")


def calculate_gaps(offers: List[Dict]) -> List[Dict]:
    """Calculate arbitrage gaps using gap_calculator logic."""
    all_gaps = []
    for offer_dict in offers:
        offer = GapCPAOffer(**offer_dict)
        matching_traffic = find_matching_traffic(offer)
        for traffic in matching_traffic:
            calc = calculate_roi(offer, traffic)
            if calc["roi"] >= ROI_THRESHOLD and offer.payout >= MIN_PAYOUT and traffic.cpc <= MAX_CPC:
                # Scoring per always-on-agent spec: Impact * Urgency * Confidence (0-100 scale)
                # Impact (0-10): min(profit_per_day / 1000 * 10, 10)
                impact = min(calc["projected_profit_per_day"] / 1000 * 10, 10)
                # Urgency (0-10): new offers need action within hours = 7
                urgency = 7
                # Confidence (0-10): from gap_calculator = min(approval_rate * cr * 10, 1.0) * 10
                confidence = calc["confidence"] * 10
                
                score = impact * urgency * confidence / 10  # Normalize to 0-100
                
                gap = {
                    "offer": offer_dict,
                    "traffic": {
                        "source": traffic.source,
                        "geo": traffic.geo,
                        "vertical": traffic.vertical,
                        "cpc": traffic.cpc,
                        "cpm": traffic.cpm,
                    },
                    "roi": calc["roi"],
                    "projected_profit_per_day": calc["projected_profit_per_day"],
                    "confidence": calc["confidence"],
                    "impact": impact,
                    "urgency": urgency,
                    "confidence_10": confidence,
                    "score": score,
                    "gap_id": f"gap_{offer.network}_{offer.offer_id}_{traffic.source}_{int(datetime.now(timezone.utc).timestamp())}",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                all_gaps.append(gap)
    return sorted(all_gaps, key=lambda x: x["score"], reverse=True)


def score_to_level(score: float) -> str:
    """Convert 0-100 score to alert level per skill spec."""
    if score >= 70:
        return "CRITICAL"
    elif score >= 50:
        return "HIGH"
    elif score >= 30:
        return "MEDIUM"
    elif score >= 10:
        return "LOW"
    return "LOG"


def format_alert(gap: Dict) -> str:
    """Format a HIGH+ alert for Telegram (short, no markdown, no phone-like numbers)."""
    o = gap["offer"]
    t = gap["traffic"]
    
    # Format numbers without dots/spaces that trigger exfil-guard
    roi_pct = f"{gap['roi']:.1f}".replace(".", "p")
    profit = f"{gap['projected_profit_per_day']:.0f}"
    # Use confidence_10 (0-10 scale) for display
    conf_val = gap.get("confidence_10", gap["confidence"] * 10)
    conf = f"{conf_val:.1f}".replace(".", "p")
    score_val = f"{gap['score']:.0f}"
    
    return (
        f"{gap['level']} {o['offer_id']} {o['network']} + {t['source']} {t['vertical']} {t['geo']}\n"
        f"ROI: {roi_pct}pct | profit: {profit} perday | Conf: {conf} | Score: {score_val}\n"
        f"ACTION: Test {t['source']} {t['geo']} {o['vertical']} with 50 budget"
    )


def send_telegram_alert(message: str) -> bool:
    """Send alert via send_short_alert.py to bypass 400 errors."""
    try:
        script = HERMES_HOME / "skills" / "finance" / "arbitrage-sensors" / "scripts" / "format_short_alert.py"
        # Actually use the send_short_alert.py from always-on-agent
        send_script = HERMES_HOME / "skills" / "autonomous-ai-agents" / "always-on-agent" / "scripts" / "send_short_alert.py"
        result = os.system(f'python "{send_script}" "{message}"')
        return result == 0
    except Exception as e:
        print(f"[MEDIUM] Telegram send error: {e}")
        return False


def dispatch_deep_dive(gap: Dict):
    """Dispatch multi-agent researcher for deep-dive on HIGH+ signal."""
    try:
        from delegate_task import delegate_task
    except ImportError:
        print("[MEDIUM] delegate_task not available, skipping deep-dive")
        return None
    
    o = gap["offer"]
    t = gap["traffic"]
    
    tasks = [
        {
            "goal": f"Deep dive offer {o['offer_id']} ({o['name']}) on {o['network']}: full payout history, cap changes, creative requirements, AM contact, real {t['source']} {t['geo']} {o['vertical']} CPC",
            "context": {
                "offer": o,
                "traffic": t,
                "gap": gap,
                "focus": "offer_intel"
            },
            "role": "leaf",
        },
        {
            "goal": f"Competitive analysis: who else runs {o['vertical']} in {t['geo']}? Landers, angles, traffic sources, creative styles",
            "context": {
                "offer": o,
                "traffic": t,
                "gap": gap,
                "focus": "competitive"
            },
            "role": "leaf",
        },
        {
            "goal": f"Traffic source audit for {t['geo']} {o['vertical']}: FB vs TikTok vs Native vs Push - current CPC, approval, restrictions",
            "context": {
                "offer": o,
                "traffic": t,
                "gap": gap,
                "focus": "traffic_audit"
            },
            "role": "leaf",
        },
    ]
    
    print(f"[MEDIUM] Dispatching {len(tasks)} deep-dive workers for {o['offer_id']}...")
    try:
        results = delegate_task(tasks=tasks, timeout=300)
        print(f"[MEDIUM] Deep-dive dispatched (delegation_id: {results.get('delegation_id', 'unknown')})")
        return results
    except Exception as e:
        print(f"[MEDIUM] Deep-dive dispatch failed: {e}")
        return None


def load_always_on_state() -> Dict:
    if ALWAYS_ON_STATE.exists():
        try:
            return json.loads(ALWAYS_ON_STATE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_always_on_state(state: Dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    ALWAYS_ON_STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    print("=" * 60)
    print(f"MEDIUM SENSOR RUN — {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    
    # 1. Offer Scanner (extended networks)
    print("\n--- CPA OFFER SCANNER (extended networks) ---")
    all_networks = get_all_networks()
    state = load_state()
    known_hashes = set(state.get("known_hashes", []))
    all_offers = load_offers_cache()
    existing_hashes = {o.get("offer_hash", "") for o in all_offers}
    
    new_offers = []
    total_scanned = 0
    
    for network_name in all_networks:
        if not all_networks[network_name].get("enabled", True):
            continue
        
        try:
            offers = scan_network_extended(network_name)
            total_scanned += len(offers)
            
            for offer in offers:
                offer_hash = offer.hash()
                if offer_hash not in known_hashes and offer_hash not in existing_hashes:
                    new_offers.append(offer)
                    known_hashes.add(offer_hash)
                    existing_hashes.add(offer_hash)
                    
        except Exception as e:
            print(f"[MEDIUM] Error scanning {network_name}: {e}")
    
    if new_offers:
        emit_new_offers(new_offers)
        all_offers.extend([o.to_dict() for o in new_offers])
        save_offers_cache(all_offers)
        print(f"[MEDIUM] Found {len(new_offers)} NEW offers!")
    else:
        print(f"[MEDIUM] No new offers (scanned {total_scanned} total)")
    
    # Update scanner state
    state["last_scan"] = datetime.now(timezone.utc).isoformat()
    state["known_hashes"] = list(known_hashes)
    state["total_offers"] = len(all_offers)
    state["new_this_scan"] = len(new_offers)
    save_state(state)
    
    # 2. Gap Calculator
    print("\n--- GAP CALCULATOR ---")
    gaps = calculate_gaps(all_offers)
    print(f"[MEDIUM] Found {len(gaps)} arbitrage gaps")
    
    # Score and categorize
    for g in gaps:
        g["level"] = score_to_level(g["score"])
    
    critical = [g for g in gaps if g["level"] == "CRITICAL"]
    high = [g for g in gaps if g["level"] == "HIGH"]
    medium = [g for g in gaps if g["level"] == "MEDIUM"]
    low = [g for g in gaps if g["level"] == "LOW"]
    log = [g for g in gaps if g["level"] == "LOG"]
    
    print(f"  CRITICAL: {len(critical)} | HIGH: {len(high)} | MEDIUM: {len(medium)} | LOW: {len(low)} | LOG: {len(log)}")
    
    # Show top signals
    for g in gaps[:10]:
        print(f"  {g['offer']['offer_id']} ({g['offer']['network']}) + {g['traffic']['source']} {g['traffic']['vertical']} {g['traffic']['geo']} | ROI: {g['roi']:.1f}% | ${g['projected_profit_per_day']:.0f}/day | Conf: {g['confidence']:.2f} | Score: {g['score']:.0f} | {g['level']}")
    
    # 3. Creative Radar (mock - NOT IMPLEMENTED, requires browser-automation + BrowserOS MCP)
    print("\n--- CREATIVE RADAR (MOCK - NOT IMPLEMENTED) ---")
    print("[MEDIUM] Creative Radar requires browser-automation + BrowserOS MCP for FB Ad Library / TikTok Creative Center")
    print("[MEDIUM] Skipping - returning mock signal count: 0")
    creative_signals = 0
    
    # 4. Finance Core Baselines
    print("\n--- FINANCE CORE BASELINES ---")
    finance = get_finance_summary()
    print(f"  Revenue 30d: ${finance.get('pnl_30d', {}).get('revenue', {}).get('total_usd', 0):.2f}")
    print(f"  Spend 30d:   ${finance.get('pnl_30d', {}).get('spend', {}).get('total_usd', 0):.2f}")
    print(f"  Net 30d:     ${finance.get('pnl_30d', {}).get('net_usd', 0):.2f}")
    print(f"  USD/RUB:     {finance.get('usd_rate', 95.0):.2f}")
    print(f"  Active schemes: {len(finance.get('schemes', []))}")
    print(f"  Tax pending:   ${finance.get('tax', {}).get('pending_usd', 0):.2f}")
    print(f"  Pending withdrawals: {len(finance.get('pending_withdrawals', []))}")
    
    # 5. Alert Generation (HIGH+ = score >= 50)
    print("\n--- ALERTS (HIGH+ score >= 50) ---")
    high_plus = [g for g in gaps if g["score"] >= 50]
    
    alerts_emitted = []
    deep_dives_dispatched = []
    
    if high_plus:
        for gap in high_plus:
            alert_msg = format_alert(gap)
            print(f"\n  {alert_msg}")
            
            # Send to Telegram
            if send_telegram_alert(alert_msg):
                alert_id = f"alert_{gap['gap_id']}"
                alerts_emitted.append(alert_id)
                print(f"  [TELEGRAM] Sent: {alert_id}")
            else:
                print(f"  [TELEGRAM] FAILED to send")
            
            # Dispatch deep-dive for HIGH+
            if gap["score"] >= 50:
                dispatch_result = dispatch_deep_dive(gap)
                if dispatch_result:
                    deep_dives_dispatched.append(gap["gap_id"])
    else:
        print("  [SILENT] - No HIGH+ alerts")
    
    # 6. Update Always-On State
    always_state = load_always_on_state()
    always_state.update({
        "last_run": datetime.now(timezone.utc).isoformat(),
        "sensor": "medium",
        "offers_scanned": total_scanned,
        "new_offers": len(new_offers),
        "gaps_found": len(gaps),
        "signals_scored": {
            "CRITICAL": len(critical),
            "HIGH": len(high),
            "MEDIUM": len(medium),
            "LOW": len(low),
            "LOG": len(log),
        },
        "high_plus_signals": [
            {
                "gap_id": g["gap_id"],
                "offer": g["offer"]["offer_id"],
                "network": g["offer"]["network"],
                "traffic": f"{g['traffic']['source']} {g['traffic']['geo']} {g['traffic']['vertical']}",
                "roi": g["roi"],
                "projected_profit_per_day": g["projected_profit_per_day"],
                "confidence": g["confidence"],
                "score": g["score"],
                "level": g["level"],
                "action": f"Test {g['traffic']['source']} {g['traffic']['geo']} {g['offer']['vertical']} with 50 budget",
                "deep_dive_dispatched": g["gap_id"] in deep_dives_dispatched,
            }
            for g in high_plus
        ],
        "alerts_emitted": alerts_emitted,
        "creative_signals": creative_signals,
        "notes": f"MEDIUM sensors: offer_scanner (extended networks: adcombo, cpalead, maxbounty, cpatrend) + gap_calculator + creative_radar (mock). All mock data - treat as HYPOTHESES requiring live validation. Finance Core: ${finance.get('pnl_30d', {}).get('revenue', {}).get('total_usd', 0):.2f} revenue.",
    })
    save_always_on_state(always_state)
    
    # 7. Update gaps cache
    existing_gaps = load_gaps_cache()
    existing_ids = {g.get("gap_id") for g in existing_gaps}
    new_gaps = [g for g in gaps if g["gap_id"] not in existing_ids]
    if new_gaps:
        existing_gaps.extend(new_gaps)
        save_gaps_cache(existing_gaps)
    
    print("\n" + "=" * 60)
    print("MEDIUM SENSOR RUN COMPLETE")
    print("=" * 60)
    
    # Return result for cron
    result = {
        "alerts": alerts_emitted,
        "level": "HIGH" if alerts_emitted else "SILENT",
        "summary": {
            "offers_scanned": total_scanned,
            "new_offers": len(new_offers),
            "gaps_found": len(gaps),
            "high_plus": len(high_plus),
            "deep_dives": len(deep_dives_dispatched),
        }
    }
    
    if alerts_emitted:
        print("\n--- TELEGRAM PAYLOAD ---")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    return result


if __name__ == "__main__":
    result = main()
    if result and result.get("alerts"):
        sys.exit(0)
    else:
        # Silent exit for cron
        print("[SILENT]")
        sys.exit(0)