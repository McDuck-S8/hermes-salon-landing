from scripts.finance_core import FinanceCore, FinanceEvent, EventType
fc = FinanceCore()
fc.add_event(FinanceEvent(
    event_type=EventType.SPEND.value,
    amount_usd=0.0,
    cost_center='other',
    scheme_name='always-on-agent',
    network='system',
    notes='FAST sensor run: gap_calculator processed 6 offers, found 4 CRITICAL (mock), 1 HIGH, 1 MEDIUM. Traffic cost monitor and network health not implemented.',
    source='always_on_agent'
))
print('Logged sensor run to finance_core')