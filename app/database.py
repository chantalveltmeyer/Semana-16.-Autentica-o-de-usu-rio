import sqlite3
from flask import current_app, g

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE COLLATE NOCASE,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'User'
                CHECK(role IN ('Admin','User')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            confirmed INTEGER NOT NULL DEFAULT 0
        )
    """)

    columns = {
        row["name"] for row in db.execute("PRAGMA table_info(users)").fetchall()
    }
    if "confirmed" not in columns:
        db.execute(
            "ALTER TABLE users ADD COLUMN confirmed INTEGER NOT NULL DEFAULT 0"
        )

    db.commit()
