<#
.SYNOPSIS
    Vérifie les chemins de déploiement PHP pour éviter les erreurs 500 en production
    
.DESCRIPTION
    Ce module analyse les fichiers PHP pour détecter les chemins d'inclusion relatifs
    qui pourraient causer des erreurs lors du déploiement sur des serveurs comme Render.
    
.NOTES
    Version: 1.1.0
    Auteur: Cascade AI Assistant
#>

function Invoke-Check-Deployment-Paths {
    param(
        [Parameter(Mandatory=$false)]
        [string]$ProjectPath,
        
        [Parameter(Mandatory=$false)]
        [string]$ProjectRoot,
        
        [Parameter(Mandatory=$false)]
        [string]$DeploymentRoot = "/var/www/html"
    )
    
    $root = if (-not [string]::IsNullOrWhiteSpace($ProjectPath)) { $ProjectPath } else { $ProjectRoot }
    if ([string]::IsNullOrWhiteSpace($root) -or -not (Test-Path $root)) {
        return @{
            Errors = 1
            Warnings = 0
            Issues = @("Chemin projet invalide pour la vérification de déploiement.")
            Score = 0
        }
    }
    
    Write-Host "🔍 Vérification des chemins de déploiement PHP..." -ForegroundColor Cyan
    
    # Patterns à rechercher (chemins d'inclusion non relatifs/absolus)
    $includePatterns = @(
        'require_once\s+[''"](?![\./])[^''"]+[''"]',
        'require\s+[''"](?![\./])[^''"]+[''"]',
        'include_once\s+[''"](?![\./])[^''"]+[''"]',
        'include\s+[''"](?![\./])[^''"]+[''"]'
    )
    
    $issues = @()
    $phpFiles = @(Get-ChildItem -Path $root -Filter "*.php" -Recurse -File -ErrorAction SilentlyContinue)
    
    Write-Host "📁 Fichiers PHP analysés: $($phpFiles.Count)" -ForegroundColor Yellow
    
    foreach ($file in $phpFiles) {
        $content = Get-Content -Path $file.FullName -Raw
        $lines = $content -split "`n"
        
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $lineNumber = $i + 1
            $line = $lines[$i]
            
            foreach ($pattern in $includePatterns) {
                if ($line -match $pattern) {
                    $issues += "Chemin d'inclusion potentiellement problématique: $($file.FullName.Replace($root, '').TrimStart('\','/')):$lineNumber"
                }
            }
        }
    }
    
    if ($issues.Count -eq 0) {
        Write-Host "✅ Aucun problème de chemin de déploiement détecté" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Problèmes de chemin de déploiement détectés: $($issues.Count)" -ForegroundColor Red
    }
    
    # Vérifier les fichiers critiques pour Render
    $criticalFiles = @(
        "api.php",
        "api/bootstrap.php",
        "api/routing/api_router.php",
        "api/index.php"
    )
    
    Write-Host ""
    Write-Host "🎯 Vérification des fichiers critiques pour Render..." -ForegroundColor Cyan
    
    foreach ($criticalFile in $criticalFiles) {
        $fullPath = Join-Path $root $criticalFile
        if (Test-Path $fullPath) {
            $content = Get-Content -Path $fullPath -Raw
            if ($content -match 'require_once\s+[''"]bootstrap/[^''"]+[''"]') {
                $issues += "Chemin relatif détecté: $criticalFile (bootstrap/...)"
            }
        } else {
            $issues += "Fichier critique manquant: $criticalFile"
        }
    }
    
    $warnings = $issues.Count
    $score = if ($warnings -eq 0) { 10 } else { [math]::Max(0, 10 - $warnings) }
    
    return @{
        Errors = 0
        Warnings = $warnings
        Issues = $issues
        Score = $score
        Recommendation = if ($warnings -gt 0) {
            "Corriger les chemins d'inclusion relatifs avec __DIR__ pour le déploiement"
        } else {
            "Les chemins sont compatibles avec le déploiement"
        }
    }
}
