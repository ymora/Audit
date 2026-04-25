"""
Phases d'audit modulaires.

Pipeline complet en 30+ dimensions organisées en 4 niveaux :
  1. CorePhases        — Fondamentaux (init, qualité, sécurité, métriques)
  2. AdvancedPhases    — Avancé (DevOps, UX, IA/ML, excellence)
  3. InventoryPhases   — Inventaire (API, env vars, complexité cyclomatique)
  4. Specialist checks — Approfondissement (sécurité, performance, IA/ML étendus)
"""

from .base_phase import BasePhase
from .core_phases import CorePhases
from .advanced_phases import AdvancedPhases
from .security_checks import SecurityChecks
from .ai_ml_checks import AIMLChecks
from .performance_checks import PerformanceChecks
from .architecture_checks import ArchitecturePhases
from .inventory_phases import InventoryPhases

__all__ = [
    'BasePhase', 'CorePhases', 'AdvancedPhases',
    'SecurityChecks', 'AIMLChecks', 'PerformanceChecks',
    'ArchitecturePhases', 'InventoryPhases'
]
