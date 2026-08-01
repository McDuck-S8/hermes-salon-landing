"""
Crystal v3 — Модуль 13: Versioning
История изменений
"""

# Revisit: when versioning format, changelog entries, or release tracking changes. Last touched: 2026-07-02.

import os
from .models import ChangelogEntry
from .config import Paths
from .models import load_json, save_json


class VersionManager:
    """Управление changelog"""

    def __init__(self):
        pass

    def get_changelog(self) -> list:
        """Получить весь changelog"""
        return load_json(Paths.changelog, ChangelogEntry)

    def add_entry(self, description: str, reason: str = "", effect: str = "", alternatives: list = None) -> ChangelogEntry:
        """Добавить запись"""
        changelog = self.get_changelog()

        version = f"v{len(changelog) + 1}.0"
        entry = ChangelogEntry(
            version=version,
            description=description,
            reason=reason,
            effect=effect,
            alternatives=alternatives or [],
        )

        changelog.append(entry)
        save_json(changelog, Paths.changelog)

        return entry

    def get_recent(self, n: int = 10) -> list:
        """Получить последние N записей"""
        changelog = self.get_changelog()
        return changelog[-n:]

    def get_by_version(self, version: str) -> ChangelogEntry:
        """Найти запись по версии"""
        changelog = self.get_changelog()
        for entry in changelog:
            if entry.version == version:
                return entry
        return None
