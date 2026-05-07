"""
Patterns de détection et d'explication des erreurs liées à l'ORM Django.

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator
  - pattern     : expression régulière sur le message d'erreur brut
  - description : explication courte de ce qui s'est passé
  - solution    : action concrète pour corriger l'erreur
  - conseil     : mécanisme Django sous-jacent pour comprendre le pourquoi
"""

PATTERNS = [

    # ──────────────────────────────────────────────────────────
    # DoesNotExist : objet introuvable en base de données
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.orm.does_not_exist",
        "pattern":     r"(\w+)\.DoesNotExist: (\w+) matching query does not exist",
        "description": "Aucun objet '{model}' ne correspond à cette requête en base de données.",
        "solution":    (
            "1. Remplace .get() par get_object_or_404() dans les vues :\n"
            "   from django.shortcuts import get_object_or_404\n"
            "   objet = get_object_or_404({model}, pk=pk)\n"
            "2. Ou utilise un try/except pour gérer le cas :\n"
            "   try:\n"
            "       objet = {model}.objects.get(pk=pk)\n"
            "   except {model}.DoesNotExist:\n"
            "       objet = None"
        ),
        "conseil":     (
            ".get() lève DoesNotExist si aucun résultat n'est trouvé, "
            "et MultipleObjectsReturned s'il en trouve plusieurs. "
            "Pour récupérer un seul objet ou None sans exception, utilise :\n"
            "{model}.objects.filter(pk=pk).first()"
        ),
    },

    # ──────────────────────────────────────────────────────────
    # MultipleObjectsReturned : .get() a retourné plusieurs objets
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.orm.multiple_objects",
        "pattern":     r"(\w+)\.MultipleObjectsReturned: get\(\) returned more than one (\w+)",
        "description": "'{model}'.objects.get() a trouvé plusieurs objets au lieu d'un seul.",
        "solution":    (
            "1. Affine ta requête pour qu'elle cible un seul objet (ajoute des filtres).\n"
            "2. Si tu veux le premier résultat : {model}.objects.filter(...).first()\n"
            "3. Si tu attends une liste : utilise .filter() au lieu de .get()"
        ),
        "conseil":     (
            ".get() est conçu pour récupérer un objet unique identifié sans ambiguïté. "
            "Si plusieurs lignes correspondent à ta condition, "
            "c'est souvent le signe que le filtre n'est pas assez précis "
            "ou que des doublons existent en base."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # FieldError : champ inexistant dans une requête ORM
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.orm.field_error",
        "pattern":     r"django\.core\.exceptions\.FieldError: (.+)",
        "description": "Erreur sur un champ de modèle dans une requête ORM : '{message}'.",
        "solution":    (
            "1. Vérifie l'orthographe du champ — Django est sensible à la casse.\n"
            "2. Pour filtrer sur une relation, utilise __ (double underscore) :\n"
            "   Commande.objects.filter(client__nom='Dupont')\n"
            "3. Consulte les champs disponibles avec : {model}._meta.get_fields()"
        ),
        "conseil":     (
            "L'ORM Django traduit tes filtres Python en SQL. "
            "Si un champ n'existe pas dans le modèle, Django lève FieldError "
            "avant même d'envoyer la requête à la base de données. "
            "Le __ permet de traverser les relations (ForeignKey, ManyToMany)."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # IntegrityError : violation de contrainte en base de données
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.orm.integrity_error",
        "pattern":     r"django\.db\.utils\.IntegrityError: (.+)",
        "description": "Une contrainte de base de données a été violée : '{message}'.",
        "solution":    (
            "1. Pour les doublons sur un champ unique :\n"
            "   objet, created = MonModel.objects.get_or_create(email=email)\n"
            "2. Pour une clé étrangère nulle sur un champ NOT NULL, assure-toi de fournir la valeur.\n"
            "3. Encapsule dans un try/except pour gérer proprement :\n"
            "   from django.db import IntegrityError\n"
            "   try:\n"
            "       objet.save()\n"
            "   except IntegrityError:\n"
            "       ..."
        ),
        "conseil":     (
            "IntegrityError vient de la base de données, pas de Django. "
            "Causes fréquentes : champ unique= True avec une valeur déjà existante, "
            "clé étrangère pointant vers un objet supprimé (CASCADE non configuré), "
            "ou champ null=False sans valeur par défaut lors d'une migration."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # ProgrammingError : migration manquante ou schéma désynchronisé
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.orm.programming_error",
        "pattern":     r"django\.db\.utils\.ProgrammingError: (.+)",
        "description": "La base de données et les modèles Django sont désynchronisés : '{message}'.",
        "solution":    (
            "1. Génère les migrations manquantes : python manage.py makemigrations\n"
            "2. Applique-les : python manage.py migrate\n"
            "3. Si la table n'existe pas du tout : vérifie que l'app est dans INSTALLED_APPS."
        ),
        "conseil":     (
            "ProgrammingError signifie que Django essaie d'exécuter une requête SQL "
            "sur une table ou une colonne qui n'existe pas encore en base. "
            "Cela arrive quand tu modifies un modèle sans créer la migration correspondante. "
            "Utilise python manage.py showmigrations pour voir l'état des migrations."
        ),
    },

]
