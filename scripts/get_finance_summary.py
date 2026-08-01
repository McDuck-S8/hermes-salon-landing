import sys
sys.path.insert(0, 'D:/Portable_Soft/hermes/scripts')
from finance_core import get_finance_summary
import json
summary = get_finance_summary()
print(json.dumps(summary, indent=2, default=str))