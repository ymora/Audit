# Systeme d'Audit Universel

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-orange.svg)](CHANGELOG.md)

Un systeme d'audit automatique et intelligent pour differents types de projets. Interface graphique moderne avec theme sombre et rapports detailles.

## Installation Rapide

```bash
# Cloner le projet
git clone https://github.com/votre-username/audit-universel.git
cd audit-universel

# Installer les dependances
pip install -r requirements.txt

# Lancer le systeme
python audit.py
```

## Utilisation

### Interface Graphique (Recommandé)
```bash
python audit.py          # Lance l'interface graphique moderne
python audit.py --gui    # Même chose, explicite
```

### Ligne de Commande
```bash
python audit.py --cli ./mon_projet    # Audit du projet ./mon_projet
python audit.py --cli /chemin/vers/projet
```

### Aide
```bash
python audit.py --help   # Affiche l'aide complete
```

## Fonctionnalites

- Interface moderne : Theme sombre inspire de Cursor
- Analyse automatique : Doublons, code mort, securite
- Rapports detailles : HTML, Markdown, JSON (comme docusense)
- Support universel : Python, Node.js, Java, PHP, Go, Rust
- Configuration flexible : Par projet et par type

## Structure

```
audit-universel/
├── audit.py              # Point d'entree unifie
├── core/                 # Fichiers principaux
├── tools/                # Outils d'analyse
├── scripts/              # Scripts utilitaires
├── tests/                # Tests automatises
├── docs/                 # Documentation complete
├── rules/                # Regles d'audit
└── projects/             # Projets audites
```

## Documentation

- [Documentation complete](docs/README_PROJET.md) - Guide detaille
- [Resume du projet](docs/RESUME_FINAL.md) - Vue d'ensemble
- [Changelog](CHANGELOG.md) - Historique des versions

## Securite

- Verification automatique des vulnerabilites
- Analyse des dependances
- Rapports de securite detailles

## Contribution

1. Fork le projet
2. Creer une branche feature
3. Commiter les changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## Licence

MIT License - Voir [LICENSE](LICENSE) pour plus de details.

---

**Developpe avec amour pour la communaute open source**
