"""Юнит-тест: in_view_guard — триггер «В поле зрения».

Молчаливая деградация: сбои ЗАПИСАНЫ в state.db, но не ОБРАБОТАНЫ.
Триггер должен находить их и отдавать предупреждением.
"""
import os
import sys
import sqlite3
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import chain_heartbeat as chb


class TestInViewGuard(unittest.TestCase):
    def setUp(self):
        # изолированная БД: копируем схему, кладём 3+ сбоя
        self.tmp = os.path.join(os.environ.get("TEMP", "/tmp"), "in_view_test.db")
        if os.path.exists(self.tmp):
            os.remove(self.tmp)
        con = sqlite3.connect(self.tmp)
        con.execute("""CREATE TABLE sessions (
            id TEXT, started_at REAL, compression_failure_error TEXT,
            compression_ineffective_count INTEGER,
            compression_fallback_streak INTEGER)""")
        now = datetime.now(timezone.utc).timestamp()
        rows = [
            (f"s{i}", now - 3600 * i, "Error code: 429 - rate limit", 0, 0) for i in range(4)
        ] + [
            (f"ok{i}", now - 3600 * i, None, 0, 0) for i in range(3)
        ]
        con.executemany("INSERT INTO sessions VALUES (?,?,?,?,?)", rows)
        con.commit()
        con.close()

    def tearDown(self):
        if os.path.exists(self.tmp):
            os.remove(self.tmp)

    def test_detects_silent_failures(self):
        """3+ однотипных сбоя = паттерн, а не случайность → предупреждение."""
        chb._IN_VIEW_DB = self.tmp  # monkeypatch на тестовую БД
        out = chb.in_view_guard(days=7)
        self.assertTrue(any("429" in w for w in out), f"не нашёл 429: {out}")

    def test_below_threshold_silent(self):
        """<3 сбоев — не паттерн, молчание легитимно."""
        con = sqlite3.connect(self.tmp)
        con.execute("DELETE FROM sessions WHERE compression_failure_error IS NOT NULL")
        con.execute("INSERT INTO sessions VALUES ('s1', ?, 'Error code: 429', 0, 0)",
                    (datetime.now(timezone.utc).timestamp(),))
        con.commit()
        con.close()
        chb.STATE_DB = self.tmp
        out = chb.in_view_guard(days=7)
        self.assertFalse(any("429" in w for w in out), f"ложное срабатывание: {out}")


if __name__ == "__main__":
    unittest.main()
