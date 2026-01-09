<#
.SYNOPSIS
    Vérifie les chemins de déploiement PHP pour éviter les erreurs 500 en production
    
.DESCRIPTION
    Ce module analyse les fichiers PHP pour détecter les chemins d'inclusion relatifs
    qui pourraient causer des erreurs lors du déploiement sur des serveurs comme Render.
    
.NOTES
    Version: 1.0.0
    Auteur: Cascade AI Assistant
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectPath,
    
    [Parameter(Mandatory=$false)]
    [string]$DeploymentRoot = "/var/www/html"
)

Write-Host "🔍 Vérification des chemins de déploiement PHP..." -ForegroundColor Cyan

# Patterns à rechercher
$includePatterns = @(
    'require_once\s+[''"](?![\./])[^''"]+[''"]',  # require sans chemin relatif/absolu
    'require\s+[''"](?![\./])[^''"]+[''"]',      # require sans chemin relatif/absolu  
    'include_once\s+[''"](?![\./])[^''"]+[''"]',  # include_once sans chemin relatif/absolu
    'include\s+[''"](?![\./])[^''"]+[''"]'       # include sans chemin relatif/absolu
)

$issues = @()
$phpFiles = @()

# Récupérer tous les fichiers PHP
Get-ChildItem -Path $ProjectPath -Filter "*.php" -Recurse | ForEach-Object {
    $phpFiles += $_.FullName
}

Write-Host "📁 Fichiers PHP analysés: $($phpFiles.Count)" -ForegroundColor Yellow

# Analyser chaque fichier PHP
foreach ($file in $phpFiles) {
    $content = Get-Content -Path $file -Raw
    $lines = $content -split "`n"
    
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $lineNumber = $i + 1
        $line = $lines[$i]
        
        foreach ($pattern in $includePatterns) {
            if ($line -match $pattern) {
                $issues += @{
                    File = $file.Replace($ProjectPath, "").TrimStart('\', '/')
                    Line = $lineNumber
                    Content = $line.Trim()
                    Issue = "Chemin d'inclusion potentiellement problématique en déploiement"
                    Recommendation = "Utiliser __DIR__ pour un chemin absolu relatif"
                }
            }
        }
    }
}

# Afficher les résultats
if ($issues.Count -eq 0) {
    Write-Host "✅ Aucun problème de chemin de déploiement détecté" -ForegroundColor Green
} else {
    Write-Host "⚠️  Problèmes de chemin de déploiement détectés: $($issues.Count)" -ForegroundColor Red
    Write-Host ""
    
    foreach ($issue in $issues) {
        Write-Host "📂 Fichier: $($issue.File):$($issue.Line)" -ForegroundColor Yellow
        Write-Host "   ❌ $($issue.Content)" -ForegroundColor Red
        Write-Host "   💡 $($issue.Recommendation)" -ForegroundColor Cyan
        Write-Host ""
    }
    
    # Score d'impact
    $score = [math]::Max(0, 100 - ($issues.Count * 10))
    Write-Host "📊 Score de compatibilité déploiement: $score/100" -ForegroundColor $(if($score -ge 80) { "Green" } elseif($score -ge 60) { "Yellow" } else { "Red" })
}

# Vérifier les fichiers critiques pour le déploiement Render
$criticalFiles = @(
    "api.php",
    "api/bootstrap.php", 
    "api/routing/api_router.php",
    "api/index.php"
)

Write-Host ""
Write-Host "🎯 Vérification des fichiers critiques pour Render..." -ForegroundColor Cyan

foreach ($criticalFile in $criticalFiles) {
    $fullPath = Join-Path $ProjectPath $criticalFile
    if (Test-Path $fullPath) {
        Write-Host "✅ $criticalFile trouvé" -ForegroundColor Green
        
        # Vérifier spécifiquement les problèmes connus
        $content = Get-Content -Path $fullPath -Raw
        if ($content -match "require_once\s+[''"]bootstrap/[^'"]+[''"]") {
            Write-Host "   ⚠️  Chemin relatif détecté: bootstrap/..." -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ $criticalFile manquant" -ForegroundColor Red
    }
}

# Exporter les résultats
$auditResult = @{
    Success = ($issues.Count -eq 0)
    Issues = $issues
    Score = if ($issues.Count -eq 0) { 100 } else { [math]::Max(0, 100 - ($issues.Count * 10)) }
    Recommendation = if ($issues.Count -gt 0) { 
        "Corriger les chemins d'inclusion relatifs avec __DIR__ pour le deploiement" 
    } else { 
        "Les chemins sont compatibles avec le deploiement" 
    }
}

return $auditResult
