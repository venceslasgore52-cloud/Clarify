"""
Patterns de détection et d'explication des erreurs système Python.

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator pour récupérer la traduction
  - pattern     : expression régulière appliquée sur le message d'erreur Python brut
  - description : explication courte de ce qui s'est passé
  - solution    : action concrète à faire pour corriger ou gérer l'erreur
  - conseil     : explication du mécanisme Python sous-jacent pour mieux comprendre le pourquoi
"""

PATTERNS = [

    # ──────────────────────────────────────────────────────────
    # SystemExit : arrêt volontaire du programme via sys.exit()
    # ──────────────────────────────────────────────────────────
    {
        "id":          "system.exit",
        "pattern":     r"SystemExit: (.+)",
        "description": "Le programme s'est arrêté volontairement avec le code de sortie '{code}'.",
        "solution":    (
            "1. Si ce n'est pas voulu, cherche les appels à sys.exit() ou raise SystemExit() dans ton code.\n"
            "2. Pour intercepter cet arrêt sans stopper le programme : "
            "utilise 'except SystemExit as e' dans un bloc try/except.\n"
            "3. Un code de sortie 0 signifie succès, tout autre valeur signale une erreur."
        ),
        "conseil":     (
            "SystemExit n'hérite pas d'Exception mais de BaseException. "
            "Un 'except Exception' classique ne l'attrape pas. "
            "C'est voulu : Python veut que le programme puisse toujours s'arrêter proprement, "
            "même si tu as un catch-all dans ton code."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # KeyboardInterrupt : arrêt par l'utilisateur (Ctrl+C)
    # ──────────────────────────────────────────────────────────
    {
        "id":          "system.keyboard_interrupt",
        "pattern":     r"KeyboardInterrupt",
        "description": "L'utilisateur a interrompu le programme manuellement (Ctrl+C).",
        "solution":    (
            "1. C'est souvent normal — l'utilisateur a voulu arrêter le programme.\n"
            "2. Pour faire un nettoyage propre avant l'arrêt (fermer des fichiers, sauvegarder) :\n"
            "   try:\n"
            "       ...\n"
            "   except KeyboardInterrupt:\n"
            "       print('Arrêt propre...')\n"
            "       # nettoyage ici"
        ),
        "conseil":     (
            "Comme SystemExit, KeyboardInterrupt hérite de BaseException, pas d'Exception. "
            "Si ton programme ignore Ctrl+C, vérifie que tu n'as pas un 'except Exception' "
            "qui consomme toutes les exceptions sans laisser passer KeyboardInterrupt."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # GeneratorExit : fermeture d'un générateur en cours d'exécution
    # ──────────────────────────────────────────────────────────
    {
        "id":          "system.generator_exit",
        "pattern":     r"GeneratorExit",
        "description": "Un générateur a été fermé avant d'avoir fini de produire toutes ses valeurs.",
        "solution":    (
            "1. C'est souvent normal : appeler .close() sur un générateur lève GeneratorExit à l'intérieur.\n"
            "2. Si tu veux exécuter du code de nettoyage quand le générateur se ferme, "
            "utilise un bloc try/finally dans la fonction générateur.\n"
            "3. Ne jamais ignorer GeneratorExit avec 'except GeneratorExit: pass' — "
            "cela empêche Python de fermer le générateur correctement."
        ),
        "conseil":     (
            "GeneratorExit est lancée à l'intérieur du générateur quand Python appelle .close() dessus. "
            "Elle signale au générateur qu'il doit s'arrêter. "
            "C'est un mécanisme interne de Python — tu la rencontres rarement sauf si tu écris "
            "des générateurs avancés avec des ressources à libérer (ex. connexions, fichiers)."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # RuntimeError : erreur générique détectée pendant l'exécution
    # ──────────────────────────────────────────────────────────
    {
        "id":          "system.runtime_error",
        "pattern":     r"RuntimeError: (.+)",
        "description": "Une erreur d'exécution s'est produite : '{message}'.",
        "solution":    (
            "1. Lis attentivement le message — il décrit le problème précis.\n"
            "2. Cas fréquents :\n"
            "   - 'maximum recursion depth exceeded' → ta fonction s'appelle elle-même à l'infini.\n"
            "   - 'dictionary changed size during iteration' → ne modifie pas un dict pendant une boucle for.\n"
            "   - 'super(): no arguments' → appel de super() hors d'une classe."
        ),
        "conseil":     (
            "RuntimeError est une erreur fourre-tout utilisée quand aucune autre catégorie ne convient. "
            "Le message qui l'accompagne est toujours plus important que le type lui-même. "
            "Les bibliothèques tierces l'utilisent aussi pour signaler leurs propres erreurs internes."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # NotImplementedError : méthode abstraite non implémentée
    # ──────────────────────────────────────────────────────────
    {
        "id":          "system.not_implemented",
        "pattern":     r"NotImplementedError: ?(.*)",
        "description": "Une méthode ou fonctionnalité requise n'a pas encore été implémentée : '{message}'.",
        "solution":    (
            "1. Si tu hérites d'une classe abstraite, implémente toutes les méthodes marquées "
            "avec 'raise NotImplementedError'.\n"
            "2. Si tu vois cette erreur dans une bibliothèque tierce, "
            "vérifie sa documentation — la fonctionnalité peut nécessiter une sous-classe spécifique."
        ),
        "conseil":     (
            "NotImplementedError est un signal volontaire laissé par le développeur : "
            "'cette méthode doit être réécrite dans une sous-classe'. "
            "C'est différent de NotImplemented (sans Error), qui est une valeur de retour "
            "spéciale utilisée dans les opérateurs Python comme __eq__ ou __add__."
        ),
    },

]
