# ⬡ Clarify

> Extension VS Code qui intercepte les erreurs Python, les décode et les explique en langage naturel — avec support Django, multilingue et tableau de bord en temps réel.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![VS Code](https://img.shields.io/badge/VS%20Code-1.80%2B-blue)
![License](https://img.shields.io/badge/licence-MIT-green)
![Version](https://img.shields.io/badge/version-1.0.5-orange)

---

## ✨ Ce que fait Clarify

Au lieu de ce message brut :

```
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

Clarify affiche :

```
┌ Clarify — Erreur détectée ──────────────────────────────────────────────┐
│ Type        │ TypeError                                                  │
│ Message     │ unsupported operand type(s) for +: 'int' and 'str'        │
│ Fichier     │ app.py  │  Ligne  │ 12                                     │
├─────────────┼──────────────────────────────────────────────────────────-┤
│ Explication │ L'opération '+' ne peut pas s'appliquer entre int et str.  │
│ Solution    │ Convertis : int(valeur) ou str(valeur) selon ton besoin.   │
│ Conseil     │ Python ne mélange pas les types. 5 + '3' → erreur,        │
│             │ mais 5 + int('3') → 8.                                     │
└─────────────┴────────────────────────────────────────────────────────────┘
```

---

## 🚀 Démarrage rapide

### 1. Prérequis

- Python 3.10+
- Node.js 18+
- VS Code 1.80+

### 2. Installation

```bash
git clone https://github.com/venceslasgore52-cloud/Clarify.git
cd Clarify
npm install
pip install deep-translator terminaltables
```

### 3. Lancer l'extension VS Code

```
F5  →  ouvre l'Extension Development Host
```

### 4. Utiliser Clarify dans un script Python

```python
from src.engine.core import activate
activate()   # une seule ligne — Clarify intercepte toutes les erreurs

# ton code ici...
```

### 5. Forcer la langue

```bash
# PowerShell
$env:CLARIFY_LANG="fr"   # fr | en | zh | ar | pt | es

# Linux / Mac
export CLARIFY_LANG=fr
```

---

## 🧪 Simulation de test

```bash
python -X utf8 test_clarify.py
```

Lance 10 erreurs Python réelles et affiche le tableau Clarify pour chacune.

---

## 🗂️ Architecture

```
clarify/
├── extension.js                         # Extension VS Code (point d'entrée)
├── package.json                         # Manifeste & configuration
│
├── src/
│   ├── engine/
│   │   ├── core.py                      # Pipeline principal (sys.excepthook)
│   │   ├── decoder.py                   # Correspondance regex → pattern
│   │   ├── translator.py                # Traduction via deep-translator
│   │   └── terminal.py                  # Affichage tableau coloré
│   │
│   ├── patterns/python/
│   │   ├── builtin/                     # Erreurs Python standard
│   │   │   ├── variables.py             # NameError, UnboundLocalError, AttributeError
│   │   │   ├── types.py                 # TypeError
│   │   │   ├── collections.py           # IndexError, KeyError
│   │   │   ├── syntax.py                # SyntaxError, IndentationError, TabError
│   │   │   ├── imports.py               # ImportError, ModuleNotFoundError
│   │   │   ├── files.py                 # FileNotFoundError, PermissionError…
│   │   │   ├── runtime.py               # ZeroDivisionError, RecursionError…
│   │   │   └── system.py                # SystemExit, KeyboardInterrupt…
│   │   │
│   │   └── django/                      # Erreurs Django / DRF
│   │       ├── orm.py                   # DoesNotExist, IntegrityError…
│   │       ├── views.py                 # Http404, PermissionDenied…
│   │       ├── urls.py                  # NoReverseMatch, Resolver404…
│   │       ├── templates.py             # TemplateDoesNotExist…
│   │       ├── config.py                # ImproperlyConfigured, DisallowedHost…
│   │       ├── serializers.py           # ValidationError DRF…
│   │       ├── middleware.py            # CSRF, SessionMiddleware…
│   │       ├── celery.py                # Broker, NotRegistered…
│   │       └── redis.py                 # ConnectionError, TimeoutError…
│   │
│   ├── locale/
│   │   └── detector.py                  # Détection langue (env → OS → défaut)
│   │
│   ├── database/
│   │   ├── db.py                        # SQLite (intégré Python, zéro config)
│   │   ├── models.py                    # ErrorRecord dataclass
│   │   └── queries.py                   # CRUD + statistiques
│   │
│   └── reporter/
│       ├── logger.py                    # DB + fichier .log horodaté
│       ├── dashboard.py                 # Génère le HTML du webview
│       └── visualizer.py               # Schéma ASCII du flux d'erreur
│
└── webview/
    ├── dashboard.html                   # Interface tableau de bord
    ├── dashboard.css                    # Thème sombre (Catppuccin)
    └── dashboard.js                     # Logique + pont VS Code API
```

---

## ⚙️ Fonctionnement

```
Exception Python
      │
      ▼  sys.excepthook
 core.handle_exception()
      │
      ├─► get_error_info()      extrait : type, message, fichier, ligne
      │
      ├─► decoder.decode()      cherche la regex correspondante dans les patterns
      │         │
      │         └─► translator.translate()   traduit si langue ≠ français
      │
      ├─► terminal.render()     affiche le tableau coloré
      │
      └─► reporter.logger.log_error()
                │
                ├─► SQLite (clarify.db)
                ├─► clarify.log
                └─► dashboard webview
```

---

## 🌍 Langues supportées

| Code | Langue    |
|------|-----------|
| `fr` | Français  |
| `en` | English   |
| `zh` | 中文       |
| `ar` | العربية    |
| `pt` | Português |
| `es` | Español   |

La langue source des patterns est le **français** (`SOURCE_LANGUAGE = "fr"` dans `detector.py`).
Changer cette constante suffit si les patterns sont réécrits dans une autre langue.

---

## 🗺️ Roadmap

| Version | Contenu                 | Statut      |
|---------|-------------------------|-------------|
| V1.0.5  | Python builtin + Django | 🔄 En cours |
| V1.1.0  | Flask + FastAPI         | 🔒 Prévu    |
| V1.2.0  | JavaScript + React      | 🔒 Prévu    |
| V2.0.0  | Flutter + Dart          | 🔒 Prévu    |
| V3.0.0  | Multi-langages complet  | 🔒 Prévu    |

---

## 🤝 Contribuer

- Ajouter des patterns dans `src/patterns/python/`
- Traduire les patterns dans une nouvelle langue
- Signaler une erreur non couverte en ouvrant une issue

---

## 📄 Licence

MIT License — Libre et gratuit pour toujours.

---

## 👨🏾‍💻 Auteur

**Venceslas Malepoh** — DIGIX Technology
Abidjan, Côte d'Ivoire 🇨🇮

[GitHub](https://github.com/venceslasgore52-cloud/Clarify)
