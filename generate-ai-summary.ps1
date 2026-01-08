# ===============================================================================
# GENERE LE RESUME IA A PARTIR DU DERNIER AUDIT
# Usage: .\audit\generate-ai-summary.ps1
# ===============================================================================

param(
    [string]$ResultsDir = (Join-Path $PSScriptRoot "resultats"),
    [string]$ProjectName = ""
)

Write-Host "[IA] Generation du resume IA..." -ForegroundColor Cyan

# Si un projet est spécifié, utiliser son dossier
if ($ProjectName) {
    $ResultsDir = Join-Path $ResultsDir $ProjectName.ToLower()
}

# Trouver le dernier fichier AI-SUMMARY existant ou le dernier audit
$summaryFile = Join-Path $ResultsDir "AI-SUMMARY.md"
$latestContext = Get-ChildItem -Path $ResultsDir -Filter "ai-context-*.json" -ErrorAction SilentlyContinue | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 1

if (-not $latestContext) {
    Write-Host "[ERR] Aucun fichier ai-context trouve. Lancez d'abord un audit complet." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Fichier source: $($latestContext.Name)" -ForegroundColor Gray

# Lire le contexte avec encodage UTF-8 explicite
$context = Get-Content $latestContext.FullName -Raw -Encoding UTF8 | ConvertFrom-Json

# Obtenir le type de projet depuis les métriques si disponible
$projectType = if ($context.QualityMetrics.ProjectType) { 
    $context.QualityMetrics.ProjectType 
} else { 
    "Inconnu" 
}

# Générer le résumé
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
$projectPath = if ($context.ProjectInfo) { $context.ProjectInfo.ProjectRoot } else { "N/A" }

$summary = "# AUDIT IA - VERIFICATION ET CORRECTIONS`n"
$summary += "> Genere: $timestamp | Projet: $projectPath`n`n"
$summary += "## INSTRUCTIONS`n"
$summary += "Pour chaque probleme, verifier le code et repondre:`n"
$summary += "- **FAUX POSITIF** : expliquer pourquoi ce n'est pas un vrai probleme`n"
$summary += "- **A CORRIGER** : proposer le fix avec extrait de code`n`n"
$summary += "## SCORES ACTUELS`n"
$summary += "| Categorie | Score | Status |`n"
$summary += "|-----------|-------|--------|`n`n"
$summary += "---`n`n"
$summary += "## PROBLEMES A ANALYSER`n`n"

# Extraire et formater les questions depuis AIContext
$questionId = 1
$categories = @("SemanticAnalysis", "RefactoringAdvice", "ArchitectureReview", "SecurityReview")

foreach ($categoryName in $categories) {
    if ($context.$categoryName -and $context.$categoryName.Questions) {
        $summary += "### $categoryName`n`n"
        
        foreach ($q in $context.$categoryName.Questions) {
            $priority = switch ($q.Priority) {
                "high" { "IMPORTANT" }
                "medium" { "MOYEN" }
                "low" { "INFO" }
                default { "MOYEN" }
            }
            
            $summary += "#### [$questionId] $($q.Type) - $priority`n"
            $summary += "- **Fichier**: ``$($q.File)```n"
            $summary += "- **Question**: $($q.Question)`n"
            $summary += "- **Suggestion**: $($q.Suggestion)`n`n"
            
            $questionId++
        }
    }
}

$summary += "---`n`n"
$summary += "## MÉTRIQUES DE QUALITÉ IA`n`n"

if ($context.QualityMetrics) {
    $summary += "- **Score de qualité**: $($context.QualityMetrics.Score)/100`n"
    $summary += "- **Nombre de questions**: $($context.QualityMetrics.TotalQuestions)`n"
    $summary += "- **Priorité HAUTE**: $($context.QualityMetrics.HighPriorityCount)`n"
    $summary += "- **Catégories couvertes**: $($context.QualityMetrics.Categories -join ', ')`n"
    $summary += "- **Spécifique domaine**: $projectType`n"
} else {
    $summary += "- **Score de qualité**: N/A`n"
    $summary += "- **Nombre de questions**: $questionId`n"
    $summary += "- **Priorité HAUTE**: N/A`n"
    $summary += "- **Catégories couvertes**: SemanticAnalysis, RefactoringAdvice, ArchitectureReview, SecurityReview`n"
    $summary += "- **Spécifique domaine**: $projectType`n"
}

$summary += "`n---`n`n"
$summary += "## FORMAT DE REPONSE ATTENDU`n`n"
$summary += "Pour chaque probleme:`n"
$summary += "`````n"
$summary += "### [ID] Verdict: FAUX POSITIF | A CORRIGER`n"
$summary += "Explication: ...`n"
$summary += "Fix propose (si applicable):`n"
$summary += "// code...`n"
$summary += "`````n`n"

# Sauvegarder
$summary | Out-File -FilePath $summaryFile -Encoding UTF8 -Force

Write-Host "[OK] Resume genere: $summaryFile" -ForegroundColor Green
Write-Host "[OK] Projet détecté: $projectType" -ForegroundColor Cyan
Write-Host ""
Write-Host "Statistiques:" -ForegroundColor Cyan
Write-Host "- Questions générées: $($questionId - 1)" -ForegroundColor Gray
Write-Host "- Type de projet: $projectType" -ForegroundColor Gray
