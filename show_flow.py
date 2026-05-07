import sys
sys.path.insert(0, '.')
from src.reporter.visualizer import print_flow
from src.engine.core import get_error_info
from src.engine.decoder import decode

# Simule la vraie erreur de test.py
try:
    a = 5
    b = 5
    c = "5"         # str au lieu de int — provoque le TypeError
    result = a + b + c
except Exception:
    exc_type, exc_val, exc_tb = sys.exc_info()

    # Étape 1 — extraction
    error_info = get_error_info(exc_type, exc_val, exc_tb)
    print("\n── Étape 1 : error_info extrait ──────────────────")
    for k, v in error_info.items():
        print(f"  {k:12} : {v}")

    # Étape 2 — décodage
    decoded = decode(error_info, "en")
    print("\n── Étape 2 : pattern trouvé ──────────────────────")
    print(f"  pattern_id  : {decoded['pattern_id']}")
    print(f"  description : {decoded['description']}")

    # Étape 3 — schéma du flux
    print("\n── Étape 3 : flux complet Clarify ────────────────")
    decoded["langue"] = "en"
    print_flow(decoded)
