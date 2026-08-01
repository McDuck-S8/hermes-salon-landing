#!/usr/bin/env python3
"""
Preview generated content — opens HTML gallery in browser.
Usage: python preview.py [--session N]
"""

import sys
import argparse
from pathlib import Path
from urllib.request import pathname2url

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = PROJECT_ROOT / "content" / "sessions"


def main():
    parser = argparse.ArgumentParser(description="Preview AI OFM content")
    parser.add_argument("--session", type=int, default=None,
                        help="Session number (default: latest)")
    args = parser.parse_args()

    # Find latest session if not specified
    if args.session is None:
        existing = sorted([int(d.name) for d in CONTENT_DIR.glob("*")
                          if d.is_dir() and d.name.isdigit()])
        if not existing:
            print("No sessions found. Run generate.py first.")
            sys.exit(1)
        args.session = existing[-1]

    session_dir = CONTENT_DIR / f"{args.session:02d}"
    preview = session_dir / "preview.html"

    if not preview.exists():
        print(f"Preview not found: {preview}")
        sys.exit(1)

    # Convert to file:// URL
    url = f"file:///{pathname2url(str(preview))}"
    print(f"Session {args.session:02d}: {preview}")
    print(f"Open in browser: {url}")

    # Try to open in default browser
    try:
        import webbrowser
        webbrowser.open(url)
        print("Opened in browser.")
    except Exception:
        pass


if __name__ == "__main__":
    main()
