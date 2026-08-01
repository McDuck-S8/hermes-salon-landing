#!/usr/bin/env python3
"""
Verification script for fractal-knowledge-wheel skill.
Run after any changes to ensure both modes work correctly.
"""

import sys
sys.path.insert(0, 'D:/d/Portable_Soft/hermes/skills/arbitrage/fractal-knowledge-wheel/scripts')

from fractal_wheel import FractalWheel, KnowledgeSource, SynthesisEngine
from pathlib import Path
import json


def test_analysis_mode():
    """Test Режим 1: Анализ"""
    print("=" * 50)
    print("TEST: Analysis Mode")
    print("=" * 50)
    
    wheel = FractalWheel(
        center="PWA-арбитраж беттинга на Индию",
        domain="arbitrage"
    )
    
    assessment = wheel.run_analysis_mode()
    
    assert len(assessment.sectors) == 8, f"Expected 8 sectors, got {len(assessment.sectors)}"
    assert assessment.overall_percent == 56, f"Expected 56%, got {assessment.overall_percent}%"
    assert len(assessment.green_sectors) == 4
    assert len(assessment.yellow_sectors) == 2
    assert len(assessment.red_sectors) == 2
    assert len(assessment.critical_red_sectors) == 1
    assert len(assessment.priority_tasks) == 4
    assert assessment.priority_tasks[0]["priority"] == "critical"
    assert assessment.priority_tasks[0]["sector_name"] == "Креативы"
    assert assessment.priority_tasks[1]["priority"] == "high"
    assert assessment.priority_tasks[1]["sector_name"] == "Масштабирование"
    
    print(f"  ✅ 8 sectors built")
    print(f"  ✅ Overall: {assessment.overall_percent}%")
    print(f"  ✅ Green: {len(assessment.green_sectors)}, Yellow: {len(assessment.yellow_sectors)}, Red: {len(assessment.red_sectors)}")
    print(f"  ✅ Priority tasks: {len(assessment.priority_tasks)} (critical→high→medium)")
    print(f"  ✅ Analysis mode: PASS")


def test_synthesis_mode():
    """Test Режим 2: Синтез"""
    print("\n" + "=" * 50)
    print("TEST: Synthesis Mode")
    print("=" * 50)
    
    wheel = FractalWheel(
        center="Test concept",
        domain="arbitrage"
    )
    
    novel_keys = wheel.run_synthesis_mode(days=7)
    
    assert len(novel_keys) >= 10, f"Expected at least 10 novel keys, got {len(novel_keys)}"
    
    # Check first key structure
    k = novel_keys[0]
    assert "→" in k.name, f"Key name should contain arrows: {k.name}"
    assert 0 <= k.compatibility_score <= 1
    assert 0 <= k.novelty_score <= 1
    assert len(k.description) > 0
    assert len(k.reasoning) > 0
    assert "traffic" in k.components
    assert "bridge" in k.components
    assert "offer" in k.components
    assert "geo" in k.components
    assert "payment" in k.components
    assert "withdrawal" in k.components
    
    # Check sorting: compatibility * novelty descending
    for i in range(len(novel_keys) - 1):
        curr = novel_keys[i].compatibility_score * novel_keys[i].novelty_score
        nxt = novel_keys[i+1].compatibility_score * novel_keys[i+1].novelty_score
        assert curr >= nxt, f"Keys not sorted by score: {curr} < {nxt}"
    
    print(f"  ✅ {len(novel_keys)} novel keys synthesized")
    print(f"  ✅ Top key: {novel_keys[0].name}")
    print(f"  ✅ Compatibility: {novel_keys[0].compatibility_score:.0%}, Novelty: {novel_keys[0].novelty_score:.0%}")
    print(f"  ✅ Keys sorted by compatibility*novelty")
    print(f"  ✅ Synthesis mode: PASS")


def test_domains():
    """Test different domains"""
    print("\n" + "=" * 50)
    print("TEST: Domain Support")
    print("=" * 50)
    
    for domain in ["arbitrage", "ai-ofm", "craft", "default"]:
        wheel = FractalWheel(center="Test", domain=domain)
        sectors = wheel.build_wheel()
        assert len(sectors) >= 6, f"Domain {domain} has only {len(sectors)} sectors"
        print(f"  ✅ {domain}: {len(sectors)} sectors")
    
    print(f"  ✅ All domains supported")


def test_knowledge_source():
    """Test KnowledgeSource integration"""
    print("\n" + "=" * 50)
    print("TEST: KnowledgeSource Integration")
    print("=" * 50)
    
    ks = KnowledgeSource()
    findings = ks.get_recent_findings(days=7)
    
    assert len(findings) > 0, "No findings from knowledge cube"
    
    # Check structure
    f = findings[0]
    required = ["id", "content", "tags", "source", "category", "importance", "created_at", "type"]
    for field in required:
        assert field in f, f"Missing field {field} in finding"
    
    # Check we have both kc_entries and experiences
    types = {f["type"] for f in findings}
    assert "kc_entry" in types
    assert "experience" in types
    
    print(f"  ✅ {len(findings)} findings from last 7 days")
    print(f"  ✅ Types: {types}")
    print(f"  ✅ KnowledgeSource: PASS")


def test_entity_extraction():
    """Test entity extraction from real findings"""
    print("\n" + "=" * 50)
    print("TEST: Entity Extraction")
    print("=" * 50)
    
    ks = KnowledgeSource()
    findings = ks.get_recent_findings(days=7)
    
    engine = SynthesisEngine(ks)
    entities = engine.extract_entities(findings)
    
    expected_types = ["traffic", "offer", "payment", "withdrawal", "geo", "bridge", "tool"]
    for etype in expected_types:
        assert etype in entities, f"Missing entity type: {etype}"
    
    # Check we have meaningful entities
    assert len(entities["traffic"]) >= 10
    assert len(entities["offer"]) >= 5
    assert len(entities["payment"]) >= 3
    assert len(entities["geo"]) >= 1
    
    print(f"  ✅ Entity types: {list(entities.keys())}")
    for etype, ents in entities.items():
        print(f"     {etype}: {len(ents)} entities")
    print(f"  ✅ Entity extraction: PASS")


def test_cli_compatibility():
    """Test that the module can be run as script"""
    print("\n" + "=" * 50)
    print("TEST: CLI Compatibility")
    print("=" * 50)
    
    import subprocess
    
    # Test analysis mode
    result = subprocess.run([
        sys.executable,
        "D:/d/Portable_Soft/hermes/skills/arbitrage/fractal-knowledge-wheel/scripts/fractal_wheel.py",
        "Test concept", "arbitrage", "analysis"
    ], capture_output=True, text=True, cwd="D:/d/Portable_Soft/hermes", timeout=30)
    
    assert result.returncode == 0, f"CLI analysis failed: {result.stderr}"
    assert "ANALYSIS" in result.stdout
    assert "Overall:" in result.stdout
    
    # Test synthesis mode
    result = subprocess.run([
        sys.executable,
        "D:/d/Portable_Soft/hermes/skills/arbitrage/fractal-knowledge-wheel/scripts/fractal_wheel.py",
        "Test concept", "arbitrage", "synthesis"
    ], capture_output=True, text=True, cwd="D:/d/Portable_Soft/hermes", timeout=30)
    
    assert result.returncode == 0, f"CLI synthesis failed: {result.stderr}"
    assert "SYNTHESIS" in result.stdout
    assert "novel keys" in result.stdout
    
    print(f"  ✅ CLI analysis mode works")
    print(f"  ✅ CLI synthesis mode works")
    print(f"  ✅ CLI compatibility: PASS")


def run_all_tests():
    """Run all verification tests"""
    print("\n" + "🔍 " + "FRACTAL KNOWLEDGE WHEEL - VERIFICATION SUITE")
    print("=" * 60)
    
    test_analysis_mode()
    test_synthesis_mode()
    test_domains()
    test_knowledge_source()
    test_entity_extraction()
    test_cli_compatibility()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        run_all_tests()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)