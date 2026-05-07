"""
Translator : traduit les messages d'erreur vers la langue de l'utilisateur
en utilisant deep-translator (compatible Python 3.13+).
"""

import sys
from deep_translator import GoogleTranslator
from src.locale.detector import get_language, SOURCE_LANGUAGE

# Correspondance code Clarify → code attendu par deep-translator
LANG_MAP = {
    "fr": "french",
    "en": "english",
    "zh": "chinese (simplified)",
    "ar": "arabic",
    "pt": "portuguese",
    "es": "spanish",
}

# Langue source des patterns (définie dans detector.py)
_SOURCE = LANG_MAP.get(SOURCE_LANGUAGE, "french")


def translate(text: str, target_lang: str = None) -> str:
    """Traduit un texte brut vers la langue cible (ou celle détectée si non précisée)."""
    langue = target_lang or get_language()

    # deep-translator n'a pas besoin de traduction si la source est déjà la cible
    dest = LANG_MAP.get(langue, "english")

    try:
        # Une nouvelle instance par appel — léger et thread-safe
        return GoogleTranslator(source=_SOURCE, target=dest).translate(text)
    except Exception as e:
        # En cas d'échec (réseau, quota), on retourne le texte français original
        print(f"[Clarify][translator] Echec de traduction ({langue}) : {e}", file=sys.stderr)
        return text


def translate_error(error_info: dict, target_lang: str = None) -> dict:
    """Traduit uniquement le champ 'message' d'un dictionnaire d'erreur.

    Le champ 'type' (ex. ValueError, KeyError) n'est pas traduit :
    ce sont des noms de classes Python standardisés.
    """
    langue = target_lang or get_language()
    translated = error_info.copy()
    translated["message"] = translate(error_info.get("message", ""), langue)
    return translated
