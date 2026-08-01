import sys
sys.path.insert(0, 'skills/finance/arbitrage-sensors/scripts')
from gap_calculator import run_calculation
result = run_calculation()
import json
print(json.dumps(result, indent=2))