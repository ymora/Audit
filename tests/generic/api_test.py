#!/usr/bin/env python3
"""
Mixin pour les tests d'API.
"""

import requests
import json
from typing import Dict, Any, List

class APITestMixin:
    """Mixin pour ajouter des fonctionnalités de test d'API."""
    
    def test_endpoint(self, base_url: str, endpoint: str, method: str = "GET", 
                     expected_status: int = 200, timeout: int = 5) -> Dict[str, Any]:
        """Teste un endpoint d'API."""
        url = f"{base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, timeout=timeout)
            else:
                return {"success": False, "error": f"Méthode HTTP non supportée: {method}"}
            
            success = response.status_code == expected_status
            
            return {
                "success": success,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "response_time": response.elapsed.total_seconds(),
                "url": url,
                "method": method
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "method": method
            }
    
    def test_api_health(self, base_url: str) -> Dict[str, Any]:
        """Teste la santé de l'API."""
        return self.test_endpoint(base_url, "/api/health", "GET", 200)
    
    def batch_test_endpoints(self, base_url: str, endpoints: List[Dict]) -> Dict[str, Any]:
        """Teste plusieurs endpoints en lot."""
        results = {
            "total": len(endpoints),
            "passed": 0,
            "failed": 0,
            "details": {}
        }
        
        for endpoint_config in endpoints:
            name = endpoint_config.get("name", endpoint_config["url"])
            result = self.test_endpoint(
                base_url,
                endpoint_config["url"],
                endpoint_config.get("method", "GET"),
                endpoint_config.get("expected_status", 200)
            )
            
            results["details"][name] = result
            if result["success"]:
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        results["success"] = results["failed"] == 0
        return results
