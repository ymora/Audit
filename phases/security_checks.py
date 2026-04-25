"""
Checks de sécurité spécialisés.

Ce module implémente `SecurityChecks` comme une phase BasePhase complète,
auditant les secrets hardcodés, les fonctions système dangereuses et les
risques d'injection SQL. Compatible avec le pipeline unifié du moteur.
"""

import re
from pathlib import Path
from typing import Dict, List, Any

from .base_phase import BasePhase, AuditIssue, Severity


class SecurityChecks(BasePhase):
    """
    Phase de vérification de sécurité approfondie.

    Hérite de `BasePhase` pour s'intégrer au pipeline unifié du moteur.
    Impémente trois contrôles : secrets hardcodés, fonctions système
    dangereuses, et risques d'injection SQL.
    """

    def __init__(self, project_path: Path, exclude_dirs: List[str] = None, exclude_files: List[str] = None):
        """
        Initialise les contrôles de sécurité.

        Args:
            project_path (Path): Chemin racine du projet.
            exclude_dirs (List[str], optional): Répertoires à ignorer.
            exclude_files (List[str], optional): Patterns de fichiers à ignorer.
        """
        super().__init__(project_path, exclude_dirs, exclude_files)

    def execute(self) -> Dict[str, Any]:
        """
        Exécute tous les contrôles de sécurité et retourne le rapport.

        Returns:
            Dict[str, Any]: Résultats aggrégés des trois contrôles.
        """
        self.get_all_issues()
        return self.get_results()

    def get_all_issues(self) -> List[AuditIssue]:
        """
        Déclenche tous les contrôles et retourne la liste consolidée.

        Returns:
            List[AuditIssue]: Toutes les issues de sécurité détectées.
        """
        self.issues = []  # Reset pour éviter les doublons si appelé plusieurs fois
        self.check_hardcoded_secrets()
        self.check_dangerous_functions()
        self.check_sql_injection()
        return self.issues

    def check_hardcoded_secrets(self) -> List[AuditIssue]:
        """
        Analyse le code source à la recherche de secrets (mots de passe, tokens) hardcodés.

        Returns:
            List[AuditIssue]: Liste des vulnérabilités de secrets détectées.
        """
        secret_patterns = {
            'password': r'password\s*=\s*["\']',
            'api_key': r'api_key\s*=\s*["\']',
            'secret': r'secret\s*=\s*["\']',
            'token': r'token\s*=\s*["\']',
            'private_key': r'private_key\s*=\s*["\']'
        }
        
        for file_path in self.project_path.rglob("*.py"):
            if any(exclude_dir in file_path.parts for exclude_dir in self.exclude_dirs):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for secret_type, pattern in secret_patterns.items():
                        for match in re.finditer(pattern, content, re.IGNORECASE):
                            line_num = content[:match.start()].count('\n') + 1
                            snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                            
                            # Ignorer la ligne si c'est la définition du pattern lui-même (faux positif)
                            if 'secret_patterns =' in snippet or 'r\'' in snippet:
                                continue
                                
                            self.issues.append(AuditIssue(
                                phase="security",
                                severity=Severity.CRITICAL,
                                category="hardcoded_secret",
                                message=f"{secret_type} hardcodé détecté",
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=snippet.strip(),
                                suggestion=f"Utiliser variables d'environnement pour {secret_type}",
                                priority_score=100,
                                estimated_fix_time="30 minutes - 1 heure"
                            ))
            except Exception:
                continue
        
        return self.issues
    
    def check_dangerous_functions(self) -> List[AuditIssue]:
        """
        Détecte l'usage de fonctions Python intrinsèquement dangereuses (eval, exec, os.system).

        Returns:
            List[AuditIssue]: Liste des mauvaises pratiques de sécurité détectées.
        """
        dangerous_patterns = {
            'eval': r'eval\(',
            'exec': r'exec\(',
            'shell_true': r'shell\s*=\s*True',
            'os_system': r'os\.system\(',
            'pickle_loads': r'pickle\.loads\(',
            'subprocess_shell': r'subprocess\.(call|run|Popen).*shell\s*=\s*True'
        }
        
        for file_path in self.project_path.rglob("*.py"):
            if any(exclude_dir in file_path.parts for exclude_dir in self.exclude_dirs):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for func_type, pattern in dangerous_patterns.items():
                        for match in re.finditer(pattern, content, re.IGNORECASE):
                            line_num = content[:match.start()].count('\n') + 1
                            snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                            
                            # Ignorer si c'est la définition des règles (auto-audit)
                            if 'dangerous_patterns =' in snippet or 'r\'' in snippet:
                                continue
                                
                            self.issues.append(AuditIssue(
                                phase="security",
                                severity=Severity.MAJOR,
                                category="dangerous_function",
                                message=f"Fonction dangereuse détectée: {func_type}",
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=snippet.strip(),
                                suggestion=f"Éviter l'utilisation de {func_type} ou valider les entrées",
                                priority_score=75,
                                estimated_fix_time="1-2 heures"
                            ))
            except Exception:
                continue
        
        return self.issues
    
    def check_sql_injection(self) -> List[AuditIssue]:
        """
        Identifie les patterns typiques de vulnérabilité aux injections SQL.

        Returns:
            List[AuditIssue]: Alertes sur les risques d'injection.
        """
        sql_patterns = [
            r'%s.*%s',
            r'\.format\(.*\)',
            r'f["\'].*SELECT.*\{.*\}.*["\']',
            r'sql\.execute.*\+'
        ]
        
        for file_path in self.project_path.rglob("*.py"):
            if any(exclude_dir in file_path.parts for exclude_dir in self.exclude_dirs):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for pattern in sql_patterns:
                        for match in re.finditer(pattern, content, re.IGNORECASE):
                            line_num = content[:match.start()].count('\n') + 1
                            snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                            
                            # Ignorer si c'est la définition des règles
                            if 'sql_patterns =' in snippet or 'r\'' in snippet:
                                continue
                                
                            self.issues.append(AuditIssue(
                                phase="security",
                                severity=Severity.MAJOR,
                                category="sql_injection",
                                message="Potentielle vulnérabilité SQL injection",
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=snippet.strip(),
                                suggestion="Utiliser des requêtes paramétrées",
                                priority_score=80,
                                estimated_fix_time="1-2 heures"
                            ))
            except Exception:
                continue
        
        return self.issues
    
    def get_all_issues(self) -> List[AuditIssue]:
        """
        Orchestre l'exécution de tous les contrôles de sécurité et retourne la synthèse.

        Returns:
            List[AuditIssue]: Compilation de tous les problèmes de sécurité trouvés.
        """
        self.check_hardcoded_secrets()
        self.check_dangerous_functions()
        self.check_sql_injection()
        return self.issues
