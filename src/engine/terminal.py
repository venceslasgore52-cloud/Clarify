"""
Terminal : affiche les erreurs décodées dans le terminal VS Code
sous forme de tableau coloré, et fournit une fonction de log par niveau.
"""

from terminaltables import SingleTable

# Codes ANSI : séquences spéciales reconnues par les terminaux pour
# changer la couleur ou le style du texte. \033[ est le caractère
# d'échappement, suivi d'un code numérique et terminé par "m".
# Exemple : "\033[31m" active le rouge, "\033[0m" remet tout à zéro.
RESET  = "\033[0m"   # annule tout style actif
BOLD   = "\033[1m"   # texte en gras
CYAN   = "\033[36m"  # couleur info
GREEN  = "\033[32m"  # couleur succès
YELLOW = "\033[33m"  # couleur avertissement
RED    = "\033[31m"  # couleur erreur
DIM    = "\033[2m"   # texte atténué

# Table de correspondance niveau → couleur utilisée par log()
LEVEL_COLORS = {
    "info":    CYAN,
    "warning": YELLOW,
    "error":   RED,
    "success": GREEN,
}


def render(decoded: dict) -> None:
    """Affiche une erreur décodée dans le terminal sous forme de tableau."""
    # Chaque ligne du tableau est une paire [étiquette, valeur].
    # .get("clé", "?") retourne "?" si le champ est absent du dictionnaire.
    table_data = [
        ["Champ", "Valeur"],
        ["Type",    decoded.get("type",    "?")],
        ["Message", decoded.get("message", "?")],
        ["Fichier", decoded.get("file",    "?")],
        ["Ligne",   str(decoded.get("line", "?"))],
        ["Heure",   decoded.get("time",    "?")],
    ]

    # Séparateur visuel avant les champs d'aide
    if decoded.get("explanation") or decoded.get("solution") or decoded.get("conseil"):
        table_data.append(["", ""])

    if decoded.get("explanation"):
        table_data.append([f"{BOLD}Explication{RESET}", decoded["explanation"]])

    if decoded.get("solution"):
        table_data.append([f"{GREEN}Solution{RESET}",    decoded["solution"]])

    if decoded.get("conseil"):
        table_data.append([f"{CYAN}Conseil{RESET}",      decoded["conseil"]])

    table = SingleTable(table_data, f" {RED}Clarify — Erreur detectee{RESET} ")
    # Limite la largeur max pour éviter les tableaux trop larges
    table.inner_row_border = True
    print(f"\n{table.table}\n")


def log(message: str, level: str = "info") -> None:
    """Affiche un message de log coloré selon son niveau (info / warning / error / success)."""
    # Si le niveau est inconnu, RESET est utilisé : le texte s'affiche sans couleur
    color = LEVEL_COLORS.get(level, RESET)
    print(f"{color}{BOLD}[{level.upper()}]{RESET} {message}")
