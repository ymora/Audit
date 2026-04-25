# ===============================================================================
# CONFIGURATION AUDIT - Projet OTT
# ===============================================================================

@{
    # Informations du projet
    Project = @{
        Name = "OTT"
        Company = "Votre Société"
        Description = "Projet OTT de gestion de contenu"
    }

    # Configuration API
    Api = @{
        BaseUrl = "https://api.ott.com"
        AuthEndpoint = "/api/auth/login"
        Endpoints = @(
            @{ Path = "/api/firmwares"; Name = "Firmwares" }
            @{ Path = "/api/devices"; Name = "Devices" }
            @{ Path = "/api/health"; Name = "Healthcheck" }
        )
    }

    # Routes de l'application
    Routes = @(
        @{ Route = "/dashboard"; File = "app/dashboard/page.js"; Name = "Dashboard" }
        @{ Route = "/firmwares"; File = "app/firmwares/page.js"; Name = "Firmwares" }
    )

    # Configuration spécifique OTT
    OTT = @{
        FirmwarePath = "d:\\Windsurf\\OTT\\api\\handlers\\firmwares"
        CompilePath = "d:\\Windsurf\\OTT\\api\\handlers\\compile_optimized.php"
    }
}
