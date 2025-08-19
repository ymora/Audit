"""
Framework de tests génériques pour le système d'audit.

Ce module contient des classes et fonctions de base réutilisables
pour créer des tests spécifiques à chaque projet.
"""

from .base_test import BaseAuditTest, BaseProjectTest
from .security_test import SecurityTestMixin
from .api_test import APITestMixin
from .frontend_test import FrontendTestMixin

__all__ = [
    'BaseAuditTest',
    'BaseProjectTest', 
    'SecurityTestMixin',
    'APITestMixin',
    'FrontendTestMixin'
]
