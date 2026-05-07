"""
Patterns de détection et d'explication des erreurs liées aux imports Python.

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator pour récupérer la traduction
  - pattern     : expression régulière appliquée sur le message d'erreur Python brut
  - description : explication courte de ce qui s'est passé (utilise {module}, {name}…)
  - solution    : action concrète à faire pour corriger l'erreur
  - conseil     : explication du mécanisme Python sous-jacent pour mieux comprendre le pourquoi
"""

PATTERNS = [

    # ──────────────────────────────────────────────────────────────────────
    # ModuleNotFoundError : module introuvable (Python 3.6+, couvre ImportError aussi)
    # Regex couvre les deux formes : "No module named 'x'" et "No module named 'x.y'"
    # ──────────────────────────────────────────────────────────────────────
    {
        "id":          "import.module_not_found",
        "pattern":     r"(?:ModuleNotFoundError|ImportError): No module named '(.+)'",
        "description": "Le module '{module}' est introuvable dans ton environnement Python.",
        "solution":    (
            "1. Installe le module manquant : pip install {module}\n"
            "2. Si tu l'as déjà installé, vérifie que tu utilises le bon environnement virtuel (venv).\n"
            "3. Si c'est un fichier local, vérifie que le chemin et l'orthographe sont corrects."
        ),
        "conseil":     (
            "Python cherche les modules dans cet ordre : dossier courant, "
            "PYTHONPATH, puis les packages installés. "
            "Si tu travailles avec un venv, active-le avant de lancer ton script : "
            "le module installé hors venv n'y est pas visible."
        ),
    },

    # ──────────────────────────────────────────────────────────────────────
    # ImportError : nom spécifique introuvable dans un module existant
    # Exemple. : from os import inexistant  →  cannot import name 'inexistant' from 'os'
    # ──────────────────────────────────────────────────────────────────────
    {
        "id":          "import.name_not_found",
        "pattern":     r"ImportError: cannot import name '(.+)' from '(.+)' \(most likely due to a circular import\)",
        "description": "'{name}' n'existe pas dans le module '{module}' — c'est probablement un import circulaire.",
        "solution":    (
            "Réorganise ton code pour briser la boucle : "
            "déplace les éléments partagés dans un troisième module indépendant "
            "que les deux autres importent sans se croiser."
        ),
        "conseil":     (
            "Un import circulaire se produit quand A importe B et B importe A. "
            "Au moment où Python charge A, B n'est pas encore fini de charger, "
            "donc '{name}' n'y existe pas encore. "
            "Le message '(most likely due to a circular import)' confirme ce cas."
        ),
    },

    # ──────────────────────────────────────────────────────────────────────
    # ImportError : nom introuvable dans un module (faute de frappe ou version)
    # Exemple. : from os.path import joyn  →  cannot import name 'joyn' from 'os.path'
    # ──────────────────────────────────────────────────────────────────────
    {
        "id":          "import.attribute_not_found",
        "pattern":     r"ImportError: cannot import name '(.+)' from '(.+)'",
        "description": "'{name}' n'existe pas dans le module '{module}'.",
        "solution":    (
            "Vérifie l'orthographe de '{name}' (Python est sensible à la casse). "
            "Utilise help('{module}') ou dir() dans la console pour voir ce que le module expose réellement."
        ),
        "conseil":     (
            "Quand tu écris 'from {module} import {name}', Python doit trouver "
            "'{name}' à l'intérieur de '{module}'. "
            "Si ta version du module est ancienne, certaines fonctions récentes n'y sont pas encore : "
            "mets à jour avec pip install --upgrade {module}."
        ),
    },

]
