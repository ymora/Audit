# ===============================================================================
# INTÉGRATION IA AUTOMATIQUE DANS L'AUDIT
# ===============================================================================
# Intégration Ollama pour détecter faux positifs en temps réel

function Invoke-AI-Analysis {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Problem,
        
        [Parameter(Mandatory=$true)]
        [string]$Context,
        
        [Parameter(Mandatory=$false)]
        [string]$Severity = "medium",
        
        [Parameter(Mandatory=$false)]
        [switch]$Quick = $true
    )
    
    try {
        # Prompt optimisé pour analyse rapide
        $prompt = @"
Analyse ce problème d'audit pour DocuSense AI V2:

PROBLÈME: $Problem
CONTEXTE: $Context
SÉVÉRITÉ: $Severity

Donne un verdict unique:
- FAUX POSITIF : si ce n'est pas un vrai problème pour DocSense
- A CORRIGER : si c'est un vrai problème à résoudre

Format réponse: VERDICT: [FAUX POSITIF|A CORRIGER] | Raison courte
"@
        
        $body = @{
            model = "qwen2.5:3b"
            prompt = $prompt
            stream = $false
            options = @{
                temperature = 0.1
                num_predict = 50
            }
        } | ConvertTo-Json -Depth 5
        
        $timeout = if ($Quick) { 10 } else { 30 }
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec $timeout
        
        # Extraire le verdict
        if ($response.response -match "VERDICT:\s*(FAUX POSITIF|A CORRIGER)") {
            $verdict = $matches[1]
            $reason = if ($response.response -match "\|\s*(.+)$") { $matches[1].Trim() } else { "" }
            
            return @{
                Verdict = $verdict
                Reason = $reason
                Confidence = "high"
            }
        } else {
            return @{
                Verdict = "A CORRIGER"
                Reason = "Impossible d'analyser automatiquement"
                Confidence = "low"
            }
        }
        
    } catch {
        return @{
            Verdict = "A CORRIGER"
            Reason = "Erreur IA: $($_.Exception.Message)"
            Confidence = "none"
        }
    }
}

function Invoke-AI-ModuleValidation {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ModuleName,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Results,
        
        [Parameter(Mandatory=$true)]
        [string]$ProjectRoot
    )
    
    Write-Info "🤖 IA validation du module: $ModuleName"
    
    $problems = @()
    $aiValidated = @()
    
    # Analyser chaque problème détecté
    foreach ($key in $Results.Keys) {
        if ($Results[$key] -is [hashtable] -and $Results[$key].Issues -gt 0) {
            $problems += @{
                Type = $key
                Details = $Results[$key]
            }
        }
    }
    
    if ($problems.Count -eq 0) {
        Write-OK "✅ IA: Aucun problème à valider pour $ModuleName"
        return $aiValidated
    }
    
    # Analyser chaque problème avec l'IA
    foreach ($problem in $problems) {
        $context = "Module: $ModuleName | Projet: DocuSense AI V2"
        
        $aiResult = Invoke-AI-Analysis -Problem $problem.Type -Context $context -Quick
        
        $aiValidated += @{
            Type = $problem.Type
            OriginalSeverity = "medium"
            AIVerdict = $aiResult.Verdict
            AIReason = $aiResult.Reason
            AIConfidence = $aiResult.Confidence
        }
        
        $icon = if ($aiResult.Verdict -eq "FAUX POSITIF") { "✅" } else { "⚠️" }
        Write-Info "$icon IA: $($problem.Type) → $($aiResult.Verdict)"
    }
    
    return $aiValidated
}

function Invoke-AI-PhaseValidation {
    param(
        [Parameter(Mandatory=$true)]
        [int]$PhaseId,
        
        [Parameter(Mandatory=$true)]
        [string]$PhaseName,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$PhaseResults,
        
        [Parameter(Mandatory=$true)]
        [string]$ProjectRoot
    )
    
    Write-Info "🤖 IA validation de la phase $PhaseId : $PhaseName"
    
    $totalProblems = 0
    $falsePositives = 0
    $realProblems = 0
    
    # Analyser tous les modules de la phase
    foreach ($module in $PhaseResults.Keys) {
        if ($PhaseResults[$module] -is [hashtable]) {
            $moduleResult = $PhaseResults[$module]
            
            if ($moduleResult.Issues -gt 0) {
                $totalProblems += $moduleResult.Issues
                
                # Validation IA pour les problèmes significatifs
                if ($moduleResult.Issues -gt 2 -or $moduleResult.Errors -gt 0) {
                    $context = "Phase $PhaseId | Module: $module | Projet: DocuSense AI V2"
                    
                    $aiResult = Invoke-AI-Analysis -Problem "$($moduleResult.Issues) problèmes détectés" -Context $context
                    
                    if ($aiResult.Verdict -eq "FAUX POSITIF") {
                        $falsePositives += $moduleResult.Issues
                        Write-OK "✅ IA: $module - FAUX POSITIF ($($moduleResult.Issues) problèmes ignorés)"
                    } else {
                        $realProblems += $moduleResult.Issues
                        Write-Warn "⚠️ IA: $module - A CORRIGER ($($moduleResult.Issues) problèmes réels)"
                    }
                }
            }
        }
    }
    
    # Résumé de la validation IA
    Write-Info "📊 IA Phase $PhaseId - Résumé:"
    Write-Info "  • Problèmes totaux: $totalProblems"
    Write-Info "  • Faux positifs: $falsePositives"
    Write-Info "  • Problèmes réels: $realProblems"
    
    if ($falsePositives -gt 0) {
        $reduction = [math]::Round(($falsePositives / $totalProblems) * 100, 1)
        Write-OK "🎯 IA réduction: $reduction% des problèmes éliminés"
    }
    
    return @{
        TotalProblems = $totalProblems
        FalsePositives = $falsePositives
        RealProblems = $realProblems
        Reduction = if ($totalProblems -gt 0) { [math]::Round(($falsePositives / $totalProblems) * 100, 1) } else { 0 }
    }
}

function Invoke-AI-GlobalValidation {
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$AllResults,
        
        [Parameter(Mandatory=$true)]
        [string]$ProjectRoot
    )
    
    Write-Info "🤖 IA Validation Globale de l'Audit"
    
    # Analyser les scores globaux
    $lowScores = @()
    foreach ($category in $AllResults.Scores.Keys) {
        $score = $AllResults.Scores[$category]
        if ($score -lt 6) {
            $lowScores += @{
                Category = $category
                Score = $score
            }
        }
    }
    
    if ($lowScores.Count -gt 0) {
        Write-Warn "⚠️ Catégories avec score bas détectées: $($lowScores.Count)"
        
        foreach ($lowScore in $lowScores) {
            $context = "Score bas: $($lowScore.Category) = $($lowScore.Score)/10 | Projet: DocuSense AI V2"
            
            $aiResult = Invoke-AI-Analysis -Problem "Score $($lowScore.Score)/10 pour $($lowScore.Category)" -Context $context
            
            $icon = if ($aiResult.Verdict -eq "FAUX POSITIF") { "✅" } else { "⚠️" }
            Write-Info "$icon IA: $($lowScore.Category) ($($lowScore.Score)/10) → $($aiResult.Verdict)"
        }
    } else {
        Write-OK "✅ IA: Tous les scores sont acceptables"
    }
    
    # Analyser les modules non pertinents pour DocSense
    $docSenseSpecificModules = @("Firmware", "Hardware", "Deployment")
    foreach ($module in $docSenseSpecificModules) {
        if ($AllResults.Scores.ContainsKey($module)) {
            $score = $AllResults.Scores[$module]
            if ($score -lt 5) {
                Write-OK "✅ IA: $module score bas ($score/10) - NORMAL pour DocSense (non pertinent)"
            }
        }
    }
}

# Exporter les fonctions
Export-ModuleMember -Function Invoke-AI-Analysis, Invoke-AI-ModuleValidation, Invoke-AI-PhaseValidation, Invoke-AI-GlobalValidation
