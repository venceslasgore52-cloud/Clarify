"""
Patterns de détection et d'explication des erreurs liées à Redis
dans un projet Django (cache, sessions, Celery broker).

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator
  - pattern     : expression régulière sur le message d'erreur brut
  - description : explication courte de ce qui s'est passé
  - solution    : action concrète pour corriger l'erreur
  - conseil     : mécanisme Redis/Django sous-jacent pour comprendre le pourquoi
"""

PATTERNS = [

    # ──────────────────────────────────────────────────────────
    # ConnectionError : Redis inaccessible
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.redis.connection_error",
        "pattern":     r"redis\.exceptions\.ConnectionError: (.+)",
        "description": "Impossible de se connecter au serveur Redis : '{message}'.",
        "solution":    (
            "1. Vérifie que Redis est démarré :\n"
            "   redis-cli ping  → doit répondre PONG\n"
            "2. Vérifie l'URL dans settings.py :\n"
            "   CACHES = {'default': {'BACKEND': 'django_redis.cache.RedisCache',\n"
            "                         'LOCATION': 'redis://127.0.0.1:6379/1'}}\n"
            "3. Sur Windows, utilise Redis via WSL2 ou Docker :\n"
            "   docker run -p 6379:6379 redis"
        ),
        "conseil":     (
            "Redis écoute par défaut sur le port 6379. "
            "Si tu utilises un port différent, un mot de passe, ou une base autre que 0, "
            "l'URL suit ce format : redis://:motdepasse@host:port/numero_base. "
            "En production, ne jamais exposer Redis sur une interface publique sans authentification."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # TimeoutError : Redis ne répond pas assez vite
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.redis.timeout",
        "pattern":     r"redis\.exceptions\.TimeoutError",
        "description": "Redis n'a pas répondu dans le délai imparti.",
        "solution":    (
            "1. Vérifie la charge du serveur Redis (redis-cli info stats).\n"
            "2. Augmente le timeout de connexion dans les options :\n"
            "   'OPTIONS': {'socket_connect_timeout': 5, 'socket_timeout': 5}\n"
            "3. Vérifie la latence réseau entre ton serveur Django et Redis."
        ),
        "conseil":     (
            "Redis est très rapide — un timeout signale généralement un problème réseau "
            "ou un serveur Redis surchargé (trop de connexions, mémoire saturée). "
            "Surveille redis-cli info memory pour voir si Redis approche de sa limite mémoire "
            "(maxmemory dans redis.conf)."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # ResponseError : commande Redis refusée
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.redis.response_error",
        "pattern":     r"redis\.exceptions\.ResponseError: (.+)",
        "description": "Redis a refusé la commande : '{message}'.",
        "solution":    (
            "1. WRONGTYPE : tu appliques une commande sur un mauvais type de clé\n"
            "   (ex. LPUSH sur une clé qui contient un string). Supprime la clé et recommence.\n"
            "2. NOAUTH : authentification requise — ajoute le mot de passe dans l'URL.\n"
            "3. OOM : Redis est à court de mémoire — libère des clés ou augmente maxmemory."
        ),
        "conseil":     (
            "Redis est typé : chaque clé a un type (string, list, hash, set, sorted set). "
            "Appliquer une commande de liste sur une clé string lève WRONGTYPE. "
            "Utilise redis-cli TYPE ma_cle pour vérifier le type d'une clé."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # Cache Miss non géré : clé expirée ou absente du cache
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.redis.cache_miss",
        "pattern":     r"KeyError: .+ cache",
        "description": "La clé demandée n'existe pas ou a expiré dans le cache Redis.",
        "solution":    (
            "1. Utilise cache.get() avec une valeur par défaut :\n"
            "   from django.core.cache import cache\n"
            "   valeur = cache.get('ma_cle', valeur_par_defaut)\n"
            "2. Utilise le pattern cache-aside pour recalculer si absent :\n"
            "   valeur = cache.get('ma_cle')\n"
            "   if valeur is None:\n"
            "       valeur = calculer_valeur()\n"
            "       cache.set('ma_cle', valeur, timeout=300)"
        ),
        "conseil":     (
            "Ne jamais supposer qu'une clé existe dans le cache. "
            "Redis expire les clés selon le TTL (timeout) ou en cas de pression mémoire "
            "(politique d'éviction allkeys-lru). "
            "Ton code doit toujours gérer le cas où la valeur est absente du cache."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # django-redis non installé ou mal configuré
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.redis.backend_not_found",
        "pattern":     r"django\.core\.cache\.backends\.base\.InvalidCacheBackendError: (.+)",
        "description": "Le backend de cache Redis n'est pas trouvé : '{message}'.",
        "solution":    (
            "1. Installe django-redis : pip install django-redis\n"
            "2. Configure le backend dans settings.py :\n"
            "   CACHES = {\n"
            "       'default': {\n"
            "           'BACKEND': 'django_redis.cache.RedisCache',\n"
            "           'LOCATION': 'redis://127.0.0.1:6379/1',\n"
            "           'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'}\n"
            "       }\n"
            "   }"
        ),
        "conseil":     (
            "Django inclut un backend de cache Redis natif depuis la version 4.0 "
            "(django.core.cache.backends.redis.RedisCache), "
            "mais django-redis offre plus de fonctionnalités (compression, sérialisation custom). "
            "Vérifie que tu utilises le bon BACKEND selon ta version de Django et le package installé."
        ),
    },

]
