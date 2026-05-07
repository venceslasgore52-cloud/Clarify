"""
visualizer.py — génère le schéma ASCII du flux d'une erreur dans Clarify.

Montre le chemin complet qu'une exception parcourt :
    Exception Python → core → decoder → translator → terminal → logger → dashboard

Utilisé dans le panneau de détail du webview et dans le terminal.
"""

# Largeur du schéma
_W = 54

# Couleurs ANSI
_R  = "\033[0m"
_B  = "\033[1m"
_C  = "\033[36m"
_G  = "\033[32m"
_Y  = "\033[33m"
_RE = "\033[31m"
_D  = "\033[2m"


def _box(label: str, color: str = _C) -> str:
    """Retourne une boîte ASCII centrée."""
    inner = f"  {label}  "
    pad   = max(0, _W - len(inner) - 2)
    left  = pad // 2
    right = pad - left
    top   = "┌" + "─" * (len(inner) + left + right) + "┐"
    mid   = "│" + " " * left + inner + " " * right + "│"
    bot   = "└" + "─" * (len(inner) + left + right) + "┘"
    return f"{color}{_B}{top}\n{mid}\n{bot}{_R}"


def _arrow(label: str = "") -> str:
    """Retourne une flèche avec étiquette optionnelle."""
    center = _W // 2
    arr    = " " * center + "│"
    if label:
        tag = f" {_D}{label}{_R}"
        arr = " " * (center - 1) + "↓" + tag
    else:
        arr = " " * center + "↓"
    return arr


def build_flow(error_info: dict) -> str:
    """
    Génère le schéma de flux complet pour une erreur donnée.

    Chaque étape indique son rôle et le module responsable.
    Les étapes actives (pattern trouvé, traduction effectuée) sont mises en valeur.
    """
    etype      = error_info.get("type",       "Exception")
    file_      = error_info.get("file",       "?").split("\\")[-1].split("/")[-1]
    line       = error_info.get("line",       "?")
    pattern_id = error_info.get("pattern_id")
    langue     = error_info.get("langue",     "fr")

    pattern_label = f"pattern : {pattern_id}" if pattern_id else "aucun pattern"
    lang_label    = f"langue : {langue}" if langue != "fr" else "fr (pas de traduction)"

    lines = [
        "",
        _box(f"{etype}  —  {file_}:{line}", _RE),
        _arrow("sys.excepthook"),
        _box("core.handle_exception()", _C),
        _arrow("get_error_info()"),
        _box("decoder.decode()", _C),
        _arrow(pattern_label),
    ]

    # Étape traduction : uniquement si langue != source
    if langue != "fr":
        lines += [
            _box(f"translator.translate()  [{langue}]", _Y),
            _arrow(lang_label),
        ]
    else:
        lines += [
            _box("translator  [ignoré — langue source]", _D + _C),
            _arrow(),
        ]

    lines += [
        _box("terminal.render()", _G),
        _arrow("tableau coloré"),
        _box("reporter.logger.log_error()", _G),
        _arrow("SQLite + .log"),
        _box("reporter.dashboard  →  webview", _G),
        "",
    ]

    return "\n".join(lines)


def print_flow(error_info: dict) -> None:
    """Affiche le schéma de flux dans le terminal."""
    print(build_flow(error_info))


def flow_to_html(error_info: dict) -> str:
    """
    Retourne le schéma de flux en HTML <pre> pour l'affichage dans le webview.
    Les codes ANSI sont remplacés par des spans CSS.
    """
    import re
    flow = build_flow(error_info)

    # Supprime les codes ANSI pour l'affichage HTML (le CSS du webview gère les couleurs)
    clean = re.sub(r"\033\[[0-9;]*m", "", flow)

    return f'<pre class="error-flow">{clean}</pre>'


def flow_to_dict(error_info: dict) -> list[dict]:
    """
    Retourne le flux sous forme de liste de steps pour le webview JS.
    Chaque step a un label, un module et un statut (active / skipped).
    """
    langue     = error_info.get("langue",     "fr")
    pattern_id = error_info.get("pattern_id")

    steps = [
        {"step": 1, "label": "Exception capturée",      "module": "sys.excepthook",              "status": "active"},
        {"step": 2, "label": "Extraction des métadonnées","module": "core.get_error_info",        "status": "active"},
        {"step": 3, "label": "Décodage du pattern",      "module": "decoder.decode",              "status": "active" if pattern_id else "warning",
         "detail": pattern_id or "aucun pattern trouvé"},
        {"step": 4, "label": "Traduction",               "module": "translator.translate",        "status": "active" if langue != "fr" else "skipped",
         "detail": f"→ {langue}" if langue != "fr" else "ignoré (langue source)"},
        {"step": 5, "label": "Affichage terminal",       "module": "terminal.render",             "status": "active"},
        {"step": 6, "label": "Enregistrement log + DB",  "module": "reporter.logger.log_error",   "status": "active"},
        {"step": 7, "label": "Mise à jour dashboard",    "module": "reporter.dashboard",          "status": "active"},
    ]
    return steps
