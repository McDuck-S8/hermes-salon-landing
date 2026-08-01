#!/usr/bin/env python3
"""CLI entry point for Skill Forge."""

import click
import time
from pathlib import Path
from typing import Optional, List

from .registry import Registry
from .importer import import_skills
from .validator import validate_all as validate_all_skills, validate_skill
from .constants import FRONTMATTER_RE, SEMVER_RE


def _get_registry(db_path: str) -> Registry:
    """Get a Registry instance, creating the DB directory if needed."""
    return Registry(db_path)


def _parse_skill_file(path: Path) -> Optional[dict]:
    """Parse a SKILL.md file and return skill metadata."""
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return None

    fm_match = FRONTMATTER_RE.match(content)
    if not fm_match:
        return None

    import yaml
    try:
        frontmatter = yaml.safe_load(fm_match.group(1))
    except yaml.YAMLError:
        return None

    if not frontmatter or not isinstance(frontmatter, dict):
        return None

    return {
        "name": frontmatter.get("name"),
        "description": frontmatter.get("description", ""),
        "version": frontmatter.get("version"),
        "category": frontmatter.get("category"),
        "path": str(path),
        "body": content[fm_match.end():],
    }


# ── Version Bumping Helpers ─────────────────────────────────────────

def _bump_version(version: str, bump_type: str) -> str:
    """Bump a semver version string."""
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid semver: {version}")

    major, minor, patch = map(int, parts)

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

    return f"{major}.{minor}.{patch}"


def _update_skill_version(skill_path: Path, new_version: str) -> bool:
    """Update the version in a SKILL.md file."""
    content = skill_path.read_text(encoding="utf-8")
    fm_match = FRONTMATTER_RE.match(content)
    if not fm_match:
        return False

    fm_end = fm_match.end()
    frontmatter_str = fm_match.group(1)

    import yaml
    try:
        frontmatter = yaml.safe_load(frontmatter_str)
    except yaml.YAMLError:
        return False

    frontmatter["version"] = new_version

    # Reconstruct frontmatter
    new_fm = yaml.dump(frontmatter, sort_keys=False, allow_unicode=True)
    new_content = f"---\n{new_fm}---\n{content[fm_end:]}"

    skill_path.write_text(new_content, encoding="utf-8")
    return True


def _get_skill_history(registry: Registry, skill_name: str) -> List[dict]:
    """Get version history for a skill."""
    with registry._conn() as conn:
        skill = conn.execute("SELECT id FROM skills WHERE name = ?", (skill_name,)).fetchone()
        if not skill:
            return []

        rows = conn.execute(
            "SELECT version, changelog, published_at FROM versions WHERE skill_id = ? ORDER BY published_at DESC",
            (skill["id"],)
        ).fetchall()
        return [dict(r) for r in rows]


# ── CLI Commands ────────────────────────────────────────────────────

@click.group()
@click.version_option(version="0.1.0")
def main():
    """Skill Forge — Agent Skill Registry with Quality Gates.

    Manage agent skills: import, register, validate, search, and version.
    Database: ~/.hermes/skill-forge/forge.db
    """
    pass


@main.group()
def version():
    """Skill version management commands."""
    pass


@version.command("list")
@click.argument("skill_name")
@click.option(
    "--db-path",
    default=str(Path.home() / ".hermes" / "skill-forge" / "forge.db"),
    help="Database path",
)
def version_list(skill_name, db_path):
    """Show version history for a skill."""
    registry = _get_registry(db_path)
    history = _get_skill_history(registry, skill_name)

    if not history:
        click.echo(f"No version history found for: {skill_name}")
        return

    click.echo(f"Version history for: {skill_name}")
    click.echo("-" * 50)
    for v in history:
        click.echo(f"  {v['version']}  —  {v['published_at']}")
        if v['changelog']:
            click.echo(f"    {v['changelog']}")


@version.command("bump")
@click.argument("skill_name")
@click.option(
    "--type", "-t",
    type=click.Choice(["patch", "minor", "major"]),
    default="patch",
    help="Version bump type"
)
@click.option(
    "--changelog", "-c",
    default="",
    help="Changelog entry for this version"
)
@click.option(
    "--db-path",
    default=str(Path.home() / ".hermes" / "skill-forge" / "forge.db"),
    help="Database path",
)
def version_bump(skill_name, type, changelog, db_path):
    """Bump skill version (patch/minor/major)."""
    registry = _get_registry(db_path)

    # Get skill
    skill = registry.get_skill(skill_name)
    if not skill:
        click.echo(f"✗ Skill not found: {skill_name}", err=True)
        raise SystemExit(1)

    current_version = skill.get("version", "0.0.0")
    new_version = _bump_version(current_version, type)

    # Update file - skill["path"] is already the SKILL.md file path
    skill_path = Path(skill["path"])
    if not _update_skill_version(skill_path, new_version):
        click.echo(f"✗ Failed to update SKILL.md", err=True)
        raise SystemExit(1)

    # Update registry (records version history)
    registry.upsert_skill(
        name=skill["name"],
        category=skill.get("category"),
        version=new_version,
        path=skill["path"],
        body=skill.get("body", ""),
        description=skill.get("description", ""),
    )

    # Add changelog if provided
    if changelog:
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with registry._conn() as conn:
            conn.execute(
                "UPDATE versions SET changelog = ? WHERE skill_id = ? AND version = ?",
                (changelog, skill["id"], new_version),
            )

    click.echo(f"✓ {skill_name}: {current_version} → {new_version} ({type})")
    if changelog:
        click.echo(f"  Changelog: {changelog}")


@version.command("release")
@click.argument("skill_name")
@click.argument("version")
@click.option(
    "--changelog", "-c",
    default="",
    help="Changelog for this release"
)
@click.option(
    "--db-path",
    default=str(Path.home() / ".hermes" / "skill-forge" / "forge.db"),
    help="Database path",
)
def version_release(skill_name, version, changelog, db_path):
    """Record a specific version release (without bumping)."""
    registry = _get_registry(db_path)

    skill = registry.get_skill(skill_name)
    if not skill:
        click.echo(f"✗ Skill not found: {skill_name}", err=True)
        raise SystemExit(1)

    # Validate version format
    if not SEMVER_RE.match(version):
        click.echo(f"✗ Invalid version format: {version} (must be semver)", err=True)
        raise SystemExit(1)

    # Update file
    skill_path = Path(skill["path"])
    if not _update_skill_version(skill_path, version):
        click.echo(f"✗ Failed to update SKILL.md", err=True)
        raise SystemExit(1)

    # Update registry
    registry.upsert_skill(
        name=skill["name"],
        category=skill.get("category"),
        version=version,
        path=skill["path"],
        body=skill.get("body", ""),
        description=skill.get("description", ""),
    )

    # Add changelog
    if changelog:
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with registry._conn() as conn:
            conn.execute(
                "UPDATE versions SET changelog = ? WHERE skill_id = ? AND version = ?",
                (changelog, skill["id"], version),
            )

    click.echo(f"✓ Released {skill_name} v{version}")
    if changelog:
        click.echo(f"  Changelog: {changelog}")


@version.command("diff")
@click.argument("skill_name")
@click.argument("from_version")
@click.argument("to_version")
@click.option(
    "--db-path",
    default=str(Path.home() / ".hermes" / "skill-forge" / "forge.db"),
    help="Database path",
)
def version_diff(skill_name, from_version, to_version, db_path):
    """Show diff between two versions of a skill (changelog only)."""
    registry = _get_registry(db_path)

    with registry._conn() as conn:
        skill = conn.execute("SELECT id FROM skills WHERE name = ?", (skill_name,)).fetchone()
        if not skill:
            click.echo(f"✗ Skill not found: {skill_name}", err=True)
            raise SystemExit(1)

        rows = conn.execute(
            "SELECT version, changelog, published_at FROM versions WHERE skill_id = ? AND version IN (?, ?)",
            (skill["id"], from_version, to_version)
        ).fetchall()

        if len(rows) < 2:
            click.echo(f"✗ One or both versions not found in history", err=True)
            raise SystemExit(1)

        click.echo(f"Diff: {skill_name} {from_version} → {to_version}")
        click.echo("=" * 50)

        for row in rows:
            click.echo(f"\n{row['version']} ({row['published_at']})")
            if row['changelog']:
                click.echo(f"  {row['changelog']}")
            else:
                click.echo("  (no changelog)")


@version.command("current")
@click.argument("skill_name")
@click.option(
    "--db-path",
    default=str(Path.home() / ".hermes" / "skill-forge" / "forge.db"),
    help="Database path",
)
def version_current(skill_name, db_path):
    """Show current version of a skill."""
    registry = _get_registry(db_path)
    skill = registry.get_skill(skill_name)

    if not skill:
        click.echo(f"✗ Skill not found: {skill_name}", err=True)
        raise SystemExit(1)

    click.echo(f"{skill_name}: v{skill.get('version', 'unknown')}")


# ── Import / Register / Validate / Search ──────────────────────────

@main.command()
@click.option(
    "--skills-dir",
    default=str(Path.home() / ".hermes" / "skills"),
    help="Directory containing Hermes skills (default: ~/.hermes/skills)",
)
@click.option(
    "--db-path",
    default=str(Path.home() / ".hermes" / "skill-forge" / "forge.db"),
    help="Database path",
)
@click.option("-v", "--verbose", is_flag=True, help="Show per-skill progress")
def import_hermes(skills_dir, db_path, verbose):
    """Import all skills from a Hermes skills directory."""
    registry = _get_registry(db_path)

    click.echo(f"Importing from: {skills_dir}")
    result = import_skills(registry, skills_dir, verbose=verbose)

    click.echo(f"\n  Imported: {result['imported']}")
    click.echo(f"  Skipped:  {result['skipped']}")
    click.echo(f"  Failed:   {result['failed']}")
    click.echo(f"  Total:    {result['total']}")


@main.command()
@click.argument("path")
@click.option(
    "--db-path",
    default=str(Path.home() / ".hermes" / "skill-forge" / "forge.db"),
    help="Database path",
)
def register(path, db_path):
    """Register a single SKILL.md file."""
    registry = _get_registry(db_path)
    skill_path = Path(path).resolve()

    if not skill_path.exists():
        click.echo(f"✗ File not found: {path}", err=True)
        raise SystemExit(1)

    skill = _parse_skill_file(skill_path)
    if skill is None:
        click.echo(f"✗ Failed to parse SKILL.md: {path}", err=True)
        raise SystemExit(1)

    registry.upsert_skill(
        name=skill["name"],
        category=skill.get("category"),
        version=skill.get("version"),
        path=skill["path"],
        body=skill["body"],
        description=skill.get("description", ""),
    )
    click.echo(f"✓ Registered: {skill['name']} (v{skill['version']})")


@main.command()
@click.option("--name", "-n", default=None, help="Validate a specific skill by name")
@click.option("--skills-dir", default=None, help="Path to skills directory (for --all)")
@click.option(
    "--db-path",
    default=str(Path.home() / ".hermes" / "skill-forge" / "forge.db"),
    help="Database path",
)
def validate(name, skills_dir, db_path):
    """Run quality gates on skills."""
    registry = _get_registry(db_path)

    if name:
        skill = registry.get_skill(name)
        if not skill:
            click.echo(f"✗ Skill not found: {name}", err=True)
            raise SystemExit(1)

        click.echo(f"Validating: {name}")
        results = validate_skill(skill["path"])
        for r in results:
            icon = "✓" if r["passed"] else "✗"
            click.echo(f"  {icon} {r['check_name']}: {r['details']}")

        skill_id = skill["id"]
        for r in results:
            registry.record_quality_check(skill_id, r["check_name"], r["passed"], r["details"])

    elif skills_dir:
        results = validate_all_skills(skills_dir)
        if not results:
            click.echo("No skills found.")
            return

        passed_count = sum(1 for r in results if r["all_passed"])
        click.echo(f"Validated {len(results)} skills: {passed_count} passed, {len(results) - passed_count} failed\n")

        for r in results:
            status = "✓" if r["all_passed"] else "✗"
            click.echo(f"  {status} {r['name']}")
            for c in r["checks"]:
                icon = "  ✓" if c["passed"] else "  ✗"
                if not c["passed"]:
                    click.echo(f"    {icon} {c['check_name']}: {c['details']}")

    else:
        skills = registry.list_skills()
        if not skills:
            click.echo("No skills registered. Run 'forge import-hermes' first.")
            return

        passed_count = 0
        failed_count = 0
        for s in skills:
            results = validate_skill(s["path"])
            all_ok = all(r["passed"] for r in results)
            if all_ok:
                passed_count += 1
            else:
                failed_count += 1

            skill_id = s["id"]
            for r in results:
                registry.record_quality_check(skill_id, r["check_name"], r["passed"], r["details"])

        click.echo(f"Validated {len(skills)} skills: {passed_count} passed, {failed_count} failed")


@main.command()
@click.option("--category", "-c", default=None, help="Filter by category")
@click.option("--status", "-s", default=None, help="Filter by status (active/deprecated/broken)")
@click.option(
    "--db-path",
    default=str(Path.home() / ".hermes" / "skill-forge" / "forge.db"),
    help="Database path",
)
def list(category, status, db_path):
    """List registered skills."""
    registry = _get_registry(db_path)
    skills = registry.list_skills(category=category, status=status)

    if not skills:
        click.echo("No skills registered.")
        return

    filters = []
    if category:
        filters.append(f"category={category}")
    if status:
        filters.append(f"status={status}")
    filter_str = ", ".join(filters) if filters else "all"
    click.echo(f"Skills ({filter_str}): {len(skills)}\n")

    for s in skills:
        cat = s["category"] or "—"
        ver = s["version"] or "—"
        status_str = "" if s["status"] == "active" else f" ({s['status']})"
        click.echo(f"  {s['name']}  [{cat}]  v{ver}{status_str}")


@main.command()
@click.argument("query")
@click.option("--limit", "-l", default=20, help="Max results")
@click.option(
    "--db-path",
    default=str(Path.home() / ".hermes" / "skill-forge" / "forge.db"),
    help="Database path",
)
def search(query, limit, db_path):
    """Full-text search across skills."""
    registry = _get_registry(db_path)
    results = registry.search(query, limit=limit)

    if not results:
        click.echo(f"No skills found for: {query}")
        return

    for s in results:
        version = s.get("version", "?")
        category = s.get("category", "")
        cat_str = f" [{category}]" if category else ""
        click.echo(f"  {s['name']} v{version}{cat_str}")
        if s.get("description"):
            click.echo(f"    {s['description'][:80]}")


@main.command(name="status", aliases=["stats"])
@click.option(
    "--db-path",
    default=str(Path.home() / ".hermes" / "skill-forge" / "forge.db"),
    help="Database path",
)
def stats(db_path):
    """Show registry statistics."""
    registry = _get_registry(db_path)
    stats = registry.get_stats()

    click.echo("Skill Forge Registry Status")
    click.echo("=" * 30)
    click.echo(f"Total skills: {stats['total_skills']}")

    if stats["by_status"]:
        click.echo("By status:")
        for s, count in sorted(stats["by_status"].items()):
            click.echo(f"  {s}: {count}")

    if stats["by_category"]:
        click.echo("By category:")
        for cat, count in stats["by_category"].items():
            click.echo(f"  {cat}: {count}")

    click.echo(f"Quality checks: {stats['total_quality_checks']}")
    if stats["skills_with_failures"] > 0:
        click.echo(f"Skills with failures: {stats['skills_with_failures']} ⚠️")
    else:
        click.echo(f"Skills with failures: 0 ✓")
    click.echo(f"DB: {stats['db_path']}")


@main.command()
@click.argument("name")
@click.option(
    "--db-path",
    default=str(Path.home() / ".hermes" / "skill-forge" / "forge.db"),
    help="Database path",
)
def inspect(name, db_path):
    """Show detailed information for a skill."""
    registry = _get_registry(db_path)
    skill = registry.get_skill(name)

    if not skill:
        click.echo(f"✗ Skill not found: {name}", err=True)
        raise SystemExit(1)

    click.echo(f"Name:        {skill['name']}")
    click.echo(f"Category:    {skill['category'] or '—'}")
    click.echo(f"Version:     {skill['version'] or '—'}")
    click.echo(f"Status:      {skill['status']}")
    click.echo(f"Description: {skill['description'] or '—'}")
    click.echo(f"Path:        {skill['path']}")
    click.echo(f"Installed:   {skill['installed_at'] or '—'}")
    click.echo(f"Updated:     {skill['updated_at'] or '—'}")

    # Quality checks
    checks = registry.get_latest_checks(skill["id"])
    if checks:
        click.echo(f"\nQuality Checks ({len(checks)}):")
        for c in checks:
            icon = "✓" if c["passed"] else "✗"
            click.echo(f"  {icon} {c['check_name']}")
            if c["details"]:
                click.echo(f"    {c['details']}")


@main.command()
@click.option(
    "--db-path",
    default=str(Path.home() / ".hermes" / "skill-forge" / "forge.db"),
    help="Database path",
)
def prune(db_path):
    """Remove skills whose files no longer exist on disk."""
    registry = _get_registry(db_path)
    count = registry.prune_stale()
    if count:
        click.echo(f"✓ Pruned {count} stale skill(s)")
    else:
        click.echo("No stale skills found.")


@main.command()
@click.option(
    "--db-path",
    default=str(Path.home() / ".hermes" / "skill-forge" / "forge.db"),
    help="Database path",
)
@click.option("-o", "--output", default=None, help="Write to file instead of stdout")
def export(db_path, output):
    """Export registry as JSON."""
    registry = _get_registry(db_path)
    data = registry.export_json()
    if output:
        Path(output).write_text(data)
        click.echo(f"✓ Exported to {output}")
    else:
        click.echo(data)


@main.command()
@click.option(
    "--skills-dir",
    default=str(Path.home() / ".hermes" / "skills"),
    help="Directory to watch",
)
@click.option(
    "--db-path",
    default=str(Path.home() / ".hermes" / "skill-forge" / "forge.db"),
    help="Database path",
)
@click.option("-i", "--interval", default=300, help="Poll interval in seconds (default: 300)")
@click.option("--once", is_flag=True, help="Run import once and exit (for cron)")
def watch(skills_dir, db_path, interval, once):
    """Watch skills directory and auto-reimport on changes."""
    registry = _get_registry(db_path)

    if once:
        result = import_skills(registry, skills_dir, verbose=True)
        click.echo(f"\nImported: {result['imported']}, Skipped: {result['skipped']}, "
                   f"Failed: {result['failed']}")
        return

    click.echo(f"Watching: {skills_dir}")
    click.echo(f"Poll interval: {interval}s (Ctrl+C to stop)")

    try:
        while True:
            result = import_skills(registry, skills_dir)
            if result["imported"] > 0 or result["failed"] > 0:
                click.echo(f"[{time.strftime('%H:%M:%S')}] "
                           f"imported={result['imported']} "
                           f"skipped={result['skipped']} "
                           f"failed={result['failed']}")
            time.sleep(interval)
    except KeyboardInterrupt:
        click.echo("\nStopped.")


if __name__ == "__main__":
    main()