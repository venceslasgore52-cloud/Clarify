"""
Patterns de détection et d'explication des erreurs liées aux URLs Django.

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator
  - pattern     : expression régulière sur le message d'erreur brut
  - description : explication courte de ce qui s'est passé
  - solution    : action concrète pour corriger l'erreur
  - conseil     : mécanisme Django sous-jacent pour comprendre le pourquoi
"""

PATTERNS = [

    # ──────────────────────────────────────────────────────────
    # NoReverseMatch : reverse() ne trouve pas l'URL nommée
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.urls.no_reverse_match",
        "pattern":     r"django\.urls\.exceptions\.NoReverseMatch: Reverse for '(.+)' (.+)",
        "description": "Django ne trouve pas l'URL nommée '{name}' pour construire un lien.",
        "solution":    (
            "1. Vérifie que le nom existe dans urls.py avec name='...' :\n"
            "   path('articles/', views.liste, name='article-liste')\n"
            "2. Si l'URL est dans une app avec namespace, utilise le préfixe :\n"
            "   {% url 'blog:article-liste' %} ou reverse('blog:article-liste')\n"
            "3. Vérifie que les arguments obligatoires sont bien fournis :\n"
            "   reverse('article-detail', args=[pk])"
        ),
        "conseil":     (
            "NoReverseMatch est levée quand reverse() ou {% url %} cherche un nom d'URL "
            "qui n'existe pas ou reçoit les mauvais arguments. "
            "Utilise python manage.py show_urls (avec django-extensions) "
            "pour lister toutes les URLs et leurs noms disponibles."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # Resolver404 : aucune URL ne correspond à la requête
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.urls.resolver_404",
        "pattern":     r"django\.urls\.exceptions\.Resolver404: \{'tried': .+, 'path': '(.+)'\}",
        "description": "Aucune URL configurée ne correspond au chemin '{path}'.",
        "solution":    (
            "1. Vérifie que le chemin est bien défini dans urls.py.\n"
            "2. Vérifie l'ordre des URL patterns — Django prend la première correspondance.\n"
            "3. Assure-toi que l'app est incluse dans le urls.py principal :\n"
            "   path('blog/', include('blog.urls'))"
        ),
        "conseil":     (
            "Django parcourt la liste urlpatterns de haut en bas et s'arrête à la première correspondance. "
            "Si aucune ne correspond, il lève Resolver404 (qui affiche la page 404). "
            "Active DEBUG=True pour voir toutes les URLs essayées dans le message d'erreur."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # ImproperlyConfigured : include() sans namespace ou app_name manquant
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.urls.missing_app_name",
        "pattern":     r"django\.core\.exceptions\.ImproperlyConfigured: .+app_name.+",
        "description": "Le namespace d'URL est défini mais 'app_name' est manquant dans urls.py.",
        "solution":    (
            "Ajoute app_name en haut du fichier urls.py de l'application :\n"
            "   app_name = 'blog'\n"
            "   urlpatterns = [...]"
        ),
        "conseil":     (
            "Quand tu utilises namespace= dans include(), Django exige que le fichier urls.py "
            "inclus déclare app_name pour éviter les conflits de noms entre applications. "
            "Sans app_name, Django ne sait pas à quelle app les noms d'URLs appartiennent."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # TypeError : argument manquant dans reverse() ou {% url %}
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.urls.missing_argument",
        "pattern":     r"NoReverseMatch: Reverse for '(.+)' with no arguments not found",
        "description": "L'URL '{name}' nécessite des arguments qui n'ont pas été fournis.",
        "solution":    (
            "Fournis les arguments requis par l'URL :\n"
            "   # Dans une vue Python :\n"
            "   reverse('article-detail', args=[article.pk])\n"
            "   # Dans un template :\n"
            "   {% url 'article-detail' article.pk %}"
        ),
        "conseil":     (
            "Un pattern URL avec <int:pk> ou <slug:slug> attend un argument au moment du reverse. "
            "Sans lui, Django ne peut pas construire l'URL. "
            "Vérifie le nombre et le type des arguments dans la définition path() correspondante."
        ),
    },

]
