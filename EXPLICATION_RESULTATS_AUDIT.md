# 📊 Explication des Résultats de l'Audit (19 phases)

Ce document décrit le format des résultats et le calcul du score pour le système d'audit basé sur `audit/audit.ps1`.

## 🔍 Structure de l'audit

L'audit est organisé en **19 phases** (avec dépendances). Chaque phase exécute une ou plusieurs vérifications (modules `Checks-*.ps1`).

**Sous-numérotation des phases spécifiques :**
- `13a` = Phase 13 (spécifique OTT)
- `15a` à `15e` = Phases 15 à 19 (spécifiques Haies)

Les phases actuellement définies dans `audit.ps1` sont :

| Phase | Nom | Catégorie | Modules |
|------:|-----|-----------|---------|
| 1 | Inventaire Complet | Structure | `Checks-ProjectInventory.ps1` |
| 2 | Architecture Projet | Structure | `Checks-Architecture.ps1`, `Checks-Organization.ps1` |
| 3 | Sécurité | Sécurité | `Checks-Security.ps1` |
| 4 | Configuration | Configuration | `Checks-ConfigConsistency.ps1` |
| 5 | Backend API | Backend | `Checks-API.ps1`, `Checks-StructureAPI.ps1`, `Checks-Database.ps1` |
| 6 | Frontend | Frontend | `Checks-Routes.ps1`, `Checks-UI.ps1` |
| 7 | Qualité Code | Qualité | `Checks-CodeQuality.ps1`, `Checks-Duplication.ps1`, `Checks-Complexity.ps1` |
| 8 | Performance | Performance | `Checks-Performance.ps1`, `Checks-Optimizations.ps1` |
| 9 | Documentation | Documentation | `Checks-Documentation.ps1`, `Checks-MarkdownQuality.ps1` |
| 10 | Tests | Tests | `Checks-TestCoverage.ps1`, `Checks-FunctionalTests-Placeholder.ps1` |
| 11 | Déploiement | Déploiement | `Checks-Deployment-Paths.ps1` |
| 12 | Hardware/Firmware | Hardware | `Checks-HardwareFirmware.ps1` |
| 13a | IA & Compléments | IA | `projects/ott/modules/Checks-FunctionalTests.ps1`, `Checks-TestsComplets.ps1`, `Checks-TimeTracking.ps1`, `AI-TestsComplets.ps1` |
| 14 | Questions IA | IA | `AI-QuestionGenerator.ps1` |
| 15a | Intelligence du Domaine | Intelligence | `projects/haies/modules/Checks-DomainIntelligence.ps1` |
| 15b | Architecture Intelligente | Intelligence | `projects/haies/modules/Checks-SmartArchitecture.ps1` |
| 15c | Intelligence Utilisateur | Intelligence | `projects/haies/modules/Checks-UserIntelligence.ps1` |
| 15d | Intelligence Écologique | Intelligence | `projects/haies/modules/Checks-EcologicalIntelligence.ps1` |
| 15e | Intelligence Documentaire | Intelligence | `projects/haies/modules/Checks-DocumentationIntelligence.ps1` |

> **Note :** Les phases 13 et 15–19 sont spécifiques à certains projets.

## 📁 Fichiers générés

Les résultats sont écrits dans `audit/resultats/<projet>/`.

### 1) Résultat par phase

Les résultats par phase sont stockés **dans le résumé global** (`audit_summary_<timestamp>.json`) via la clé `PhaseResults`.
Les fichiers `phase_<ID>_<timestamp>.json` ne sont **pas générés** par défaut (désactivés dans `audit.ps1`).

### 2) Résumé global

En fin d'audit :

`audit_summary_<timestamp>.json`

Structure (extrait) :
```json
{
  "AuditVersion": "2.0.0",
  "Target": "project",
  "ProjectRoot": "...",
  "RequestedPhases": [1,2,3],
  "ExecutedPhases": [1,2,3],
  "PhaseResults": [ /* résultats en mémoire */ ],
  "TotalPhases": 3,
  "TotalModules": 10,
  "TotalErrors": 1,
  "TotalWarnings": 2,
  "Timestamp": "2026-01-04_200000",
  "OutputDir": "audit/resultats/<projet>"
}
```

### 3) Résumé IA

Dans le même dossier :

- `AI-SUMMARY.md` : instructions et problèmes à vérifier par l'IA
- `ai-context-<timestamp>.json` : contexte brut (questions + métriques)

## 📈 Comment fonctionne le scoring

### 1) Où sont stockés les scores ?

Les modules alimentent un dictionnaire :

`$Results.Scores["<Categorie>"] = <note sur 10>`

Exemple :
```json
{
  "Architecture": 10,
  "API": 4.5,
  "Database": 5,
  "CodeQuality": 8,
  "Complexity": 8,
  "Security": 10
}
```

### 2) Score global = moyenne pondérée

Le score global est disponible via `Calculate-GlobalScore` (dans `audit/modules/Utils.ps1`) mais **n'est pas automatiquement écrit** dans `audit_summary_<timestamp>.json`. Les scores par catégorie sont affichés dans `AI-SUMMARY.md`.

Les poids proviennent en priorité de :

`$AuditConfig.ScoreWeights`

Puis un jeu de poids par défaut est utilisé si absent.

Formule :
```
Score Global = (Somme(score_categorie × poids_categorie)) / (Somme(poids_categorie))
```

### 3) Pourquoi le score global peut être bas avec beaucoup de 10/10 ?

Parce que :
- certaines catégories ont un poids faible
- d'autres catégories (souvent backend/sécurité/qualité) ont un poids plus fort

Donc une note basse sur une catégorie “fortement pondérée” peut faire baisser significativement le global.

## ✅ Conseils de lecture

- Le fichier `audit_summary_*.json` permet de savoir :
  - quelles phases ont été exécutées
  - combien de modules ont échoué
- le détail des modules par phase
- Pour diagnostiquer un module : relancer avec `-Verbose` et ne cibler qu'une phase via `-Phases "<id>"`.

