"""
Detector : détecte la langue de l'utilisateur pour afficher les messages
de Clarify dans sa langue.

Ordre de priorité :
  1. Variable d'environnement CLARIFY_LANG (ex. export CLARIFY_LANG=fr)
  2. Langue du système d'exploitation (locale)
  3. Langue par défaut : anglais (en)
"""

import locale
import os

SUPPORTED_LANGUAGES = ["fr", "en", "zh", "ar", "pt", "es"]
DEFAULT_LANGUAGE    = "en"

# Langue dans laquelle les patterns Clarify sont écrits.
# Le translator s'en sert comme source pour toutes les traductions.
# Changer cette valeur suffit si les patterns sont réécrits dans une autre langue.
SOURCE_LANGUAGE = "fr"


def get_language() -> str:
    """Retourne le code langue à utiliser (ex. 'fr', 'en', 'ar')."""

    # 1. Variable d'environnement — priorité maximale, permet de forcer la langue
    env_lang = os.environ.get("CLARIFY_LANG", "").strip().lower()
    if env_lang in SUPPORTED_LANGUAGES:
        return env_lang

    # 2. Langue du système d'exploitation
    try:
        system_locale = locale.getdefaultlocale()[0]  # ex. 'fr_FR', 'en_US', 'zh_CN'
        if system_locale:
            code = system_locale[:2].lower()           # garde uniquement 'fr', 'en', 'zh'…
            if code in SUPPORTED_LANGUAGES:
                return code
    except Exception:
        pass

    # 3. Aucune langue détectée → langue par défaut
    return DEFAULT_LANGUAGE
