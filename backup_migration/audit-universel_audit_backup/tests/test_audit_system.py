#!/usr/bin/env python3
"""
Test du système d'audit pour le projet audit-universel.
"""

import sys
from pathlib import Path

# Ajouter le framework au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tests"))

from generic.base_test import BaseProjectTest
from generic.api_test import APITestMixin
from generic.security_test import SecurityTestMixin

class AuditSystemTest(BaseProjectTest, SecurityTestMixin):
    """Test du système d'audit."""
    
    async def run_test(self):
        """Exécute le test du système d'audit."""
        print("🔍 Test du système d'audit...")
        
        # Vérifier que les fichiers principaux existent
        core_files = [
            "audit.py",
            "core/audit_gui.py",
            "core/audit.py",
            "core/init_audit.py"
        ]
        
        missing_files = []
        for file_path in core_files:
            full_path = self.project_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log_failure(f"Fichiers manquants: {missing_files}")
        else:
            self.log_success("Tous les fichiers principaux présents")
        
        # Test de sécurité sur le code
        security_result = self.run_bandit_scan(self.project_path)
        if security_result["success"]:
            self.log_success("Scan de sécurité réussi")
        else:
            self.log_failure("Problèmes de sécurité détectés")
        
        return self.results

# Compatibilité avec l'ancien système
async def run_test(project_path: Path, config: dict):
    test = AuditSystemTest(project_path, config)
    return await test.run_test()
