"""
Patterns de détection et d'explication des erreurs de syntaxe Python.

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator pour récupérer la traduction
  - pattern     : expression régulière appliquée sur le message d'erreur Python brut
  - description : explication courte de ce qui s'est passé
  - solution    : action concrète à faire pour corriger l'erreur
  - conseil     : explication du mécanisme Python sous-jacent pour mieux comprendre le pourquoi

Note : SyntaxError, IndentationError et TabError sont détectées AVANT l'exécution.
Python refuse de lancer le programme tant que ces erreurs existent.
"""

PATTERNS = [

    # ──────────────────────────────────────────────────────────
    # SyntaxError : code illisible par l'interpréteur Python
    # ──────────────────────────────────────────────────────────
    {
        "id":          "syntax.invalid",
        "pattern":     r"SyntaxError: invalid syntax",
        "description": "Python ne comprend pas cette ligne — la syntaxe est incorrecte.",
        "solution":    (
            "1. Regarde la ligne indiquée ET la ligne juste au-dessus : "
            "l'erreur vient souvent de la ligne précédente (parenthèse non fermée, virgule manquante).\n"
            "2. Causes fréquentes :\n"
            "   - Parenthèse, crochet ou accolade non fermé(e)\n"
            "   - Deux-points ':' manquants après if / for / def / class\n"
            "   - Mot-clé Python utilisé comme nom de variable (ex. class = 5)\n"
            "   - Opérateur incorrect (ex. == au lieu de = dans une assignation)"
        ),
        "conseil":     (
            "Python signale la ligne où il a renoncé à comprendre le code, "
            "pas forcément là où l'erreur a été commise. "
            "Si la ligne indiquée semble correcte, remonte d'une ou deux lignes."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # SyntaxError : EOF inattendu — bloc ouvert jamais fermé
    # ──────────────────────────────────────────────────────────
    {
        "id":          "syntax.unexpected_eof",
        "pattern":     r"SyntaxError: unexpected EOF while parsing",
        "description": "Python a atteint la fin du fichier sans que tous les blocs soient fermés.",
        "solution":    (
            "1. Cherche une parenthèse, un crochet ou une accolade ouverte sans sa fermeture.\n"
            "2. Vérifie que chaque bloc (if, for, def, class) contient au moins une instruction.\n"
            "3. Un bloc vide doit contenir 'pass' pour être valide :\n"
            "   def ma_fonction():\n"
            "       pass"
        ),
        "conseil":     (
            "Python construit un arbre de blocs imbriqués en lisant ton fichier. "
            "Si un bloc n'est jamais fermé, Python arrive à la fin du fichier sans avoir "
            "terminé sa lecture — d'où 'unexpected EOF' (End Of File)."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # SyntaxError : caractère invalide dans le code source
    # ──────────────────────────────────────────────────────────
    {
        "id":          "syntax.invalid_character",
        "pattern":     r"SyntaxError: invalid character '(.+)' \(U\+([0-9A-Fa-f]+)\)",
        "description": "Le caractère '{char}' (Unicode U+{code}) n'est pas autorisé dans le code Python.",
        "solution":    (
            "1. Remplace le caractère par son équivalent ASCII standard.\n"
            "2. Causes fréquentes : copier-coller depuis un PDF ou un traitement de texte "
            "qui remplace les guillemets droits par des guillemets typographiques "
            "(' ' au lieu de ' ') ou les tirets par des tirets longs (— au lieu de -)."
        ),
        "conseil":     (
            "Les éditeurs de texte riches (Word, Notion, Google Docs) transforment "
            "automatiquement certains caractères en variantes typographiques. "
            "Toujours écrire du code dans un éditeur de code (VS Code, PyCharm) "
            "qui conserve les caractères ASCII exacts."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # IndentationError : indentation incorrecte
    # ──────────────────────────────────────────────────────────
    {
        "id":          "syntax.indentation_error",
        "pattern":     r"IndentationError: (.+)",
        "description": "L'indentation de cette ligne est incorrecte : {message}.",
        "solution":    (
            "1. Vérifie que toutes les lignes d'un même bloc ont exactement la même indentation.\n"
            "2. Utilise toujours des espaces OU toujours des tabulations — pas les deux.\n"
            "3. La convention Python (PEP 8) recommande 4 espaces par niveau d'indentation.\n"
            "4. Active l'affichage des espaces/tabulations dans VS Code "
            "(View → Render Whitespace) pour voir les différences."
        ),
        "conseil":     (
            "En Python, l'indentation définit la structure du programme — "
            "elle remplace les accolades {} d'autres langages. "
            "Une ligne trop indentée ou pas assez change complètement "
            "à quel bloc elle appartient, ce que Python refuse si c'est incohérent."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # IndentationError : bloc attendu mais ligne non indentée
    # ──────────────────────────────────────────────────────────
    {
        "id":          "syntax.expected_indented_block",
        "pattern":     r"IndentationError: expected an indented block after '(.+)' statement on line (\d+)",
        "description": "Le bloc après '{statement}' (ligne {line}) est vide ou non indenté.",
        "solution":    (
            "1. Indente le contenu du bloc avec 4 espaces.\n"
            "2. Si le bloc est intentionnellement vide pour l'instant, utilise 'pass' :\n"
            "   if condition:\n"
            "       pass"
        ),
        "conseil":     (
            "Chaque structure qui se termine par ':' (if, else, for, while, def, class, try…) "
            "attend obligatoirement au moins une ligne indentée après elle. "
            "Python ne tolère pas les blocs vides sans 'pass'."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # TabError : mélange de tabulations et d'espaces
    # ──────────────────────────────────────────────────────────
    {
        "id":          "syntax.tab_error",
        "pattern":     r"TabError: inconsistent use of tabs and spaces in indentation",
        "description": "Ce fichier mélange des tabulations et des espaces pour l'indentation.",
        "solution":    (
            "1. Dans VS Code : ouvre la palette de commandes (Ctrl+Shift+P) → "
            "'Convert Indentation to Spaces' pour tout normaliser en espaces.\n"
            "2. En ligne de commande : python -tt mon_script.py signale toutes les lignes mixtes.\n"
            "3. Configure ton éditeur pour insérer automatiquement des espaces quand tu appuies sur Tab."
        ),
        "conseil":     (
            "Python 3 interdit strictement de mélanger tabulations et espaces dans un même fichier. "
            "Python 2 l'autorisait, ce qui causait des bugs invisibles — "
            "une tabulation peut visuellement ressembler à 4 ou 8 espaces selon l'éditeur, "
            "mais Python les traite différemment. Python 3 a corrigé ce problème en le rendant illégal."
        ),
    },

]
