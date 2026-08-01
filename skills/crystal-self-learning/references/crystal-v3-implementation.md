# Crystal v3 — Implementation Reference

## Quick Start

```bash
python scripts/crystal.py              # full cycle
python scripts/crystal.py --summary    # quick overview
python scripts/crystal.py --test       # test all modules
python scripts/crystal.py --propose    # generate proposals
python scripts/crystal.py --department ai-core  # per-department
```

## Module Map

| Module | File | Purpose | Dependencies |
|--------|------|---------|--------------|
| Session Reader | session_reader.py | Read state.db, extract signals | sqlite3 |
| Pattern Detector | pattern_detector.py | Find correction loops, frustrations | Session Reader |
| Need Analyzer | need_analyzer.py | Patterns → needs | Pattern Detector |
| Priority Engine | priority_engine.py | urgency × impact / effort | Need Analyzer |
| Risk Assessment | risk_assessment.py | safe/moderate/risky/critical | Proposals |
| Memory Integration | memory_integration.py | Read USER.md + MEMORY.md | os |
| Knowledge Base | knowledge_base.py | Proven solutions store | models |
| Dev Proposer | dev_proposer.py | Needs → actions | Need Analyzer, KB |
| Testing | testing.py | Test before applying | Proposal |
| Feedback Loop | feedback_loop.py | Measure if changes helped | Signals, Proposals |
| Versioning | versioning.py | Changelog | models |
| Rollback | rollback.py | Snapshot + revert | shutil |
| Synergy | synergy.py | Cross-department connections | Proposals, Needs |
| Staleness | staleness.py | Outdated detection | os, time |
| Alerts | alerts.py | Proactive notifications | Signals, Patterns |
| Resources | resources.py | Budget and limits | os |
| Self-Evolution | self_evolution.py | Crystal improves itself | Signals, Patterns |
| Goals | goals.py | Long-term objectives | models |
| Intelligence | intelligence.py | External world scanning | (stub) |
| Communication | communication_adapter.py | Style adaptation | models |

## Data Flow

```
state.db → SessionReader → [Signal] → PatternDetector → [Pattern]
    → NeedAnalyzer → [Need] → PriorityEngine → [PrioritizedItem]
    → DevelopmentProposer → [Proposal] → RiskAssessor → [RiskAssessment]
    → ProposalTester → [TestResult] → (apply or skip)
    → FeedbackLoop → [Assessment] → VersionManager → [ChangelogEntry]
```

## State.DB Schema

```sql
sessions (id, source, user_id, model, title, started_at, ended_at, message_count)
messages (id, session_id, role, content, tool_call_id, tool_calls, tool_name, timestamp)
```

## JSON Data Files (cache/crystal/)

signals.json, patterns.json, needs.json, priority.json, proposals.json,
feedback.json, staleness.json, energy.json, dependencies.json,
versioning.json, knowledge_base.json, communication.json, resources.json,
changelog.json, synergies.json, goals.json, intelligence.json, snapshots/
