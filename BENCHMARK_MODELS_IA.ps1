# ===============================================================================
# BENCHMARK COMPLET DES MODÈLES IA POUR L'AUDIT DOCSENSE
# ===============================================================================

Write-Host "BENCHMARK MODELES IA - AUDIT DOCSENSE" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Scénarios de test réels pour DocSense
$testScenarios = @(
    @{
        Name = "Hardware/Firmware Non Pertinent"
        Problem = "Tests Hardware/Firmware non executes"
        Context = "Phase 12: Hardware | Projet: DocSense AI V2 (application web)"
        Expected = "FAUX POSITIF"
        Difficulty = "Facile"
    },
    @{
        Name = "Fichiers Volumineux Complexes"
        Problem = "8 fichiers volumineux detectes (> 450 lignes): UIComponents.tsx (955 lignes), advanced_viewer_service.py (681 lignes)"
        Context = "Phase 7: Qualite Code | Projet: DocSense AI V2 (FastAPI + React + IA)"
        Expected = "PARTIEL (certains normaux, d'autres a corriger)"
        Difficulty = "Moyen"
    },
    @{
        Name = "API Non Accessible"
        Problem = "URL API non configuree - Impossible de tester l'API"
        Context = "Phase 5: Backend API | Projet: DocSense AI V2 (FastAPI local)"
        Expected = "A CORRIGER"
        Difficulty = "Moyen"
    },
    @{
        Name = "Documentation Manquante"
        Problem = "README.md absent et 4 fichiers dashboard manquants"
        Context = "Phase 9: Documentation | Projet: DocSense AI V2 (projet mature)"
        Expected = "A CORRIGER"
        Difficulty = "Facile"
    },
    @{
        Name = "Complexite Architecture"
        Problem = "Architecture complexe avec 64 scripts de production et 105 scripts de test"
        Context = "Phase 2: Architecture | Projet: DocSense AI V2 (systeme IA complet)"
        Expected = "FAUX POSITIF (normal pour projet IA)"
        Difficulty = "Difficile"
    }
)

# Modèles disponibles à tester
$models = @(
    @{ Name = "qwen2.5:3b"; Desc = "Actuel - Léger (1.9GB)"; Timeout = 15 }
    @{ Name = "qwen2.5:7b"; Desc = "Moyen (4.7GB)"; Timeout = 30 }
    @{ Name = "qwen2.5:14b"; Desc = "Puissant (9GB)"; Timeout = 60 }
    @{ Name = "deepseek-r1:14b"; Desc = "Expert Raisonnement (9GB)"; Timeout = 90 }
)

# Résultats du benchmark
$benchmarkResults = @()

Write-Host "`nScenarios de test: $($testScenarios.Count)" -ForegroundColor Yellow
Write-Host "Modeles a tester: $($models.Count)" -ForegroundColor Yellow
Write-Host "Tests totaux: $($testScenarios.Count * $models.Count)" -ForegroundColor Yellow

foreach ($model in $models) {
    Write-Host "`n=====================================" -ForegroundColor Cyan
    Write-Host "TEST MODELE: $($model.Name)" -ForegroundColor Cyan
    Write-Host "Description: $($model.Desc)" -ForegroundColor Gray
    Write-Host "=====================================" -ForegroundColor Cyan
    
    $modelResults = @{
        Model = $model.Name
        Description = $model.Desc
        Scenarios = @()
        TotalTime = 0
        SuccessRate = 0
        AverageTime = 0
    }
    
    foreach ($scenario in $testScenarios) {
        Write-Host "`nScenario: $($scenario.Name) [$($scenario.Difficulty)]" -ForegroundColor Yellow
        Write-Host "Expected: $($scenario.Expected)" -ForegroundColor Gray
        
        $prompt = @"
Analyse ce probleme d'audit pour DocSense AI V2:

PROBLEME: $($scenario.Problem)
CONTEXTE: $($scenario.Context)

Donne un verdict unique:
- FAUX POSITIF : si ce n'est pas un vrai probleme pour DocSense
- A CORRIGER : si c'est un vrai probleme a resoudre

Format reponse: VERDICT: [FAUX POSITIF|A CORRIGER] | Raison detaillee (2-3 phrases)
"@
        
        try {
            $body = @{
                model = $model.Name
                prompt = $prompt
                stream = $false
                options = @{
                    temperature = 0.1
                    num_predict = 200
                }
            } | ConvertTo-Json -Depth 5
            
            $startTime = Get-Date
            $response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec $model.Timeout
            $duration = (Get-Date) - $startTime
            
            $modelResults.TotalTime += $duration.TotalSeconds
            
            # Extraire le verdict
            if ($response.response -match "VERDICT:\s*(FAUX POSITIF|A CORRIGER)") {
                $verdict = $matches[1]
                $reason = if ($response.response -match "\|\s*(.+)$") { $matches[1].Trim() } else { "Pas de raison" }
                
                Write-Host "Temps: $($duration.TotalSeconds)s" -ForegroundColor Cyan
                Write-Host "Verdict: $verdict" -ForegroundColor $(if ($verdict -eq "FAUX POSITIF") { "Green" } else { "Yellow" })
                Write-Host "Raison: $reason" -ForegroundColor White
                
                # Évaluer la qualité du verdict
                $quality = "Correct"
                if ($scenario.Expected -eq "FAUX POSITIF" -and $verdict -eq "FAUX POSITIF") { $quality = "Correct" }
                elseif ($scenario.Expected -eq "A CORRIGER" -and $verdict -eq "A CORRIGER") { $quality = "Correct" }
                elseif ($scenario.Expected -eq "PARTIEL") { $quality = "Acceptable" }
                else { $quality = "Incorrect" }
                
                $modelResults.Scenarios += @{
                    Scenario = $scenario.Name
                    Verdict = $verdict
                    Reason = $reason
                    Time = $duration.TotalSeconds
                    Quality = $quality
                    Expected = $scenario.Expected
                }
                
                Write-Host "Qualite: $quality" -ForegroundColor $(if ($quality -eq "Correct") { "Green" } elseif ($quality -eq "Acceptable") { "Yellow" } else { "Red" })
                
            } else {
                Write-Host "Format de reponse invalide" -ForegroundColor Red
                $modelResults.Scenarios += @{
                    Scenario = $scenario.Name
                    Verdict = "ERREUR"
                    Reason = "Format invalide"
                    Time = $duration.TotalSeconds
                    Quality = "Incorrect"
                    Expected = $scenario.Expected
                }
            }
            
        } catch {
            Write-Host "Erreur: $($_.Exception.Message)" -ForegroundColor Red
            $modelResults.Scenarios += @{
                Scenario = $scenario.Name
                Verdict = "ERREUR"
                Reason = $_.Exception.Message
                Time = $model.Timeout
                Quality = "Incorrect"
                Expected = $scenario.Expected
            }
        }
        
        Write-Host "---" -ForegroundColor Gray
    }
    
    # Calculer les statistiques du modèle
    $modelResults.AverageTime = [math]::Round($modelResults.TotalTime / $testScenarios.Count, 2)
    $correctResults = ($modelResults.Scenarios | Where-Object { $_.Quality -eq "Correct" }).Count
    $modelResults.SuccessRate = [math]::Round(($correctResults / $testScenarios.Count) * 100, 1)
    
    $benchmarkResults += $modelResults
    
    Write-Host "`nSTATISTIQUES $($model.Name):" -ForegroundColor Cyan
    Write-Host "Taux de succes: $($modelResults.SuccessRate)%" -ForegroundColor $(if ($modelResults.SuccessRate -ge 80) { "Green" } elseif ($modelResults.SuccessRate -ge 60) { "Yellow" } else { "Red" })
    Write-Host "Temps moyen: $($modelResults.AverageTime)s" -ForegroundColor Cyan
    Write-Host "Temps total: $($modelResults.TotalTime)s" -ForegroundColor Gray
}

# Générer le rapport final
Write-Host "`n=====================================" -ForegroundColor Green
Write-Host "RAPPORT COMPARATIF DES MODELES IA" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

Write-Host "`nClassement par taux de succes:" -ForegroundColor Yellow
$sortedBySuccess = $benchmarkResults | Sort-Object -Property SuccessRate -Descending
for ($i = 0; $i -lt $sortedBySuccess.Count; $i++) {
    $model = $sortedBySuccess[$i]
    $color = if ($i -eq 0) { "Green" } elseif ($i -eq 1) { "Yellow" } else { "Gray" }
    Write-Host "$($i + 1). $($model.Model) - $($model.SuccessRate)% de succes - $($model.AverageTime)s moyenne" -ForegroundColor $color
}

Write-Host "`nClassement par vitesse:" -ForegroundColor Yellow
$sortedBySpeed = $benchmarkResults | Sort-Object -Property AverageTime
for ($i = 0; $i -lt $sortedBySpeed.Count; $i++) {
    $model = $sortedBySpeed[$i]
    $color = if ($i -eq 0) { "Green" } elseif ($i -eq 1) { "Yellow" } else { "Gray" }
    Write-Host "$($i + 1). $($model.Model) - $($model.AverageTime)s moyenne - $($model.SuccessRate)% de succes" -ForegroundColor $color
}

# Recommandation finale
$bestModel = $sortedBySuccess[0]
$fastestModel = $sortedBySpeed[0]

Write-Host "`nRECOMMANDATIONS:" -ForegroundColor Cyan
Write-Host "Meilleur qualite: $($bestModel.Model) ($($bestModel.SuccessRate)% de succes)" -ForegroundColor Green
Write-Host "Plus rapide: $($fastestModel.Model) ($($fastestModel.AverageTime)s)" -ForegroundColor Green

if ($bestModel.Model -eq $fastestModel.Model) {
    Write-Host ">>> LE MODELE IDEAL: $($bestModel.Model) (meilleur qualite ET plus rapide) <<<" -ForegroundColor Green
} else {
    Write-Host ">>> QUALITE: $($bestModel.Model) | VITESSE: $($fastestModel.Model) <<<" -ForegroundColor Yellow
}

Write-Host "`nBenchmark termine !" -ForegroundColor Green
