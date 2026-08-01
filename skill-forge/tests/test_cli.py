"""Integration tests for CLI commands via Click's CliRunner."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from skill_forge.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def skills_dir(tmp_path):
    """Create a test skills directory."""
    (tmp_path / "good-skill").mkdir()
    (tmp_path / "good-skill" / "SKILL.md").write_text("""---
name: good-skill
description: A valid skill
version: 1.0.0
category: testing
---
## Trigger
When testing.
""")
    (tmp_path / "bad-skill").mkdir()
    (tmp_path / "bad-skill" / "SKILL.md").write_text("No frontmatter")
    return tmp_path


class TestImportHermes:
    """forge import-hermes command."""

    def test_imports_skills(self, runner, skills_dir, tmp_path):
        db = tmp_path / "test.db"
        result = runner.invoke(main, [
            "import-hermes",
            "--skills-dir", str(skills_dir),
            "--db-path", str(db),
        ])
        assert result.exit_code == 0
        assert "Imported:" in result.output
        assert "Failed:" in result.output

    def test_verbose(self, runner, skills_dir, tmp_path):
        db = tmp_path / "test.db"
        result = runner.invoke(main, [
            "import-hermes",
            "--skills-dir", str(skills_dir),
            "--db-path", str(db),
            "-v",
        ])
        assert result.exit_code == 0
        assert "good-skill" in result.output


class TestList:
    """forge list command."""

    def test_lists_skills(self, runner, skills_dir, tmp_path):
        db = tmp_path / "test.db"
        # Import first
        runner.invoke(main, ["import-hermes", "--skills-dir", str(skills_dir), "--db-path", str(db)])
        # Then list
        result = runner.invoke(main, ["list", "--db-path", str(db)])
        assert result.exit_code == 0
        assert "good-skill" in result.output

    def test_filter_by_category(self, runner, skills_dir, tmp_path):
        db = tmp_path / "test.db"
        runner.invoke(main, ["import-hermes", "--skills-dir", str(skills_dir), "--db-path", str(db)])
        result = runner.invoke(main, ["list", "--db-path", str(db), "--category", "testing"])
        assert "good-skill" in result.output

    def test_empty_registry(self, runner, tmp_path):
        db = tmp_path / "empty.db"
        result = runner.invoke(main, ["list", "--db-path", str(db)])
        assert "No skills registered" in result.output


class TestStatus:
    """forge status command."""

    def test_shows_stats(self, runner, skills_dir, tmp_path):
        db = tmp_path / "test.db"
        runner.invoke(main, ["import-hermes", "--skills-dir", str(skills_dir), "--db-path", str(db)])
        result = runner.invoke(main, ["status", "--db-path", str(db)])
        assert result.exit_code == 0
        assert "Total skills" in result.output

    def test_empty_status(self, runner, tmp_path):
        db = tmp_path / "empty.db"
        result = runner.invoke(main, ["status", "--db-path", str(db)])
        assert result.exit_code == 0
        assert "Total skills: 0" in result.output


class TestValidate:
    """forge validate command."""

    def test_validate_by_name(self, runner, skills_dir, tmp_path):
        db = tmp_path / "test.db"
        runner.invoke(main, ["import-hermes", "--skills-dir", str(skills_dir), "--db-path", str(db)])
        result = runner.invoke(main, ["validate", "--name", "good-skill", "--db-path", str(db)])
        assert result.exit_code == 0
        assert "frontmatter" in result.output

    def test_validate_nonexistent(self, runner, tmp_path):
        db = tmp_path / "test.db"
        result = runner.invoke(main, ["validate", "--name", "nope", "--db-path", str(db)])
        assert result.exit_code == 1

    def test_validate_all_registered(self, runner, skills_dir, tmp_path):
        db = tmp_path / "test.db"
        runner.invoke(main, ["import-hermes", "--skills-dir", str(skills_dir), "--db-path", str(db)])
        result = runner.invoke(main, ["validate", "--db-path", str(db)])
        assert result.exit_code == 0
        assert "passed" in result.output.lower()

    def test_validate_directory(self, runner, skills_dir, tmp_path):
        db = tmp_path / "test.db"
        result = runner.invoke(main, [
            "validate", "--skills-dir", str(skills_dir), "--db-path", str(db),
        ])
        assert result.exit_code == 0
        assert "good-skill" in result.output


class TestSearch:
    """forge search command."""

    def test_search_finds_skill(self, runner, skills_dir, tmp_path):
        db = tmp_path / "test.db"
        runner.invoke(main, ["import-hermes", "--skills-dir", str(skills_dir), "--db-path", str(db)])
        result = runner.invoke(main, ["search", "good", "--db-path", str(db)])
        assert result.exit_code == 0
        assert "good-skill" in result.output

    def test_search_no_results(self, runner, skills_dir, tmp_path):
        db = tmp_path / "test.db"
        runner.invoke(main, ["import-hermes", "--skills-dir", str(skills_dir), "--db-path", str(db)])
        result = runner.invoke(main, ["search", "zzzznomatch", "--db-path", str(db)])
        assert "No skills found" in result.output


class TestInspect:
    """forge inspect command."""

    def test_inspect_skill(self, runner, skills_dir, tmp_path):
        db = tmp_path / "test.db"
        runner.invoke(main, ["import-hermes", "--skills-dir", str(skills_dir), "--db-path", str(db)])
        result = runner.invoke(main, ["inspect", "good-skill", "--db-path", str(db)])
        assert result.exit_code == 0
        assert "good-skill" in result.output
        assert "testing" in result.output

    def test_inspect_nonexistent(self, runner, tmp_path):
        db = tmp_path / "test.db"
        result = runner.invoke(main, ["inspect", "nope", "--db-path", str(db)])
        assert result.exit_code == 1


class TestRegister:
    """forge register command."""

    def test_register_single_skill(self, runner, skills_dir, tmp_path):
        db = tmp_path / "test.db"
        skill_md = skills_dir / "good-skill" / "SKILL.md"
        result = runner.invoke(main, ["register", str(skill_md), "--db-path", str(db)])
        assert result.exit_code == 0
        assert "Registered" in result.output

        # Verify it's in the registry
        list_result = runner.invoke(main, ["list", "--db-path", str(db)])
        assert "good-skill" in list_result.output

    def test_register_nonexistent(self, runner, tmp_path):
        db = tmp_path / "test.db"
        result = runner.invoke(main, ["register", "/nonexistent/skill.md", "--db-path", str(db)])
        assert result.exit_code == 1


class TestPruneExportWatch:
    """forge prune, export, watch commands."""

    def test_prune(self, runner, skills_dir, tmp_path):
        db = tmp_path / "test.db"
        runner.invoke(main, ["import-hermes", "--skills-dir", str(skills_dir), "--db-path", str(db)])
        result = runner.invoke(main, ["prune", "--db-path", str(db)])
        assert result.exit_code == 0
        # Skills still exist, so none pruned
        assert "No stale" in result.output or "Pruned 0" in result.output

    def test_export(self, runner, skills_dir, tmp_path):
        db = tmp_path / "test.db"
        runner.invoke(main, ["import-hermes", "--skills-dir", str(skills_dir), "--db-path", str(db)])
        result = runner.invoke(main, ["export", "--db-path", str(db)])
        assert result.exit_code == 0
        assert "good-skill" in result.output

    def test_export_to_file(self, runner, skills_dir, tmp_path):
        db = tmp_path / "test.db"
        out = tmp_path / "export.json"
        runner.invoke(main, ["import-hermes", "--skills-dir", str(skills_dir), "--db-path", str(db)])
        result = runner.invoke(main, ["export", "--db-path", str(db), "-o", str(out)])
        assert result.exit_code == 0
        assert out.exists()

    def test_watch_once(self, runner, skills_dir, tmp_path):
        db = tmp_path / "test.db"
        result = runner.invoke(main, [
            "watch", "--skills-dir", str(skills_dir), "--db-path", str(db), "--once"
        ])
        assert result.exit_code == 0
        assert "Imported:" in result.output
