# Clarify

Extension VS Code qui décode et traduit les patterns de code Python — dont Django — en explications claires et lisibles, avec un tableau de bord en temps réel pour l'analyse et le reporting.

## Architecture

```
clarify/
├── extension.js                    # Point d'entrée de l'extension VS Code
├── package.json                    # Manifeste & dépendances
│
├── src/
│   ├── engine/                     # Moteur d'analyse principal
│   │   ├── core.py                 # Orchestre le pipeline d'analyse
│   │   ├── decoder.py              # Lecture et parsing des fichiers source
│   │   ├── translator.py           # Conversion des patterns en explications
│   │   └── terminal.py             # Sortie terminal & commandes
│   │
│   ├── patterns/python/
│   │   ├── builtin/                # Patterns Python standard
│   │   │   ├── syntax.py
│   │   │   ├── variables.py
│   │   │   ├── types.py
│   │   │   ├── collections.py
│   │   │   ├── imports.py
│   │   │   ├── files.py
│   │   │   ├── runtime.py
│   │   │   └── system.py
│   │   └── django/                 # Patterns spécifiques à Django
│   │       ├── orm.py
│   │       ├── views.py
│   │       ├── urls.py
│   │       ├── templates.py
│   │       └── config.py
│   │
│   ├── locale/
│   │   └── detector.py             # Détecte la langue de l'utilisateur
│   │
│   ├── database/
│   │   ├── db.py                   # Connexion à la base de données
│   │   ├── models.py               # Modèles de données
│   │   └── queries.py              # Helpers de requêtes
│   │
│   └── reporter/
│       ├── logger.py               # Journalisation des événements et erreurs
│       ├── dashboard.py            # Fournisseur de données du tableau de bord
│       └── visualizer.py          # Génération de graphiques
│
└── webview/
    ├── dashboard.html              # Interface du tableau de bord
    ├── dashboard.css               # Styles
    └── dashboard.js                # Logique webview & pont avec l'API VS Code
```

## Fonctionnement

1. **Décodage** — `decoder.py` analyse un fichier Python et en extrait les constructions significatives.
2. **Correspondance** — `core.py` associe ces constructions aux bibliothèques de patterns (`builtin/`, `django/`).
3. **Traduction** — `translator.py` génère des explications en langage naturel, selon la langue détectée.
4. **Rapport** — les résultats sont journalisés, stockés et affichés dans le tableau de bord webview de VS Code.

## Démarrage

```bash
npm install
```

Appuyez sur `F5` dans VS Code pour lancer l'hôte de développement d'extension.

## Prérequis

- VS Code 1.80+
- Python 3.10+
- Node.js 18+

---

## 🌍 Langues supportées

| Code | Langue     |
|------|------------|
| fr   | Français   |
| en   | English    |
| zh   | 中文        |
| ar   | العربية     |
| pt   | Português  |
| es   | Español    |

---

## 🗺️ Roadmap

| Version | Contenu                    | Statut |
|---------|----------------------------|--------|
| V1.0.5  | Python builtin + Django    | 🔄 En cours |
| V1.1.0  | Flask + FastAPI            | 🔒 Prévu |
| V1.2.0  | JavaScript + React         | 🔒 Prévu |
| V2.0.0  | Flutter + Dart             | 🔒 Prévu |
| V3.0.0  | Multi-langages complet     | 🔒 Prévu |

---

## 🤝 Contribuer

Tu peux contribuer en :
- Ajoutant des patterns d'erreurs
- Traduisant dans ta langue
- Signalant des erreurs manquantes

---

## 📄 Licence

MIT License — Libre et gratuit

---

## 👨🏾‍💻 Auteur

Venceslas — DIGIX Technology
Abidjan, Côte d'Ivoire 🇨🇮
