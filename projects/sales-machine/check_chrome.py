#!/usr/bin/env python3
"""Check if Chrome is available via browser-harness"""
import sys, os
sys.path.insert(0, '/d/Portable_Soft/hermes/browser-harness/src')
try:
    from browser_harness.helpers import goto_url, wait_for_load, page_info
    info = page_info()
    print('page_info:', info)
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
