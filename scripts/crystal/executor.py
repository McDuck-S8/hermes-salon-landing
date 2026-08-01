"""Crystal v3 — Исполнитель предложений
Применяет предложения автоматически
"""

# Revisit: when proposal execution actions, skill creation/patching, or dox updates change. Last touched: 2026-07-02.

import os
import re
from datetime import datetime
from .models import Proposal, Signal, Pattern, KnowledgeEntry
from .config import Paths, SKILLS_DIR, HERMES_HOME, DEPARTMENTS

# Import PRINCIPLE/ARTIFACT logging
from .core import log_principle, log_artifact


class ProposalExecutor:
    """Применяет предложения — создаёт/патчит скиллы, обновляет DOX"""

    def __init__(self, config=None):
        self.config = config or {}
        self.dry_run = self.config.get("dry_run", False)
        self.applied = []

    def execute(self, proposals: list) -> list:
        """Применить предложения"""
        results = []
        for proposal in proposals:
            result = self._execute_one(proposal)
            results.append(result)
            if result["success"]:
                proposal.applied = True
                self.applied.append(proposal)
        return results

    def _execute_one(self, proposal: Proposal) -> dict:
        """Выполнить одно предложение"""
        proposal_id = f"{proposal.action}_{hash(proposal.description) % 10000}"
        
        # PRINCIPLE: Log what principle/lesson drives this execution
        log_principle(
            principle=f"Executor: applying {proposal.action} for {proposal.department}",
            action=f"execute_{proposal.action}",
            proposal_id=proposal_id
        )
        
        try:
            if proposal.action == "create_skill":
                result = self._create_skill(proposal)
            elif proposal.action == "patch_skill":
                result = self._patch_skill(proposal)
                # Fallback: если скилла нет — создаём новый
                if not result.get("success") and "не найден" in result.get("error", ""):
                    result = self._create_skill(proposal)
                return result
            elif proposal.action == "update_dox":
                result = self._update_dox(proposal)
            elif proposal.action == "update_memory":
                result = self._update_memory(proposal)
            # Маппинг действий из conversation_analyzer
            elif proposal.action in ("implement_idea", "create_feature", "fix_gap", "optimize"):
                result = self._create_skill(proposal)
            elif proposal.action in ("fix_problem", "try_experiment"):
                result = self._patch_skill(proposal)
            else:
                result = {"success": False, "error": f"Неизвестное действие: {proposal.action}"}
        except Exception as e:
            result = {"success": False, "error": str(e)}
        
        # ARTIFACT: Log the result
        if result.get("success"):
            artifact_path = result.get("path", result.get("would_create", result.get("would_patch", result.get("would_update", "executed"))))
            log_artifact(
                artifact_path=artifact_path,
                action=f"execute_{proposal.action}",
                proposal_id=proposal_id,
                success=True
            )
        else:
            log_artifact(
                artifact_path="none",
                action=f"execute_{proposal.action}",
                proposal_id=proposal_id,
                success=False
            )
        
        return result

    def _create_skill(self, proposal: Proposal) -> dict:
        """Создать новый скилл с РЕАЛЬНЫМ контентом из ошибок"""
        dept = proposal.department

        # Проверяем существующие скиллы — пропускаем только ТОЧНЫЕ дубликаты
        if os.path.exists(SKILLS_DIR):
            for d in os.listdir(SKILLS_DIR):
                if d.startswith(f"crystal-{dept}-"):
                    skill_file = os.path.join(SKILLS_DIR, d, "SKILL.md")
                    if os.path.exists(skill_file):
                        try:
                            with open(skill_file, "r", encoding="utf-8") as f:
                                content = f.read()
                            # Точное сравнение purpose
                            if "## Purpose" in content:
                                purpose = content.split("## Purpose")[1].split("##")[0].strip()
                                if purpose.lower() == proposal.description.lower():
                                    return {"success": False, "error": f"Точный дубликат: {d}"}
                        except Exception:
                            pass

        desc_hash = abs(hash(proposal.description)) % 10000
        name = f"crystal-{dept}-{desc_hash}"
        skill_dir = os.path.join(SKILLS_DIR, name)
        skill_file = os.path.join(skill_dir, "SKILL.md")

        if os.path.exists(skill_file):
            return {"success": False, "error": f"Скилл {name} уже существует"}

        if self.dry_run:
            return {"success": True, "dry_run": True, "would_create": skill_file}

        # Анализируем ошибки для генерации реального контента
        error_content = self._generate_error_content(dept, proposal)

        os.makedirs(skill_dir, exist_ok=True)

        content = f"""---
name: {name}
description: Crystal v3: {proposal.description[:80]}
category: {dept}
created_by: crystal-v3
created_at: {datetime.now().isoformat()}
---

# {name}

## Purpose
{proposal.description}

## Errors Found
{error_content['errors']}

## Recommended Fixes
{error_content['fixes']}

## Department
{dept}

## Created
{datetime.now().isoformat()}
"""

        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(content)

        return {"success": True, "action": "created", "path": skill_file}

    def _generate_error_content(self, dept: str, proposal: Proposal) -> dict:
        """Генерировать контент для скилла из описания proposal"""
        # Используем описание proposal вместо тяжёлого анализа логов
        desc = proposal.description
        return {
            "errors": f"Обнаружено из анализа сигналов: {desc}",
            "fixes": f"Рекомендация: создать/дополнить скилл для отдела {dept}",
        }

    def _patch_skill(self, proposal: Proposal) -> dict:
        """Патч существующего скилла — добавить секцию из предложения"""
        dept = proposal.department
        
        # Ищем скилл по нескольким паттернам
        skill_file = None
        patterns = [
            os.path.join(SKILLS_DIR, dept, "SKILL.md"),
            os.path.join(SKILLS_DIR, f"crystal-{dept}-auto", "SKILL.md"),
            os.path.join(SKILLS_DIR, f"{dept}-auto", "SKILL.md"),
        ]
        
        for pattern in patterns:
            if os.path.exists(pattern):
                skill_file = pattern
                break
        
        if not skill_file:
            # Ищем по содержимому
            for item in os.listdir(SKILLS_DIR):
                if dept in item.lower() and os.path.isdir(os.path.join(SKILLS_DIR, item)):
                    candidate = os.path.join(SKILLS_DIR, item, "SKILL.md")
                    if os.path.exists(candidate):
                        skill_file = candidate
                        break
        
        if not skill_file:
            return {"success": False, "error": f"Скилл для {dept} не найден"}

        if self.dry_run:
            return {"success": True, "dry_run": True, "would_patch": skill_file}

        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Добавляем секцию
        patch_section = f"\n\n## Crystal Patch ({datetime.now().strftime('%Y-%m-%d')})\n{proposal.description}\n"

        if "Crystal Patch" not in content:
            content += patch_section
            with open(skill_file, "w", encoding="utf-8") as f:
                f.write(content)

        return {"success": True, "action": "patched", "path": skill_file}

    def _update_dox(self, proposal: Proposal) -> dict:
        """Обновить AGENTS.md"""
        agents_file = os.path.join(HERMES_HOME, "AGENTS.md")

        if not os.path.exists(agents_file):
            return {"success": False, "error": "AGENTS.md не найден"}

        if self.dry_run:
            return {"success": True, "dry_run": True, "would_update": agents_file}

        with open(agents_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Добавляем Crystal note
        note = f"\n\n### Crystal Update ({datetime.now().strftime('%Y-%m-%d')})\n{proposal.description}\n"

        if "Crystal Update" not in content:
            content += note
            with open(agents_file, "w", encoding="utf-8") as f:
                f.write(content)

        return {"success": True, "action": "updated", "path": agents_file}

    def _update_memory(self, proposal: Proposal) -> dict:
        """Обновить MEMORY.md"""
        memory_file = os.path.join(HERMES_HOME, "MEMORY.md")

        if not os.path.exists(memory_file):
            os.makedirs(os.path.dirname(memory_file), exist_ok=True)

        if self.dry_run:
            return {"success": True, "dry_run": True, "would_update": memory_file}

        note = f"\n\n## Crystal ({datetime.now().strftime('%Y-%m-%d')})\n{proposal.description}\n"

        with open(memory_file, "a", encoding="utf-8") as f:
            f.write(note)

        return {"success": True, "action": "updated", "path": memory_file}