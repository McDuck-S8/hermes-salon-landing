#!/usr/bin/env python3
"""
CPA Offer Scanner — Parses offers from CPA networks.
Emits new_cpa_offer events for gap calculation.
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
CACHE_DIR = HERMES_HOME / "cache"
OFFERS_CACHE = CACHE_DIR / "cpa_offers.json"
STATE_FILE = CACHE_DIR / "cpa_scanner_state.json"

# Event bus integration
sys.path.insert(0, str(HERMES_HOME / "scripts"))
try:
    from event_bus import emit
    _EVENT_BUS_ENABLED = True
except ImportError:
    _EVENT_BUS_ENABLED = False
    def emit(event_type: str, payload: dict = None):
        pass

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
    
    def to_dict(self):
        return asdict(self)
    
    def hash(self) -> str:
        content = f"{self.network}:{self.offer_id}:{self.payout}:{self.approval_rate}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

# Network configurations
NETWORKS = {
    "admitad": {
        "base_url": "https://api.admitad.com",
        "offers_endpoint": "/offers/",
        "enabled": True,
    },
    "cityads": {
        "base_url": "https://api.cityads.com",
        "offers_endpoint": "/v1/offers",
        "enabled": True,
    },
    "actionpay": {
        "base_url": "https://api.actionpay.ru",
        "offers_endpoint": "/offers",
        "enabled": True,
    },
    "ad1": {
        "base_url": "https://api.ad1.ru",
        "offers_endpoint": "/offers",
        "enabled": True,
    },
}

def load_state() -> Dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"last_scan": None, "known_hashes": set()}

def save_state(state: Dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    # Convert set to list for JSON
    state_copy = state.copy()
    if "known_hashes" in state_copy:
        state_copy["known_hashes"] = list(state_copy["known_hashes"])
    STATE_FILE.write_text(json.dumps(state_copy, indent=2, ensure_ascii=False), encoding="utf-8")

def load_offers_cache() -> List[Dict]:
    if OFFERS_CACHE.exists():
        try:
            data = json.loads(OFFERS_CACHE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data.get("offers", [])
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []

def save_offers_cache(offers: List[Dict]):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    OFFERS_CACHE.write_text(json.dumps(offers, indent=2, ensure_ascii=False), encoding="utf-8")

def get_api_key(network: str) -> Optional[str]:
    """Get API key from env."""
    key_map = {
        "admitad": "ADMITAD_API_KEY",
        "cityads": "CITYADS_API_KEY",
        "actionpay": "ACTIONPAY_API_KEY",
        "ad1": "AD1_API_KEY",
    }
    return os.environ.get(key_map.get(network, ""))

def mock_fetch_offers(network: str) -> List[CPAOffer]:
    """Mock data for testing without API keys."""
    mock_offers = {
        "admitad": [
            CPAOffer(
                network="admitad",
                offer_id="adm_001",
                name="Кредитная карта Тинькофф",
                vertical="finance",
                geo="RU",
                payout=1500.0,
                conversion_type="CPA",
                approval_rate=0.65,
                epc=45.0,
                cr=0.03,
                restrictions=["no_incent", "age_18+"],
                landing_url="https://landing.tinkoff.ru/credit-card",
                updated_at=datetime.now(timezone.utc).isoformat(),
            ),
            CPAOffer(
                network="admitad",
                offer_id="adm_002",
                name="Игра Raid Shadow Legends",
                vertical="gaming",
                geo="RU",
                payout=120.0,
                conversion_type="CPI",
                approval_rate=0.85,
                epc=18.0,
                cr=0.15,
                restrictions=["no_incent", "android_only"],
                landing_url="https://raid-shadow-legends.com/ru",
                updated_at=datetime.now(timezone.utc).isoformat(),
            ),
            CPAOffer(
                network="admitad",
                offer_id="adm_003",
                name="Нутра: Похудение Keto Slim",
                vertical="nutra",
                geo="RU",
                payout=850.0,
                conversion_type="CPS",
                approval_rate=0.45,
                epc=32.0,
                cr=0.038,
                restrictions=["no_incent", "age_18+", "cod_only"],
                landing_url="https://keto-slim.ru/landing",
                updated_at=datetime.now(timezone.utc).isoformat(),
            ),
        ],
        "cityads": [
            CPAOffer(
                network="cityads",
                offer_id="cit_001",
                name="Микрозайм MoneyMan",
                vertical="finance",
                geo="RU",
                payout=950.0,
                conversion_type="CPA",
                approval_rate=0.55,
                epc=28.0,
                cr=0.029,
                restrictions=["no_incent", "age_18+"],
                landing_url="https://moneyman.ru/loan",
                updated_at=datetime.now(timezone.utc).isoformat(),
            ),
            CPAOffer(
                network="cityads",
                offer_id="cit_002",
                name="Страховка авто РасСтрехование",
                vertical="finance",
                geo="RU",
                payout=650.0,
                conversion_type="CPS",
                approval_rate=0.70,
                epc=22.0,
                cr=0.034,
                restrictions=["no_incent"],
                landing_url="https://rasstrakhovanie.ru/auto",
                updated_at=datetime.now(timezone.utc).isoformat(),
            ),
        ],
        "actionpay": [
            CPAOffer(
                network="actionpay",
                offer_id="act_001",
                name="Крипто-биржа Bybit регистрация",
                vertical="crypto",
                geo="RU",
                payout=450.0,
                conversion_type="CPL",
                approval_rate=0.60,
                epc=15.0,
                cr=0.033,
                restrictions=["no_incent", "kyc_required"],
                landing_url="https://bybit.com/ru-RU/register",
                updated_at=datetime.now(timezone.utc).isoformat(),
            ),
        ],
    }
    return mock_offers.get(network, [])

def scan_network(network: str) -> List[CPAOffer]:
    """Scan a single network for offers."""
    api_key = get_api_key(network)
    
    if not api_key:
        # Use mock data for testing
        log(f"No API key for {network}, using mock data")
        return mock_fetch_offers(network)
    
    # Real API implementation would go here
    # For now, return mock
    return mock_fetch_offers(network)

def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [CPA_SCANNER] {msg}")

def emit_new_offers(new_offers: List[CPAOffer]):
    """Emit events for new offers."""
    for offer in new_offers:
        payload = offer.to_dict()
        payload["offer_hash"] = offer.hash()
        emit("new_cpa_offer", payload)
        log(f"Emitted new_cpa_offer: {offer.network}:{offer.offer_id} - {offer.name} ({offer.payout} RUB)")

def run_scan() -> Dict[str, Any]:
    """Run one scan cycle across all networks."""
    log("Starting CPA offer scan...")
    state = load_state()
    known_hashes = set(state.get("known_hashes", []))
    all_offers = load_offers_cache()
    existing_hashes = {o.get("offer_hash", "") for o in all_offers}
    
    new_offers = []
    total_scanned = 0
    
    for network_name, config in NETWORKS.items():
        if not config.get("enabled", True):
            continue
            
        try:
            offers = scan_network(network_name)
            total_scanned += len(offers)
            
            for offer in offers:
                offer_hash = offer.hash()
                
                if offer_hash not in known_hashes and offer_hash not in existing_hashes:
                    new_offers.append(offer)
                    known_hashes.add(offer_hash)
                    existing_hashes.add(offer_hash)
                    
        except Exception as e:
            log(f"Error scanning {network_name}: {e}")
    
    # Emit events for new offers
    if new_offers:
        emit_new_offers(new_offers)
        
        # Update cache
        all_offers.extend([o.to_dict() for o in new_offers])
        save_offers_cache(all_offers)
    
    # Update state
    state["last_scan"] = datetime.now(timezone.utc).isoformat()
    state["known_hashes"] = list(known_hashes)
    state["total_offers"] = len(all_offers)
    state["new_this_scan"] = len(new_offers)
    save_state(state)
    
    log(f"Scan complete: {total_scanned} offers scanned, {len(new_offers)} new")
    
    return {
        "scanned": total_scanned,
        "new": len(new_offers),
        "total_cached": len(all_offers),
    }

def run_daemon(interval_minutes: int = 60):
    """Run as daemon with interval."""
    log(f"CPA Scanner daemon started (interval: {interval_minutes}min)")
    
    # Initial scan
    run_scan()
    
    while True:
        time.sleep(interval_minutes * 60)
        try:
            run_scan()
        except Exception as e:
            log(f"Scan error: {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="CPA Offer Scanner")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=int, default=60, help="Interval in minutes (daemon mode)")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    args = parser.parse_args()
    
    if args.once or not args.daemon:
        result = run_scan()
        print(json.dumps(result, indent=2))
    else:
        run_daemon(args.interval)

if __name__ == "__main__":
    main()