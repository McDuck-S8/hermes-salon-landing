"""
Crystal v3 — Анализатор ошибок
Читает реальные логи, находит конкретные проблемы
"""

# Revisit: when error pattern definitions, health score calculation, or log sources change. Last touched: 2026-07-02.

import os
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from .config import HERMES_HOME


class ErrorAnalyzer:
    """Анализирует реальные логи ошибок"""

    LOG_DIR = os.path.join(HERMES_HOME, "logs")

    # Паттерны ошибок
    ERROR_PATTERNS = {
        "model_not_supported": {
            "pattern": r"Model (\S+) is not supported",
            "severity": "critical",
            "fix": "Сменить модель в config.yaml",
        },
        "memory_overflow": {
            "pattern": r"Memory at (\d+)/(\d+) chars.*exceed the limit",
            "severity": "high",
            "fix": "Консолидировать memory: удалить старые записи",
        },
        "api_timeout": {
            "pattern": r"API call failed.*APITimeoutError|Request timed out",
            "severity": "medium",
            "fix": "Увеличить timeout или сменить provider",
        },
        "lsp_failure": {
            "pattern": r"lsp\[pyright\] spawn/initialize failed",
            "severity": "low",
            "fix": "Pyright не работает на Windows — отключить или починить",
        },
        "terminal_timeout": {
            "pattern": r"\[Command timed out (\d+)s\]",
            "severity": "medium",
            "fix": "Увеличить timeout или оптимизировать команду",
        },
        "entry_not_found": {
            "pattern": r"No entry matched",
            "severity": "medium",
            "fix": "Проверить что memory entry существует перед update",
        },
        "file_blocked": {
            "pattern": r"BLOCKED: You have called read_file on this exact region",
            "severity": "low",
            "fix": "Не читать один и тот же регион файла повторно",
        },
        "tool_loop": {
            "pattern": r"Tool loop warning: same_tool_failure_warning",
            "severity": "high",
            "fix": "Агент зацикливается — нужно прервать и переключиться",
        },
        "non_retryable": {
            "pattern": r"Non-retryable client error",
            "severity": "critical",
            "fix": "Проверить API ключ и модель",
        },
    }

    def __init__(self):
        self.errors = []
        self.stats = {}

    def analyze(self, hours: int = 24) -> dict:
        """Анализировать логи за последние N часов"""
        self.errors = []
        self.stats = {}

        # Читаем все лог-файлы
        log_files = self._get_log_files()

        for log_file in log_files:
            self._parse_log(log_file, hours)

        # Считаем статистику
        self._compute_stats()

        return {
            "total_errors": len(self.errors),
            "by_type": self.stats,
            "top_errors": self._get_top_errors(5),
            "fixes": self._get_fixes(),
            "health_score": self._health_score(),
        }

    def _get_log_files(self) -> list:
        """Получить список лог-файлов"""
        files = []
        if not os.path.exists(self.LOG_DIR):
            return files

        for f in os.listdir(self.LOG_DIR):
            if f.endswith(".log") or f.endswith(".log.1"):
                path = os.path.join(self.LOG_DIR, f)
                files.append(path)

        return files

    def _parse_log(self, log_file: str, hours: int):
        """Парсить один лог-файл"""
        try:
            cutoff = datetime.now() - timedelta(hours=hours)

            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    # Ищем ERROR и WARNING
                    if "ERROR" not in line and "WARNING" not in line:
                        continue

                    # Проверяем время
                    match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                    if match:
                        try:
                            ts = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
                            if ts < cutoff:
                                continue
                        except ValueError:
                            pass

                    # Ищем паттерны
                    for error_type, info in self.ERROR_PATTERNS.items():
                        if re.search(info["pattern"], line):
                            self.errors.append({
                                "type": error_type,
                                "severity": info["severity"],
                                "fix": info["fix"],
                                "source": os.path.basename(log_file),
                                "line": line.strip()[:200],
                            })
        except Exception:
            pass

    def _compute_stats(self):
        """Считаем статистику"""
        self.stats = Counter(e["type"] for e in self.errors)

    def _get_top_errors(self, n: int) -> list:
        """Топ N ошибок"""
        counter = Counter(e["type"] for e in self.errors)
        return [{"type": t, "count": c} for t, c in counter.most_common(n)]

    def _get_fixes(self) -> list:
        """Уникальные фиксы"""
        seen = set()
        fixes = []
        for e in self.errors:
            if e["fix"] not in seen:
                seen.add(e["fix"])
                fixes.append({
                    "error": e["type"],
                    "severity": e["severity"],
                    "fix": e["fix"],
                })
        return fixes

    def _health_score(self) -> float:
        """Оценка здоровья системы (0-100)"""
        if not self.errors:
            return 100.0

        severity_weights = {"critical": 10, "high": 5, "medium": 2, "low": 1}
        penalty = sum(severity_weights.get(e["severity"], 1) for e in self.errors)
        score = max(0, 100 - penalty)
        return round(score, 1)
