import sys
import os
from pathlib import Path

# Exactly as in medium_sensor_run.py
HERMES_HOME = Path(os.environ.get("HERMES_HOME", r"D:\Portable_Soft\hermes"))
CACHE_DIR = HERMES_HOME / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Add all necessary paths
sys.path.insert(0, str(HERMES_HOME / "scripts"))
sys.path.insert(0, str(HERMES_HOME / "skills" / "finance" / "arbitrage-sensors" / "scripts"))
sys.path.insert(0, str(HERMES_HOME / "skills" / "finance" / "finance-core" / "scripts"))

print("HERMES_HOME:", HERMES_HOME)
print("sys.path:")
for p in sys.path[:10]:
    print(f"  {p}")

# Check if the sensor scripts path exists
sensor_path = HERMES_HOME / "skills" / "finance" / "arbitrage-sensors" / "scripts"
print(f"\nSensor path exists: {sensor_path.exists()}")
print(f"Sensor path: {sensor_path}")

# List files in sensor path
if sensor_path.exists():
    for f in sensor_path.iterdir():
        print(f"  {f.name}")

# Try import
try:
    from gap_calculator import calculate_roi
    print("\ngap_calculator import: SUCCESS")
except Exception as e:
    print(f"\ngap_calculator import: FAILED - {e}")