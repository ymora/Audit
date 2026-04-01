# ===============================================================================
# INTÉGRATION IA AUTOMATIQUE DANS L'AUDIT
# ===============================================================================

function Invoke-AI-Analysis {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Problem,
        
        [Parameter(Mandatory=$true)]
        [string]$Context,
        
        [Parameter(Mandatory=$false)]
        [string]$Severity = "medium"
    )
    
    try {
        $prompt = @"
Analyse ce probleme d'audit pour DocuSense AI V2:

PROBLEME: $Problem
CONTEXTE: $Context
SEVERITE: $Severity

Donne un verdict unique:
- FAUX POSITIF : si ce n'est pas un vrai probleme pour DocSense
- A CORRIGER : si c'est un vrai probleme a resoudre

Format reponse: VERDICT: [FAUX POSITIF|A CORRIGER] | Raison courte
"@
        
        $body = @{
            model = "qwen2.5:3b"
            prompt = $prompt
            stream = $false
            options = @{
                temperature = 0.1
                num_predict = 50
            }
        } | ConvertTo-Json -Depth 5
        
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
        
        if ($response.response -match "VERDICT:\s*(FAUX POSITIF|A CORRIGER)") {
            $verdict = $matches[1]
            $reason = if ($response.response -match "\|\s*(.+)$") { $matches[1].Trim() } else { "" }
            
            return @{
                Verdict = $verdict
                Reason = $reason
                Success = $true
            }
        } else {
            return @{
                Verdict = "A CORRIGER"
                Reason = "Impossible d'analyser"
                Success = $false
            }
        }
        
    } catch {
        return @{
            Verdict = "A CORRIGER"
            Reason = "Erreur IA"
            Success = $false
        }
    }
}

function Test-AI-Integration {
    # Test simple pour vérifier si Ollama fonctionne
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
        return $response.models.Count -gt 0
    } catch {
        return $false
    }
}

Export-ModuleMember -Function Invoke-AI-Analysis, Test-AI-Integration
