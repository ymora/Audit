$root = Resolve-Path (Join-Path $PSScriptRoot "..")
. (Join-Path $root "modules/Utils.ps1")

Describe "Normalize-ScoreKey" {
    It "mappe les clés connues" {
        (Normalize-ScoreKey -Key "CodeQuality") | Should -Be "Qualité de Code"
        (Normalize-ScoreKey -Key "ConfigConsistency") | Should -Be "Cohérence Configuration"
        (Normalize-ScoreKey -Key "MarkdownQuality") | Should -Be "MarkdownFiles"
    }
}

Describe "Calculate-GlobalScore" {
    It "calcule la moyenne pondérée" {
        $results = @{ Scores = @{ "Security" = 10; "Inventory" = 8 } }
        $config = @{ ScoreWeights = @{ "Security" = 2; "Inventory" = 1 } }
        (Calculate-GlobalScore -Results $results -Config $config) | Should -Be 9.3
    }
}

