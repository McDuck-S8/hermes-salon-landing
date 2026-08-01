import sys
sys.path.insert(0, '/d/Portable_Soft/hermes/scripts')
from finance_core import FinanceCore, get_finance_summary
import json

fc = FinanceCore()
summary = get_finance_summary()
print(json.dumps(summary, indent=2, ensure_ascii=False))