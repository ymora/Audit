# ===============================================================================
# OLLAMA QUICK AUDIT - Version rapide
# ===============================================================================

function Invoke-OllamaQuickAudit {
    param(
        [string]$Model = "qwen2.5:3b"
    )
    
    Write-Host "🤖 Ollama Quick Audit..." -ForegroundColor Cyan
    
    # Vérifier Ollama
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
        Write-Host "✅ Ollama: modèles disponibles" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Ollama indisponible" -ForegroundColor Red
        return
    }
    
    # Lire seulement les problèmes clés de l'audit
    $auditPath = "resultats\AI-SUMMARY.md"
    $content = Get-Content $auditPath -Raw -Encoding UTF8
    
    # Extraire seulement la section des problèmes
    $problemsSection = ""
    $inProblems = $false
    foreach ($line in $content -split "`n") {
        if ($line -match "## PROBLEMES A ANALYSER") {
            $inProblems = $true
            continue
        }
        if ($inProblems -and $line -match "---") {
            break
        }
        if ($inProblems) {
            $problemsSection += $line + "`n"
        }
    }
    
    # Prompt court et direct
    $prompt = @"
Analyse ces problèmes d'audit DocuSense AI V2:

$problemsSection

Réponds FORMAT EXACT:
## [1] Verdict: FAUX POSITIF
**Raison**: explication courte

## [2] Verdict: A CORRIGER  
**Raison**: problème réel
**Fix**: solution rapide

Sois concis, max 5 problèmes.
"@
    
    Write-Host "🧠 Analyse avec $Model..." -ForegroundColor Yellow
    
    # Appel Ollama avec timeout court
    $body = @{
        model = $Model
        prompt = $prompt
        stream = $false
        options = @{
            temperature = 0.1
            num_predict = 500
        }
    } | ConvertTo-Json -Depth 5
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 30
        
        # Sauvegarder
        $output = $response.response
        $output | Out-File -FilePath "resultats\OLLAMA_QUICK_ANALYSIS.md" -Encoding UTF8 -Force
        
        Write-Host "✅ Analyse terminée" -ForegroundColor Green
        Write-Host "📄 Fichier: resultats\OLLAMA_QUICK_ANALYSIS.md" -ForegroundColor Cyan
        
        # Afficher les 3 premières lignes
        $firstLines = ($output -split "`n" | Select-Object -First 10) -join "`n"
        Write-Host "`n🎯 Aperçu:" -ForegroundColor Yellow
        Write-Host $firstLines -ForegroundColor White
        
    }
    catch {
        Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Lancer l'analyse
Invoke-OllamaQuickAudit
