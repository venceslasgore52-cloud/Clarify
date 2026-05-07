"""
Decoder : reçoit les informations brutes d'une erreur Python,
les fait correspondre aux patterns de la bibliothèque Clarify,
et retourne un dictionnaire enrichi avec description, solution et conseil.
"""

import re
import importlib

# Liste des modules de patterns à charger (ordre = priorité de correspondance)
PATTERN_MODULES = [
    "src.patterns.python.builtin.variables",
    "src.patterns.python.builtin.types",
    "src.patterns.python.builtin.collections",
    "src.patterns.python.builtin.syntax",
    "src.patterns.python.builtin.imports",
    "src.patterns.python.builtin.files",
    "src.patterns.python.builtin.runtime",
    "src.patterns.python.builtin.system",
    "src.patterns.python.django.orm",
    "src.patterns.python.django.views",
    "src.patterns.python.django.urls",
    "src.patterns.python.django.templates",
    "src.patterns.python.django.config",
    "src.patterns.python.django.serializers",
    "src.patterns.python.django.middleware",
    "src.patterns.python.django.celery",
    "src.patterns.python.django.redis",
]


def _load_all_patterns() -> list[dict]:
    """Charge et fusionne tous les patterns de tous les modules."""
    all_patterns = []
    for module_path in PATTERN_MODULES:
        try:
            module = importlib.import_module(module_path)
            all_patterns.extend(getattr(module, "PATTERNS", []))
        except ImportError:
            pass  # module absent → on ignore silencieusement
    return all_patterns


def _match(error_message: str, pattern: dict) -> dict | None:
    """
    Tente de faire correspondre le message d'erreur au pattern.
    Retourne les groupes capturés si correspondance, None sinon.
    """
    match = re.search(pattern["pattern"], error_message)
    if not match:
        return None
    return match.groups()


def _format(template: str, groups: tuple, error_info: dict) -> str:
    """
    Injecte les groupes capturés et les infos d'erreur dans un template de texte.
    Les noms de placeholders dépendent du pattern (ex. {var}, {module}, {key}…).
    On injecte les groupes dans l'ordre : groupe 1 → premier placeholder, etc.
    """
    placeholders = re.findall(r'\{(\w+)\}', template)

    context = dict(error_info)  # contient type, message, file, line, time

    # Associe chaque groupe capturé au premier placeholder encore sans valeur
    group_index = 0
    for name in dict.fromkeys(placeholders):  # ordre d'apparition, sans doublon
        if name not in context and group_index < len(groups):
            context[name] = groups[group_index]
            group_index += 1

    try:
        return template.format(**context)
    except KeyError:
        return template  # retourne le template brut si un placeholder manque


def _translate_fields(result: dict, langue: str) -> dict:
    """Traduit description, solution et conseil si la langue n'est pas le français."""
    from src.locale.detector import SOURCE_LANGUAGE
    if langue == SOURCE_LANGUAGE:
        return result

    # Import ici pour éviter un import circulaire au chargement du module
    from src.engine.translator import translate

    for field in ("description", "solution", "conseil", "explanation"):
        if result.get(field):
            result[field] = translate(result[field], langue)

    return result


def decode(error_info: dict, langue: str = "fr") -> dict:
    """
    Cherche le premier pattern qui correspond au message d'erreur,
    retourne error_info enrichi avec description, solution et conseil,
    puis traduit les champs dans la langue demandée si ce n'est pas le français.
    """
    raw_message = f"{error_info.get('type', '')}: {error_info.get('message', '')}"
    patterns    = _load_all_patterns()

    for pattern in patterns:
        groups = _match(raw_message, pattern)
        if groups is not None:
            result = {
                **error_info,
                "pattern_id":  pattern.get("id", ""),
                "description": _format(pattern.get("description", ""), groups, error_info),
                "solution":    _format(pattern.get("solution",    ""), groups, error_info),
                "conseil":     _format(pattern.get("conseil",     ""), groups, error_info),
                "explanation": _format(pattern.get("description", ""), groups, error_info),
            }
            return _translate_fields(result, langue)

    # Aucun pattern trouvé → retourne l'erreur brute sans enrichissement
    return {
        **error_info,
        "pattern_id":  None,
        "description": error_info.get("message", ""),
        "solution":    "",
        "conseil":     "",
        "explanation": error_info.get("message", ""),
    }
