# ===============================================================================
# SCRIPT DE BENCHMARK IA AUTONOME
# ===============================================================================

param(
    [switch]$Quick = $false,
    [switch]$Verbose = $false
)

Write-Host "BENCHMARK IA - SYSTEME D'AUDIT" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

# Charger le module
$modulePath = Join-Path $PSScriptRoot "modules\Checks-IABenchmark.ps1"
if (Test-Path $modulePath) {
    . $modulePath
    
    # Configurer le contexte d'audit minimal
    $script:Config = @{
        ProjectRoot = $PSScriptRoot
        OutputDir = Join-Path $PSScriptRoot "resultats"
    }
    
    # Créer le répertoire de résultats
    if (-not (Test-Path $script:Config.OutputDir)) {
        New-Item -ItemType Directory -Path $script:Config.OutputDir -Force | Out-Null
    }
    
    # Lancer le benchmark
    $result = Invoke-Check-IABenchmark -Quick:$Quick -Verbose:$Verbose
    
    if ($result.Success) {
        Write-Host "`n✅ Benchmark termine avec succes" -ForegroundColor Green
        Write-Host "Modele recommande: $($result.RecommendedModel)" -ForegroundColor Cyan
        
        if ($result.Warnings -gt 0) {
            Write-Host "⚠️ Attention: Qualite des modeles pourrait etre amelioree" -ForegroundColor Yellow
        }
    } else {
        Write-Host "`n❌ Benchmark echoue: $($result.Message)" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Module de benchmark non trouve: $modulePath" -ForegroundColor Red
    exit 1
}

Write-Host "`nBenchmark IA termine !" -ForegroundColor Green
