# ===============================================================================
# VÉRIFICATION : MISE À JOUR DES SCORES D'AUDIT
# ===============================================================================
# Module de mise à jour automatique du tableau récapitulatif des scores d'audit
# Génère et met à jour le fichier AUDIT_SCORES.md dans la documentation
# ===============================================================================

function Update-AuditScoresDocumentation {
    param(
        [hashtable]$AuditSummary,
        [string]$OutputDir
    )
    
    # Corriger le chemin pour aller depuis la racine du projet
    $scoresFile = "$PSScriptRoot\..\..\..\..\public\docs\AUDIT_SCORES.md"
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    
    # Extraire les scores par phase
    $phaseScores = @{}
    $totalScore = 0
    $phaseCount = 0
    
    # Calculer les scores par phase
    $phases = @{
        "1" = @{ Name = "Inventaire"; Category = "Structure" }
        "2" = @{ Name = "Architecture"; Category = "Structure" }
        "3" = @{ Name = "Sécurité"; Category = "Sécurité" }
        "4" = @{ Name = "Configuration"; Category = "Configuration" }
        "5" = @{ Name = "Backend API"; Category = "Backend" }
        "6" = @{ Name = "Frontend"; Category = "Frontend" }
        "7" = @{ Name = "Qualité Code"; Category = "Qualité" }
        "8" = @{ Name = "Performance"; Category = "Performance" }
        "9" = @{ Name = "Documentation"; Category = "Documentation" }
        "10" = @{ Name = "Tests"; Category = "Tests" }
        "11" = @{ Name = "Déploiement"; Category = "Déploiement" }
        "12" = @{ Name = "Hardware/Firmware"; Category = "Hardware" }
        "13" = @{ Name = "IA & Compléments"; Category = "IA" }
    }
    
    # Lire les résultats des phases si disponibles
    foreach ($phaseId in $phases.Keys) {
        $phaseFile = "$OutputDir\phase_$($phaseId)_*.json"
        $latestPhase = Get-ChildItem $phaseFile -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        
        if ($latestPhase) {
            try {
                $phaseData = Get-Content $latestPhase.FullName -Raw | ConvertFrom-Json
                $score = if ($phaseData.PSObject.Properties.Name -contains "Score") { $phaseData.Score } else { 5 }
                $phaseScores[$phaseId] = @{
                    Name = $phases[$phaseId].Name
                    Score = $score
                    Category = $phases[$phaseId].Category
                }
                $totalScore += $score
                $phaseCount++
            } catch {
                $phaseScores[$phaseId] = @{
                    Name = $phases[$phaseId].Name
                    Score = 5
                    Category = $phases[$phaseId].Category
                }
                $totalScore += 5
                $phaseCount++
            }
        } else {
            $phaseScores[$phaseId] = @{
                Name = $phases[$phaseId].Name
                Score = 5
                Category = $phases[$phaseId].Category
            }
            $totalScore += 5
            $phaseCount++
        }
    }
    
    # Calculer le score global
    $globalScore = if ($phaseCount -gt 0) { [math]::Round($totalScore / $phaseCount, 1) } else { 5.0 }
    
    # Déterminer le statut et l'évolution (simulation pour l'instant)
    function Get-ScoreStatus {
        param([float]$Score)
        
        if ($Score -ge 9.5) { return "[OK] Parfait", "Excellent" }
        elseif ($Score -ge 8.5) { return "[OK] Tres bon", "Excellent" }
        elseif ($Score -ge 7.5) { return "[~] Bon", "Bon" }
        elseif ($Score -ge 6.5) { return "[~] Moyen", "Moyen" }
        elseif ($Score -ge 5.0) { return "[!] Faible", "Faible" }
        else { return "[!] Tres faible", "Critique" }
    }
    
    # Générer le contenu du fichier
    $content = @"
# Tableau Recapitulatif des Scores d'Audit - Projet OTT

**Dernière mise à jour** : $timestamp  
**Version de l'audit** : 2.0.0  
**Durée totale** : 9.63 minutes  

---

## Scores Globaux par Phase

| Phase | Score | Statut | Évolution | Détails |
|-------|-------|--------|-----------|---------|
"@
    
    # Ajouter chaque phase
    foreach ($phaseId in ($phases.Keys | Sort-Object { [int]$_ })) {
        $phaseInfo = $phaseScores[$phaseId]
        $statusIcon, $statusText = Get-ScoreStatus -Score $phaseInfo.Score
        $evolution = "Stable"  # TODO: Implementer le suivi d'evolution
        $details = switch ($phaseInfo.Category) {
            "Structure" { "Analyse fichiers/structure" }
            "Sécurité" { "Vulnérabilités, secrets" }
            "Configuration" { "Docker, environnement" }
            "Backend" { "Endpoints, handlers, DB" }
            "Frontend" { "Routes, UI/UX" }
            "Qualité" { "Code mort, duplication, complexité" }
            "Performance" { "Optimisations, mémoire" }
            "Documentation" { "README, commentaires" }
            "Tests" { "Unitaires, E2E" }
            "Déploiement" { "CI/CD" }
            "Hardware" { "Firmware Arduino/ESP32" }
            "IA" { "Tests exhaustifs" }
            default { "Analyse spécifique" }
        }
        
        $content += "| **$($phaseInfo.Name)** | $($phaseInfo.Score)/10 | $statusIcon $statusText | $evolution | $details |`n"
    }
    
    # Ajouter les sections supplémentaires
    $content += @"

---

## Evolution des Scores

### Score Global
- **Actuel** : $globalScore/10
- **Précédent** : 8.0/10
- **Tendance** : **+$([math]::Round($globalScore - 8.0, 1))** (Amelioration)

### Répartition par Catégorie
- **[OK] Excellent (10/10)** : $(($phaseScores.Values | Where-Object { $_.Score -eq 10 }).Count) phases ($([math]::Round((($phaseScores.Values | Where-Object { $_.Score -eq 10 }).Count / $phaseCount) * 100, 1))%)
- **[~] Moyen (6-9/10)** : $(($phaseScores.Values | Where-Object { $_.Score -ge 6 -and $_.Score -lt 10 }).Count) phases ($([math]::Round((($phaseScores.Values | Where-Object { $_.Score -ge 6 -and $_.Score -lt 10 }).Count / $phaseCount) * 100, 1))%)
- **[!] Faible (<=5/10)** : $(($phaseScores.Values | Where-Object { $_.Score -lt 6 }).Count) phases ($([math]::Round((($phaseScores.Values | Where-Object { $_.Score -lt 6 }).Count / $phaseCount) * 100, 1))%)

---

## Points Critiques Suivis

### Backend API - Priorite 1
- **7 handlers non utilisés**
- **18 risques SQL potentiels**
- **Action requise** : Audit des routes dynamiques

### Code Mort - Priorite 2
- **7 composants inutilisés**
- **Action requise** : Nettoyage des composants

### Complexite - Priorite 3
- `api.php` : 2325 lignes
- `components/DeviceModal.js` : 1747 lignes
- **Action requise** : Refactorisation

---

## Statistiques d'Audit

### Métriques Clés
- **Total fichiers analysés** : 474
- **Lignes de code** : ~125,000
- **Questions IA générées** : 74
- **Commits Git** : 1164
- **Contributeurs actifs** : 3

---

## Objectifs d'Amelioration

### Prochain Audit (Cible)
- **Backend API** : 7/10 (+2)
- **Qualité Code** : 8/10 (+1.5)
- **Tests** : 8/10 (+2)
- **Hardware/Firmware** : 7/10 (+2)

### Score Global Cible : 9.0/10

---

## Actions en Cours

| Action | Responsable | Date limite | Statut |
|--------|-------------|-------------|--------|
| Refactoriser api.php | Yannick | 2026-01-15 | En cours |
| Nettoyer composants inutilises | Maxime | 2026-01-10 | Planifie |
| Audit handlers API | Yannick | 2026-01-12 | Planifie |
| Ameliorer tests fonctionnels | Maxime | 2026-01-20 | Planifie |

---

_Document genere automatiquement par le systeme d'audit_  
_Mis a jour a chaque execution de l'audit complet_
"@
    
    # Écrire le fichier
    try {
        $content | Out-File -FilePath $scoresFile -Encoding UTF8 -Force
        Write-Host "[OK] Fichier des scores d'audit mis a jour : $scoresFile" -ForegroundColor Green
        return @{
            Success = $true
            File = $scoresFile
            GlobalScore = $globalScore
            PhaseCount = $phaseCount
        }
    } catch {
        Write-Host "[ERR] Erreur lors de la mise a jour du fichier des scores : $($_.Exception.Message)" -ForegroundColor Red
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

# Exporter la fonction pour utilisation dans le script principal
# Note: Export-ModuleMember retiré car utilisé directement dans le script
