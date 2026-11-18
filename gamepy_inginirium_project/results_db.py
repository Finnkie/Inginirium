"""Логи результатов в SQLite: сохранение раундов и топ-5 игроков.
При равенстве очков выше тот, кто набрал их раньше."""

import sqlite3
from datetime import datetime


class ResultDB:
    def __init__(self, path):
        self.path = path
        conn = sqlite3.connect(self.path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS results ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "nickname TEXT NOT NULL, "
            "score INTEGER NOT NULL, "
            "played_at TEXT NOT NULL)"
        )
        conn.commit()
        conn.close()

    def save(self, nickname, score):
        """Сохраняет результат раунда и возвращает топ-5: список пар
        (ник, очки)."""
        conn = sqlite3.connect(self.path)
        played_at = datetime.now().strftime("%d.%m.%Y %H:%M")
        conn.execute(
            "INSERT INTO results (nickname, score, played_at) VALUES (?, ?, ?)",
            (nickname, score, played_at),
        )
        conn.commit()
        top = conn.execute(
            "SELECT nickname, score FROM results "
            "ORDER BY score DESC, played_at ASC LIMIT 5"
        ).fetchall()
        conn.close()
        return top
