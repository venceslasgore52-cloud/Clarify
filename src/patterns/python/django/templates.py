"""
Patterns de détection et d'explication des erreurs liées aux templates Django.

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator
  - pattern     : expression régulière sur le message d'erreur brut
  - description : explication courte de ce qui s'est passé
  - solution    : action concrète pour corriger l'erreur
  - conseil     : mécanisme Django sous-jacent pour comprendre le pourquoi
"""

PATTERNS = [

    # ──────────────────────────────────────────────────────────
    # TemplateDoesNotExist : fichier HTML introuvable
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.templates.not_found",
        "pattern":     r"django\.template\.exceptions\.TemplateDoesNotExist: (.+)",
        "description": "Le template '{template}' est introuvable.",
        "solution":    (
            "1. Vérifie que le fichier existe dans un dossier templates/ de ton app.\n"
            "2. Assure-toi que APP_DIRS=True dans TEMPLATES (settings.py) :\n"
            "   TEMPLATES = [{'BACKEND': ..., 'APP_DIRS': True, ...}]\n"
            "3. Si tu utilises DIRS, ajoute le chemin absolu :\n"
            "   'DIRS': [BASE_DIR / 'templates']"
        ),
        "conseil":     (
            "Django cherche les templates dans deux endroits selon ta configuration : "
            "les dossiers listés dans DIRS, et les sous-dossiers templates/ de chaque app "
            "si APP_DIRS=True. "
            "La convention est : monapp/templates/monapp/mon_template.html "
            "(le nom de l'app est répété pour éviter les conflits entre apps)."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # TemplateSyntaxError : erreur de syntaxe dans un template
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.templates.syntax_error",
        "pattern":     r"django\.template\.exceptions\.TemplateSyntaxError: (.+)",
        "description": "Erreur de syntaxe dans le template : '{message}'.",
        "solution":    (
            "1. Vérifie les balises de template mal fermées :\n"
            "   {% if condition %} ... {% endif %}  ← endif obligatoire\n"
            "   {% for item in liste %} ... {% endfor %}\n"
            "2. Vérifie qu'un tag custom est bien chargé en haut du template :\n"
            "   {% load mon_tag %}"
        ),
        "conseil":     (
            "Le moteur de templates Django est volontairement limité — "
            "il interdit le code Python arbitraire pour séparer logique et présentation. "
            "Si tu as besoin de logique complexe dans un template, "
            "déplace-la dans la vue ou crée un template tag personnalisé."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # VariableDoesNotExist : variable de contexte absente (mode strict)
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.templates.variable_missing",
        "pattern":     r"django\.template\.base\.VariableDoesNotExist: (.+)",
        "description": "Une variable du contexte de template n'existe pas : '{message}'.",
        "solution":    (
            "1. Vérifie que la variable est bien passée dans le contexte de la vue :\n"
            "   return render(request, 'template.html', {'ma_variable': valeur})\n"
            "2. Dans le template, utilise le filtre default pour une valeur de secours :\n"
            "   {{ ma_variable|default:'valeur par défaut' }}"
        ),
        "conseil":     (
            "Par défaut, Django affiche une chaîne vide pour les variables absentes "
            "au lieu de planter — VariableDoesNotExist n'est visible qu'en mode strict "
            "(string_if_invalid configuré dans TEMPLATES). "
            "C'est utile pour déboguer des templates qui affichent des zones vides inexpliquées."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # TypeError dans un filtre de template
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.templates.filter_type_error",
        "pattern":     r"TypeError: (.+) in template (.+) \(line (\d+)\)",
        "description": "Un filtre de template a reçu un type de données inattendu (ligne {line}) : '{message}'.",
        "solution":    (
            "1. Vérifie le type de la variable avant d'appliquer le filtre.\n"
            "2. Utilise le filtre default pour éviter les valeurs None :\n"
            "   {{ nombre|default:0|floatformat:2 }}\n"
            "3. Prépare les données dans la vue plutôt que de les transformer dans le template."
        ),
        "conseil":     (
            "Les filtres Django comme |date, |floatformat, |length "
            "attendent un type précis. Passer None ou un type incompatible lève TypeError. "
            "La bonne pratique est de préparer les données dans la vue (views.py) "
            "et de passer au template uniquement ce dont il a besoin, déjà formaté."
        ),
    },

]
