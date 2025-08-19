# Script PowerShell pour lancer l'Interface Graphique - Système d'Audit Universel
# =============================================================================

Write-Host "🔍 Lancement de l'Interface Graphique - Système d'Audit Universel" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Vérifier que Python est disponible
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python détecté: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python non trouvé. Veuillez installer Python." -ForegroundColor Red
    exit 1
}

# Chemin vers le script de lancement
$auditDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$launchScript = Join-Path $auditDir "launch_gui.py"

if (-not (Test-Path $launchScript)) {
    Write-Host "❌ Script de lancement introuvable: $launchScript" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Script de lancement trouvé: $launchScript" -ForegroundColor Green
Write-Host "🚀 Lancement de l'interface graphique..." -ForegroundColor Yellow
Write-Host ""

try {
    # Lancer l'interface graphique
    python $launchScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Interface graphique fermée avec succès." -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Erreur lors de l'exécution de l'interface graphique." -ForegroundColor Red
    }
} catch {
    Write-Host ""
    Write-Host "❌ Erreur lors du lancement: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
