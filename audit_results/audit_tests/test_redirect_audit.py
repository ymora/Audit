#!/usr/bin/env python3
"""
Test de redirection vers les tests du projet audit.
Ce fichier évite les doublons en redirigeant vers les vrais tests.
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Ajouter le répertoire du projet audit au path
audit_tests_dir = Path(__file__).parent / "audit"
sys.path.insert(0, str(audit_tests_dir))

async def run_test(project_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test de redirection vers le test exhaustif du projet audit."""
    
    try:
        # Importer et exécuter le test de qualité du code (qui est maintenant exhaustif)
        from test_code_quality import run_test as run_quality_test
        
        # Exécuter le test exhaustif
        quality_results = await run_quality_test(project_path, config)
        
        # Modifier le message pour indiquer la redirection
        if quality_results.get("success", False):
            quality_results["message"] = f"✅ Redirection réussie - {quality_results['message']}"
        else:
            quality_results["message"] = f"⚠️ Redirection - {quality_results['message']}"
        
        return quality_results
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Erreur lors de la redirection vers les tests audit: {str(e)}",
            "details": {"error": str(e)}
        }
