"""Tests for Hermes skill importer."""

import tempfile
from pathlib import Path

import pytest

from skill_forge.importer import _parse_skill_file, import_skills
from skill_forge.registry import Registry


# ── Test fixtures ─────────────────────────────────────────────


@pytest.fixture
def skills_dir():
    """Create a temporary skills directory with test skill files."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        # Valid skill
        (base / "test-skill").mkdir()
        (base / "test-skill" / "SKILL.md").write_text("""---
name: test-skill
description: A test skill
version: 1.0.0
category: devops
---
# Test Skill

This is the body.
""")

        # Skill without category
        (base / "no-category").mkdir()
        (base / "no-category" / "SKILL.md").write_text("""---
name: no-category
description: No category here
version: 0.1.0
---
Body without category.
""")

        # Skill without frontmatter (should fail)
        (base / "bad-skill").mkdir()
        (base / "bad-skill" / "SKILL.md").write_text("No frontmatter here, just text.")

        # Empty directory (no SKILL.md)
        (base / "empty-dir").mkdir()

        # Corrupt YAML
        (base / "corrupt").mkdir()
        (base / "corrupt" / "SKILL.md").write_text("""---
name: corrupt
description: [unclosed bracket
---
Body.
""")

        # Nested skill (in subdirectory)
        (base / "category" / "nested-skill").mkdir(parents=True)
        (base / "category" / "nested-skill" / "SKILL.md").write_text("""---
name: nested-skill
description: Nested under category/
version: 2.0.0
category: nested
---
Nested body.
""")

        yield base


# ── Tests ─────────────────────────────────────────────────────


class TestParseSkillFile:
    """Unit tests for _parse_skill_file."""

    def test_valid_skill(self, skills_dir):
        skill = _parse_skill_file(skills_dir / "test-skill" / "SKILL.md")
        assert skill is not None
        assert skill["name"] == "test-skill"
        assert skill["category"] == "devops"
        assert skill["version"] == "1.0.0"
        assert skill["description"] == "A test skill"
        assert "This is the body" in skill["body"]
        assert str(skills_dir / "test-skill" / "SKILL.md") in skill["path"]

    def test_no_category(self, skills_dir):
        skill = _parse_skill_file(skills_dir / "no-category" / "SKILL.md")
        assert skill is not None
        assert skill["category"] == ""

    def test_no_frontmatter(self, skills_dir):
        skill = _parse_skill_file(skills_dir / "bad-skill" / "SKILL.md")
        assert skill is None

    def test_corrupt_yaml(self, skills_dir):
        skill = _parse_skill_file(skills_dir / "corrupt" / "SKILL.md")
        assert skill is None

    def test_nonexistent_file(self):
        skill = _parse_skill_file(Path("/nonexistent/path/SKILL.md"))
        assert skill is None

    def test_nested_skill(self, skills_dir):
        skill = _parse_skill_file(skills_dir / "category" / "nested-skill" / "SKILL.md")
        assert skill is not None
        assert skill["name"] == "nested-skill"
        assert skill["category"] == "nested"


class TestImportSkills:
    """Integration tests for import_skills."""

    def test_imports_all_valid(self, skills_dir, db_path):
        registry = Registry(db_path)
        result = import_skills(registry, skills_dir)
        assert result["imported"] >= 3  # test-skill, no-category, nested-skill
        assert result["failed"] >= 1     # bad-skill or corrupt
        assert result["total"] >= 4

        # Verify registry has skills
        skill = registry.get_skill("test-skill")
        assert skill is not None
        assert skill["category"] == "devops"

    def test_skip_unchanged(self, skills_dir, db_path):
        registry = Registry(db_path)
        # First import
        result1 = import_skills(registry, skills_dir)
        # Second import — should skip unchanged
        result2 = import_skills(registry, skills_dir)
        assert result2["skipped"] >= result1["imported"]
        # Total should still be same count
        assert registry.skill_count() > 0

    def test_update_changed(self, skills_dir, db_path):
        registry = Registry(db_path)
        import_skills(registry, skills_dir)

        # Modify a skill
        skill_md = skills_dir / "test-skill" / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: Updated description
version: 2.0.0
category: devops
---
Updated body.
""")

        result = import_skills(registry, skills_dir)
        assert result["imported"] >= 1  # should re-import as "updated"
        skill = registry.get_skill("test-skill")
        assert skill["description"] == "Updated description"
        assert skill["version"] == "2.0.0"

    def test_empty_directory(self, db_path):
        with tempfile.TemporaryDirectory() as tmp:
            registry = Registry(db_path)
            result = import_skills(registry, tmp)
            assert result["total"] == 0
            assert result["imported"] == 0

    def test_nonexistent_directory(self, db_path):
        registry = Registry(db_path)
        result = import_skills(registry, "/nonexistent/path/12345")
        assert result["total"] == 0

    def test_verbose_mode(self, skills_dir, db_path, capsys):
        registry = Registry(db_path)
        import_skills(registry, skills_dir, verbose=True)
        captured = capsys.readouterr()
        # Should mention some skills
        assert "test-skill" in captured.out or "imported" in captured.out
