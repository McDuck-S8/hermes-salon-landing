#!/usr/bin/env python3
"""
Test fast sensor run with correct path setup
"""
import sys
import os
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path(__file__).resolve().parent))
print(f"HERMES_HOME: {HERMES_HOME}")

sys.path.insert(0, str(HERMES_HOME / "scripts"))
print(f"sys.path[0]: {sys.path[0]}")

# Import finance_core
from finance_core import FinanceCore, get_finance_summary
print("finance_core imported OK")

# Import gap_calculator
ARBITRAGE_SENSORS = HERMES_HOME / "skills" / "finance" / "arbitrage-sensors" / "scripts"
print(f"ARBITRAGE_SENSORS: {ARBITRAGE_SENSORS}")
sys.path.insert(0, str(ARBITRAGE_SENSORS))

from gap_calculator import MOCK_TRAFFIC_COSTS, CPAOffer, TrafficCost, calculate_roi, find_matching_traffic, ROI_THRESHOLD, MIN_PAYOUT, MAX_CPC
print("gap_calculator imported OK")

print("All imports successful!")