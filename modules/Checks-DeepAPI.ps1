# ===============================================================================
# MODULE D'AUDIT: Analyse approfondie des APIs
# ===============================================================================

function Invoke-DeepAPIAnalysis {
    param(
        [string]$ProjectPath = $script:Config.ProjectRoot
    )
    
    Write-Host "[AUDIT] Analyse approfondie des APIs..." -ForegroundColor Cyan
    
    $results = @{
        Category = "API Analysis"
        Issues = @()
        Score = 100
        Details = @{}
    }
    
    $apiPath = Join-Path $ProjectPath "backend\app\api"
    $frontendPath = Join-Path $ProjectPath "frontend\src"
    
    if (-not (Test-Path $apiPath)) {
        Write-Warning "Répertoire API non trouvé: $apiPath"
        return $results
    }
    
    # Analyser les endpoints backend
    $backendEndpoints = @{}
    $endpointFiles = Get-ChildItem -Path $apiPath -Filter "*.py" -Exclude "__init__.py"
    
    foreach ($file in $endpointFiles) {
        $content = Get-Content $file.FullName -Raw -Encoding UTF8
        
        # Extraire le préfixe du routeur
        $prefixMatch = [regex]::Match($content, 'router\s*=\s*APIRouter\(prefix=["'']([^"'']+)["'']')
        $prefix = if ($prefixMatch.Success) { $prefixMatch.Groups[1].Value } else { "" }
        
        # Extraire tous les endpoints
        $endpointPattern = '@router\.(get|post|put|delete|patch)\(["'']([^"'']+)["''].*?\n\s*(?:async\s+)?def\s+(\w+)'
        $matches = [regex]::Matches($content, $endpointPattern, [Text.RegularExpressions.RegexOptions]::Singleline)
        
        $endpoints = @()
        foreach ($match in $matches) {
            $method = $match.Groups[1].Value
            $path = $match.Groups[2].Value
            $functionName = $match.Groups[3].Value
            
            $endpointInfo = @{
                Method = $method.ToUpper()
                Path = $prefix + $path
                Function = $functionName
                File = $file.Name
                FullPath = $prefix + $path
            }
            
            $endpoints += $endpointInfo
            $backendEndpoints[$endpointInfo.FullPath] = $endpointInfo
        }
        
        $results.Details[$file.Name] = @{
            Prefix = $prefix
            Endpoints = $endpoints
            Count = $endpoints.Count
        }
    }
    
    # Analyser l'utilisation frontend
    $frontendUsage = @{}
    if (Test-Path $frontendPath) {
        $tsFiles = Get-ChildItem -Path $frontendPath -Filter "*.ts*" -Recurse
        
        foreach ($file in $tsFiles) {
            $content = Get-Content $file.FullName -Raw -Encoding UTF8
            
            # Chercher les appels API
            $apiCallPattern = ['"/api/([^"']+)"', 'fetch\(["'']/api/([^"']+)["'']']
            
            foreach ($pattern in $apiCallPattern) {
                $matches = [regex]::Matches($content, $pattern)
                foreach ($match in $matches) {
                    $apiPath = "/api/" + $match.Groups[1].Value
                    if (-not $frontendUsage.ContainsKey($apiPath)) {
                        $frontendUsage[$apiPath] = @()
                    }
                    $frontendUsage[$apiPath] += $file.Name
                }
            }
        }
    }
    
    # Comparer backend vs frontend
    $unusedEndpoints = @()
    $missingEndpoints = @()
    
    foreach ($endpoint in $backendEndpoints.Keys) {
        if (-not $frontendUsage.ContainsKey($endpoint)) {
            $unusedEndpoints += $backendEndpoints[$endpoint]
        }
    }
    
    foreach ($endpoint in $frontendUsage.Keys) {
        if (-not $backendEndpoints.ContainsKey($endpoint)) {
            $missingEndpoints += @{
                Path = $endpoint
                UsedIn = $frontendUsage[$endpoint]
            }
        }
    }
    
    # Générer les problèmes
    if ($unusedEndpoints.Count -gt 0) {
        $results.Issues += @{
            Type = "Unused Endpoints"
            Severity = "medium"
            Count = $unusedEndpoints.Count
            Details = $unusedEndpoints
            Description = "Endpoints backend non utilisés par le frontend"
        }
        $results.Score -= [math]::Min(20, $unusedEndpoints.Count * 2)
    }
    
    if ($missingEndpoints.Count -gt 0) {
        $results.Issues += @{
            Type = "Missing Endpoints"
            Severity = "high"
            Count = $missingEndpoints.Count
            Details = $missingEndpoints
            Description = "Endpoints appelés par frontend mais non définis dans backend"
        }
        $results.Score -= [math]::Min(30, $missingEndpoints.Count * 3)
    }
    
    # Statistiques
    $results.Details["Statistics"] = @{
        TotalBackendEndpoints = $backendEndpoints.Count
        TotalFrontendCalls = $frontendUsage.Count
        UnusedEndpoints = $unusedEndpoints.Count
        MissingEndpoints = $missingEndpoints.Count
        UtilizationRate = if ($backendEndpoints.Count -gt 0) { 
            [math]::Round((($backendEndpoints.Count - $unusedEndpoints.Count) / $backendEndpoints.Count) * 100, 2) 
        } else { 0 }
    }
    
    Write-Host "[OK] Analyse API terminée - Score: $($results.Score)/100" -ForegroundColor Green
    Write-Host "  - Endpoints backend: $($backendEndpoints.Count)" -ForegroundColor Gray
    Write-Host "  - Endpoints utilisés: $($backendEndpoints.Count - $unusedEndpoints.Count)" -ForegroundColor Gray  
    Write-Host "  - Endpoints manquants: $($missingEndpoints.Count)" -ForegroundColor Gray
    
    return $results
}

# Exporter la fonction
Export-ModuleMember -Function Invoke-DeepAPIAnalysis
