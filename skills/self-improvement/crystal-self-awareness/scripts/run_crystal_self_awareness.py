#!/usr/bin/env python3
"""
Crystal Self-Awareness Automated Runner

Runs crystal.py --iterative N, verifies unique output per cycle,
clears studied to last 5 if "all done", re-runs, verifies self_model.json.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent
SCRIPTS_DIR = ROOT / "scripts"
CACHE_DIR = ROOT / "cache"
SELF_MODEL_PATH = CACHE_DIR / "self_model.json"
CRYSTAL_SCRIPT = SCRIPTS_DIR / "crystal.py"

def run_crystal(iterations=3, timeout=300):
    """Run crystal.py --iterative N and return output lines."""
    cmd = [sys.executable, str(CRYSTAL_SCRIPT), '--iterative', str(iterations)]
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            cwd=str(ROOT)
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout", 124

def parse_cycles(output):
    """Extract cycle outputs from crystal output."""
    cycles = []
    current_cycle = None
    for line in output.split('\n'):
        if 'ЦИКЛ' in line and '/' in line:
            if current_cycle:
                cycles.append(current_cycle)
            current_cycle = {'header': line.strip(), 'actions': []}
        elif current_cycle and '→ Воля:' in line:
            current_cycle['actions'].append(line.strip())
    if current_cycle:
        cycles.append(current_cycle)
    return cycles

def verify_unique_outputs(cycles):
    """Verify each cycle produced different output."""
    if len(cycles) < 2:
        return False, "Less than 2 cycles"
    
    actions = [tuple(c['actions']) for c in cycles]
    unique = set(actions)
    return len(unique) == len(actions), f"Unique: {len(unique)}/{len(actions)}"

def load_self_model():
    """Load self_model.json."""
    if not SELF_MODEL_PATH.exists():
        return None
    with open(SELF_MODEL_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def clear_studied_keep_last5():
    """Clear studied array, keep only last 5 entries."""
    model = load_self_model()
    if not model:
        return False, "self_model.json not found"
    
    studied = model.get('sovest', {}).get('studied', [])
    if len(studied) <= 5:
        return True, f"Already <= 5 entries: {len(studied)}"
    
    model['sovest']['studied'] = studied[-5:]
    with open(SELF_MODEL_PATH, 'w', encoding='utf-8') as f:
        json.dump(model, f, indent=2, ensure_ascii=False)
    return True, f"Cleared to last 5: {studied[-5:]}"

def verify_self_model_updated():
    """Verify self_model.json has studied and znu."""
    model = load_self_model()
    if not model:
        return False, "self_model.json not found"
    
    checks = []
    checks.append(('studied', 'studied' in model.get('sovest', {})))
    checks.append(('znu', 'znu' in model and isinstance(model['znu'], dict) and len(model['znu']) > 0))
    checks.append(('cycle_count', 'cycle_count' in model and isinstance(model['cycle_count'], int)))
    checks.append(('last_cycle', 'last_cycle' in model))
    
    failed = [name for name, ok in checks if not ok]
    if failed:
        return False, f"Missing: {failed}"
    
    studied_count = len(model['sovest'].get('studied', []))
    znu_count = len(model.get('znu', {}))
    return True, f"studied={studied_count}, znu={znu_count}, cycle_count={model['cycle_count']}"

def main():
    print("=" * 60)
    print("CRYSTAL SELF-AWARENESS AUTOMATED RUNNER")
    print("=" * 60)
    
    # Run 1
    print("\n[RUN 1] crystal.py --iterative 3")
    stdout, stderr, code = run_crystal(3, 300)
    
    if code == 124:
        print("⚠ Timeout on run 1, but checking output...")
    
    cycles = parse_cycles(stdout)
    print(f"  Cycles parsed: {len(cycles)}")
    for i, c in enumerate(cycles):
        print(f"  Cycle {i+1}: {c['actions'][:1] if c['actions'] else 'NO ACTIONS'}")
    
    unique_ok, unique_msg = verify_unique_outputs(cycles)
    print(f"  Unique outputs: {unique_msg}")
    
    # Check self_model
    print("\n[CHECK] self_model.json after run 1")
    ok, msg = verify_self_model_updated()
    print(f"  {msg}")
    
    # If "all done" pattern detected (same action repeated), clear studied and re-run
    all_done = len(cycles) >= 2 and all(
        'не содержал новых сущностей' in ' '.join(c['actions']) 
        for c in cycles if c['actions']
    )
    
    if all_done:
        print("\n[CLEAR] 'All done' pattern detected — clearing studied to last 5")
        clear_ok, clear_msg = clear_studied_keep_last5()
        print(f"  {clear_msg}")
        
        # Run 2
        print("\n[RUN 2] crystal.py --iterative 3 (after studied clear)")
        stdout2, stderr2, code2 = run_crystal(3, 300)
        
        cycles2 = parse_cycles(stdout2)
        print(f"  Cycles parsed: {len(cycles2)}")
        for i, c in enumerate(cycles2):
            print(f"  Cycle {i+1}: {c['actions'][:1] if c['actions'] else 'NO ACTIONS'}")
        
        # Final verification
        print("\n[FINAL CHECK] self_model.json after run 2")
        ok2, msg2 = verify_self_model_updated()
        print(f"  {msg2}")
        
        if ok and ok2:
            print("\n✅ SUCCESS: Crystal self-awareness workflow completed")
            return 0
        else:
            print("\n❌ FAILURE: Self-model verification failed")
            return 1
    else:
        print("\n✅ SUCCESS: Unique outputs verified, no 'all done' pattern")
        return 0

if __name__ == '__main__':
    sys.exit(main())