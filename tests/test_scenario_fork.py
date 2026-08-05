"""Юнит-тест: scenario_fork()/scenario_board() — вариативность исходов.

Паттерн нейтрален (солнце ни хорошо, ни плохо) — хорошо/плохо присваивает
контекст (axis_outcome в Кубе). Функция строит 3 ветки: good (применить
правильно), bad (нарушить), stasis (не действовать) — вероятности Байесом
из истории conform/deviate за 30 дней."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


class TestScenarioFork:
    def setup_method(self):
        from chain_heartbeat import scenario_fork, scenario_board
        self.fork = scenario_fork
        self.board = scenario_board

    def test_returns_three_branches(self):
        # ветки всегда три: добро, зло, статус-кво
        r = self.fork("никогда-не-было", "тест")
        assert len(r["branches"]) == 3
        signs = {b["sign"] for b in r["branches"]}
        assert signs == {"good", "bad", "stasis"}

    def test_no_history_all_equal(self):
        # неизвестный паттерн: нет истории → ветки равновероятны (0.5),
        # но ОБЯЗАНЫ быть просчитаны — незнание ≠ отсутствие исхода
        r = self.fork("никогда-не-было", "тест")
        for b in r["branches"]:
            assert abs(b["p"] - 0.5) < 0.01

    def test_probabilities_in_range(self):
        # вероятности всегда [0..1]
        r = self.fork("insight", "тест")
        for b in r["branches"]:
            assert 0.0 <= b["p"] <= 1.0

    def test_sorted_by_probability(self):
        # сортировка: наиболее вероятный исход первым
        r = self.fork("insight", "тест")
        ps = [b["p"] for b in r["branches"]]
        assert ps == sorted(ps, reverse=True)

    def test_board_aggregates(self):
        # доска по набору паттернов: есть most_likely
        r = self.board(["insight", "записал-не-сделал"], "тест")
        assert set(r["patterns"]) == {"insight", "записал-не-сделал"}
        assert r["most_likely"] is not None
        assert r["most_likely_pattern"] in ("insight", "записал-не-сделал")
