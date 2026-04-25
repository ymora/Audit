# 🔍 Audit System v4.0 — Architecture "Grâal"

## 📋 Vue d'ensemble
Le système d'audit le plus avancé pour la gouvernance technique de projets. Entièrement réécrit en **Python (Grâal v4.0)**, il offre une analyse multi-dimensionnelle (30+ phases) conçue pour une exploitation directe par des agents IA.

**Points forts de la v4.0:**
- **Pipeline Unifié** : 30+ dimensions d'analyse (Core, Advanced, Inventory, Specialist).
- **Analyse AST Directe** : Compréhension réelle de la logique du code (et non simple regex).
- **Synthèse IA native** : Produit un `executive_summary` et un plan d'action priorisé.
- **Inventaire Technique Profond** : Cartographie des endpoints API, variables d'env et complexité cyclomatique.
- **Reporting Premium** : Dashboard HTML elegant (Glassmorphism) pour une lecture rapide.

---

## 🚀 Utilisation (Python 3.10+)

```powershell
# 1. Installer (si nécessaire, stdlib uniquement par défaut + pathlib)
# Le système est conçu pour être portable sans dépendances lourdes.

# 2. Lancer l'audit d'un projet spécifique
python audit.py d:/Windsurf/MonProjet

# 3. Mode interactif (Menu de sélection)
python audit.py --interactive
```

---

## 🏗️ Architecture du Pipeline (30 Phases)

Le système exécute désormais un pipeline en 4 couches successives :

| Couche | Phases | Objectif |
| :--- | :--- | :--- |
| **Core** | Initialization, Discovery, Quality, Security, Metrics... | Fondations techniques et validité du projet. |
| **Advanced** | DevOps, UX, Scalability, Innovation, Git History... | Gouvernance, maintenance et évolution temporelle. |
| **Inventory** | API Inventory, Env Vars, Cyclomatic Complexity... | Cartographie technique précise pour l'IA. |
| **Specialist** | Security Extended, Performance, AI/ML Extended... | Deep dive sur les risques et composants IA. |

---

## 📊 Intelligence de Sortie

Contrairement aux versions précédentes, la v4.0 génère une **Synthèse IA** exploitable :
1. **Résumé Exécutif** : Texte naturel décrivant l'état de santé du projet.
2. **Issues Agrégées** : Regroupement du bruit technique pour se concentrer sur l'essentiel.
3. **Plan d'Action** : Liste triée par priorité (Critical > Major) avec effort estimé.

Les résultats sont sauvegardés dans `reports/<projet>/` :
- `audit_<timestamp>.json` : Rapport complet pour exploitation machine.
- `dashboard_<timestamp>.html` : Dashboard visuel pour lecture humaine.

---

## 📁 Structure du Projet

```
audit/
├── audit.py           # Point d'entrée principal (v4.0)
├── core/              # Moteur d'orchestration Graal
│   ├── engine.py      # Pipeline & Synthèse IA
│   └── project_detector.py
├── phases/            # Logique d'audit modulaire
│   ├── base_phase.py       # Interface unifiée
│   ├── core_phases.py      # Couche 1
│   ├── advanced_phases.py  # Couche 2
│   ├── inventory_phases.py # Couche 3 (AST-based)
│   └── specialist_*.py     # Couche 4 (Security, Perf, ML)
├── reports/           # Résultats (HTML & JSON)
├── tests/             # Suite de tests logicielle (Pytest)
└── legacy/            # Archives PowerShell v2.0 (Optionnel)
```

---

## 🤖 Pourquoi "Architecture Béton" ?
L'architecture Béton / Grâal garantit que l'audit est **immuable, traçable et hautement précis**. Chaque rapport est une "source de vérité" (Single Source of Truth) permettant à un agent IA de prendre des décisions de correction sans ambiguïté.

---
*Généré par Antigravity Audit Engine — Architecture Graal v4.0.*
