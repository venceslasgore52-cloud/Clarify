"""
Patterns de détection et d'explication des erreurs liées aux types Python.

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator pour récupérer la traduction
  - pattern     : expression régulière appliquée sur le message d'erreur Python brut
  - description : explication courte de ce qui s'est passé (utilise {op}, {type1}, {type2}, {obj}…)
  - solution    : action concrète à faire pour corriger l'erreur
  - conseil     : explication du mécanisme Python sous-jacent pour mieux comprendre le pourquoi
"""

PATTERNS = [

    # ──────────────────────────────────────────────────────────
    # TypeError : opération entre deux types incompatibles
    # ──────────────────────────────────────────────────────────
    {
        "id":          "type.unsupported_operand",
        "pattern":     r"TypeError: unsupported operand type\(s\) for (.+): '(.+)' and '(.+)'",
        "description": "L'opération '{op}' ne peut pas s'appliquer entre un '{type1}' et un '{type2}'.",
        "solution":    (
            "Convertis l'une des valeurs au bon type avant l'opération. "
            "Exemple : int('{type2}') ou str('{type1}') selon ce que tu veux faire."
        ),
        "conseil":     (
            "Python ne mélange pas les types automatiquement. "
            "Tu ne peux pas additionner un nombre et une chaîne sans conversion explicite : "
            "5 + '3' → erreur, mais 5 + int('3') → 8."
        ),
    },

    # ───────────────────────────────────────────────────────────────
    # TypeError : objet appelé comme une fonction alors qu'il ne l'est pas
    # ───────────────────────────────────────────────────────────────
    {
        "id":          "type.not_callable",
        "pattern":     r"TypeError: '(.+)' object is not callable",
        "description": "Un objet de type '{obj}' est appelé avec () comme si c'était une fonction, mais ce n'en est pas une.",
        "solution":    (
            "Supprime les parenthèses si tu veux lire la valeur, "
            "ou vérifie que tu n'as pas écrasé accidentellement un nom de fonction "
            "(ex. list = [1, 2] puis list() plantera)."
        ),
        "conseil":     (
            "Utiliser un nom de variable identique à une fonction intégrée (list, dict, str, len…) "
            "masque la fonction. '{obj} = ...' remplace la fonction dans ta portée locale."
        ),
    },

]
