#!/usr/bin/env python3
"""Check browser-harness availability."""
import sys, os
sys.path.insert(0, '/d/Portable_Soft/hermes/browser-harness/src')
try:
    from browser_harness.helpers import goto_url, wait_for_load
    import browser_harness.helpers
    print('browser-harness OK')
    print('helpers:', dir(browser_harness.helpers))
except Exception as e:
    print(f'browser-harness ERROR: {e}')
    import traceback
    traceback.print_exc()
