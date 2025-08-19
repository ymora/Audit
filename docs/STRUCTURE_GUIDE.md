# GUIDE DE LA STRUCTURE DU SYSTÈME D'AUDIT

## Vue d'ensemble

Le système d'audit universel suit maintenant une structure claire et centralisée qui évite la pollution des projets audités.

## Structure du système d'audit

```
audit-universel/
├── audit.py              # Point d'entrée unifié
├── core/                 # Fichiers principaux du système
│   ├── audit.py         # Logique d'audit universel
│   ├── audit_gui.py     # Interface graphique
│   └── project_cleaner.py # Système de nettoyage
├── tools/                # Outils d'analyse
├── scripts/              # Scripts utilitaires
├── tests/                # Tests du système d'audit
├── docs/                 # Documentation
├── rules/                # Règles d'audit
├── project_audits/       # Tests spécifiques par projet
│   ├── projet_a/
│   │   ├── test_custom.py
│   │   ├── config.json
│   │   └── README.md
│   └── projet_b/
│       ├── test_custom.py
│       └── config.json
└── projects/             # Rapports générés uniquement
    ├── projet_a/
    │   ├── reports/
    │   │   ├── audit_report_20250819.html
    │   │   └── audit_report_20250819.json
    │   └── logs/
    │       └── audit_20250819.log
    └── projet_b/
        ├── reports/
        └── logs/
```

## Workflow d'audit

### 1. Préparation
```bash
# Ouvrir le projet à auditer dans Cursor
# Le projet reste dans son emplacement original (ex: C:\Users\ymora\Desktop\mon_projet)
```

### 2. Audit
```bash
# Depuis le système d'audit
python audit.py --cli C:\Users\ymora\Desktop\mon_projet
```

### 3. Résultats
- **Tests spécifiques** : Créés automatiquement dans `project_audits/mon_projet/`
- **Rapports** : Générés dans `projects/mon_projet/reports/`
- **Logs** : Sauvegardés dans `projects/mon_projet/logs/`

## Avantages de cette structure

### ✅ **Projets propres**
- Aucune pollution des projets audités
- Pas de dossiers `.audit/`, `.project/`, etc.
- Projets restent dans leur état original

### ✅ **Centralisation**
- Tous les tests d'audit au même endroit
- Gestion unifiée des rapports
- Configuration centralisée

### ✅ **Flexibilité**
- Tests personnalisés par projet
- Configuration spécifique par projet
- Détection automatique des besoins

### ✅ **Maintenance**
- Nettoyage automatique des rapports
- Structure claire et logique
- Documentation centralisée

## Utilisation

### Interface graphique
```bash
python audit.py          # Lance l'interface moderne
python audit.py --gui    # Même chose, explicite
```

### Ligne de commande
```bash
python audit.py --cli C:\chemin\vers\projet    # Audit d'un projet
python audit.py --cleanup                      # Nettoyage global
python audit.py --help                         # Aide
```

### Nettoyage automatique
- Exécuté automatiquement après chaque audit
- Configuration par projet dans `project_audits/projet/cleanup_config.json`
- Rapports de nettoyage dans `docs/cleanup_report_*.md`

## Configuration

### Tests spécifiques
```python
# project_audits/mon_projet/test_custom.py
async def run_test(project_path, config):
    # Tests personnalisés pour ce projet
    return {"success": True, "message": "Test réussi"}
```

### Configuration par projet
```json
// project_audits/mon_projet/config.json
{
  "name": "Mon Projet",
  "type": "python",
  "custom_settings": {
    "ignore_patterns": ["venv/", "__pycache__/"],
    "quality_threshold": 80
  }
}
```

## Migration depuis l'ancienne structure

Si vous aviez des tests spécifiques dans les projets, ils peuvent être migrés automatiquement :

1. **Détection** : Le système détecte les tests existants
2. **Copie** : Les tests sont copiés dans `project_audits/`
3. **Nettoyage** : Les anciens dossiers d'audit sont supprimés

---

*Cette structure garantit une organisation claire et une maintenance facile du système d'audit.*
