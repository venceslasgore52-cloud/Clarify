"""
Patterns de détection et d'explication des erreurs liées aux collections Python
(listes, tuples, dictionnaires, ensembles).

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator pour récupérer la traduction
  - pattern     : expression régulière appliquée sur le message d'erreur Python brut
  - description : explication courte de ce qui s'est passé
  - solution    : action concrète à faire pour corriger l'erreur
  - conseil     : explication du mécanisme Python sous-jacent pour mieux comprendre le pourquoi

Note : AttributeError est couvert dans variables.py (id: var.attribute_error).
"""

PATTERNS = [

    # ──────────────────────────────────────────────────────────
    # IndexError : index hors des limites d'une liste ou d'un tuple
    # ──────────────────────────────────────────────────────────
    {
        "id":          "collections.index_error",
        "pattern":     r"IndexError: list index out of range",
        "description": "Tu essaies d'accéder à un index qui n'existe pas dans la liste.",
        "solution":    (
            "1. Vérifie la taille de la liste avant d'accéder à un index :\n"
            "   if index < len(ma_liste):\n"
            "       valeur = ma_liste[index]\n"
            "2. Pour accéder au dernier élément, utilise l'index -1 : ma_liste[-1]\n"
            "3. Pour parcourir tous les éléments sans risque : for element in ma_liste"
        ),
        "conseil":     (
            "Les index Python commencent à 0, pas à 1. "
            "Une liste de 5 éléments a les index 0, 1, 2, 3, 4 — "
            "accéder à l'index 5 déclenche IndexError. "
            "Les index négatifs partent de la fin : -1 = dernier, -2 = avant-dernier, etc."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # IndexError : index hors des limites d'un tuple
    # ──────────────────────────────────────────────────────────
    {
        "id":          "collections.tuple_index_error",
        "pattern":     r"IndexError: tuple index out of range",
        "description": "Tu essaies d'accéder à un index qui n'existe pas dans le tuple.",
        "solution":    (
            "1. Vérifie la taille du tuple : len(mon_tuple)\n"
            "2. Les mêmes règles qu'une liste s'appliquent : index de 0 à len-1.\n"
            "3. Pour déstructurer un tuple en variables : a, b, c = mon_tuple "
            "(plus sûr que l'accès par index)"
        ),
        "conseil":     (
            "Un tuple est comme une liste mais immuable (non modifiable). "
            "IndexError sur un tuple vient souvent d'un retour de fonction qui renvoie "
            "moins de valeurs que prévu, ou d'un tuple vide () accédé sans vérification."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # IndexError : index hors des limites d'une chaîne
    # ──────────────────────────────────────────────────────────
    {
        "id":          "collections.string_index_error",
        "pattern":     r"IndexError: string index out of range",
        "description": "Tu essaies d'accéder à un caractère à un index qui n'existe pas dans la chaîne.",
        "solution":    (
            "1. Vérifie la longueur de la chaîne : len(ma_chaine)\n"
            "2. Pour parcourir caractère par caractère sans risque : for c in ma_chaine\n"
            "3. Pour extraire une partie : ma_chaine[debut:fin] "
            "(le slicing ne lève pas IndexError même si les bornes dépassent)"
        ),
        "conseil":     (
            "Une chaîne vide '' a une longueur de 0 — tout accès par index dessus lève IndexError. "
            "Vérifie qu'une chaîne n'est pas vide avant d'y accéder : if ma_chaine: ..."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # KeyError : clé inexistante dans un dictionnaire
    # ──────────────────────────────────────────────────────────
    {
        "id":          "collections.key_error",
        "pattern":     r"KeyError: (.+)",
        "description": "La clé '{key}' n'existe pas dans le dictionnaire.",
        "solution":    (
            "1. Utilise .get() pour obtenir une valeur par défaut si la clé est absente :\n"
            "   valeur = mon_dict.get('{key}', valeur_par_defaut)\n"
            "2. Vérifie la présence de la clé avant d'y accéder :\n"
            "   if '{key}' in mon_dict:\n"
            "       valeur = mon_dict['{key}']\n"
            "3. Pour une valeur par défaut automatique à la création, utilise defaultdict :\n"
            "   from collections import defaultdict\n"
            "   mon_dict = defaultdict(list)"
        ),
        "conseil":     (
            "Contrairement aux listes, les dictionnaires n'ont pas d'ordre garanti d'index. "
            "Accéder à une clé inexistante avec [] lève KeyError immédiatement. "
            ".get() est la méthode la plus propre pour éviter l'erreur : "
            "elle retourne None (ou ta valeur par défaut) sans planter."
        ),
    },

]
