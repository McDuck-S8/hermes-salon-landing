#!/usr/bin/env python3
"""
Crystal v3 — CLI
Персональный Development Advisor

Использование:
    python scripts/crystal.py                    # полный цикл
    python scripts/crystal.py --summary          # краткая сводка
    python scripts/crystal.py --analyze-sessions # анализ сессий
    python scripts/crystal.py --analyze-conversation  # анализ ПОЛНОЙ переписки
    python scripts/crystal.py --check-staleness  # проверка актуальности
    python scripts/crystal.py --propose          # предложение
    python scripts/crystal.py --apply            # применить предложений
    python scripts/crystal.py --apply --dry-run  # dry run
    python scripts/crystal.py --errors           # анализ ошибок из логов
    python scripts/crystal.py --cycle            # полный цикл:提议→apply→feedback
    python scripts/crystal.py --feedback-stats   # статистика feedback
    python scripts/crystal.py --feedback         # оценка
    python scripts/crystal.py --department X     # конкретный отдел
    python scripts/crystal.py --intelligence     # внешний мир
    python scripts/crystal.py --goals            # цели
    python scripts/crystal.py --synergies        # синергия
    python scripts/crystal.py --changelog        # история
    python scripts/crystal.py --rollback <ver>   # откат
    python scripts/crystal.py --test             # тест
    python scripts/crystal.py --knowledge        # база знаний
    python scripts/crystal.py --communication    # стиль общения
    python scripts/crystal.py --resources        # ресурсы
    python scripts/crystal.py --evolve           # самоэволюция
"""

import sys
import os

# Добавляем scripts/ в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crystal.core import CrystalEngine
from crystal.config import DEPARTMENTS


def main():
    args = sys.argv[1:]

    engine = CrystalEngine()

    if not args:
        # Полный цикл
        result = engine.run_full_cycle()
        print()
        print(engine.summary())
        return

    cmd = args[0]

    if cmd == "--summary":
        print(engine.summary())

    elif cmd == "--analyze-sessions":
        signals = engine.read_sessions()
        patterns = engine.detect_patterns()
        print(f"Сигналов: {len(signals)}")
        print(f"Паттернов: {len(patterns)}")
        for p in patterns[:10]:
            print(f"  [{p.type}] {p.department}: {p.description[:80]}")

    elif cmd == "--check-staleness":
        items = engine.check_staleness()
        print(f"Устаревших: {len(items)}")
        for item in items:
            print(f"  [{item.type}] {item.name}: {item.stale_days} дней → {item.action}")

    elif cmd == "--propose":
        engine.read_sessions()
        engine.detect_patterns()
        needs = engine.analyze_needs()
        proposals = engine.propose()
        print(f"Потребностей: {len(needs)}")
        print(f"Предложений: {len(proposals)}")
        for p in proposals:
            print(f"  [{p.action}] {p.department}: {p.description[:80]}")

    elif cmd == "--feedback":
        if len(args) > 1:
            proposal_id = args[1]
            # Ищем proposal
            from crystal.config import Paths
            from crystal.models import load_json, Proposal
            proposals = load_json(Paths.proposals, Proposal)
            for p in proposals:
                if p.id == proposal_id:
                    assessment = engine.measure_feedback(p)
                    print(f"Метрика: {assessment.metric}")
                    print(f"До: {assessment.before:.3f}")
                    print(f"После: {assessment.after:.3f}")
                    print(f"Дельта: {assessment.delta:.3f}")
                    print(f"Успех: {'✅' if assessment.success else '❌'}")
                    break
            else:
                print(f"Proposal {proposal_id} не найден")
        else:
            print("Использование: --feedback <proposal_id>")

    elif cmd == "--apply":
        dry_run = "--dry-run" in args
        from crystal.executor import ProposalExecutor
        from crystal.config import Paths
        from crystal.models import load_json, Proposal
        
        # Берём кэшированные предложения
        proposals = load_json(Paths.proposals, Proposal)
        
        if not proposals:
            print("Нет предложений. Сначала: --propose")
        else:
            executor = ProposalExecutor({"dry_run": dry_run})
            results = executor.execute(proposals)
            
            print(f"Предложений: {len(proposals)}")
            for r in results:
                if r["success"]:
                    status = "[DRY RUN]" if r.get("dry_run") else "[DONE]"
                    print(f"  {status} {r.get('action', '?')}: {r.get('path', r.get('would_create', r.get('would_patch', r.get('would_update', '?'))))}")
                else:
                    print(f"  [FAIL] {r.get('error', '?')}")

    elif cmd == "--department":
        if len(args) > 1:
            dept = args[1]
            if dept in DEPARTMENTS:
                engine.read_sessions()
                engine.detect_patterns()
                result = engine.run_department(dept)
            else:
                print(f"Неизвестный отдел: {dept}")
                print(f"Доступные: {', '.join(DEPARTMENTS.keys())}")
        else:
            print("Использование: --department <name>")
            print(f"Доступные: {', '.join(DEPARTMENTS.keys())}")

    elif cmd == "--errors":
        hours = 48
        if "--24h" in args:
            hours = 24
        elif "--7d" in args:
            hours = 168
        
        result = engine.analyze_errors(hours=hours)
        
        print(f"🔮 Crystal — Анализ ошибок ({hours}h)")
        print(f"Всего ошибок: {result['total_errors']}")
        print(f"Здоровье системы: {result['health_score']}%")
        print()
        
        if result['top_errors']:
            print("Типы ошибок:")
            for e in result['top_errors']:
                print(f"  {e['type']}: {e['count']}")
            print()
        
        if result['fixes']:
            print("Что исправить:")
            for f in result['fixes']:
                print(f"  [{f['severity']}] {f['error']}: {f['fix']}")

    elif cmd == "--cycle":
        dry_run = "--dry-run" in args
        from crystal.config import Paths
        from crystal.models import load_json, Proposal
        
        proposals = load_json(Paths.proposals, Proposal)
        
        if not proposals:
            print("Нет предложений. Сначала: --propose")
        else:
            results = engine.execute_with_feedback(proposals, dry_run=dry_run)
            
            print(f"🔮 Crystal — Полный цикл")
            print(f"Предложений: {len(results)}")
            print()
            
            successes = sum(1 for r in results if r["assessment"].success)
            print(f"Успешно: {successes}/{len(results)}")
            print()
            
            for r in results:
                status = "✅" if r["assessment"].success else "❌"
                action = r["result"].get("action", "?")
                delta = r["assessment"].delta
                print(f"  {status} {action}: дельта={delta:.0f}")

    elif cmd == "--feedback-stats":
        stats = engine.feedback_stats()
        
        print(f"🔮 Crystal — Статистика feedback")
        print(f"Всего циклов: {stats['total']}")
        print(f"Успешно: {stats.get('successes', 0)}")
        print(f"Процент успеха: {stats['success_rate']}%")
        print(f"Средняя дельта: {stats['avg_delta']}")
        
        if stats.get("recent"):
            print()
            print("Последние:")
            for h in stats["recent"]:
                status = "✅" if h.get("assessment_success") else "❌"
                print(f"  {status} {h.get('action', '?')}: {h.get('delta', 0):.0f}")

    elif cmd == "--analyze-conversation":
        from crystal.conversation_analyzer import ConversationAnalyzer
        
        days = 30
        for arg in args:
            if arg.startswith("--days="):
                days = int(arg.split("=")[1])
        
        analyzer = ConversationAnalyzer()
        result = analyzer.analyze_full(days=days)
        
        print(f"🔮 Crystal — Анализ переписки за {days} дней")
        print(f"Всего сообщений: {result['total_messages']}")
        print()
        
        # Инсайты
        if result["insights"]:
            print(f"💡 Инсайты ({len(result['insights'])}):")
            for i, insight in enumerate(result["insights"][:5], 1):
                print(f"  {i}. {insight['text'][:100]}...")
            print()
        
        # Идеи
        if result["ideas"]:
            print(f"🚀 Идеи ({len(result['ideas'])}):")
            for i, idea in enumerate(result["ideas"][:5], 1):
                print(f"  {i}. {idea['text'][:100]}...")
            print()
        
        # Проблемы
        if result["problems"]:
            print(f"⚠️ Проблемы ({len(result['problems'])}):")
            for i, prob in enumerate(result["problems"][:5], 1):
                print(f"  {i}. {prob['text'][:100]}...")
            print()
        
        # Процессы
        if result["workflows"]:
            print(f"📋 Описанные процессы ({len(result['workflows'])}):")
            for i, wf in enumerate(result["workflows"][:3], 1):
                print(f"  {i}. {wf['text'][:100]}...")
            print()
        
        # Паттерны
        if result["patterns"].get("daily_activity"):
            print("📊 Активность по дням:")
            for day, count in list(result["patterns"]["daily_activity"].items())[-7:]:
                print(f"  {day}: {count} сообщений")
        
        print()
        print(f"Сводка: {result['summary']}")

    elif cmd == "--generate-proposals":
        """Генерирует предложения на основе анализа переписки"""
        from crystal.config import Paths
        from crystal.models import load_json, Proposal
        
        days = 30
        for arg in args:
            if arg.startswith("--days="):
                days = int(arg.split("=")[1])
        
        # Анализируем переписку
        proposals = engine.analyze_conversation(days=days)
        
        print(f"🔮 Crystal — Предложения на основе переписки ({days} дней)")
        print(f"Сгенерировано предложений: {len(proposals)}")
        print()
        
        for i, p in enumerate(proposals[:10], 1):
            print(f"{i}. [{p.action}] {p.description[:120]}")
            print(f"   Приоритет: {p.priority:.1f} | Риск: {p.risk_level}")
        
        print()
        print("Для применения: python scripts/crystal.py --apply")

    elif cmd == "--intelligence":
        items = engine.scan_intelligence()
        print(f"Внешних данных: {len(items)}")
        for item in items[:5]:
            print(f"  [{item.source}] {item.title}: {item.description[:60]}")

    elif cmd == "--goals":
        goals = engine.update_goals()
        print(f"Целей: {len(goals)}")
        for g in goals:
            print(f"  [{g.department}] {g.title}: {g.progress:.0%}")

    elif cmd == "--synergies":
        engine.read_sessions()
        engine.detect_patterns()
        engine.analyze_needs()
        proposals = engine.propose()
        synergies = engine.find_synergies()
        print(f"Синергий: {len(synergies)}")
        for s in synergies:
            print(f"  {s.type}: {' + '.join(s.departments)} — {s.description}")

    elif cmd == "--changelog":
        from crystal.versioning import VersionManager
        vm = VersionManager()
        entries = vm.get_recent(10)
        print(f"Последние {len(entries)} изменений:")
        for e in entries:
            print(f"  {e.version}: {e.description}")

    elif cmd == "--rollback":
        if len(args) > 1:
            version = args[1]
            success = engine.rollback(version)
            print(f"Откат {'✅' if success else '❌'}")
        else:
            print("Использование: --rollback <version>")

    elif cmd == "--test":
        from crystal.testing import ProposalTester
        from crystal.models import Proposal
        tester = ProposalTester()
        p = Proposal(description="Тестовый proposal", action="create_skill", department="ai-core")
        result = tester.test(p)
        print(f"Тест: {'✅' if result.passed else '❌'}")
        print(f"Детали: {result.details}")

    elif cmd == "--knowledge":
        from crystal.knowledge_base import KnowledgeBase
        kb = KnowledgeBase(engine.knowledge)
        print(f"База знаний: {len(kb.entries)} записей")
        for e in kb.entries[:5]:
            print(f"  [{e.department}] {e.problem[:60]} → {e.solution[:40]}")

    elif cmd == "--communication":
        print(f"Язык: {engine.communication.language}")
        print(f"Длина: {engine.communication.length}")
        print(f"Техничность: {engine.communication.technicality}")
        print(f"Тон: {engine.communication.tone}")
        print(f"Формат: {engine.communication.format}")
        print(f"Поправок: {len(engine.communication.learned_corrections)}")

    elif cmd == "--resources":
        resources = engine.check_resources()
        print(f"API вызовов: {resources.api_calls_today}/{resources.api_limit_daily}")
        print(f"Токенов: {resources.tokens_this_month}/{resources.tokens_limit_monthly}")
        print(f"Бюджет: {resources.budget_spent:.2f}/{resources.budget_limit}")
        print(f"Диск: {resources.disk_usage_mb:.1f} MB")

    elif cmd == "--evolve":
        engine.read_sessions()
        engine.detect_patterns()
        entries = engine.evolve()
        print(f"Эволюций: {len(entries)}")
        for e in entries:
            print(f"  [{e.action}] {e.module}: {e.reason}")

    elif cmd == "--help" or cmd == "-h":
        print(__doc__)

    else:
        print(f"Неизвестная команда: {cmd}")
        print("Используйте --help для справки")


if __name__ == "__main__":
    main()
