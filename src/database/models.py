"""
models.py — représentation Python d'une erreur stockée en base.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ErrorRecord:
    type:        str
    message:     str
    file:        str        = ""
    line:        int        = 0
    time:        str        = ""
    pattern_id:  str        = ""
    description: str        = ""
    solution:    str        = ""
    conseil:     str        = ""
    langue:      str        = "fr"
    saved_at:    str        = field(default_factory=lambda: datetime.now().isoformat())
    id:          int        = 0

    @staticmethod
    def from_row(row) -> "ErrorRecord":
        """Construit un ErrorRecord depuis une ligne SQLite (sqlite3.Row)."""
        return ErrorRecord(**{k: row[k] for k in row.keys()})

    def to_dict(self) -> dict:
        """Sérialise l'enregistrement en dictionnaire (pour le webview JSON)."""
        return {
            "id":          self.id,
            "type":        self.type,
            "message":     self.message,
            "file":        self.file,
            "line":        self.line,
            "time":        self.time,
            "pattern_id":  self.pattern_id,
            "description": self.description,
            "solution":    self.solution,
            "conseil":     self.conseil,
            "langue":      self.langue,
            "saved_at":    self.saved_at,
        }
