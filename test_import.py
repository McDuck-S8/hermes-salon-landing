import sys
sys.path.insert(0, r"D:\Portable_Soft\hermes\skills\finance\arbitrage-sensors\scripts")
import gap_calculator
print("gap_calculator OK")

import format_short_alert
print("format_short_alert OK")

import send_short_alert
print("send_short_alert OK")

# Test finance_core
sys.path.insert(0, r"D:\Portable_Soft\hermes\scripts")
import finance_core
print("finance_core OK")