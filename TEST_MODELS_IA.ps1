# ===============================================================================
# TEST DES MODÈLES IA POUR L'AUDIT
# ===============================================================================

Write-Host "Test des modeles IA pour l'audit" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Test prompt complexe
$testPrompt = @"
Analyse ce problème d'audit pour DocSense AI V2:

PROBLEME: 8 fichiers volumineux détectés (> 450 lignes)
CONTEXTE: Phase 7: Qualité Code | Projet: DocuSense AI V2 (application web complexe avec FastAPI + React + IA)

Fichiers concernés:
- frontend/src/components/UIComponents.tsx (955 lignes)
- backend/app/services/advanced_viewer_service.py (681 lignes)
- backend/app/services/dual_ia_display_service.py (647 lignes)

Donne un verdict détaillé:
- FAUX POSITIF : si c'est normal pour une application de cette complexité
- A CORRIGER : si c'est vraiment problématique

Justifie avec des arguments techniques précis sur l'architecture DocSense.
"@

# Modèles à tester
$models = @(
    @{ Name = "qwen2.5:3b"; Desc = "Actuel - Léger et rapide" }
    @{ Name = "qwen2.5:7b"; Desc = "Moyen - Bon équilibre" }
    @{ Name = "qwen2.5:14b"; Desc = "Puissant - Meilleure qualité" }
    @{ Name = "deepseek-r1:14b"; Desc = "Expert - Raisonnement avancé" }
)

foreach ($model in $models) {
    Write-Host "`nTest $($model.Name) - $($model.Desc)" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Gray
    
    try {
        $body = @{
            model = $model.Name
            prompt = $testPrompt
            stream = $false
            options = @{
                temperature = 0.1
                num_predict = 300
            }
        } | ConvertTo-Json -Depth 5
        
        $startTime = Get-Date
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 60
        $duration = (Get-Date) - $startTime
        
        Write-Host "Temps: $($duration.TotalSeconds) secondes" -ForegroundColor Cyan
        Write-Host "Reponse:" -ForegroundColor White
        Write-Host $response.response -ForegroundColor Green
        Write-Host "---" -ForegroundColor Gray
        
    } catch {
        Write-Host "Erreur: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nTest termine !" -ForegroundColor Green
