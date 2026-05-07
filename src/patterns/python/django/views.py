"""
Patterns de détection et d'explication des erreurs liées aux vues Django.

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator
  - pattern     : expression régulière sur le message d'erreur brut
  - description : explication courte de ce qui s'est passé
  - solution    : action concrète pour corriger l'erreur
  - conseil     : mécanisme Django sous-jacent pour comprendre le pourquoi
"""

PATTERNS = [

    # ──────────────────────────────────────────────────────────
    # Http404 : ressource introuvable dans une vue
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.views.http404",
        "pattern":     r"django\.http\.response\.Http404: ?(.+)?",
        "description": "La vue n'a pas trouvé la ressource demandée et a renvoyé une page 404.",
        "solution":    (
            "1. Utilise get_object_or_404() au lieu d'un .get() direct :\n"
            "   from django.shortcuts import get_object_or_404\n"
            "   objet = get_object_or_404(MonModel, pk=pk)\n"
            "2. Vérifie que l'URL transmise correspond bien à un objet existant en base."
        ),
        "conseil":     (
            "get_object_or_404() combine Model.objects.get() et la levée de Http404 "
            "en une seule ligne lisible. "
            "En production (DEBUG=False), Django affiche ta page 404 personnalisée "
            "définie dans templates/404.html."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # PermissionDenied : accès refusé dans une vue
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.views.permission_denied",
        "pattern":     r"django\.core\.exceptions\.PermissionDenied",
        "description": "L'utilisateur n'a pas les droits nécessaires pour accéder à cette vue.",
        "solution":    (
            "1. Protège la vue avec @login_required ou @permission_required :\n"
            "   from django.contrib.auth.decorators import login_required\n"
            "   @login_required\n"
            "   def ma_vue(request): ...\n"
            "2. Pour les class-based views, utilise LoginRequiredMixin."
        ),
        "conseil":     (
            "PermissionDenied renvoie automatiquement une réponse HTTP 403. "
            "Tu peux personnaliser la page 403 en créant templates/403.html. "
            "Pour des règles fines, utilise django-guardian ou le système de permissions intégré."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # ValueError dans une vue : type incorrect passé à la vue
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.views.value_error",
        "pattern":     r"ValueError: (.+)",
        "description": "Une valeur incorrecte a été passée dans la vue : '{message}'.",
        "solution":    (
            "1. Valide les données entrantes avec un formulaire Django avant de les utiliser :\n"
            "   form = MonForm(request.POST)\n"
            "   if form.is_valid():\n"
            "       valeur = form.cleaned_data['champ']\n"
            "2. Utilise int(), float() dans un try/except si tu convertis des paramètres d'URL."
        ),
        "conseil":     (
            "Ne fais jamais confiance aux données venant de request.GET ou request.POST "
            "sans validation. Les formulaires Django (forms.py) centralisent la validation "
            "et nettoient les données automatiquement via cleaned_data."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # SuspiciousOperation : requête Django jugée malveillante
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.views.suspicious_operation",
        "pattern":     r"django\.core\.exceptions\.SuspiciousOperation: ?(.+)?",
        "description": "Django a détecté une opération suspecte ou invalide : '{message}'.",
        "solution":    (
            "1. Ne manipule pas manuellement les cookies de session ou les tokens CSRF.\n"
            "2. Si l'erreur vient d'un upload de fichier, vérifie que le nom de fichier "
            "ne contient pas de caractères interdits (ex. '../').\n"
            "3. Assure-toi que le middleware CSRF est bien activé dans MIDDLEWARE."
        ),
        "conseil":     (
            "Django lève SuspiciousOperation pour protéger l'application. "
            "Elle retourne une réponse 400 (Bad Request) et ne doit jamais être ignorée. "
            "Sous-classes fréquentes : DisallowedHost, InvalidSessionKey, SuspiciousFileOperation."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # ImproperlyConfigured : vue mal configurée
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.views.improperly_configured",
        "pattern":     r"django\.core\.exceptions\.ImproperlyConfigured: (.+)",
        "description": "La vue est mal configurée : '{message}'.",
        "solution":    (
            "1. Lis le message — il indique exactement ce qui manque.\n"
            "2. Cas fréquents avec les class-based views :\n"
            "   - Oubli de 'model' ou 'queryset' dans une ListView/DetailView\n"
            "   - Oubli de 'template_name' quand le nom ne suit pas la convention\n"
            "   - Oubli de 'fields' ou 'form_class' dans une CreateView/UpdateView"
        ),
        "conseil":     (
            "Les class-based views Django ont des attributs obligatoires selon leur type. "
            "ImproperlyConfigured est levée au démarrage ou au premier appel de la vue, "
            "pas à l'exécution — ce qui facilite le débogage."
        ),
    },

]
