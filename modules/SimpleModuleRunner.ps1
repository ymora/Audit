# ===============================================================================
# LANCEUR DE MODULES SIMPLE - FONCTIONNEL
# ===============================================================================

function Invoke-AuditModuleSimple {
    param(
        [Parameter(Mandatory=$true)][string]$Module,
        [string]$ProjectName = "",
        [hashtable]$Config = @{},
        [hashtable]$Results = @{},
        [hashtable]$ProjectInfo = @{},
        [string]$ProjectPath = "",
        [array]$Files = @()
    )
    
    # Charger le module
    $modulePath = Get-ModulePath -ModuleName $Module -ProjectName $ProjectName -BasePath (Join-Path $PSScriptRoot "modules")
    
    if ($null -eq $modulePath) {
        throw "Module introuvable: $Module"
    }
    
    try {
        . $modulePath
    } catch {
        throw "Erreur chargement module $Module`: $($_.Exception.Message)"
    }
    
    # Exécuter la fonction du module
    $suffix = ($Module -replace '^Checks-','' -replace '\.ps1$','')
    $functionName = "Invoke-Check-$suffix"
    
    if (-not (Get-Command $functionName -ErrorAction SilentlyContinue)) {
        throw "Fonction $functionName introuvable dans $Module"
    }
    
    # Préparer les paramètres avec conversion de type
    $invokeParams = @{}
    $cmd = Get-Command $functionName -ErrorAction SilentlyContinue
    
    if ($cmd) {
        if ($cmd.Parameters.ContainsKey('Config') -and $Config.Count -gt 0) { 
            $invokeParams.Config = $Config 
        }
        if ($cmd.Parameters.ContainsKey('Results') -and $Results.Count -gt 0) { 
            $invokeParams.Results = $Results 
        }
        if ($cmd.Parameters.ContainsKey('ProjectInfo') -and $ProjectInfo.Count -gt 0) { 
            $invokeParams.ProjectInfo = $ProjectInfo 
        }
        if ($cmd.Parameters.ContainsKey('ProjectPath') -and $ProjectPath) { 
            $invokeParams.ProjectPath = $ProjectPath 
        }
        if ($cmd.Parameters.ContainsKey('Files') -and $Files.Count -gt 0) { 
            $invokeParams.Files = $Files 
        }
        if ($cmd.Parameters.ContainsKey('ProjectRoot') -and $ProjectPath) { 
            $invokeParams.ProjectRoot = $ProjectPath 
        }
    }
    
    # Exécuter avec gestion d'erreur améliorée
    try {
        Write-Log "Exécution de $functionName avec $(($invokeParams.Count)) paramètres" "DETAIL"
        
        $result = & $functionName @invokeParams
        
        Write-Log "Module $Module terminé avec succès" "INFO"
        
        # Normaliser le résultat
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
        Write-Log "Erreur module $Module`: $($_.Exception.Message)" "ERROR"
        return @{
            Success = $false
            Errors = 1
            Warnings = 0
            Issues = @("Erreur: $($_.Exception.Message)")
            Score = 0
            Result = @{ Error = $_.Exception.Message }
        }
    }
}
