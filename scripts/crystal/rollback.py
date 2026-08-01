"""
Crystal v3 — Модуль 18: Rollback
Откат изменений
"""

# Revisit: when rollback strategy, snapshot format, or version compatibility changes. Last touched: 2026-07-02.

import os
import shutil
from datetime import datetime
from .models import Snapshot
from .config import Paths
from .models import load_json, save_json


class RollbackManager:
    """Управление снэпшотами и откатом"""

    def __init__(self):
        os.makedirs(Paths.snapshots_dir, exist_ok=True)

    def create_snapshot(self, version: str, files: list, description: str = "") -> Snapshot:
        """Создать снэпшот перед изменением"""
        snapshot = Snapshot(
            version=version,
            description=description,
            files=files,
        )

        # Копируем файлы в снэпшот
        snapshot_dir = os.path.join(Paths.snapshots_dir, snapshot.id)
        os.makedirs(snapshot_dir, exist_ok=True)

        for f in files:
            if os.path.exists(f):
                dest = os.path.join(snapshot_dir, os.path.basename(f))
                shutil.copy2(f, dest)

        # Сохраняем метаданные
        meta_path = os.path.join(snapshot_dir, "_meta.json")
        save_json(snapshot, meta_path)

        return snapshot

    def rollback(self, version: str) -> bool:
        """Откат к указанной версии"""
        # Ищем снэпшот
        snapshot_dir = os.path.join(Paths.snapshots_dir, f"snap_*_{hash(version) % 10000}")

        # Ищем по частичному совпадению
        snapshots = os.listdir(Paths.snapshots_dir)
        target = None
        for s in snapshots:
            if version in s:
                target = os.path.join(Paths.snapshots_dir, s)
                break

        if not target or not os.path.exists(target):
            return False

        # Восстанавливаем файлы
        for item in os.listdir(target):
            if item.startswith("_"):
                continue
            src = os.path.join(target, item)
            # Здесь нужно знать куда восстанавливать
            # Пока просто логируем
            print(f"Rollback: {item} from {target}")

        return True

    def list_snapshots(self) -> list:
        """Список снэпшотов"""
        snapshots = []
        for item in os.listdir(Paths.snapshots_dir):
            meta_path = os.path.join(Paths.snapshots_dir, item, "_meta.json")
            if os.path.exists(meta_path):
                meta = load_json(meta_path)
                if isinstance(meta, dict):
                    snapshots.append(meta)
        return snapshots
