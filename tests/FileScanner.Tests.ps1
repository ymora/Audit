$root = Resolve-Path (Join-Path $PSScriptRoot "..")
. (Join-Path $root "modules/FileScanner.ps1")

Describe "FileScanner" {
    It "collecte des fichiers du projet" {
        $config = @{ Exclude = @{ Directories = @(); Files = @() } }
        $files = Get-ProjectFiles -Path $root -Config $config
        ($files.Count -gt 0) | Should -BeTrue
    }
}

