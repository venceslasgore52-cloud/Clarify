"""
Patterns de détection et d'explication des erreurs de configuration Django (settings.py).

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator
  - pattern     : expression régulière sur le message d'erreur brut
  - description : explication courte de ce qui s'est passé
  - solution    : action concrète pour corriger l'erreur
  - conseil     : mécanisme Django sous-jacent pour comprendre le pourquoi
"""

PATTERNS = [

    # ──────────────────────────────────────────────────────────
    # ImproperlyConfigured : settings.py mal configuré
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.config.improperly_configured",
        "pattern":     r"django\.core\.exceptions\.ImproperlyConfigured: (.+)",
        "description": "Django a détecté une configuration incorrecte dans settings.py : '{message}'.",
        "solution":    (
            "1. Lis le message — il pointe vers le paramètre exact à corriger.\n"
            "2. Vérifie les paramètres obligatoires : SECRET_KEY, DATABASES, INSTALLED_APPS.\n"
            "3. Assure-toi que DJANGO_SETTINGS_MODULE pointe vers le bon fichier settings."
        ),
        "conseil":     (
            "Django valide sa configuration au démarrage. "
            "ImproperlyConfigured est levée avant même le premier traitement de requête, "
            "ce qui facilite le débogage. "
            "Utilise python manage.py check pour détecter tous les problèmes de configuration "
            "sans lancer le serveur."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # Django non configuré : settings non chargés
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.config.not_configured",
        "pattern":     r"django\.core\.exceptions\.ImproperlyConfigured: Requested setting (.+), but settings are not configured",
        "description": "Django essaie d'accéder à '{setting}' mais les settings ne sont pas encore chargés.",
        "solution":    (
            "1. Définis la variable d'environnement avant d'importer Django :\n"
            "   import os\n"
            "   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monprojet.settings')\n"
            "2. Ou appelle django.setup() explicitement dans les scripts standalone :\n"
            "   import django; django.setup()"
        ),
        "conseil":     (
            "Cette erreur arrive souvent dans des scripts Python qui importent des modèles Django "
            "sans initialiser Django au préalable. "
            "manage.py et wsgi.py font cela automatiquement — "
            "dans un script custom, tu dois le faire toi-même."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # SECRET_KEY vide ou manquante
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.config.secret_key_missing",
        "pattern":     r"django\.core\.exceptions\.ImproperlyConfigured: The SECRET_KEY setting must not be empty",
        "description": "La SECRET_KEY de Django est vide ou absente dans settings.py.",
        "solution":    (
            "1. Génère une nouvelle clé sécurisée :\n"
            "   python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\"\n"
            "2. Stocke-la dans une variable d'environnement, jamais en clair dans le code :\n"
            "   SECRET_KEY = os.environ.get('SECRET_KEY')\n"
            "3. Utilise python-decouple ou django-environ pour gérer les variables d'env."
        ),
        "conseil":     (
            "SECRET_KEY est utilisée pour signer les cookies de session, les tokens CSRF et bien d'autres mécanismes. "
            "Ne la commite jamais dans git — "
            "utilise un fichier .env ignoré par .gitignore. "
            "Si elle a été exposée, régénère-la immédiatement : "
            "toutes les sessions actives seront invalidées."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # DATABASES mal configuré
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.config.database_error",
        "pattern":     r"django\.db\.utils\.OperationalError: (.+)",
        "description": "Django ne peut pas se connecter à la base de données : '{message}'.",
        "solution":    (
            "1. Vérifie les paramètres DATABASES dans settings.py (HOST, PORT, NAME, USER, PASSWORD).\n"
            "2. Pour SQLite (développement), vérifie que le chemin du fichier .db est correct.\n"
            "3. Pour PostgreSQL/MySQL, vérifie que le serveur de base de données est démarré.\n"
            "4. Teste la connexion : python manage.py dbshell"
        ),
        "conseil":     (
            "OperationalError vient directement du pilote de base de données, pas de Django. "
            "Les messages varient selon le moteur (SQLite, PostgreSQL, MySQL). "
            "En développement, SQLite est recommandé — aucun serveur à démarrer, "
            "la base est un simple fichier .db dans ton projet."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # ALLOWED_HOSTS : hôte non autorisé (fréquent en production)
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.config.disallowed_host",
        "pattern":     r"django\.core\.exceptions\.DisallowedHost: Invalid HTTP_HOST header: '(.+)'",
        "description": "Le domaine '{host}' n'est pas dans la liste ALLOWED_HOSTS de settings.py.",
        "solution":    (
            "Ajoute le domaine à ALLOWED_HOSTS dans settings.py :\n"
            "   ALLOWED_HOSTS = ['monsite.com', 'www.monsite.com']\n"
            "En développement uniquement (jamais en production) :\n"
            "   ALLOWED_HOSTS = ['*']"
        ),
        "conseil":     (
            "ALLOWED_HOSTS est une protection contre les attaques par en-tête Host. "
            "Django refuse toute requête dont le domaine ne figure pas dans cette liste "
            "quand DEBUG=False. "
            "En production, liste explicitement chaque domaine et sous-domaine autorisé — "
            "ne jamais utiliser '*' en production."
        ),
    },

]
