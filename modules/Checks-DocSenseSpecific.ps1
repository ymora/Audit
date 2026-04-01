# ===============================================================================
# VÉRIFICATION : DOCUSENSE SPÉCIFIQUE
# ===============================================================================
# Module adapté spécifiquement pour DocuSense AI V2
# Exclut les modules non pertinents (Firmware, Hardware)

function Invoke-Check-DocSenseSpecific {
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Config,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Results
    )
    
    Write-PhaseSection -PhaseNumber 15 -Title "DocuSense Spécifique"
    
    $docSenseScore = 0
    $aiContext = @()
    
    try {
        Write-Info "Analyse spécifique DocuSense AI V2..."
        
        $projectRoot = if ($Config.ProjectRoot) { $Config.ProjectRoot } else { $PSScriptRoot }
        
        # =========================================================================
        # 1. VÉRIFICATION STRUCTURE DOCUSENSE
        # =========================================================================
        Write-Info "Vérification structure DocuSense..."
        
        $expectedStructure = @{
            "backend\main.py" = "Point d'entrée FastAPI"
            "backend\app" = "Application FastAPI"
            "frontend\src" = "Source React/TypeScript"
            "data\defense_docling.db" = "Base de données principale"
            "docs" = "Documentation"
        }
        
        $structureStatus = @{
            Valid = @()
            Missing = @()
        }
        
        foreach ($path in $expectedStructure.Keys) {
            $fullPath = Join-Path $projectRoot $path
            $exists = Test-Path $fullPath
            
            if ($exists) {
                $structureStatus.Valid += @{
                    Path = $path
                    Description = $expectedStructure[$path]
                }
                $docSenseScore += 1
                Write-OK "✓ $path"
            } else {
                $structureStatus.Missing += @{
                    Path = $path
                    Description = $expectedStructure[$path]
                }
                Write-Warn "✗ $path manquant"
            }
        }
        
        # =========================================================================
        # 2. VÉRIFICATION TECHNOLOGIES DOCUSENSE
        # =========================================================================
        Write-Info "Vérification technologies DocuSense..."
        
        $techChecks = @{
            "FastAPI" = @(Join-Path $projectRoot "backend\main.py", "from fastapi import")
            "React" = @(Join-Path $projectRoot "frontend\package.json", "react")
            "TypeScript" = @(Join-Path $projectRoot "frontend\tsconfig.json")
            "SQLite" = @(Join-Path $projectRoot "data\defense_docling.db")
            "Python" = @(Join-Path $projectRoot "requirements.txt")
            "Node" = @(Join-Path $projectRoot "frontend\package.json")
        }
        
        $techStatus = @{}
        
        foreach ($tech in $techChecks.Keys) {
            $detected = $false
            foreach ($check in $techChecks[$tech]) {
                if ($check -match "\.py$|\.json$|\.db$") {
                    # Fichier
                    $detected = Test-Path $check
                } else {
                    # Contenu
                    $file = $techChecks[$tech][0]
                    if (Test-Path $file) {
                        $content = Get-Content $file -Raw -ErrorAction SilentlyContinue
                        $detected = $content -match $check
                    }
                }
                if ($detected) { break }
            }
            
            $techStatus[$tech] = $detected
            if ($detected) {
                $docSenseScore += 1
                Write-OK "✓ $tech détecté"
            } else {
                Write-Warn "✗ $tech non détecté"
            }
        }
        
        # =========================================================================
        # 3. CATÉGORISATION SCRIPTS DOCUSENSE
        # =========================================================================
        Write-Info "Catégorisation scripts spécifiques DocuSense..."
        
        $scriptCategories = @{
            "Tests Unitaires" = @("backend\tests\unit", "backend\tests\integration")
            "Scripts Démo" = @("test_demo_", "demo_")
            "Scripts Outils" = @("backend\scripts\tools", "check_", "inspect_")
            "Scripts Benchmarks" = @("benchmark_", "test_benchmark")
            "Scripts Migration" = @("migrate_", "patch_")
            "Scripts Debug" = @("debug_", "diag_", "test_ocr")
        }
        
        $scriptStats = @{}
        
        foreach ($category in $scriptCategories.Keys) {
            $count = 0
            foreach ($pattern in $scriptCategories[$category]) {
                if ($pattern -match "\\") {
                    # Dossier
                    $folder = Join-Path $projectRoot $pattern
                    if (Test-Path $folder) {
                        $count += (Get-ChildItem -Path $folder -Filter "*.py" -ErrorAction SilentlyContinue).Count
                    }
                } else {
                    # Pattern de nom
                    $allScripts = Get-ChildItem -Path $projectRoot -Recurse -Filter "*.py" -ErrorAction SilentlyContinue
                    $count += ($allScripts | Where-Object { $_.Name -match $pattern }).Count
                }
            }
            $scriptStats[$category] = $count
            Write-Info "  $category : $count scripts"
        }
        
        # =========================================================================
        # 4. EXCLUSION MODULES NON PERTINENTS
        # =========================================================================
        Write-Info "Exclusion modules non pertinents pour DocuSense..."
        
        $nonPertinentModules = @(
            "Firmware",
            "Hardware", 
            "USB",
            "Arduino",
            "ESP32"
        )
        
        foreach ($module in $nonPertinentModules) {
            Write-Info "  ✗ $module exclu (non pertinent pour DocuSense)"
        }
        
        # Score maximum ajusté pour DocuSense
        $maxScore = 20
        $finalScore = [math]::Min($docSenseScore, $maxScore)
        $scorePercentage = [math]::Round(($finalScore / $maxScore) * 10, 1)
        
        Write-Success "Score DocuSense: $finalScore/$maxScore ($scorePercentage/10)"
        
        # Ajouter aux résultats
        $Results["DocSenseSpecific"] = @{
            Score = $scorePercentage
            Structure = $structureStatus
            Technologies = $techStatus
            Scripts = $scriptStats
            NonPertinentExcluded = $nonPertinentModules
        }
        
        # Contexte pour l'IA
        $aiContext += @{
            Type = "DocSenseSpecific"
            Score = $scorePercentage
            Issues = if ($structureStatus.Missing.Count -gt 0) { 
                @("Structure incomplète: $($structureStatus.Missing.Count) éléments manquants")
            } else { @() }
        }
        
    } catch {
        Write-Error "Erreur analyse DocuSense: $($_.Exception.Message)"
        $Results["DocSenseSpecific"] = @{
            Score = 0
            Error = $_.Exception.Message
        }
    }
    
    return $aiContext
}
