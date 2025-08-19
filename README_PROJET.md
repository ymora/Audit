# 🔍 Système d'Audit Universel

## 📋 Description

Le **Système d'Audit Universel** est une solution complète et modulaire pour auditer automatiquement différents types de projets. Il offre une interface graphique intuitive et un système de tests personnalisables pour chaque type de projet.

## ✨ Fonctionnalités Principales

### 🎯 **Audit Automatisé**
- **Détection automatique** du type de projet
- **Tests spécifiques** selon le type de projet
- **Rapports détaillés** en HTML et JSON
- **Historique complet** des audits

### 🖥️ **Interface Graphique**
- **Sélection facile** des projets via interface graphique
- **Lancement d'audit** en un clic
- **Ouverture automatique** des rapports HTML
- **Gestion des projets récents**
- **Logs en temps réel**

### 🏗️ **Architecture Modulaire**
- **Tests personnalisables** par type de projet
- **Configuration flexible** pour chaque projet
- **Système de plugins** extensible
- **Support multi-projets**

## 🚀 Installation

### Prérequis
- Python 3.8+
- tkinter (généralement inclus avec Python)

### Installation Rapide
```bash
# Cloner le projet
git clone <repository-url>
cd systeme-audit-universel

# Lancer l'interface graphique
python audit/launch_gui.py
```

### Installation via PowerShell (Windows)
```powershell
# Lancer l'interface graphique
.\audit\start_gui.ps1
```

## 📖 Utilisation

### Interface Graphique (Recommandé)

1. **Lancer l'interface** : `python audit/launch_gui.py`
2. **Sélectionner un projet** : Cliquer sur "📂 Parcourir"
3. **Lancer l'audit** : Cliquer sur "🔍 Lancer l'Audit"
4. **Consulter le rapport** : Cliquer sur "📄 Ouvrir Rapport"

### Ligne de Commande

```bash
# Audit d'un projet spécifique
python audit/universal_auditor.py /chemin/vers/projet

# Initialiser l'audit dans un projet
python audit/init_audit.py /chemin/vers/projet

# Migrer les anciens rapports
python audit/migrate_old_reports.py /chemin/vers/projet
```

## 🏗️ Structure du Projet

```
audit/
├── universal_auditor.py          # Script principal d'audit
├── audit_gui.py                  # Interface graphique
├── launch_gui.py                 # Lanceur de l'interface
├── init_audit.py                 # Initialisation d'un projet
├── migrate_old_reports.py        # Migration des anciens rapports
├── cleanup_old_audit.py          # Nettoyage de l'ancien système
├── start_gui.ps1                 # Lanceur PowerShell
├── README.md                     # Documentation principale
├── README_PROJET.md              # Ce fichier
├── gui_config.json               # Configuration de l'interface
├── projects/                     # Configurations par type de projet
│   ├── docusense_ai/
│   │   ├── config.json
│   │   └── tests/
│   │       ├── test_ai_providers.py
│   │       ├── test_backend_api.py
│   │       └── test_frontend_components.py
│   └── [autres_types]/
└── tools/                        # Outils utilitaires
    └── generic_auditor.py
```

## 🔧 Configuration

### Types de Projets Supportés

- **docusense_ai** : Applications d'IA et de traitement de documents
- **web_app** : Applications web (React, Vue, etc.)
- **python_app** : Applications Python
- **mobile_app** : Applications mobiles
- **generic** : Projets génériques

### Ajouter un Nouveau Type de Projet

1. **Créer le dossier** : `audit/projects/nouveau_type/`
2. **Configuration** : `config.json`
3. **Tests spécifiques** : `tests/test_*.py`
4. **Documentation** : Ajouter dans le README

## 📊 Rapports et Logs

### Structure des Rapports
```
.audit/
├── reports/
│   ├── latest_report.html        # Dernier rapport HTML
│   ├── latest_report.json        # Dernier rapport JSON
│   └── audit_report_YYYYMMDD_HHMMSS.*
├── logs/
│   └── audit_YYYYMMDD_HHMMSS.log
├── config/
│   └── project_config.json
└── tests/
    └── [tests_specifiques]
```

### Types de Rapports
- **HTML** : Rapport visuel avec graphiques et statistiques
- **JSON** : Données structurées pour traitement automatisé
- **Markdown** : Documentation technique

## 🛠️ Développement

### Ajouter de Nouveaux Tests

```python
# Exemple de test personnalisé
def test_custom_feature(project_path):
    """Test d'une fonctionnalité personnalisée."""
    try:
        # Logique de test
        return {
            "name": "Test Fonctionnalité Personnalisée",
            "status": "success",
            "details": "Fonctionnalité opérationnelle"
        }
    except Exception as e:
        return {
            "name": "Test Fonctionnalité Personnalisée",
            "status": "error",
            "details": str(e)
        }
```

### Extensions et Plugins

Le système supporte les extensions via :
- **Tests personnalisés** dans `tests/`
- **Configurations spécifiques** dans `config.json`
- **Scripts d'initialisation** personnalisés

## 📈 Roadmap

### Version 1.1
- [ ] Support pour plus de types de projets
- [ ] Tests de performance
- [ ] Intégration CI/CD
- [ ] API REST pour l'audit

### Version 1.2
- [ ] Interface web
- [ ] Tableau de bord en temps réel
- [ ] Notifications par email
- [ ] Export vers différents formats

### Version 2.0
- [ ] Intelligence artificielle pour l'analyse
- [ ] Suggestions d'amélioration automatiques
- [ ] Intégration avec des outils externes
- [ ] Support multi-utilisateurs

## 🤝 Contribution

### Comment Contribuer

1. **Fork** le projet
2. **Créer** une branche pour votre fonctionnalité
3. **Développer** et tester votre code
4. **Soumettre** une pull request

### Standards de Code

- **Python** : PEP 8
- **Documentation** : Docstrings en français
- **Tests** : Couverture minimale de 80%
- **Commits** : Messages en français

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

### Documentation
- **README principal** : `audit/README.md`
- **Documentation utilisateur** : `docs/`
- **Exemples** : `examples/`

### Contact
- **Issues** : GitHub Issues
- **Discussions** : GitHub Discussions
- **Email** : [votre-email]

## 🙏 Remerciements

- **tkinter** : Interface graphique
- **pathlib** : Gestion des chemins
- **subprocess** : Exécution de commandes
- **json** : Sérialisation des données

---

**🔍 Système d'Audit Universel** - Fait pour simplifier l'audit de vos projets !
