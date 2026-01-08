# ===============================================================================
# DÉTECTEUR DE PROJET GÉNÉRIQUE
# ===============================================================================
# Détecte automatiquement le type de projet et charge la configuration appropriée
# ===============================================================================

function Get-ProjectProfile {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectPath
    )
    
    # Chercher les profils de projet disponibles
    $profilesBasePath = Join-Path $PSScriptRoot "..\projects"
    $profiles = @()
    
    Write-Log "Recherche des profils dans: $profilesBasePath" "DETAIL"
    
    if (Test-Path $profilesBasePath) {
        Get-ChildItem $profilesBasePath -Directory | ForEach-Object {
            $projectName = $_.Name
            $profileFile = Join-Path $_.FullName "project.ps1"
            
            Write-Log "Test du profil: $projectName -> $profileFile" "DETAIL"
            
            if (Test-Path $profileFile) {
                try {
                    # Charger le profil dans un scope séparé
                    $profileScript = Get-Content $profileFile -Raw
                    . ([scriptblock]::Create($profileScript))
                    
                    if (Get-Command Test-ProjectDetection -ErrorAction SilentlyContinue) {
                        $score = Test-ProjectDetection -ProjectPath $ProjectPath
                        Write-Log "Score pour $projectName`: $score" "DETAIL"
                        
                        if ($score -gt 0) {
                            $profiles += @{
                                Name = $projectName
                                Score = $score
                                Path = $_.FullName
                                ProfileFile = $profileFile
                            }
                        }
                    } else {
                        Write-Log "Fonction Test-ProjectDetection non trouvée dans $projectName" "WARN"
                    }
                } catch {
                    Write-Log "Erreur profil $projectName`: $($_.Exception.Message)" "WARN"
                }
            } else {
                Write-Log "Fichier profil non trouvé: $profileFile" "DETAIL"
            }
        }
    } else {
        Write-Log "Répertoire des profils non trouvé: $profilesBasePath" "WARN"
    }
    
    # Afficher les résultats
    if ($profiles.Count -gt 0) {
        Write-Log "Profils détectés: $($profiles.Count)" "INFO"
        foreach ($p in $profiles) {
            Write-Log "  - $($p.Name): score $($p.Score)" "DETAIL"
        }
        
        # Retourner le profil avec le meilleur score
        $bestProfile = $profiles | Sort-Object Score -Descending | Select-Object -First 1
        Write-Log "Meilleur profil: $($bestProfile.Name) avec score $($bestProfile.Score)" "SUCCESS"
        return $bestProfile
    }
    
    # Profil générique par défaut
    Write-Log "Aucun profil détecté, utilisation du profil générique" "INFO"
    return @{
        Name = "generic"
        Score = 1
        Path = Join-Path $profilesBasePath "generic"
        ProfileFile = $null
    }
}

function Get-ProjectConfiguration {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectPath,
        
        [string]$ProjectName = ""
    )
    
    # Si pas de nom de projet, détecter automatiquement
    if ([string]::IsNullOrWhiteSpace($ProjectName)) {
        $projectProfile = Get-ProjectProfile -ProjectPath $ProjectPath
        $ProjectName = $projectProfile.Name
    }
    
    # Charger la configuration du projet
    $configPaths = @(
        (Join-Path $ProjectPath "audit.config.ps1"),           # Config locale au projet
        (Join-Path $ProjectPath "audit.config.local.ps1"),    # Config locale non versionnée
        (Join-Path $PSScriptRoot "..\projects\$ProjectName\config\audit.config.ps1"),  # Config spécifique
        (Join-Path $PSScriptRoot "..\projects\$ProjectName\config\audit.config.local.ps1"),  # Config locale spécifique
        (Join-Path $PSScriptRoot "..\config\audit.config.ps1") # Config globale par défaut
    )
    
    foreach ($configPath in $configPaths) {
        if (Test-Path $configPath) {
            try {
                . $configPath
                if ($global:AuditConfig) {
                    Write-Log "Configuration chargée: $configPath" "INFO"
                    return $global:AuditConfig
                }
            } catch {
                Write-Log "Erreur configuration $configPath`: $($_.Exception.Message)" "WARN"
            }
        }
    }
    
    # Configuration par défaut générique
    return Get-DefaultAuditConfig
}

function Get-DefaultAuditConfig {
    return @{
        Project = @{
            Name = "Generic"
            Type = "Unknown"
            Description = "Projet générique"
            Language = @()
            Framework = @()
        }
        
        Phases = @{
            Include = @(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14)
            Exclude = @(11, 12)
        }
        
        Modules = @{
            "Checks-Tests" = @{
                MinTestFiles = 1
                TestPatterns = @("test/*", "tests/*", "*test*", "*spec*")
                Required = $false
            }
            
            "Checks-API" = @{
                ApiRequired = $false
                ApiUrl = ""
                TimeoutMs = 5000
            }
            
            "Checks-Performance" = @{
                MaxBundleSizeKB = 500
                MaxTimers = 5
            }
            
            "Checks-Documentation" = @{
                RequiredFiles = @("README.md")
                DocPatterns = @("*.md", "docs/*", "doc/*")
                MinDocCount = 1
            }
        }
        
        Excludes = @(
            "node_modules/*",
            ".git/*",
            "dist/*",
            "build/*",
            "*.log",
            "temp/*",
            ".DS_Store",
            "coverage/*"
        )
        
        Patterns = @{
            Include = @("*")
            Exclude = @("*.min.js", "*.bundle.js")
        }
        
        BaseScores = @{
            "Architecture" = 8
            "Security" = 8
            "Documentation" = 7
            "CodeQuality" = 7
            "Performance" = 7
            "Tests" = 5
            "API" = 6
        }
        
        Messages = @{
            ProjectType = "Projet Générique"
            TestStrategy = "Tests automatisés recommandés"
            APINote = "API non détectée"
            SecurityNote = "Sécurité standard"
        }
    }
}

function Get-ProjectInfo {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path
    )
    
    $detectedProfile = Get-ProjectProfile -ProjectPath $Path
    $config = Get-ProjectConfiguration -ProjectPath $Path -ProjectName $detectedProfile.Name
    
    return @{
        Name = $detectedProfile.Name
        Type = $config.Project.Type
        Framework = ($config.Project.Framework -join ", ")
        Version = $config.Project.Version
        Language = $config.Project.Language
        HasBackend = $false
        HasFrontend = $false
        PackageManager = $null
        ProjectSpecific = ($detectedProfile.Score -gt 1)
        Profile = $detectedProfile
        Configuration = $config
    }
}

# Les fonctions sont chargées directement - pas besoin d'Export-ModuleMember dans un script
