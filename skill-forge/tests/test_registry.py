"""Tests for SQLite registry CRUD, quality checks, and search."""

import pytest

from skill_forge.registry import Registry


class TestSchema:
    """Schema creation and basic structure tests."""

    def test_creates_tables(self, registry):
        with registry._conn() as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
            names = {r["name"] for r in tables}
            assert "skills" in names
            assert "quality_checks" in names
            assert "versions" in names
            assert "dependencies" in names
            assert "skills_fts" in names

    def test_wal_mode(self, registry):
        with registry._conn() as conn:
            mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            assert mode.lower() == "wal"

    def test_foreign_keys_enabled(self, registry):
        with registry._conn() as conn:
            fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
            assert fk == 1

    def test_creates_db_directory(self, tmp_path):
        db = tmp_path / "subdir" / "test.db"
        Registry(db)
        assert db.exists()

    def test_reopen_preserves_data(self, db_path):
        reg1 = Registry(db_path)
        reg1.add_skill("test", "dev", "1.0", "/tmp/test.md")

        reg2 = Registry(db_path)
        skill = reg2.get_skill("test")
        assert skill is not None
        assert skill["name"] == "test"


class TestSkillsCRUD:
    """Basic Create, Read, Update, Delete for skills."""

    def test_add_skill(self, registry):
        sid = registry.add_skill("my-skill", "devops", "1.0.0", "/tmp/test.md",
                                  "body content", "A test skill")
        assert sid == 1

        skill = registry.get_skill("my-skill")
        assert skill["name"] == "my-skill"
        assert skill["category"] == "devops"
        assert skill["version"] == "1.0.0"
        assert skill["path"] == "/tmp/test.md"
        assert skill["body"] == "body content"
        assert skill["description"] == "A test skill"
        assert skill["status"] == "active"
        assert skill["installed_at"] is not None

    def test_add_skill_duplicate_raises(self, registry):
        registry.add_skill("dup", "dev", "1.0", "/tmp/a.md")
        with pytest.raises(Exception):
            registry.add_skill("dup", "dev", "1.0", "/tmp/b.md")

    def test_upsert_skill_insert(self, registry):
        sid = registry.upsert_skill("new", "dev", "1.0", "/tmp/n.md")
        assert sid == 1
        assert registry.skill_count() == 1

    def test_upsert_skill_update(self, registry):
        registry.add_skill("test", "dev", "1.0", "/tmp/t.md", body="old")
        sid = registry.upsert_skill("test", "ops", "2.0", "/tmp/t2.md", body="new")
        assert sid == 1
        skill = registry.get_skill("test")
        assert skill["category"] == "ops"
        assert skill["version"] == "2.0"
        assert skill["path"] == "/tmp/t2.md"
        assert skill["body"] == "new"

    def test_get_nonexistent(self, registry):
        assert registry.get_skill("nope") is None

    def test_get_by_id(self, registry):
        sid = registry.add_skill("target", "dev", "1.0", "/tmp/t.md")
        skill = registry.get_skill_by_id(sid)
        assert skill["name"] == "target"

    def test_list_all(self, registry):
        registry.add_skill("a", "dev", "1.0", "/tmp/a.md")
        registry.add_skill("b", "ops", "1.0", "/tmp/b.md")
        registry.add_skill("c", "dev", "1.0", "/tmp/c.md")
        all_skills = registry.list_skills()
        assert len(all_skills) == 3

    def test_list_by_category(self, registry):
        registry.add_skill("a", "dev", "1.0", "/tmp/a.md")
        registry.add_skill("b", "ops", "1.0", "/tmp/b.md")
        dev = registry.list_skills(category="dev")
        assert len(dev) == 1
        assert dev[0]["name"] == "a"

    def test_list_by_status(self, registry):
        registry.add_skill("a", "dev", "1.0", "/tmp/a.md")
        registry.add_skill("b", "dev", "1.0", "/tmp/b.md")
        registry.update_skill_status("b", "deprecated")
        active = registry.list_skills(status="active")
        assert len(active) == 1
        assert active[0]["name"] == "a"

    def test_update_status(self, registry):
        registry.add_skill("s", "dev", "1.0", "/tmp/s.md")
        assert registry.update_skill_status("s", "broken")
        assert registry.get_skill("s")["status"] == "broken"

    def test_update_status_nonexistent(self, registry):
        assert not registry.update_skill_status("nope", "broken")

    def test_delete_skill(self, registry):
        registry.add_skill("del", "dev", "1.0", "/tmp/d.md")
        assert registry.delete_skill("del")
        assert registry.get_skill("del") is None
        assert registry.skill_count() == 0

    def test_delete_cascades(self, registry):
        sid = registry.add_skill("cascade", "dev", "1.0", "/tmp/c.md")
        registry.record_quality_check(sid, "lint", True)
        registry.delete_skill("cascade")
        with registry._conn() as conn:
            checks = conn.execute(
                "SELECT COUNT(*) FROM quality_checks WHERE skill_id = ?", (sid,)
            ).fetchone()[0]
            assert checks == 0


class TestQualityChecks:
    """Quality check recording and retrieval."""

    def test_record_and_retrieve(self, registry):
        sid = registry.add_skill("test", "dev", "1.0", "/tmp/t.md")
        cid = registry.record_quality_check(sid, "frontmatter", True, "all good")
        assert cid == 1

        checks = registry.get_latest_checks(sid)
        assert len(checks) == 1
        assert checks[0]["check_name"] == "frontmatter"
        assert checks[0]["passed"] == 1
        assert checks[0]["details"] == "all good"

    def test_multiple_checks_same_name(self, registry):
        sid = registry.add_skill("test", "dev", "1.0", "/tmp/t.md")
        registry.record_quality_check(sid, "lint", False, "first fail")
        registry.record_quality_check(sid, "lint", True, "fixed")
        checks = registry.get_latest_checks(sid)
        assert len(checks) == 1
        assert checks[0]["passed"] == 1

    def test_failed_checks_report(self, registry):
        sid = registry.add_skill("bad", "dev", "1.0", "/tmp/b.md")
        sid2 = registry.add_skill("good", "dev", "1.0", "/tmp/g.md")
        registry.record_quality_check(sid, "frontmatter", False, "missing name")
        registry.record_quality_check(sid2, "frontmatter", True)
        failed = registry.get_failed_checks()
        assert len(failed) == 1
        assert failed[0]["name"] == "bad"


class TestSearch:
    """FTS5 full-text search."""

    def test_search_by_name(self, registry):
        registry.add_skill("python-pypi-release", "devops", "1.0", "/tmp/p.md",
                            description="PyPI release helper")
        results = registry.search("pypi")
        assert len(results) == 1
        assert results[0]["name"] == "python-pypi-release"

    def test_search_by_description(self, registry):
        registry.add_skill("calculator", "math", "1.0", "/tmp/c.md",
                            description="Evaluate math expressions")
        results = registry.search("math")
        assert len(results) >= 1

    def test_search_by_body(self, registry):
        registry.add_skill("guide", "docs", "1.0", "/tmp/g.md",
                            body="pip install skill-forge to get started")
        results = registry.search("install")
        assert len(results) >= 1

    def test_search_no_results(self, registry):
        registry.add_skill("test", "dev", "1.0", "/tmp/t.md")
        results = registry.search("zzzznomatch")
        assert len(results) == 0

    def test_search_fallback_like(self, registry):
        """FTS5 rejects special chars — fallback to LIKE should work."""
        registry.add_skill("test", "dev", "1.0", "/tmp/t.md",
                            body="some special! content")
        # Query with special chars that FTS5 might reject
        results = registry.search("special!")
        # Should not crash — LIKE fallback handles it
        assert isinstance(results, list)


class TestStats:
    """Registry health statistics."""

    def test_empty_stats(self, registry):
        stats = registry.get_stats()
        assert stats["total_skills"] == 0
        assert stats["skills_with_failures"] == 0

    def test_stats_with_data(self, registry):
        registry.add_skill("a", "dev", "1.0", "/tmp/a.md")
        registry.add_skill("b", "ops", "1.0", "/tmp/b.md")
        registry.add_skill("c", "dev", "1.0", "/tmp/c.md")
        registry.update_skill_status("c", "deprecated")

        stats = registry.get_stats()
        assert stats["total_skills"] == 3
        assert stats["by_status"]["active"] == 2
        assert stats["by_status"]["deprecated"] == 1
        assert stats["by_category"]["dev"] == 2
        assert stats["by_category"]["ops"] == 1
        assert stats["db_path"] == str(registry.db_path)

    def test_stats_with_failures(self, registry):
        sid = registry.add_skill("bad", "dev", "1.0", "/tmp/b.md")
        registry.record_quality_check(sid, "lint", False)
        stats = registry.get_stats()
        assert stats["skills_with_failures"] == 1


class TestConcurrency:
    """Tests for concurrent access safety."""

    def test_separate_connections(self, db_path):
        reg1 = Registry(db_path)
        reg2 = Registry(db_path)
        reg1.add_skill("from-1", "dev", "1.0", "/tmp/1.md")
        assert reg2.get_skill("from-1") is not None
        assert reg2.skill_count() == 1

    def test_wal_allows_concurrent_readers(self, db_path):
        reg1 = Registry(db_path)
        reg1.add_skill("shared", "dev", "1.0", "/tmp/s.md")
        # Open a second connection while first has data
        with reg1._conn() as c1:
            c1.execute("SELECT * FROM skills")
            reg2 = Registry(db_path)
            skill = reg2.get_skill("shared")
            assert skill is not None


class TestPruneExport:
    """Prune stale skills and JSON export."""

    def test_prune_removes_deleted_files(self, db_path, tmp_path):
        reg = Registry(db_path)
        skill_md = tmp_path / "temp-skill" / "SKILL.md"
        skill_md.parent.mkdir()
        skill_md.write_text("""---
name: temp-skill
description: temp
version: 1.0.0
---
## Trigger
Test.
""")
        from skill_forge.importer import import_skills
        import_skills(reg, tmp_path)
        assert reg.skill_count() == 1

        skill_md.unlink()
        skill_md.parent.rmdir()

        pruned = reg.prune_stale()
        assert pruned == 1
        assert reg.skill_count() == 0

    def test_prune_keeps_existing_files(self, db_path, tmp_path):
        reg = Registry(db_path)
        skill_md = tmp_path / "keep-skill" / "SKILL.md"
        skill_md.parent.mkdir()
        skill_md.write_text("""---
name: keep-skill
description: keep
version: 1.0.0
---
## Trigger
Test.
""")
        from skill_forge.importer import import_skills
        import_skills(reg, tmp_path)
        pruned = reg.prune_stale()
        assert pruned == 0
        assert reg.skill_count() == 1

    def test_export_json(self, db_path, tmp_path):
        reg = Registry(db_path)
        skill_md = tmp_path / "exp-skill" / "SKILL.md"
        skill_md.parent.mkdir()
        skill_md.write_text("""---
name: exp-skill
description: export test
version: 1.0.0
---
## Trigger
Test.
""")
        from skill_forge.importer import import_skills
        import_skills(reg, tmp_path)
        reg.record_quality_check(1, "frontmatter", True, "all good")

        import json
        data = reg.export_json()
        skills = json.loads(data)
        assert len(skills) == 1
        assert skills[0]["name"] == "exp-skill"
        assert len(skills[0]["quality_checks"]) == 1
