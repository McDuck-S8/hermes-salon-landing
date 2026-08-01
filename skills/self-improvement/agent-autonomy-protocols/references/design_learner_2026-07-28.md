# Design Learner Infrastructure — 2026-07-28

## Summary
Full DESIGN_LEARNER v1.0 implementation: continuous design trend learning, automated quality evaluation, pattern promotion, and integration with autonomy core.

---

## Architecture

### Core Modules (in `scripts/`)
| Module | Purpose |
|--------|---------|
| `design_reference_collector.py` | Scans Awwwards, Behance, Dribbble, YouTube, GitHub, blogs for design trends via external_import protocol |
| `design_analyzer.py` | Extracts visual patterns (color, typography, layout, animation, components) from references |
| `design_skill_generator.py` | Dynamically composes skills from patterns (pattern → skill pipeline) |
| `design_evaluator.py` | Automated quality checks: Lighthouse (perf/a11y/best-practices/SEO), axe-core, ESLint, W3C, custom design checks |
| `design_critic.py` | LLM-based deep critique: visual quality, trend alignment, usability, brand fit |
| `design_feedback.py` | Feedback loop: auto scores, user ratings, A/B tests, client feedback → pattern promotion/demotion |
| `design_redesign.py` | Full pipeline: analysis → research → adaptation → generation → QC → critique → handoff |
| `design-code-generator.py` | HTML/CSS/JS generation from patterns + brand tokens |
| `design-adaptation.py` | PatternAdapter: maps generic patterns to project brand tokens |
| `design-quality-check.py` | Quality gates: Lighthouse ≥80, axe ≥90, W3C=0, custom checks ≥70 |

### Design Skills Created (6)
| Skill | Triggers | Integration |
|-------|----------|-------------|
| `design-research` | "research design trends", "find references for" | external_import |
| `design-adaptation` | "adapt pattern to brand", "apply color scheme" | PatternAdapter |
| `design-code-generator` | "generate component", "create landing page" | skill_composer |
| `design-quality-check` | "check design quality", "run lighthouse" | Lighthouse, axe-core, ESLint, W3C |
| `design-feedback` | "collect feedback", "rate design" | feedback_store |
| `design-redesign` | "redesign website", "modernize UI" | full pipeline + handoff |

### YouTube Integration
- `youtube_pipeline.py` — Fallback chain: oembed (200ms) → HTML proxy (2s) → yt-dlp (10s) → subtitles
- Videos processed: o1DsUPdSj1s, L9vDhq_W3Tk, 8m-YA7jphM0, qiDalcMeBFk (cached in `cache/youtube/`)
- Concepts extracted to tactical buffer with TTL 14d, confidence 0.4

---

## Quality Thresholds

| Metric | Threshold |
|--------|-----------|
| Lighthouse Performance | ≥80 |
| Lighthouse Accessibility | ≥90 |
| Lighthouse Best Practices | ≥85 |
| Lighthouse SEO | ≥80 |
| axe-core Score | ≥90 |
| W3C Errors | 0 |
| ESLint Errors | 0 |
| Custom Design Checks | ≥70 |

---

## Promotion Pipeline

```
Tactical Buffer (TTL 14d, confidence 0.4)
    ↓ 3 successful uses + 80% score
Strategic DB (versioned, confidence > 0.8)
```

---

## Integration with Agent Autonomy

- **DIRECTIVE 0x15: DESIGN_LEARNING** — Daily trend updates, auto-checks, pattern promotion
- **Chain Heartbeat** — Fires `design_collection_complete` event
- **Feedback Store** — Source for success_rate calculations
- **PatternMerger** — Auto-promotes winning design patterns
- **SkillComposer** — Dynamically assembles design agents from skills

---

## Verification

```bash
# Check design evaluator
python scripts/design_evaluator.py test_project

# Check design critic
python scripts/design_critic.py test_project

# Check skill audit
python scripts/skill_audit.py | grep design

# Run autonomy cycle
python scripts/autonomy_cycle.py
```