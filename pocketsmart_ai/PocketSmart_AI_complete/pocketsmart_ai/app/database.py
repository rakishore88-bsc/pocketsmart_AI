from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.config import get_settings


def _db_path() -> Path:
    url = get_settings().database_url
    if not url.startswith("sqlite:///"):
        raise ValueError("This starter implementation expects a SQLite DATABASE_URL")
    path = Path(url.removeprefix("sqlite:///"))
    if not path.is_absolute():
        path = Path.cwd() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS recommendation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                planner_type TEXT NOT NULL,
                request_json TEXT NOT NULL,
                response_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )


def create_user(email: str, name: str, password_hash: str) -> dict[str, Any]:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO users(email, name, password_hash) VALUES (?, ?, ?)",
            (email.lower().strip(), name.strip(), password_hash),
        )
        user_id = cur.lastrowid
        row = conn.execute("SELECT id, email, name, created_at FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(row)


def get_user_by_email(email: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE email=?", (email.lower().strip(),)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute("SELECT id, email, name, created_at FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(row) if row else None


def save_history(user_id: int, planner_type: str, request_data: dict, response_data: dict) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO recommendation_history(user_id, planner_type, request_json, response_json) VALUES (?, ?, ?, ?)",
            (user_id, planner_type, json.dumps(request_data), json.dumps(response_data)),
        )
        return int(cur.lastrowid)


def get_history(user_id: int, limit: int = 50) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, planner_type, request_json, response_json, created_at FROM recommendation_history WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["request"] = json.loads(item.pop("request_json"))
        item["response"] = json.loads(item.pop("response_json"))
        result.append(item)
    return result
