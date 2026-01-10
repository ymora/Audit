# ===============================================================================
# VÉRIFICATION : QUALITÉ DE CODE (VERSION AMÉLIORÉE)
# ===============================================================================
# Détecte le code mort, les éléments indésirables (TODO, simulations, contournements)
# et génère un rapport complet pour l'IA
# Évite les faux positifs en détectant les imports conditionnels et dynamiques

function Invoke-Check-CodeQuality {
    param(
        [Parameter(Mandatory=$true)]
        [array]$Files,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Config,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Results
    )
    
    # Si Checks n'existe pas ou CodeQuality.Enabled n'est pas défini, activer par défaut
    if ($Config.Checks -and $Config.Checks.CodeQuality -and $Config.Checks.CodeQuality.Enabled -eq $false) {
        return
    }
    
    Write-PhaseSectionNamed -Title "Qualité de Code et Éléments Indésirables" -Description "Détection du code mort, TODO, simulations, contournements et données sensibles"
    
    try {
        $deadCode = @{
            Components = @()
            Hooks = @()
            Libs = @()
        }
        $aiContext = @()  # Contexte pour l'IA
        
        $searchFiles = $Files | Where-Object { $_.Extension -match "\.jsx?$" }
        
        # Inclure aussi les fichiers app/ dans la recherche
        if (Test-Path "app") {
            $appFiles = Get-ChildItem -Path app -Recurse -File -Include *.js,*.jsx -ErrorAction SilentlyContinue
            $searchFiles = $searchFiles + $appFiles
        }
        
        # Analyser composants (AMÉLIORÉ - Détecte imports conditionnels)
        if (Test-Path "components") {
            Write-Info "Analyse composants avec détection imports conditionnels..."
            $allComponents = Get-ChildItem -Path components -Recurse -File -Include *.js,*.jsx -ErrorAction SilentlyContinue
            
            # Exclure les fichiers backup, old, temp, etc.
            $allComponents = $allComponents | Where-Object { 
                $_.BaseName -notmatch '_backup$|_old$|_temp$|_copy$|\.bak$|\.old$' 
            }
            
            foreach ($compFile in $allComponents) {
                $compName = $compFile.BaseName
                
                # Ignorer les hooks (use*) - ils ne sont pas utilisés en JSX
                if ($compName -match '^use[A-Z]') {
                    continue
                }
                
                $allFiles = $searchFiles + $compFile
                $allFiles = $allFiles | Where-Object { $_.FullName -ne $compFile.FullName }
                
                $importUsage = 0
                $jsxUsage = 0
                $conditionalUsage = 0
                $dynamicUsage = 0
                
                # Patterns d'imports à chercher
                $importStrings = @(
                    "from '@/components/$compName'",
                    "from '@/components/$compName.js'",
                    "from '@/components/$compName.jsx'",
                    "from `"@/components/$compName`"",
                    "from 'components/$compName'",
                    "import $compName from",
                    "import { $compName } from"
                )
                
                foreach ($file in $allFiles) {
                    $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
                    if (-not $content) { continue }
                    
                    # Chercher les imports directs
                    foreach ($importStr in $importStrings) {
                        if ($content -like "*$importStr*") {
                            $importUsage++
                            break
                        }
                    }
                    
                    # Chercher les imports conditionnels (if, ternary, etc.)
                    if ($content -match "if\s*\([^)]*\)\s*.*import.*$compName|ternary.*import.*$compName|\?\s*.*import.*$compName") {
                        $conditionalUsage++
                    }
                    
                    # Chercher les imports dynamiques
                    if ($content -match "React\.lazy.*$compName|lazy\(.*$compName|dynamic.*$compName|await import.*$compName|import\(.*$compName") {
                        $dynamicUsage++
                    }
                    
                    # Chercher les utilisations JSX
                    if ($content -like "*<$compName*" -or $content -like "*<$compName>*") {
                        $jsxUsage++
                    }
                }
                
                $totalUsage = $importUsage + $jsxUsage + $conditionalUsage + $dynamicUsage
                
                if ($totalUsage -le 1) {
                    # Potentiellement mort, mais générer contexte pour l'IA
                    $deadCode.Components += $compName
                    
                    $aiContext += @{
                        Category = "Code Mort"
                        Type = "Unused Component"
                        Component = $compName
                        File = $compFile.FullName
                        ImportUsage = $importUsage
                        JsxUsage = $jsxUsage
                        ConditionalUsage = $conditionalUsage
                        DynamicUsage = $dynamicUsage
                        Severity = "medium"
                        NeedsAICheck = $true
                        Question = "Le composant '$compName' est-il vraiment inutilisé ou est-il importé de manière conditionnelle/dynamique non détectée automatiquement ?"
                    }
                    
                    Write-Warn "Composant potentiellement mort: $compName (imports: $importUsage, JSX: $jsxUsage, conditionnel: $conditionalUsage, dynamique: $dynamicUsage)"
                } else {
                    Write-Info "  $compName utilisé (imports: $importUsage, JSX: $jsxUsage, conditionnel: $conditionalUsage, dynamique: $dynamicUsage)"
                }
            }
        }
        
        # Analyser hooks (AMÉLIORÉ)
        if (Test-Path "hooks") {
            Write-Info "Analyse hooks avec détection usage conditionnel..."
            $allHooks = Get-ChildItem -Path hooks -File -Include *.js -Exclude index.js -ErrorAction SilentlyContinue
            
            foreach ($hookFile in $allHooks) {
                $hookName = $hookFile.BaseName
                $usage = 0
                $conditionalUsage = 0
                
                foreach ($file in $searchFiles) {
                    $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
                    if (-not $content) { continue }
                    
                    # Chercher usage direct
                    if ($content -match "\b$hookName\s*\(") {
                        $usage++
                    }
                    
                    # Chercher usage conditionnel
                    if ($content -match "if\s*\([^)]*\)\s*.*$hookName|ternary.*$hookName") {
                        $conditionalUsage++
                    }
                }
                
                if ($usage -le 1 -and $conditionalUsage -eq 0) {
                    $deadCode.Hooks += $hookName
                    
                    $aiContext += @{
                        Category = "Code Mort"
                        Type = "Unused Hook"
                        Hook = $hookName
                        File = $hookFile.FullName
                        Usage = $usage
                        ConditionalUsage = $conditionalUsage
                        Severity = "medium"
                        NeedsAICheck = $true
                        Question = "Le hook '$hookName' est-il vraiment inutilisé ou est-il utilisé de manière conditionnelle non détectée ?"
                    }
                    
                    Write-Warn "Hook potentiellement mort: $hookName"
                }
            }
        }
        
        # Analyser libs (AMÉLIORÉ)
        if (Test-Path "lib") {
            Write-Info "Analyse libs avec détection usage conditionnel..."
            $allLibs = Get-ChildItem -Path lib -File -Include *.js -ErrorAction SilentlyContinue
            
            foreach ($libFile in $allLibs) {
                $libName = $libFile.BaseName
                $usage = 0
                $conditionalUsage = 0
                
                foreach ($file in $searchFiles) {
                    $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
                    if (-not $content) { continue }
                    
                    # Chercher usage direct
                    $libPattern = "from.*['`"]@/lib/$libName|from.*['`"]lib/$libName|import.*$libName"
                    if ($content -match $libPattern) {
                        $usage++
                    }
                    
                    # Chercher usage conditionnel
                    if ($content -match "if\s*\([^)]*\)\s*.*import.*$libName") {
                        $conditionalUsage++
                    }
                }
                
                if ($usage -le 1 -and $conditionalUsage -eq 0) {
                    $deadCode.Libs += $libName
                    
                    $aiContext += @{
                        Category = "Code Mort"
                        Type = "Unused Library"
                        Library = $libName
                        File = $libFile.FullName
                        Usage = $usage
                        ConditionalUsage = $conditionalUsage
                        Severity = "low"
                        NeedsAICheck = $true
                        Question = "La librairie '$libName' est-elle vraiment inutilisée ou est-elle importée de manière conditionnelle non détectée ?"
                    }
                    
                    Write-Warn "Lib potentiellement morte: $libName"
                }
            }
        }
        
        # ====================================================================
        # DÉTECTION DES ÉLÉMENTS INDÉSIRABLES (TODO, SIMULATION, CONTOURNEMENTS)
        # ====================================================================
        
        Write-Info "Recherche des éléments indésirables (TODO, simulations, contournements)..."
        
        $undesirableElements = @()
        $allSourceFiles = $Files | Where-Object { 
            $_.Extension -match "\.(js|jsx|ts|tsx|py|php|java|cpp|c|cs|go|rs|swift|kt|scala|rb|sh|ps1|html|css|scss|less|sql|json|yaml|yml|xml|md)$" 
        }
        
        foreach ($file in $allSourceFiles) {
            try {
                $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
                if (-not $content) { continue }
                
                $lines = $content -split "`n"
                $lineNumber = 0
                
                foreach ($line in $lines) {
                    $lineNumber++
                    $trimmedLine = $line.Trim()
                    
                    # Ignorer les lignes vides et les commentaires de documentation
                    if ([string]::IsNullOrWhiteSpace($trimmedLine) -or 
                        $trimmedLine -match "^/\*\*" -or 
                        $trimmedLine -match "^\s*\*" -or 
                        $trimmedLine -match "^\s*//\s*@") {
                        continue
                    }
                    
                    # Patterns à détecter
                    $patterns = @{
                        # TODO/FIXME/HACK
                        "TODO" = @(
                            "^\s*//\s*TODO\s*[:\-]?\s*(.+)",
                            "^\s*/\*\s*TODO\s*[:\-]?\s*(.+)\*/",
                            "^\s*#\s*TODO\s*[:\-]?\s*(.+)",
                            "^\s*<!--\s*TODO\s*[:\-]?\s*(.+)\s*-->",
                            "TODO\s*[:\-]?\s*(.+)"
                        )
                        
                        "FIXME" = @(
                            "^\s*//\s*FIXME\s*[:\-]?\s*(.+)",
                            "^\s*/\*\s*FIXME\s*[:\-]?\s*(.+)\*/",
                            "^\s*#\s*FIXME\s*[:\-]?\s*(.+)",
                            "FIXME\s*[:\-]?\s*(.+)"
                        )
                        
                        "HACK" = @(
                            "^\s*//\s*HACK\s*[:\-]?\s*(.+)",
                            "^\s*/\*\s*HACK\s*[:\-]?\s*(.+)\*/",
                            "^\s*#\s*HACK\s*[:\-]?\s*(.+)",
                            "HACK\s*[:\-]?\s*(.+)"
                        )
                        
                        "XXX" = @(
                            "^\s*//\s*XXX\s*[:\-]?\s*(.+)",
                            "^\s*/\*\s*XXX\s*[:\-]?\s*(.+)\*/",
                            "^\s*#\s*XXX\s*[:\-]?\s*(.+)",
                            "XXX\s*[:\-]?\s*(.+)"
                        )
                        
                        # Simulations et données de test
                        "SIMULATION" = @(
                            "(?i)(simulation|simulated|mock|stub|dummy|fake).*data",
                            "(?i)data.*(simulation|simulated|mock|stub|dummy|fake)",
                            "(?i)test.*data",
                            "(?i)demo.*data",
                            "(?i)sample.*data",
                            "(?i)hardcoded.*value",
                            "(?i)placeholder.*data"
                        )
                        
                        # Contournements et solutions temporaires
                        "WORKAROUND" = @(
                            "(?i)workaround\s*[:\-]?\s*(.+)",
                            "(?i)temporaire|temporary\s*[:\-]?\s*(.+)",
                            "(?i)contournement\s*[:\-]?\s*(.+)",
                            "(?i)quick\s+fix\s*[:\-]?\s*(.+)",
                            "(?i)hotfix\s*[:\-]?\s*(.+)",
                            "(?i)patch\s*[:\-]?\s*(.+)"
                        )
                        
                        # Code de débogage
                        "DEBUG" = @(
                            "(?i)console\.(log|debug|warn|error)",
                            "(?i)print\(",
                            "(?i)debug\.print",
                            "(?i)alert\(",
                            "(?i)console\.assert"
                        )
                        
                        # Credentials et données sensibles
                        "SENSITIVE" = @(
                            "(?i)(password|pwd|secret|token|key|api_key)\s*[:=]\s*['\"]\w+['\"]",
                            "(?i)(username|user|login)\s*[:=]\s*['\"]\w+['\"]",
                            "(?i)(connection|conn)\s*[:=]\s*['\"]\w+['\"]"
                        )
                    }
                    
                    foreach ($category in $patterns.Keys) {
                        foreach ($pattern in $patterns[$category]) {
                            if ($trimmedLine -match $pattern) {
                                $description = if ($matches.Count -gt 1) { $matches[1] } else { $trimmedLine }
                                
                                $undesirableElements += @{
                                    Category = $category
                                    Type = "Undesirable Element"
                                    File = $file.FullName
                                    Line = $lineNumber
                                    Content = $trimmedLine
                                    Description = $description
                                    Severity = switch ($category) {
                                        "TODO" { "low" }
                                        "FIXME" { "medium" }
                                        "HACK" { "medium" }
                                        "XXX" { "high" }
                                        "SIMULATION" { "medium" }
                                        "WORKAROUND" { "medium" }
                                        "DEBUG" { "low" }
                                        "SENSITIVE" { "high" }
                                        default { "medium" }
                                    }
                                    NeedsAICheck = $true
                                    Question = switch ($category) {
                                        "TODO" { "Ce TODO doit-il être résolu avant la mise en production ?" }
                                        "FIXME" { "Ce FIXME est-il bloquant pour la production ?" }
                                        "HACK" { "Ce hack peut-il être remplacé par une solution propre ?" }
                                        "XXX" { "Ce point d'attention XXX est-il critique ?" }
                                        "SIMULATION" { "Ces données de simulation/mock doivent-elles être supprimées ?" }
                                        "WORKAROUND" { "Ce contournement temporaire peut-il être remplacé par une solution définitive ?" }
                                        "DEBUG" { "Ce code de débogage doit-il être supprimé ?" }
                                        "SENSITIVE" { "Ces données sensibles doivent-elles être externalisées dans la configuration ?" }
                                        default { "Cet élément indésirable doit-il être traité ?" }
                                    }
                                }
                                
                                Write-Warn "$category : $($file.Name):$lineNumber - $description"
                                break
                            }
                        }
                    }
                }
            } catch {
                # Ignorer les erreurs de lecture de fichiers
            }
        }
        
        # Ajouter les éléments indésirables au contexte IA
        if ($undesirableElements.Count -gt 0) {
            $aiContext += $undesirableElements
            
            # Regrouper par catégorie pour le résumé
            $summary = $undesirableElements | Group-Object Category | ForEach-Object {
                "$($_.Name): $($_.Count)"
            }
            
            Write-Warn "Éléments indésirables détectés: $($undesirableElements.Count) total ($($summary -join ', '))"
            
            # Ajuster le score en fonction des éléments critiques
            $criticalCount = ($undesirableElements | Where-Object { $_.Severity -eq "high" }).Count
            $mediumCount = ($undesirableElements | Where-Object { $_.Severity -eq "medium" }).Count
            
            if ($criticalCount -gt 0) {
                $Results.Scores["Qualité de Code"] = [Math]::Max($Results.Scores["Qualité de Code"] - $criticalCount * 2, 3)
            } elseif ($mediumCount -gt 5) {
                $Results.Scores["Qualité de Code"] = [Math]::Max($Results.Scores["Qualité de Code"] - 1, 6)
            }
        } else {
            Write-OK "Aucun élément indésirable détecté"
        }
        
        # Sauvegarder le contexte pour l'IA
        if (-not $Results.AIContext) {
            $Results.AIContext = @{}
        }
        $Results.AIContext.CodeQuality = @{
            Components = $deadCode.Components.Count
            Hooks = $deadCode.Hooks.Count
            Libs = $deadCode.Libs.Count
            UndesirableElements = $undesirableElements.Count
            Questions = $aiContext
        }
        
        if ($deadCode.Components.Count -eq 0 -and $deadCode.Hooks.Count -eq 0 -and $deadCode.Libs.Count -eq 0 -and $undesirableElements.Count -eq 0) {
            Write-OK "Aucun problème détecté"
            $Results.Scores["Qualité de Code"] = 10
        } else {
            $totalIssues = $deadCode.Components.Count + $deadCode.Hooks.Count + $deadCode.Libs.Count + $undesirableElements.Count
            Write-Warn "$totalIssues problème(s) détecté(s) (nécessite vérification IA)"
            $Results.Scores["Qualité de Code"] = [Math]::Max(10 - $totalIssues * 0.3, 4)
        }
    } catch {
        Write-Err "Erreur analyse qualité de code: $($_.Exception.Message)"
        $Results.Scores["Qualité de Code"] = 7
    }
}

