"""
Patterns de détection et d'explication des erreurs liées à Celery
(tâches asynchrones) dans un projet Django.

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator
  - pattern     : expression régulière sur le message d'erreur brut
  - description : explication courte de ce qui s'est passé
  - solution    : action concrète pour corriger l'erreur
  - conseil     : mécanisme Celery sous-jacent pour comprendre le pourquoi
"""

PATTERNS = [

    # ──────────────────────────────────────────────────────────
    # KombuError / broker inaccessible
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.celery.broker_unreachable",
        "pattern":     r"kombu\.exceptions\.OperationalError: (.+)",
        "description": "Celery ne peut pas se connecter au broker de messages : '{message}'.",
        "solution":    (
            "1. Vérifie que Redis ou RabbitMQ est démarré.\n"
            "2. Vérifie CELERY_BROKER_URL dans settings.py :\n"
            "   CELERY_BROKER_URL = 'redis://localhost:6379/0'\n"
            "3. Teste la connexion directement : redis-cli ping → doit répondre PONG."
        ),
        "conseil":     (
            "Celery a besoin d'un broker (Redis ou RabbitMQ) pour transmettre les tâches "
            "entre le code Django et les workers. "
            "Sans broker actif, .delay() et .apply_async() échouent immédiatement. "
            "En développement, Redis est recommandé — simple à installer et à démarrer."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # NotRegistered : tâche inconnue du worker
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.celery.task_not_registered",
        "pattern":     r"celery\.exceptions\.NotRegistered: '(.+)'",
        "description": "La tâche '{task}' n'est pas enregistrée dans le worker Celery.",
        "solution":    (
            "1. Vérifie que le module contenant la tâche est dans CELERY_IMPORTS ou autodiscover :\n"
            "   app.autodiscover_tasks()  # dans celery.py\n"
            "2. Redémarre le worker après toute modification de tâche :\n"
            "   celery -A monprojet worker --loglevel=info\n"
            "3. Vérifie que le décorateur @shared_task ou @app.task est bien présent."
        ),
        "conseil":     (
            "Le worker Celery charge les tâches au démarrage. "
            "Si tu ajoutes ou renommes une tâche, le worker doit être redémarré "
            "pour la connaître. "
            "autodiscover_tasks() cherche automatiquement les tâches dans les fichiers "
            "tasks.py de chaque app listée dans INSTALLED_APPS."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # TimeLimitExceeded : tâche trop longue
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.celery.time_limit_exceeded",
        "pattern":     r"celery\.exceptions\.TimeLimitExceeded: (.+)",
        "description": "La tâche '{task}' a dépassé sa limite de temps d'exécution.",
        "solution":    (
            "1. Augmente la limite de temps si la tâche est légitimement longue :\n"
            "   @shared_task(time_limit=300)  # 5 minutes\n"
            "   def ma_tache(): ...\n"
            "2. Découpe la tâche en sous-tâches plus petites avec Celery Canvas (chain, group).\n"
            "3. Optimise le code de la tâche (requêtes N+1, traitement par lots)."
        ),
        "conseil":     (
            "CELERYD_TASK_TIME_LIMIT (temps dur) et CELERYD_TASK_SOFT_TIME_LIMIT (temps doux) "
            "permettent de contrôler la durée des tâches. "
            "Le soft limit lève SoftTimeLimitExceeded que tu peux attraper pour faire un nettoyage. "
            "Le hard limit tue le worker sans préavis."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # Retry : tâche en échec relancée automatiquement
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.celery.max_retries_exceeded",
        "pattern":     r"celery\.exceptions\.MaxRetriesExceededError: (.+)",
        "description": "La tâche a épuisé toutes ses tentatives de relance sans succès.",
        "solution":    (
            "1. Augmente max_retries si l'opération nécessite plus de tentatives :\n"
            "   @shared_task(bind=True, max_retries=5)\n"
            "   def ma_tache(self): ...\n"
            "2. Ajoute un délai exponentiel entre les relances :\n"
            "   self.retry(exc=exc, countdown=2 ** self.request.retries)\n"
            "3. Traite le cas d'échec définitif dans un bloc except."
        ),
        "conseil":     (
            "Les relances automatiques sont utiles pour les erreurs transitoires "
            "(réseau, service temporairement indisponible). "
            "Utilise un backoff exponentiel pour ne pas surcharger le service en difficulté. "
            "Envoie les tâches en échec définitif dans une dead letter queue "
            "pour les analyser plus tard."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # Django non initialisé dans une tâche Celery
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.celery.django_not_setup",
        "pattern":     r"django\.core\.exceptions\.ImproperlyConfigured: Requested setting .+ but settings are not configured.+celery",
        "description": "Django n'est pas initialisé dans le contexte Celery.",
        "solution":    (
            "Assure-toi que celery.py initialise bien Django :\n"
            "   import os\n"
            "   from celery import Celery\n"
            "   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monprojet.settings')\n"
            "   app = Celery('monprojet')\n"
            "   app.config_from_object('django.conf:settings', namespace='CELERY')\n"
            "   app.autodiscover_tasks()"
        ),
        "conseil":     (
            "Le worker Celery est un processus séparé de Django. "
            "Il doit initialiser Django lui-même pour accéder aux modèles et aux settings. "
            "La configuration se fait dans monprojet/celery.py, "
            "importé depuis __init__.py du projet pour être chargé au démarrage."
        ),
    },

]
