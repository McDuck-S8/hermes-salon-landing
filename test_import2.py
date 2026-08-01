import sys
import os
from pathlib import Path

# Force correct paths
HERMES_HOME = Path(r"D:\Portable_Soft\hermes")
SENSORS_SCRIPTS = HERMES_HOME / "skills" / "finance" / "arbitrage-sensors" / "scripts"
FINANCE_CORE_SCRIPTS = HERMES_HOME / "skills" / "finance" / "finance-core" / "scripts"
MAIN_SCRIPTS = HERMES_HOME / "scripts"

for p in [MAIN_SCRIPTS, SENSORS_SCRIPTS, FINANCE_CORE_SCRIPTS]:
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)
    print(f"Added to sys.path: {p_str}")

# Test imports
try:
    from gap_calculator import calculate_roi, CPAOffer, TrafficCost
    print("gap_calculator OK")
except Exception as e:
    print(f"gap_calculator FAILED: {e}")

try:
    from format_short_alert import format_alert, format_alert_high
    print("format_short_alert OK")
except Exception as e:
    print(f"format_short_alert FAILED: {e}")

try:
    from send_short_alert import send_alert
    print("send_short_alert OK")
except Exception as e:
    print(f"send_short_alert FAILED: {e}")

try:
    from finance_core import get_finance_summary
    print("finance_core OK")
except Exception as e:
    print(f"finance_core FAILED: {e}")