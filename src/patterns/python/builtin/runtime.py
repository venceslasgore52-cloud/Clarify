"""
Patterns de détection et d'explication des erreurs d'exécution Python.

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator pour récupérer la traduction
  - pattern     : expression régulière appliquée sur le message d'erreur Python brut
  - description : explication courte de ce qui s'est passé
  - solution    : action concrète à faire pour corriger l'erreur
  - conseil     : explication du mécanisme Python sous-jacent pour mieux comprendre le pourquoi
"""

PATTERNS = [

    # ──────────────────────────────────────────────────────────
    # ZeroDivisionError : division ou modulo par zéro
    # ──────────────────────────────────────────────────────────
    {
        "id":          "runtime.zero_division",
        "pattern":     r"ZeroDivisionError: (.+)",
        "description": "Une division par zéro a été tentée : {message}.",
        "solution":    (
            "1. Vérifie que le diviseur n'est jamais égal à zéro avant l'opération :\n"
            "   if diviseur != 0:\n"
            "       resultat = valeur / diviseur\n"
            "2. Ou utilise un bloc try/except pour gérer le cas :\n"
            "   try:\n"
            "       resultat = valeur / diviseur\n"
            "   except ZeroDivisionError:\n"
            "       resultat = 0"
        ),
        "conseil":     (
            "En mathématiques, diviser par zéro est indéfini. "
            "Python l'interdit strictement, contrairement à certains langages qui retournent 'Infinity'. "
            "Le modulo (%) et la division entière (//) déclenchent la même erreur si le diviseur vaut 0."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # RecursionError : profondeur maximale de récursion dépassée
    # ──────────────────────────────────────────────────────────
    {
        "id":          "runtime.recursion_error",
        "pattern":     r"RecursionError: maximum recursion depth exceeded(.+)?",
        "description": "La fonction s'appelle elle-même trop de fois — la limite de récursion est atteinte.",
        "solution":    (
            "1. Vérifie que ta fonction récursive a un cas de base qui arrête les appels :\n"
            "   def factorielle(n):\n"
            "       if n <= 1:       # cas de base — OBLIGATOIRE\n"
            "           return 1\n"
            "       return n * factorielle(n - 1)\n"
            "2. Si ta récursion est profonde par conception, augmente la limite (déconseillé) :\n"
            "   import sys; sys.setrecursionlimit(2000)\n"
            "3. Pour les grandes profondeurs, réécris la fonction en boucle iterative."
        ),
        "conseil":     (
            "Python limite la récursion à 1000 appels par défaut pour éviter un crash mémoire. "
            "Chaque appel de fonction empile un 'frame' en mémoire — "
            "sans cas de base, la pile grossit jusqu'à épuisement. "
            "La plupart des fonctions récursives peuvent être réécrites en boucle for/while "
            "qui ne consomme pas de pile d'appels."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # OverflowError : résultat numérique trop grand pour être représenté
    # ──────────────────────────────────────────────────────────
    {
        "id":          "runtime.overflow_error",
        "pattern":     r"OverflowError: (.+)",
        "description": "Le résultat du calcul est trop grand pour être stocké : {message}.",
        "solution":    (
            "1. Pour les flottants (float), utilise le module 'decimal' pour une précision arbitraire :\n"
            "   from decimal import Decimal\n"
            "   resultat = Decimal('1e500')\n"
            "2. Pour les entiers, Python gère nativement les grands entiers — "
            "OverflowError sur un int vient souvent d'une conversion vers float.\n"
            "3. Vérifie que tu n'opères pas sur des valeurs issues d'une bibliothèque C (numpy, etc.) "
            "qui utilise des types à taille fixe."
        ),
        "conseil":     (
            "En Python pur, les entiers (int) n'ont pas de limite de taille — "
            "ils grandissent en mémoire autant que nécessaire. "
            "OverflowError apparaît surtout avec les flottants (float), "
            "qui suivent la norme IEEE 754 et ont une valeur maximale d'environ 1.8 × 10^308."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # MemoryError : mémoire RAM insuffisante pour l'opération
    # ──────────────────────────────────────────────────────────
    {
        "id":          "runtime.memory_error",
        "pattern":     r"MemoryError",
        "description": "Python ne dispose plus de suffisamment de mémoire RAM pour continuer.",
        "solution":    (
            "1. Traite les données par morceaux (chunks) au lieu de tout charger en mémoire :\n"
            "   for chunk in pd.read_csv('fichier.csv', chunksize=1000):\n"
            "       traiter(chunk)\n"
            "2. Utilise des générateurs (yield) au lieu de listes pour les grandes séquences.\n"
            "3. Libère les variables volumineuses dont tu n'as plus besoin : del ma_liste\n"
            "4. Vérifie s'il y a une fuite mémoire (objets créés en boucle et jamais supprimés)."
        ),
        "conseil":     (
            "MemoryError signifie que le système d'exploitation a refusé d'allouer plus de RAM. "
            "Sur les machines 64 bits, cette erreur arrive rarement sauf avec de très grandes structures. "
            "Les causes les plus fréquentes : charger un fichier CSV ou JSON de plusieurs Go en une fois, "
            "ou construire une liste avec des millions d'éléments dans une boucle."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # TimeoutError : opération trop longue, délai dépassé
    # ──────────────────────────────────────────────────────────
    {
        "id":          "runtime.timeout_error",
        "pattern":     r"TimeoutError: (.+)?",
        "description": "Une opération a dépassé le délai autorisé et a été interrompue.",
        "solution":    (
            "1. Augmente le délai si l'opération est légitimement longue.\n"
            "2. Pour les requêtes réseau, ajoute un timeout explicite :\n"
            "   import requests\n"
            "   requests.get(url, timeout=10)  # 10 secondes max\n"
            "3. Pour tes propres fonctions, utilise signal (Unix) ou threading.Timer :\n"
            "   import threading\n"
            "   timer = threading.Timer(5.0, handle_timeout)\n"
            "   timer.start()"
        ),
        "conseil":     (
            "TimeoutError hérite d'OSError — c'est une erreur système, pas applicative. "
            "Elle est souvent levée par des opérations réseau (sockets, HTTP) "
            "ou des accès à des ressources externes qui ne répondent pas. "
            "Toujours définir un timeout sur les appels réseau : "
            "une connexion qui ne répond jamais bloque ton programme indéfiniment sans timeout."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # StopIteration : itérateur épuisé, plus aucun élément à retourner
    # ──────────────────────────────────────────────────────────
    {
        "id":          "runtime.stop_iteration",
        "pattern":     r"StopIteration",
        "description": "L'itérateur est épuisé — il n'y a plus d'éléments à parcourir.",
        "solution":    (
            "1. Utilise une boucle for au lieu d'appeler next() manuellement — "
            "elle gère StopIteration automatiquement.\n"
            "2. Si tu dois utiliser next(), fournis une valeur par défaut pour éviter l'erreur :\n"
            "   valeur = next(mon_iterateur, None)  # retourne None si épuisé\n"
            "3. Si l'erreur vient d'un générateur, vérifie que yield n'est pas atteint "
            "avant que toutes les valeurs soient produites."
        ),
        "conseil":     (
            "StopIteration est le signal normal qui indique à Python qu'un itérateur est terminé. "
            "La boucle for l'attrape silencieusement — c'est pourquoi elle s'arrête proprement. "
            "Si tu la vois comme une erreur, c'est que tu appelles next() directement "
            "sans vérifier si l'itérateur a encore des valeurs. "
            "Depuis Python 3.7, lever StopIteration dans un générateur est interdit "
            "et se transforme en RuntimeError."
        ),
    },

]
