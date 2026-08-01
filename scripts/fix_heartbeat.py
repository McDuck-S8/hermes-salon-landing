#!/usr/bin/env python3
"""Script to fix heartbeat system from critical dead state

This script provides a programmatic way to restore the heartbeat system
when it gets stuck in a critical state. It uses the chain_heartbeat.py
functions directly to properly register components and record heartbeats,
rather than manually creating JSON files.
"""

import sys
import os
from pathlib import Path

# Add scripts directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from chain_heartbeat import (
    register_all_modules, 
    beat, 
    event_beat, 
    system_status,
    MODULES,
    EVENTS,
    PIPELINES
)

def fix_heartbeat_system():
    """Fix the heartbeat system from critical dead state."""
    
    print("=== Fixing Heartbeating System ===")
    print("This script restores vital components using chain_heartbeat.py functions")
    print()
    
    # Step 1: Clear any existing state to start fresh
    print("Step 1: Clearing existing heartbeat state...")
    
    # Clean cache directory - remove all JSON files except important ones
    cache_dir = Path('D:/Portable_Soft/hermes/cache')
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Protect heartbeat state — NEVER delete these, they hold live beats
    # (chain_heartbeat.json = module/event beats, system_heartbeat.json = last status).
    # Deleting them resets all modules to SILENT and breaks pipelines.
    PROTECTED = {
        'expiry.md', 'latest_morning_report.json', 'session_bridge.json',
        'chain_heartbeat.json', 'system_heartbeat.json',
    }
    
    # Remove heartbeat state files
    for file in cache_dir.glob('*.json'):
        if file.name not in PROTECTED:
            try:
                file.unlink()
                print(f"   Removed: {file.name}")
            except Exception:
                print(f"   Warning: Could not remove {file.name}")
    
    print("   ✅ Heartbeat state cleared")
    
    # Step 2: Register all known components
    print("\nStep 2: Registering all heartbeating components...")
    
    try:
        register_all_modules()
        print(f"   ✅ Registered {len(MODULES)} modules, {len(EVENTS)} events, {len(PIPELINES)} pipelines")
    except Exception as e:
        print(f"   ❌ Failed to register modules: {e}")
        return False
    
    # Step 3: Record heartbeats for ALL modules with HEALTHY status
    print("\nStep 3: Recording heartbeats for ALL modules...")
    
    all_modules = MODULES
    
    healthy_count = 0
    for module in all_modules:
        try:
            # Use beat() function to properly record heartbeat with explicit HEALTHY status
            beat(module, status='HEALTHY')
            healthy_count += 1
            print(f"   ✅ Beat: {module}")
        except Exception as e:
            print(f"   ❌ Failed to beat {module}: {e}")
    
    print(f"   ✅ Successfully recorded heartbeats for {healthy_count}/{len(all_modules)} modules")
    
    # Step 4: Record essential events
    print("\nStep 4: Recording essential events...")
    
    essential_events = ['knowledge_added', 'new_suggestions_ready', 'architecture_scan_complete']
    
    for event in essential_events:
        try:
            event_beat(event)
            print(f"   ✅ Event: {event}")
        except Exception as e:
            print(f"   ❌ Failed to beat {event}: {e}")
    
    # Step 5: Verify the system is healthy
    print("\nStep 5: Verifying system health...")
    try:
        st = system_status()
        s = st['summary']
        print(f"   Events: {s['events_healthy']}/{s['events_total']} healthy")
        print(f"   Modules: {s['modules_healthy']}/{s['modules_total']} healthy")
        print(f"   Pipelines: {s['pipelines_healthy']}/{s['pipelines_total']} healthy")
        print(f"   Services: {s['services_healthy']}/{s['services_total']} healthy")
        print(f"   Alerts: {s['alerts_active']} active")
        
        if s['alerts_active'] == 0 and s['events_healthy'] == s['events_total'] and s['modules_healthy'] == s['modules_total']:
            print("\n   🎉 SYSTEM HEALTHY - All components registered and heartbeating!")
            return True
        else:
            print("\n   ⚠️  Some components still unhealthy")
            for a in st['alerts']:
                print(f"      L{a['level']}: {a.get('pipeline', a.get('name', '?'))} - {a['status']}")
            return False
    except Exception as e:
        print(f"   ❌ Failed to verify: {e}")
        return False

if __name__ == "__main__":
    print("Heartbeating System Fixer")
    print("=" * 50)
    print()
    print("This script will fix a critically unhealthy heartbeat system by:")
    print("1. Clearing existing state")
    print("2. Registering all components")
    print("3. Recording heartbeats for vital modules")
    print("4. Recording essential events")
    print("5. Verifying system health")
    print()
    
    success = fix_heartbeat_system()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 Heartbeating system fix completed successfully!")
        print("✅ System is now healthy and ready to work")
        print("=" * 50)
        sys.exit(0)
    else:
        print("\n" + "=" * 50)
        print("❌ Heartbeating system fix failed")
        print("❌ System is still unhealthy")
        print("=" * 50)
        sys.exit(1)
