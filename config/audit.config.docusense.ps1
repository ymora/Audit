# ===============================================================================
# CONFIGURATION AUDIT SPÉCIFIQUE DOCUSENSE AI V2
# ===============================================================================

# Configuration spécifique pour DocuSense AI V2
# Exclut les modules non pertinents et adapte les scores

@{
    # Métadonnées du projet
    Project = @{
        Name = "DocuSense AI V2"
        Type = "WebApplication"
        Technologies = @("FastAPI", "React", "TypeScript", "SQLite", "Python", "Node.js")
        Description = "Application web d'analyse de documents avec IA"
    }
    
    # Modules à EXCLURE (non pertinents pour DocuSense)
    ExcludedModules = @(
        "Checks-FirmwareInteractive.ps1",
        "Checks-Database.ps1",  # Utilise Checks-DocSenseSpecific.ps1 à la place
        "Checks-API.ps1"         # Utilise Checks-DocSenseSpecific.ps1 à la place
    )
    
    # Modules à INCLURE (spécifiques à DocuSense)
    IncludedModules = @(
        "Checks-DocSenseSpecific.ps1"
    )
    
    # Configuration des phases
    Phases = @{
        # Phase 15: DocSense Spécifique (après toutes les autres phases)
        15 = @{
            Name = "DocSense Spécifique"
            Description = "Analyse adaptée à DocuSense AI V2"
            Modules = @("Checks-DocSenseSpecific.ps1")
            Dependencies = @()  # Aucune dépendance
            Priority = 1
        }
    }
    
    # Scoring adapté DocuSense
    Scoring = @{
        # Poids plus élevés pour les technologies pertinentes
        "DocSenseSpecific" = @{
            Weight = 3.0
            MaxScore = 10
        }
        
        # Poids réduits pour les modules moins critiques
        "Tests" = @{
            Weight = 0.5
            MaxScore = 10
        }
        
        "Documentation" = @{
            Weight = 1.0
            MaxScore = 10
        }
        
        # Exclure ces modules du scoring
        "Firmware" = @{
            Weight = 0
            MaxScore = 0
            Excluded = $true
        }
        
        "Hardware" = @{
            Weight = 0
            MaxScore = 0
            Excluded = $true
        }
    }
    
    # Filtres de fichiers spécifiques DocuSense
    FileFilters = @{
        # Inclure ces types de fichiers
        Include = @("*.py", "*.tsx", "*.ts", "*.js", "*.json", "*.md", "*.db", "*.env*")
        
        # Exclure ces répertoires
        ExcludeDirectories = @("node_modules", ".git", "__pycache__", ".pytest_cache")
        
        # Scripts spécifiques à DocuSense
        ScriptCategories = @{
            "Tests Unitaires" = @("backend/tests/*", "*test*.py")
            "Scripts Outils" = @("backend/scripts/tools/*", "check_*.py", "inspect_*.py")
            "Scripts Démo" = @("demo_*.py", "test_demo*.py")
            "Scripts Debug" = @("debug_*.py", "diag_*.py")
            "Scripts Migration" = @("migrate_*.py", "patch_*.py")
        }
    }
    
    # Messages spécifiques DocuSense
    Messages = @{
        "FirmwareExcluded" = "✓ Firmware exclu (DocuSense est une application web pure)"
        "HardwareExcluded" = "✓ Hardware exclu (DocuSense n'utilise pas de dispositifs physiques)"
        "APIFastAPIDetected" = "✓ FastAPI détecté (technologie appropriée pour DocuSense)"
        "SQLiteDetected" = "✓ SQLite détecté (base de données principale DocuSense)"
    }
}
