"""
Patterns de détection et d'explication des erreurs liées aux variables Python.

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator pour récupérer la traduction
  - pattern     : expression régulière appliquée sur le message d'erreur Python brut
  - description : explication courte de ce qui s'est passé (utilise {var}, {obj}, {attr}…)
  - solution    : action concrète à faire pour corriger l'erreur
  - conseil     : explication du mécanisme Python sous-jacent pour mieux comprendre le pourquoi
"""

PATTERNS = [

    # ──────────────────────────────────────────────
    # NameError : variable utilisée sans être définie
    # ──────────────────────────────────────────────
    {
        "id":          "var.name_error",
        "pattern":     r"NameError: name '(.+)' is not defined",
        "description": "La variable '{var}' est utilisée mais elle n'a jamais été créée.",
        "solution":    "Crée '{var}' avant de l'utiliser, et vérifie l'orthographe (Python distingue majuscules et minuscules : 'nom' ≠ 'Nom').",
        "conseil":     (
            "Python exécute le code de haut en bas. "
            "Si tu appelles '{var}' avant de lui donner une valeur, il ne sait pas ce que c'est. "
            "Assigne-lui une valeur d'abord : {var} = ..."
        ),
    },

    # ──────────────────────────────────────────────────────────────────
    # UnboundLocalError : variable locale utilisée avant d'être assignée
    # ──────────────────────────────────────────────────────────────────
    {
        "id":          "var.unbound_local",
        "pattern":     r"UnboundLocalError: local variable '(.+)' referenced before assignment",
        "description": "'{var}' est traitée comme une variable locale dans la fonction, mais elle n'a pas encore reçu de valeur.",
        "solution":    (
            "Option 1 — Assigne une valeur à '{var}' avant de l'utiliser dans la fonction.\n"
            "Option 2 — Si '{var}' est définie en dehors de la fonction et que tu veux la modifier, "
            "ajoute 'global {var}' au début de la fonction."
        ),
        "conseil":     (
            "Dès que Python voit '{var} = ...' n'importe où dans une fonction, "
            "il considère '{var}' comme locale pour toute la fonction, même les lignes au-dessus. "
            "C'est pourquoi lire '{var}' avant cette ligne provoque l'erreur."
        ),
    },

    # ────────────────────────────────────────────────────────────
    # AttributeError : accès à un attribut inexistant sur un objet
    # ────────────────────────────────────────────────────────────
    {
        "id":          "var.attribute_error",
        "pattern":     r"AttributeError: '(.+)' object has no attribute '(.+)'",
        "description": "L'objet de type '{obj}' ne possède pas d'attribut ou de méthode appelé '{attr}'.",
        "solution":    (
            "Vérifie que '{attr}' est bien orthographié. "
            "Utilise dir({obj_instance}) dans la console pour voir tous les attributs disponibles."
        ),
        "conseil":     (
            "Causes fréquentes : faute de frappe dans le nom, "
            "mauvais type d'objet (ex. appeler .append() sur un tuple au lieu d'une liste), "
            "ou attribut non initialisé dans __init__."
        ),
    },

]
