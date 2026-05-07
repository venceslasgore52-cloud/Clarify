"""
Simulation réelle de Clarify.
Chaque bloc lève une vraie exception Python — Clarify l'intercepte,
la décode et l'affiche comme elle le ferait en production.

Lance : python -X utf8 test_clarify.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.locale.detector  import get_language
from src.engine.core      import get_error_info
from src.engine.decoder   import decode
from src.engine.terminal  import render, log
from src.database.queries import save_error

CYAN  = "\033[36m"
BOLD  = "\033[1m"
DIM   = "\033[2m"
RESET = "\033[0m"

langue = get_language()


def clarify(fn):
    """Exécute fn(), intercepte l'exception et affiche le résultat Clarify."""
    try:
        fn()
    except Exception:
        exc_type, exc_value, exc_tb = sys.exc_info()
        error_info = get_error_info(exc_type, exc_value, exc_tb)
        decoded    = decode(error_info, langue)
        render(decoded)
        save_error(decoded, langue)


def separateur(titre):
    print(f"\n{DIM}{'─' * 50}{RESET}")
    print(f"{BOLD}{CYAN}  {titre}{RESET}")
    print(f"{DIM}{'─' * 50}{RESET}")


# ─────────────────────────────────────────────────
#  1. NameError
# ─────────────────────────────────────────────────
separateur("1. NameError — variable non definie")
def sim_name_error():
    print(resultat_inexistant)  # noqa

clarify(sim_name_error)


# ─────────────────────────────────────────────────
#  2. IndexError
# ─────────────────────────────────────────────────
separateur("2. IndexError — index hors limites")
def sim_index_error():
    liste = [1, 2, 3]
    return liste[10]

clarify(sim_index_error)


# ─────────────────────────────────────────────────
#  3. KeyError
# ─────────────────────────────────────────────────
separateur("3. KeyError — cle absente")
def sim_key_error():
    utilisateur = {"nom": "Venceslas"}
    return utilisateur["email"]

clarify(sim_key_error)


# ─────────────────────────────────────────────────
#  4. ZeroDivisionError
# ─────────────────────────────────────────────────
separateur("4. ZeroDivisionError — division par zero")
def sim_zero_division():
    total  = 100
    compte = 0
    return total / compte

clarify(sim_zero_division)


# ─────────────────────────────────────────────────
#  5. FileNotFoundError
# ─────────────────────────────────────────────────
separateur("5. FileNotFoundError — fichier introuvable")
def sim_file_not_found():
    with open("rapport_inexistant.csv", "r") as f:
        return f.read()

clarify(sim_file_not_found)


# ─────────────────────────────────────────────────
#  6. TypeError
# ─────────────────────────────────────────────────
separateur("6. TypeError — types incompatibles")
def sim_type_error():
    age = "25"
    return age + 5

clarify(sim_type_error)


# ─────────────────────────────────────────────────
#  7. AttributeError
# ─────────────────────────────────────────────────
separateur("7. AttributeError — attribut inexistant")
def sim_attribute_error():
    nombre = 42
    return nombre.upper()

clarify(sim_attribute_error)


# ─────────────────────────────────────────────────
#  8. RecursionError
# ─────────────────────────────────────────────────
separateur("8. RecursionError — recursion infinie")
def sim_recursion():
    def infinie(n):
        return infinie(n + 1)
    infinie(0)

clarify(sim_recursion)


# ─────────────────────────────────────────────────
#  9. ModuleNotFoundError
# ─────────────────────────────────────────────────
separateur("9. ModuleNotFoundError — module manquant")
def sim_import_error():
    import module_qui_nexiste_pas  # noqa

clarify(sim_import_error)


# ─────────────────────────────────────────────────
# 10. PermissionError
# ─────────────────────────────────────────────────
separateur("10. PermissionError — acces refuse")
def sim_permission_error():
    raise PermissionError("[Errno 13] Permission denied: 'C:/Windows/system32/hosts'")

clarify(sim_permission_error)


print(f"\n{DIM}{'─' * 50}{RESET}")
log("Simulation terminee — 10 erreurs traitees par Clarify.", "success")
print()
