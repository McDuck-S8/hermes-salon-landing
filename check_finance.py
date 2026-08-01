from scripts.finance_core import FinanceCore, get_finance_summary

fc = FinanceCore()
summary = get_finance_summary()
print('USD Rate:', summary.get('usd_rate', 'N/A'))
print('P&L 30d:', summary.get('pnl_30d', {}))
print('Schemes:', summary.get('schemes', []))
print('Tax:', summary.get('tax', {}))
print('Pending Withdrawals:', summary.get('pending_withdrawals', []))