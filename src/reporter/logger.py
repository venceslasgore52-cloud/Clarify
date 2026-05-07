"""
logger.py — enregistre chaque erreur interceptée par Clarify en base de données
et écrit une ligne de log horodatée dans un fichier texte local.

Rôle dans le pipeline :
    core.handle_exception()
        → decoder.decode()
        → terminal.render()
        → reporter.logger.log_error()   ← ici
"""

import os
from datetime import datetime
from src.database.queries import save_error

# Fichier de log texte lisible à côté de la DB
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "database", "clarify.log")

# Niveaux de log et leur préfixe
LEVELS = {
    "info":    "[INFO   ]",
    "warning": "[WARNING]",
    "error":   "[ERROR  ]",
    "debug":   "[DEBUG  ]",
}


def log_error(decoded: dict, langue: str = "fr") -> int:
    """
    Persiste une erreur décodée en base SQLite et dans le fichier de log.
    Retourne l'id de la ligne insérée en base.
    """
    error_id = save_error(decoded, langue)
    _write_log_line(decoded, error_id)
    return error_id


def _write_log_line(decoded: dict, error_id: int) -> None:
    """Écrit une ligne structurée dans clarify.log."""
    now    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    etype  = decoded.get("type",    "UnknownError")
    msg    = decoded.get("message", "").replace("\n", " ")
    file_  = decoded.get("file",    "?")
    line   = decoded.get("line",    "?")
    pid    = decoded.get("pattern_id", "no-pattern")

    entry  = f"{now} {LEVELS['error']} [{error_id:>4}] {etype}: {msg} | {file_}:{line} | {pid}\n"

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except OSError:
        pass  # Ne jamais planter à cause du logger


def log_message(message: str, level: str = "info") -> None:
    """Écrit un message libre dans clarify.log (info, warning, debug)."""
    now    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = LEVELS.get(level, LEVELS["info"])
    entry  = f"{now} {prefix} {message}\n"

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except OSError:
        pass


def get_log_tail(n: int = 50) -> list[str]:
    """Retourne les n dernières lignes du fichier de log."""
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [l.rstrip() for l in lines[-n:]]
    except OSError:
        return []


def clear_log() -> None:
    """Vide le fichier de log (garde le fichier, supprime le contenu)."""
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("")
    except OSError:
        pass
