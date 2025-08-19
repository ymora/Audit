#!/usr/bin/env python3
"""
Test des providers AI pour DocuSense AI
=======================================

Teste la connectivité et la validité des clés API pour tous les providers AI configurés.
"""

import asyncio
import sys
import os
import requests
from pathlib import Path
from typing import Dict, Any

# Ajouter le répertoire backend au path
project_path = Path(__file__).parent.parent.parent.parent
backend_path = project_path / "backend"
sys.path.insert(0, str(backend_path))

async def run_test(project_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    """Exécute le test des providers AI."""
    
    print("🧪 Test des providers AI...")
    
    results = {
        "success": True,
        "message": "Tous les providers AI testés avec succès",
        "details": {
            "providers_tested": 0,
            "providers_successful": 0,
            "providers_failed": 0,
            "provider_results": {}
        }
    }
    
    # Vérifier si le backend est en cours d'exécution
    backend_url = "http://localhost:8000"
    try:
        response = requests.get(f"{backend_url}/api/health", timeout=5)
        if response.status_code != 200:
            return {
                "success": False,
                "message": "Backend non accessible - impossible de tester les providers AI",
                "details": {"error": "Backend offline"}
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Impossible de se connecter au backend: {str(e)}",
            "details": {"error": str(e)}
        }
    
    # Récupérer la configuration des providers AI
    ai_providers = config.get("ai_providers", {})
    
    for provider_name, provider_config in ai_providers.items():
        print(f"  🔍 Test du provider: {provider_name}")
        
        test_key = provider_config.get("test_key")
        required = provider_config.get("required", False)
        
        if not test_key and not required:
            print(f"    ⚪ Provider {provider_name} non configuré (non requis)")
            results["details"]["provider_results"][provider_name] = {
                "status": "skipped",
                "message": "Provider non configuré et non requis"
            }
            continue
        
        if not test_key and required:
            print(f"    ❌ Provider {provider_name} requis mais non configuré")
            results["details"]["provider_results"][provider_name] = {
                "status": "failed",
                "message": "Provider requis mais clé API manquante"
            }
            results["details"]["providers_failed"] += 1
            results["success"] = False
            continue
        
        # Tester le provider avec sa clé API
        try:
            test_url = f"{backend_url}/api/config/ai/test"
            test_data = {"api_key": test_key}
            test_params = {"provider": provider_name}
            
            response = requests.post(
                test_url,
                params=test_params,
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("success", False):
                    print(f"    ✅ Provider {provider_name} testé avec succès")
                    results["details"]["provider_results"][provider_name] = {
                        "status": "success",
                        "message": "Provider fonctionnel",
                        "response": response_data
                    }
                    results["details"]["providers_successful"] += 1
                else:
                    print(f"    ❌ Provider {provider_name} test échoué")
                    results["details"]["provider_results"][provider_name] = {
                        "status": "failed",
                        "message": response_data.get("message", "Test échoué"),
                        "response": response_data
                    }
                    results["details"]["providers_failed"] += 1
                    results["success"] = False
            else:
                print(f"    ❌ Erreur HTTP {response.status_code} pour {provider_name}")
                results["details"]["provider_results"][provider_name] = {
                    "status": "failed",
                    "message": f"Erreur HTTP {response.status_code}",
                    "response": response.text
                }
                results["details"]["providers_failed"] += 1
                results["success"] = False
                
        except Exception as e:
            print(f"    ❌ Erreur lors du test de {provider_name}: {str(e)}")
            results["details"]["provider_results"][provider_name] = {
                "status": "failed",
                "message": f"Erreur de connexion: {str(e)}"
            }
            results["details"]["providers_failed"] += 1
            results["success"] = False
        
        results["details"]["providers_tested"] += 1
    
    # Mettre à jour le message de résultat
    if results["details"]["providers_failed"] > 0:
        results["message"] = f"{results['details']['providers_failed']} provider(s) AI en échec"
    elif results["details"]["providers_successful"] > 0:
        results["message"] = f"{results['details']['providers_successful']} provider(s) AI testé(s) avec succès"
    else:
        results["message"] = "Aucun provider AI testé"
    
    return results
