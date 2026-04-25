# 🔍 AUDIT COMPLET VRAI DU PROJET OTT - SCAN DE TOUS LES MODULES

Write-Host "🚀 AUDIT COMPLET VRAI DU PROJET OTT" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Yellow

# Créer le rapport
$rapport = @()
$rapport += "# 🔍 AUDIT COMPLET VRAI - PROJET OTT"
$rapport += ""
$rapport += "**Date**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$rapport += "**Scan complet de tous les modules**"
$rapport += ""

# =================================================================
# 1. SCAN DES FICHIERS PHP
# =================================================================

Write-Host "`n🐘 SCAN DES FICHIERS PHP" -ForegroundColor Cyan
$rapport += "## 🐘 SCAN DES FICHIERS PHP"
$rapport += ""

$phpFiles = Get-ChildItem -Path "." -Filter "*.php" -Recurse
Write-Host "Fichiers PHP trouvés: $($phpFiles.Count)" -ForegroundColor White
$rapport += "**Fichiers PHP**: $($phpFiles.Count)"

$phpIssues = @()
$phpStats = @{
    Total = $phpFiles.Count
    Handlers = 0
    Helpers = 0
    Bootstrap = 0
    Other = 0
    SecurityIssues = 0
    PerformanceIssues = 0
    QualityIssues = 0
}

foreach ($file in $phpFiles) {
    $content = Get-Content $file.FullName -Raw
    $relativePath = $file.FullName.Replace((Get-Location).Path, "").TrimStart("\")
    
    # Catégoriser les fichiers
    if ($relativePath -match "handlers") { $phpStats.Handlers++ }
    elseif ($relativePath -match "helpers") { $phpStats.Helpers++ }
    elseif ($relativePath -match "bootstrap") { $phpStats.Bootstrap++ }
    else { $phpStats.Other++ }
    
    # Vérifier les problèmes de sécurité
    if ($content -match "echo json_encode.*success.*false.*error") {
        $phpIssues += @{
            Fichier = $relativePath
            Type = "Sécurité"
            Problème = "echo json_encode avec succès=false détecté"
            Ligne = ($content -split "`n" | Where-Object { $_ -match "echo json_encode.*success.*false.*error" }).LineNumber
        }
        $phpStats.SecurityIssues++
    }
    
    # Vérifier les injections SQL
    if ($content -match "\$_GET\[" -or $content -match "\$_POST\[" -and $content -notmatch "prepare\|execute") {
        $phpIssues += @{
            Fichier = $relativePath
            Type = "Sécurité"
            Problème = "Requête SQL sans prepare/execute détectée"
            Ligne = ($content -split "`n" | Where-Object { $_ -match "\$_GET\[|\$_POST\[" }).LineNumber
        }
        $phpStats.SecurityIssues++
    }
    
    # Vérifier les problèmes de performance
    if ($content -match "SELECT.*\* FROM.*WHERE.*1=1") {
        $phpIssues += @{
            Fichier = $relativePath
            Type = "Performance"
            Problème = "Requête sans WHERE clause sur clé primaire"
            Ligne = ($content -split "`n" | Where-Object { $_ -match "SELECT.*\* FROM.*WHERE.*1=1" }).LineNumber
        }
        $phpStats.PerformanceIssues++
    }
    
    # Vérifier les requêtes N+1
    $n1Matches = [regex]::Matches($content, "SELECT.*FROM.*WHERE.*IN.*SELECT")
    if ($n1Matches.Count -gt 0) {
        $phpIssues += @{
            Fichier = $relativePath
            Type = "Performance"
            Problème = "Problème N+1 potentiel détecté"
            Ligne = ($content -split "`n" | Where-Object { $_ -match "SELECT.*FROM.*WHERE.*IN.*SELECT" }).LineNumber
        }
        $phpStats.PerformanceIssues++
    }
    
    # Vérifier la qualité du code
    if ($content -match "var_dump\|print_r\|die\(" -and $content -notmatch "//.*var_dump") {
        $phpIssues += @{
            Fichier = $relativePath
            Type = "Qualité"
            Problème = "Code de debug en production détecté"
            Ligne = ($content -split "`n" | Where-Object { $_ -match "var_dump|print_r|die\(" }).LineNumber
        }
        $phpStats.QualityIssues++
    }
}

$rapport += "- **Handlers**: $($phpStats.Handlers)"
$rapport += "- **Helpers**: $($phpStats.Helpers)"
$rapport += "- **Bootstrap**: $($phpStats.Bootstrap)"
$rapport += "- **Autres**: $($phpStats.Other)"
$rapport += ""

# =================================================================
# 2. SCAN DES FICHIERS JAVASCRIPT
# =================================================================

Write-Host "`n📱 SCAN DES FICHIERS JAVASCRIPT" -ForegroundColor Cyan
$rapport += "## 📱 SCAN DES FICHIERS JAVASCRIPT"
$rapport += ""

$jsFiles = Get-ChildItem -Path "." -Filter "*.js" -Recurse
Write-Host "Fichiers JS trouvés: $($jsFiles.Count)" -ForegroundColor White
$rapport += "**Fichiers JS**: $($jsFiles.Count)"

$jsIssues = @()
$jsStats = @{
    Total = $jsFiles.Count
    Hooks = 0
    Components = 0
    Contexts = 0
    Other = 0
    PerformanceIssues = 0
    QualityIssues = 0
    SecurityIssues = 0
}

foreach ($file in $jsFiles) {
    $content = Get-Content $file.FullName -Raw
    $relativePath = $file.FullName.Replace((Get-Location).Path, "").TrimStart("\")
    
    # Catégoriser les fichiers
    if ($relativePath -match "hooks") { $jsStats.Hooks++ }
    elseif ($relativePath -match "components") { $jsStats.Components++ }
    elseif ($relativePath -match "contexts") { $jsStats.Contexts++ }
    else { $jsStats.Other++ }
    
    # Vérifier les problèmes de performance
    if ($content -match "console\.log" -and $content -notmatch "//.*console\.log") {
        $jsIssues += @{
            Fichier = $relativePath
            Type = "Performance"
            Problème = "console.log en production"
            Ligne = ($content -split "`n" | Where-Object { $_ -match "console\.log" -and $_ -notmatch "//.*console\.log" }).LineNumber
        }
        $jsStats.PerformanceIssues++
    }
    
    # Vérifier les useEffect sans dépendances
    if ($content -match "useEffect\(\s*\)" -and $content -notmatch "useEffect\(\s*\[") {
        $jsIssues += @{
            Fichier = $relativePath
            Type = "Performance"
            Problème = "useEffect sans tableau de dépendances"
            Ligne = ($content -split "`n" | Where-Object { $_ -match "useEffect\(\s*\)" -and $_ -notmatch "useEffect\(\s*\[") }).LineNumber
        }
        $jsStats.PerformanceIssues++
    }
    
    # Vérifier les variables non utilisées
    if ($content -match "duplicateUser|duplicateDevice|duplicatePatient|noAuthRequest|invalidAuthRequest") {
        $jsIssues += @{
            Fichier = $relativePath
            Type = "Qualité"
            Problème = "Variables non utilisées détectées"
            Ligne = ($content -split "`n" | Where-Object { $_ -match "duplicateUser|duplicateDevice|duplicatePatient|noAuthRequest|invalidAuthRequest" }).LineNumber
        }
        $jsStats.QualityIssues++
    }
    
    # Vérifier les problèmes de sécurité
    if ($content -match "eval\(|dangerouslySetInnerHTML") {
        $jsIssues += @{
            Fichier = $relativePath
            Type = "Sécurité"
            Problème = "Code eval ou innerHTML dangereux détecté"
            Ligne = ($content -split "`n" | Where-Object { $_ -match "eval\(|dangerouslySetInnerHTML" }).LineNumber
        }
        $jsStats.SecurityIssues++
    }
}

$rapport += "- **Hooks**: $($jsStats.Hooks)"
$rapport += "- **Components**: $($jsStats.Components)"
$rapport += "- **Contexts**: $($jsStats.Contexts)"
$rapport += "- **Autres**: $($jsStats.Other)"
$rapport += ""

# =================================================================
# 3. SCAN DES FICHIERS DE CONFIGURATION
# =================================================================

Write-Host "`n⚙️ SCAN DE LA CONFIGURATION" -ForegroundColor Cyan
$rapport += "## ⚙️ SCAN DE LA CONFIGURATION"
$rapport += ""

$configIssues = @()

# Vérifier docker-compose.yml
if (Test-Path ".\docker-compose.yml") {
    $dockerCompose = Get-Content ".\docker-compose.yml" -Raw
    Write-Host "✅ docker-compose.yml trouvé" -ForegroundColor Green
    $rapport += "✅ **docker-compose.yml**: Trouvé"
    
    # Vérifier les ports
    if ($dockerCompose -match "3000:3000" -and $dockerCompose -match "8000:8000") {
        Write-Host "✅ Ports corrects" -ForegroundColor Green
        $rapport += "  - Ports: 3000, 8000 ✅"
    } else {
        Write-Host "⚠️ Ports incorrects" -ForegroundColor Red
        $rapport += "  - Ports: ❌ Incorrects"
        $configIssues += "Ports incorrects dans docker-compose.yml"
    }
    
    # Vérifier les variables d'environnement
    if ($dockerCompose -match "MYSQL_ROOT|POSTGRES_DB") {
        Write-Host "⚠️ Variables d'environnement codées en dur" -ForegroundColor Red
        $rapport += "  - Variables: ❌ Codées en dur"
        $configIssues += "Variables d'environnement codées en dur"
    } else {
        Write-Host "✅ Variables d'environnement externes" -ForegroundColor Green
        $rapport += "  - Variables: ✅ Externes"
    }
} else {
    Write-Host "❌ docker-compose.yml non trouvé" -ForegroundColor Red
    $rapport += "❌ **docker-compose.yml**: Non trouvé"
    $configIssues += "docker-compose.yml manquant"
}

# Vérifier package.json
if (Test-Path ".\package.json") {
    $packageJson = Get-Content ".\package.json" -Raw | ConvertFrom-Json
    Write-Host "✅ package.json trouvé" -ForegroundColor Green
    $rapport += "✅ **package.json**: Trouvé"
    
    # Vérifier les dépendances
    $totalDeps = $packageJson.dependencies.PSObject.Properties.Count + $packageJson.devDependencies.PSObject.Properties.Count
    $rapport += "  - Dépendances: $totalDeps"
    
    # Vérifier les scripts
    if ($packageJson.scripts) {
        $scriptCount = $packageJson.scripts.PSObject.Properties.Count
        Write-Host "✅ Scripts npm: $scriptCount" -ForegroundColor Green
        $rapport += "  - Scripts: $scriptCount ✅"
    } else {
        Write-Host "⚠️ Aucun script npm" -ForegroundColor Yellow
        $rapport += "  - Scripts: ❌ Aucun"
        $configIssues += "Aucun script npm trouvé"
    }
} else {
    Write-Host "❌ package.json non trouvé" -ForegroundColor Red
    $rapport += "❌ **package.json**: Non trouvé"
    $configIssues += "package.json manquant"
}

# =================================================================
# 4. SCAN DE LA BASE DE DONNÉES
# =================================================================

Write-Host "`n🗄️ SCAN DE LA BASE DE DONNÉES" -ForegroundColor Cyan
$rapport += "## 🗄️ SCAN DE LA BASE DE DONNÉES"
$rapport += ""

$sqlFiles = Get-ChildItem -Path ".\sql" -Filter "*.sql"
Write-Host "Fichiers SQL trouvés: $($sqlFiles.Count)" -ForegroundColor White
$rapport += "**Fichiers SQL**: $($sqlFiles.Count)"

$dbIssues = @()

foreach ($sqlFile in $sqlFiles) {
    $content = Get-Content $sqlFile.FullName -Raw
    $fileName = $sqlFile.Name
    
    if ($fileName -eq "schema.sql") {
        Write-Host "✅ Schema SQL trouvé" -ForegroundColor Green
        $rapport += "✅ **schema.sql**: Trouvé"
        
        # Vérifier les tables critiques
        if ($content -match "CREATE TABLE.*users.*password") {
            $rapport += "  - Table users avec password ✅"
        }
        
        if ($content -match "CREATE TABLE.*patients.*email.*UNIQUE") {
            $rapport += "  - Contrainte unique email patients ✅"
        }
        
        if ($content -match "CREATE TABLE.*devices.*patient_id") {
            $rapport += "  - Relation devices-patients ✅"
        }
    }
    
    if ($fileName -match "demo_seed") {
        Write-Host "✅ Données de démo trouvées" -ForegroundColor Green
        $rapport += "✅ **$fileName**: Données de démo"
    }
}

# =================================================================
# 5. SCAN DES TESTS
# =================================================================

Write-Host "`n🧪 SCAN DES TESTS" -ForegroundColor Cyan
$rapport += "## 🧪 SCAN DES TESTS"
$rapport += ""

$testFiles = @()
$testStats = @{
    UnitTests = 0
    IntegrationTests = 0
    E2ETests = 0
    Total = 0
}

# Chercher les fichiers de test
$testFiles += Get-ChildItem -Path "." -Filter "*.test.js" -Recurse
$testFiles += Get-ChildItem -Path "." -Filter "*.spec.js" -Recurse
$testFiles += Get-ChildItem -Path "." -Filter "*test*" -Recurse | Where-Object { $_.Extension -eq ".js" }

$testStats.Total = $testFiles.Count
Write-Host "Fichiers de test trouvés: $($testStats.Total)" -ForegroundColor White
$rapport += "**Fichiers de test**: $($testStats.Total)"

foreach ($testFile in $testFiles) {
    $relativePath = $testFile.FullName.Replace((Get-Location).Path, "").TrimStart("\")
    
    if ($relativePath -match "__tests__") {
        $testStats.UnitTests++
    } elseif ($relativePath -match "test\.js$") {
        $testStats.IntegrationTests++
    } else {
        $testStats.E2ETests++
    }
}

$rapport += "- **Tests unitaires**: $($testStats.UnitTests)"
$rapport += "- **Tests intégration**: $($testStats.IntegrationTests)"
$rapport += "- **Tests E2E**: $($testStats.E2ETests)"

# Vérifier Jest configuration
if (Test-Path ".\jest.config.js") {
    Write-Host "✅ Configuration Jest trouvée" -ForegroundColor Green
    $rapport += "✅ **jest.config.js**: Trouvé"
} else {
    Write-Host "❌ Configuration Jest non trouvée" -ForegroundColor Red
    $rapport += "❌ **jest.config.js**: Non trouvé"
}

# =================================================================
# 6. SCAN DE LA DOCUMENTATION
# =================================================================

Write-Host "`n📚 SCAN DE LA DOCUMENTATION" -ForegroundColor Cyan
$rapport += "## 📚 SCAN DE LA DOCUMENTATION"
$rapport += ""

$docFiles = Get-ChildItem -Path "." -Filter "*.md" -Recurse
Write-Host "Fichiers de documentation: $($docFiles.Count)" -ForegroundColor White
$rapport += "**Fichiers de documentation**: $($docFiles.Count)"

# Vérifier les documents critiques
$criticalDocs = @("README.md", "CHANGELOG.md", "CONTRIBUTING.md", "LICENSE")
foreach ($doc in $criticalDocs) {
    if (Test-Path ".\$doc") {
        Write-Host "✅ $doc trouvé" -ForegroundColor Green
        $rapport += "✅ **$doc**: Trouvé"
    } else {
        Write-Host "⚠️ $doc non trouvé" -ForegroundColor Yellow
        $rapport += "⚠️ **$doc**: Non trouvé"
    }
}

# Vérifier la documentation API
if (Test-Path ".\api\openapi.json") {
    Write-Host "✅ Documentation OpenAPI trouvée" -ForegroundColor Green
    $rapport += "✅ **openapi.json**: Trouvé"
} else {
    Write-Host "⚠️ Documentation OpenAPI non trouvée" -ForegroundColor Yellow
    $rapport += "⚠️ **openapi.json**: Non trouvé"
}

# =================================================================
# 7. SCAN DES SCRIPTS ET OUTILS
# =================================================================

Write-Host "`n🔧 SCAN DES SCRIPTS ET OUTILS" -ForegroundColor Cyan
$rapport += "## 🔧 SCAN DES SCRIPTS ET OUTILS"
$rapport += ""

$scriptFiles = Get-ChildItem -Path ".\scripts" -Filter "*.ps1" -Recurse
Write-Host "Scripts PowerShell: $($scriptFiles.Count)" -ForegroundColor White
$rapport += "**Scripts PowerShell**: $($scriptFiles.Count)"

# Catégoriser les scripts
$scriptCategories = @{
    Database = 0
    Dev = 0
    Hardware = 0
    Monitoring = 0
    Other = 0
}

foreach ($script in $scriptFiles) {
    $relativePath = $script.FullName.Replace((Get-Location).Path, "").TrimStart("\")
    
    if ($relativePath -match "db\\|database") { $scriptCategories.Database++ }
    elseif ($relativePath -match "dev\\|start") { $scriptCategories.Dev++ }
    elseif ($relativePath -match "hardware\\|firmware") { $scriptCategories.Hardware++ }
    elseif ($relativePath -match "monitoring\\|logs") { $scriptCategories.Monitoring++ }
    else { $scriptCategories.Other++ }
}

$rapport += "- **Database**: $($scriptCategories.Database)"
$rapport += "- **Dev**: $($scriptCategories.Dev)"
$rapport += "- **Hardware**: $($scriptCategories.Hardware)"
$rapport += "- **Monitoring**: $($scriptCategories.Monitoring)"
$rapport += "- **Autres**: $($scriptCategories.Other)"

# =================================================================
# 8. SYNTHÈSE DES PROBLÈMES
# =================================================================

Write-Host "`n📊 SYNTHÈSE DES PROBLÈMES" -ForegroundColor Yellow
$rapport += "## 📊 SYNTHÈSE DES PROBLÈMES"
$rapport += ""

$totalIssues = $phpIssues.Count + $jsIssues.Count + $configIssues.Count
Write-Host "Total des problèmes: $totalIssues" -ForegroundColor $(
    if ($totalIssues -eq 0) { "Green" } elseif ($totalIssues -lt 10) { "Yellow" } else { "Red" }
)
$rapport += "**Total des problèmes**: $totalIssues"

# Catégoriser les problèmes
$allIssues = @()
$allIssues += $phpIssues | ForEach-Object { $_.Type = "PHP - $($_.Type)"; $_ }
$allIssues += $jsIssues | ForEach-Object { $_.Type = "JS - $($_.Type)"; $_ }

if ($allIssues.Count -gt 0) {
    $rapport += ""
    $rapport += "### 🔧 Problèmes détectés:"
    
    foreach ($issue in $allIssues) {
        $rapport += "- **$($issue.Fichier)**: $($_.Problème) (ligne $($_.Ligne))"
    }
    
    Write-Host "`n⚠️ Problèmes trouvés:" -ForegroundColor Red
    foreach ($issue in $allIssues) {
        Write-Host "  ❌ $($issue.Fichier): $($issue.Problème)" -ForegroundColor Red
    }
} else {
    Write-Host "`n✅ Aucun problème critique trouvé!" -ForegroundColor Green
    $rapport += ""
    $rapport += "✅ **Aucun problème critique trouvé!**"
}

# =================================================================
# 9. SCORE FINAL
# =================================================================

Write-Host "`n📊 SCORE FINAL DE L'AUDIT" -ForegroundColor Green
$rapport += "## 📊 SCORE FINAL DE L'AUDIT"
$rapport += ""

$score = 100

# Déductions pour les problèmes
$score -= $phpIssues.Count * 2
$score -= $jsIssues.Count * 1
$score -= $configIssues.Count * 3

# Déductions pour les éléments manquants
if (-not (Test-Path ".\docker-compose.yml")) { $score -= 5 }
if (-not (Test-Path ".\package.json")) { $score -= 5 }
if (-not (Test-Path ".\README.md")) { $score -= 3 }
if ($testStats.Total -eq 0) { $score -= 5 }
if (-not (Test-Path ".\jest.config.js")) { $score -= 3 }

Write-Host "Score final: $score/100" -ForegroundColor $(
    if ($score -ge 90) { "Green" } 
    elseif ($score -ge 70) { "Yellow" } 
    else { "Red" }
)
$rapport += "**Score final**: $score/100"

# =================================================================
# 10. CONCLUSION
# =================================================================

Write-Host "`n🎯 CONCLUSION DE L'AUDIT" -ForegroundColor Green
$rapport += "## 🎯 CONCLUSION DE L'AUDIT"
$rapport += ""

if ($score -ge 90) {
    Write-Host "✅ EXCELLENT - Projet en très bon état" -ForegroundColor Green
    $rapport += "✅ **EXCELLENT** - Projet en très bon état"
} elseif ($score -ge 70) {
    Write-Host "✅ BON - Projet en bon état avec quelques améliorations possibles" -ForegroundColor Yellow
    $rapport += "✅ **BON** - Projet en bon état avec quelques améliorations possibles"
} else {
    Write-Host "❌ À AMÉLIORER - Projet nécessite des corrections importantes" -ForegroundColor Red
    $rapport += "❌ **À AMÉLIORER** - Projet nécessite des corrections importantes"
}

# =================================================================
# 11. RECOMMANDATIONS
# =================================================================

Write-Host "`n🚀 RECOMMANDATIONS PRIORITAIRES" -ForegroundColor Cyan
$rapport += "## 🚀 RECOMMANDATIONS PRIORITAIRES"
$rapport += ""

$recommendations = @()

# Priorité 1: Sécurité
$securityIssues = $allIssues | Where-Object { $_.Type -match "Sécurité" }
if ($securityIssues.Count -gt 0) {
    $recommendations += "1. 🔒 Corriger les problèmes de sécurité ($($securityIssues.Count) problèmes)"
    foreach ($issue in $securityIssues) {
        $recommendations += "   - $($issue.Fichier): $($issue.Problème)"
    }
}

# Priorité 2: Performance
$perfIssues = $allIssues | Where-Object { $_.Type -match "Performance" }
if ($perfIssues.Count -gt 0) {
    $recommendations += "2. ⚡ Optimiser les performances ($($perfIssues.Count) problèmes)"
    foreach ($issue in $perfIssues) {
        $recommendations += "   - $($issue.Fichier): $($issue.Problème)"
    }
}

# Priorité 3: Qualité
$qualityIssues = $allIssues | Where-Object { $_.Type -match "Qualité" }
if ($qualityIssues.Count -gt 0) {
    $recommendations += "3. 🧹 Améliorer la qualité du code ($($qualityIssues.Count) problèmes)"
    foreach ($issue in $qualityIssues) {
        $recommendations += "   - $($issue.Fichier): $($issue.Problème)"
    }
}

# Priorité 4: Tests
if ($testStats.Total -eq 0) {
    $recommendations += "4. 🧪 Implémenter les tests unitaires et d'intégration"
}

# Priorité 5: Documentation
if (-not (Test-Path ".\api\openapi.json")) {
    $recommendations += "5. 📚 Documenter l'API avec OpenAPI/Swagger"
}

foreach ($rec in $recommendations) {
    Write-Host $rec -ForegroundColor Cyan
    $rapport += "$rec"
}

# =================================================================
# 12. SAUVEGARDER LE RAPPORT
# =================================================================

$rapport += ""
$rapport += "---"
$rapport += "*Audit complet terminé le $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')*"
$rapport += "*Projet OTT - Scan de tous les modules*"

$rapportPath = ".\AUDIT_COMPLET_VRAI_RAPPORT.md"
$rapport | Out-File -FilePath $rapportPath -Encoding UTF8

Write-Host "`n📄 Rapport sauvegardé dans: $rapportPath" -ForegroundColor Green

# =================================================================
# 13. RÉCAPITULATIF FINAL
# =================================================================

Write-Host "`n`n📊 RÉCAPITULATIF FINAL DE L'AUDIT COMPLET" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "📄 Fichiers PHP: $($phpFiles.Count)" -ForegroundColor White
Write-Host "📄 Fichiers JS: $($jsFiles.Count)" -ForegroundColor White
Write-Host "📄 Fichiers SQL: $($sqlFiles.Count)" -ForegroundColor White
Write-Host "📄 Scripts PS1: $($scriptFiles.Count)" -ForegroundColor White
Write-Host "📄 Documentation: $($docFiles.Count)" -ForegroundColor White
Write-Host "📄 Tests: $($testStats.Total)" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "🔍 Problèmes trouvés: $totalIssues" -ForegroundColor $(
    if ($totalIssues -eq 0) { "Green" } elseif ($totalIssues -lt 10) { "Yellow" } else { "Red" }
)
Write-Host "📊 Score final: $score/100" -ForegroundColor $(
    if ($score -ge 90) { "Green" } 
    elseif ($score -ge 70) { "Yellow" } 
    else { "Red" }
)

Write-Host "`n🎉 AUDIT COMPLET TERMINÉ" -ForegroundColor Green
