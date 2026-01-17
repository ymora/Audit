$root = Resolve-Path (Join-Path $PSScriptRoot "..")
. (Join-Path $root "modules/Utils.ps1")
. (Join-Path $root "modules/ModuleLoader.ps1")

Describe "ModuleLoader" {
    It "trouve un module de base existant" {
        $path = Get-ModulePath -ModuleName "Checks-ProjectInventory.ps1" -ProjectName "" -BasePath (Join-Path $root "modules")
        ($null -ne $path -and (Test-Path $path)) | Should -BeTrue
    }
}

