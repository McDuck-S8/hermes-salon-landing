import sys
sys.path.insert(0, 'scripts')
from chain_heartbeat import system_status
s = system_status()
print(f"Events: {s['summary']['events_healthy']}/{s['summary']['events_total']}")
print(f"Modules: {s['summary']['modules_healthy']}/{s['summary']['modules_total']}")
print(f"Services: {s['summary']['services_healthy']}/{s['summary']['services_total']}")
if 'events' in s:
    for e in s['events']:
        print(f"  {e['name']}: {e['status']} (last: {e['last_ts']})")
if 'modules' in s:
    for m in s['modules']:
        print(f"  {m['name']}: {m['status']}")
if 'services' in s:
    for svc in s['services']:
        print(f"  {svc['name']}: {svc['status']}")