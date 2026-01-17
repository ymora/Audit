# 🔍 Système d'Audit v2.0 - Documentation

## 📋 Vue d'ensemble

Système d'audit générique et portable pour analyser la qualité, la sécurité et la structure de projets web (Next.js, React, PHP, etc.).

**Fonctionnalités principales:**
- 19 phases d'analyse (certaines spécifiques à des projets)
- Détection automatique du type de projet
- Export JSON pour analyse IA (nombre de questions variable)
- Interface graphique Windows + ligne de commande
- Extensible par projet (surcharges config/modules)

## 🖥️ Interface Graphique (Recommandé)

**Double-cliquez sur `audit-gui.bat`** pour ouvrir l'interface visuelle :

- Sélection de la cible (projet, fichier, répertoire)
- Choix des phases à exécuter
- Options verbose/silencieux
- Accès direct aux résultats

## 🚀 Utilisation en ligne de commande

```powershell
# Audit complet (19 phases, certaines spécifiques projet)
.\audit\audit.ps1 -Phases "all" -Verbose

# Audit de phases spécifiques (les dépendances sont ajoutées automatiquement)
.\audit\audit.ps1 -Phases "3,7" -Verbose

# Audit d'un fichier spécifique
.\audit\audit.ps1 -Target "file" -Path ".\api.php" -Phases "3,7" -Verbose

# Audit d'un répertoire spécifique
.\audit\audit.ps1 -Target "directory" -Path ".\app" -Phases "2,6,7" -Verbose

# Via le script batch (ligne de commande)
.\audit\audit.bat -Phases "all" -Verbose

# Menu interactif (sans arguments)
.\audit\audit.ps1
```

## 📚 Documentation

- **[EXPLICATION_RESULTATS_AUDIT.md](EXPLICATION_RESULTATS_AUDIT.md)** : Comprendre les scores et résultats de l'audit
- **[INTEGRATION_IA.md](INTEGRATION_IA.md)** : Guide d'intégration IA pour vérification des cas douteux
- **[CONFIGURATION_MULTIPROJET.md](CONFIGURATION_MULTIPROJET.md)** : Configuration multiprojet et détection automatique

## 📁 Structure

```
audit/
├── audit.ps1          # Point d'entrée principal
├── audit-gui.ps1      # Interface graphique Windows
├── audit-gui.bat      # Lanceur interface graphique (double-clic)
├── audit.bat          # Lanceur ligne de commande
├── modules/           # Modules de vérification (24 actifs)
│   ├── Checks-*.ps1         # Modules de vérification
│   ├── Utils.ps1            # Utilitaires
│   ├── FileScanner.ps1      # Scan fichiers
│   ├── ProjectDetector.ps1  # Détection type projet
│   ├── ReportGenerator.ps1  # Export JSON/MD
├── config/            # Configuration
│   ├── audit.config.ps1         # Configuration globale (générique)
│   └── audit.config.example.ps1 # Exemple
├── projects/          # Spécificités projet (auto-détection)
│   └── ott/
│       ├── project.ps1        # Détection projet OTT
│       ├── config/            # Surcharges config
│       └── modules/           # Modules spécifiques OTT
└── resultats/         # Résultats d'audit (générés)
    └── <projet>/      # Un dossier par projet audité
        ├── audit_summary_<timestamp>.json
        ├── AI-SUMMARY.md              # Résumé IA unique (par audit)
        └── ai-context-<timestamp>.json
```

## 🎯 Les 19 Phases d'Audit

**Sous-numérotation des phases spécifiques :**
- `13a` = Phase 13 (spécifique OTT)
- `15a` à `15e` = Phases 15 à 19 (spécifiques Haies)

| Phase | Nom | Description | Dépendances |
|-------|-----|-------------|-------------|
| 1 | Inventaire | Analyse fichiers/structure | - |
| 2 | Architecture | Structure projet | 1 |
| 3 | Sécurité | Vulnérabilités, secrets | 1,2 |
| 4 | Configuration | Docker, environnement | 1 |
| 5 | Backend API | Endpoints, handlers, DB | 1,2 |
| 6 | Frontend | Routes, UI/UX | 1,2 |
| 7 | Qualité Code | Code mort, duplication, complexité | 1,2 |
| 8 | Performance | Optimisations, mémoire | 1,2,5,6 |
| 9 | Documentation | README, commentaires | 1,2 |
| 10 | Tests | Unitaires, E2E | 1,2,5 |
| 11 | Déploiement | CI/CD | 1,4 |
| 12 | Hardware | Firmware Arduino/ESP32 | 1 |
| 13a | IA & Compléments | Tests exhaustifs, suivi temps (OTT) | 1,2,5,10 |
| 14 | Questions IA | Cas ambigus à déléguer | 1,2,7 |
| 15a | Intelligence du Domaine | Expertise métier (Haies) | 1,2 |
| 15b | Architecture Intelligente | Choix techniques (Haies) | 1,2 |
| 15c | Intelligence Utilisateur | UX intelligente (Haies) | 1,2 |
| 15d | Intelligence Écologique | Vision durable (Haies) | 1,2 |
| 15e | Intelligence Documentaire | Transmission du savoir (Haies) | 1,2 |

**Note :** Certaines phases sont spécifiques à un projet. Par exemple la phase 13 (OTT) et les phases 15 à 19 (Haies).

## ⚙️ Configuration

Voir [CONFIGURATION_MULTIPROJET.md](CONFIGURATION_MULTIPROJET.md) pour la configuration détaillée.

## 📊 Comprendre les Résultats

Voir [EXPLICATION_RESULTATS_AUDIT.md](EXPLICATION_RESULTATS_AUDIT.md) pour comprendre les scores et leur calcul.

## 🤖 Intégration IA

Voir [INTEGRATION_IA.md](INTEGRATION_IA.md) pour utiliser l'IA pour vérifier les cas douteux détectés par l'audit.

