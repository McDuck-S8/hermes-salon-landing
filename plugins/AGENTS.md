# plugins/ — Hermes Plugin Ecosystem

## Purpose
Self-contained plugins that extend Hermes functionality. Each plugin has its own `plugin.yaml`, entry points, and tests.

## Ownership
Each plugin is independently maintained. Plugins are loaded by the Hermes plugin system.

## Local Contracts
- Each plugin must have a `plugin.yaml` manifest
- Plugins export tools, commands, or hooks via `__init__.py`
- Tests live in `tests/` within each plugin
- Dependencies are declared in `pyproject.toml` or `requirements.txt`

## Work Guidance
- **hermes-lcm/**: Lossless Context Management — context compression, session patterns, model routing
- **icarus/**: Browser automation — Playwright-based browsing, state management, export
- **self-evolution/**: Self-improvement system — skill evolution, knowledge base, fitness evaluation
- **web-search-plus/**: Enhanced web search — multiple providers, caching, quality scoring

## Verification
- Each plugin has its own test suite in `tests/`
- Run `pytest plugins/<name>/tests/` to verify a specific plugin

## Child DOX Index
| Plugin | Purpose | Tests |
|---|---|---|
| `hermes-lcm/` | Context compression & management | `tests/test_*.py` |
| `icarus/` | Browser automation | `scripts/test-plugin.sh` |
| `self-evolution/` | Self-improvement & skill evolution | `tests/` |
| `web-search-plus/` | Enhanced web search | `tests/test_*.py` |
