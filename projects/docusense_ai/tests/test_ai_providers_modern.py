#!/usr/bin/env python3
"""
Test modernisé des providers AI pour DocuSense AI.
Utilise le framework de tests génériques.
"""

import sys
from pathlib import Path

# Ajouter le framework de tests au path
audit_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(audit_dir))

from tests.generic.base_test import BaseProjectTest
from tests.generic.api_test import APITestMixin
from tests.generic.security_test import SecurityTestMixin

class AIProvidersTest(BaseProjectTest, APITestMixin, SecurityTestMixin):
    """Test des providers AI utilisant le framework générique."""
    
    async def run_test(self):
        """Exécute le test des providers AI."""
        print("🤖 Test des providers AI (version modernisée)...")
        
        # Vérifier que l'API backend est accessible
        backend_ports = self.get_project_config("backend_ports", [8000])
        base_url = f"http://localhost:{backend_ports[0]}"
        
        health_result = self.test_api_health(base_url)
        if not health_result["success"]:
            self.log_failure("Backend non accessible", health_result.get("error"))
            return self.results
        
        # Tester les endpoints des providers AI
        ai_endpoints = [
            {"name": "providers_list", "url": "/api/config/ai/providers"},
            {"name": "functional_providers", "url": "/api/config/ai/providers/functional"},
        ]
        
        api_results = self.batch_test_endpoints(base_url, ai_endpoints)
        
        if api_results["success"]:
            self.log_success(
                f"Tous les providers AI testés avec succès ({api_results['passed']}/{api_results['total']})",
                api_results["details"]
            )
        else:
            self.log_failure(
                f"Échec de {api_results['failed']}/{api_results['total']} tests de providers AI",
                str(api_results["details"])
            )
        
        return self.results

# Fonction compatible avec l'ancien système
async def run_test(project_path: Path, config: dict):
    """Point d'entrée compatible avec l'ancien système."""
    test = AIProvidersTest(project_path, config)
    return await test.run_test()
