"""
Crystal v3 — Модуль 9: Staleness Detector
Проверяет что устарело
"""

# Revisit: when staleness thresholds, skill age checks, or config freshness rules change. Last touched: 2026-07-02.

import os
import time
from .models import StalenessItem
from .config import SKILLS_DIR, CONFIG_PATH


class StalenessDetector:
    """Проверяет актуальность скиллов, зависимостей, док"""

    def __init__(self, config=None):
        self.config = config or {}
        self.skill_stale_days = self.config.get("skill_stale_days", 30)
        self.dep_stale_days = self.config.get("dependency_stale_days", 60)

    def check(self) -> list:
        """Проверить всё на актуальность"""
        items = []
        items.extend(self._check_skills())
        items.extend(self._check_config())
        return items

    def _check_skills(self) -> list:
        """Проверить скиллы"""
        items = []
        if not os.path.exists(SKILLS_DIR):
            return items

        now = time.time()
        stale_threshold = now - (self.skill_stale_days * 86400)

        for item in os.listdir(SKILLS_DIR):
            item_path = os.path.join(SKILLS_DIR, item)
            if not os.path.isdir(item_path):
                continue

            # Проверяем SKILL.md
            skill_file = os.path.join(item_path, "SKILL.md")
            if os.path.exists(skill_file):
                mtime = os.path.getmtime(skill_file)
                if mtime < stale_threshold:
                    days_old = int((now - mtime) / 86400)
                    items.append(StalenessItem(
                        type="skill",
                        name=item,
                        stale_days=days_old,
                        action="update",
                    ))

        return items

    def _check_config(self) -> list:
        """Проверить конфиг"""
        items = []
        if not os.path.exists(CONFIG_PATH):
            return items

        now = time.time()
        mtime = os.path.getmtime(CONFIG_PATH)
        stale_threshold = now - (self.dep_stale_days * 86400)

        if mtime < stale_threshold:
            days_old = int((now - mtime) / 86400)
            items.append(StalenessItem(
                type="config",
                name="config.yaml",
                stale_days=days_old,
                action="review",
            ))

        return items
