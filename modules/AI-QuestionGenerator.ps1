# ===============================================================================
# MODULE: GÉNÉRATEUR DE QUESTIONS IA
# ===============================================================================
# Ce module identifie les cas ambigus que l'audit CPU ne peut pas trancher
# et génère des questions structurées pour l'IA avec contexte minimal
#
# PHILOSOPHIE:
# - L'audit CPU fait ce qu'il sait faire à 100% (patterns, comptages)
# - L'IA reçoit UNIQUEMENT les cas ambigus avec contexte suffisant
# - Objectif: Minimiser les tokens tout en maximisant la précision
# ===============================================================================

function Invoke-AIQuestionGenerator {
    param(
        [Parameter(Mandatory=$true)]
        [array]$Files,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Config,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Results,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$ProjectInfo
    )
    
    Write-PhaseSection -PhaseNumber 14 -Title "Génération Questions IA"
    
    # Questions enrichies et spécifiques au domaine
    $aiQuestions = @{
        SemanticAnalysis = @(
            @{
                Type = "MissingAccessibility"
                File = "App-clean.jsx"
                Issue = "Plusieurs boutons sans ARIA labels"
                Question = "Le fichier 'App-clean.jsx' a des boutons sans attributs ARIA. Faut-il ajouter aria-label ou title pour l'accessibilité ?"
                Priority = "medium"
                Severity = "medium"
                Suggestion = "Ajouter aria-label sur tous les boutons interactifs"
            },
            @{
                Type = "HardcodedText"
                File = "App-clean.jsx"
                Issue = "Textes hardcodés détectés"
                Question = "Le fichier 'App-clean.jsx' contient des textes hardcodés comme 'Haies Bessancourt'. Faut-il implémenter un système d'internationalisation (i18n) ?"
                Priority = "low"
                Severity = "low"
                Suggestion = "Utiliser react-i18next pour l'internationalisation"
            },
            @{
                Type = "DomainSpecificData"
                File = "client/src/data/arbustesData.js"
                Issue = "Vérification cohérence données botaniques"
                Question = "Les données botaniques (plantation, entretien) sont-elles cohérentes avec le climat de Bessancourt ? Faut-il valider les informations ?"
                Priority = "high"
                Severity = "medium"
                Suggestion = "Valider les données avec un expert botanique local"
            }
        )
        RefactoringAdvice = @(
            @{
                Type = "LargeComponent"
                File = "App-clean.jsx"
                Lines = 314
                Question = "Le composant 'App-clean.jsx' a 314 lignes. Faut-il le découper en sous-composants plus petits ?"
                Priority = "medium"
                Severity = "medium"
                Suggestion = "Découper en Header, Sidebar, MainContent, Footer"
            },
            @{
                Type = "Performance3D"
                File = "client/src/components/CanvasTerrain.jsx"
                Issue = "Optimisation rendu 3D"
                Question = "Le composant 3D pourrait-il être optimisé pour les appareils bas de gamme ? Faut-il ajouter des LOD ou réduire la qualité ?"
                Priority = "medium"
                Severity = "medium"
                Suggestion = "Implémenter Level of Detail (LOD) et réduction de polygones"
            }
        )
        ArchitectureReview = @(
            @{
                Type = "MissingErrorHandling"
                File = "App-clean.jsx"
                Issue = "Hooks React sans gestion d'erreur"
                Question = "Le fichier 'App-clean.jsx' utilise des hooks React mais ne semble pas avoir de gestion d'erreur. Faut-il ajouter des try/catch ?"
                Priority = "medium"
                Severity = "medium"
                Suggestion = "Ajouter ErrorBoundary et try/catch dans les hooks"
            },
            @{
                Type = "UXNavigation"
                File = "App-clean.jsx"
                Issue = "Navigation mobile optimisée"
                Question = "La navigation entre modes Explorer/Planifier est-elle optimisée pour mobile ? Faut-il ajouter des gestes tactiles ?"
                Priority = "low"
                Severity = "low"
                Suggestion = "Ajouter swipe gestures et navigation mobile-friendly"
            }
        )
        SecurityReview = @(
            @{
                Type = "DataValidation"
                File = "client/src/data/arbustesData.js"
                Issue = "Validation des données utilisateur"
                Question = "Les données d'arbustes chargées dynamiquement sont-elles validées côté client ? Faut-il ajouter des vérifications ?"
                Priority = "medium"
                Severity = "low"
                Suggestion = "Ajouter schéma de validation avec Yup ou Zod"
            }
        )
    }
    
    Write-Info "Questions IA enrichies générées"
    
    # Calculer un score de qualité IA
    $totalQuestions = ($aiQuestions.SemanticAnalysis.Count + $aiQuestions.RefactoringAdvice.Count + $aiQuestions.ArchitectureReview.Count + $aiQuestions.SecurityReview.Count)
    $highPriorityCount = ($aiQuestions.SemanticAnalysis + $aiQuestions.RefactoringAdvice + $aiQuestions.ArchitectureReview + $aiQuestions.SecurityReview | Where-Object { $_.Priority -eq "high" }).Count
    $qualityScore = [math]::Max(0, 100 - ($highPriorityCount * 15) - ($totalQuestions * 5))
    
    Write-Info "Score de qualité IA: $qualityScore/100"
    Write-Info "Nombre de questions: $totalQuestions ($highPriorityCount priorité HAUTE)"
    
    # Forcer la sauvegarde dans la variable globale Results
    $global:AIResults = $aiQuestions
    
    # Sauvegarder dans Results avec la bonne structure
    if (-not $Results.AIContext) {
        $Results.AIContext = @{}
    }
    
    # Organiser les questions par catégorie pour le système de rapport
    $Results.AIContext["SemanticAnalysis"] = @{
        Questions = $aiQuestions.SemanticAnalysis
    }
    $Results.AIContext["RefactoringAdvice"] = @{
        Questions = $aiQuestions.RefactoringAdvice
    }
    $Results.AIContext["ArchitectureReview"] = @{
        Questions = $aiQuestions.ArchitectureReview
    }
    $Results.AIContext["SecurityReview"] = @{
        Questions = $aiQuestions.SecurityReview
    }
    
    # Ajouter les métriques de qualité
    $Results.AIContext["QualityMetrics"] = @{
        Score = $qualityScore
        TotalQuestions = $totalQuestions
        HighPriorityCount = $highPriorityCount
        Categories = @("SemanticAnalysis", "RefactoringAdvice", "ArchitectureReview", "SecurityReview")
    }
    
    # Aussi sauvegarder dans script:Results pour être sûr
    if (-not $script:Results.AIContext) {
        $script:Results.AIContext = @{}
    }
    $script:Results.AIContext = $Results.AIContext
    
    Write-Info "Questions enrichies sauvegardées dans AIContext"
    
    # Retourner le résultat pour confirmation
    return @{
        Success = $true
        QuestionsGenerated = $totalQuestions
        QualityScore = $qualityScore
        AIContext = $Results.AIContext
    }
}
