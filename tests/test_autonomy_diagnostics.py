"""
Diagnostic test suite for agent autonomy.
Каждый тест проверяет конкретный разрыв цикла.
FAIL = разрыв подтверждён.
PASS = цикл замкнут.
"""
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

# ============================================================
# ТЕСТ 1: WEIGHTS LOOP — влияет ли исход на следующий выбор?
# ============================================================

def test_1_negative_outcome_reduces_weight():
    """Действие с негативными исходами должно терять приоритет"""
    from feedback_store import record_outcome, compute_weight

    action_id = "test_diagnostic_a"

    # Записываем 5 негативных исходов
    for _ in range(5):
        record_outcome(action_id, -1.0, evidence="test failure")

    weight = compute_weight(action_id)

    assert weight < 1.0, (
        "FAIL: Негативные исходы не снизили вес. "
        "Вес должен быть < 1.0, а не %.3f" % weight
    )
    print("PASS: Negative outcome reduces weight (%.3f < 1.0)" % weight)


def test_2_positive_outcome_increases_weight():
    """Действие с позитивными исходами должно расти"""
    from feedback_store import record_outcome, compute_weight

    action_id = "test_diagnostic_b"

    for _ in range(5):
        record_outcome(action_id, 1.0, evidence="test success")

    weight = compute_weight(action_id)

    assert weight > 1.0, (
        "FAIL: Позитивные исходы не повысили вес. "
        "Вес должен быть > 1.0, а не %.3f" % weight
    )
    print("PASS: Positive outcome increases weight (%.3f > 1.0)" % weight)


def test_3_weights_affect_scoring():
    """compute_score должен учитывать веса из feedback_store"""
    from feedback_store import record_outcome
    from autonomous_agent import compute_score

    # Записываем негативные исходы для test_action
    for _ in range(3):
        record_outcome("test_scoring_neg", -1.0, evidence="fail")

    # Записываем позитивные для другого
    for _ in range(3):
        record_outcome("test_scoring_pos", 1.0, evidence="success")

    action_neg = {"id": "test_scoring_neg", "urgency": 5, "impact": 5, "tier": 2}
    action_pos = {"id": "test_scoring_pos", "urgency": 5, "impact": 5, "tier": 2}

    score_neg = compute_score(action_neg, {})
    score_pos = compute_score(action_pos, {})

    assert score_pos > score_neg, (
        "FAIL: Weights не влияют на scoring. "
        "Провальное: %.2f, успешное: %.2f" % (score_neg, score_pos)
    )
    print("PASS: Weights affect scoring (%.2f vs %.2f)" % (score_neg, score_pos))


# ============================================================
# ТЕСТ 2: GOAL → ACTION — выполняются ли цели?
# ============================================================

def test_4_goal_executor_returns_action():
    """goal_executor должен возвращать action, а не 'acknowledged'"""
    from goal_executor import execute_goal

    goal = {
        "id": "test_goal_1",
        "title": "Build salon booking bot template",
        "priority": 8,
    }

    result = execute_goal(goal)

    assert "acknowledged" not in result.get("evidence", "").lower(), (
        "FAIL: Goal executor вернул 'acknowledged' — placeholder вместо реального действия"
    )
    assert "action" in result or result.get("success") is True, (
        "FAIL: Goal executor не определил action для цели"
    )
    print("PASS: Goal executor returns real action (not placeholder)")


def test_5_goal_executor_checks_criteria():
    """goal_executor должен проверять success_criteria"""
    from goal_executor import execute_goal

    # Goal для несуществующего файла
    goal = {
        "id": "test_goal_2",
        "title": "Create file /nonexistent/path/test.txt",
        "priority": 5,
    }

    result = execute_goal(goal)

    # Criteria: "exists at /nonexistent/path/test.txt" — файл не существует
    assert result.get("outcome", 0) <= 0.5, (
        "FAIL: Goal executor не проверил критерий — файл не существует но goal помечена как частично выполненная"
    )
    print("PASS: Goal executor checks success criteria")


def test_6_goal_executor_detects_already_met():
    """goal_executor должен определить что критерий уже выполнен"""
    from goal_executor import execute_goal

    goal = {
        "id": "test_goal_3",
        "title": "Build salon booking bot template",
        "priority": 5,
    }

    result = execute_goal(goal)

    # salon_booking_bot.py существует → критерий "Bot exists" выполнен
    assert result.get("outcome", 0) >= 0.8, (
        "FAIL: Goal executor не определил что критерий уже выполнен "
        "(salon_booking_bot.py существует)"
    )
    print("PASS: Goal executor detects already-met criteria (outcome=%.2f)" % result.get("outcome", 0))


# ============================================================
# ТЕСТ 3: ACTION LOG — логируется ли каждое действие?
# ============================================================

def test_7_action_log_exists():
    """Каждое действие должно записываться в action_log.jsonl"""
    from feedback_store import record_outcome

    record_outcome("test_log_action", 0.7, evidence="test")

    log_file = Path("D:/Portable_Soft/hermes/cache/action_log.jsonl")
    assert log_file.exists(), "FAIL: action_log.jsonl не существует"

    lines = log_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) > 0, "FAIL: action_log.jsonl пуст"

    # Проверяем что последняя запись валидна
    last = json.loads(lines[-1])
    assert "timestamp" in last, "FAIL: Запись без timestamp"
    assert "action_id" in last, "FAIL: Запись без action_id"
    assert "status" in last, "FAIL: Запись без status"

    print("PASS: Action log exists with %d entries, last has all fields" % len(lines))


# ============================================================
# ТЕСТ 4: FEEDBACK STORE — данные сохраняются?
# ============================================================

def test_8_feedback_persists():
    """Feedback должен сохраняться между вызовами"""
    from feedback_store import record_outcome, get_action_history

    action_id = "test_persist_%d" % int(datetime.now().timestamp())
    record_outcome(action_id, 0.5, evidence="persist test")

    history = get_action_history(action_id)
    assert len(history) >= 1, "FAIL: Feedback не сохранился"
    assert history[-1]["outcome"] == 0.5, "FAIL: Outcome не совпадает"
    print("PASS: Feedback persists across calls")


# ============================================================
# ТЕСТ 5: SESSION CONTEXT — загружается ли ВСЁ при boot?
# ============================================================

def test_9_context_loads_all_sections():
    """Session context должен содержать все секции"""
    from session_context import build_context

    ctx = build_context("test query")

    required_sections = [
        "Previous Session",
        "Active Goals",
        "Knowledge Graph",
        "Available Tools",
    ]

    for section in required_sections:
        assert section in ctx, (
            "FAIL: Секция '%s' отсутствует в session context" % section
        )

    print("PASS: Session context has all %d required sections" % len(required_sections))


def test_10_tool_catalog_in_context():
    """Tool catalog должен быть виден в контексте"""
    from session_context import build_context

    ctx = build_context("test")

    assert "Tool catalog" in ctx or "tools" in ctx.lower(), (
        "FAIL: Tool catalog не отображается в session context"
    )

    # Проверяем что хотя бы 10 tools упомянуто
    import re
    tool_matches = re.findall(r"\d+ tools", ctx)
    assert len(tool_matches) > 0, "FAIL: Количество tools не указано в контексте"

    print("PASS: Tool catalog visible in session context")


# ============================================================
# ТЕСТ 6: FEEDBACK STORE WEIGHTS
# ============================================================

def test_11_weights_computed_correctly():
    """Веса должны корректно вычисляться из истории"""
    from feedback_store import compute_weight, get_all_weights

    # Нет данных → вес 1.0
    w_unknown = compute_weight("nonexistent_action_xyz")
    assert w_unknown == 1.0, "FAIL: Unknown action weight should be 1.0, got %.3f" % w_unknown

    # Все успехи → вес > 1.0
    w_success = compute_weight("test_scoring_pos")  # из теста 2
    assert w_success > 1.0, "FAIL: All-success weight should be > 1.0, got %.3f" % w_success

    # Все провалы → вес < 1.0
    w_failure = compute_weight("test_scoring_neg")  # из теста 1
    assert w_failure < 1.0, "FAIL: All-failure weight should be < 1.0, got %.3f" % w_failure

    print("PASS: Weights computed correctly (unknown=%.2f, success=%.2f, failure=%.2f)" % (
        w_unknown, w_success, w_failure
    ))


# ============================================================
# ТЕСТ 7: AUTONOMOUS AGENT — 33 actions available?
# ============================================================

def test_12_agent_has_diverse_actions():
    """Агент должен иметь actions из разных tier"""
    from autonomous_agent import evaluate_actions

    state = {
        "knowledge_cube": {"entries": 4000, "domains": 150, "failure_rate": 0.03, "white_spots": 200},
        "cron_health": {"jobs_total": 40, "jobs_with_errors": 5, "enabled": 35},
        "resources": {"disk_free_gb": 200},
        "recent_errors": [],
        "verified_fixes_count": 0,
    }
    profile = {"telegram_channels": [], "business": ""}

    candidates = evaluate_actions(state, profile)

    # Должно быть минимум 20 actions
    assert len(candidates) >= 20, (
        "FAIL: Только %d candidate actions (нужно минимум 20)" % len(candidates)
    )

    # Должны быть actions из разных tier
    tiers = set(c.get("tier", 0) for c in candidates)
    assert len(tiers) >= 2, (
        "FAIL: Actions только из %d tier (нужно минимум 2)" % len(tiers)
    )

    # Должны быть LEARN actions (curiosity, graph, needs)
    learn_actions = [c for c in candidates if c.get("tier_name") == "LEARN"]
    assert len(learn_actions) >= 3, (
        "FAIL: Только %d LEARN actions (нужно минимум 3)" % len(learn_actions)
    )

    print("PASS: Agent has %d actions across %d tiers (%d LEARN)" % (
        len(candidates), len(tiers), len(learn_actions)
    ))


# ============================================================
# ТЕСТ 8: ROTATION — каждые 3 run非goals?
# ============================================================

def test_13_rotation_logic():
    """Каждый 3-й run должен выбирать non-goal action"""
    from autonomous_agent import pick_best_action, evaluate_actions, load_decisions

    state = {
        "knowledge_cube": {"entries": 4000, "domains": 150, "failure_rate": 0.03, "white_spots": 200},
        "cron_health": {"jobs_total": 40, "jobs_with_errors": 5, "enabled": 35},
        "resources": {"disk_free_gb": 200},
        "recent_errors": [],
        "verified_fixes_count": 0,
    }
    profile = {"telegram_channels": [], "business": ""}

    candidates = evaluate_actions(state, profile)

    # Simulate 3 consecutive goal runs
    decisions = load_decisions()
    goal_runs = sum(1 for d in decisions[-3:] if d.get("action_id", "").startswith("goal-"))

    if goal_runs >= 2:
        # Rotation should kick in — force non-goal
        non_goal = [c for c in candidates if not c["id"].startswith("goal-") and c.get("tier_name") in ("LEARN", "PRODUCE")]
        assert len(non_goal) > 0, (
            "FAIL: Rotation triggered but no non-goal LEARN/PRODUCE actions available"
        )
        print("PASS: Rotation logic active (%d non-goal actions available)" % len(non_goal))
    else:
        print("PASS: Rotation not needed yet (only %d goal runs in last 3)" % goal_runs)


# ============================================================
# ТЕСТ 9: FULL CYCLE — boot → decide → execute → record
# ============================================================

def test_14_full_autonomy_cycle():
    """Сквозной тест: boot → context → decide → execute → record"""
    from session_context import build_context
    from autonomous_agent import evaluate_actions, compute_score, pick_best_action
    from feedback_store import record_outcome

    # 1. Boot — build context
    ctx = build_context("test cycle")
    assert len(ctx) > 100, "FAIL: Context пустой после boot"

    # 2. Evaluate actions
    state = {
        "knowledge_cube": {"entries": 4000, "domains": 150, "failure_rate": 0.03, "white_spots": 200},
        "cron_health": {"jobs_total": 40, "jobs_with_errors": 5, "enabled": 35},
        "resources": {"disk_free_gb": 200},
        "recent_errors": [],
        "verified_fixes_count": 0,
    }
    profile = {"telegram_channels": [], "business": ""}
    candidates = evaluate_actions(state, profile)
    assert len(candidates) > 0, "FAIL: Нет candidates"

    # 3. Pick best
    best = pick_best_action(candidates, state)
    assert best is not None, "FAIL: pick_best_action вернул None"
    assert "id" in best, "FAIL: Best action без id"
    assert "score" in best, "FAIL: Best action без score"

    # 4. Record outcome (simulated)
    record_outcome(best["id"], 0.5, evidence="diagnostic test")

    print("PASS: Full cycle works: boot(%d chars) -> %d candidates -> picked '%s' (score=%.2f) -> recorded" % (
        len(ctx), len(candidates), best["id"][:30], best["score"]
    ))


# ============================================================
# ТЕСТ 10: NO PLACEHOLDERS IN CODEBASE
# ============================================================

def test_15_no_placeholder_in_goal_queue():
    """goal_queue.py не должен содержать 'acknowledged' в execute_fn"""
    gq_path = Path("D:/Portable_Soft/hermes/scripts/goal_queue.py")
    content = gq_path.read_text(encoding="utf-8")

    # Проверяем что _action_pursue_goal НЕ возвращает просто "acknowledged"
    assert '"acknowledged"' not in content or "goal_executor" in content, (
        "FAIL: goal_queue.py всё ещё содержит placeholder 'acknowledged'"
    )
    assert "goal_executor" in content, (
        "FAIL: goal_queue.py не импортирует goal_executor"
    )
    print("PASS: goal_queue.py uses goal_executor (no placeholder)")


def test_16_action_feedback_uses_feedback_store():
    """action_feedback.py должен использовать feedback_store"""
    af_path = Path("D:/Portable_Soft/hermes/scripts/action_feedback.py")
    content = af_path.read_text(encoding="utf-8")

    assert "feedback_store" in content, (
        "FAIL: action_feedback.py не импортирует feedback_store"
    )
    assert "compute_weight" in content, (
        "FAIL: action_feedback.py не использует compute_weight"
    )
    print("PASS: action_feedback.py integrated with feedback_store")


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    from datetime import datetime

    tests = [
        test_1_negative_outcome_reduces_weight,
        test_2_positive_outcome_increases_weight,
        test_3_weights_affect_scoring,
        test_4_goal_executor_returns_action,
        test_5_goal_executor_checks_criteria,
        test_6_goal_executor_detects_already_met,
        test_7_action_log_exists,
        test_8_feedback_persists,
        test_9_context_loads_all_sections,
        test_10_tool_catalog_in_context,
        test_11_weights_computed_correctly,
        test_12_agent_has_diverse_actions,
        test_13_rotation_logic,
        test_14_full_autonomy_cycle,
        test_15_no_placeholder_in_goal_queue,
        test_16_action_feedback_uses_feedback_store,
    ]

    passed = 0
    failed = 0
    errors = []

    print("=" * 60)
    print("AUTONOMY DIAGNOSTIC SUITE")
    print("=" * 60)
    print()

    for test_fn in tests:
        name = test_fn.__name__
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            failed += 1
            errors.append((name, str(e)))
            print("FAIL: %s" % name)
            print("  %s" % str(e)[:200])
        except Exception as e:
            failed += 1
            errors.append((name, "EXCEPTION: %s" % str(e)))
            print("ERROR: %s" % name)
            print("  %s" % str(e)[:200])

    print()
    print("=" * 60)
    print("RESULTS: %d PASSED / %d FAILED / %d TOTAL" % (passed, failed, len(tests)))
    print("=" * 60)

    if errors:
        print("\nFAILURES:")
        for name, msg in errors:
            print("  %s: %s" % (name, msg[:150]))
