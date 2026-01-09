# ===============================================================================
# MODULE AUDIT - COHÉRENCE DE CONFIGURATION
# ===============================================================================
# Vérifie que la configuration est cohérente (Docker OU Render OU Autre)
# Pas de mélange entre environnements différents
# ===============================================================================

function Invoke-Check-ConfigConsistency {
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Config,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Results,
        
        [hashtable]$ProjectInfo = @{},
        
        [string]$ProjectRoot = ".",
        [string]$ProjectPath = "."
    )
    
    Write-PhaseSection -PhaseNumber 4 -Title "Cohérence Configuration"
    
    try {
        $issues = @()
        $warnings = @()
        $score = 10.0
        
        # Utiliser ProjectRoot ou ProjectPath
        if (-not $ProjectRoot -or $ProjectRoot -eq ".") {
            if ($ProjectPath -and $ProjectPath -ne ".") {
                $ProjectRoot = $ProjectPath
            } else {
                $ProjectRoot = (Get-Location).Path
            }
        }
        
        # ===============================================================================
        # DÉTECTION DE L'ENVIRONNEMENT CIBLE
        # ===============================================================================
        
        function Get-ConfigEnvironment {
            param([string]$file, [string]$content)
            
            $env = @{
                Docker = $false
                Render = $false
                GitHub = $false
                Local = $false
                Production = $false
                IsDocumentation = $false
            }
            
            # Fichiers de documentation (OK d'avoir plusieurs environnements)
            if ($file -match "README|example|\.md$|next\.config\.js|render\.yaml") {
                $env.IsDocumentation = $true
            }
            
            # Enlever les commentaires pour ne détecter que le code actif
            $activeContent = $content
            $activeContent = $activeContent -replace '(?m)^\s*//.*$', ''
            $activeContent = $activeContent -replace '(?m)^\s*#.*$', ''
            $activeContent = $activeContent -replace '/\*[\s\S]*?\*/', ''
            
            # Détection Docker
            if ($activeContent -match "localhost:8000|localhost:3000|db:5432|ott-postgres|ott-api|ott-dashboard|docker-compose") {
                $env.Docker = $true
                $env.Local = $true
            }
            
            # Détection Render
            if ($activeContent -match "render\.com|dpg-.*\.render\.com|ott-jbln\.onrender\.com|fromDatabase") {
                $env.Render = $true
                $env.Production = $true
            }
            
            # Détection GitHub Pages
            if ($activeContent -match "github\.io|ymora\.github\.io") {
                $env.GitHub = $true
                $env.Production = $true
            }
            
            return $env
        }
        
        # ===============================================================================
        # ANALYSE DES FICHIERS DE CONFIGURATION
        # ===============================================================================
        
        $configFiles = @{}
        $configFilePaths = @(
            "docker-compose.yml",
            "Dockerfile",
            "Dockerfile.dashboard",
            "render.yaml",
            "env.example",
            ".env.local",
            "next.config.js",
            "api.php",
            "bootstrap/database.php"
        )
        
        $environments = @{}
        
        Write-Info "Analyse des fichiers de configuration..."
        
        foreach ($file in $configFilePaths) {
            $filePath = Join-Path $ProjectRoot $file
            if (Test-Path $filePath) {
                $content = Get-Content $filePath -Raw -ErrorAction SilentlyContinue
                if ($content) {
                    $configFiles[$file] = $content
                    $env = Get-ConfigEnvironment -file $file -content $content
                    $environments[$file] = $env
                }
            }
        }
        
        # ===============================================================================
        # VÉRIFICATION DE LA COHÉRENCE
        # ===============================================================================
        
        Write-Info "Vérification de la cohérence..."
        
        # Compter les environnements détectés
        $dockerCount = 0
        $renderCount = 0
        $githubCount = 0
        
        foreach ($env in $environments.Values) {
            if ($env.Docker) { $dockerCount++ }
            if ($env.Render) { $renderCount++ }
            if ($env.GitHub) { $githubCount++ }
        }
        
        Write-Info "Docker: $dockerCount, Render: $renderCount, GitHub: $githubCount"
        
        # Vérifier les fichiers de configuration actifs (pas la documentation)
        $activeConfigFiles = $environments.Keys | Where-Object { 
            -not $environments[$_].IsDocumentation
        }
        
        # Si plusieurs environnements sont mélangés dans les fichiers ACTIFS
        $dockerInActive = 0
        $renderInActive = 0
        $githubInActive = 0
        
        foreach ($file in $activeConfigFiles) {
            $env = $environments[$file]
            if ($env.Docker) { $dockerInActive++ }
            if ($env.Render) { $renderInActive++ }
            if ($env.GitHub) { $githubInActive++ }
        }
        
        if (($dockerInActive -gt 0 -and $renderInActive -gt 0) -or 
            ($dockerInActive -gt 0 -and $githubInActive -gt 0) -or 
            ($renderInActive -gt 0 -and $githubInActive -gt 0)) {
            
            $issues += "Mélange de configurations Docker/Render/GitHub dans les fichiers actifs"
            Write-Warn "Incohérence: Mélange d'environnements dans les fichiers de configuration actifs"
            $score -= 3.0
            
            # Détailler les fichiers problématiques
            foreach ($file in $activeConfigFiles) {
                $env = $environments[$file]
                $envCount = 0
                if ($env.Docker) { $envCount++ }
                if ($env.Render) { $envCount++ }
                if ($env.GitHub) { $envCount++ }
                
                if ($envCount -gt 1) {
                    $issues += "  → $file mélange plusieurs environnements"
                    Write-Warn "    $file (fichier actif) mélange plusieurs environnements"
                }
            }
        } else {
            Write-OK "Aucune incohérence majeure détectée dans les fichiers actifs"
        }
        
        # Vérifier env.example vs fichiers Docker
        if ($environments.ContainsKey("env.example") -and $environments.ContainsKey("docker-compose.yml")) {
            $envExample = $environments["env.example"]
            $dockerCompose = $environments["docker-compose.yml"]
            
            if (-not $envExample.Docker -and $dockerCompose.Docker) {
                $warnings += "env.example ne documente pas Docker alors que docker-compose.yml existe"
                Write-Warn "env.example devrait documenter Docker"
                $score -= 0.5
            }
        }
        
        # Vérifier que render.yaml n'existe pas si on veut Docker uniquement
        if (Test-Path (Join-Path $ProjectRoot "render.yaml")) {
            if ($dockerInActive -gt $renderInActive -and $renderInActive -eq 0) {
                $warnings += "render.yaml existe mais n'est pas utilisé (projet Docker uniquement)"
                Write-Warn "render.yaml peut être archivé (projet Docker uniquement)"
                $score -= 0.3
            }
        }

        # =======================================================================
        # VARIABLES SENSIBLES : pas de valeurs en dur dans les fichiers serveur
        # =======================================================================
        $sensitivePatterns = @(
            @{ Key = "DATABASE_URL"; Regex = "(?i)(?:define\s*\(\s*['""]DATABASE_URL['""]|const\s+DATABASE_URL|['""]DATABASE_URL['""]\s*=>)\s*['""][^'""]+['""]" },
            @{ Key = "DB_HOST"; Regex = "(?i)['""]DB_HOST['""]\s*=>\s*['""][^'""]+['""]" },
            @{ Key = "DB_NAME"; Regex = "(?i)['""]DB_NAME['""]\s*=>\s*['""][^'""]+['""]" },
            @{ Key = "DB_USER"; Regex = "(?i)['""]DB_USER['""]\s*=>\s*['""][^'""]+['""]" },
            @{ Key = "DB_PASS"; Regex = "(?i)['""]DB_PASS['""]\s*=>\s*['""][^'""]+['""]" },
            @{ Key = "JWT_SECRET"; Regex = "(?i)(?:define\s*\(\s*['""]JWT_SECRET['""]|['""]JWT_SECRET['""]\s*=>)\s*['""][^'""]+['""]" },
            @{ Key = "SENDGRID_API_KEY"; Regex = "(?i)(?:define\s*\(\s*['""]SENDGRID_API_KEY['""]|['""]SENDGRID_API_KEY['""]\s*=>)\s*['""][^'""]+['""]" },
            @{ Key = "TWILIO_AUTH_TOKEN"; Regex = "(?i)(?:define\s*\(\s*['""]TWILIO_AUTH_TOKEN['""]|['""]TWILIO_AUTH_TOKEN['""]\s*=>)\s*['""][^'""]+['""]" }
        )

        $sensitiveIssues = @()
        $aiSensitiveContext = @()
        $phpFilesToScan = Get-ChildItem -Path $ProjectRoot -Recurse -File -Include *.php -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch 'vendor|node_modules|\.git|\.next|hardware|docs' }

        foreach ($file in $phpFilesToScan) {
            $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
            if (-not $content) { continue }

            foreach ($pattern in $sensitivePatterns) {
                $matches = [regex]::Matches($content, $pattern.Regex, [System.Text.RegularExpressions.RegexOptions]::Singleline)
                foreach ($match in $matches) {
                    $lineNumber = ($content.Substring(0, $match.Index) -split "`n").Count
                    $snippet = ($match.Value -split "`n")[0].Trim()
                    $sensitiveIssues += @{
                        File = $file.Name
                        Path = $file.FullName
                        Line = $lineNumber
                        Key = $pattern.Key
                        Snippet = $snippet
                    }
                    $aiSensitiveContext += @{
                        Category = "Configuration"
                        Type = "Variable sensible en dur"
                        File = $file.Name
                        Line = $lineNumber
                        Severity = "high"
                        NeedsAICheck = $true
                        Question = "La variable '$($pattern.Key)' doit-elle provenir d'un getenv() plutôt que d'une valeur littérale dans $($file.Name) ?"
                    }
                }
            }
        }

        if ($sensitiveIssues.Count -gt 0) {
            Write-Warn "$($sensitiveIssues.Count) variable(s) sensibles définie(s) en dur"
            $score -= 0.5 * $sensitiveIssues.Count
            foreach ($issue in $sensitiveIssues) {
                $Results.Issues += "Cohérence Configuration: '$($issue.Key)' défini en dur dans $($issue.Path):$($issue.Line) ($($issue.Snippet))"
            }
        } else {
            Write-OK "Aucune variable sensible définie en dur"
        }
        
        # ===============================================================================
        # DÉTERMINER L'ENVIRONNEMENT PRINCIPAL
        # ===============================================================================
        
        $primaryEnv = "INCONNU"
        if ($dockerCount -gt $renderCount -and $dockerCount -gt $githubCount) {
            $primaryEnv = "DOCKER"
            Write-OK "Environnement principal: DOCKER (Local)"
        } elseif ($renderCount -gt $dockerCount -and $renderCount -gt $githubCount) {
            $primaryEnv = "RENDER"
            Write-OK "Environnement principal: RENDER (Production)"
        } elseif ($githubCount -gt $dockerCount -and $githubCount -gt $renderCount) {
            $primaryEnv = "GITHUB"
            Write-OK "Environnement principal: GITHUB PAGES (Production)"
        } else {
            $primaryEnv = "MIXTE"
            Write-Warn "Environnement principal: MIXTE (INCOHÉRENT)"
            $issues += "Impossible de déterminer l'environnement principal"
            $score -= 2.0
        }
        
        # ===============================================================================
        # RECOMMANDATIONS
        # ===============================================================================
        
        if ($issues.Count -gt 0 -or $primaryEnv -eq "MIXTE") {
            $Results.Recommendations += "Unifier la configuration (actuellement $primaryEnv)"
        }
        
        # ===============================================================================
        # ENREGISTRER LES RÉSULTATS
        # ===============================================================================
        
        $Results.Scores["Cohérence Configuration"] = [Math]::Max($score, 0)
        
        if ($issues.Count -gt 0) {
            foreach ($issue in $issues) {
                $Results.Issues += "Cohérence Configuration: $issue"
            }
        }
        
        if ($warnings.Count -gt 0) {
            foreach ($warning in $warnings) {
                $Results.Warnings += "Cohérence Configuration: $warning"
            }
        }
        
        Write-OK "Vérification cohérence configuration terminée"
        
    } catch {
        Write-Err "Erreur vérification cohérence configuration: $($_.Exception.Message)"
        $Results.Scores["Cohérence Configuration"] = 5
    }
}
