"""
Classe de base pour toutes les phases d'audit
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import fnmatch


class Severity(Enum):
    """Niveaux de sévérité"""
    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


@dataclass
class AuditIssue:
    """Issue d'audit enrichie"""
    phase: str
    severity: Severity
    category: str
    message: str
    file_path: str
    line_number: int = None
    code_snippet: str = None
    suggestion: str = None
    priority_score: int = 50
    estimated_fix_time: str = "1-2 heures"


class BasePhase(ABC):
    """Classe de base abstraite pour toutes les phases"""
    
    def __init__(self, project_path: Path, exclude_dirs: List[str] = None, exclude_files: List[str] = None):
        self.project_path = project_path
        self.exclude_dirs = exclude_dirs or [
            '.git', '__pycache__', 'node_modules', '.vscode', 'venv',
            '.pytest_cache', '.mypy_cache', 'dist', 'build', '*.egg-info'
        ]
        self.exclude_files = exclude_files or []
        self.issues: List[AuditIssue] = []
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Exécuter la phase d'audit"""
        pass
    
    def is_excluded(self, file_path: Path) -> bool:
        """Vérifier si le fichier doit être exclu"""
        # Vérifier les répertoires exclus
        if any(exclude_dir in file_path.parts for exclude_dir in self.exclude_dirs):
            return True
        
        # Vérifier les patterns de fichiers exclus
        for pattern in self.exclude_files:
            # Pattern avec chemin (ex: "seed/*.py")
            if '/' in pattern or '\\' in pattern:
                pattern_path = Path(pattern)
                if file_path.match(pattern):
                    return True
            # Pattern de nom de fichier (ex: "check_*.py")
            elif fnmatch.fnmatch(file_path.name, pattern):
                return True
        
        return False
    
    def add_issue(self, issue: AuditIssue):
        """Ajouter une issue à la liste"""
        self.issues.append(issue)
    
    def get_results(self) -> Dict[str, Any]:
        """Retourner les résultats de la phase"""
        return {
            "status": "success",
            "summary": f"Phase terminée - {len(self.issues)} problèmes détectés",
            "issues_found": len(self.issues),
            "issues": [issue.__dict__ for issue in self.issues]
        }
