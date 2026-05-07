"""
Patterns de détection et d'explication des erreurs liées aux middlewares Django.

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator
  - pattern     : expression régulière sur le message d'erreur brut
  - description : explication courte de ce qui s'est passé
  - solution    : action concrète pour corriger l'erreur
  - conseil     : mécanisme Django sous-jacent pour comprendre le pourquoi
"""

PATTERNS = [

    # ──────────────────────────────────────────────────────────
    # CSRF : token manquant ou invalide
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.middleware.csrf_failed",
        "pattern":     r"django\.middleware\.csrf\.CsrfViewMiddleware: (.+)",
        "description": "La vérification CSRF a échoué : '{message}'.",
        "solution":    (
            "1. Dans les formulaires HTML, ajoute le tag CSRF :\n"
            "   <form method='post'>{% csrf_token %}</form>\n"
            "2. Pour les requêtes AJAX, inclus le token dans le header :\n"
            "   headers: {'X-CSRFToken': getCookie('csrftoken')}\n"
            "3. Pour une vue API sans formulaire HTML, utilise @csrf_exempt "
            "(uniquement si tu gères l'authentification autrement, ex. JWT)."
        ),
        "conseil":     (
            "CSRF (Cross-Site Request Forgery) est une attaque où un site malveillant "
            "soumet un formulaire à ta place. "
            "Le token CSRF prouve que la requête vient bien de ton propre formulaire. "
            "Ne désactive jamais CsrfViewMiddleware globalement — "
            "utilise @csrf_exempt uniquement sur les vues qui le justifient."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # SessionMiddleware manquant
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.middleware.session_missing",
        "pattern":     r"django\.contrib\.sessions\.backends\.base\.SessionBase: .+",
        "description": "Le middleware de session n'est pas correctement configuré.",
        "solution":    (
            "Vérifie que SessionMiddleware est dans MIDDLEWARE (avant AuthenticationMiddleware) :\n"
            "   MIDDLEWARE = [\n"
            "       'django.contrib.sessions.middleware.SessionMiddleware',\n"
            "       'django.middleware.common.CommonMiddleware',\n"
            "       'django.contrib.auth.middleware.AuthenticationMiddleware',\n"
            "       ...\n"
            "   ]"
        ),
        "conseil":     (
            "L'ordre des middlewares Django est crucial — ils s'exécutent de haut en bas "
            "pour les requêtes entrantes, et de bas en haut pour les réponses. "
            "AuthenticationMiddleware dépend de SessionMiddleware : "
            "SessionMiddleware doit toujours être placé avant."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # MiddlewareNotUsed : middleware qui se retire lui-même
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.middleware.not_used",
        "pattern":     r"django\.core\.exceptions\.MiddlewareNotUsed: (.+)",
        "description": "Le middleware '{middleware}' s'est retiré lui-même de la chaîne.",
        "solution":    (
            "1. Ce n'est pas forcément une erreur — certains middlewares se désactivent "
            "volontairement selon la configuration (ex. DEBUG=False).\n"
            "2. Si ce n'est pas voulu, vérifie la méthode __init__ du middleware : "
            "elle ne doit pas lever MiddlewareNotUsed dans ce contexte."
        ),
        "conseil":     (
            "Un middleware peut lever MiddlewareNotUsed dans son __init__ "
            "pour signaler à Django de l'ignorer complètement. "
            "C'est un mécanisme propre pour désactiver conditionnellement un middleware "
            "selon l'environnement (développement vs production)."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # ImproperlyConfigured : middleware mal écrit ou mal configuré
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.middleware.improperly_configured",
        "pattern":     r"django\.core\.exceptions\.ImproperlyConfigured: (.+[Mm]iddleware.+)",
        "description": "Un middleware est mal configuré ou mal écrit : '{message}'.",
        "solution":    (
            "1. Un middleware Django doit avoir la structure suivante :\n"
            "   class MonMiddleware:\n"
            "       def __init__(self, get_response):\n"
            "           self.get_response = get_response\n"
            "       def __call__(self, request):\n"
            "           # avant la vue\n"
            "           response = self.get_response(request)\n"
            "           # après la vue\n"
            "           return response\n"
            "2. Vérifie que le chemin dans MIDDLEWARE est correct (module.ClassName)."
        ),
        "conseil":     (
            "Depuis Django 1.10, les middlewares utilisent le nouveau style (callable). "
            "L'ancien style avec process_request/process_response est déprécié. "
            "get_response est la fonction qui appelle la vue suivante dans la chaîne — "
            "toujours l'appeler et retourner sa réponse."
        ),
    },

]
