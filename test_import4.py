import sys
import os
from pathlib import Path

# Fix for Windows path resolution - use os.path instead of Path.resolve()
HERMES_HOME = os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes")
# Ensure it's a proper path with drive letter
if not os.path.isabs(HERMES_HOME):
    HERMES_HOME = os.path.abspath(HERMES_HOME)
HERMES_HOME = os.path.normpath(HERMES_HOME)

print(f"HERMES_HOME (fixed): {HERMES_HOME}")

CACHE_DIR = os.path.join(HERMES_HOME, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Add all necessary paths
paths_to_add = [
    os.path.join(HERMES_HOME, "scripts"),
    os.path.join(HERMES_HOME, "skills", "finance", "arbitrage-sensors", "scripts"),
    os.path.join(HERMES_HOME, "skills", "finance", "finance-core", "scripts"),
]

for p in paths_to_add:
    p_norm = os.path.normpath(p)
    if p_norm not in sys.path:
        sys.path.insert(0, p_norm)
    print(f"Added to sys.path: {p_norm}")

print("\nsys.path (first 10):")
for p in sys.path[:10]:
    print(f"  {p}")

# Check if the sensor scripts path exists
sensor_path = os.path.join(HERMES_HOME, "skills", "finance", "arbitrage-sensors", "scripts")
print(f"\nSensor path exists: {os.path.exists(sensor_path)}")
print(f"Sensor path: {sensor_path}")

if os.path.exists(sensor_path):
    for f in os.listdir(sensor_path):
        print(f"  {f}")

# Try import
try:
    from gap_calculator import calculate_roi
    print("\ngap_calculator import: SUCCESS")
except Exception as e:
    print(f"\ngap_calculator import: FAILED - {e}")

try:
    from format_short_alert import format_alert
    print("format_short_alert import: SUCCESS")
except Exception as e:
    print(f"format_short_alert import: FAILED - {e}")

try:
    from send_short_alert import send_alert
    print("send_short_alert import: SUCCESS")
except Exception as e:
    print(f"send_short_alert import: FAILED - {e}")

try:
    from finance_core import get_finance_summary
    print("finance_core import: SUCCESS")
except Exception as e:
    print(f"finance_core import: FAILED - {e}")