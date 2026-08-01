"""
Crystal v3 — Модуль 17: Automated Testing
Тест перед применением
"""

# Revisit: when test levels, validation criteria, or dry-run behavior changes. Last touched: 2026-07-02.

import os
import re
import ast
from .models import Proposal, TestResult


class ProposalTester:
    """Тест proposal перед применением"""

    def __init__(self, config=None):
        self.config = config or {}
        self.default_level = self.config.get("default_level", "quick")

    def test(self, proposal: Proposal) -> TestResult:
        """Протестировать proposal"""
        level = "full" if proposal.action == "architecture_change" else self.default_level

        if level == "quick":
            return self._quick_test(proposal)
        elif level == "standard":
            return self._standard_test(proposal)
        else:
            return self._full_test(proposal)

    def _quick_test(self, proposal: Proposal) -> TestResult:
        """Быстрый тест — проверка синтаксиса"""
        errors = []

        # Проверяем что описание не пустое
        if not proposal.description:
            errors.append("Пустое описание")

        # Проверяем тип действия
        valid_actions = [
            "create_skill", "patch_skill", "update_dox",
            "update_memory", "new_tool", "architecture_change",
            "config_change", "delete",
        ]
        if proposal.action not in valid_actions:
            errors.append(f"Неизвестный тип действия: {proposal.action}")

        # Проверяем отдел
        if not proposal.department:
            errors.append("Не указан отдел")

        passed = len(errors) == 0
        return TestResult(
            target="proposal",
            name=f"quick_test_{proposal.id}",
            level="quick",
            passed=passed,
            details="; ".join(errors) if errors else "OK",
        )

    def _standard_test(self, proposal: Proposal) -> TestResult:
        """Стандартный тест — проверка что proposal рабочий"""
        errors = []

        # Быстрый тест
        quick = self._quick_test(proposal)
        if not quick.passed:
            return quick

        # Дополнительные проверки
        if proposal.action == "create_skill":
            if len(proposal.description) < 20:
                errors.append("Описание слишком короткое для создания скилла")

        if proposal.action == "patch_skill":
            if "patch" not in proposal.description.lower():
                errors.append("Нет конкретики что патчить")

        if proposal.action == "architecture_change":
            errors.append("Architecture change требует полного теста")

        passed = len(errors) == 0
        return TestResult(
            target="proposal",
            name=f"standard_test_{proposal.id}",
            level="standard",
            passed=passed,
            details="; ".join(errors) if errors else "OK",
        )

    def _full_test(self, proposal: Proposal) -> TestResult:
        """Полный тест — проверка всех зависимостей"""
        errors = []

        # Стандартный тест
        standard = self._standard_test(proposal)
        if not standard.passed:
            return standard

        # Проверяем что целевой файл существует (если patch)
        if proposal.action == "patch_skill":
            # Ищем упоминания файлов в описании
            file_matches = re.findall(r'[\w/]+\.\w+', proposal.description)
            for f in file_matches:
                if os.path.exists(f):
                    # Проверяем Python syntax
                    if f.endswith('.py'):
                        try:
                            with open(f, 'r') as fh:
                                ast.parse(fh.read())
                        except SyntaxError as e:
                            errors.append(f"Syntax error in {f}: {e}")

        passed = len(errors) == 0
        return TestResult(
            target="proposal",
            name=f"full_test_{proposal.id}",
            level="full",
            passed=passed,
            details="; ".join(errors) if errors else "OK",
        )
