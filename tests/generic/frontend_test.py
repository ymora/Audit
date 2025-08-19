#!/usr/bin/env python3
"""
Mixin pour les tests de frontend.
"""

import requests
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

class FrontendTestMixin:
    """Mixin pour ajouter des fonctionnalités de test de frontend."""
    
    def check_frontend_server(self, port: int = 3000) -> Dict[str, Any]:
        """Vérifie si le serveur frontend est accessible."""
        url = f"http://localhost:{port}"
        
        try:
            response = requests.get(url, timeout=5)
            return {
                "success": True,
                "status_code": response.status_code,
                "url": url,
                "response_time": response.elapsed.total_seconds()
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    def check_static_files(self, frontend_path: Path) -> Dict[str, Any]:
        """Vérifie la présence des fichiers statiques essentiels."""
        essential_files = [
            "index.html",
            "package.json",
            "src/",
            "public/"
        ]
        
        results = {
            "success": True,
            "missing_files": [],
            "found_files": []
        }
        
        for file_name in essential_files:
            file_path = frontend_path / file_name
            if file_path.exists():
                results["found_files"].append(file_name)
            else:
                results["missing_files"].append(file_name)
                results["success"] = False
        
        return results
    
    def run_frontend_build(self, frontend_path: Path) -> Dict[str, Any]:
        """Teste la construction du frontend."""
        package_json = frontend_path / "package.json"
        
        if not package_json.exists():
            return {
                "success": False,
                "error": "package.json non trouvé"
            }
        
        try:
            # Essayer npm run build
            result = subprocess.run([
                "npm", "run", "build"
            ], cwd=frontend_path, capture_output=True, text=True, timeout=120)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Timeout lors de la construction (> 2 minutes)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
