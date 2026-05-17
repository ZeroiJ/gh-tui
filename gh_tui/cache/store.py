from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any


class CacheStore:
    """SQLite-backed key-value cache with TTL."""

    def __init__(self, db_path: Path | None = None) -> None:
        if db_path is None:
            db_path = Path.home() / ".local" / "share" / "gh-tui" / "cache.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                  key TEXT PRIMARY KEY,
                  value TEXT NOT NULL,
                  expires_at REAL NOT NULL,
                  created_at REAL NOT NULL
                )
                """
            )
            conn.commit()

    def get(self, key: str) -> tuple[Any | None, bool]:
        """Return (value, is_stale). None if missing."""
        now = time.time()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value, expires_at FROM cache WHERE key = ?", (key,)
            ).fetchone()
        if row is None:
            return None, False
        value = json.loads(row["value"])
        is_stale = now > row["expires_at"]
        return value, is_stale

    def set(self, key: str, value: Any, ttl_seconds: int = 600) -> None:
        now = time.time()
        expires_at = now + ttl_seconds
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO cache (key, value, expires_at, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                  value = excluded.value,
                  expires_at = excluded.expires_at,
                  created_at = excluded.created_at
                """,
                (key, json.dumps(value), expires_at, now),
            )
            conn.commit()

    def delete(self, key: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM cache")
            conn.commit()
