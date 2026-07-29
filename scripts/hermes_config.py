"""
Hermes Config — Unified configuration for all scripts.

Single source of truth for:
  - HERMES_HOME path resolution (was 5 different strategies)
  - DB connections (was N× sqlite3.connect() calls)
  - Logging (was duplicated in 50+ files)

Import from anywhere in scripts/:
    from hermes_config import HERMES_HOME, get_db, log

No external dependencies — stdlib only.
"""

import json
import logging
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── HERMES_HOME resolution ──────────────────────────────────────────
# Priority: env var > portable detection > ~/.hermes fallback
#
# Portable detection: if cache/event_bus.json exists next to the scripts/
# parent directory, that's our home.  This handles the common case where
# hermes is cloned/copied to an arbitrary location (e.g. D:\Portable_Soft\hermes).

def _resolve_hermes_home() -> Path:
    """Resolve HERMES_HOME with a single, deterministic strategy."""
    # 1. Environment variable (explicit override)
    env = os.environ.get("HERMES_HOME", "").strip()
    if env:
        return Path(env)

    # 2. Portable detection: walk up from this file to find cache/event_bus.json
    #    This handles D:/Portable_Soft/hermes style installations.
    here = Path(__file__).resolve().parent          # scripts/
    project_root = here.parent                      # D:/Portable_Soft/hermes
    if (project_root / "cache" / "event_bus.json").exists():
        return project_root
    if (project_root / "cache").is_dir():
        return project_root

    # 3. Fallback: ~/.hermes (standard installation)
    return Path.home() / ".hermes"


HERMES_HOME: Path = _resolve_hermes_home()

# ── Derived paths ───────────────────────────────────────────────────
CACHE_DIR = HERMES_HOME / "cache"
LOGS_DIR = HERMES_HOME / "logs"
MEMORIES_DIR = HERMES_HOME / "memories"
SCRIPTS_DIR = HERMES_HOME / "scripts"
STATE_DB = HERMES_HOME / "state.db"
CUBE_DB = CACHE_DIR / "knowledge_cube.db"
FIXES_DB = CACHE_DIR / "verified_fixes.db"

# Ensure common dirs exist (safe to call multiple times)
for _d in (CACHE_DIR, LOGS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ── Database connections ────────────────────────────────────────────

def get_db(db_path: Optional[Path] = None, timeout: float = 5.0) -> Optional[sqlite3.Connection]:
    """Get a SQLite connection with WAL mode and row_factory.

    Args:
        db_path: Path to the database file.  Defaults to state.db.
        timeout: Connection timeout in seconds.

    Returns:
        sqlite3.Connection or None if file doesn't exist / error.
    """
    if db_path is None:
        db_path = STATE_DB
    if not db_path.exists():
        return None
    try:
        conn = sqlite3.connect(str(db_path), timeout=timeout)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    except Exception:
        return None


def db_count(conn: sqlite3.Connection, table: str, allowed: frozenset = frozenset()) -> int:
    """Count rows in a table.  Uses allowlist to prevent SQL injection."""
    if allowed and table not in allowed:
        raise ValueError(f"Table '{table}' not in allowlist")
    try:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    except Exception:
        return 0


def db_fetch_all(conn: sqlite3.Connection, sql: str, params=()) -> list[dict]:
    """Fetch all rows as list of dicts."""
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def db_tables(conn: sqlite3.Connection) -> list[str]:
    """Get list of tables in a SQLite database."""
    try:
        return [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]
    except Exception:
        return []


# ── Logging ─────────────────────────────────────────────────────────

_logger_cache: dict[str, logging.Logger] = {}


def log(msg: str, level: str = "INFO", name: str = "hermes"):
    """Log to both console and a per-component file.

    Args:
        msg: Log message.
        level: Log level (DEBUG, INFO, WARNING, ERROR).
        name: Logger name — used as the log file name (e.g. "autonomous_agent").
    """
    if name not in _logger_cache:
        logger = logging.getLogger(f"hermes.{name}")
        logger.setLevel(logging.DEBUG)
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, level.upper(), logging.INFO))
        ch.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s",
                                          datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(ch)
        # File handler
        log_file = LOGS_DIR / f"{name}.log"
        try:
            fh = logging.FileHandler(str(log_file), encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s",
                                              datefmt="%Y-%m-%d %H:%M:%S"))
            logger.addHandler(fh)
        except Exception:
            pass
        _logger_cache[name] = logger

    logger = _logger_cache[name]
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, msg)


def log_json(data: dict, name: str = "hermes"):
    """Append a structured JSON entry to the log file."""
    log_file = LOGS_DIR / f"{name}.log"
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except Exception:
        pass
