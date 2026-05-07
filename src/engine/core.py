"""
Core : capture les erreurs du programme et les enregistre en base de données.
Utilisé dans tous les modules de Clarify pour une gestion centralisée des erreurs.
"""

import sys
import traceback
import datetime
from src.engine.decoder    import decode
from src.engine.terminal   import render
from src.reporter.logger   import log_error
from src.locale.detector   import get_language


def get_error_info(exception_type, exception_value, exception_traceback):
    """Extrait les informations utiles d'une exception pour les enregistrer et les afficher."""

    # traceback.extract_tb() transforme la pile d'appels (suite de fonctions appelées
    # avant l'erreur) en une liste d'objets FrameSummary qu'on peut lire facilement.
    traceback_info = traceback.extract_tb(exception_traceback)

    # La dernière frame est l'endroit exact où l'erreur s'est produite.
    # Si la liste est vide (ex. erreur levée directement en C), on sécurise avec None.
    last_frame = traceback_info[-1] if traceback_info else None

    get_file  = last_frame.filename if last_frame else "inconnu"
    get_ligne = last_frame.lineno   if last_frame else "?"
    get_time  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        # __name__ donne le nom textuel de la classe (ex. "ValueError" au lieu de <class 'ValueError'>)
        "type":    str(exception_type.__name__),
        "message": str(exception_value),
        "file":    get_file,
        "line":    get_ligne,
        "time":    get_time,
    }


def handle_exception(exception_type, exception_value, exception_traceback):
    """Pipeline complet : extraction → décodage → affichage → sauvegarde."""
    # Étape 1 : extraire les métadonnées brutes de l'exception
    error_info = get_error_info(exception_type, exception_value, exception_traceback)

    # Étape 2 : décoder et enrichir l'erreur selon la langue de l'utilisateur
    langue = get_language()
    decoded = decode(error_info, langue)

    # Étape 3 : afficher le résultat dans le terminal
    render(decoded)

    # Étape 4 : persister en DB + fichier log via le reporter
    log_error(decoded, langue)


def activate():
    """Installe le gestionnaire global d'exceptions de Clarify.

    sys.excepthook est la fonction que Python appelle automatiquement
    quand une exception non capturée fait planter le programme.
    En la remplaçant par handle_exception, Clarify intercepte toutes
    les erreurs avant qu'elles s'affichent en brut dans le terminal.
    """
    sys.excepthook = handle_exception
