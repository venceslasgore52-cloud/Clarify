"""
dashboard.py — génère le fichier webview/preview.html avec les données
réelles de la base de données Clarify.

Utilisé :
  - par l'extension VS Code pour rafraîchir le webview
  - en standalone pour prévisualiser le dashboard dans un navigateur
"""

import os
import json
from src.database.queries import get_all_errors, get_stats

WEBVIEW_DIR  = os.path.join(os.path.dirname(__file__), "..", "..", "webview")
TEMPLATE     = os.path.join(WEBVIEW_DIR, "dashboard.html")
CSS_FILE     = os.path.join(WEBVIEW_DIR, "dashboard.css")
JS_FILE      = os.path.join(WEBVIEW_DIR, "dashboard.js")
PREVIEW_FILE = os.path.join(WEBVIEW_DIR, "preview.html")


def get_dashboard_data(limit: int = 100) -> dict:
    """
    Collecte les données depuis la base et les retourne sous forme de dict
    prêt à être sérialisé en JSON pour le webview.
    """
    stats  = get_stats()
    errors = [e.to_dict() for e in get_all_errors(limit=limit)]
    return {"stats": stats, "errors": errors}


def generate_preview(limit: int = 100) -> str:
    """
    Génère webview/preview.html — version standalone du dashboard
    avec les données injectées dans window.CLARIFY_DATA.

    Retourne le chemin absolu du fichier généré.
    """
    data = get_dashboard_data(limit)

    with open(TEMPLATE,  encoding="utf-8") as f: html = f.read()
    with open(CSS_FILE,  encoding="utf-8") as f: css  = f.read()
    with open(JS_FILE,   encoding="utf-8") as f: js   = f.read()

    # Intègre CSS et JS directement dans le HTML pour un fichier auto-suffisant
    html = html.replace(
        '<link rel="stylesheet" href="dashboard.css" />',
        f"<style>\n{css}\n</style>"
    )
    html = html.replace(
        '<script src="dashboard.js"></script>',
        f"<script>window.CLARIFY_DATA = {json.dumps(data, ensure_ascii=False)};</script>\n"
        f"<script>\n{js}\n</script>"
    )

    with open(PREVIEW_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    return os.path.abspath(PREVIEW_FILE)


def get_webview_html(limit: int = 100) -> str:
    """
    Retourne le HTML complet du dashboard avec données injectées.
    Utilisé par l'extension VS Code pour peupler le WebviewPanel.
    """
    data = get_dashboard_data(limit)

    with open(TEMPLATE, encoding="utf-8") as f: html = f.read()
    with open(CSS_FILE, encoding="utf-8") as f: css  = f.read()
    with open(JS_FILE,  encoding="utf-8") as f: js   = f.read()

    html = html.replace(
        '<link rel="stylesheet" href="dashboard.css" />',
        f"<style>\n{css}\n</style>"
    )
    html = html.replace(
        '<script src="dashboard.js"></script>',
        f"<script>window.CLARIFY_DATA = {json.dumps(data, ensure_ascii=False)};</script>\n"
        f"<script>\n{js}\n</script>"
    )
    return html
