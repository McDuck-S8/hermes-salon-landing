---
name: boot-context
description: "Auto-generated from BOOT_CONTEXT.md"
trigger: "When user asks about BOOT_CONTEXT concepts"
usage: boot-context
Revisit: 2026-07-31
---

## CRITICAL: Context Loss Between Sessions

Agent has two types of memory:
- DATA: files (feedback_store, goals, weights) — PERSISTS ✅
- CONTEXT: understanding built during conversation — LOST on restart ❌

The agent thinks correctly NOW because it has conversation history.
After restart, history is gone. Only files remain.

**Solution:** Save THINKING (not just data) in files that agent reads at boot.

Files that must exist at boot:
1. agent_policies.md — ALL thinking rules (not just 5)
2. USER_PROFILE.md — who is the user
3. DECISION_LOG.md (last 50) — what happened
4. ALERTS.md — current problems
5. SELF_AUDIT.md — last self-assessment
6. cache/action_weights.json — learned weights

Lessons from this session that must persist:
- Don't lie about success when something doesn't work
- Go find information instead of saying "need to check"
- Blocked goals can't be top priority
- Don't build infrastructure for infrastructure's sake
- Think about adjacent areas (taxes, legal, scaling)
- User profiling is as-needed, not upfront interrogation
