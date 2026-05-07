"""
Patterns de détection et d'explication des erreurs liées aux fichiers Python.

Chaque entrée contient :
  - id          : identifiant unique utilisé par le translator pour récupérer la traduction
  - pattern     : expression régulière appliquée sur le message d'erreur Python brut
  - description : explication courte de ce qui s'est passé (utilise {filename}…)
  - solution    : action concrète à faire pour corriger l'erreur
  - conseil     : explication du mécanisme Python sous-jacent pour mieux comprendre le pourquoi
"""

PATTERNS = [

    # ──────────────────────────────────────────────────────────
    # FileNotFoundError : fichier ou dossier inexistant
    # ──────────────────────────────────────────────────────────
    {
        "id":          "file.not_found",
        "pattern":     r"FileNotFoundError: \[Errno 2\] No such file or directory: '(.+)'",
        "description": "Le fichier ou dossier '{filename}' est introuvable à l'emplacement spécifié.",
        "solution":    (
            "1. Vérifie que le chemin est correct et que le fichier existe bien.\n"
            "2. Si tu utilises un chemin relatif, assure-toi d'exécuter ton script "
            "depuis le bon dossier (ou utilise os.path.abspath() pour voir le chemin absolu résolu)."
        ),
        "conseil":     (
            "Python cherche les fichiers par rapport au dossier de travail courant (os.getcwd()). "
            "Un chemin comme 'data/fichier.txt' suppose que 'data/' est dans le même dossier "
            "que l'endroit où tu lances le script, pas là où le script est enregistré."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # FileExistsError : tentative de création d'un fichier déjà existant
    # ──────────────────────────────────────────────────────────
    {
        "id":          "file.already_exists",
        "pattern":     r"FileExistsError: \[Errno 17\] File exists: '(.+)'",
        "description": "Le fichier ou dossier '{filename}' existe déjà — Python refuse de l'écraser.",
        "solution":    (
            "1. Supprime ou renomme '{filename}' avant de le recréer.\n"
            "2. Pour créer un dossier sans erreur s'il existe déjà : "
            "os.makedirs('{filename}', exist_ok=True).\n"
            "3. Pour ouvrir un fichier en écrasant son contenu : open('{filename}', 'w')."
        ),
        "conseil":     (
            "Python protège les fichiers existants par défaut. "
            "Le mode 'x' de open() est conçu pour la création exclusive : "
            "il lève FileExistsError si le fichier est déjà là, ce qui évite d'écraser des données par accident."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # PermissionError : accès refusé par le système d'exploitation
    # ──────────────────────────────────────────────────────────
    {
        "id":          "file.permission_denied",
        "pattern":     r"PermissionError: \[Errno 13\] Permission denied: '(.+)'",
        "description": "Python n'a pas la permission d'accéder à '{filename}'.",
        "solution":    (
            "1. Vérifie les permissions du fichier (clic droit → Propriétés sur Windows, "
            "ls -l sur Unix).\n"
            "2. Sur Unix, accorde les droits nécessaires : chmod 644 '{filename}'.\n"
            "3. Sur Windows, vérifie que le fichier n'est pas ouvert dans un autre programme."
        ),
        "conseil":     (
            "Le système d'exploitation gère qui peut lire, écrire ou exécuter chaque fichier. "
            "Python ne peut pas contourner ces restrictions — même en tant qu'administrateur, "
            "certains fichiers système sont protégés."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # IsADirectoryError : open() reçoit un dossier à la place d'un fichier
    # ──────────────────────────────────────────────────────────
    {
        "id":          "file.is_directory",
        "pattern":     r"IsADirectoryError: \[Errno 21\] Is a directory: '(.+)'",
        "description": "'{filename}' est un dossier, pas un fichier — open() ne peut pas l'ouvrir.",
        "solution":    (
            "1. Vérifie ton chemin : tu as peut-être oublié le nom du fichier à la fin.\n"
            "2. Pour lister les fichiers dans ce dossier : os.listdir('{filename}').\n"
            "3. Pour parcourir les fichiers récursivement : pathlib.Path('{filename}').rglob('*')."
        ),
        "conseil":     (
            "open() est conçu pour les fichiers uniquement. "
            "Un chemin qui se termine par '/' ou un nom de dossier existant déclenchera cette erreur. "
            "Utilise os.path.isfile() pour vérifier qu'un chemin pointe bien vers un fichier avant de l'ouvrir."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # NotADirectoryError : opération de dossier sur un fichier
    # ──────────────────────────────────────────────────────────
    {
        "id":          "file.not_a_directory",
        "pattern":     r"NotADirectoryError: \[Errno 20\] Not a directory: '(.+)'",
        "description": "'{filename}' est un fichier, mais une opération réservée aux dossiers lui a été appliquée.",
        "solution":    (
            "1. Vérifie ton chemin — une partie du chemin pointe vers un fichier au lieu d'un dossier.\n"
            "2. Utilise os.path.isdir('{filename}') pour confirmer que le chemin est bien un dossier."
        ),
        "conseil":     (
            "Cette erreur est l'inverse de IsADirectoryError. "
            "Elle survient souvent quand un chemin contient un fichier là où Python attend un dossier, "
            "par exemple : 'mon_fichier.txt/sous_dossier' — 'mon_fichier.txt' n'est pas un dossier."
        ),
    },

    # ──────────────────────────────────────────────────────────
    # OSError : erreur système générique liée aux fichiers
    # Couvre les cas non capturés par les erreurs plus spécifiques ci-dessus
    # ──────────────────────────────────────────────────────────
    {
        "id":          "file.os_error",
        "pattern":     r"OSError: \[Errno (\d+)\] (.+): '(.+)'",
        "description": "Erreur système (code {errno}) sur '{filename}' : {message}.",
        "solution":    (
            "1. Lis le message d'erreur : le code Errno indique la cause exacte.\n"
            "2. Codes fréquents : 28 = disque plein, 36 = nom de fichier trop long, "
            "16 = fichier verrouillé par un autre processus.\n"
            "3. Utilise errno.errorcode[{errno}] dans Python pour obtenir le nom symbolique de l'erreur."
        ),
        "conseil":     (
            "OSError est la classe parente de FileNotFoundError, PermissionError, etc. "
            "Si Clarify affiche ce message, c'est que l'erreur est rare ou spécifique au système. "
            "Le code Errno est la clé : cherche 'Python OSError Errno {errno}' pour le contexte exact."
        ),
    },

]
