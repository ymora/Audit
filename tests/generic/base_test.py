#!/usr/bin/env python3
"""
Classes de base pour les tests du système d'audit.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class BaseAuditTest(ABC):
    """Classe de base pour tous les tests d'audit."""
    
    def __init__(self, project_path: Path, config: Dict[str, Any]):
        self.project_path = project_path
        self.config = config
        self.results = {
            "success": True,
            "message": "",
            "details": {}
        }
    
    @abstractmethod
    async def run_test(self) -> Dict[str, Any]:
        """Méthode abstraite à implémenter par chaque test."""
        pass
    
    def log_success(self, message: str, details: Optional[Dict] = None):
        """Enregistre un succès."""
        self.results["success"] = True
        self.results["message"] = message
        if details:
            self.results["details"].update(details)
    
    def log_failure(self, message: str, error: Optional[str] = None):
        """Enregistre un échec."""
        self.results["success"] = False
        self.results["message"] = message
        if error:
            self.results["details"]["error"] = error

class BaseProjectTest(BaseAuditTest):
    """Classe de base pour les tests spécifiques à un projet."""
    
    def __init__(self, project_path: Path, config: Dict[str, Any]):
        super().__init__(project_path, config)
        self.project_name = config.get("name", "Unknown")
        self.project_type = config.get("type", "unknown")
    
    def get_project_config(self, key: str, default=None):
        """Récupère une valeur de configuration du projet."""
        return self.config.get(key, default)
    
    def is_service_running(self, port: int) -> bool:
        """Vérifie si un service est en cours d'exécution sur un port."""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                return s.connect_ex(('localhost', port)) == 0
        except:
            return False
