$root = Resolve-Path (Join-Path $PSScriptRoot "..")

Describe "Project profile audit" {
    It "charge le profil audit" {
        $profilePath = Join-Path $root "projects/audit/project.ps1"
        $profile = . $profilePath
        ($profile.Id -eq "audit") | Should -BeTrue
    }
}

