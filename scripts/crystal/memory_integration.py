"""
Crystal v3 — Модуль 11: Memory Integration
Читает USER.md + MEMORY.md
"""

# Revisit: when memory integration sources, USER.md/MEMORY.md parsing, or context summary logic changes. Last touched: 2026-07-02.

import os
from .config import HERMES_HOME


class MemoryIntegration:
    """Читает и понимает memory пользователя"""

    def __init__(self):
        self.memories_dir = HERMES_HOME

    def read(self) -> list:
        """
        Читает USER.md + MEMORY.md
        Возвращает список записей
        """
        entries = []

        # USER.md
        user_path = os.path.join(self.memories_dir, "USER.md")
        if os.path.exists(user_path):
            content = self._read_file(user_path)
            entries.extend(self._parse_user(content))

        # MEMORY.md
        memory_path = os.path.join(self.memories_dir, "MEMORY.md")
        if os.path.exists(memory_path):
            content = self._read_file(memory_path)
            entries.extend(self._parse_memory(content))

        return entries

    def _read_file(self, path: str) -> str:
        """Безопасное чтение файла"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""

    def _parse_user(self, content: str) -> list:
        """Парсит USER.md в записи"""
        entries = []
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                entries.append({
                    "type": "user_profile",
                    "content": line,
                    "source": "USER.md",
                })
        return entries

    def _parse_memory(self, content: str) -> list:
        """Парсит MEMORY.md в записи"""
        entries = []
        current_section = ""

        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("## "):
                current_section = line[3:]
            elif line and not line.startswith("#") and current_section:
                entries.append({
                    "type": "memory",
                    "section": current_section,
                    "content": line,
                    "source": "MEMORY.md",
                })

        return entries

    def write_preference(self, key: str, value: str):
        """Записать новое предпочтение в USER.md"""
        path = os.path.join(self.memories_dir, "USER.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)

        content = ""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

        # Проверяем есть ли уже
        if key.lower() in content.lower():
            return  # уже есть

        # Добавляем
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n{key}: {value}")

    def get_context_summary(self) -> str:
        """Краткая сводка из memory"""
        entries = self.read()
        if not entries:
            return "Memory пуста"

        user_entries = [e for e in entries if e["type"] == "user_profile"]
        memory_entries = [e for e in entries if e["type"] == "memory"]

        lines = [f"USER: {len(user_entries)} записей, MEMORY: {len(memory_entries)} записей"]
        return "\n".join(lines)
