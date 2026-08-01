---
type: tools
title: "[event_reactor.py] Event Reactor — reacts to system events beyond file changes.
"
timestamp: 2026-07-18T18:29:38.344689
confidence: 0.500
verification_method: manual
source_table: kc_entries
importance: 6
tags:
  - script
  - event_reactor.py
resource: scripts
---

[event_reactor.py] Event Reactor — reacts to system events beyond file changes.


> Revisit: when reactor logic, event-to-action mapping, or handler execution changes. Last touched: 2026-07-02.
Extends file_watcher.py with event-driven triggers:
- Knowledge Cube changes → auto-classify new entries
- Goal queue changes
