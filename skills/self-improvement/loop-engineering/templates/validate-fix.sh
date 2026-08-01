#!/usr/bin/env bash
# validate-fix.sh — Deterministic validation template
# Usage: ./scripts/validate-fix.sh <scheme_name>

set -euo pipefail

SCHEME_NAME="${1:-}"
if [[ -z "$SCHEME_NAME" ]]; then
    echo "FAIL: scheme name required"
    exit 1
fi

HERMES_HOME="D:/Portable_Soft/hermes"
WORKSHOP="$HERMES_HOME/ARBITRAGE_WORKSHOP.md"
LOG_FILE="$HERMES_HOME/ARBITRAGE_LOG.md"

echo "=== VALIDATING: $SCHEME_NAME ==="

# 1. Check scheme exists in Workshop with ЦА template
if ! grep -q "СХЕМА: $SCHEME_NAME" "$WORKSHOP" 2>/dev/null; then
    echo "FAIL: Scheme $SCHEME_NAME not found in Workshop"
    exit 1
fi

# 2. Check ЦА template filled
if ! grep -A 20 "СХЕМА: $SCHEME_NAME" "$WORKSHOP" | grep -q "ЦА:"; then
    echo "FAIL: ЦА template not filled for $SCHEME_NAME"
    exit 1
fi

# 3. Check finance core has scheme data
if ! python -c "
import sys
sys.path.insert(0, '$HERMES_HOME/scripts')
from finance_core import FinanceCore
fc = FinanceCore()
schemes = fc.get_scheme_economics()
found = any(s['scheme_name'] == '$SCHEME_NAME' for s in schemes)
sys.exit(0 if found else 1)
" 2>/dev/null; then
    echo "FAIL: Scheme $SCHEME_NAME not tracked in finance core"
    exit 1
fi

# 4. Check revenue recorded
REVENUE=$(python -c "
import sys
sys.path.insert(0, '$HERMES_HOME/scripts')
from finance_core import FinanceCore
fc = FinanceCore()
schemes = fc.get_scheme_economics()
for s in schemes:
    if s['scheme_name'] == '$SCHEME_NAME':
        print(s['total_revenue_usd'])
        break
" 2>/dev/null || echo "0")

if python -c "import sys; sys.exit(0 if float('$REVENUE') >= 1 else 1)" 2>/dev/null; then
    : # OK
else
    echo "FAIL: No revenue recorded for $SCHEME_NAME (revenue: \$$REVENUE)"
    exit 1
fi

# 5. Check withdrawal path tested
WITHDRAWN=$(python -c "
import sys
sys.path.insert(0, '$HERMES_HOME/scripts')
from finance_core import FinanceCore
fc = FinanceCore()
pending = fc.get_pending_withdrawals()
count = sum(1 for w in pending if w.get('scheme_name') == '$SCHEME_NAME' and w.get('event_type') == 'withdrawal_received' and w.get('status') == 'confirmed')
print(count)
" 2>/dev/null || echo "0")

if python -c "import sys; sys.exit(0 if int('$WITHDRAWN') >= 1 else 1)" 2>/dev/null; then
    : # OK
else
    echo "FAIL: No confirmed withdrawal for $SCHEME_NAME"
    exit 1
fi

# 6. Check tax liability manageable
TAX_PENDING=$(python -c "
import sys
sys.path.insert(0, '$HERMES_HOME/scripts')
from finance_core import FinanceCore
fc = FinanceCore()
tax = fc.get_tax_liability()
print(tax['pending_usd'])
" 2>/dev/null || echo "0")

if python -c "import sys; sys.exit(0 if float('$TAX_PENDING') <= 500 else 1)" 2>/dev/null; then
    : # OK
else
    echo "FAIL: Tax liability too high (\$$TAX_PENDING)"
    exit 1
fi

# 7. Check no critical errors in recent logs
if grep -q "ERROR.*$SCHEME_NAME" "$HERMES_HOME/logs/autonomous_agent.log" 2>/dev/null | tail -20; then
    echo "FAIL: Critical errors found in logs for $SCHEME_NAME"
    exit 1
fi

echo "=== PASS: $SCHEME_NAME ==="
echo "Revenue: \$$REVENUE"
echo "Withdrawals confirmed: $WITHDRAWN"
echo "Tax pending: \$$TAX_PENDING"
exit 0