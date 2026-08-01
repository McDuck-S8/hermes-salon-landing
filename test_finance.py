import sys
sys.path.insert(0, 'scripts')
from finance_core import get_finance_summary
print("OK")
result = get_finance_summary()
print(result)