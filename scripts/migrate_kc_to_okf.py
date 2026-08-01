#!/usr/bin/env python3
"""
OKF-Lite Migration — Knowledge Cube → Open Knowledge Format.

Adds three critical fields to the experiences table:
  1. confidence REAL (already exists — DEFAULT 0.5)
  2. expiration_date TEXT (when knowledge expires)
  3. verification_method TEXT (how to verify: manual, automated, cross-reference)

Also ensures kc_entries table has these fields.

Usage:
    python scripts/migrate_kc_to_okf.py          # run migration
    python scripts/migrate_kc_to_okf.py --status  # show current schema
    python scripts/migrate_kc_to_okf.py --test    # run tests
"""

import sqlite3
import os
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "cache" / "knowledge_cube.db"
OKF_BUNDLE_ROOT = Path(__file__).resolve().parent.parent / "knowledge" / "okf"
OKF_SPEC_VERSION = "0.1"


def log(msg: str):
    print(f"[OKF-MIGRATE] {msg}")


def get_db() -> sqlite3.Connection:
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    """Check if a column exists in a table."""
    try:
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
        return column in cols
    except Exception:
        return False


def migrate_experiences(conn: sqlite3.Connection):
    """Add OKF-Lite fields to experiences table."""
    table = "experiences"

    # 1. confidence — already exists, just ensure DEFAULT
    if not column_exists(conn, table, "confidence"):
        log("Adding confidence column...")
        conn.execute(f"ALTER TABLE {table} ADD COLUMN confidence REAL DEFAULT 0.5")
        log("  ✓ confidence REAL DEFAULT 0.5")
    else:
        log("  ✓ confidence already exists")

    # 2. expiration_date — NEW
    if not column_exists(conn, table, "expiration_date"):
        log("Adding expiration_date column...")
        conn.execute(f"ALTER TABLE {table} ADD COLUMN expiration_date TEXT")
        log("  ✓ expiration_date TEXT")
    else:
        log("  ✓ expiration_date already exists")

    # 3. verification_method — NEW
    if not column_exists(conn, table, "verification_method"):
        log("Adding verification_method column...")
        conn.execute(f"ALTER TABLE {table} ADD COLUMN verification_method TEXT DEFAULT 'manual'")
        log("  ✓ verification_method TEXT DEFAULT 'manual'")
    else:
        log("  ✓ verification_method already exists")

    # Set default confidence for existing rows without it
    conn.execute(f"""
        UPDATE {table}
        SET confidence = 0.5
        WHERE confidence IS NULL
    """)
    log("  ✓ Set default confidence=0.5 for NULL rows")

    # Set default verification_method for existing rows
    conn.execute(f"""
        UPDATE {table}
        SET verification_method = 'manual'
        WHERE verification_method IS NULL
    """)
    log("  ✓ Set default verification_method='manual' for NULL rows")

    conn.commit()
    log("Experiences migration complete.")


def migrate_kc_entries(conn: sqlite3.Connection):
    """Create/update kc_entries table with OKF-Lite fields."""
    # Check if table exists
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]

    if "kc_entries" not in tables:
        log("Creating kc_entries table with OKF-Lite fields...")
        conn.execute("""CREATE TABLE IF NOT EXISTS kc_entries (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            tags TEXT DEFAULT '',
            source TEXT DEFAULT '',
            category TEXT DEFAULT '',
            importance INTEGER DEFAULT 5,
            created_at TEXT,
            updated_at TEXT,
            access_count INTEGER DEFAULT 0,
            confidence REAL DEFAULT 0.5,
            expiration_date TEXT,
            verification_method TEXT DEFAULT 'manual'
        )""")
        conn.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS kc_fts USING fts5(
            id, content, tags, source, category
        )""")
        log("  ✓ kc_entries created with OKF-Lite fields")
    else:
        log("kc_entries exists — checking OKF-Lite columns...")
        if not column_exists(conn, "kc_entries", "confidence"):
            conn.execute("ALTER TABLE kc_entries ADD COLUMN confidence REAL DEFAULT 0.5")
            log("  ✓ added confidence")
        if not column_exists(conn, "kc_entries", "expiration_date"):
            conn.execute("ALTER TABLE kc_entries ADD COLUMN expiration_date TEXT")
            log("  ✓ added expiration_date")
        if not column_exists(conn, "kc_entries", "verification_method"):
            conn.execute("ALTER TABLE kc_entries ADD COLUMN verification_method TEXT DEFAULT 'manual'")
            log("  ✓ added verification_method")

    conn.commit()
    log("kc_entries migration complete.")


def show_status(conn: sqlite3.Connection):
    """Show current schema status."""
    for table in ["experiences", "kc_entries"]:
        try:
            cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"\n{table} ({count} rows):")
            for col in cols:
                nullable = "NULL" if col[3] == 0 else "NOT NULL"
                default = f" DEFAULT {col[4]}" if col[4] is not None else ""
                print(f"  {col[1]:25s} {col[2]:10s} {nullable}{default}")
        except Exception as e:
            print(f"\n{table}: {e}")

    # Show OKF-Lite specific stats
    try:
        expired = conn.execute(
            "SELECT COUNT(*) FROM experiences WHERE expiration_date IS NOT NULL AND expiration_date < ?",
            (datetime.now().isoformat(),)
        ).fetchone()[0]
        with_verification = conn.execute(
            "SELECT COUNT(*) FROM experiences WHERE verification_method IS NOT NULL AND verification_method != ''"
        ).fetchone()[0]
        avg_conf = conn.execute(
            "SELECT AVG(confidence) FROM experiences"
        ).fetchone()[0] or 0

        print(f"\nOKF-Lite Stats:")
        print(f"  Average confidence: {avg_conf:.3f}")
        print(f"  With expiration_date: {expired} expired / total set")
        print(f"  With verification_method: {with_verification}")
    except Exception as e:
        print(f"\nOKF-Lite stats error: {e}")


def run_tests(conn: sqlite3.Connection):
    """Test OKF-Lite functionality."""
    print("\n=== OKF-Lite Tests ===\n")

    # Test 1: Insert expired record
    test_id = "okf_test_expired_001"
    test_content = "Test knowledge that expired in 2020"
    expired_date = "2020-01-01T00:00:00"
    now = datetime.now().isoformat()

    conn.execute("""INSERT OR REPLACE INTO experiences
        (ts, content, raw_text, hash, axis_domain, axis_outcome, source, confidence, expiration_date, verification_method)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (now, test_content, test_content, test_id, "test", "success", "test", 0.3, expired_date, "manual"))
    conn.commit()
    log(f"Test 1: Inserted expired record (id={test_id})")

    # Test 2: find_expired_knowledge equivalent
    expired_rows = conn.execute(
        "SELECT id, content, confidence, expiration_date FROM experiences WHERE expiration_date IS NOT NULL AND expiration_date < ?",
        (now,)
    ).fetchall()
    found = any(r["content"] == test_content for r in expired_rows)
    log(f"Test 2: find_expired_knowledge found test record: {'✓ PASS' if found else '✗ FAIL'}")

    # Test 3: confidence-based search (higher confidence first)
    high_conf = conn.execute(
        "SELECT id, content, confidence FROM experiences WHERE content LIKE '%test%' ORDER BY confidence DESC LIMIT 3"
    ).fetchall()
    log(f"Test 3: confidence-ranked search returned {len(high_conf)} results")
    for r in high_conf:
        log(f"    {r['id']}: confidence={r['confidence']:.3f}")

    # Test 4: verification_method
    verified = conn.execute(
        "SELECT id, verification_method FROM experiences WHERE verification_method = 'automated'"
    ).fetchall()
    log(f"Test 4: automated verification count: {len(verified)}")

    # Cleanup test records
    conn.execute("DELETE FROM experiences WHERE id LIKE 'okf_test_%'")
    conn.commit()
    log("Test cleanup: removed test records")

    print("\n=== All Tests Complete ===")


# ═══════════════════════════════════════════════════════════════
# Full OKF Export — OKF SPEC v0.1 compliant bundle on disk
# ═══════════════════════════════════════════════════════════════


def safe_str(value) -> str:
    """Convert DB value to string, with None → empty string."""
    if value is None:
        return ""
    return str(value)


def yaml_list(items_str: str) -> str:
    """Format a tag string into a proper YAML list.
    
    Handles:
    - Comma/space separated: "okf, google, knowledge-format"
    - JSON list: '["source:agent_decisions", "complexity:low"]'
    - Mixed: '["complexity:low"], auto_tagged, auto_tagged'
    - Already clean tags
    """
    items_str = items_str.strip()
    if not items_str:
        return ""

    items = []

    # Extract JSON list part if present
    if "[" in items_str and "]" in items_str:
        json_start = items_str.index("[")
        json_end = items_str.index("]") + 1
        json_part = items_str[json_start:json_end]
        rest = items_str[json_end:].lstrip(",").strip()
        
        import json
        try:
            parsed = json.loads(json_part)
            if isinstance(parsed, list):
                items.extend(str(t) for t in parsed)
        except (json.JSONDecodeError, TypeError):
            pass
        
        # Process remaining text after JSON
        if rest:
            for part in rest.replace(",", " ").split():
                part = part.strip().strip('"').strip("'")
                if part:
                    items.append(part)
    else:
        # Simple comma/space separated
        for t in items_str.replace(",", " ").split():
            t = t.strip().strip('"').strip("'")
            if t:
                items.append(t)

    # Clean tags
    clean = []
    seen = set()
    for t in items:
        t = str(t).strip('"').strip("'").strip()
        # Skip empty, duplicates, and "auto_tagged"
        if not t or t in seen or t in ("auto_tagged", "auto_tag"):
            continue
        # Skip long strings (not tag-like)
        if len(t) > 80:
            continue
        clean.append(t)
        seen.add(t)

    if not clean:
        return ""
    return "\n" + "\n".join(f"  - {t}" for t in clean[:10])


def concept_to_md(row: dict, source_table: str) -> str:
    """Convert a DB row into an OKF-conformant .md file."""
    now = datetime.now().isoformat()

    # Derive type from available fields
    if source_table == "experiences":
        concept_type = safe_str(row.get("axis_domain", "Experience")) or "Experience"
        title = safe_str(row.get("content", ""))[:80]
        description = safe_str(row.get("axis_outcome", ""))[:200]
        resource = safe_str(row.get("source", ""))
        tags_raw = safe_str(row.get("tags", ""))
        ts = safe_str(row.get("ts", now))
        body = safe_str(row.get("raw_text", "") or row.get("content", ""))
    else:
        concept_type = safe_str(row.get("category", "Knowledge")) or "Knowledge"
        title = safe_str(row.get("content", ""))[:80]
        description = ""
        resource = safe_str(row.get("source", ""))
        tags_raw = safe_str(row.get("tags", ""))
        ts = safe_str(row.get("updated_at", "") or row.get("created_at", now))
        body = safe_str(row.get("content", ""))

    # Default values
    confidence = row.get("confidence", 0.5)
    expiration_date = safe_str(row.get("expiration_date", ""))
    verification_method = safe_str(row.get("verification_method", "manual"))
    importance = row.get("importance", 5)

    # Build YAML frontmatter
    fm = f"---\n"
    fm += f"type: {concept_type}\n"
    if title:
        fm += f"title: \"{title.replace(chr(34), chr(39))}\"\n"
    if description:
        fm += f"description: \"{description.replace(chr(34), chr(39))}\"\n"
    if resource:
        fm += f"resource: {resource}\n"
    if tags_raw:
        yl = yaml_list(tags_raw)
        if yl:
            fm += f"tags:{yl}\n"
    fm += f"timestamp: {ts}\n"
    fm += f"confidence: {float(confidence):.3f}\n"
    if expiration_date:
        fm += f"expiration_date: {expiration_date}\n"
    fm += f"verification_method: {verification_method}\n"
    fm += f"source_table: {source_table}\n"
    fm += f"importance: {int(importance)}\n"
    fm += "---\n\n"
    fm += body.rstrip() + "\n"

    return fm


def get_entries_for_export(conn: sqlite3.Connection) -> list[dict]:
    """Fetch all rows from both tables for export."""
    entries = []

    # kc_entries
    try:
        rows = conn.execute("SELECT * FROM kc_entries").fetchall()
        for r in rows:
            d = dict(r)
            d["_source_table"] = "kc_entries"
            entries.append(d)
    except Exception:
        pass

    # experiences (limit to 1000 to avoid explosion)
    try:
        rows = conn.execute(
            "SELECT * FROM experiences ORDER BY ts DESC LIMIT 1000"
        ).fetchall()
        for r in rows:
            d = dict(r)
            d["_source_table"] = "experiences"
            entries.append(d)
    except Exception:
        pass

    return entries


def determine_subdir(entry: dict) -> str:
    """Determine OKF subdirectory for an entry based on category/domain."""
    if entry["_source_table"] == "experiences":
        domain = safe_str(entry.get("axis_domain", "unknown"))
        return f"experiences/{domain.lower().replace(' ', '_')[:40]}"
    cat = safe_str(entry.get("category", "uncategorized"))
    return f"knowledge/{cat.lower().replace(' ', '_').replace('/', '_')[:40]}"


def write_log_entry(log_path: Path, action: str, concept_id: str, detail: str = ""):
    """Append to log.md per OKF SPEC §7."""
    now = datetime.now().isoformat()
    line = f"| {now} | {action} | {concept_id} | {detail} |\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)


def export_to_okf(conn: sqlite3.Connection, export_dir: str = None):
    """Export Knowledge Cube to OKF bundle directory."""
    if export_dir:
        bundle_root = Path(export_dir)
    else:
        bundle_root = OKF_BUNDLE_ROOT

    log(f"Exporting to OKF bundle: {bundle_root}")
    log(f"OKF SPEC version: {OKF_SPEC_VERSION}")

    # Create bundle root
    os.makedirs(bundle_root, exist_ok=True)

    # Fetch all entries
    entries = get_entries_for_export(conn)
    log(f"Total entries to export: {len(entries)} (max 1000 experiences)")

    if not entries:
        log("No entries found. Nothing to export.")
        return

    # Track subdirectories for index.md generation
    subdirs: dict[str, list[dict]] = {}
    written = 0
    skipped = 0

    for entry in entries:
        subdir = determine_subdir(entry)
        target_dir = bundle_root / subdir
        os.makedirs(target_dir, exist_ok=True)

        # Generate filename: hash-based for stability
        entry_id = safe_str(entry.get("id", ""))
        if not entry_id:
            entry_id = hashlib.md5(
                safe_str(entry.get("content", "")).encode()
            ).hexdigest()[:12]

        filename = f"{entry_id}.md"
        filepath = target_dir / filename

        # Generate content
        md_content = concept_to_md(entry, entry["_source_table"])

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)
        written += 1

        # Track for index
        if subdir not in subdirs:
            subdirs[subdir] = []
        concept_type = (
            safe_str(entry.get("axis_domain", "Experience"))
            if entry["_source_table"] == "experiences"
            else safe_str(entry.get("category", "Knowledge"))
        )
        title = safe_str(entry.get("content", ""))[:80]
        subdirs[subdir].append({
            "id": entry_id,
            "title": title,
            "type": concept_type,
        })

    # ── Generate index.md per subdirectory (OKF §6) ──
    for subdir, concepts in sorted(subdirs.items()):
        index_path = bundle_root / subdir / "index.md"
        parts = subdir.split("/")
        dir_name = parts[-1].replace("_", " ").title()

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(f"# {dir_name}\n\n")
            f.write(f"OKF bundle directory. {len(concepts)} concepts.\n\n")
            f.write("## Concepts\n\n")
            f.write("| ID | Type | Title |\n")
            f.write("|-----|------|-------|\n")
            for c in concepts:
                title_esc = c["title"].replace("|", "/")
                f.write(f"| [{c['id']}]({c['id']}.md) | {c['type']} | {title_esc} |\n")
            f.write("\n")

        log(f"  index.md: {subdir}/ ({len(concepts)} concepts)")

    # ── Generate root index.md ──
    index_path = bundle_root / "index.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"okf_version: \"{OKF_SPEC_VERSION}\"\n")
        f.write("---\n\n")
        f.write("# Hermes Knowledge Cube — OKF Bundle\n\n")
        f.write(f"Exported from Knowledge Cube (SQLite).\n\n")
        f.write(f"- **Total concepts:** {written}\n")
        f.write(f"- **OKF version:** {OKF_SPEC_VERSION}\n")
        f.write(f"- **Exported at:** {datetime.now().isoformat()}\n")
        f.write(f"- **Source:** `{DB_PATH}`\n\n")

        # Count by subdir
        f.write("## Bundle Layout\n\n")
        f.write("| Directory | Concepts |\n")
        f.write("|-----------|----------|\n")
        for subdir, concepts in sorted(subdirs.items()):
            f.write(f"| [{subdir}/]({subdir}/index.md) | {len(concepts)} |\n")
        f.write("\n")

        f.write("## Usage\n\n")
        f.write("This bundle is an OKF v0.1 compliant knowledge package.\n")
        f.write("See [OKF SPEC](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) for details.\n")
        f.write("\n### Consumption by agents\n\n")
        f.write("- Browse `index.md` files for navigation.\n")
        f.write("- Read `log.md` for change history.\n")
        f.write("- Parse YAML frontmatter for metadata.\n")
        f.write("- Follow cross-links between concepts.\n")
        f.write("\n")

    log(f"  index.md: root/ ({len(subdirs)} directories)")

    # ── Generate log.md (OKF §7) ──
    log_path = bundle_root / "log.md"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("# OKF Bundle Log\n\n")
        f.write("| Timestamp | Action | Concept | Detail |\n")
        f.write("|-----------|--------|---------|--------|\n")

    write_log_entry(log_path, "EXPORT", "*", f"Initial export: {written} concepts, {len(subdirs)} directories")
    log(f"  log.md: created")

    log(f"Done. Exported {written} concepts to {bundle_root}")
    log(f"  {len(subdirs)} subdirectories with index.md")
    if skipped:
        log(f"  {skipped} entries skipped (no content)")


def validate_bundle(bundle_root: Path = None):
    """Validate OKF bundle against OKF SPEC v0.1."""
    if bundle_root is None:
        bundle_root = OKF_BUNDLE_ROOT

    print(f"\n=== OKF Bundle Validation ===\n")
    errors = 0
    warnings = 0

    if not bundle_root.exists():
        print(f"✗ Bundle root not found: {bundle_root}")
        return False

    # Check index.md exists
    index_path = bundle_root / "index.md"
    if not index_path.exists():
        print(f"✗ Missing root index.md")
        errors += 1
    else:
        print(f"✓ root/index.md exists")

    # Check log.md exists
    log_path = bundle_root / "log.md"
    if not log_path.exists():
        print(f"✗ Missing root log.md")
        errors += 1
    else:
        print(f"✓ root/log.md exists")

    # Walk all .md files and validate frontmatter
    md_files = sorted(bundle_root.rglob("*.md"))
    concepts = [f for f in md_files if f.name not in ("index.md", "log.md")]

    print(f"\n  {len(concepts)} concept files, {len(md_files) - len(concepts)} index/log files")

    type_count = {}
    for fpath in concepts:
        rel = fpath.relative_to(bundle_root)
        content = fpath.read_text(encoding="utf-8")

        # Check frontmatter
        if not content.startswith("---"):
            print(f"✗ {rel}: missing frontmatter")
            errors += 1
            continue

        # Parse frontmatter
        parts = content.split("---", 2)
        if len(parts) < 3:
            print(f"✗ {rel}: malformed frontmatter (no closing ---)")
            errors += 1
            continue

        fm = parts[1].strip()
        body = parts[2].strip()

        # Check required fields
        if "type:" not in fm:
            print(f"✗ {rel}: missing REQUIRED 'type' field")
            errors += 1
        else:
            # Extract type value
            for line in fm.split("\n"):
                if line.strip().startswith("type:"):
                    t = line.split(":", 1)[1].strip()
                    type_count[t] = type_count.get(t, 0) + 1
                    break

        if not body:
            print(f"⚠ {rel}: empty body")
            warnings += 1

    # Summary
    print(f"\n=== Validation Summary ===")
    if errors:
        print(f"✗ {errors} errors, {warnings} warnings")
    else:
        print(f"✓ PASSED: 0 errors, {warnings} warnings")

    if type_count:
        print(f"\nConcept types:")
        for t, n in sorted(type_count.items(), key=lambda x: -x[1])[:10]:
            print(f"  {t}: {n}")

    return errors == 0


if __name__ == "__main__":
    conn = get_db()

    if "--status" in sys.argv:
        show_status(conn)
    elif "--test" in sys.argv:
        run_tests(conn)
    elif "--export" in sys.argv:
        export_dir = None
        if "--export-dir" in sys.argv:
            idx = sys.argv.index("--export-dir")
            if idx + 1 < len(sys.argv):
                export_dir = sys.argv[idx + 1]
        export_to_okf(conn, export_dir)
    elif "--validate" in sys.argv:
        bundle_root = None
        if "--validate-dir" in sys.argv:
            idx = sys.argv.index("--validate-dir")
            if idx + 1 < len(sys.argv):
                bundle_root = Path(sys.argv[idx + 1])
        validate_bundle(bundle_root)
    else:
        log("Starting OKF-Lite migration...")
        log(f"Database: {DB_PATH}")
        log(f"Size: {DB_PATH.stat().st_size / 1024:.1f} KB")
        print()

        migrate_experiences(conn)
        print()
        migrate_kc_entries(conn)
        print()

        show_status(conn)
        print()
        run_tests(conn)

    conn.close()
