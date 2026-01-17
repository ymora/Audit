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
    
    # Fonctions de logging fallback si non disponibles
    if (-not (Get-Command Write-PhaseSection -ErrorAction SilentlyContinue)) {
        function Write-PhaseSection { param($PhaseNumber, $Title) Write-Host "=== Phase $PhaseNumber : $Title ===" -ForegroundColor Cyan }
    }
    if (-not (Get-Command Write-Info -ErrorAction SilentlyContinue)) {
        function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Gray }
    }
    
    Write-PhaseSection -PhaseNumber 14 -Title "Génération Questions IA"
    
    # Détecter le type de projet et charger les questions appropriées
    $projectType = Detect-ProjectType -ProjectInfo $ProjectInfo -Files $Files
    Write-Info "Projet détecté: $projectType"
    
    # Charger les questions spécifiques au projet
    $aiQuestions = Get-ProjectSpecificQuestions -ProjectType $projectType -Files $Files -Config $Config
    
    Write-Info "Questions IA enrichies générées"
    
    # Calculer un score de qualité IA
    $totalQuestions = ($aiQuestions.SemanticAnalysis.Count + $aiQuestions.RefactoringAdvice.Count + $aiQuestions.ArchitectureReview.Count + $aiQuestions.SecurityReview.Count)
    $highPriorityCount = ($aiQuestions.SemanticAnalysis + $aiQuestions.RefactoringAdvice + $aiQuestions.ArchitectureReview + $aiQuestions.SecurityReview | Where-Object { $_.Priority -eq "high" }).Count
    $qualityScore = [math]::Max(0, 100 - ($highPriorityCount * 15) - ($totalQuestions * 5))
    
    Write-Info "Score de qualité IA: $qualityScore/100"
    Write-Info "Nombre de questions: $totalQuestions ($highPriorityCount priorité HAUTE)"
    
    # Forcer la sauvegarde dans la variable globale Results même en cas d'erreur
    try {
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
            ProjectType = $projectType
        }
        
        # Aussi sauvegarder dans script:Results pour être sûr
        if (-not $script:Results.AIContext) {
            $script:Results.AIContext = @{}
        }
        $script:Results.AIContext = $Results.AIContext
        
        # Générer directement le fichier ai-context dans le dossier de sortie du projet
        $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
        $contextFile = Join-Path $script:Config.OutputDir "ai-context-$timestamp.json"
        $Results.AIContext | ConvertTo-Json -Depth 10 | Out-File -FilePath $contextFile -Encoding UTF8
        
        Write-Info "Questions enrichies sauvegardées dans AIContext et $contextFile"
    } catch {
        Write-Host "[ERROR] Erreur lors de la sauvegarde: $($_.Exception.Message)" -ForegroundColor Red
        # Forcer quand même la sauvegarde minimale
        $script:Results.AIContext = @{
            SemanticAnalysis = @{ Questions = $aiQuestions.SemanticAnalysis }
            RefactoringAdvice = @{ Questions = $aiQuestions.RefactoringAdvice }
            ArchitectureReview = @{ Questions = $aiQuestions.ArchitectureReview }
            SecurityReview = @{ Questions = $aiQuestions.SecurityReview }
            QualityMetrics = @{
                Score = $qualityScore
                TotalQuestions = $totalQuestions
                HighPriorityCount = $highPriorityCount
                Categories = @("SemanticAnalysis", "RefactoringAdvice", "ArchitectureReview", "SecurityReview")
                ProjectType = $projectType
            }
        }
        
        # Même en cas d'erreur, générer le fichier
        try {
            $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
            $contextFile = Join-Path $script:Config.OutputDir "ai-context-$timestamp.json"
            $script:Results.AIContext | ConvertTo-Json -Depth 10 | Out-File -FilePath $contextFile -Encoding UTF8
        } catch {
            Write-Host "[ERROR] Impossible de générer le fichier de contexte" -ForegroundColor Red
        }
    }
    
    # Retourner le résultat pour confirmation
    return @{
        Success = $true
        QuestionsGenerated = $totalQuestions
        QualityScore = $qualityScore
        AIContext = $Results.AIContext
        ProjectType = $projectType
    }
}

# Wrapper compatible avec le chargeur de modules (Checks-*.ps1)
function Invoke-Check-AI-QuestionGenerator {
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
    
    return Invoke-AIQuestionGenerator -Files $Files -Config $Config -Results $Results -ProjectInfo $ProjectInfo
}

# ===============================================================================
# FONCTIONS DE DÉTECTION ET GÉNÉRATION SPÉCIFIQUES
# ===============================================================================

function Detect-ProjectType {
    param(
        [hashtable]$ProjectInfo,
        [array]$Files
    )
    
    # Analyser les fichiers et configuration pour déterminer le type de projet
    $projectRoot = $ProjectInfo.ProjectRoot
    
    # Détecter OTT (projet médical)
    if ((Test-Path (Join-Path $projectRoot "api.php")) -and 
        (Test-Path (Join-Path $projectRoot "components")) -and
        (Test-Path (Join-Path $projectRoot "contexts/AuthContext.js"))) {
        return "OTT"
    }
    
    # Détecter Haies (projet écologique) - amélioration
    $haiesIndicators = 0
    if (Test-Path (Join-Path $projectRoot "client")) { $haiesIndicators += 2 }
    if (Test-Path (Join-Path $projectRoot "admin")) { $haiesIndicators += 2 }
    if (Test-Path (Join-Path $projectRoot "get_images.php")) { $haiesIndicators += 1 }
    if (Test-Path (Join-Path $projectRoot "server.js")) { $haiesIndicators += 1 }
    
    # Vérifier les fichiers avec noms spécifiques
    $specificFiles = @("arbuste*", "haie*", "bessancourt*", "vegetal*", "plant*")
    foreach ($pattern in $specificFiles) {
        if ($Files | Where-Object { $_.Name -like $pattern -or $_.Directory -like $pattern }) {
            $haiesIndicators += 1
        }
    }
    
    # Vérifier les dossiers spécifiques
    $specificDirs = @("client/src/data", "client/src/components", "admin/server")
    foreach ($dir in $specificDirs) {
        if (Test-Path (Join-Path $projectRoot $dir)) {
            $haiesIndicators += 1
        }
    }
    
    if ($haiesIndicators -ge 3) {
        return "Haies"
    }
    
    # Détecter DocuSense (projet documentation)
    $docuSenseIndicators = 0
    if (Test-Path (Join-Path $projectRoot ".docs")) { $docuSenseIndicators += 2 }
    if (Test-Path (Join-Path $projectRoot "README.md")) { $docuSenseIndicators += 1 }
    if ($Files | Where-Object { $_.Name -like "*doc*" -or $_.Directory -like "*doc*" }) {
        $docuSenseIndicators += 1
    }
    
    if ($docuSenseIndicators -ge 2) {
        return "DocuSense"
    }
    
    # Par défaut, retourner "Generic"
    return "Generic"
}

function Get-ProjectSpecificQuestions {
    param(
        [string]$ProjectType,
        [array]$Files,
        [hashtable]$Config
    )
    
    switch ($ProjectType) {
        "OTT" {
            return Get-OTTQuestions -Files $Files
        }
        "Haies" {
            return Get-HaiesQuestions -Files $Files
        }
        "DocuSense" {
            return Get-DocuSenseQuestions -Files $Files
        }
        default {
            return Get-GenericQuestions -Files $Files
        }
    }
}

function Get-OTTQuestions {
    param([array]$Files)
    
    return @{
        SemanticAnalysis = @(
            @{
                Type = "MissingAccessibility"
                File = "components/DeviceModal.js"
                Issue = "Composants modaux sans attributs ARIA complets"
                Question = "Les composants modaux comme DeviceModal.js ont-ils des attributs ARIA appropriés (role, aria-modal, aria-label) ?"
                Priority = "medium"
                Severity = "medium"
                Suggestion = "Ajouter role='dialog', aria-modal='true' et aria-label sur tous les modaux"
            },
            @{
                Type = "HardcodedText"
                File = "components/Login.js"
                Issue = "Textes hardcodés en français détectés"
                Question = "Le composant Login.js contient des textes hardcodés en français. Faut-il implémenter un système d'internationalisation (i18n) ?"
                Priority = "low"
                Severity = "low"
                Suggestion = "Utiliser next-i18next pour l'internationalisation"
            },
            @{
                Type = "MedicalDataValidation"
                File = "api.php"
                Issue = "Validation des données médicales insuffisante"
                Question = "Les données médicales (patients, dispositifs) sont-elles validées côté serveur avec des schémas stricts ?"
                Priority = "high"
                Severity = "high"
                Suggestion = "Implémenter une validation avec des schémas JSON pour toutes les données médicales"
            }
        )
        RefactoringAdvice = @(
            @{
                Type = "LargeComponent"
                File = "components/DeviceModal.js"
                Lines = 8639
                Question = "Le composant DeviceModal.js a 8639 caractères. Faut-il le découper en sous-composants plus petits ?"
                Priority = "medium"
                Severity = "medium"
                Suggestion = "Découper en DeviceForm, DeviceList, DeviceActions"
            },
            @{
                Type = "ComplexAPI"
                File = "api.php"
                Lines = 331
                Question = "Le fichier api.php semble complexe. Faut-il le refactoriser en plusieurs fichiers handlers ?"
                Priority = "medium"
                Severity = "medium"
                Suggestion = "Séparer les handlers par entité (devices, patients, users)"
            }
        )
        ArchitectureReview = @(
            @{
                Type = "MissingErrorHandling"
                File = "components/DeviceDashboard.js"
                Issue = "Hooks React sans gestion d'erreur"
                Question = "Le composant DeviceDashboard.js utilise des hooks React mais semble avoir une gestion d'erreur limitée. Faut-il améliorer les try/catch ?"
                Priority = "medium"
                Severity = "medium"
                Suggestion = "Ajouter des ErrorBoundary et try/catch dans les hooks async"
            },
            @{
                Type = "APIArchitecture"
                File = "api.php"
                Issue = "Architecture API monolithique"
                Question = "L'API utilise-t-elle une architecture appropriée pour un système médical ? Faut-il ajouter des middlewares ?"
                Priority = "medium"
                Severity = "medium"
                Suggestion = "Implémenter des middlewares pour auth, validation, logging"
            }
        )
        SecurityReview = @(
            @{
                Type = "DataValidation"
                File = "api.php"
                Issue = "Validation des données médicales"
                Question = "Les données médicales envoyées à l'API sont-elles validées côté serveur ? Faut-il renforcer la sécurité ?"
                Priority = "high"
                Severity = "high"
                Suggestion = "Ajouter validation stricte avec schémas JSON et sanitization"
            },
            @{
                Type = "Authentication"
                File = "contexts/AuthContext.js"
                Issue = "Sécurité de l'authentification"
                Question = "Le contexte d'authentification gère-t-il correctement les tokens et la sécurité ?"
                Priority = "high"
                Severity = "high"
                Suggestion = "Vérifier expiry tokens, refresh token, secure storage"
            }
        )
    }
}

function Get-HaiesQuestions {
    param([array]$Files)
    
    return @{
        SemanticAnalysis = @(
            @{
                Type = "MissingAccessibility"
                File = "client/src/App-clean.jsx"
                Issue = "Boutons sans attributs ARIA"
                Question = "Le fichier 'App-clean.jsx' a des boutons sans attributs ARIA. Faut-il ajouter aria-label ou title pour l'accessibilité ?"
                Priority = "medium"
                Severity = "medium"
                Suggestion = "Ajouter aria-label sur tous les boutons interactifs"
            },
            @{
                Type = "HardcodedText"
                File = "client/src/App-clean.jsx"
                Issue = "Textes hardcodés détectés"
                Question = "Le fichier 'App-clean.jsx' contient des textes hardcodés comme 'Haies Bessancourt'. Faut-il implémenter un système d'internationalisation (i18n) ?"
                Priority = "low"
                Severity = "low"
                Suggestion = "Utiliser react-i18next pour l'internationalisation"
            },
            @{
                Type = "DomainSpecificData"
                File = "client/src/data/arbustesData.js"
                Issue = "Données botaniques potentiellement incorrectes"
                Question = "Les données botaniques (plantation, entretien) sont-elles cohérentes avec le climat de Bessancourt ? Faut-il valider les informations ?"
                Priority = "high"
                Severity = "high"
                Suggestion = "Valider les données avec un expert botanique local"
            }
        )
        RefactoringAdvice = @(
            @{
                Type = "LargeComponent"
                File = "client/src/App-clean.jsx"
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
                File = "client/src/App-clean.jsx"
                Issue = "Hooks React sans gestion d'erreur"
                Question = "Le fichier 'App-clean.jsx' utilise des hooks React mais ne semble pas avoir de gestion d'erreur. Faut-il ajouter des try/catch ?"
                Priority = "medium"
                Severity = "medium"
                Suggestion = "Ajouter ErrorBoundary et try/catch dans les hooks"
            },
            @{
                Type = "UXNavigation"
                File = "client/src/App-clean.jsx"
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
}

function Get-DocuSenseQuestions {
    param([array]$Files)
    
    return @{
        SemanticAnalysis = @(
            @{
                Type = "DocumentationQuality"
                File = "README.md"
                Issue = "Qualité de la documentation"
                Question = "La documentation est-elle complète et à jour pour un projet IA ?"
                Priority = "medium"
                Severity = "medium"
                Suggestion = "Améliorer la documentation technique et utilisateur"
            }
        )
        RefactoringAdvice = @(
            @{
                Type = "CodeOrganization"
                File = "src/"
                Issue = "Organisation du code"
                Question = "Le code est-il bien organisé pour un projet d'IA documentaire ?"
                Priority = "medium"
                Severity = "medium"
                Suggestion = "Structurer le code par modules fonctionnels"
            }
        )
        ArchitectureReview = @(
            @{
                Type = "AIIntegration"
                File = "src/"
                Issue = "Intégration IA"
                Question = "L'intégration IA est-elle bien architecturée ?"
                Priority = "high"
                Severity = "high"
                Suggestion = "Optimiser l'architecture pour les traitements IA"
            }
        )
        SecurityReview = @(
            @{
                Type = "DataPrivacy"
                File = "src/"
                Issue = "Confidentialité des données"
                Question = "Les données utilisateur sont-elles protégées conformément au RGPD ?"
                Priority = "high"
                Severity = "high"
                Suggestion = "Implémenter chiffrement et anonymisation"
            }
        )
    }
}

function Get-GenericQuestions {
    param([array]$Files)
    
    return @{
        SemanticAnalysis = @(
            @{
                Type = "CodeQuality"
                File = "src/"
                Issue = "Qualité générale du code"
                Question = "Le code respecte-t-il les bonnes pratiques de développement ?"
                Priority = "medium"
                Severity = "medium"
                Suggestion = "Appliquer les standards de codage et linting"
            }
        )
        RefactoringAdvice = @(
            @{
                Type = "Structure"
                File = "src/"
                Issue = "Structure du projet"
                Question = "La structure du projet est-elle cohérente et maintenable ?"
                Priority = "medium"
                Severity = "medium"
                Suggestion = "Organiser le code en modules logiques"
            }
        )
        ArchitectureReview = @(
            @{
                Type = "DesignPatterns"
                File = "src/"
                Issue = "Patrons de conception"
                Question = "Les patrons de conception utilisés sont-ils appropriés ?"
                Priority = "medium"
                Severity = "medium"
                Suggestion = "Appliquer les patrons de conception standards"
            }
        )
        SecurityReview = @(
            @{
                Type = "BasicSecurity"
                File = "src/"
                Issue = "Sécurité de base"
                Question = "Les mesures de sécurité de base sont-elles en place ?"
                Priority = "high"
                Severity = "high"
                Suggestion = "Implémenter validation et authentification"
            }
        )
    }
}
