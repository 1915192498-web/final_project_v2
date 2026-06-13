import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "game.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                novel_title TEXT,
                current_chapter INTEGER DEFAULT 1,
                current_scene TEXT DEFAULT '开头',
                hp INTEGER DEFAULT 100,
                attack INTEGER DEFAULT 15,
                defense INTEGER DEFAULT 10,
                inventory TEXT DEFAULT '[]',
                flags TEXT DEFAULT '{}',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES game_sessions(session_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS world_clues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                clue_type TEXT,
                clue_content TEXT,
                discovered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES game_sessions(session_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS game_saves (
                save_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                save_name TEXT NOT NULL,
                save_data TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES game_sessions(session_id)
            )
        """)


def create_user(user_id: str, username: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username),
        )


def create_session(user_id: str, novel_title: str, hp: int = 100, attack: int = 15, defense: int = 10) -> int:
    with get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO game_sessions (user_id, novel_title, hp, attack, defense) VALUES (?, ?, ?, ?, ?)",
            (user_id, novel_title, hp, attack, defense),
        )
        return cursor.lastrowid


def get_session(session_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM game_sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if row:
            d = dict(row)
            d["inventory"] = json.loads(d.get("inventory") or "[]")
            d["flags"] = json.loads(d.get("flags") or "{}")
            return d
        return None


def update_session(session_id: int, **kwargs):
    sets = []
    vals = []
    for k, v in kwargs.items():
        if k in ("inventory", "flags") and isinstance(v, (list, dict)):
            v = json.dumps(v, ensure_ascii=False)
        sets.append(f"{k} = ?")
        vals.append(v)
    vals.append(session_id)
    with get_conn() as conn:
        conn.execute(
            f"UPDATE game_sessions SET {', '.join(sets)} WHERE session_id = ?",
            vals,
        )


def save_chat(session_id: int, role: str, content: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content),
        )


def get_chat_history(session_id: int, limit: int = 50):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT role, content, timestamp FROM chat_history WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit),
        ).fetchall()
        return [dict(r) for r in reversed(rows)]


def save_clue(session_id: int, clue_type: str, content: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO world_clues (session_id, clue_type, clue_content) VALUES (?, ?, ?)",
            (session_id, clue_type, content),
        )


def get_clues(session_id: int):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT clue_type, clue_content, discovered_at FROM world_clues WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_user_sessions(user_id: str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM game_sessions WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def save_game_snapshot(session_id: int, save_name: str = "自动存档"):
    with get_conn() as conn:
        session = dict(conn.execute(
            "SELECT * FROM game_sessions WHERE session_id = ?", (session_id,)
        ).fetchone() or {})
        if not session:
            return None

        chat_rows = conn.execute(
            "SELECT role, content FROM chat_history WHERE session_id = ? ORDER BY id", (session_id,)
        ).fetchall()
        clue_rows = conn.execute(
            "SELECT clue_type, clue_content FROM world_clues WHERE session_id = ? ORDER BY id", (session_id,)
        ).fetchall()

        save_data = json.dumps({
            "session": session,
            "chat_history": [dict(r) for r in chat_rows],
            "clues": [dict(r) for r in clue_rows],
        }, ensure_ascii=False)

        conn.execute(
            "INSERT INTO game_saves (session_id, save_name, save_data) VALUES (?, ?, ?)",
            (session_id, save_name, save_data)
        )
        return save_name


def get_saves_for_session(session_id: int):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT save_id, save_name, created_at FROM game_saves WHERE session_id = ? ORDER BY created_at DESC",
            (session_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_saves():
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT gs.save_id, gs.save_name, gs.created_at, 
                      gs.session_id, gss.novel_title, gss.hp, gss.current_chapter
               FROM game_saves gs
               JOIN game_sessions gss ON gs.session_id = gss.session_id
               ORDER BY gs.created_at DESC""",
        ).fetchall()
        return [dict(r) for r in rows]


def load_game_snapshot(session_id: int, save_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT save_data FROM game_saves WHERE save_id = ? AND session_id = ?",
            (save_id, session_id)
        ).fetchone()
        if not row:
            return None

        data = json.loads(row["save_data"])

        s = data["session"]
        conn.execute(
            "UPDATE game_sessions SET hp=?, attack=?, defense=?, current_chapter=?, current_scene=?, inventory=?, flags=? WHERE session_id=?",
            (s["hp"], s["attack"], s["defense"], s["current_chapter"], s["current_scene"], json.dumps(s.get("inventory", []), ensure_ascii=False), json.dumps(s.get("flags", {}), ensure_ascii=False), session_id)
        )

        conn.execute("DELETE FROM chat_history WHERE session_id=?", (session_id,))
        for msg in data.get("chat_history", []):
            conn.execute(
                "INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, msg["role"], msg["content"])
            )

        conn.execute("DELETE FROM world_clues WHERE session_id=?", (session_id,))
        for clue in data.get("clues", []):
            conn.execute(
                "INSERT INTO world_clues (session_id, clue_type, clue_content) VALUES (?, ?, ?)",
                (session_id, clue["clue_type"], clue["clue_content"])
            )

        return data
