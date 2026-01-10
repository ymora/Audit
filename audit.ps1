# ===============================================================================
# SYSTÈME D'AUDIT OTT v2.0 - ARCHITECTURE RECONÇUE
# ===============================================================================

param(
    [string]$Target = "project",  # project, file, directory
    [string]$Path = "",           # Chemin spécifique pour file/directory
    [string]$Phases = "all",      # all, ou liste: "1,2,3"
    [switch]$Verbose = $true,    # Verbose par défaut pour voir l'exécution
    [switch]$Quiet = $false
)

$allowedTargets = @("project", "file", "directory")
if ($allowedTargets -notcontains $Target) {
    if (-not [string]::IsNullOrWhiteSpace($Target) -and [string]::IsNullOrWhiteSpace($Path) -and (Test-Path $Target)) {
        $Path = $Target
        $item = Get-Item -LiteralPath $Path -ErrorAction Stop
        $Target = if ($item.PSIsContainer) { "directory" } else { "file" }
    } elseif ([string]::IsNullOrWhiteSpace($Target) -and -not [string]::IsNullOrWhiteSpace($Path) -and (Test-Path $Path)) {
        $item = Get-Item -LiteralPath $Path -ErrorAction Stop
        $Target = if ($item.PSIsContainer) { "directory" } else { "file" }
    } else {
        throw "Paramètre -Target invalide: '$Target'. Valeurs possibles: project, file, directory. Exemple: .\\audit.ps1 -Target directory -Path 'C:\\Projet'"
    }
 }

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
try { & chcp 65001 > $null } catch { }
$global:OutputEncoding = [System.Text.Encoding]::UTF8

# Configuration
$script:Config = @{
    Version = "2.0.0"
    ProjectRoot = ""
    OutputDir = (Join-Path $PSScriptRoot "resultats")
    Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    ProjectName = ""  # Sera rempli automatiquement
}

$script:AuditConfig = $null
$script:Results = $null
$script:ProjectInfo = $null
$script:Files = @()

$script:Verbose = [bool]$Verbose
$script:Quiet = [bool]$Quiet

# Forcer l'affichage si verbose est demandé
if ($script:Verbose) { $script:Quiet = $false }

$utilsPath = Join-Path $PSScriptRoot "modules\Utils.ps1"
if (Test-Path $utilsPath) { . $utilsPath }
$fileScannerPath = Join-Path $PSScriptRoot "modules\FileScanner.ps1"
if (Test-Path $fileScannerPath) { . $fileScannerPath }
$moduleLoaderPath = Join-Path $PSScriptRoot "modules\ModuleLoader.ps1"
if (Test-Path $moduleLoaderPath) { . $moduleLoaderPath }
$simpleProjectDetectorPath = Join-Path $PSScriptRoot "modules\SimpleProjectDetector.ps1"
if (Test-Path $simpleProjectDetectorPath) { . $simpleProjectDetectorPath }
$simpleModuleRunnerPath = Join-Path $PSScriptRoot "modules\SimpleModuleRunner.ps1"
if (Test-Path $simpleModuleRunnerPath) { . $simpleModuleRunnerPath }
$ultraSimpleModuleRunnerPath = Join-Path $PSScriptRoot "modules\UltraSimpleModuleRunner.ps1"
if (Test-Path $ultraSimpleModuleRunnerPath) { . $ultraSimpleModuleRunnerPath }

# Définition des phases avec dépendances et ordre logique
$script:AuditPhases = @(
    # PHASE 1: STRUCTURE DE BASE (fondation)
    @{
        Id = 1
        Name = "Inventaire Complet"
        Description = "Analyse de tous les fichiers et répertoires"
        Category = "Structure"
        Dependencies = @()
        Priority = 1
        Modules = @("Checks-ProjectInventory.ps1")
        Target = "project"
    },
    
    # PHASE 2: ARCHITECTURE (dépend de l'inventaire)
    @{
        Id = 2
        Name = "Architecture Projet"
        Description = "Structure, organisation, dépendances"
        Category = "Structure"
        Dependencies = @(1)
        Priority = 2
        Modules = @("Checks-Architecture.ps1", "Checks-Organization.ps1")
        Target = "project"
    },
    
    # PHASE 3: SÉCURITÉ (critique, dépend de la structure)
    @{
        Id = 3
        Name = "Sécurité"
        Description = "Vulnérabilités, secrets, injections"
        Category = "Sécurité"
        Dependencies = @(1, 2)
        Priority = 3
        Modules = @("Checks-Security.ps1")
        Target = "project"
    },
    
    # PHASE 4: CONFIGURATION (cohérence environnement)
    @{
        Id = 4
        Name = "Configuration"
        Description = "Docker, environnement, cohérence"
        Category = "Configuration"
        Dependencies = @(1)
        Priority = 4
        Modules = @("Checks-ConfigConsistency.ps1")
        Target = "project"
    },
    
    # PHASE 5: BACKEND (API et base de données)
    @{
        Id = 5
        Name = "Backend API"
        Description = "Endpoints, handlers, base de données"
        Category = "Backend"
        Dependencies = @(1, 2)
        Priority = 5
        Modules = @("Checks-API.ps1", "Checks-StructureAPI.ps1", "Checks-Database.ps1")
        Target = "project"
    },
    
    # PHASE 6: FRONTEND (interface utilisateur)
    @{
        Id = 6
        Name = "Frontend"
        Description = "Routes, navigation, accessibilité"
        Category = "Frontend"
        Dependencies = @(1, 2)
        Priority = 6
        Modules = @("Checks-Routes.ps1", "Checks-UI.ps1")
        Target = "project"
    },
    
    # PHASE 7: QUALITÉ CODE (analyse statique)
    @{
        Id = 7
        Name = "Qualité Code"
        Description = "Code mort, duplication, complexité"
        Category = "Qualité"
        Dependencies = @(1, 2)
        Priority = 7
        Modules = @("Checks-CodeQuality.ps1", "Checks-Duplication.ps1", "Checks-Complexity.ps1")
        Target = "project"
    },
    
    # PHASE 8: PERFORMANCE
    @{
        Id = 8
        Name = "Performance"
        Description = "Optimisations, mémoire, vitesse"
        Category = "Performance"
        Dependencies = @(1, 2, 5, 6)
        Priority = 8
        Modules = @("Checks-Performance.ps1", "Checks-Optimizations.ps1")
        Target = "project"
    },
    
    # PHASE 9: DOCUMENTATION
    @{
        Id = 9
        Name = "Documentation"
        Description = "README, commentaires, guides"
        Category = "Documentation"
        Dependencies = @(1, 2)
        Priority = 9
        Modules = @("Checks-Documentation.ps1", "Checks-MarkdownQuality.ps1")
        Target = "project"
    },
    
    # PHASE 10: TESTS
    @{
        Id = 10
        Name = "Tests"
        Description = "Tests unitaires, intégration, fonctionnels"
        Category = "Tests"
        Dependencies = @(1, 2, 5)
        Priority = 10
        Modules = @("Checks-TestCoverage.ps1", "Checks-FunctionalTests-Placeholder.ps1")
        Target = "project"
    },
    
    # PHASE 11: DÉPLOIEMENT
    @{
        Id = 11
        Name = "Déploiement"
        Description = "CI/CD, GitHub Pages, configuration et chemins de déploiement"
        Category = "Déploiement"
        Dependencies = @(1, 4)
        Priority = 11
        Modules = @("Checks-Deployment-Paths.ps1")
        Target = "project"
    },
    
    # PHASE 12: HARDWARE/FIRMWARE
    @{
        Id = 12
        Name = "Hardware/Firmware"
        Description = "Arduino, compilation, cohérence"
        Category = "Hardware"
        Dependencies = @(1)
        Priority = 12
        Modules = @("Checks-HardwareFirmware.ps1")
        Target = "project"
    },
    
    # PHASE 13: IA et Compléments
    @{
        Id = 13
        Name = "IA et Compléments"
        Description = "Tests exhaustifs, IA, suivi temps"
        Category = "IA"
        Dependencies = @(1, 2, 5, 10)
        Priority = 13
        Modules = @("Checks-FunctionalTests.ps1", "Checks-TestsComplets.ps1", "Checks-TimeTracking.ps1", "AI-TestsComplets.ps1")
        Target = "project"
        ProjectSpecific = @()  # Plus de restriction - disponible pour tous les projets
    },
    
    # PHASE 15: INTELLIGENCE DU DOMAINE (nouvelle phase intelligente)
    @{
        Id = 15
        Name = "Intelligence du Domaine"
        Description = "Évalue l'intelligence du domaine métier et l'expertise thématique"
        Category = "Intelligence"
        Dependencies = @(1, 2)
        Priority = 15
        Modules = @("Checks-DomainIntelligence.ps1")
        Target = "project"
        ProjectSpecific = @("haies")  # Phase spécifique aux projets avec expertise
    },
    
    # PHASE 16: ARCHITECTURE INTELLIGENTE (nouvelle phase intelligente)
    @{
        Id = 16
        Name = "Architecture Intelligente"
        Description = "Évalue l'intelligence de l'architecture et les choix techniques"
        Category = "Intelligence"
        Dependencies = @(1, 2)
        Priority = 16
        Modules = @("Checks-SmartArchitecture.ps1")
        Target = "project"
        ProjectSpecific = @("haies")
    },
    
    # PHASE 17: INTELLIGENCE UTILISATEUR (nouvelle phase intelligente)
    @{
        Id = 17
        Name = "Intelligence Utilisateur"
        Description = "Évalue l'intelligence de l'interface utilisateur et l'expérience"
        Category = "Intelligence"
        Dependencies = @(1, 2)
        Priority = 17
        Modules = @("Checks-UserIntelligence.ps1")
        Target = "project"
        ProjectSpecific = @("haies")
    },
    
    # PHASE 18: INTELLIGENCE ÉCOLOGIQUE (nouvelle phase intelligente)
    @{
        Id = 18
        Name = "Intelligence Écologique"
        Description = "Évalue l'intelligence écologique et la vision durable"
        Category = "Intelligence"
        Dependencies = @(1, 2)
        Priority = 18
        Modules = @("Checks-EcologicalIntelligence.ps1")
        Target = "project"
        ProjectSpecific = @("haies")
    },
    
    # PHASE 19: INTELLIGENCE DOCUMENTAIRE (nouvelle phase intelligente)
    @{
        Id = 19
        Name = "Intelligence Documentaire"
        Description = "Évalue l'intelligence de la documentation et la transmission du savoir"
        Category = "Intelligence"
        Dependencies = @(1, 2)
        Priority = 19
        Modules = @("Checks-DocumentationIntelligence.ps1")
        Target = "project"
        ProjectSpecific = @("haies")
    },
    
    # PHASE 14: QUESTIONS IA (cas ambigus à déléguer à l'IA)
    @{
        Id = 14
        Name = "Questions IA"
        Description = "Génère des questions ciblées pour l'IA sur les cas ambigus"
        Category = "IA"
        Dependencies = @(1, 2, 7)
        Priority = 14
        Modules = @("AI-QuestionGenerator.ps1")
        Target = "project"
    }
)

# Fonctions utilitaires
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [switch]$NoNewline
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $prefix = "[$timestamp] [$Level]"
    
    if ($NoNewline) {
        Write-Host "$prefix $Message" -NoNewline
    } else {
        Write-Host "$prefix $Message"
    }
}

function Remove-OldAuditResults {
    <#
    .SYNOPSIS
        Nettoie automatiquement les anciens résultats d'audit en ne conservant que les N plus récents
    .DESCRIPTION
        Supprime les anciens fichiers d'audit JSON en ne conservant que le nombre configuré d'audits les plus récents
        S'exécute uniquement si l'audit actuel s'est terminé avec succès
    .PARAMETER OutputDir
        Répertoire contenant les résultats d'audit
    .PARAMETER KeepCount
        Nombre d'audits à conserver (défaut: 3)
    #>
    param(
        [string]$OutputDir,
        [int]$KeepCount = 3
    )
    
    try {
        Write-Log "Nettoyage automatique des anciens audits..." "INFO"
        
        # Récupérer tous les fichiers audit_summary_*.json
        $auditFiles = Get-ChildItem -Path $OutputDir -Filter "audit_summary_*.json" | Sort-Object Name -Descending
        
        if ($auditFiles.Count -le $KeepCount) {
            Write-Log "Nettoyage non nécessaire: $($auditFiles.Count) fichiers trouvés, conservation des $KeepCount plus récents" "INFO"
            return
        }
        
        # Supprimer les fichiers les plus anciens
        $filesToDelete = $auditFiles | Select-Object -Skip $KeepCount
        $deletedCount = 0
        
        foreach ($file in $filesToDelete) {
            try {
                Remove-Item -Path $file.FullName -Force
                $deletedCount++
                Write-Log "Supprimé: $($file.Name)" "INFO"
            } catch {
                Write-Log "Erreur lors de la suppression de $($file.Name): $($_.Exception.Message)" "WARN"
            }
        }
        
        if ($deletedCount -gt 0) {
            Write-Log "Nettoyage terminé: $deletedCount ancien(s) audit(s) supprimé(s)" "SUCCESS"
        }
        
        # Nettoyer aussi les fichiers de phase associés
        $phaseFiles = Get-ChildItem -Path $OutputDir -Filter "phase_*.json" | Sort-Object Name -Descending
        if ($phaseFiles.Count -gt 0) {
            # Regrouper les fichiers de phase par timestamp et garder uniquement ceux des audits conservés
            $keptTimestamps = $auditFiles | Select-Object -First $KeepCount | ForEach-Object {
                if ($_.Name -match 'audit_summary_(\d{8}_\d{6})\.json') {
                    return $matches[1]
                }
            }
            
            $phaseFilesToDelete = $phaseFiles | Where-Object {
                if ($_.Name -match 'phase_\d+_(\d{8}_\d{6})\.json') {
                    $timestamp = $matches[1]
                    return $timestamp -notin $keptTimestamps
                }
                return $false
            }
            
            $deletedPhaseCount = 0
            foreach ($file in $phaseFilesToDelete) {
                try {
                    Remove-Item -Path $file.FullName -Force
                    $deletedPhaseCount++
                } catch {
                    Write-Log "Erreur lors de la suppression du fichier de phase $($file.Name): $($_.Exception.Message)" "WARN"
                }
            }
            
            if ($deletedPhaseCount -gt 0) {
                Write-Log "Nettoyage des phases: $deletedPhaseCount fichier(s) de phase supprimé(s)" "SUCCESS"
            }
        }
        
    } catch {
        Write-Log "Erreur lors du nettoyage automatique: $($_.Exception.Message)" "ERROR"
    }
}

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [switch]$NoNewline,
        [switch]$NoTimestamp
    )
    
    if ($script:Quiet -and $Level -notin @("PHASE", "SUCCESS", "ERROR", "MODULE", "PROGRESS")) { return }

    $prefix = if (-not $NoTimestamp) { "[$(Get-Date -Format 'HH:mm:ss')]" } else { "" }
    
    switch ($Level) {
        "INFO" { Write-Host "$prefix [INFO] $Message" -ForegroundColor White }
        "SUCCESS" { Write-Host "$prefix [SUCCESS] $Message" -ForegroundColor Green }
        "WARN" { Write-Host "$prefix [WARN] $Message" -ForegroundColor Yellow }
        "ERROR" { Write-Host "$prefix [ERROR] $Message" -ForegroundColor Red }
        "PHASE" { Write-Host "$prefix [PHASE] $Message" -ForegroundColor Cyan }
        "MODULE" { Write-Host "$prefix [MODULE] $Message" -ForegroundColor Magenta }
        "DETAIL" { Write-Host "$prefix [DETAIL] $Message" -ForegroundColor Gray }
        "PROGRESS" { Write-Host "$prefix [PROGRESS] $Message" -ForegroundColor Blue }
        default { Write-Host "$prefix [$Level] $Message" }
    }
}

function Write-PhaseHeader {
    param([int]$PhaseId, [string]$PhaseName, [string]$Description, [int]$ModuleCount)
    Write-Log "=== Phase $PhaseId : $PhaseName ===" "PHASE" -NoTimestamp
    Write-Log "Description: $Description" "DETAIL"
    Write-Log "Modules à exécuter: $ModuleCount" "DETAIL"
    if ($script:ProjectProfile) {
        Write-Log "Projet détecté: $($script:ProjectProfile.Id)" "DETAIL"
    }
}

function Write-ModuleStart {
    param([string]$ModuleName, [string]$ModulePath)
    Write-Log "Démarrage: $ModuleName" "MODULE"
    if ($Verbose) {
        Write-Log "  Chemin: $ModulePath" "DETAIL"
    }
}

function Write-ModuleResult {
    param([string]$ModuleName, [string]$Status, [timespan]$Duration, [int]$Issues = 0)
    $statusIcon = switch ($Status) {
        "SUCCESS" { "[OK]" }
        "WARNING" { "[WARN]" }
        "ERROR" { "[ERR]" }
        "SKIPPED" { "[SKIP]" }
        default { "[?]" }
    }
    $issuesText = if ($Issues -gt 0) { " ($Issues issues)" } else { "" }
    Write-Log "$statusIcon $ModuleName termine en $([math]::Round($Duration.TotalSeconds, 2))s$issuesText" "MODULE"
}

function Write-PhaseSummary {
    param([int]$PhaseId, [string]$PhaseName, [timespan]$TotalDuration, [hashtable]$Results)
    $successCount = ($Results.Values | Where-Object { $_.Status -eq "SUCCESS" }).Count
    $warningCount = ($Results.Values | Where-Object { $_.Status -eq "WARNING" }).Count
    $errorCount = ($Results.Values | Where-Object { $_.Status -eq "ERROR" }).Count
    
    Write-Log "Phase $PhaseId terminee en $([math]::Round($TotalDuration.TotalSeconds, 2))s" "SUCCESS"
    if ($warningCount -gt 0 -or $errorCount -gt 0) {
        Write-Log "  Resume: $successCount succes, $warningCount avertissements, $errorCount erreurs" "DETAIL"
    }
    Write-Log "Resultats: $($script:Config.OutputDir)\phase_$PhaseId`_$($script:Config.Timestamp).json" "DETAIL"
}

function Import-AuditDependencies {
    $utilsPath = Join-Path $PSScriptRoot "modules\Utils.ps1"
    if (Test-Path $utilsPath) {
        . $utilsPath
    }

    $fileScannerPath = Join-Path $PSScriptRoot "modules\FileScanner.ps1"
    if (Test-Path $fileScannerPath) {
        . $fileScannerPath
    }

    $projectDetectorPath = Join-Path $PSScriptRoot "modules\ProjectDetector.ps1"
    if (Test-Path $projectDetectorPath) {
        . $projectDetectorPath
    }
}

function Get-ProjectProfile {
    param(
        [Parameter(Mandatory=$true)][string]$ProjectRoot
    )

    $projectsDir = Join-Path $PSScriptRoot "projects"
    if (-not (Test-Path $projectsDir)) { return $null }

    $best = $null
    $bestScore = -1

    $projectFiles = Get-ChildItem -Path $projectsDir -Filter "project.ps1" -Recurse -File -ErrorAction SilentlyContinue
    foreach ($file in $projectFiles) {
        try {
            $projProfile = . $file.FullName
            if (-not ($projProfile -is [hashtable])) { continue }
            if (-not $projProfile.ContainsKey('Id')) { continue }
            if (-not $projProfile.ContainsKey('Detect')) { continue }

            $detect = $projProfile.Detect
            $score = 0
            if ($detect -is [scriptblock]) {
                $score = & $detect $ProjectRoot
            }

            $projProfile.Score = $score

            if ($score -gt $bestScore) {
                $bestScore = $score
                $best = $projProfile
                $best.ProjectFile = $file.FullName
            }
        } catch {
        }
    }

    if ($bestScore -le 0) { return $null }
    $best.Score = $bestScore
    return $best
}

function Merge-Hashtable {
    param(
        [Parameter(Mandatory=$true)][hashtable]$Base,
        [Parameter(Mandatory=$true)][hashtable]$Override
    )

    $merged = $Base.Clone()
    foreach ($key in $Override.Keys) {
        if ($merged.ContainsKey($key) -and ($merged[$key] -is [hashtable]) -and ($Override[$key] -is [hashtable])) {
            $merged[$key] = Merge-Hashtable -Base $merged[$key] -Override $Override[$key]
        } elseif ($merged.ContainsKey($key) -and ($merged[$key] -is [array]) -and ($Override[$key] -is [array])) {
            $merged[$key] = @($merged[$key] + $Override[$key])
        } else {
            $merged[$key] = $Override[$key]
        }
    }
    return $merged
}

function Load-AuditConfig {
    $base = @{
        Exclude = @{
            Directories = @()
            Files = @()
        }
        Checks = @{ }
    }

    $configPath = Join-Path $PSScriptRoot "config\audit.config.ps1"
    if (Test-Path $configPath) {
        try {
            $cfg = . $configPath
            if ($cfg -is [hashtable]) {
                $base = Merge-Hashtable -Base $base -Override $cfg
            }
        } catch {
            Write-Log "Erreur chargement config globale: $($_.Exception.Message)" "WARN"
        }
    }

    $configLocalPath = Join-Path $PSScriptRoot "config\audit.config.local.ps1"
    if (Test-Path $configLocalPath) {
        try {
            $cfgLocal = . $configLocalPath
            if ($cfgLocal -is [hashtable]) {
                $base = Merge-Hashtable -Base $base -Override $cfgLocal
            }
        } catch {
            Write-Log "Erreur chargement config locale: $($_.Exception.Message)" "WARN"
        }
    }

    # Détecter le projet et charger la configuration
    Write-Log "Détection du projet..." "INFO"
    
    # Utiliser une détection simple pour OTT
    $projectRoot = $script:Config.ProjectRoot
    $projectName = $projectRoot.Split('\')[-1]
    
    # Configuration simple pour OTT
    if ($projectName -eq "OTT" -or (Test-Path (Join-Path $projectRoot "api.php"))) {
        $script:ProjectInfo = @{
            Name = "ott"
            Type = "web"
            Framework = "php"
            Profile = @{ Score = 8 }
        }
        Write-Log "Projet détecté: ott (application web PHP)" "SUCCESS"
    } else {
        # Fallback sur l'ancien système si disponible
        if (Get-Command Get-ProjectInfo -ErrorAction SilentlyContinue) {
            try {
                $projectInfoResult = Get-ProjectInfo -Path $script:Config.ProjectRoot
                $script:ProjectInfo = if ($projectInfoResult -is [hashtable]) { $projectInfoResult } else { @{ } }
                $script:ProjectProfile = $script:ProjectInfo.Profile
                $projectId = $script:ProjectInfo.Name
                Write-Log "Projet détecté: $projectId (score: $($script:ProjectProfile.Score))" "SUCCESS"
                
                # Charger la configuration spécifique au projet
                $script:AuditConfig = $script:ProjectInfo.Configuration
            } catch {
                Write-Log "Erreur détection projet: $($_.Exception.Message)" "WARN"
                $script:ProjectInfo = @{ Name = "unknown" }
                $script:ProjectProfile = $null
                $script:AuditConfig = Get-DefaultAuditConfig
            }
        } else {
            Write-Log "Aucun détecteur de projet disponible, utilisation configuration par défaut" "WARN"
            $script:ProjectInfo = @{ Name = "unknown" }
            $script:ProjectProfile = $null
            $script:AuditConfig = Get-DefaultAuditConfig
        }
    }

    return $base
}

function Resolve-AuditModulePath {
    param(
        [Parameter(Mandatory=$true)][string]$Module,
        [string]$ProjectName = ""
    )

    # Utiliser le nouveau système de chargement de modules
    return Get-ModulePath -ModuleName $Module -ProjectName $ProjectName -BasePath (Join-Path $PSScriptRoot "modules")
}

function Resolve-TargetRoot {
    if ($Target -eq "project") {
        if (-not [string]::IsNullOrWhiteSpace($Path)) {
            if (-not (Test-Path $Path)) {
                throw "Chemin introuvable: $Path"
            }
            $resolved = (Resolve-Path $Path -ErrorAction Stop).Path
            $item = Get-Item -LiteralPath $resolved -ErrorAction Stop
            if ($item.PSIsContainer) { 
                return $item.FullName 
            } else { 
                return $item.Directory.FullName 
            }
        }

        $workspaceRoot = Split-Path -Parent $PSScriptRoot

        $siblingDirs = @(Get-ChildItem -Path $workspaceRoot -Directory -ErrorAction SilentlyContinue | Where-Object {
            $_.Name -ne (Split-Path -Leaf $PSScriptRoot) -and $_.Name -notmatch '^\.'
        })

        $detected = @()
        foreach ($dir in $siblingDirs) {
            try {
                $projProfile = Get-ProjectProfile -ProjectRoot $dir.FullName
                if ($projProfile) {
                    $detected += [pscustomobject]@{
                        Path = $dir.FullName
                        Id = $projProfile.Id
                        Score = [int]$projProfile.Score
                    }
                }
            } catch {
            }
        }

        if ($detected.Count -eq 0) {
            return $workspaceRoot
        }

        $bestScore = ($detected | Measure-Object -Property Score -Maximum).Maximum
        $best = @($detected | Where-Object { $_.Score -eq $bestScore } | Sort-Object Id, Path)
        if ($best.Count -eq 1 -or $Quiet) {
            return $best[0].Path
        }

        Write-Host "Plusieurs projets détectés. Sélectionner le projet à auditer:" -ForegroundColor Yellow
        for ($i = 0; $i -lt $best.Count; $i++) {
            Write-Host ("  [" + ($i + 1) + "] " + $best[$i].Id + " (score: " + $best[$i].Score + ") - " + $best[$i].Path) -ForegroundColor Gray
        }
        $choice = Read-Host "Choix [1]"
        if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "1" }
        $idx = ([int]$choice) - 1
        if ($idx -lt 0 -or $idx -ge $best.Count) {
            throw "Choix invalide: $choice"
        }
        return $best[$idx].Path
    }
    if ([string]::IsNullOrWhiteSpace($Path)) {
        throw "Le paramÃ¨tre -Path est requis pour Target=$Target"
    }
    if (-not (Test-Path $Path)) {
        throw "Chemin introuvable: $Path"
    }
    $resolved = (Resolve-Path $Path -ErrorAction Stop).Path
    $item = Get-Item $resolved -ErrorAction Stop
    if ($Target -eq "file") {
        return $item.Directory.FullName
    }
    if ($Target -eq "directory") {
        return $item.FullName
    }
    return (Get-Location).Path
}

function Initialize-AuditContext {
    $script:Verbose = [bool]$Verbose

    $script:AuditConfig = Load-AuditConfig

    if (Get-Command Get-ProjectInfo -ErrorAction SilentlyContinue) {
        try {
            $script:ProjectInfo = Get-ProjectInfo -Path $script:Config.ProjectRoot
        } catch {
            $script:ProjectInfo = @{ }
        }
    } else {
        $script:ProjectInfo = @{ }
    }

    # Déterminer le nom du projet et créer le répertoire de sortie
    $projectName = if ($script:ProjectInfo.Name) { $script:ProjectInfo.Name } else { 
        $script:Config.ProjectRoot.Split('\')[-1] 
    }
    $script:Config.ProjectName = $projectName -replace '[^a-zA-Z0-9_-]', '_'
    
    # Créer le répertoire de sortie par projet
    $projectOutputDir = Join-Path $script:Config.OutputDir $script:Config.ProjectName
    if (-not (Test-Path $projectOutputDir)) {
        New-Item -ItemType Directory -Path $projectOutputDir -Force | Out-Null
    }
    $script:Config.OutputDir = $projectOutputDir

    $script:Results = @{
        StartTime = Get-Date
        Scores = @{}
        Issues = @()
        Warnings = @()
        Recommendations = @()
        Stats = @{}
        Statistics = @{}
        API = @{}
        AIContext = @{}
    }

    Write-Log "Collecte des fichiers du projet en cours..." "INFO"
    $collectedFiles = @()
    if ($Target -eq "file") {
        $collectedFiles = @((Get-Item $Path -ErrorAction Stop))
    } elseif (Get-Command Get-ProjectFiles -ErrorAction SilentlyContinue) {
        $collectedFiles = @(Get-ProjectFiles -Path $script:Config.ProjectRoot -Config $script:AuditConfig)
    } else {
        $collectedFiles = @(Get-ChildItem -Path $script:Config.ProjectRoot -Recurse -File -ErrorAction SilentlyContinue)
    }
    $script:Files = $collectedFiles
    Write-Log "Fichiers collectés : $($collectedFiles.Count)" "INFO"
}

function Invoke-AuditModule {
    param(
        [Parameter(Mandatory=$true)][string]$Module,
        [string]$ProjectName = ""
    )

    # Utiliser le système ultra-simple qui fonctionne
    $result = Invoke-AuditModuleUltraSimple -Module $Module -ProjectName $ProjectName
    
    return $result
}

function Test-ModuleExists {
    param([string]$ModuleName)
    $modulePath = Resolve-AuditModulePath -Module $ModuleName
    return Test-Path $modulePath
}

function Get-PhaseDependencies {
    param([int]$PhaseId, [hashtable]$Visited = @{ })

    if ($Visited.ContainsKey($PhaseId)) {
        return @()
    }

    $phase = $script:AuditPhases | Where-Object { $_.Id -eq $PhaseId }
    if (-not $phase) {
        return @()
    }

    $Visited[$PhaseId] = $true
    $allDeps = @()

    foreach ($depId in $phase.Dependencies) {
        $allDeps += Get-PhaseDependencies -PhaseId $depId -Visited $Visited
        $allDeps += $depId
    }

    return ($allDeps | Sort-Object -Unique)
}

function Resolve-PhaseExecution {
    param([array]$RequestedPhases)

    $allPhases = @()
    foreach ($phaseId in $RequestedPhases) {
        $deps = Get-PhaseDependencies -PhaseId $phaseId
        foreach ($dep in $deps) {
            if ($allPhases -notcontains $dep) {
                $allPhases += $dep
            }
        }
        if ($allPhases -notcontains $phaseId) {
            $allPhases += $phaseId
        }
    }

    # Filtrer les phases spÃ©cifiques projet si non dÃ©tectÃ©
    $availablePhases = @()
    foreach ($phaseId in $allPhases) {
        $phase = $script:AuditPhases | Where-Object { $_.Id -eq $phaseId }
        if ($phase -and $phase.ProjectSpecific) {
            # Phase spÃ©cifique projet : vÃ©rifier si le projet dÃ©tectÃ© est autorisÃ©
            if ($script:ProjectProfile -and $phase.ProjectSpecific -contains $script:ProjectProfile.Id) {
                $availablePhases += $phaseId
            }
            # Sinon, ignorer cette phase
        } else {
            # Phase gÃ©nÃ©rique : toujours inclure
            $availablePhases += $phaseId
        }
    }

    # Trier par prioritÃ© en respectant les dÃ©pendances (tri topologique)
    $sortedPhases = @()
    $processed = @{}
    
    # Tri topologique : traiter les phases dans l'ordre de prioritÃ©, mais seulement si leurs dÃ©pendances sont dÃ©jÃ  traitÃ©es
    $remainingPhases = $availablePhases | ForEach-Object { $_ }
    while ($remainingPhases.Count -gt 0) {
        $found = $false
        # Parcourir les phases par ordre de prioritÃ©
        foreach ($phase in $script:AuditPhases | Sort-Object Priority, Id) {
            if ($remainingPhases -contains $phase.Id) {
                # VÃ©rifier si toutes les dÃ©pendances sont traitÃ©es
                $allDepsProcessed = $true
                foreach ($depId in $phase.Dependencies) {
                    if ($availablePhases -contains $depId -and -not $processed.ContainsKey($depId)) {
                        $allDepsProcessed = $false
                        break
                    }
                }
                
                if ($allDepsProcessed) {
                    $sortedPhases += $phase.Id
                    $processed[$phase.Id] = $true
                    $remainingPhases = $remainingPhases | Where-Object { $_ -ne $phase.Id }
                    $found = $true
                    break
                }
            }
        }
        if (-not $found) {
            # Si aucune phase ne peut Ãªtre traitÃ©e (cycle de dÃ©pendances), prendre la suivante par prioritÃ©
            $nextPhase = $script:AuditPhases | Where-Object { $remainingPhases -contains $_.Id } | Sort-Object Priority, Id | Select-Object -First 1
            if ($nextPhase) {
                $sortedPhases += $nextPhase.Id
                $processed[$nextPhase.Id] = $true
                $remainingPhases = $remainingPhases | Where-Object { $_ -ne $nextPhase.Id }
            } else {
                break
            }
        }
    }

    # VÃ©rifier que l'ordre est correct (debug)
    if ($script:Verbose) {
        Write-Log "Ordre des phases aprÃ¨s tri topologique: $($sortedPhases -join ', ')" "DETAIL"
    }

    return $sortedPhases
}

function Invoke-InteractiveMenu {
    Write-Host "" 
    Write-Host "==============================" -ForegroundColor Cyan
    Write-Host "Menu Audit" -ForegroundColor Cyan
    Write-Host "==============================" -ForegroundColor Cyan

    $targetChoice = Read-Host "Cible (1=projet, 2=fichier, 3=repertoire) [1]"
    if ([string]::IsNullOrWhiteSpace($targetChoice)) { $targetChoice = "1" }

    switch ($targetChoice) {
        "2" { $script:Target = "file" }
        "3" { $script:Target = "directory" }
        default { $script:Target = "project" }
    }

    if ($script:Target -ne "project") {
        $p = Read-Host "Chemin (relatif ou absolu)"
        if ([string]::IsNullOrWhiteSpace($p)) {
            throw "Chemin requis pour Target=$script:Target"
        }
        $script:Path = $p
    }

    Write-Host "" 
    Write-Host "Phases disponibles:" -ForegroundColor Gray
    # Trier par Priority puis Id pour garantir l'ordre correct (synchronisé avec l'exécution)
    # Forcer le tri numérique explicite pour éviter les problèmes de type
    $sortedPhases = $script:AuditPhases | Sort-Object @{Expression={[int]$_.Priority}}, @{Expression={[int]$_.Id}}
    foreach ($ph in $sortedPhases) {
        Write-Host ("  " + $ph.Id + " - " + $ph.Name) -ForegroundColor Gray
    }

    $phasesChoice = Read-Host "Phases (all ou liste ex: 1,2,3) [all]"
    if ([string]::IsNullOrWhiteSpace($phasesChoice)) { $phasesChoice = "all" }
    $script:Phases = $phasesChoice

    $verboseChoice = Read-Host "Verbose ? (o/n) [n]"
    $script:Verbose = ($verboseChoice -match '^(o|oui|y|yes)$')

    $quietChoice = Read-Host "Silencieux ? (o/n) [n]"
    $script:Quiet = ($quietChoice -match '^(o|oui|y|yes)$')

    Write-Host "" 
    Write-Host "RÃ©sumÃ©:" -ForegroundColor Cyan
    Write-Host ("  Target: " + $script:Target) -ForegroundColor Cyan
    if ($script:Target -ne "project") {
        Write-Host ("  Path: " + $script:Path) -ForegroundColor Cyan
    }
    Write-Host ("  Phases: " + $script:Phases) -ForegroundColor Cyan
    Write-Host ("  Verbose: " + [bool]$script:Verbose) -ForegroundColor Cyan
    Write-Host ("  Quiet: " + [bool]$script:Quiet) -ForegroundColor Cyan

    $confirm = Read-Host "Lancer l'audit ? (o/n) [o]"
    if ([string]::IsNullOrWhiteSpace($confirm)) { $confirm = "o" }
    if ($confirm -notmatch '^(o|oui|y|yes)$') {
        Write-Host "Audit annulÃ©." -ForegroundColor Yellow
        exit 0
    }
}

function Initialize-AuditEnvironment {
    Write-Log "Initialisation de l'environnement d'audit..." "INFO"

    $script:Config.ProjectRoot = Resolve-TargetRoot

    $script:OriginalLocation = (Get-Location).Path

    try {
        Push-Location -Path $script:Config.ProjectRoot
    } catch {
        throw "Impossible de se placer dans le rÃ©pertoire projet '$($script:Config.ProjectRoot)': $($_.Exception.Message)"
    }

    # CrÃ©ation du rÃ©pertoire de rÃ©sultats
    if (-not (Test-Path $script:Config.OutputDir)) {
        New-Item -ItemType Directory -Path $script:Config.OutputDir -Force | Out-Null
        Write-Log "CrÃ©ation du rÃ©pertoire de rÃ©sultats: $($script:Config.OutputDir)" "INFO"
    }

    Write-Log "Projet: $($script:Config.ProjectRoot)" "SUCCESS"
    Write-Log "Cible: $Target" "INFO"

    Import-AuditDependencies
    Initialize-AuditContext

    $projectDisplayName = $null
    if ($script:AuditConfig -and $script:AuditConfig.Project -and $script:AuditConfig.Project.Name) {
        $projectDisplayName = $script:AuditConfig.Project.Name
    } elseif ($script:ProjectInfo -and $script:ProjectInfo.Name) {
        $projectDisplayName = $script:ProjectInfo.Name
    } elseif ($script:Config.ProjectName) {
        $projectDisplayName = $script:Config.ProjectName
    }

    if (-not [string]::IsNullOrWhiteSpace($projectDisplayName)) {
        $idText = if ($script:ProjectProfile -and $script:ProjectProfile.Id) { " (id: $($script:ProjectProfile.Id))" } else { "" }
        Write-Log "Projet en cours: $projectDisplayName$idText" "SUCCESS"
    }
}

function Execute-Phase {
    param([object]$Phase, [string]$ProjectName = "")

    $phaseStartTime = Get-Date
    Write-PhaseHeader -PhaseId $Phase.Id -PhaseName $Phase.Name -Description $Phase.Description -ModuleCount $Phase.Modules.Count

    if ($Phase.Dependencies.Count -gt 0) {
        Write-Log "DÃ©pendances: $($Phase.Dependencies -join ', ')" "DETAIL"
    }

    $results = @{}
    $moduleIndex = 0
    
    foreach ($module in $Phase.Modules) {
        $moduleIndex++
        
        Write-ModuleStart -ModuleName $module -ModulePath $module
        Write-Log "[$moduleIndex/$($Phase.Modules.Count)] ExÃ©cution en cours..." "PROGRESS"

        try {
            $sw = [System.Diagnostics.Stopwatch]::StartNew()
            $moduleResult = Invoke-AuditModule -Module $module -ProjectName $ProjectName
            $sw.Stop()
            
            # Adapter le résultat au format attendu
            $status = if ($moduleResult.Error) { 
                "ERROR"
            } elseif ($moduleResult.Errors -gt 0) { 
                "WARNING"
            } else {
                "SUCCESS"
            }
            
            $issues = if ($moduleResult.Errors) { $moduleResult.Errors } else { 0 }
            if ($moduleResult.Warnings) { $issues += $moduleResult.Warnings }
            
            $results[$module] = @{
                Status = $status
                Duration = $sw.Elapsed
                DurationMs = $sw.ElapsedMilliseconds
                Timestamp = Get-Date
                Issues = $issues
                Errors = if ($moduleResult.Errors) { $moduleResult.Errors } else { 0 }
                Warnings = if ($moduleResult.Warnings) { $moduleResult.Warnings } else { 0 }
                Result = $moduleResult
            }
            
            Write-ModuleResult -ModuleName $module -Status $status -Duration $sw.Elapsed -Issues $issues
            
            if ($Verbose -and $issues -gt 0) {
                Write-Log "  DÃ©tail: $($moduleResult.Errors) erreurs, $($moduleResult.Warnings) avertissements" "DETAIL"
            }
            
        } catch {
            $sw.Stop()
            $results[$module] = @{
                Status = "ERROR"
                Duration = $sw.Elapsed
                DurationMs = $sw.ElapsedMilliseconds
                Timestamp = Get-Date
                Issues = 1
                Errors = 1
                Warnings = 0
                Error = $_.Exception.Message
            }
            
            Write-ModuleResult -ModuleName $module -Status "ERROR" -Duration $sw.Elapsed -Issues 1
            Write-Log "  Erreur: $($_.Exception.Message)" "ERROR"
        }
    }

    # Sauvegarde des rÃ©sultats de la phase
    $phaseEndTime = Get-Date
    $totalDuration = $phaseEndTime - $phaseStartTime
    
    $phaseResult = @{
        Phase = $Phase
        Results = $results
        StartTime = $phaseStartTime
        EndTime = $phaseEndTime
        TotalDuration = $totalDuration
        TotalDurationMs = $totalDuration.TotalMilliseconds
        Timestamp = $phaseEndTime
        ModuleCount = $Phase.Modules.Count
        SuccessCount = ($results.Values | Where-Object { $_.Status -eq "SUCCESS" }).Count
        WarningCount = ($results.Values | Where-Object { $_.Status -eq "WARNING" }).Count
        ErrorCount = ($results.Values | Where-Object { $_.Status -eq "ERROR" }).Count
    }

    # DESACTIVE: Plus de fichiers phase_*.json (tout dans AI-SUMMARY.md)
    # $resultFile = Join-Path $script:Config.OutputDir "phase_$($Phase.Id)_$($script:Config.Timestamp).json"
    # $phaseResult | ConvertTo-Json -Depth 10 | Out-File -FilePath $resultFile -Encoding UTF8

    Write-PhaseSummary -PhaseId $Phase.Id -PhaseName $Phase.Name -TotalDuration $totalDuration -Results $results
    return $phaseResult
}

# Programme principal
function Main {
    try {
        Write-Host "================================================================" -ForegroundColor Cyan
        Write-Host "SYSTEME D'AUDIT v$($script:Config.Version)" -ForegroundColor Cyan
        Write-Host "================================================================" -ForegroundColor Cyan

        Initialize-AuditEnvironment

        # RÃ©solution des phases Ã  exÃ©cuter
        $requestedPhases = @()
        if ($Phases -eq "all") {
            # Trier par Priority pour garantir l'ordre correct
            $requestedPhases = $script:AuditPhases | Sort-Object Priority, Id | ForEach-Object { $_.Id }
            Write-Log "Mode: Audit complet (toutes les phases)" "INFO"
        } else {
            $requestedPhases = $Phases -split ',' | ForEach-Object { 
                $num = [int]($_.Trim())
                if ($script:AuditPhases | Where-Object { $_.Id -eq $num }) {
                    $num
                } else {
                    Write-Log "Phase $num invalide, ignorÃ©e" "WARN"
                }
            }
            Write-Log "Mode: Phases sÃ©lectives - $($Phases)" "INFO"
        }

        if ($requestedPhases.Count -eq 0) {
            Write-Log "Aucune phase valide Ã  exÃ©cuter" "ERROR"
            return
        }

        $executionPlan = Resolve-PhaseExecution -RequestedPhases $requestedPhases

        Write-Log "Plan d'exÃ©cution: $($executionPlan -join ', ')" "INFO"
        Write-Log "Nombre de phases: $($executionPlan.Count)" "INFO"
        # VÃ©rifier l'ordre des phases (debug)
        if ($executionPlan.Count -gt 1) {
            $isOrdered = $true
            for ($i = 1; $i -lt $executionPlan.Count; $i++) {
                if ($executionPlan[$i] -lt $executionPlan[$i-1]) {
                    $isOrdered = $false
                    break
                }
            }
            if (-not $isOrdered) {
                Write-Log "⚠️  ATTENTION: L'ordre des phases n'est pas strictement croissant" "WARN"
                Write-Log "   Ordre actuel: $($executionPlan -join ', ')" "WARN"
            }
        }
        
        if ($script:ProjectProfile) {
            Write-Log "Projet dÃ©tectÃ©: $($script:ProjectProfile.Id) (score: $($script:ProjectProfile.Score))" "SUCCESS"
        } else {
            Write-Log "Aucun projet spÃ©cifique dÃ©tectÃ© (mode gÃ©nÃ©rique)" "INFO"
        }

        Write-Log "RÃ©pertoire de sortie: $($script:Config.OutputDir)" "INFO"
        Write-Log "Timestamp: $($script:Config.Timestamp)" "DETAIL"

        # ExÃ©cution des phases
        $auditStartTime = Get-Date
        $allPhaseResults = @()
        $totalModules = 0
        $totalErrors = 0
        $totalWarnings = 0

        for ($i = 0; $i -lt $executionPlan.Count; $i++) {
            $phaseId = $executionPlan[$i]
            $phase = $script:AuditPhases | Where-Object { $_.Id -eq $phaseId }
            
            if (-not $phase) { continue }
            
            Write-Log "" "INFO"
            Write-Log "[$($i + 1)/$($executionPlan.Count)] DÃ©marrage Phase $phaseId" "PROGRESS"
            
            try {
                $phaseResult = Execute-Phase -Phase $phase -ProjectName $script:ProjectInfo.Name
                $allPhaseResults += $phaseResult
                
                $totalModules += $phaseResult.ModuleCount
                $totalErrors += $phaseResult.ErrorCount
                $totalWarnings += $phaseResult.WarningCount
                
                # Progression globale
                $progressPercent = [math]::Round((($i + 1) / $executionPlan.Count) * 100)
                Write-Log "Progression globale: $progressPercent% ($($i + 1)/$($executionPlan.Count) phases)" "DETAIL"
                
            } catch {
                Write-Log "Erreur critique durant Phase $phaseId : $($_.Exception.Message)" "ERROR"
                continue
            }
        }

        # RÃ©sumÃ© final
        $auditEndTime = Get-Date
        $totalDuration = $auditEndTime - $auditStartTime
        
        Write-Log "" "INFO"
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host "AUDIT TERMINE AVEC SUCCÃˆS" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Green
        
        Write-Log "DurÃ©e totale: $([math]::Round($totalDuration.TotalMinutes, 2)) minutes" "SUCCESS"
        Write-Log "Phases exÃ©cutÃ©es: $($allPhaseResults.Count)" "SUCCESS"
        Write-Log "Modules exÃ©cutÃ©s: $totalModules" "SUCCESS"
        
        if ($totalErrors -gt 0 -or $totalWarnings -gt 0) {
            Write-Log "ProblÃ¨mes dÃ©tectÃ©s: $totalErrors erreurs, $totalWarnings avertissements" "WARN"
        } else {
            Write-Log "Aucun problÃ¨me dÃ©tectÃ©" "SUCCESS"
        }
        
        Write-Log "Rapport complet: $($script:Config.OutputDir)\audit_summary_$($script:Config.Timestamp).json" "INFO"

        # GÃ©nÃ©ration du rÃ©sumÃ© global
        $summary = @{
            AuditVersion = $script:Config.Version
            StartTime = $auditStartTime
            EndTime = $auditEndTime
            TotalDuration = $totalDuration
            Target = $Target
            ProjectRoot = $script:Config.ProjectRoot
            ProjectProfile = if ($script:ProjectProfile) { $script:ProjectProfile.Id } else { $null }
            RequestedPhases = $requestedPhases
            ExecutedPhases = $executionPlan
            PhaseResults = $allPhaseResults
            TotalPhases = $allPhaseResults.Count
            TotalModules = $totalModules
            TotalErrors = $totalErrors
            TotalWarnings = $totalWarnings
            Timestamp = $script:Config.Timestamp
            OutputDir = $script:Config.OutputDir
            AIContext = $script:Results.AIContext  # Inclure le contexte IA dans le summary
        }

        # FICHIER UNIQUE AI-SUMMARY.md avec contexte complet
        $aiSummaryFile = Join-Path $script:Config.OutputDir "AI-SUMMARY.md"
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        $projectRoot = $script:Config.ProjectRoot
        
        $aiSummary = "# AUDIT IA - VERIFICATION ET CORRECTIONS`n"
        $aiSummary += "> Genere: $timestamp | Projet: $projectRoot`n`n"
        
        # Instructions pour l'IA
        $aiSummary += "## INSTRUCTIONS`n"
        $aiSummary += "Pour chaque probleme, verifier le code et repondre:`n"
        $aiSummary += "- **FAUX POSITIF** : expliquer pourquoi ce n'est pas un vrai probleme`n"
        $aiSummary += "- **A CORRIGER** : proposer le fix avec extrait de code`n`n"
        
        # Scores
        $aiSummary += "## SCORES ACTUELS`n"
        $aiSummary += "| Categorie | Score | Status |`n"
        $aiSummary += "|-----------|-------|--------|`n"
        foreach ($key in ($script:Results.Scores.Keys | Sort-Object)) {
            $score = $script:Results.Scores[$key]
            $status = if($score -ge 8){"OK"}elseif($score -ge 5){"A verifier"}else{"CRITIQUE"}
            $aiSummary += "| $key | $score/10 | $status |`n"
        }
        $aiSummary += "`n"
        
        # Questions IA avec contexte complet
        if ($script:Results.AIContext -and $script:Results.AIContext.Count -gt 0) {
            $aiSummary += "---`n`n## PROBLEMES A ANALYSER`n`n"
            $questionId = 1
            
            foreach ($category in $script:Results.AIContext.Keys) {
                $catData = $script:Results.AIContext[$category]
                if ($catData.Questions -and $catData.Questions.Count -gt 0) {
                    $aiSummary += "### $category`n`n"
                    
                    foreach ($q in $catData.Questions) {
                        $severity = switch ($q.Severity) { "critical" {"CRITIQUE"} "high" {"IMPORTANT"} "medium" {"MOYEN"} default {"INFO"} }
                        
                        $aiSummary += "#### [$questionId] $($q.Type) - $severity`n"
                        $aiSummary += "- **Fichier**: ``$($q.File)``"
                        if ($q.Line) { $aiSummary += " ligne $($q.Line)" }
                        $aiSummary += "`n"
                        
                        # Ajouter le contexte si disponible
                        if ($q.Context) {
                            $aiSummary += "- **Contexte**:`n"
                            $aiSummary += "```````n$($q.Context)`n```````n"
                        }
                        
                        # Question specifique
                        if ($q.Question) {
                            $aiSummary += "- **Question**: $($q.Question)`n"
                        } else {
                            # Generer une question par defaut
                            $defaultQ = switch ($q.Type) {
                                "Timer Without Cleanup" { "Ce timer a-t-il besoin d'un cleanup dans useEffect ? Si oui, proposer le fix." }
                                "Unused Handler" { "Ce handler est-il utilise dynamiquement ? Si non, peut-on le supprimer ?" }
                                "Request In Loop" { "Cette requete dans une boucle est-elle un probleme N+1 ? Proposer une optimisation." }
                                "API non accessible" { "L'API est-elle configuree correctement ? Verifier .env et connexion DB." }
                                default { "Analyser ce probleme et proposer une solution." }
                            }
                            $aiSummary += "- **Question**: $defaultQ`n"
                        }
                        $aiSummary += "`n"
                        $questionId++
                    }
                }
            }
        } else {
            # FORCER LES QUESTIONS ENRICHIES SI AUCUNES NE SONT DETECTEES
            $aiSummary += "---`n`n## PROBLEMES A ANALYSER`n`n"
            # Utiliser les vraies questions du AI-QuestionGenerator
            if ($script:Results.AIContext) {
                $questionId = 1
                $categories = @("SemanticAnalysis", "RefactoringAdvice", "ArchitectureReview", "SecurityReview")
                
                foreach ($categoryName in $categories) {
                    if ($script:Results.AIContext.$categoryName -and $script:Results.AIContext.$categoryName.Questions) {
                        $aiSummary += "### $categoryName`n`n"
                        
                        foreach ($q in $script:Results.AIContext.$categoryName.Questions) {
                            $priority = switch ($q.Priority) {
                                "high" { "IMPORTANT" }
                                "medium" { "MOYEN" }
                                "low" { "INFO" }
                                default { "MOYEN" }
                            }
                            
                            $aiSummary += "#### [$questionId] $($q.Type) - $priority`n"
                            $aiSummary += "- **Fichier**: ``$($q.File)```n"
                            $aiSummary += "- **Question**: $($q.Question)`n"
                            $aiSummary += "- **Suggestion**: $($q.Suggestion)`n`n"
                            
                            $questionId++
                        }
                    }
                }
                
                # Ajouter les métriques de qualité réelles
                $aiSummary += "---`n`n## MÉTRIQUES DE QUALITÉ IA`n`n"
                if ($script:Results.AIContext.QualityMetrics) {
                    $metrics = $script:Results.AIContext.QualityMetrics
                    $aiSummary += "- **Score de qualité**: $($metrics.Score)/100`n"
                    $aiSummary += "- **Nombre de questions**: $($metrics.TotalQuestions)`n"
                    $aiSummary += "- **Priorité HAUTE**: $($metrics.HighPriorityCount)`n"
                    $aiSummary += "- **Catégories couvertes**: $($metrics.Categories -join ', ')`n"
                    $aiSummary += "- **Spécifique domaine**: $($metrics.ProjectType)`n"
                } else {
                    $aiSummary += "- **Score de qualité**: N/A`n"
                    $aiSummary += "- **Nombre de questions**: $($questionId - 1)`n"
                    $aiSummary += "- **Priorité HAUTE**: N/A`n"
                    $aiSummary += "- **Catégories couvertes**: SemanticAnalysis, RefactoringAdvice, ArchitectureReview, SecurityReview`n"
                    $aiSummary += "- **Spécifique domaine**: Inconnu`n"
                }
                $aiSummary += "`n"
            } else {
                # Fallback si pas de AIContext (ne devrait pas arriver)
                $aiSummary += "### SemanticAnalysis`n`n"
                $aiSummary += "#### [1] NoData - INFO`n"
                $aiSummary += "- **Fichier**: N/A`n"
                $aiSummary += "- **Question**: Aucune question IA générée. Vérifier la configuration de l'audit.`n"
                $aiSummary += "- **Suggestion**: Relancer l'audit avec la phase 14`n`n"
                
                $aiSummary += "---`n`n## MÉTRIQUES DE QUALITÉ IA`n`n"
                $aiSummary += "- **Score de qualité**: N/A`n"
                $aiSummary += "- **Nombre de questions**: 0`n"
                $aiSummary += "- **Priorité HAUTE**: 0`n"
                $aiSummary += "- **Catégories couvertes**: N/A`n"
                $aiSummary += "- **Spécifique domaine**: Inconnu`n"
                $aiSummary += "`n"
            }
        
        # Format de reponse attendu
        $aiSummary += "---`n`n## FORMAT DE REPONSE ATTENDU`n`n"
        $aiSummary += "Pour chaque probleme:`n"
        $aiSummary += "```````n"
        $aiSummary += "### [ID] Verdict: FAUX POSITIF | A CORRIGER`n"
        $aiSummary += "Explication: ...`n"
        $aiSummary += "Fix propose (si applicable):`n"
        $aiSummary += "// code...`n"
        $aiSummary += "```````n"
        
        $aiSummary | Out-File -FilePath $aiSummaryFile -Encoding UTF8 -Force
        Write-Log "Resume IA genere: $aiSummaryFile" "SUCCESS"

        # SAUVEGARDER LE RAPPORT GLOBAL JSON
        $globalSummaryFile = Join-Path $script:Config.OutputDir "audit_summary_$($script:Config.Timestamp).json"
        $summary | ConvertTo-Json -Depth 10 | Out-File -FilePath $globalSummaryFile -Encoding UTF8 -Force
        Write-Log "Rapport global JSON sauvegardé: $globalSummaryFile" "SUCCESS"

        # Mise à jour du tableau récapitulatif des scores d'audit
        try {
            # Détecter le projet et utiliser le module approprié
            $projectName = if ($summary -and $summary.ProjectName) { $summary.ProjectName } else { "ott" }
            $auditScoresUpdatePath = Join-Path $PSScriptRoot "projects\$projectName\modules\Checks-AuditScoresUpdate.ps1"
            
            # Fallback sur OTT si le module spécifique n'existe pas
            if (-not (Test-Path $auditScoresUpdatePath)) {
                $auditScoresUpdatePath = Join-Path $PSScriptRoot "projects\ott\modules\Checks-AuditScoresUpdate.ps1"
            }
            
            if (Test-Path $auditScoresUpdatePath) {
                . $auditScoresUpdatePath
                
                $updateResult = Update-AuditScoresDocumentation -AuditSummary $summary -OutputDir $script:Config.OutputDir
                if ($updateResult.Success) {
                    Write-Log "Tableau des scores d'audit mis à jour: $($updateResult.File)" "SUCCESS"
                    Write-Log "Score global: $($updateResult.GlobalScore)/10 sur $($updateResult.PhaseCount) phases" "INFO"
                } else {
                    Write-Log "Erreur lors de la mise à jour des scores: $($updateResult.Error)" "WARN"
                }
            } else {
                Write-Log "Module Checks-AuditScoresUpdate.ps1 non trouvé, mise à jour des scores ignorée" "WARN"
            }
        } catch {
        Write-Log "Erreur lors de la mise à jour du tableau des scores: $($_.Exception.Message)" "WARN"
    }
    
    # NETTOYAGE AUTOMATIQUE DES ANCIENS AUDITS (uniquement si audit réussi)
    try {
        # Vérifier si l'audit a réussi (pas d'erreurs critiques)
        $hasCriticalErrors = $summary.PhaseResults | Where-Object { $_.Errors -gt 0 }
        if (-not $hasCriticalErrors) {
            # Configurer le nombre d'audits à conserver (3 par défaut)
            $keepCount = 3
            if ($script:AuditConfig -and $script:AuditConfig.Cleanup -and $script:AuditConfig.Cleanup.KeepCount) {
                $keepCount = $script:AuditConfig.Cleanup.KeepCount
            }
            
            Remove-OldAuditResults -OutputDir $script:Config.OutputDir -KeepCount $keepCount
        } else {
            Write-Log "Nettoyage automatique désactivé: des erreurs critiques ont été détectées" "WARN"
        }
    } catch {
        Write-Log "Erreur lors du nettoyage automatique: $($_.Exception.Message)" "ERROR"
    }
    }
} catch {
    Write-Log "Erreur critique: $($_.Exception.Message)" "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" "ERROR"
    exit 1
}
}

# Lancement du programme principal
if ($PSBoundParameters.Count -eq 0 -and -not $script:Config.ProjectRoot) {
    Invoke-InteractiveMenu
} else {
    Main
}
