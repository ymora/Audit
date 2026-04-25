# Architecture du projet `audit`

## Vue d'ensemble

L'auditeur est un pipeline modulaire Python 3.8+ sans dépendance externe.

```
audit/
├── audit.py              # CLI / point d'entrée
├── core/
│   ├── engine.py         # Orchestrateur principal du pipeline
│   └── project_detector.py  # Auto-détection du type de projet
├── phases/
│   ├── base_phase.py     # Classe abstraite BasePhase + AuditIssue
│   ├── core_phases.py    # Phases fondamentales (init → sécurité → métriques)
│   ├── advanced_phases.py    # Phases avancées (DevOps, UX, IA/ML, DevEx...)
│   ├── security_checks.py    # Module spécialiste : secrets, fonctions dangereuses, SQLi
│   ├── performance_checks.py # Module spécialiste : boucles, mémoire, DB queries
│   ├── ai_ml_checks.py       # Module spécialiste : frameworks ML, LLM, VectorDB, OCR
│   └── architecture_checks.py  # Vérification SQLAlchemy, nommage config
├── reports/              # Rapports générés (JSON + HTML)
├── scripts/
│   └── docusense/        # Scripts de diagnostic DocuSense (non génériques)
├── tests/
│   └── test_engine.py    # Tests pytest complets
└── docs/                 # Cette documentation
```

## Pipeline d'exécution

```
AuditEngine.run_audit()
 ├── _run_core_phases()          # 11 phases : init → discovery → quality(AST) → security → metrics
 ├── _run_advanced_phases()      # 13 phases : devops → UX → docs → excellence → IA/ML → reporting
 └── _run_specialist_checks()    # 3 modules  : SecurityChecks + PerformanceChecks + AIMLChecks
      │
      ├── SecurityChecks.get_all_issues()    → secrets, fonctions dangereuses, SQLi
      ├── PerformanceChecks.get_all_issues() → boucles, fuites mémoire, DB
      └── AIMLChecks.get_all_components()   → ML frameworks, LLM, VectorDB, OCR
```

## Score de santé

| Pénalité     | Valeur |
|-------------|--------|
| Issue CRITICAL | -25 pts (global) / -40 pts (sécurité) |
| Issue MAJOR    | -10 pts (global) / -15 pts (sécurité) |
| Issue MINOR    | -1 pt (linéaire jusqu'à 20, logarithmique ensuite) |

## Ajouter une phase

1. Créer une classe héritant de `BasePhase` dans `phases/`
2. Implémenter la méthode `execute() -> Dict[str, Any]`
3. Utiliser `self.add_issue(AuditIssue(...))` pour reporter
4. Retourner `self.get_results()` ou un dict custom
5. Enregistrer dans `core/engine.py` dans `_run_core_phases()` ou `_run_advanced_phases()`
6. Exporter dans `phases/__init__.py`

## Détection de projet (ProjectDetector)

Auto-détecte : langages, frameworks, bases de données, ports, services, Docker, CI/CD.
Supporte Python, TypeScript, JavaScript, Go, Rust, Java, Ruby, PHP.
