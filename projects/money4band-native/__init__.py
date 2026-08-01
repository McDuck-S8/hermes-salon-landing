"""
Money4Band Native — Run bandwidth-sharing apps without Docker
══════════════════════════════════════════════════════════════
Each app runs as a native Python subprocess or system process.
No Docker, no containers — just pure Python + native binaries.

Supported apps:
  - Honeygain (native client)
  - EarnApp (native client)
  - PacketStream (native client)
  - Pawns.app (CLI client)
  - Traffmonetizer (CLI)
  - Peer2Profit (CLI)
  - Bitping (CLI/Node)
  - Grass (browser-based)

Architecture:
  - config.yaml — all app configs, proxies, device info
  - apps/ — per-app runner modules
  - manager.py — process orchestrator
  - dashboard.py — web dashboard (optional)
  - cli.py — CLI interface

Author: Hermes Agent
"""

__version__ = "1.0.0"
