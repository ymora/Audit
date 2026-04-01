# ===============================================================================
# AUTO-AUDIT DE L'AUDIT
# ===============================================================================

param(
    [switch]$Verbose = $false
)

Write-Host "🔍 AUTO-AUDIT DE L'AUDIT" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

# Analyser le projet audit lui-même
$auditPath = $PSScriptRoot

Write-Host "`n📁 Analyse de la structure..." -ForegroundColor Yellow

# Vérifier les fichiers essentiels
$essentialFiles = @(
    "audit.ps1",
    "README.md",
    "AI-Integration.ps1",
    "OLLAMA_QUICK.ps1"
)

$missingFiles = @()
foreach ($file in $essentialFiles) {
    if (Test-Path (Join-Path $auditPath $file)) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file manquant" -ForegroundColor Red
        $missingFiles += $file
    }
}

# Vérifier les dossiers essentiels
$essentialDirs = @(
    "modules",
    "config",
    "resultats"
)

$missingDirs = @()
foreach ($dir in $essentialDirs) {
    if (Test-Path (Join-Path $auditPath $dir)) {
        Write-Host "✅ $dir/" -ForegroundColor Green
    } else {
        Write-Host "❌ $dir/ manquant" -ForegroundColor Red
        $missingDirs += $dir
    }
}

# Analyser les modules
Write-Host "`n📚 Analyse des modules..." -ForegroundColor Yellow
$modulesPath = Join-Path $auditPath "modules"
if (Test-Path $modulesPath) {
    $moduleCount = (Get-ChildItem -Path $modulesPath -Filter "Checks-*.ps1").Count
    Write-Host "✅ $moduleCount modules de vérification" -ForegroundColor Green
    
    # Vérifier les modules cassés ou vides
    $brokenModules = @()
    Get-ChildItem -Path $modulesPath -Filter "Checks-*.ps1" | ForEach-Object {
        try {
            $content = Get-Content $_.FullName -Raw -ErrorAction Stop
            if ($content.Length -lt 100) {
                $brokenModules += $_.Name
                Write-Host "⚠️ $($_.Name) - Vide ou trop court" -ForegroundColor Yellow
            }
        } catch {
            $brokenModules += $_.Name
            Write-Host "❌ $($_.Name) - Erreur lecture" -ForegroundColor Red
        }
    }
    
    if ($brokenModules.Count -eq 0) {
        Write-Host "✅ Tous les modules sont valides" -ForegroundColor Green
    }
}

# Vérifier la documentation
Write-Host "`n📖 Analyse de la documentation..." -ForegroundColor Yellow
$readmePath = Join-Path $auditPath "README.md"
if (Test-Path $readmePath) {
    $readmeContent = Get-Content $readmePath -Raw
    if ($readmeContent -match "IA|Ollama|DocSense") {
        Write-Host "✅ README.md à jour (IA/Ollama mentionné)" -ForegroundColor Green
    } else {
        Write-Host "⚠️ README.md pas à jour (IA/Ollama non mentionné)" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ README.md manquant" -ForegroundColor Red
}

# Vérifier l'intégration IA
Write-Host "`n🤖 Analyse de l'intégration IA..." -ForegroundColor Yellow
$aiIntegrationPath = Join-Path $auditPath "AI-Integration.ps1"
if (Test-Path $aiIntegrationPath) {
    try {
        . $aiIntegrationPath
        if (Test-AI-Integration) {
            Write-Host "✅ IA intégrée et Ollama disponible" -ForegroundColor Green
        } else {
            Write-Host "⚠️ IA intégrée mais Ollama non disponible" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Erreur chargement IA: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "❌ AI-Integration.ps1 manquant" -ForegroundColor Red
}

# Nettoyer les fichiers temporaires
Write-Host "`n🧹 Nettoyage des fichiers temporaires..." -ForegroundColor Yellow
$tempFiles = @(
    "*.log",
    "*.tmp",
    "TEST_*.ps1",
    "*_BACKUP*",
    "*_OLD*"
)

$cleanedFiles = 0
foreach ($pattern in $tempFiles) {
    $files = Get-ChildItem -Path $auditPath -Filter $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        Remove-Item $file.FullName -Force -ErrorAction SilentlyContinue
        $cleanedFiles++
    }
}

if ($cleanedFiles -gt 0) {
    Write-Host "✅ $cleanedFiles fichiers temporaires supprimés" -ForegroundColor Green
} else {
    Write-Host "✅ Aucun fichier temporaire à supprimer" -ForegroundColor Green
}

# Calculer le score de l'audit
Write-Host "`n📊 Score de l'audit..." -ForegroundColor Yellow

$totalChecks = $essentialFiles.Count + $essentialDirs.Count + 3  # +3 pour modules, docs, IA
$passedChecks = ($essentialFiles.Count - $missingFiles.Count) + 
                 ($essentialDirs.Count - $missingDirs.Count) + 
                 $(if ($brokenModules.Count -eq 0) { 1 } else { 0 }) +
                 $(if (Test-Path $readmePath -and ($readmeContent -match "IA|Ollama")) { 1 } else { 0 }) +
                 $(if (Test-Path $aiIntegrationPath) { 1 } else { 0 })

$score = [math]::Round(($passedChecks / $totalChecks) * 10, 1)

Write-Host "Score: $score/10" -ForegroundColor $(if ($score -ge 8) { "Green" } elseif ($score -ge 6) { "Yellow" } else { "Red" })

# Recommandations
Write-Host "`n🎯 Recommandations:" -ForegroundColor Cyan

if ($missingFiles.Count -gt 0) {
    Write-Host "• Ajouter les fichiers manquants: $($missingFiles -join ', ')" -ForegroundColor Yellow
}

if ($missingDirs.Count -gt 0) {
    Write-Host "• Créer les dossiers manquants: $($missingDirs -join ', ')" -ForegroundColor Yellow
}

if ($brokenModules.Count -gt 0) {
    Write-Host "• Réparer les modules cassés: $($brokenModules -join ', ')" -ForegroundColor Yellow
}

if (-not (Test-Path $readmePath) -or -not ($readmeContent -match "IA|Ollama")) {
    Write-Host "• Mettre à jour README.md avec la documentation IA/Ollama" -ForegroundColor Yellow
}

if ($score -ge 8) {
    Write-Host "• L'audit est en bon état !" -ForegroundColor Green
} elseif ($score -ge 6) {
    Write-Host "• L'audit a besoin de quelques améliorations" -ForegroundColor Yellow
} else {
    Write-Host "• L'audit nécessite une révision importante" -ForegroundColor Red
}

Write-Host "`n✅ Auto-audit terminé !" -ForegroundColor Green
