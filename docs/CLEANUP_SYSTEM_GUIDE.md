# GUIDE DU SYSTÈME DE NETTOYAGE AUTOMATIQUE

## Vue d'ensemble

Le système d'audit universel intègre un système de nettoyage automatique pour les dossiers `.project` qui suit les mêmes règles que les audits. Ce système garantit que les projets restent organisés et ne prennent pas trop d'espace disque.

## Fonctionnalités

### 🧹 Nettoyage automatique
- **Nettoyage après audit** : Exécuté automatiquement après chaque audit
- **Nettoyage global** : Peut être lancé manuellement pour tous les projets
- **Configuration flexible** : Chaque projet peut avoir ses propres règles de nettoyage

### 📁 Gestion intelligente des fichiers
- **Rétention configurable** : Durée de conservation des fichiers par type
- **Limite de fichiers** : Nombre maximum de fichiers par dossier
- **Archivage automatique** : Conservation des fichiers importants
- **Suppression sélective** : Suppression des fichiers les plus anciens

## Configuration

### Configuration par défaut

Chaque projet peut avoir sa propre configuration de nettoyage dans :
```
projet/.project/config/cleanup_config.json
```

Configuration par défaut :
```json
{
  "enabled": true,
  "retention_days": {
    "logs": 30,
    "reports": 90,
    "tests": 60
  },
  "max_files": {
    "logs": 100,
    "reports": 50,
    "tests": 30
  },
  "archive_enabled": true,
  "archive_path": "archive",
  "cleanup_schedule": "daily"
}
```

### Paramètres de configuration

| Paramètre | Description | Valeur par défaut |
|-----------|-------------|-------------------|
| `enabled` | Active/désactive le nettoyage | `true` |
| `retention_days.logs` | Jours de conservation des logs | `30` |
| `retention_days.reports` | Jours de conservation des rapports | `90` |
| `retention_days.tests` | Jours de conservation des tests | `60` |
| `max_files.logs` | Nombre max de fichiers de logs | `100` |
| `max_files.reports` | Nombre max de fichiers de rapports | `50` |
| `max_files.tests` | Nombre max de fichiers de tests | `30` |
| `archive_enabled` | Active l'archivage | `true` |
| `cleanup_schedule` | Fréquence de nettoyage | `"daily"` |

### Options de planning

- `"daily"` : Nettoyage quotidien
- `"weekly"` : Nettoyage hebdomadaire
- `"monthly"` : Nettoyage mensuel

## Utilisation

### Nettoyage automatique

Le nettoyage s'exécute automatiquement après chaque audit :
```bash
python audit.py --cli projects/mon_projet
```

### Nettoyage global manuel

Pour nettoyer tous les projets :
```bash
python audit.py --cleanup
```

### Nettoyage d'un projet spécifique

```python
from core.project_cleaner import ProjectCleaner
from pathlib import Path

project_path = Path("projects/mon_projet")
cleaner = ProjectCleaner(project_path)

# Vérifier si le nettoyage est nécessaire
if cleaner.should_run_cleanup():
    results = cleaner.cleanup_project_directory()
    print(f"Espace libéré: {results['space_freed']} bytes")
```

## Règles de nettoyage

### 📝 Logs
- **Conservation** : 30 jours par défaut
- **Limite** : 100 fichiers maximum
- **Archivage** : Fichiers `.log` importants

### 📋 Rapports
- **Conservation** : 90 jours par défaut
- **Limite** : 50 fichiers maximum
- **Archivage** : Fichiers `.html`, `.json`, `.md`

### 🧪 Tests
- **Conservation** : 60 jours par défaut
- **Limite** : 30 fichiers maximum
- **Archivage** : Fichiers de test importants

## Archivage

### Fichiers archivés
Les fichiers suivants sont automatiquement archivés :
- `.html` : Rapports HTML
- `.json` : Rapports JSON
- `.md` : Documentation Markdown
- `.log` : Logs importants

### Structure d'archivage
```
projet/.project/archive/
├── logs/
│   ├── audit_20250819_115223_20250819_120000.log
│   └── ...
├── reports/
│   ├── audit_report_20250819_115223_20250819_120000.html
│   └── ...
└── tests/
    └── ...
```

## Rapports de nettoyage

### Rapport automatique
Après chaque nettoyage global, un rapport est généré dans :
```
docs/cleanup_report_YYYYMMDD_HHMMSS.md
```

### Contenu du rapport
- Résumé du nettoyage
- Détails par projet
- Espace libéré
- Erreurs éventuelles

### Exemple de rapport
```markdown
# RAPPORT DE NETTOYAGE AUTOMATIQUE
Date: 2025-08-19 11:52:23

## Résumé
- **Projets traités:** 2
- **Projets nettoyés:** 2
- **Projets ignorés:** 0
- **Espace libéré:** 1.25 MB

## Détails par projet

### audit-universel
- **Statut:** success
- **Timestamp:** 2025-08-19T11:52:23

#### logs/
- Fichiers vérifiés: 15
- Fichiers supprimés: 5
- Fichiers archivés: 2
- Espace libéré: 256.50 KB
```

## Intégration avec l'audit

### Déclenchement automatique
Le nettoyage est automatiquement déclenché :
1. Après chaque audit de projet
2. Selon le planning configuré
3. Si l'espace disque est insuffisant

### Logs de nettoyage
Les actions de nettoyage sont enregistrées dans :
```
projet/.project/logs/cleanup_YYYYMMDD_HHMMSS.log
```

## Personnalisation

### Configuration personnalisée
Pour personnaliser le nettoyage d'un projet :

1. Créer le fichier de configuration :
```bash
mkdir -p projet/.project/config
```

2. Éditer `projet/.project/config/cleanup_config.json` :
```json
{
  "enabled": true,
  "retention_days": {
    "logs": 60,
    "reports": 180,
    "tests": 90
  },
  "max_files": {
    "logs": 200,
    "reports": 100,
    "tests": 50
  },
  "archive_enabled": true,
  "cleanup_schedule": "weekly"
}
```

### Désactivation du nettoyage
Pour désactiver le nettoyage d'un projet :
```json
{
  "enabled": false
}
```

## Surveillance et maintenance

### Vérification des statistiques
```python
from core.project_cleaner import ProjectCleaner

cleaner = ProjectCleaner(project_path)
stats = cleaner.get_cleanup_stats()
print(f"Taille totale: {stats['total_size']} bytes")
print(f"Dernier nettoyage: {stats['last_cleanup']}")
```

### Nettoyage manuel des archives
Les archives peuvent être nettoyées manuellement :
```bash
# Supprimer les archives de plus de 1 an
find projet/.project/archive -type f -mtime +365 -delete
```

## Bonnes pratiques

### ✅ Recommandations
1. **Configurer selon l'usage** : Ajuster les durées selon l'activité du projet
2. **Surveiller l'espace** : Vérifier régulièrement l'utilisation du disque
3. **Archiver les rapports importants** : Garder les rapports critiques
4. **Tester la configuration** : Vérifier que le nettoyage fonctionne comme attendu

### ❌ À éviter
1. **Désactiver complètement** : Le nettoyage est important pour la maintenance
2. **Durées trop courtes** : Risque de perdre des informations importantes
3. **Limites trop élevées** : Peut consommer beaucoup d'espace disque
4. **Ignorer les erreurs** : Toujours vérifier les rapports de nettoyage

## Dépannage

### Problèmes courants

#### Nettoyage ne s'exécute pas
- Vérifier que `enabled: true` dans la configuration
- Contrôler le planning de nettoyage
- Vérifier les permissions sur les dossiers

#### Erreurs d'archivage
- Vérifier l'espace disque disponible
- Contrôler les permissions d'écriture
- Vérifier que le dossier archive existe

#### Fichiers non supprimés
- Vérifier les dates de modification
- Contrôler les limites de fichiers
- Vérifier les permissions de suppression

### Logs de débogage
Pour activer les logs détaillés, ajouter dans la configuration :
```json
{
  "debug": true,
  "log_level": "verbose"
}
```

## Support

Pour toute question ou problème :
1. Consulter les logs de nettoyage
2. Vérifier la configuration du projet
3. Tester avec le nettoyage manuel
4. Consulter la documentation du projet

---

*Ce guide est maintenu avec le système d'audit universel v2.0.0*
