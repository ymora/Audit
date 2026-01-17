# ===============================================================================
# VÉRIFICATION : COUVERTURE DE TESTS
# ===============================================================================
# Détecte et analyse les fichiers de tests existants

function Invoke-Check-TestCoverage {
    param(
        [Parameter(Mandatory=$true)]
        [array]$Files,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Config,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Results
    )
    
    # Si Checks n'existe pas ou Tests.Enabled n'est pas défini, activer par défaut
    if ($Config.Checks -and $Config.Checks.Tests -and $Config.Checks.Tests.Enabled -eq $false) {
        return
    }
    
    Write-PhaseSectionNamed -Title "Couverture de Tests" -Description "Analyse des fichiers de tests existants et de la couverture"
    
    try {
        # Vérifier si on a des fichiers à analyser
        if ($Files.Count -eq 0) {
            Write-Warn "Aucun fichier à analyser pour les tests - passage de cette phase"
            $Results.Scores["Tests"] = 10
            return
        }
        
        # Détecter les fichiers de tests (JS/TS + PowerShell)
        $testFiles = $Files | Where-Object {
            $_.Name -match '\.(test|spec)\.(js|jsx|ts|tsx)$' -or
            $_.Name -match '\.(Tests|test|spec)\.ps1$' -or
            $_.FullName -match '[\\/]__tests__[\\/]' -or
            $_.FullName -match '[\\/]tests?[\\/]'
        }
        
        # Compter aussi les fichiers dans __tests__/ même s'ils n'ont pas le pattern .test.js
        $testDirFiles = $Files | Where-Object {
            $_.FullName -match '[\\/]__tests__[\\/]' -and
            $_.Extension -match '\.(js|jsx|ts|tsx|ps1)$'
        }
        
        # Combiner et dédupliquer
        $allTestFiles = ($testFiles + $testDirFiles) | Sort-Object FullName -Unique
        
        Write-Host "  Fichiers de tests: $($allTestFiles.Count)" -ForegroundColor White
        if ($testDirFiles.Count -gt 0) {
            Write-Info "  Dont $($testDirFiles.Count) dans __tests__/"
        }
        
        $testScore = if($allTestFiles.Count -ge 10) { 8 } 
                    elseif($allTestFiles.Count -ge 5) { 6 } 
                    else { 4 }
        
        # Générer contexte pour l'IA si nécessaire
        $aiContext = @()
        if ($allTestFiles.Count -lt 5) {
            Write-Warn "Tests insuffisants ($($allTestFiles.Count) fichiers)"
            $Results.Recommendations += "Ajouter tests E2E pour fonctionnalités critiques"
            $aiContext += @{
                Category = "Tests"
                Type = "Insufficient Tests"
                Count = $allTestFiles.Count
                Recommended = 5
                Severity = "medium"
                NeedsAICheck = $true
                Question = "Seulement $($allTestFiles.Count) fichier(s) de tests détecté(s) (recommandé >= 5). Les tests sont-ils dans un autre répertoire, ou faut-il ajouter des tests pour les fonctionnalités critiques ?"
            }
        } else {
            Write-OK "$($allTestFiles.Count) fichiers de tests détectés"
        }
        
        $Results.Scores["Couverture de Tests"] = $testScore
        
        # Sauvegarder le contexte pour l'IA
        if (-not $Results.AIContext) {
            $Results.AIContext = @{}
        }
        if ($aiContext.Count -gt 0) {
            $Results.AIContext.Tests = @{
                Questions = $aiContext
            }
        }
    } catch {
        $Results.Scores["Couverture de Tests"] = 4
    }
}

