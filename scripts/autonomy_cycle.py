#!/usr/bin/env python3
"""
Autonomy Cycle Cron Job — runs every 30 minutes

Executes full autonomy cycle:
1. Check knowledge gaps
2. External import if needed
3. Conflict resolution
4. Pattern promotion/merger
5. Archival cleanup
6. Heartbeat event
"""

import sys
import os

# Add scripts to path
HERMES_HOME = os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes")
sys.path.insert(0, os.path.join(HERMES_HOME, "scripts"))

from autonomy.autonomy_core import AutonomyCore


def main():
    core = AutonomyCore()
    result = core.run_cycle()
    
    # Print summary
    print(f"=== AUTONOMY CYCLE #{result['cycle']} ===")
    print(f"Duration: {result['duration_ms']}ms")
    print(f"Steps: {list(result['steps'].keys())}")
    
    if result.get("error"):
        print(f"ERROR: {result['error']}")
        sys.exit(1)
    
    # Check critical steps
    if not result.get("heartbeat_fired"):
        print("WARNING: Heartbeat not fired")
        sys.exit(1)
    
    print("SUCCESS: Autonomy cycle complete")
    sys.exit(0)


if __name__ == "__main__":
    main()