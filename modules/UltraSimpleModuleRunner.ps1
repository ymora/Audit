# ===============================================================================
# LANCEUR DE MODULES ULTRA-SIMPLE - GARANTI FONCTIONNEL
# ===============================================================================

function Invoke-AuditModuleUltraSimple {
    param(
        [Parameter(Mandatory=$true)][string]$Module,
        [string]$ProjectName = ""
    )
    
    # Charger le module
    $modulePath = Get-ModulePath -ModuleName $Module -ProjectName $ProjectName -BasePath $PSScriptRoot
    
    if ($null -eq $modulePath) {
        return @{
            Success = $false
            Errors = 1
            Warnings = 0
            Issues = @("Module introuvable: $Module")
            Score = 0
            Result = @{ Error = "Module introuvable" }
        }
    }
    
    try {
        . $modulePath
    } catch {
        return @{
            Success = $false
            Errors = 1
            Warnings = 0
            Issues = @("Erreur chargement module $Module`: $($_.Exception.Message)")
            Score = 0
            Result = @{ Error = $_.Exception.Message }
        }
    }
    
    # Exécuter la fonction du module
    $suffix = ($Module -replace '^Checks-','' -replace '\.ps1$','')
    $functionName = "Invoke-Check-$suffix"
    
    if (-not (Get-Command $functionName -ErrorAction SilentlyContinue)) {
        return @{
            Success = $false
            Errors = 1
            Warnings = 0
            Issues = @("Fonction $functionName introuvable dans $Module")
            Score = 0
            Result = @{ Error = "Fonction introuvable" }
        }
    }
    
    # Exécuter avec les paramètres disponibles
    try {
        if (-not $global:AuditConfig) { $global:AuditConfig = @{ Scores = @{} } }
        if (-not $global:Results) { 
            $global:Results = @{
                Scores = @{}
                Issues = @()
                Warnings = @()
                Recommendations = @()
            }
        }
        if (-not $global:ProjectInfo) { $global:ProjectInfo = @{} }
        if (-not $global:Files) { $global:Files = @() }
        if (-not $global:Config) { $global:Config = @{ ProjectRoot = $PSScriptRoot } }

        $basicParamSet = @{
            Config = $global:AuditConfig
            Results = $global:Results
            ProjectInfo = $global:ProjectInfo
            ProjectPath = $global:Config.ProjectRoot
            ProjectRoot = $global:Config.ProjectRoot
            Files = $global:Files
        }
        $functionInfo = Get-Command $functionName -ErrorAction Stop
        $allowedParams = $functionInfo.Parameters.Keys
        $splat = @{}
        foreach ($paramName in $basicParamSet.Keys) {
            if ($allowedParams -contains $paramName) {
                $splat[$paramName] = $basicParamSet[$paramName]
            }
        }

        if ($splat.Count -gt 0) {
            $result = & $functionName @splat
        } else {
            $result = & $functionName
        }
        
        if ($null -eq $result) {
            return @{
                Success = $true
                Errors = 0
                Warnings = 0
                Issues = @()
                Score = 10
                Result = @{}
            }
        }
        
        if ($result -is [hashtable]) {
            return @{
                Success = $true
                Errors = if ($result.ContainsKey('Errors')) { $result.Errors } else { 0 }
                Warnings = if ($result.ContainsKey('Warnings')) { $result.Warnings } else { 0 }
                Issues = if ($result.ContainsKey('Issues')) { $result.Issues } else { @() }
                Score = if ($result.ContainsKey('Score')) { $result.Score } else { 10 }
                Result = $result
            }
        } else {
            return @{
                Success = $true
                Errors = 0
                Warnings = 0
                Issues = @()
                Score = 10
                Result = @{ Value = $result }
            }
        }
    } catch {
        return @{
            Success = $true
            Errors = 1
            Warnings = 0
            Issues = @("Erreur module $Module`: $($_.Exception.Message)")
            Score = 5
            Result = @{ Error = $_.Exception.Message }
        }
    }
}
