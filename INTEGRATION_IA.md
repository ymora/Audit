# Integration IA dans l'Audit

## POINT D'ENTREE UNIQUE

**Fichier:** `audit/resultats/<projet>/AI-SUMMARY.md`

Ce fichier est regenere automatiquement a chaque audit et contient:
- Scores par categorie
- Questions a verifier par l'IA
- Format de reponse attendu

## Workflow Simplifie

```powershell
# 1. Lancer l'audit
.\audit\audit.ps1 -Phases "all"

# 2. Lire le resume IA
Get-Content audit\resultats\<projet>\AI-SUMMARY.md
```

## Architecture 2 Niveaux

| Niveau | Responsable | Fiabilite |
|--------|-------------|-----------|
| **CPU** | Audit auto (patterns, comptages) | 100% |
| **IA** | Cas ambigus (contexte semantique) | Variable |

## Format du Resume IA

```markdown
# AUDIT IA - VERIFICATION ET CORRECTIONS
> Genere: 2026-01-07 10:17 | Projet: D:\Windsurf\OTT

## INSTRUCTIONS
Pour chaque probleme, verifier le code et repondre:
- **FAUX POSITIF** : expliquer pourquoi ce n'est pas un vrai probleme
- **A CORRIGER** : proposer le fix avec extrait de code

## SCORES ACTUELS
| Categorie | Score | Status |
|-----------|-------|--------|

## PROBLEMES A ANALYSER
### API
#### [1] SQL Injection Risk - IMPORTANT
- **Fichier**: ``api.php`` ligne 45
- **Question**: Analyser ce probleme et proposer une solution.
```

## Reponse Attendue de l'IA

```
### [1] Verdict: FAUX POSITIF | A CORRIGER
Explication: ...
Fix propose (si applicable):
// code...
```

## Fichiers

| Fichier | Description |
|---------|-------------|
| `audit/resultats/<projet>/AI-SUMMARY.md` | Résumé IA principal |
| `audit/resultats/<projet>/audit_summary_<timestamp>.json` | Résumé JSON global |
| `audit/resultats/<projet>/ai-context-<timestamp>.json` | Contexte IA brut |
| `audit/audit.ps1` | Script principal |
| `audit/modules/*.ps1` | Modules de verification |
