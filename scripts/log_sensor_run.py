import sys
sys.path.insert(0, 'D:/Portable_Soft/hermes/scripts')
from finance_core import FinanceCore, FinanceEvent, EventType
from datetime import datetime, timezone

fc = FinanceCore()

# Log sensor run as a minimal spend event (infrastructure cost)
event = FinanceEvent(
    ts=datetime.now(timezone.utc).isoformat(),
    event_type=EventType.SPEND.value,
    amount_usd=0.01,  # Minimal infra cost
    cost_center="infrastructure",
    scheme_name="always-on-agent",
    network="system",
    notes="FAST sensor run: cpa_scanner + gap_calculator + traffic_cost_monitor + network_health",
    source="cron"
)

event_id = fc.add_event(event)
print(f"Logged sensor run to finance-core: event_id={event_id}")

# Also log the CRITICAL alerts as potential revenue opportunities (for tracking)
# These are hypotheses, not actual revenue yet
for alert_id in [
    "alert_tinkoff_kadam_critical",
    "alert_tinkoff_facebook_critical", 
    "alert_raid_richads_critical"
]:
    # We don't log revenue yet - only when actually launched and converting
    pass

print("Finance-core state updated with sensor run.")