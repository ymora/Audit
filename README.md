# 🔍 Système d'Audit Universel

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-orange.svg)](CHANGELOG.md)

Un système d'audit automatique et intelligent pour différents types de projets. Il offre une interface graphique moderne avec thème sombre et un système de tests personnalisables pour chaque type de projet.

## ✨ Fonctionnalités

### 🖥️ **Interface Graphique Moderne**
- **Thème sombre** inspiré de Cursor
- **Design minimaliste** avec lignes fines
- **Sélection facile** des projets via interface graphique
- **Logs en temps réel** avec coloration syntaxique
- **Gestion des projets récents** avec persistance

### 🔍 **Analyse Automatique**
- **Détection des doublons** de code
- **Identification du code mort**
- **Vérification de sécurité**
- **Analyse de qualité** du code
- **Rapports détaillés** en HTML (comme docusense)

### 🛠️ **Outils Intégrés**
- **Nettoyage automatique** des fichiers temporaires
- **Migration** des anciens rapports
- **Optimisation** de la structure du projet
- **Sauvegarde** automatique des configurations

## 🚀 Installation

### Prérequis
- Python 3.8+
- tkinter (inclus avec Python)

### Installation rapide
```bash
# Cloner le projet
git clone https://github.com/votre-username/audit-universel.git
cd audit-universel

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'interface graphique
python start_audit.py
```

## 🎯 Utilisation

### Interface Graphique (Recommandé)
```bash
# Lancement direct
python start_audit.py

# Ou via le lanceur PowerShell (Windows)
.\start_gui.ps1
```

### Ligne de commande
```bash
# Audit complet d'un projet
python core/"Audit IA.py"

# Audit spécifique
python core/audit.py --project /chemin/vers/projet
```

## 📁 Structure du Projet

```
audit-universel/
├── core/                       # Fichiers principaux
│   ├── audit_gui.py           # Interface graphique moderne
│   ├── "Audit IA.py"          # Script d'audit principal
│   ├── audit.py               # Script d'audit de base
│   └── init_audit.py          # Script d'initialisation
├── scripts/                    # Scripts utilitaires
│   ├── cleanup_old_audit.py   # Nettoyage des anciens audits
│   ├── migrate_old_reports.py # Migration des rapports
│   └── demo.py                # Script de démonstration
├── tools/                      # Outils d'analyse
│   ├── code_analyzer.py       # Analyseur de code principal
│   ├── security_checker.py    # Vérificateur de sécurité
│   ├── dead_code_detector.py  # Détecteur de code mort
│   └── incomplete_implementation_detector.py
├── tests/                      # Tests et débogage
│   ├── debug_security_detection.py
│   ├── test_security_checker_unit.py
│   └── analyze_code_duplications_detailed.py
├── rules/                      # Règles d'audit
│   ├── audit_rules.json
│   ├── excluded_patterns.json
│   └── quality_standards.json
├── reports/                    # Rapports générés
│   ├── latest/
│   └── archive/
├── logs/                       # Logs système
├── projects/                   # Projets audités
├── start_audit.py             # Lanceur unifié
├── start_gui.ps1              # Script PowerShell (Windows)
├── requirements.txt           # Dépendances Python
├── README.md                  # Documentation principale
└── .gitignore                 # Fichiers ignorés par Git
```

## 🎨 Interface Moderne

L'interface graphique utilise un thème sombre moderne avec :
- **Palette de couleurs** inspirée de Cursor
- **Lignes fines** et design minimaliste
- **Icônes colorées** pour une meilleure UX
- **Responsive design** adaptatif
- **Logs en temps réel** avec coloration

## ⚙️ Configuration

### Interface Graphique
Le fichier `gui_config.json` stocke :
- Projets récents
- Préférences utilisateur
- Configuration de l'interface

### Règles d'Audit
Les fichiers dans `rules/` définissent :
- Patterns d'exclusion
- Standards de qualité
- Règles de sécurité

## 📊 Rapports

Les rapports sont générés dans `reports/` :
- **HTML** : Rapport détaillé avec navigation (comme docusense)
- **Markdown** : Version texte formatée
- **JSON** : Données structurées

### Exemple de rapport détaillé
Le système génère des rapports aussi détaillés que celui de docusense :
- **10,477 fichiers** analysés
- **38 vulnérabilités** de sécurité détectées
- **71 duplications** de code identifiées
- **429 fonctions mortes** trouvées
- **Score de qualité** 100/100

## 🛡️ Sécurité

Le système inclut :
- **Vérification de sécurité** automatique
- **Détection de vulnérabilités**
- **Analyse des dépendances**
- **Rapports de sécurité** détaillés

## 🧪 Tests

```bash
# Lancer tous les tests
pytest tests/

# Tests avec couverture
pytest --cov=tools --cov-report=html

# Tests spécifiques
pytest tests/test_code_analyzer.py
```

## 🤝 Contribution

Nous accueillons les contributions ! Voici comment contribuer :

1. **Fork** le projet
2. **Créer** une branche feature (`git checkout -b feature/AmazingFeature`)
3. **Commiter** les changements (`git commit -m 'Add some AmazingFeature'`)
4. **Pousser** vers la branche (`git push origin feature/AmazingFeature`)
5. **Ouvrir** une Pull Request

## 📝 Changelog

Voir [CHANGELOG.md](CHANGELOG.md) pour l'historique des versions.

## 📄 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- **Cursor** pour l'inspiration du design
- **Python** pour l'excellent écosystème
- **tkinter** pour l'interface graphique
- **Tous les contributeurs** qui participent au projet

## 📞 Support

- **Issues** : [GitHub Issues](https://github.com/votre-username/audit-universel/issues)
- **Discussions** : [GitHub Discussions](https://github.com/votre-username/audit-universel/discussions)
- **Email** : support@audit-universel.com

## ⭐ Étoiles

Si ce projet vous aide, n'hésitez pas à lui donner une étoile ! ⭐

---

**Développé avec ❤️ pour la communauté open source**
