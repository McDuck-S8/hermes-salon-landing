# Contributing to Skill Forge

## Dev Environment

```bash
git clone https://github.com/vystartasv/skill-forge.git
cd skill-forge
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Testing

```bash
pytest -v
```

## Pull Request Checklist

- [ ] Tests pass: `pytest` (89 tests)
- [ ] New code has tests
- [ ] README updated if needed
- [ ] CHANGELOG entry added under `[Unreleased]`
