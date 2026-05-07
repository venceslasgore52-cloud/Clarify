"""
queries.py — opérations CRUD sur la base SQLite de Clarify.
"""

from datetime import datetime
from src.database.db import get_connection, init_db
from src.database.models import ErrorRecord

# Initialise la DB au premier import du module
init_db()


def save_error(error_info: dict, langue: str = "fr") -> int:
    """Insère une erreur en base et retourne son id."""
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO errors
                (type, message, file, line, time,
                 pattern_id, description, solution, conseil, langue, saved_at)
            VALUES
                (:type, :message, :file, :line, :time,
                 :pattern_id, :description, :solution, :conseil, :langue, :saved_at)
        """, {
            "type":        error_info.get("type",        ""),
            "message":     error_info.get("message",     ""),
            "file":        error_info.get("file",        ""),
            "line":        error_info.get("line",        0),
            "time":        error_info.get("time",        ""),
            "pattern_id":  error_info.get("pattern_id",  ""),
            "description": error_info.get("description", ""),
            "solution":    error_info.get("solution",    ""),
            "conseil":     error_info.get("conseil",     ""),
            "langue":      langue,
            "saved_at":    datetime.now().isoformat(),
        })
        conn.commit()
        return cursor.lastrowid


def get_all_errors(limit: int = 100) -> list[ErrorRecord]:
    """Retourne les dernières erreurs enregistrées, les plus récentes en premier."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM errors
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [ErrorRecord.from_row(r) for r in rows]


def get_error_by_id(error_id: int) -> ErrorRecord | None:
    """Retourne une erreur par son id, ou None si introuvable."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM errors WHERE id = ?", (error_id,)
        ).fetchone()
        return ErrorRecord.from_row(row) if row else None


def get_stats() -> dict:
    """Retourne les statistiques pour le dashboard."""
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM errors").fetchone()[0]

        by_type = conn.execute("""
            SELECT type, COUNT(*) as count
            FROM errors
            GROUP BY type
            ORDER BY count DESC
            LIMIT 10
        """).fetchall()

        by_file = conn.execute("""
            SELECT file, COUNT(*) as count
            FROM errors
            WHERE file != ''
            GROUP BY file
            ORDER BY count DESC
            LIMIT 5
        """).fetchall()

        recent = conn.execute("""
            SELECT DATE(saved_at) as day, COUNT(*) as count
            FROM errors
            GROUP BY day
            ORDER BY day DESC
            LIMIT 7
        """).fetchall()

        return {
            "total":   total,
            "by_type": [{"type": r["type"], "count": r["count"]} for r in by_type],
            "by_file": [{"file": r["file"], "count": r["count"]} for r in by_file],
            "recent":  [{"day":  r["day"],  "count": r["count"]} for r in recent],
        }


def delete_error(error_id: int) -> bool:
    """Supprime une erreur par son id. Retourne True si supprimée."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM errors WHERE id = ?", (error_id,))
        conn.commit()
        return cursor.rowcount > 0


def clear_all_errors() -> int:
    """Supprime toutes les erreurs. Retourne le nombre de lignes supprimées."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM errors")
        conn.commit()
        return cursor.rowcount
