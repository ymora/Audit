"""
Checks de performance spécialisés.

Impémente `PerformanceChecks` comme une phase `BasePhase` complète,
auditant les boucles inefficaces, les fuites mémoire et les requêtes
de base de données non optimisées. Compatible avec le pipeline unifié.
"""

import re
from pathlib import Path
from typing import Dict, List, Any

from .base_phase import BasePhase, AuditIssue, Severity


class PerformanceChecks(BasePhase):
    """
    Phase de vérification des performances approfondies.

    Hérite de `BasePhase` pour s'intégrer au pipeline unifié du moteur.
    Audite les boucles N+1, les fuites mémoire potentielles et les requêtes DB
    non optimisées en utilisant des patterns de détection regex.
    """

    def __init__(self, project_path: Path, exclude_dirs: List[str] = None, exclude_files: List[str] = None):
        """
        Initialise les contrôles de performance.

        Args:
            project_path (Path): Chemin racine du projet.
            exclude_dirs (List[str], optional): Répertoires à ignorer.
            exclude_files (List[str], optional): Patterns de fichiers à ignorer.
        """
        super().__init__(project_path, exclude_dirs, exclude_files)

    def execute(self) -> Dict[str, Any]:
        """
        Exécute tous les contrôles de performance et retourne le rapport.

        Returns:
            Dict[str, Any]: Résultats aggrégés incluant les pattern async détectés.
        """
        self.get_all_issues()
        async_patterns = self.check_async_usage()
        result = self.get_results()
        result["async_patterns_detected"] = len(async_patterns)
        result["async_usage"] = async_patterns
        return result

    def get_all_issues(self) -> List[AuditIssue]:
        """
        Déclenche tous les contrôles de performance.

        Returns:
            List[AuditIssue]: Toutes les issues de performance détectées.
        """
        self.issues = []  # Reset pour éviter les doublons
        self.check_inefficient_loops()
        self.check_memory_leaks()
        self.check_database_queries()
        return self.issues

    def check_inefficient_loops(self) -> List[AuditIssue]:
        """Vérifier les boucles inefficaces"""
        inefficient_patterns = {
            'nested_loops': r'for\s+.*\s+in\s+.*:\s+for\s+',
            'range_len': r'for\s+.*\s+in\s+range\(len\(',
            'inefficient_list_comp': r'\.append\(.*\)\s*for\s+.*\s+in\s+.*\]:'
        }
        
        for file_path in self.project_path.rglob("*.py"):
            if any(exclude_dir in file_path.parts for exclude_dir in self.exclude_dirs):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for pattern_type, pattern in inefficient_patterns.items():
                        for match in re.finditer(pattern, content):
                            line_num = content[:match.start()].count('\n') + 1
                            self.issues.append(AuditIssue(
                                phase="performance",
                                severity=Severity.MINOR,
                                category="inefficient_loop",
                                message=f"Pattern inefficace détecté: {pattern_type}",
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=lines[line_num - 1] if line_num <= len(lines) else "",
                                suggestion="Optimiser la boucle pour améliorer les performances",
                                priority_score=35,
                                estimated_fix_time="30-60 minutes"
                            ))
            except Exception:
                continue
        
        return self.issues
    
    def check_memory_leaks(self) -> List[AuditIssue]:
        """Vérifier les fuites de mémoire potentielles"""
        memory_patterns = {
            'global_variables': r'^[A-Z_]+\s*=\s*',
            'circular_imports': r'from\s+\.\s*import',
            'unclosed_resources': r'open\([^)]*\)\s*(?!with|\.close\(\))'
        }
        
        for file_path in self.project_path.rglob("*.py"):
            if any(exclude_dir in file_path.parts for exclude_dir in self.exclude_dirs):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for pattern_type, pattern in memory_patterns.items():
                        for match in re.finditer(pattern, content, re.MULTILINE):
                            line_num = content[:match.start()].count('\n') + 1
                            self.issues.append(AuditIssue(
                                phase="performance",
                                severity=Severity.MINOR,
                                category="memory_leak",
                                message=f"Potentielle fuite mémoire: {pattern_type}",
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=lines[line_num - 1] if line_num <= len(lines) else "",
                                suggestion="Revoir le code pour éviter les fuites de mémoire",
                                priority_score=30,
                                estimated_fix_time="1-2 heures"
                            ))
            except Exception:
                continue
        
        return self.issues
    
    def check_database_queries(self) -> List[AuditIssue]:
        """Vérifier les requêtes de base de données inefficaces"""
        db_patterns = {
            'n_plus_one': r'\.filter\([^)]*\)\s*for\s+.*\s+in\s+',
            'select_star': r'SELECT\s+\*',
            'missing_index_hint': r'WHERE.*LIKE\s*%',
            'large_result_sets': r'\.all\(\)'
        }
        
        for file_path in self.project_path.rglob("*.py"):
            if any(exclude_dir in file_path.parts for exclude_dir in self.exclude_dirs):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for pattern_type, pattern in db_patterns.items():
                        for match in re.finditer(pattern, content, re.IGNORECASE):
                            line_num = content[:match.start()].count('\n') + 1
                            self.issues.append(AuditIssue(
                                phase="performance",
                                severity=Severity.MINOR,
                                category="database_query",
                                message=f"Requête DB inefficace: {pattern_type}",
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=lines[line_num - 1] if line_num <= len(lines) else "",
                                suggestion="Optimiser la requête ou ajouter des index",
                                priority_score=40,
                                estimated_fix_time="1-2 heures"
                            ))
            except Exception:
                continue
        
        return self.issues
    
    def check_async_usage(self) -> List[Dict]:
        """Vérifier l'utilisation de async/await"""
        async_patterns = {
            'async_def': r'async\s+def',
            'await': r'await\s+',
            'asyncio': r'asyncio\.',
            'aiohttp': r'aiohttp',
            'asyncpg': r'asyncpg'
        }
        
        async_usage = {}
        for file_path in self.project_path.rglob("*.py"):
            if any(exclude_dir in file_path.parts for exclude_dir in self.exclude_dirs):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern_type, pattern in async_patterns.items():
                        if re.search(pattern, content):
                            async_usage[pattern_type] = async_usage.get(pattern_type, 0) + 1
            except Exception:
                continue
        
        return [{"pattern": k, "count": v} for k, v in async_usage.items()]
    
    def get_all_issues(self) -> List[AuditIssue]:
        """Exécuter tous les checks de performance"""
        self.check_inefficient_loops()
        self.check_memory_leaks()
        self.check_database_queries()
        return self.issues
