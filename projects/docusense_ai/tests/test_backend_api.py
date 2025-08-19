#!/usr/bin/env python3
"""
Test de l'API backend pour DocuSense AI
=======================================

Teste les endpoints principaux de l'API backend.
"""

import asyncio
import requests
import json
from pathlib import Path
from typing import Dict, Any

async def run_test(project_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    """Exécute le test de l'API backend."""
    
    print("🔧 Test de l'API backend...")
    
    results = {
        "success": True,
        "message": "Tous les endpoints API testés avec succès",
        "details": {
            "endpoints_tested": 0,
            "endpoints_successful": 0,
            "endpoints_failed": 0,
            "endpoint_results": {}
        }
    }
    
    backend_url = "http://localhost:8000"
    
    # Liste des endpoints à tester
    endpoints = [
        {
            "name": "health",
            "url": "/api/health",
            "method": "GET",
            "expected_status": 200,
            "description": "Endpoint de santé"
        },
        {
            "name": "ai_providers",
            "url": "/api/config/ai/providers",
            "method": "GET",
            "expected_status": 200,
            "description": "Liste des providers AI"
        },
        {
            "name": "functional_providers",
            "url": "/api/config/ai/providers/functional",
            "method": "GET",
            "expected_status": 200,
            "description": "Providers AI fonctionnels"
        },
        {
            "name": "file_upload_info",
            "url": "/api/files/info",
            "method": "GET",
            "expected_status": 200,
            "description": "Informations sur les fichiers"
        },
        {
            "name": "queue_status",
            "url": "/api/queue/status",
            "method": "GET",
            "expected_status": 200,
            "description": "Statut de la file d'attente"
        }
    ]
    
    for endpoint in endpoints:
        print(f"  🔍 Test de l'endpoint: {endpoint['name']}")
        
        try:
            url = f"{backend_url}{endpoint['url']}"
            
            if endpoint['method'] == 'GET':
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, timeout=10)
            
            if response.status_code == endpoint['expected_status']:
                print(f"    ✅ Endpoint {endpoint['name']} fonctionnel")
                results["details"]["endpoint_results"][endpoint['name']] = {
                    "status": "success",
                    "message": endpoint['description'],
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
                results["details"]["endpoints_successful"] += 1
            else:
                print(f"    ❌ Endpoint {endpoint['name']} - Status {response.status_code}")
                results["details"]["endpoint_results"][endpoint['name']] = {
                    "status": "failed",
                    "message": f"Status {response.status_code} au lieu de {endpoint['expected_status']}",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code,
                    "response_text": response.text[:200]  # Limiter la taille
                }
                results["details"]["endpoints_failed"] += 1
                results["success"] = False
                
        except requests.exceptions.ConnectionError:
            print(f"    ❌ Endpoint {endpoint['name']} - Connexion impossible")
            results["details"]["endpoint_results"][endpoint['name']] = {
                "status": "failed",
                "message": "Impossible de se connecter au backend",
                "error": "ConnectionError"
            }
            results["details"]["endpoints_failed"] += 1
            results["success"] = False
            
        except requests.exceptions.Timeout:
            print(f"    ❌ Endpoint {endpoint['name']} - Timeout")
            results["details"]["endpoint_results"][endpoint['name']] = {
                "status": "failed",
                "message": "Timeout de la requête",
                "error": "Timeout"
            }
            results["details"]["endpoints_failed"] += 1
            results["success"] = False
            
        except Exception as e:
            print(f"    ❌ Endpoint {endpoint['name']} - Erreur: {str(e)}")
            results["details"]["endpoint_results"][endpoint['name']] = {
                "status": "failed",
                "message": f"Erreur: {str(e)}",
                "error": str(e)
            }
            results["details"]["endpoints_failed"] += 1
            results["success"] = False
        
        results["details"]["endpoints_tested"] += 1
    
    # Test spécial pour vérifier la structure de la réponse des providers AI
    try:
        response = requests.get(f"{backend_url}/api/config/ai/providers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "providers" in data and isinstance(data["providers"], list):
                print(f"    ✅ Structure de réponse des providers AI valide")
                results["details"]["endpoint_results"]["providers_structure"] = {
                    "status": "success",
                    "message": "Structure de réponse valide",
                    "providers_count": len(data["providers"])
                }
            else:
                print(f"    ⚠️ Structure de réponse des providers AI inattendue")
                results["details"]["endpoint_results"]["providers_structure"] = {
                    "status": "warning",
                    "message": "Structure de réponse inattendue",
                    "data_keys": list(data.keys()) if isinstance(data, dict) else "Non-dict"
                }
    except Exception as e:
        print(f"    ❌ Erreur lors de la vérification de la structure: {str(e)}")
    
    # Mettre à jour le message de résultat
    if results["details"]["endpoints_failed"] > 0:
        results["message"] = f"{results['details']['endpoints_failed']} endpoint(s) en échec"
    elif results["details"]["endpoints_successful"] > 0:
        results["message"] = f"{results['details']['endpoints_successful']} endpoint(s) testé(s) avec succès"
    else:
        results["message"] = "Aucun endpoint testé"
    
    return results
