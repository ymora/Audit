# ===============================================================================
# CHARGEUR DE MODULES DYNAMIQUE - SYSTÈME GÉNÉRIQUE
# ===============================================================================
# Charge les modules de base et les surcharges spécifiques par projet
# ===============================================================================

function Get-ModulePath {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ModuleName,
        
        [string]$ProjectName = "",
        
        [string]$BasePath = $PSScriptRoot
    )
    
    # 1. Chercher d'abord dans les modules spécifiques au projet (uniquement si le dossier existe)
    if (-not [string]::IsNullOrWhiteSpace($ProjectName)) {
        $projectModulePath = Join-Path $BasePath "..\projects\$ProjectName\modules\$ModuleName"
        if (Test-Path $projectModulePath) {
            return $projectModulePath
        }
    }
    
    # 2. Chercher dans les modules de base génériques
    $baseModulePath = Join-Path $BasePath $ModuleName
    if (Test-Path $baseModulePath) {
        return $baseModulePath
    }
    
    # 3. Retourner $null si non trouvé
    return $null
}

function Import-AuditModule {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ModuleName,
        
        [string]$ProjectName = "",
        
        [switch]$Required = $false
    )
    
    $modulePath = Get-ModulePath -ModuleName $ModuleName -ProjectName $ProjectName
    
    if ($null -ne $modulePath) {
        try {
            # Charger le module dans un nouvel espace pour éviter les conflits
            . $modulePath
            
            # S'assurer que les utilitaires sont disponibles
            $utilsPath = Join-Path $PSScriptRoot "Utils.ps1"
            if (Test-Path $utilsPath) {
                . $utilsPath
            }
            
            Write-Log "Module chargé: $ModuleName $(if(-not [string]::IsNullOrWhiteSpace($ProjectName)) { '(projet: ' + $ProjectName + ')' })" "INFO"
            return $true
        } catch {
            Write-Log "Erreur chargement module $ModuleName`: $($_.Exception.Message)" "ERROR"
            if ($Required) {
                throw "Module requis $ModuleName ne peut pas être chargé"
            }
            return $false
        }
    } else {
        if ($Required) {
            throw "Module requis $ModuleName introuvable"
        } else {
            Write-Log "Module optionnel $ModuleName introuvable" "WARN"
            return $false
        }
    }
}

function Get-AvailableModules {
    param(
        [string]$ProjectName = "",
        [string]$BasePath = $PSScriptRoot
    )
    
    $modules = @()
    
    # Modules de base
    $baseModulesPath = Join-Path $BasePath "*.ps1"
    Get-ChildItem $baseModulesPath -ErrorAction SilentlyContinue | ForEach-Object {
        $modules += @{
            Name = $_.Name
            Path = $_.FullName
            Type = "Base"
            Project = ""
        }
    }
    
    # Modules spécifiques au projet
    if (-not [string]::IsNullOrWhiteSpace($ProjectName)) {
        $projectModulesPath = Join-Path $BasePath "..\projects\$ProjectName\modules\*.ps1"
        Get-ChildItem $projectModulesPath -ErrorAction SilentlyContinue | ForEach-Object {
            $modules += @{
                Name = $_.Name
                Path = $_.FullName
                Type = "Project"
                Project = $ProjectName
            }
        }
    }
    
    return $modules
}

function Test-ModuleFunction {
    param(
        [Parameter(Mandatory=$true)]
        [string]$FunctionName
    )
    
    return $null -ne (Get-Command $FunctionName -ErrorAction SilentlyContinue)
}

function Invoke-ModuleFunction {
    param(
        [Parameter(Mandatory=$true)]
        [string]$FunctionName,
        
        [hashtable]$Parameters = @{},
        
        # Paramètres standards pour les modules d'audit
        [hashtable]$Config = @{},
        [hashtable]$Results = @{},
        [hashtable]$ProjectInfo = @{},
        [string]$ProjectPath = "",
        [array]$Files = @()
    )
    
    if (Test-ModuleFunction $FunctionName) {
        try {
            # Construire les paramètres pour la fonction de module
            $invokeParams = @{}
            
            # Ajouter les paramètres standards si la fonction les accepte
            $cmd = Get-Command $FunctionName -ErrorAction SilentlyContinue
            if ($cmd) {
                if ($cmd.Parameters.ContainsKey('Config')) { 
                    $invokeParams.Config = $Config 
                } else {
                    # Si Config n'est pas accepté, créer une variable globale
                    $global:ModuleConfig = $Config
                }
                
                if ($cmd.Parameters.ContainsKey('Results')) { 
                    $invokeParams.Results = $Results 
                } else {
                    $global:ModuleResults = $Results
                }
                
                if ($cmd.Parameters.ContainsKey('ProjectInfo')) { 
                    $invokeParams.ProjectInfo = $ProjectInfo 
                } else {
                    $global:ModuleProjectInfo = $ProjectInfo
                }
                
                if ($cmd.Parameters.ContainsKey('ProjectPath')) { 
                    $invokeParams.ProjectPath = $ProjectPath 
                } else {
                    $global:ModuleProjectPath = $ProjectPath
                }
                
                if ($cmd.Parameters.ContainsKey('Files')) { 
                    $invokeParams.Files = $Files 
                } else {
                    $global:ModuleFiles = $Files
                }
                
                if ($cmd.Parameters.ContainsKey('ProjectRoot')) { 
                    $invokeParams.ProjectRoot = $ProjectPath 
                }
            }
            
            # Ajouter les paramètres supplémentaires
            foreach ($key in $Parameters.Keys) {
                $invokeParams[$key] = $Parameters[$key]
            }
            
            # Exécuter la fonction
            $result = & $FunctionName @invokeParams
            
            # Nettoyer les variables globales
            Remove-Variable -Name "ModuleConfig", "ModuleResults", "ModuleProjectInfo", "ModuleProjectPath", "ModuleFiles" -ErrorAction SilentlyContinue
            
            return $result
        } catch {
            Write-Log "Erreur exécution fonction $FunctionName`: $($_.Exception.Message)" "ERROR"
            return @{
                Success = $false
                Error = $_.Exception.Message
            }
        }
    } else {
        Write-Log "Fonction $FunctionName introuvable" "WARN"
        return @{
            Success = $false
            Error = "Fonction $FunctionName introuvable"
        }
    }
}

# Les fonctions sont chargées directement - pas besoin d'Export-ModuleMember dans un script
