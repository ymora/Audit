#!/usr/bin/env python3
"""
Mixin pour les tests de sécurité.
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List

class SecurityTestMixin:
    """Mixin pour ajouter des fonctionnalités de test de sécurité."""
    
    def run_bandit_scan(self, target_path: Path) -> Dict[str, Any]:
        """Exécute un scan Bandit sur le chemin cible."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "bandit", "-r", str(target_path),
                "-f", "json", "-q"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return {"success": True, "issues": []}
            else:
                issues = []
                try:
                    bandit_output = json.loads(result.stdout)
                    issues = bandit_output.get("results", [])
                except:
                    pass
                return {"success": False, "issues": issues}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_dependencies_security(self, requirements_file: Path) -> Dict[str, Any]:
        """Vérifie la sécurité des dépendances."""
        if not requirements_file.exists():
            return {"success": True, "message": "Pas de fichier requirements.txt"}
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "safety", "check", "-r", str(requirements_file),
                "--json"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return {"success": True, "vulnerabilities": []}
            else:
                vulnerabilities = []
                try:
                    safety_output = json.loads(result.stdout)
                    vulnerabilities = safety_output
                except:
                    pass
                return {"success": False, "vulnerabilities": vulnerabilities}
        except Exception as e:
            return {"success": False, "error": str(e)}
