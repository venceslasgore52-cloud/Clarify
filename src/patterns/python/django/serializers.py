"""
Patterns de détection et d'explication des erreurs liées aux serializers
Django REST Framework (DRF).

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator
  - pattern     : expression régulière sur le message d'erreur brut
  - description : explication courte de ce qui s'est passé
  - solution    : action concrète pour corriger l'erreur
  - conseil     : mécanisme DRF sous-jacent pour comprendre le pourquoi
"""

PATTERNS = [

    # ──────────────────────────────────────────────────────────
    # ValidationError : données invalides lors de la désérialisation
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.serializers.validation_error",
        "pattern":     r"rest_framework\.exceptions\.ValidationError: (.+)",
        "description": "Les données envoyées au serializer sont invalides : '{message}'.",
        "solution":    (
            "1. Appelle is_valid() avant d'accéder aux données :\n"
            "   serializer = MonSerializer(data=request.data)\n"
            "   if serializer.is_valid():\n"
            "       serializer.save()\n"
            "   else:\n"
            "       return Response(serializer.errors, status=400)\n"
            "2. Consulte serializer.errors pour voir quel champ est invalide."
        ),
        "conseil":     (
            "DRF sépare les données brutes (data=) des données validées (validated_data). "
            "Accéder à validated_data sans appeler is_valid() lève AssertionError. "
            "is_valid(raise_exception=True) lève automatiquement ValidationError "
            "et renvoie une réponse 400 — utile dans les APIView."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # AssertionError : validated_data accédé sans is_valid()
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.serializers.assert_not_validated",
        "pattern":     r"AssertionError: You must call `\.is_valid\(\)` before calling `\.save\(\)`",
        "description": "Tu appelles .save() sur un serializer sans avoir appelé .is_valid() au préalable.",
        "solution":    (
            "Appelle toujours is_valid() avant save() :\n"
            "   serializer = MonSerializer(data=request.data)\n"
            "   if serializer.is_valid(raise_exception=True):\n"
            "       serializer.save()"
        ),
        "conseil":     (
            "DRF impose cet ordre pour éviter de sauvegarder des données non validées. "
            "is_valid() peuple validated_data et errors — "
            "sans lui, DRF ne sait pas si les données sont propres."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # ImproperlyConfigured : Meta.model ou Meta.fields manquant
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.serializers.missing_meta",
        "pattern":     r"AssertionError: Class (.+)Serializer missing \"Meta\" attribute",
        "description": "Le serializer '{name}' n'a pas de classe Meta définie.",
        "solution":    (
            "Ajoute une classe Meta dans ton serializer :\n"
            "   class MonSerializer(serializers.ModelSerializer):\n"
            "       class Meta:\n"
            "           model = MonModel\n"
            "           fields = ['id', 'nom', 'email']  # ou fields = '__all__'"
        ),
        "conseil":     (
            "ModelSerializer génère automatiquement les champs à partir du modèle, "
            "mais il a besoin de Meta.model pour savoir quel modèle utiliser "
            "et de Meta.fields pour savoir quels champs exposer. "
            "Évite fields = '__all__' en production : tu risques d'exposer "
            "des champs sensibles (mot de passe, tokens)."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # UniqueValidator : violation de contrainte unique via serializer
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.serializers.unique_error",
        "pattern":     r"rest_framework\.validators\.UniqueValidator: (.+)",
        "description": "La valeur fournie existe déjà en base de données et doit être unique.",
        "solution":    (
            "1. Vérifie côté client que la valeur n'est pas déjà utilisée avant d'envoyer.\n"
            "2. Dans la vue, retourne l'erreur proprement :\n"
            "   serializer.is_valid(raise_exception=True)  # renvoie 400 automatiquement\n"
            "3. Pour une mise à jour (PATCH/PUT), passe l'instance existante au serializer :\n"
            "   serializer = MonSerializer(instance, data=request.data, partial=True)"
        ),
        "conseil":     (
            "DRF ajoute automatiquement UniqueValidator sur les champs marqués unique=True "
            "dans le modèle. Ce validateur s'exécute avant la sauvegarde, "
            "ce qui est plus propre qu'attraper IntegrityError au niveau de la base."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # AuthenticationFailed : token invalide ou expiré
    # ──────────────────────────────────────────────────────────
    {
        "id":          "django.serializers.auth_failed",
        "pattern":     r"rest_framework\.exceptions\.AuthenticationFailed: (.+)",
        "description": "L'authentification a échoué : '{message}'.",
        "solution":    (
            "1. Vérifie que le token envoyé dans le header est correct :\n"
            "   Authorization: Bearer <ton_token>\n"
            "2. Si le token est expiré, régénère-en un nouveau via l'endpoint de refresh.\n"
            "3. Vérifie que l'utilisateur existe toujours et est actif (is_active=True)."
        ),
        "conseil":     (
            "DRF distingue AuthenticationFailed (identité invalide → 401) "
            "de PermissionDenied (identité valide mais droits insuffisants → 403). "
            "Utilise JWT (djangorestframework-simplejwt) pour une gestion moderne des tokens "
            "avec refresh automatique."
        ),
    },

]
