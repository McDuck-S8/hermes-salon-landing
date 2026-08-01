import sys
sys.path.insert(0, 'scripts')
import finance_core
print('OK')
fc = finance_core.FinanceCore()
print(fc.get_pnl(30))