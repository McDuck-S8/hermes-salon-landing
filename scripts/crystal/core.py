"""Crystal v3 — Главный движок
CrystalEngine — оркестрирует все 23 модуля
"""

# Revisit: when crystal module logic, departments, or cycle phases change. Last touched: 2026-07-03.

import os
import sys
import json
import time
from datetime import datetime

# Добавляем scripts/ в путь для session_recall
_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from .config import (
    CACHE_DIR, Paths, DEPARTMENTS, DEFAULT_CONFIG,
    ensure_dirs, get_department
)
from .models import (
    Signal, Pattern, Need, Proposal, Assessment,
    PrioritizedItem, EnergyState, DependencyGraph,
    RiskAssessment, StalenessItem, Alert,
    ChangelogEntry, Synergy, Goal, IntelItem,
    TestResult, Snapshot, KnowledgeEntry,
    CommunicationProfile, ResourceState, EvolutionEntry,
    save_json, load_json
)

from pathlib import Path

# PRINCIPLE/ARTIFACT log for Law of Three Steps compliance
PRINCIPLE_LOG = Path(CACHE_DIR) / "principle_artifact_log.jsonl"

def log_principle(principle: str, action: str = "", proposal_id: str = ""):
    """Log PRINCIPLE step - what lesson/principle drives this action."""
    entry = {
        "ts": datetime.now().isoformat(),
        "type": "PRINCIPLE",
        "principle": principle,
        "action": action,
        "proposal_id": proposal_id,
    }
    PRINCIPLE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PRINCIPLE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def log_artifact(artifact_path: str, action: str = "", proposal_id: str = "", success: bool = True):
    """Log ARTIFACT step - measurable output of the action."""
    entry = {
        "ts": datetime.now().isoformat(),
        "type": "ARTIFACT",
        "artifact": artifact_path,
        "action": action,
        "proposal_id": proposal_id,
        "success": success,
    }
    PRINCIPLE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PRINCIPLE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def get_principle_artifact_stats() -> dict:
    """Get stats on PRINCIPLE vs ARTIFACT compliance."""
    if not PRINCIPLE_LOG.exists():
        return {"principles": 0, "artifacts": 0, "matched": 0, "unmatched": 0}
    principles = []
    artifacts = []
    with open(PRINCIPLE_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get("type") == "PRINCIPLE":
                    principles.append(entry)
                elif entry.get("type") == "ARTIFACT":
                    artifacts.append(entry)
            except:
                pass
    # Match by proposal_id
    matched = sum(1 for p in principles if any(a.get("proposal_id") == p.get("proposal_id") for a in artifacts))
    return {
        "principles": len(principles),
        "artifacts": len(artifacts),
        "matched": matched,
        "unmatched": len(principles) - matched,
    }


class CrystalEngine:
    """
    Главный движок Crystal v3.
    
    23 модуля, 8 отделов.
    Наблюдает → Анализирует → Предлагает → Оценивает → Эволюционирует.
    """

    def __init__(self, config=None):
        self.config = config or DEFAULT_CONFIG
        ensure_dirs()

        # Состояние
        self.signals = []
        self.patterns = []
        self.needs = []
        self.proposals = []
        self.energy = EnergyState()
        self.dependencies = DependencyGraph()
        self.goals = []
        self.knowledge = []
        self.communication = CommunicationProfile()
        self.resources = ResourceState()
        self.alerts = []
        self.evolution = []

        # Загрузка данных
        self._load_state()

    def _load_state(self):
        """Загрузить состояние из JSON-файлов"""
        self.signals = load_json(Paths.signals, Signal)
        self.patterns = load_json(Paths.patterns, Pattern)
        self.needs = load_json(Paths.needs, Need)
        self.proposals = load_json(Paths.proposals, Proposal)
        self.knowledge = load_json(Paths.knowledge_base, KnowledgeEntry)
        self.alerts = load_json(Paths.alerts, Alert)
        self.evolution = load_json(Paths.evolution, EvolutionEntry)
        self.goals = load_json(Paths.goals, Goal)

        # Загрузка состояний
        energy_data = load_json(Paths.energy)
        if energy_data and isinstance(energy_data, dict):
            self.energy = EnergyState(**energy_data)

        comm_data = load_json(Paths.communication)
        if comm_data and isinstance(comm_data, dict):
            self.communication = CommunicationProfile(**comm_data)

        res_data = load_json(Paths.resources)
        if res_data and isinstance(res_data, dict):
            self.resources = ResourceState(**res_data)

    def _save_state(self):
        """Сохранить состояние в JSON-файлы (с лимитом на размер)"""
        MAX_SIGNALS = 5000
        MAX_PATTERNS = 5000

        # Обрезаем историю чтобы не раздувать JSON
        if len(self.signals) > MAX_SIGNALS:
            self.signals = self.signals[-MAX_SIGNALS:]
        if len(self.patterns) > MAX_PATTERNS:
            self.patterns = self.patterns[-MAX_PATTERNS:]

        save_json(self.signals, Paths.signals)
        save_json(self.patterns, Paths.patterns)
        save_json(self.needs, Paths.needs)
        save_json(self.proposals, Paths.proposals)
        save_json(self.knowledge, Paths.knowledge_base)
        save_json(self.alerts, Paths.alerts)
        save_json(self.evolution, Paths.evolution)
        save_json(self.goals, Paths.goals)
        save_json(self.energy, Paths.energy)
        save_json(self.communication, Paths.communication)
        save_json(self.resources, Paths.resources)

    def _log_cycle_event(self, event_type: str, data: dict):
        """Log cycle events for PRINCIPLE/ARTIFACT tracking."""
        from pathlib import Path
        log_file = Path(CACHE_DIR) / "crystal_cycle_log.jsonl"
        entry = {
            "ts": datetime.now().isoformat(),
            "event": event_type,
            "data": data,
        }
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # ── Фаза 2: Наблюдение ────────────────────────────────────────

    def recall_context(self, query: str, limit: int = 5) -> str:
        """
        Session Recall — семантический поиск по истории сессий.
        Возвращает контекстный блок для инъекции в промпт.
        """
        try:
            from session_recall import semantic_search, format_context
            results = semantic_search(query, limit)
            return format_context(results, query)
        except Exception as e:
            return f"[Session recall unavailable: {e}]"

    def read_sessions(self, session_dir: str = None):
        """
        Модуль 1: Session Reader
        Читает JSONL сессии, извлекает сигналы
        """
        from .session_reader import SessionReader
        reader = SessionReader(self.config.get("session_reader", {}))
        new_signals = reader.read(session_dir)
        self.signals.extend(new_signals)
        return new_signals

    def detect_patterns(self):
        """
        Модуль 2: Pattern Detector
        Находит повторяющиеся паттерны из сигналов
        """
        from .pattern_detector import PatternDetector
        detector = PatternDetector(self.config.get("pattern_detector", {}))
        new_patterns = detector.detect(self.signals)
        self.patterns.extend(new_patterns)
        return new_patterns

    # ── Фаза 3: Анализ ────────────────────────────────────────────

    def analyze_needs(self):
        """
        Модуль 3: Need Analyzer
        Из паттернов формирует потребности
        """
        from .need_analyzer import NeedAnalyzer
        analyzer = NeedAnalyzer(self.config.get("need_analyzer", {}))
        new_needs = analyzer.analyze(self.patterns)
        self.needs.extend(new_needs)
        return new_needs

    def prioritize(self):
        """
        Модуль 4: Priority Engine
        Определяет что делать первым
        """
        from .priority_engine import PriorityEngine
        engine = PriorityEngine(self.config.get("priority_engine", {}))
        prioritized = engine.prioritize(self.needs, self.energy, self.dependencies)
        return prioritized

    def assess_risks(self, proposals):
        """
        Модуль 7: Risk Assessment
        Оценивает безопасность каждого proposal
        """
        from .risk_assessment import RiskAssessor
        assessor = RiskAssessor(self.config.get("risk_assessment", {}))
        assessed = assessor.assess(proposals)
        return assessed

    # ── Фаза 4: Контекст ──────────────────────────────────────────

    def load_memory(self):
        """
        Модуль 11: Memory Integration
        Читает USER.md + MEMORY.md
        """
        from .memory_integration import MemoryIntegration
        mem = MemoryIntegration()
        context = mem.read()
        return context

    def query_knowledge(self, problem: str):
        """
        Модуль 19: Knowledge Base
        Ищет в базе знаний похожую проблему
        """
        from .knowledge_base import KnowledgeBase
        kb = KnowledgeBase(self.knowledge)
        match = kb.find(problem)
        return match

    # ── Фаза 5: Действия ──────────────────────────────────────────

    def propose(self):
        """
        Модуль 8: Development Proposer
        Из потребностей генерирует конкретные действия
        """
        from .dev_proposer import DevelopmentProposer
        proposer = DevelopmentProposer(self.config.get("dev_proposer", {}))
        new_proposals = proposer.propose(self.needs, self.knowledge)
        self.proposals.extend(new_proposals)
        return new_proposals

    def find_synergies(self):
        """
        Модуль 14: Cross-department Synergy
        Находит связи между отделами
        """
        from .synergy import SynergyFinder
        finder = SynergyFinder()
        synergies = finder.find(self.proposals, self.needs)
        return synergies

    def analyze_conversation(self, days: int = 30) -> list:
        """
        Модуль 24: Conversation Analysis
        СЕМАНТИЧЕСКИЙ АНАЛИЗ — извлекает СМЫСЛ через LLM, а не ключевые слова
        """
        from .semantic_parser import SemanticParser
        
        parser = SemanticParser()
        semantic = parser.parse(days=days)
        
        new_proposals = []
        
        # ══════════════════════════════════════════════════════════════
        # СЕМАНТИЧЕСКИЙ АНАЛИЗ: LLM понимает СМЫСЛ сообщений
        # ══════════════════════════════════════════════════════════════
        
        # Извлекаем Goals → конкретные действия
        for goal in semantic.get("goals", []):
            urgency = goal.get("urgency", "medium")
            priority = {"high": 0.95, "medium": 0.8, "low": 0.6}.get(urgency, 0.7)
            
            proposal = Proposal(
                action="create_feature",
                description=f"ЦЕЛЬ: {goal.get('goal', '?')} — {goal.get('why', '')}",
                department="user-needs",
                priority=priority,
            )
            new_proposals.append(proposal)
        
        # Извлекаем Frustration → индикаторы сломанного
        for frust in semantic.get("frustration", []):
            proposal = Proposal(
                action="fix_problem",
                description=f"ИНДИКАТОР СЛОМАННОГО: {frust.get('what', '?')} — {frust.get('why', '')}",
                department="user-experience",
                priority=0.95,
            )
            new_proposals.append(proposal)
        
        # Извлекаем Pain Points → что болит в отношениях
        rel = semantic.get("relationship", {})
        for pp in rel.get("pain_points", []):
            proposal = Proposal(
                action="fix_problem",
                description=f"БОЛЕВАЯ ТОЧКА: {pp}",
                department="user-experience",
                priority=0.9,
            )
            new_proposals.append(proposal)
        
        # Сохраняем семантический контекст для использования другими модулями
        self._semantic_context = semantic
        
        # Сохраняем предложения
        self.proposals.extend(new_proposals)

        return new_proposals

    def test_proposal(self, proposal):
        """
        Модуль 17: Automated Testing
        Тест перед применением
        """
        from .testing import ProposalTester
        tester = ProposalTester(self.config.get("testing", {}))
        result = tester.test(proposal)
        return result

    # ── Фаза 6: Обратная связь ────────────────────────────────────

    def measure_feedback(self, proposal):
        """
        Модуль 12: Feedback Loop
        Оценивает помогло ли изменение
        """
        from .feedback_loop import FeedbackLoop
        loop = FeedbackLoop(self.config.get("feedback_loop", {}))
        assessment = loop.measure(proposal, self.signals)
        return assessment

    def record_changelog(self, proposal, effect=""):
        """
        Модуль 13: Versioning
        Записывает изменение в changelog
        """
        entry = ChangelogEntry(
            version=f"v{len(self.evolution)+1}.0",
            description=proposal.description,
            reason=proposal.action,
            effect=effect,
        )
        changelog = load_json(Paths.changelog, ChangelogEntry)
        changelog.append(entry)
        save_json(changelog, Paths.changelog)
        return entry

    def rollback(self, version: str):
        """
        Модуль 18: Rollback
        Откат куказанной версии
        """
        from .rollback import RollbackManager
        manager = RollbackManager()
        success = manager.rollback(version)
        return success

    # ── Фаза 7: Мониторинг ────────────────────────────────────────

    def check_staleness(self):
        """
        Модуль 9: Staleness Detector
        Проверяет что устарело
        """
        from .staleness import StalenessDetector
        detector = StalenessDetector(self.config.get("staleness", {}))
        items = detector.check()
        return items

    def check_alerts(self):
        """
        Модуль 10: Proactive Alerts
        Проверяет и генерирует уведомления
        """
        from .alerts import AlertManager
        manager = AlertManager(self.config.get("alerts", {}))
        new_alerts = manager.check(self.signals, self.patterns)
        self.alerts.extend(new_alerts)
        return new_alerts

    def check_resources(self):
        """
        Модуль 21: Resource Monitor
        Проверяет бюджет и лимиты
        """
        from .resources import ResourceMonitor
        monitor = ResourceMonitor()
        self.resources = monitor.check()
        return self.resources

    # ── Фаза 8: Эволюция ──────────────────────────────────────────

    def evolve(self):
        """
        Модуль 22: Self-Evolution
        Оценивает и улучшает модули
        """
        from .self_evolution import SelfEvolution
        evo = SelfEvolution(self.config.get("self_evolution", {}))
        entries = evo.evolve(self.signals, self.patterns, self.proposals)
        self.evolution.extend(entries)
        return entries

    def update_goals(self):
        """
        Модуль 15: Long-term Goals
        Обновляет прогресс целей
        """
        from .goals import GoalTracker
        tracker = GoalTracker()
        self.goals = tracker.update(self.goals, self.proposals)
        return self.goals

    def scan_intelligence(self):
        """
        Модуль 16: External Intelligence
        Сканирует внешний мир
        """
        from .intelligence import IntelScanner
        scanner = IntelScanner()
        items = scanner.scan()
        return items

    def adapt_communication(self, feedback_text: str):
        """
        Модуль 20: Communication Adapter
        Адаптирует стиль общения
        """
        from .communication import CommunicationAdapter
        adapter = CommunicationAdapter(self.communication)
        self.communication = adapter.adapt(feedback_text)
        save_json(self.communication, Paths.communication)
        return self.communication

    # ── Главный цикл ──────────────────────────────────────────────

    def run_full_cycle(self, quick=False):
        """
        Полный цикл Crystal:
        Наблюдение → Анализ → Действия → Обратная связь → Эволюция
        quick=True пропускает LLM-зависимые и тяжёлые шаги
        """
        # PRINCIPLE: Start cycle with explicit principle reference
        principle_ref = "Закон Трёх Ступеней: Понимание→Действие, Действие→Артефакт, Действие←Принцип"
        print(f"[Crystal] v3 - Polnyj cikl | PRINCIPLE: {principle_ref}")
        print("=" * 50)
        
        # Log cycle start
        self._log_cycle_event("start", {
            "principle": principle_ref,
            "quick": quick,
        })

        start = time.time()

        # 1. Наблюдение
        print("\n[Faza 1] Наблюдение")
        if not quick:
            signals = self.read_sessions()
            print(f"   Сигналов: {len(signals)}")
        else:
            print(f"   Сигналов: {len(self.signals)} (from cache)")

        patterns = self.detect_patterns()
        print(f"   Паттернов: {len(patterns)}")

        # Emit event if patterns found
        if patterns:
            try:
                from emit_event import emit
                emit("session_completed", {
                    "signals": len(self.signals),
                    "patterns": len(patterns),
                    "source": "crystal",
                })
            except Exception:
                pass

        # 2. Анализ
        print("\n[Faza 2] Анализ")
        needs = self.analyze_needs()
        print(f"   Потребностей: {len(needs)}")

        prioritized = self.prioritize()
        print(f"   Приоритизировано: {len(prioritized)}")

        # 3. Контекст
        print("\n[Faza 3] Контекст")
        memory = self.load_memory()
        print(f"   Memory: {len(memory)} записей")

        # 3.5. Анализ переписки (пропускается в quick-режиме)
        conv_proposals = []
        if not quick:
            print("\n[Faza 3.5] Анализ переписки")
            try:
                conv_proposals = self.analyze_conversation(days=7)
                print(f"   Предложений из переписки: {len(conv_proposals)}")
            except Exception as e:
                print(f"   [WARN] Анализ переписки пропущен: {e}")
        
        # 4. Действия — НЕМЕДЛЕННО
        print("\n[Faza 4] Действия")

        # Очищаем старые предложения — генерируем свежие
        self.proposals = []

        # Генерируем предложения из потребностей
        fresh_proposals = self.propose()
        print(f"   Свежих предложений: {len(fresh_proposals)}")

        # Добавляем из анализа переписки (если есть)
        if conv_proposals:
            fresh_proposals.extend(conv_proposals)

        # SHAME COUNTER: Track how many times a proposal appeared without artifact
        # If > 3 times → create goal_queue task with REPEATED_3X flag
        # This is NOT a filter - it's a shame sensor
        from collections import Counter
        from .config import CACHE_DIR
        import json
        from pathlib import Path

        shame_file = Path(CACHE_DIR) / "proposal_shame_counter.json"
        shame_counter = {}
        if shame_file.exists():
            try:
                with open(shame_file, "r", encoding="utf-8") as f:
                    shame_counter = json.load(f)
            except:
                pass

        # Count occurrences
        proposal_keys = []
        for p in fresh_proposals:
            words = [w.lower() for w in p.description.split() if len(w) > 3]
            key = (p.action, p.department, tuple(sorted(words[:5])))
            # Convert to string for JSON serialization
            key_str = f"{p.action}|{p.department}|{','.join(sorted(words[:5]))}"
            proposal_keys.append(key_str)
            shame_counter[key_str] = shame_counter.get(key_str, 0) + 1

        # Save updated counter
        shame_file.parent.mkdir(parents=True, exist_ok=True)
        with open(shame_file, "w", encoding="utf-8") as f:
            json.dump(shame_counter, f, ensure_ascii=False, indent=2)

        # All proposals pass through - NO FILTER
        # But tag those with shame_count > 3
        all_proposals = []
        for i, p in enumerate(fresh_proposals):
            key = proposal_keys[i]
            count = shame_counter.get(key, 0)
            if count > 3:
                p.description = f"[REPEATED_{count}X] {p.description}"
                # Force auto=True for repeated items - MUST EXECUTE
                p.auto = True
                print(f"   ⚠️ SHAME: '{p.description[:60]}' appeared {count} times without artifact!")
            all_proposals.append(p)

        # Разделяем: auto=True (выполняем сразу) и auto=False (показываем для.review)
        auto_proposals = [p for p in all_proposals if p.auto]
        review_proposals = [p for p in all_proposals if not p.auto]

        executed = 0
        total = 0

        # Выполняем ВСЕ auto=True предложения
        if auto_proposals:
            print(f"   Auto-применяемые ({len(auto_proposals)}):")
            for p in auto_proposals:
                print(f"     [{p.priority:.2f}] {p.action}: {p.description[:70]}")
            results = self.execute_with_feedback(auto_proposals, dry_run=False)
            executed = sum(1 for r in results if r.get("result", {}).get("success"))
            total = len(auto_proposals)
            print(f"   Исполнено: {executed}/{total}")

        # Показываем auto=False для.review (не выполняем)
        if review_proposals:
            top3_review = sorted(review_proposals, key=lambda p: p.priority, reverse=True)[:3]
            print(f"   Требуют.review ({len(review_proposals)}, ТОП-3):")
            for p in top3_review:
                print(f"     [{p.priority:.2f}] {p.action}: {p.description[:70]}")

        if not auto_proposals and not review_proposals:
            print("   Нет предложений для исполнения")

        # 5. Мониторинг
        print("\n[Faza 5] Мониторинг")
        stale = self.check_staleness()
        print(f"   Устаревших: {len(stale)}")

        alerts = self.check_alerts()
        print(f"   Уведомлений: {len(alerts)}")

        # Emit event if alerts found
        if alerts:
            try:
                from emit_event import emit
                emit("error_logged", {
                    "alerts": len(alerts),
                    "source": "crystal",
                })
            except Exception:
                pass

        resources = self.check_resources()
        print(f"   Бюджет: {resources.budget_spent:.2f}/{resources.budget_limit}")

        # 6. Эволюция
        print("\n[Faza 6] Эволюция")
        evo = self.evolve()
        print(f"   Эволюций: {len(evo)}")

        goals = self.update_goals()
        print(f"   Целей: {len(goals)}")

        # 5b. Agent Reach Intelligence Scan (NEW)
        print("\n[Faza 5b] Agent Reach Intelligence Scan")
        intel_items = self.scan_intelligence()
        print(f"   Найдено: {len(intel_items)} инсайтов")

        # 6b. OMH Research Pipeline (NEW) - runs if there are high-priority needs
        print("\n[Faza 6b] OMH Research Pipeline")
        omh_results = self.run_omh_research()
        print(f"   OMH циклов: {len(omh_results)}")

        elapsed = time.time() - start

        # Сохраняем всё одним вызовом в конце цикла
        self._save_state()

        # ARTIFACT: Log cycle completion with concrete artifacts
        artifacts = {
            "signals": len(self.signals),
            "patterns": len(self.patterns),
            "needs": len(self.needs),
            "proposals": len(self.proposals),
            "stale": len(stale),
            "alerts": len(alerts),
            "evolution": len(evo),
            "elapsed": elapsed,
        }
        self._log_cycle_event("complete", {"artifacts": artifacts})

        print(f"\n[OK] Цикл завершён за {elapsed:.1f}с | ARTIFACT: {artifacts}")
        print(f"   Всего: {len(self.signals)} сигналов, {len(self.patterns)} паттернов, "
              f"{len(self.needs)} потребностей, {len(self.proposals)} предложений")

        return artifacts

    def run_department(self, department: str):
        """Запуск для конкретного отдела"""
        print(f"\n[Crystal] Отдел: {department}")

        # Фильтруем по отделу
        dept_signals = [s for s in self.signals if s.department == department]
        dept_patterns = [p for p in self.patterns if p.department == department]
        dept_needs = [n for n in self.needs if n.department == department]
        dept_proposals = [p for p in self.proposals if p.department == department]

        print(f"   Сигналов: {len(dept_signals)}")
        print(f"   Паттернов: {len(dept_patterns)}")
        print(f"   Потребностей: {len(dept_needs)}")
        print(f"   Предложений: {len(dept_proposals)}")

        return {
            "signals": dept_signals,
            "patterns": dept_patterns,
            "needs": dept_needs,
            "proposals": dept_proposals,
        }

    def scan_intelligence(self) -> list:
        """Agent Reach Intelligence Scan - uses Agent Reach to gather external insights."""
        try:
            from scripts.crystal.omh_integration import CrystalOMHResearchPipeline
            pipeline = CrystalOMHResearchPipeline()
            results = pipeline.scan_and_research("AI agent automation CPA arbitrage 2024", auto_plan=True)
            
            # Convert to IntelItem format
            intel_items = []
            if "stages" in results:
                for stage_name, stage_data in results["stages"].items():
                    if isinstance(stage_data, list):
                        for item in stage_data:
                            from scripts.crystal.models import IntelItem
                            intel_items.append(IntelItem(
                                source=stage_name,
                                title=item.get("video", item.get("title", "Research finding")),
                                description=str(item)[:500],
                                url=item.get("url", ""),
                                relevance=0.8,
                            ))
            return intel_items
        except Exception as e:
            print(f"   [WARN] Intelligence scan failed: {e}")
            return []

    def run_omh_research(self) -> list:
        """Run OMH Research Pipeline on high-priority needs."""
        try:
            from scripts.crystal.omh_integration import CrystalOMHResearchPipeline, OMHIntegration
            omh = OMHIntegration()
            results = []
            
            # Check which OMH skills are available
            available = [s for s in ["omh-deep-research", "omh-ralplan", "omh-ralph", "omh-autopilot"] 
                        if omh.is_available(s)]
            
            if not available:
                return ["No OMH skills available"]
            
            # Run autopilot on top priority need
            if self.needs:
                top_need = max(self.needs, key=lambda n: n.priority if hasattr(n, 'priority') else 0)
                topic = top_need.description if hasattr(top_need, 'description') else str(top_need)
                pipeline = CrystalOMHResearchPipeline()
                result = pipeline.scan_and_research(topic, auto_plan=True)
                return [result]
            
            return ["No needs to research"]
        except Exception as e:
            print(f"   [WARN] OMH research failed: {e}")
            return [f"Error: {e}"]

    def analyze_errors(self, hours: int = 48) -> dict:
        """Анализировать реальные ошибки из логов"""
        from .error_analyzer import ErrorAnalyzer
        analyzer = ErrorAnalyzer()
        return analyzer.analyze(hours=hours)

    def execute_with_feedback(self, proposals: list, dry_run: bool = False) -> list:
        """Выполнить提议 с оценкой результата (полный цикл)"""
        from .executor import ProposalExecutor
        from .feedback_loop import FeedbackLoop

        executor = ProposalExecutor({"dry_run": dry_run})
        feedback = FeedbackLoop()
        results = []

        for proposal in proposals:
            result = feedback.execute_and_evaluate(proposal, executor, self)
            results.append(result)

        return results

    def feedback_stats(self) -> dict:
        """Статистика по feedback"""
        from .feedback_loop import FeedbackLoop
        feedback = FeedbackLoop()
        return feedback.get_stats()

    def summary(self) -> str:
        """Краткая сводка"""
        lines = [
            "[Crystal] v3 - Сводка",
            f"   Сигналов: {len(self.signals)}",
            f"   Паттернов: {len(self.patterns)}",
            f"   Потребностей: {len(self.needs)}",
            f"   Предложений: {len(self.proposals)}",
            f"   Уведомлений: {len(self.alerts)}",
            f"   Целей: {len(self.goals)}",
            f"   База знаний: {len(self.knowledge)}",
            f"   Эволюций: {len(self.evolution)}",
            f"   Энергия: {self.energy.level}",
            f"   Бюджет: {self.resources.budget_spent:.2f}/{self.resources.budget_limit}",
        ]
        return "\n".join(lines)
