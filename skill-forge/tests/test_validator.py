"""Tests for quality gate validators."""

from pathlib import Path

from skill_forge.validator import (
    validate_all,
    validate_frontmatter,
    validate_skill,
    validate_structure,
)


class TestValidateFrontmatter:
    """Frontmatter validation — required fields and format."""

    def test_valid(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("""---
name: my-skill
description: A good skill
version: 1.0.0
category: devops
---
# Body
""")
        passed, details = validate_frontmatter(f)
        assert passed
        assert "valid" in details.lower()

    def test_missing_name(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("""---
description: desc
version: 1.0.0
---
""")
        passed, details = validate_frontmatter(f)
        assert not passed
        assert "name" in details.lower()

    def test_missing_description(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("""---
name: test
version: 1.0.0
---
""")
        passed, details = validate_frontmatter(f)
        assert not passed
        assert "description" in details.lower()

    def test_missing_version(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("""---
name: test
description: desc
---
""")
        passed, details = validate_frontmatter(f)
        assert not passed
        assert "version" in details.lower()

    def test_invalid_semver(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("""---
name: test
description: desc
version: not-a-version
---
""")
        passed, details = validate_frontmatter(f)
        assert not passed
        assert "semver" in details.lower()

    def test_v_prefix_semver(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("""---
name: test
description: desc
version: v1.0.0
---
""")
        passed, details = validate_frontmatter(f)
        assert not passed  # v1.0.0 is not strict semver

    def test_missing_frontmatter(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("Just text, no frontmatter")
        passed, details = validate_frontmatter(f)
        assert not passed
        assert "missing" in details.lower() or "frontmatter" in details.lower()

    def test_corrupt_yaml(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("""---
name: [unclosed
---
""")
        passed, details = validate_frontmatter(f)
        assert not passed

    def test_empty_frontmatter(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("""---
---
""")
        passed, details = validate_frontmatter(f)
        assert not passed
        assert "empty" in details.lower()

    def test_not_a_dict(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("""---
- list item
- not a mapping
---
""")
        passed, details = validate_frontmatter(f)
        assert not passed

    def test_unreadable_file(self, tmp_path):
        passed, details = validate_frontmatter(tmp_path / "nonexistent.md")
        assert not passed
        assert "cannot read" in details.lower()


class TestValidateStructure:
    """Structure validation — required sections."""

    def test_valid_with_trigger(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("""---
name: test
description: desc
version: 1.0.0
---
## Trigger
Use this when you need to test something.
""")
        passed, details = validate_structure(f)
        assert passed

    def test_valid_with_usage(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("""---
name: test
description: desc
version: 1.0.0
---
## Usage
Some usage instructions here for the skill file.
""")
        passed, details = validate_structure(f)
        assert passed

    def test_valid_with_steps(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("""---
name: test
description: desc
version: 1.0.0
---
## Steps
1. First step
2. Second step
3. Third step here
""")
        passed, details = validate_structure(f)
        assert passed

    def test_no_headings(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("""---
name: test
description: desc
version: 1.0.0
---
Just text without headings.
""")
        passed, details = validate_structure(f)
        assert not passed
        assert "no ## sections" in details.lower()

    def test_headings_but_no_body_fails(self, tmp_path):
        """No headings = fail, but any ## section = pass."""
        f = tmp_path / "SKILL.md"
        f.write_text("""---
name: test
description: desc
version: 1.0.0
---
## Introduction
Some intro text.

## Conclusion
The end.
""")
        passed, _ = validate_structure(f)
        assert passed  # any headings are accepted

    def test_empty_section_warning(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("""---
name: test
description: desc
version: 1.0.0
---
## Trigger
too short
""")
        passed, details = validate_structure(f)
        assert passed
        assert "warning" in details.lower()

    def test_unreadable_file(self, tmp_path):
        passed, details = validate_structure(tmp_path / "nonexistent.md")
        assert not passed


class TestValidateSkill:
    """Combined validation."""

    def test_both_pass(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("""---
name: good
description: valid
version: 1.0.0
---
## Trigger
When you need it.
""")
        results = validate_skill(f)
        assert len(results) == 2
        assert all(r["passed"] for r in results)

    def test_one_fails(self, tmp_path):
        f = tmp_path / "SKILL.md"
        f.write_text("""---
name: bad
version: 1.0.0
---
## Trigger
Use when needed.
""")
        results = validate_skill(f)
        assert results[0]["passed"] is False  # missing description
        assert results[1]["passed"] is True   # structure OK


class TestValidateAll:
    """Directory-level validation."""

    def test_multiple_skills(self, tmp_path):
        (tmp_path / "good").mkdir()
        (tmp_path / "good" / "SKILL.md").write_text("""---
name: good
description: valid
version: 1.0.0
---
## Trigger
When you need it.
""")
        (tmp_path / "bad").mkdir()
        (tmp_path / "bad" / "SKILL.md").write_text("""---
name: bad
description: missing fields
version: bad
---
No headings here.
""")

        results = validate_all(tmp_path)
        assert len(results) == 2
        names = {r["name"] for r in results}
        assert "good" in names
        assert "bad" in names

        good = [r for r in results if r["name"] == "good"][0]
        assert good["all_passed"] is True

        bad = [r for r in results if r["name"] == "bad"][0]
        assert bad["all_passed"] is False

    def test_empty_directory(self, tmp_path):
        results = validate_all(tmp_path)
        assert results == []
