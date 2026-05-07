"""
db.py — connexion SQLite locale pour Clarify.
Stocke les erreurs interceptées pour les afficher dans le dashboard webview.
SQLite est intégré à Python — aucune installation nécessaire.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "clarify.db")


def get_connection() -> sqlite3.Connection:
    """Ouvre et retourne une connexion à la base SQLite."""
    conn = sqlite3.connect(DB_PATH)
    # Retourne les lignes sous forme de dict plutôt que de tuple
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Crée les tables si elles n'existent pas encore."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                type        TEXT    NOT NULL,
                message     TEXT    NOT NULL,
                file        TEXT,
                line        INTEGER,
                time        TEXT,
                pattern_id  TEXT,
                description TEXT,
                solution    TEXT,
                conseil     TEXT,
                langue      TEXT    DEFAULT 'fr',
                saved_at    TEXT    NOT NULL
            )
        """)
        conn.commit()
