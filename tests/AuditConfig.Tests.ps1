$root = Resolve-Path (Join-Path $PSScriptRoot "..")

Describe "Audit config" {
    It "charge la configuration globale" {
        $configPath = Join-Path $root "config/audit.config.ps1"
        $cfg = . $configPath
        ($cfg -is [hashtable]) | Should -BeTrue
    }
}

