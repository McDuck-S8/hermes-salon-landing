#!/usr/bin/env python3
"""
Gap Calculator — Calculates arbitrage gaps from CPA offers + traffic costs.
Emits arbitrage_gap_found when ROI exceeds threshold.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
CACHE_DIR = HERMES_HOME / "cache"
GAPS_CACHE = CACHE_DIR / "arbitrage_gaps.json"
STATE_FILE = CACHE_DIR / "gap_calculator_state.json"

# Event bus integration
sys.path.insert(0, str(HERMES_HOME / "scripts"))
try:
    from event_bus import emit
    _EVENT_BUS_ENABLED = True
except ImportError:
    _EVENT_BUS_ENABLED = False
    def emit(event_type: str, payload: dict = None):
        pass

# Config
ROI_THRESHOLD = float(os.environ.get("ARBITRAGE_ROI_THRESHOLD", "30"))  # %
MIN_PAYOUT = float(os.environ.get("ARBITRAGE_MIN_PAYOUT", "100"))
MAX_CPC = float(os.environ.get("ARBITRAGE_MAX_CPC", "50"))

@dataclass
class CPAOffer:
    network: str
    offer_id: str
    name: str
    vertical: str
    geo: str
    payout: float
    conversion_type: str
    approval_rate: float
    epc: float
    cr: float
    restrictions: List[str]
    landing_url: str
    updated_at: str
    offer_hash: str = ""

@dataclass
class TrafficCost:
    source: str
    geo: str
    vertical: str
    cpc: float
    cpm: float
    min_deposit: float
    targeting_options: List[str]
    updated_at: str

@dataclass
class ArbitrageGap:
    offer: CPAOffer
    traffic: TrafficCost
    roi: float
    projected_profit_per_day: float
    confidence: float
    created_at: str
    gap_id: str = ""

# Mock traffic costs (would come from real APIs)
MOCK_TRAFFIC_COSTS = [
    TrafficCost(
        source="kadam",
        geo="RU",
        vertical="finance",
        cpc=8.5,
        cpm=120.0,
        min_deposit=500.0,
        targeting_options=["interest:finance", "age:25-55"],
        updated_at=datetime.now(timezone.utc).isoformat(),
    ),
    TrafficCost(
        source="kadam",
        geo="RU",
        vertical="nutra",
        cpc=12.0,
        cpm=180.0,
        min_deposit=500.0,
        targeting_options=["interest:health", "age:30-60"],
        updated_at=datetime.now(timezone.utc).isoformat(),
    ),
    TrafficCost(
        source="richads",
        geo="RU",
        vertical="gaming",
        cpc=4.5,
        cpm=80.0,
        min_deposit=300.0,
        targeting_options=["interest:gaming", "age:18-35", "device:android"],
        updated_at=datetime.now(timezone.utc).isoformat(),
    ),
    TrafficCost(
        source="facebook",
        geo="RU",
        vertical="finance",
        cpc=18.0,
        cpm=350.0,
        min_deposit=1000.0,
        targeting_options=["interest:credit_cards", "age:25-50"],
        updated_at=datetime.now(timezone.utc).isoformat(),
    ),
    TrafficCost(
        source="google",
        geo="RU",
        vertical="finance",
        cpc=22.0,
        cpm=400.0,
        min_deposit=1000.0,
        targeting_options=["intent:loan", "age:25-55"],
        updated_at=datetime.now(timezone.utc).isoformat(),
    ),
    TrafficCost(
        source="tiktok",
        geo="RU",
        vertical="nutra",
        cpc=15.0,
        cpm=250.0,
        min_deposit=500.0,
        targeting_options=["interest:weight_loss", "age:25-45"],
        updated_at=datetime.now(timezone.utc).isoformat(),
    ),
]

def load_state() -> Dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"known_gap_ids": set(), "last_calculation": None}

def save_state(state: Dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    state_copy = state.copy()
    if "known_gap_ids" in state_copy:
        state_copy["known_gap_ids"] = list(state_copy["known_gap_ids"])
    STATE_FILE.write_text(json.dumps(state_copy, indent=2, ensure_ascii=False), encoding="utf-8")

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

def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [GAP_CALC] {msg}")

def calculate_roi(offer: CPAOffer, traffic: TrafficCost) -> Dict[str, Any]:
    """
    Calculate ROI for offer + traffic combination.
    
    Formula:
    - EPC_effective = payout * approval_rate
    - Cost_per_conversion = CPC / CR
    - Profit_per_conversion = EPC_effective - Cost_per_conversion
    - ROI = Profit_per_conversion / Cost_per_conversion * 100%
    """
    epc_effective = offer.payout * offer.approval_rate
    cost_per_conversion = traffic.cpc / offer.cr if offer.cr > 0 else float('inf')
    profit_per_conversion = epc_effective - cost_per_conversion
    roi = (profit_per_conversion / cost_per_conversion * 100) if cost_per_conversion > 0 else -100
    
    # Projected daily profit (assuming 100 clicks/day)
    clicks_per_day = 100
    conversions_per_day = clicks_per_day * offer.cr
    revenue_per_day = conversions_per_day * epc_effective
    cost_per_day = clicks_per_day * traffic.cpc
    profit_per_day = revenue_per_day - cost_per_day
    
    # Confidence based on data quality
    confidence = min(offer.approval_rate * offer.cr * 10, 1.0)
    
    return {
        "roi": round(roi, 2),
        "epc_effective": round(epc_effective, 2),
        "cost_per_conversion": round(cost_per_conversion, 2),
        "profit_per_conversion": round(profit_per_conversion, 2),
        "projected_profit_per_day": round(profit_per_day, 2),
        "confidence": round(confidence, 2),
    }

def find_matching_traffic(offer: CPAOffer) -> List[TrafficCost]:
    """Find traffic sources matching offer's geo and vertical."""
    matches = []
    for traffic in MOCK_TRAFFIC_COSTS:
        if traffic.geo == offer.geo and traffic.vertical == offer.vertical:
            matches.append(traffic)
    return matches

def process_offer(offer_dict: Dict) -> List[ArbitrageGap]:
    """Process a single offer against all matching traffic sources."""
    offer = CPAOffer(**offer_dict)
    gaps = []
    
    matching_traffic = find_matching_traffic(offer)
    
    for traffic in matching_traffic:
        calc = calculate_roi(offer, traffic)
        
        if calc["roi"] >= ROI_THRESHOLD and offer.payout >= MIN_PAYOUT and traffic.cpc <= MAX_CPC:
            gap_id = f"gap_{offer.network}_{offer.offer_id}_{traffic.source}_{int(time.time())}"
            
            gap = ArbitrageGap(
                offer=offer,
                traffic=traffic,
                roi=calc["roi"],
                projected_profit_per_day=calc["projected_profit_per_day"],
                confidence=calc["confidence"],
                created_at=datetime.now(timezone.utc).isoformat(),
                gap_id=gap_id,
            )
            gaps.append(gap)
    
    return gaps

def emit_gaps(gaps: List[ArbitrageGap]):
    """Emit arbitrage_gap_found events."""
    for gap in gaps:
        payload = {
            "gap_id": gap.gap_id,
            "offer": asdict(gap.offer),
            "traffic": asdict(gap.traffic),
            "roi": gap.roi,
            "projected_profit_per_day": gap.projected_profit_per_day,
            "confidence": gap.confidence,
            "created_at": gap.created_at,
        }
        emit("arbitrage_gap_found", payload)
        log(f"Emitted arbitrage_gap_found: {gap.gap_id} - ROI: {gap.roi}% - ${gap.projected_profit_per_day}/day")

def run_calculation() -> Dict[str, Any]:
    """Run gap calculation on all cached offers."""
    log("Starting gap calculation...")
    state = load_state()
    known_gap_ids = set(state.get("known_gap_ids", []))
    all_gaps = load_gaps_cache()
    existing_gap_ids = {g.get("gap_id", "") for g in all_gaps}
    
    # Load offers
    offers_cache = CACHE_DIR / "cpa_offers.json"
    if not offers_cache.exists():
        log("No offers cache found")
        return {"calculated": 0, "new_gaps": 0}
    
    raw = json.loads(offers_cache.read_text(encoding="utf-8"))
    offers = raw.get("offers", raw) if isinstance(raw, dict) else raw
    new_gaps = []
    
    for offer_dict in offers:
        gaps = process_offer(offer_dict)
        for gap in gaps:
            if gap.gap_id not in known_gap_ids and gap.gap_id not in existing_gap_ids:
                new_gaps.append(gap)
                known_gap_ids.add(gap.gap_id)
                existing_gap_ids.add(gap.gap_id)
    
    if new_gaps:
        emit_gaps(new_gaps)
        all_gaps.extend([asdict(g) for g in new_gaps])
        save_gaps_cache(all_gaps)
    
    state["last_calculation"] = datetime.now(timezone.utc).isoformat()
    state["known_gap_ids"] = list(known_gap_ids)
    state["total_gaps"] = len(all_gaps)
    state["new_this_calc"] = len(new_gaps)
    save_state(state)
    
    log(f"Calculation complete: {len(offers)} offers processed, {len(new_gaps)} new gaps")
    
    return {
        "offers_processed": len(offers),
        "new_gaps": len(new_gaps),
        "total_gaps": len(all_gaps),
    }

def run_daemon(interval_minutes: int = 30):
    """Run as daemon with interval."""
    log(f"Gap Calculator daemon started (interval: {interval_minutes}min)")
    
    # Initial calculation
    run_calculation()
    
    while True:
        time.sleep(interval_minutes * 60)
        try:
            run_calculation()
        except Exception as e:
            log(f"Calculation error: {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gap Calculator")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=int, default=30, help="Interval in minutes (daemon mode)")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    args = parser.parse_args()
    
    if args.once or not args.daemon:
        result = run_calculation()
        print(json.dumps(result, indent=2))
    else:
        run_daemon(args.interval)

if __name__ == "__main__":
    main()