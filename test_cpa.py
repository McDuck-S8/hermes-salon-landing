import sys
sys.path.insert(0, 'skills/finance/arbitrage-sensors/scripts')
from cpa_scanner import run_scan
result = run_scan()
print(result)