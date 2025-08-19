# Architecture des Tests - Système d'Audit Universel

## Vue d'ensemble

Le système d'audit utilise une architecture de tests modulaire et réutilisable pour éviter les doublons et faciliter la maintenance.

## Structure des Tests

```
audit-universel/
├── tests/                              # Tests du système d'audit
│   ├── generic/                        # Framework de tests réutilisables
│   │   ├── __init__.py                # Exports du framework
│   │   ├── base_test.py               # Classes de base
│   │   ├── api_test.py                # Mixin pour tests d'API
│   │   ├── frontend_test.py           # Mixin pour tests frontend
│   │   └── security_test.py           # Mixin pour tests de sécurité
│   ├── run_tests.py                   # Lanceur de tests unifié
│   ├── test_audit_configuration_integrity.py  # Test du système
│   ├── test_security_checker_unit.py  # Test des outils de sécurité
│   └── test_subprocess_detection.py   # Test de détection de processus
├── scripts/debug/                      # Outils de debug et analyse
│   ├── analyze_code_duplications_detailed.py
│   ├── debug_code_duplications_analysis.py
│   ├── debug_security_detection.py
│   └── fix_final_vulnerabilities.py
└── projects/{nom}/tests/               # Tests spécifiques aux projets
    ├── test_ai_providers.py           # Tests legacy
    ├── test_ai_providers_modern.py    # Tests modernisés
    ├── test_backend_api.py
    └── test_frontend_components.py
```

## Types de Tests

### 1. Tests du Système (`tests/`)

Ces tests vérifient le bon fonctionnement du système d'audit lui-même :

- **Configuration** : Intégrité des fichiers de configuration
- **Sécurité** : Fonctionnement des outils de sécurité
- **Détection** : Capacité à détecter les processus et services

### 2. Framework Générique (`tests/generic/`)

Framework réutilisable pour créer des tests spécifiques :

#### Classes de Base

```python
from tests.generic.base_test import BaseAuditTest, BaseProjectTest

class MonTest(BaseProjectTest):
    async def run_test(self):
        # Implémentation du test
        pass
```

#### Mixins Disponibles

- **SecurityTestMixin** : Tests de sécurité (Bandit, Safety)
- **APITestMixin** : Tests d'endpoints API
- **FrontendTestMixin** : Tests d'interface utilisateur

### 3. Tests Spécifiques (`projects/{nom}/tests/`)

Tests dédiés à un projet particulier :

- Utilisent le framework générique
- Testent les fonctionnalités spécifiques au projet
- Configurés via `config.json` du projet

### 4. Outils de Debug (`scripts/debug/`)

Scripts d'analyse et de débogage :

- Analyse des duplications de code
- Debug des détections de sécurité
- Outils de correction automatique

## Utilisation

### Lanceur de Tests Unifié

```bash
# Tous les tests
python tests/run_tests.py --all

# Tests du système uniquement
python tests/run_tests.py --system

# Tests d'un projet spécifique
python tests/run_tests.py --project docusense_ai
```

### Création d'un Nouveau Test

#### Test Générique

```python
#!/usr/bin/env python3
"""
Mon nouveau test générique.
"""

import sys
from pathlib import Path

# Ajouter le framework au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.generic.base_test import BaseAuditTest

class MonNouveauTest(BaseAuditTest):
    async def run_test(self):
        # Logique de test
        self.log_success("Test réussi")
        return self.results
```

#### Test de Projet avec Mixins

```python
#!/usr/bin/env python3
"""
Test spécifique utilisant les mixins.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tests.generic.base_test import BaseProjectTest
from tests.generic.api_test import APITestMixin
from tests.generic.security_test import SecurityTestMixin

class MonTestProjet(BaseProjectTest, APITestMixin, SecurityTestMixin):
    async def run_test(self):
        # Test de l'API
        result = self.test_api_health("http://localhost:8000")
        
        # Test de sécurité
        security = self.run_bandit_scan(self.project_path)
        
        if result["success"] and security["success"]:
            self.log_success("Tous les tests réussis")
        else:
            self.log_failure("Échec de certains tests")
        
        return self.results

# Compatibilité avec l'ancien système
async def run_test(project_path: Path, config: dict):
    test = MonTestProjet(project_path, config)
    return await test.run_test()
```

## Configuration des Tests

### Configuration Globale

Les tests utilisent les fichiers de configuration dans `rules/` :

- `audit_rules.json` : Règles d'audit
- `excluded_patterns.json` : Patterns à ignorer
- `quality_standards.json` : Standards de qualité

### Configuration par Projet

Chaque projet a sa configuration dans `projects/{nom}/config.json` :

```json
{
  "name": "Mon Projet",
  "type": "python",
  "specific_tests": [
    "test_api",
    "test_frontend",
    "test_security"
  ],
  "backend_ports": [8000],
  "frontend_ports": [3000],
  "quality_tools": ["pylint", "flake8"],
  "security_tools": ["bandit", "safety"]
}
```

## Rapports de Tests

Les rapports sont générés dans `reports/test_report.json` :

```json
{
  "timestamp": "2025-08-19T11:21:23",
  "total_tests": 6,
  "passed": 5,
  "failed": 1,
  "results": [
    {
      "test": "test_audit_configuration_integrity.py",
      "success": true,
      "message": "Test exécuté avec succès"
    }
  ]
}
```

## Bonnes Pratiques

### 1. Réutilisation

- Utilisez les mixins pour éviter la duplication
- Héritez des classes de base appropriées
- Partagez la logique commune dans le framework

### 2. Séparation des Responsabilités

- **Tests système** : Testent l'audit lui-même
- **Tests projet** : Testent les projets audités
- **Debug** : Outils d'analyse et correction

### 3. Configuration

- Utilisez les fichiers de configuration
- Paramétrez les tests via `config.json`
- Évitez les valeurs codées en dur

### 4. Compatibilité

- Maintenez la compatibilité avec l'ancien système
- Fournissez la fonction `run_test(project_path, config)`
- Documentez les changements

## Migration des Tests Existants

Pour migrer un ancien test :

1. **Identifier le type** : Système ou projet ?
2. **Choisir la classe de base** : `BaseAuditTest` ou `BaseProjectTest`
3. **Ajouter les mixins** nécessaires
4. **Implémenter** `run_test()`
5. **Maintenir** la fonction `run_test(project_path, config)` pour compatibilité

## Exemples Complets

Voir les fichiers suivants pour des exemples :

- `tests/test_audit_configuration_integrity.py` : Test système
- `projects/docusense_ai/tests/test_ai_providers_modern.py` : Test projet modernisé
- `tests/generic/` : Framework complet

---

**Cette architecture garantit :**
- ✅ Pas de doublons entre les tests
- ✅ Réutilisabilité maximale du code
- ✅ Maintenance simplifiée
- ✅ Extensibilité pour nouveaux projets
- ✅ Compatibilité avec l'existant
