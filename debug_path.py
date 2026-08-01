import sys
import os
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path("D:/Portable_Soft/hermes")))
scripts_path = HERMES_HOME / "scripts"
finance_core = scripts_path / "finance_core.py"

print(f"HERMES_HOME: {HERMES_HOME}")
print(f"scripts_path: {scripts_path}")
print(f"scripts_path exists: {scripts_path.exists()}")
print(f"finance_core: {finance_core}")
print(f"finance_core exists: {finance_core.exists()}")

sys.path.insert(0, str(scripts_path))
print(f"sys.path[0]: {sys.path[0]}")

try:
    from finance_core import get_finance_summary
    print("OK - imported successfully")
except ImportError as e:
    print(f"Import error: {e}")
    print(f"sys.path: {sys.path[:3]}")