# ===============================================================================
# DÉTECTEUR DE PROJET SIMPLE - FONCTIONNEL
# ===============================================================================

function Get-ProjectInfo {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path
    )
    
    # Test direct pour le projet Haies
    $haiesFiles = @(
        "package.json",
        "admin/server.js", 
        "client/package.json",
        "ADMIN_README.md"
    )
    
    $haiesScore = 0
    foreach ($file in $haiesFiles) {
        if (Test-Path (Join-Path $Path $file)) {
            $haiesScore += 3
        }
    }
    
    if ($haiesScore -ge 6) {
        Write-Log "Projet Haies détecté avec score: $haiesScore" "SUCCESS"
        
        # Charger la configuration Haies
        $configPath = Join-Path $PSScriptRoot "..\projects\haies\config\audit.config.ps1"
        if (Test-Path $configPath) {
            . $configPath
            $config = $global:AuditConfig
        } else {
            $config = Get-DefaultAuditConfig
        }
        
        return @{
            Name = "haies"
            Type = "Admin Interface"
            Framework = "Express + React"
            Version = "1.0.0"
            Language = @("JavaScript", "PHP", "HTML")
            HasBackend = $true
            HasFrontend = $true
            PackageManager = "npm"
            ProjectSpecific = $true
            Profile = @{
                Name = "haies"
                Score = $haiesScore
                Path = Join-Path $PSScriptRoot "..\projects\haies"
                ProfileFile = Join-Path $PSScriptRoot "..\projects\haies\project.ps1"
            }
            Configuration = $config
        }
    }
    
    # Test pour OTT
    $ottFiles = @(
        "api.php",
        "composer.json",
        "components/DeviceModal.js"
    )
    
    $ottScore = 0
    foreach ($file in $ottFiles) {
        if (Test-Path (Join-Path $Path $file)) {
            $ottScore += 3
        }
    }
    
    if ($ottScore -ge 6) {
        Write-Log "Projet OTT détecté avec score: $ottScore" "SUCCESS"
        
        # Charger la configuration OTT
        $configPath = Join-Path $PSScriptRoot "..\projects\ott\config\audit.config.ps1"
        if (Test-Path $configPath) {
            . $configPath
            $config = $global:AuditConfig
        } else {
            $config = Get-DefaultAuditConfig
        }
        
        return @{
            Name = "ott"
            Type = "Medical Device"
            Framework = "PHP API"
            Version = "2.0.0"
            Language = @("PHP", "JavaScript", "Arduino")
            HasBackend = $true
            HasFrontend = $true
            PackageManager = "composer"
            ProjectSpecific = $true
            Profile = @{
                Name = "ott"
                Score = $ottScore
                Path = Join-Path $PSScriptRoot "..\projects\ott"
                ProfileFile = Join-Path $PSScriptRoot "..\projects\ott\project.ps1"
            }
            Configuration = $config
        }
    }
    
    # Profil générique par défaut
    Write-Log "Aucun projet spécifique détecté, utilisation du profil générique" "INFO"
    
    return @{
        Name = "generic"
        Type = "Unknown"
        Framework = "Unknown"
        Version = $null
        Language = @()
        HasBackend = $false
        HasFrontend = $false
        PackageManager = $null
        ProjectSpecific = $false
        Profile = @{
            Name = "generic"
            Score = 1
            Path = Join-Path $PSScriptRoot "..\projects\generic"
            ProfileFile = $null
        }
        Configuration = Get-DefaultAuditConfig
    }
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
