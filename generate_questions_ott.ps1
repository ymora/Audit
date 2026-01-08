# Script pour générer les questions IA pour OTT
. .\modules\AI-QuestionGenerator.ps1

# Préparer les données
$files = Get-ChildItem -Path '../OTT' -Recurse -File
$config = @{}
$results = @{}
$projectInfo = @{
    Name = 'OTT'
    Type = 'Next.js'
    Language = 'JavaScript'
    Framework = 'Next.js'
}

# Exécuter le générateur
Invoke-AIQuestionGenerator -Files $files -Config $config -Results $results -ProjectInfo $projectInfo

# Afficher les questions générées
Write-Host "`n=== QUESTIONS IA GÉNÉRÉES POUR OTT ===" -ForegroundColor Cyan

if ($results.AIQuestions) {
    $totalQuestions = $results.AIQuestions.SemanticAnalysis.Count + 
                      $results.AIQuestions.RefactoringAdvice.Count + 
                      $results.AIQuestions.ArchitectureReview.Count +
                      $results.AIQuestions.SecurityReview.Count
    
    Write-Host "Total: $totalQuestions questions`n" -ForegroundColor Green
    
    # Questions par catégorie
    if ($results.AIQuestions.SemanticAnalysis.Count -gt 0) {
        Write-Host "📝 ANALYSE SÉMANTIQUE:" -ForegroundColor Yellow
        foreach ($q in $results.AIQuestions.SemanticAnalysis) {
            Write-Host "  [$($q.Priority.ToUpper())] $($q.Question)" -ForegroundColor White
        }
        Write-Host ""
    }
    
    if ($results.AIQuestions.RefactoringAdvice.Count -gt 0) {
        Write-Host "🔧 CONSEILS REFACTORING:" -ForegroundColor Yellow
        foreach ($q in $results.AIQuestions.RefactoringAdvice) {
            Write-Host "  [$($q.Priority.ToUpper())] $($q.Question)" -ForegroundColor White
        }
        Write-Host ""
    }
    
    if ($results.AIQuestions.ArchitectureReview.Count -gt 0) {
        Write-Host "🏗️ REVUE ARCHITECTURE:" -ForegroundColor Yellow
        foreach ($q in $results.AIQuestions.ArchitectureReview) {
            Write-Host "  [$($q.Priority.ToUpper())] $($q.Question)" -ForegroundColor White
        }
        Write-Host ""
    }
    
    if ($results.AIQuestions.SecurityReview.Count -gt 0) {
        Write-Host "🔒 REVUE SÉCURITÉ:" -ForegroundColor Yellow
        foreach ($q in $results.AIQuestions.SecurityReview) {
            Write-Host "  [$($q.Priority.ToUpper())] $($q.Question)" -ForegroundColor White
        }
        Write-Host ""
    }
} else {
    Write-Host "Aucune question générée" -ForegroundColor Red
}
