# ===============================================================================
# MODULE DE BENCHMARK IA POUR L'AUDIT
# ===============================================================================

function Invoke-Check-IABenchmark {
    param(
        [Parameter(Mandatory=$false)]
        [string]$TargetPath = $script:Config.ProjectRoot,
        
        [Parameter(Mandatory=$false)]
        [switch]$Quick = $false
    )
    
    Write-Host "=== BENCHMARK IA POUR L'AUDIT ===" -ForegroundColor Cyan
    
    # Scénarios de test spécifiques à l'audit
    $testScenarios = @(
        @{
            Name = "Hardware/Firmware Non Pertinent"
            Problem = "Tests Hardware/Firmware non executes"
            Context = "Phase 12: Hardware | Projet: DocSense AI V2 (application web)"
            Expected = "FAUX POSITIF"
            Priority = "High"
        },
        @{
            Name = "Fichiers Volumineux Complexes"
            Problem = "8 fichiers volumineux detectes (> 450 lignes) dont UIComponents.tsx (955 lignes)"
            Context = "Phase 7: Qualite Code | Projet: DocSense AI V2 (FastAPI + React + IA)"
            Expected = "PARTIEL"
            Priority = "Medium"
        }
    )
    
    # Modèles IA disponibles
    $availableModels = @()
    try {
        $modelsResponse = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
        $availableModels = $modelsResponse.models | Where-Object { $_.name -match "qwen|deepseek|llama" } | Select-Object -ExpandProperty name
    } catch {
        Write-Host "Ollama non disponible" -ForegroundColor Red
        return @{
            Success = $false
            Issues = 1
            Warnings = 0
            Message = "Ollama non disponible"
        }
    }
    
    if ($availableModels.Count -eq 0) {
        Write-Host "Aucun modele IA compatible trouve" -ForegroundColor Red
        return @{
            Success = $false
            Issues = 1
            Warnings = 0
            Message = "Aucun modele IA compatible"
        }
    }
    
    Write-Host "Modeles disponibles: $($availableModels.Count)" -ForegroundColor Green
    $availableModels | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
    
    # Mode Quick : tester seulement le meilleur modèle
    if ($Quick) {
        $modelsToTest = @($availableModels[0])
        Write-Host "Mode Quick: test de $($modelsToTest[0]) uniquement" -ForegroundColor Yellow
    } else {
        $modelsToTest = $availableModels
        Write-Host "Mode Complet: test de tous les modeles" -ForegroundColor Yellow
    }
    
    # Scénarios à tester (réduit si Quick)
    $scenariosToTest = if ($Quick) { $testScenarios[0..1] } else { $testScenarios }
    
    $benchmarkResults = @()
    $totalTests = $modelsToTest.Count * $scenariosToTest.Count
    $currentTest = 0
    
    foreach ($model in $modelsToTest) {
        Write-Host "`n--- Test modele: $model ---" -ForegroundColor Cyan
        
        $modelResults = @{
            Model = $model
            Scenarios = @()
            TotalTime = 0
            SuccessCount = 0
            AverageTime = 0
        }
        
        foreach ($scenario in $scenariosToTest) {
            $currentTest++
            Write-Host "[$currentTest/$totalTests] $($scenario.Name)..." -ForegroundColor Yellow
            
            $prompt = @"
Analyse ce probleme d'audit pour DocSense AI V2:

PROBLEME: $($scenario.Problem)
CONTEXTE: $($scenario.Context)

Donne un verdict unique:
- FAUX POSITIF : si ce n'est pas un vrai probleme pour DocSense
- A CORRIGER : si c'est un vrai probleme a resoudre

Format reponse: VERDICT: [FAUX POSITIF|A CORRIGER] | Raison courte
"@
            
            try {
                $body = @{
                    model = $model
                    prompt = $prompt
                    stream = $false
                    options = @{
                        temperature = 0.1
                        num_predict = 100
                    }
                } | ConvertTo-Json -Depth 5
                
                $startTime = Get-Date
                $timeout = if ($model -match "14b") { 60 } elseif ($model -match "7b") { 30 } else { 15 }
                $response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec $timeout
                $duration = (Get-Date) - $startTime
                
                $modelResults.TotalTime += $duration.TotalSeconds
                
                if ($response.response -match "VERDICT:\s*(FAUX POSITIF|A CORRIGER)") {
                    $verdict = $matches[1]
                    $reason = if ($response.response -match "\|\s*(.+)$") { $matches[1].Trim() } else { "" }
                    
                    # Évaluer la qualité
                    $quality = "Correct"
                    if ($scenario.Expected -eq "FAUX POSITIF" -and $verdict -eq "FAUX POSITIF") { $quality = "Correct" }
                    elseif ($scenario.Expected -eq "A CORRIGER" -and $verdict -eq "A CORRIGER") { $quality = "Correct" }
                    elseif ($scenario.Expected -eq "PARTIEL") { $quality = "Acceptable" }
                    else { $quality = "Incorrect" }
                    
                    if ($quality -eq "Correct") { $modelResults.SuccessCount++ }
                    
                    $icon = if ($quality -eq "Correct") { "✅" } elseif ($quality -eq "Acceptable") { "⚠️" } else { "❌" }
                    Write-Host "  $icon $verdict - $($duration.TotalSeconds)s" -ForegroundColor $(if ($quality -eq "Correct") { "Green" } elseif ($quality -eq "Acceptable") { "Yellow" } else { "Red" })
                    
                    $modelResults.Scenarios += @{
                        Scenario = $scenario.Name
                        Verdict = $verdict
                        Reason = $reason
                        Time = $duration.TotalSeconds
                        Quality = $quality
                    }
                    
                } else {
                    Write-Host "  ❌ Format de reponse invalide" -ForegroundColor Red
                    $modelResults.Scenarios += @{
                        Scenario = $scenario.Name
                        Verdict = "ERREUR"
                        Reason = "Format invalide"
                        Time = $timeout
                        Quality = "Incorrect"
                    }
                }
                
            } catch {
                Write-Host "  ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
                $modelResults.Scenarios += @{
                    Scenario = $scenario.Name
                    Verdict = "ERREUR"
                    Reason = $_.Exception.Message
                    Time = $timeout
                    Quality = "Incorrect"
                }
            }
        }
        
        $modelResults.AverageTime = [math]::Round($modelResults.TotalTime / $scenariosToTest.Count, 2)
        $modelResults.SuccessRate = [math]::Round(($modelResults.SuccessCount / $scenariosToTest.Count) * 100, 1)
        
        $benchmarkResults += $modelResults
        
        Write-Host "Score: $($modelResults.SuccessRate)% - Temps moyen: $($modelResults.AverageTime)s" -ForegroundColor $(if ($modelResults.SuccessRate -ge 80) { "Green" } elseif ($modelResults.SuccessRate -ge 60) { "Yellow" } else { "Red" })
    }
    
    # Résultats finaux
    Write-Host "`n=== RESULTATS BENCHMARK ===" -ForegroundColor Green
    
    if ($benchmarkResults.Count -gt 0) {
        $bestModel = $benchmarkResults | Sort-Object -Property SuccessRate -Descending | Select-Object -First 1
        $fastestModel = $benchmarkResults | Sort-Object -Property AverageTime | Select-Object -First 1
        
        Write-Host "Meilleur modele: $($bestModel.Model) ($($bestModel.SuccessRate)% de succes)" -ForegroundColor Green
        Write-Host "Plus rapide: $($fastestModel.Model) ($($fastestModel.AverageTime)s)" -ForegroundColor Green
        
        # Recommandation
        if ($bestModel.SuccessRate -ge 80) {
            Write-Host ">>> RECOMMANDE: $($bestModel.Model) <<<" -ForegroundColor Green
            $recommendedModel = $bestModel.Model
        } elseif ($fastestModel.SuccessRate -ge 60) {
            Write-Host ">>> RECOMMANDE: $($fastestModel.Model) (equilibre vitesse/qualite) <<<" -ForegroundColor Yellow
            $recommendedModel = $fastestModel.Model
        } else {
            Write-Host ">>> ATTENTION: Aucun modele ne depasse 60% de succes <<<" -ForegroundColor Red
            $recommendedModel = $availableModels[0]
        }
        
        # Sauvegarder les résultats
        $resultsFile = Join-Path $script:Config.OutputDir "IA_BENCHMARK_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
        $benchmarkResults | ConvertTo-Json -Depth 5 | Out-File -FilePath $resultsFile -Encoding UTF8
        Write-Host "Resultats sauvegardes: $resultsFile" -ForegroundColor Cyan
        
        return @{
            Success = $true
            Issues = 0
            Warnings = if ($bestModel.SuccessRate -lt 80) { 1 } else { 0 }
            Message = "Benchmark termine - Modele recommande: $recommendedModel"
            RecommendedModel = $recommendedModel
            Results = $benchmarkResults
        }
    } else {
        return @{
            Success = $false
            Issues = 1
            Warnings = 0
            Message = "Aucun resultat de benchmark"
        }
    }
}
