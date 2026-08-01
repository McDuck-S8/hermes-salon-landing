# skill-forge/ — Skill Development & Packaging

## Purpose
Python package for building, testing, and packaging agent skills. The development environment for creating new skills before they go to `skills/`.

## Ownership
Skill creation tooling. Source code lives in `src/skill_forge/`.

## Local Contracts
- Python package with `pyproject.toml`
- Source: `src/skill_forge/`
- Tests: `tests/`
- Docs: `docs/` (architecture, getting-started, implementation-plan)
- Each skill is a directory with SKILL.md + optional references/, scripts/, templates/

## Work Guidance
- Build skills here, then publish to `skills/` directory
- Follow SKILL.md format: YAML frontmatter + markdown body
- Test before publishing

## Verification
- `python -m pytest tests/`
