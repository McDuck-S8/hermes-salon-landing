# FAST Sensor Cron Fix — 2026-07-25

## Problem
Cron job `always-on-fast` (schedule `*/30 * * * *`) failed with:
```
ModuleNotFoundError: No module named 'scripts.arbitrage_sensors'
```

Root cause: The script `scripts/always_on_fast_fixed.py` had incorrect imports:
- Used `from scripts.arbitrage_sensors import ...` — module doesn't exist
- `sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))` — fragile path resolution
- `HERMES_HOME` env var not set in cron environment

## Fix Applied
Updated `scripts/always_on_fast_fixed.py` with:

```python
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(HERMES_HOME / "scripts"))

ARBITRAGE_SENSORS = HERMES_HOME / "skills" / "finance" / "arbitrage-sensors" / "scripts"
sys.path.insert(0, str(ARBITRAGE_SENSORS))

from gap_calculator import MOCK_TRAFFIC_COSTS, CPAOffer, TrafficCost, calculate_roi, find_matching_traffic, ROI_THRESHOLD, MIN_PAYOUT, MAX_CPC
```

Also rewrote sensor logic to match the working `fast_sensor_run_fixed.py` (root script):
- Load offers from `cache/cpa_offers.json`
- Calculate gaps using `gap_calculator` logic
- Score using 0-100 formula: `Impact(0-10) * Urgency(0-10) * Confidence(0-10) / 10`
- Thresholds: ≥70 CRITICAL, ≥50 HIGH, ≥30 MEDIUM, ≥10 LOW
- Plain-text Telegram format (no markdown, decimal points → `p`)

## Verification
```bash
cd /d/Portable_Soft/hermes && python scripts/always_on_fast_fixed.py
# Exit code 0, outputs 1 CRITICAL alert (Raid Shadow Legends + RichAds RU gaming, score 70)
```

## Key Lessons for Cron Scripts
1. **Always provide HERMES_HOME fallback** — cron doesn't inherit shell env
2. **Import from skill scripts directory** — not from imaginary `scripts.<skill>` modules
3. **Align scoring with skill spec** — FAST sensor must use 0-100 scale matching MEDIUM sensor
4. **Telegram format** — plain text, `< 8 lines`, no `$` or `|` tables (Exfil-Guard blocks)