"""Test fixtures for Skill Forge."""

import tempfile
from pathlib import Path

import pytest

from skill_forge.registry import Registry


@pytest.fixture
def db_path():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    yield path
    Path(path).unlink(missing_ok=True)


@pytest.fixture
def registry(db_path):
    """Create a fresh Registry with a temp database."""
    reg = Registry(db_path)
    yield reg
    # Clean up WAL/SHM files
    for suffix in ("-wal", "-shm"):
        p = Path(str(db_path) + suffix)
        p.unlink(missing_ok=True)
