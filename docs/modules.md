# Documentation Technique des Modules d'Audit

## Table des Matières
- [Structure Générale](#structure-générale)
- [Modules Documentés](#modules-documentés)
  - [Checks-Organization](#checks-organizationps1)
  - [Checks-API](#checks-apips1)
  - [Checks-CodeQuality](#checks-codequalityps1)
  - [Checks-Architecture](#checks-architectureps1)
  - [Checks-CodeMort](#checks-codemortps1)
  - [Checks-Complexity](#checks-complexityps1)
  - [Checks-Duplication](#checks-duplicationps1)
  - [Checks-Performance](#checks-performanceps1)
  - [Autres Modules](#autres-modules)

## Structure Générale
Chaque module doit implémenter une fonction `Invoke-Check-*` avec les paramètres suivants :
```powershell
param(
    [Parameter(Mandatory=$true)]
    [array]$Files,
    
    [Parameter(Mandatory=$true)]
    [hashtable]$Config,
    
    [Parameter(Mandatory=$true)]
    [hashtable]$Results
)
```

## Modules Disponibles

## Checks-Organization.ps1
**Objectif** : Vérifier l'organisation du code et détecter les éléments temporaires
```@d:\Windsurf\audit\modules\Checks-Organization.ps1:1-20
# ===============================================================================
# VÉRIFICATION : ORGANISATION
# ===============================================================================

function Invoke-Check-Organization {
    param(
        [Parameter(Mandatory=$true)]
        [array]$Files,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Config,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Results
    )
```

---

## Checks-API.ps1
**Objectif** : Tester les endpoints API et vérifier leur fonctionnement
```@d:\Windsurf\audit\modules\Checks-API.ps1:1-20
# ===============================================================================
# VÉRIFICATION : API
# ===============================================================================

function Invoke-Check-API {
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Config,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Results,
        
        [string]$ProjectRoot = $global:ProjectRoot
    )
```

---

## Checks-CodeQuality.ps1
**Objectif** : Détecter le code mort et les éléments indésirables
```@d:\Windsurf\audit\modules\Checks-CodeQuality.ps1:1-20
# ===============================================================================
# VÉRIFICATION : QUALITÉ DE CODE
# ===============================================================================

function Invoke-Check-CodeQuality {
    param(
        [Parameter(Mandatory=$true)]
        [array]$Files,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Config,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Results
    )

```

## Checks-Architecture.ps1
**Objectif** : Analyser la structure globale du projet et vérifier la cohérence architecturale
```@d:\Windsurf\audit\modules\Checks-Architecture.ps1:1-20
# ===============================================================================
# VÉRIFICATION : ARCHITECTURE
# ===============================================================================

function Invoke-Check-Architecture {
    param(
        [Parameter(Mandatory=$true)]
        [array]$Files,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Config,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Results
    )
```

## Checks-CodeMort.ps1
**Objectif** : Détecter le code mort et les fonctions inutilisées
```@d:\Windsurf\audit\modules\Checks-CodeMort.ps1:1-20
# ===============================================================================
# VÉRIFICATION : CODE MORT
# ===============================================================================

function Invoke-Check-CodeMort {
    param(
        [Parameter(Mandatory=$true)]
        [array]$Files,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Config,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Results
    )
```

## Checks-Complexity.ps1
**Objectif** : Mesurer la complexité cyclomatique du code
```@d:\Windsurf\audit\modules\Checks-Complexity.ps1:1-20
# ===============================================================================
# VÉRIFICATION : COMPLEXITÉ
# ===============================================================================

function Invoke-Check-Complexity {
    param(
        [Parameter(Mandatory=$true)]
        [array]$Files,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Config,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Results
    )
```

## Checks-Duplication.ps1
**Objectif** : Détecter les duplications de code
```@d:\Windsurf\audit\modules\Checks-Duplication.ps1:1-20
# ===============================================================================
# VÉRIFICATION : DUPLICATION DE CODE
# ===============================================================================

function Invoke-Check-Duplication {
    param(
        [Parameter(Mandatory=$true)]
        [array]$Files,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Config,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Results
    )
```

## Checks-Performance.ps1
**Objectif** : Vérifier les performances du code
```@d:\Windsurf\audit\modules\Checks-Performance.ps1:1-20
# ===============================================================================
# VÉRIFICATION : PERFORMANCE
# ===============================================================================

function Invoke-Check-Performance {
    param(
        [Parameter(Mandatory=$true)]
        [array]$Files,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Config,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Results
    )
```

## Autres Modules
Les modules suivants seront documentés progressivement :
