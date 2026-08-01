#!/usr/bin/env python3
"""
Test script for Bandwidth Sharing Launcher
Verifies the launcher can be imported and basic functions work.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """Test importing the launcher module."""
    try:
        from bandwidth_launcher import BandwidthLauncher, BandwidthApp
        print("✓ Successfully imported BandwidthLauncher")
        return True
    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        return False

def test_config():
    """Test loading configuration."""
    try:
        from bandwidth_launcher import BandwidthLauncher
        launcher = BandwidthLauncher()
        print(f"✓ Config loaded: {len(launcher.config)} settings")
        return True
    except Exception as e:
        print(f"✗ Config loading failed: {e}")
        return False

def test_app_discovery():
    """Test app discovery (may find none if not installed)."""
    try:
        from bandwidth_launcher import BandwidthLauncher
        launcher = BandwidthLauncher()
        launcher.discover_apps()
        print(f"✓ App discovery completed: {len(launcher.apps)} apps found")
        return True
    except Exception as e:
        print(f"✗ App discovery failed: {e}")
        return False

def test_status():
    """Test status generation."""
    try:
        from bandwidth_launcher import BandwidthLauncher
        launcher = BandwidthLauncher()
        launcher.discover_apps()
        status = launcher.status()
        print(f"✓ Status generation works: {len(status)} apps")
        return True
    except Exception as e:
        print(f"✗ Status generation failed: {e}")
        return False

def test_report():
    """Test report generation."""
    try:
        from bandwidth_launcher import BandwidthLauncher
        launcher = BandwidthLauncher()
        launcher.discover_apps()
        report = launcher.generate_report()
        print(f"✓ Report generation works: {len(report)} characters")
        return True
    except Exception as e:
        print(f"✗ Report generation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("BANDWIDTH SHARING LAUNCHER - TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_import),
        ("Config Test", test_config),
        ("App Discovery Test", test_app_discovery),
        ("Status Test", test_status),
        ("Report Test", test_report),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
