# Audit simple et complet du projet OTT

Write-Host "🚀 AUDIT COMPLET DU PROJET OTT" -ForegroundColor Green

# 1. Compter les fichiers
$phpFiles = Get-ChildItem -Path "." -Filter "*.php" -Recurse | Measure-Object | Select-Object Count
$jsFiles = Get-ChildItem -Path "." -Filter "*.js" -Recurse | Measure-Object | Select-Object Count
$sqlFiles = Get-ChildItem -Path "." -Filter "*.sql" -Recurse | Measure-Object | Select-Object Count
$mdFiles = Get-ChildItem -Path "." -Filter "*.md" -Recurse | Measure-Object | Select-Object Count
$ps1Files = Get-ChildItem -Path "." -Filter "*.ps1" -Recurse | Measure-Object | Select-Object Count

Write-Host "📁 STRUCTURE DES FICHIERS" -ForegroundColor Cyan
Write-Host "  PHP: $($phpFiles.Count)" -ForegroundColor White
Write-Host "  JS: $($jsFiles.Count)" -ForegroundColor White
Write-Host "  SQL: $($sqlFiles.Count)" -ForegroundColor White
Write-Host "  MD: $($mdFiles.Count)" -ForegroundColor White
Write-Host "  PS1: $($ps1Files.Count)" -ForegroundColor White

# 2. Scanner les problèmes PHP
Write-Host "`n🐘 SCAN PHP" -ForegroundColor Cyan
$phpIssues = 0

foreach ($file in Get-ChildItem -Path "." -Filter "*.php" -Recurse) {
    $content = Get-Content $file.FullName -Raw
    
    # Vérifier echo json_encode
    if ($content -match "echo json_encode.*success.*false.*error") {
        $phpIssues++
        Write-Host "  ❌ $($file.Name): echo json_encode avec succès=false" -ForegroundColor Red
    }
    
    # Vérifier var_dump/print_r
    if ($content -match "var_dump|print_r" -and $content -notmatch "//.*var_dump") {
        $phpIssues++
        Write-Host "  ⚠️ $($file.Name): Code de debug détecté" -ForegroundColor Yellow
    }
}

Write-Host "  Problèmes PHP: $phpIssues" -ForegroundColor $(
    if ($phpIssues -eq 0) { "Green" } elseif ($phpIssues -lt 5) { "Yellow" } else { "Red" }
)

# 3. Scanner les problèmes JS
Write-Host "`n📱 SCAN JS" -ForegroundColor Cyan
$jsIssues = 0

foreach ($file in Get-ChildItem -Path "." -Filter "*.js" -Recurse) {
    $content = Get-Content $file.FullName -Raw
    
    # Vérifier console.log
    if ($content -match "console\.log" -and $content -notmatch "//.*console\.log") {
        $jsIssues++
        Write-Host "  ⚠️ $($file.Name): console.log en production" -ForegroundColor Yellow
    }
    
    # Vérifier variables non utilisées
    if ($content -match "duplicateUser|duplicateDevice|duplicatePatient") {
        $jsIssues++
        Write-Host "  ⚠️ $($file.Name): Variables non utilisées" -ForegroundColor Yellow
    }
}

Write-Host "  Problèmes JS: $jsIssues" -ForegroundColor $(
    if ($jsIssues -eq 0) { "Green" } elseif ($jsIssues -lt 5) { "Yellow" } else { "Red" }
)

# 4. Vérifier la configuration
Write-Host "`n⚙️ CONFIGURATION" -ForegroundColor Cyan

if (Test-Path ".\docker-compose.yml") {
    Write-Host "  ✅ docker-compose.yml: Trouvé" -ForegroundColor Green
} else {
    Write-Host "  ❌ docker-compose.yml: Non trouvé" -ForegroundColor Red
}

if (Test-Path ".\package.json") {
    Write-Host "  ✅ package.json: Trouvé" -ForegroundColor Green
} else {
    Write-Host "  ❌ package.json: Non trouvé" -ForegroundColor Red
}

if (Test-Path ".\README.md") {
    Write-Host "  ✅ README.md: Trouvé" -ForegroundColor Green
} else {
    Write-Host "  ❌ README.md: Non trouvé" -ForegroundColor Red
}

# 5. Vérifier les tests
Write-Host "`n🧪 TESTS" -ForegroundColor Cyan

$testFiles = Get-ChildItem -Path "." -Filter "*.test.js" -Recurse
Write-Host "  Tests unitaires: $($testFiles.Count)" -ForegroundColor White

if (Test-Path ".\jest.config.js") {
    Write-Host "  ✅ jest.config.js: Trouvé" -ForegroundColor Green
} else {
    Write-Host "  ❌ jest.config.js: Non trouvé" -ForegroundColor Red
}

# 6. Score final
Write-Host "`n📊 SCORE FINAL" -ForegroundColor Green

$score = 100
$score -= $phpIssues * 2
$score -= $jsIssues * 1
if (-not (Test-Path ".\docker-compose.yml")) { $score -= 5 }
if (-not (Test-Path ".\package.json")) { $score -= 5 }
if (-not (Test-Path ".\README.md")) { $score -= 3 }
if ($testFiles.Count -eq 0) { $score -= 5 }

Write-Host "  Score: $score/100" -ForegroundColor $(
    if ($score -ge 90) { "Green" } 
    elseif ($score -ge 70) { "Yellow" } 
    else { "Red" }
)

# 7. Conclusion
Write-Host "`n🎯 CONCLUSION" -ForegroundColor Green

if ($score -ge 90) {
    Write-Host "✅ EXCELLENT - Projet en très bon état" -ForegroundColor Green
} elseif ($score -ge 70) {
    Write-Host "✅ BON - Projet en bon état" -ForegroundColor Yellow
} else {
    Write-Host "❌ À AMÉLIORER - Projet nécessite des corrections" -ForegroundColor Red
}

Write-Host "`n🎉 AUDIT TERMINÉ" -ForegroundColor Green
