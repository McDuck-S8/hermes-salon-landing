#!/usr/bin/env python3
"""
Ripple Engine Test Script — Standalone test for human-source conflict detection.
Run: python skills/human-source/scripts/test_ripple.py
"""

import sys
from pathlib import Path

# Add skills to path
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR))

from human_source.scripts.analyze import HumanAnalyzer, Key, RippleCircle, ValueConflict

def test_ripple_engine():
    """Test ripple engine with various keys against user's values map."""
    
    config = {
        'analysis': {'dimensions': {'frustrations': 0.3, 'sins': 0.2, 'norms': 0.2, 'strengths': 0.15, 'context': 0.15}},
        'ripple_engine': {'max_depth': 3, 'conflict_threshold': 0.7, 'stop_on_conflict': True},
    }
    
    analyzer = HumanAnalyzer(config)
    
    # User's values map (from session analysis)
    values_map = {
        'deep_zones': [
            {'name': 'Technical Mastery', 'depth': 'deep'},
            {'name': 'Autonomous Execution', 'depth': 'deep'},
        ],
        'shallow_zones': [
            {'name': 'Agent Passivity', 'depth': 'shallow'},
        ],
        'underwater_rocks': [
            {'name': 'No KYC / No Documents', 'type': 'hard_constraint'},
            {'name': 'No Risk / Stability', 'type': 'value'},
            {'name': 'Stdlib-First / No Heavy Frameworks', 'type': 'value'},
            {'name': 'Clickable Artifacts Only', 'type': 'value'},
            {'name': 'Passive Autonomy', 'type': 'value'},
            {'name': 'Crimea Constraints', 'type': 'environmental'},
        ]
    }
    
    test_keys = [
        "PWA-арбитраж на Индию",
        "Автономная система поиска работы в Крыму без KYC",
        "Полностью автономный контент-конвейер для Shorts/TikTok без участия человека",
        "USDT→RUB off-ramp автоматизация без KYC через P2P/Whitebird",
        "Автономные агенты для мониторинга и исправления сломанных кронов/демонов",
        "Матричный арбитраж-движок: не линейные цепочки, а сетка альтернатив с авто-переключением",
        "AI OFM Tribute Channel",
    ]
    
    print("="*70)
    print("RIPPLE ENGINE TEST — Conflict Detection")
    print("="*70)
    
    all_passed = True
    
    for key_text in test_keys:
        key = Key(
            text=key_text,
            source_dimension="test",
            rationale="Test key"
        )
        analyzer._run_ripple_engine(key, values_map)
        
        status = "✅ PASS" if key.status == 'validated' else "❌ REJECTED"
        print(f"\n{status} | {key_text}")
        print(f"   Circles: {len(key.circles)}, Conflicts: {len(key.conflicts)}")
        
        for circle in key.circles:
            if circle.conflicts:
                for c in circle.conflicts:
                    sev = "🔴" if c.severity == 'critical' else "🟡"
                    print(f"   {sev} Circle {circle.depth} ({circle.name}): {c.violated_value} — {c.aspect}")
        
        if key.replacement:
            print(f"   🔄 Replacement: {key.replacement}")
    
    print("\n" + "="*70)
    print("EXPECTED RESULTS:")
    print("  PWA-арбитраж на Индию          → REJECTED (2 critical: No KYC)")
    print("  Job search Crimea              → VALIDATED (0 conflicts)")
    print("  Content pipeline Shorts        → VALIDATED (0 conflicts)")
    print("  USDT→RUB off-ramp              → VALIDATED (0 conflicts)")
    print("  Cron monitoring agents         → VALIDATED (0 conflicts)")
    print("  Matrix arbitrage engine        → VALIDATED (0 conflicts)")
    print("  AI OFM Tribute                 → VALIDATED (0 conflicts)")
    print("="*70)
    
    return all_passed

if __name__ == "__main__":
    test_ripple_engine()