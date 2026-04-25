"""
Phases core d'audit - phases fondamentales
"""

import re
from pathlib import Path
from typing import Dict, Any, List
from .base_phase import BasePhase, AuditIssue, Severity


class CorePhases:
    """Regroupe les phases core fondamentales"""
    
    class InitializationPhase(BasePhase):
        """
        Phase d'initialisation critique.
        
        Vérifie l'existence et l'accessibilité du chemin du projet avant toute analyse.
        """
        
        def execute(self) -> Dict[str, Any]:
            if not self.project_path.exists():
                return {"status": "error", "message": "Le chemin du projet n'existe pas"}
            if not self.project_path.is_dir():
                return {"status": "error", "message": "Le chemin n'est pas un répertoire"}
            
            return {"status": "success", "summary": "Initialisation terminée. Cible validée."}
    
    class DiscoveryPhase(BasePhase):
        """
        Phase de découverte et d'inventaire.
        
        Recense tous les fichiers du projet et extrait des statistiques sur les langages et la taille.
        """
        
        def execute(self) -> Dict[str, Any]:
            files = list(self.project_path.rglob("*"))
            python_files = [f for f in files if f.suffix == '.py']
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            
            return {
                "status": "success",
                "summary": f"Découverte terminée - {len(files)} fichiers inventoriés",
                "files_count": len(files),
                "python_files": len(python_files),
                "total_size_mb": total_size / 1024 / 1024
            }
    
    class ValidationPhase(BasePhase):
        """
        Phase de validation de l'intégrité des fichiers.
        
        Vérifie les contraintes physiques (taille des fichiers) pour prévenir les problèmes de performance.
        """
        
        def execute(self) -> Dict[str, Any]:
            issues = []
            processed = 0
            max_size = 10 * 1024 * 1024  # 10 MB
            
            for file_path in self.project_path.rglob("*"):
                if not file_path.is_file():
                    continue
                if self.is_excluded(file_path):
                    continue
                
                processed += 1
                if file_path.stat().st_size > max_size:
                    self.add_issue(AuditIssue(
                        phase="validation",
                        severity=Severity.MAJOR,
                        category="file_size",
                        message=f"Fichier trop volumineux: {file_path.stat().st_size/1024/1024:.1f} MB",
                        file_path=str(file_path),
                        suggestion=f"Réduire la taille sous 10 MB ou externaliser",
                        priority_score=70,
                        estimated_fix_time="2-4 heures"
                    ))
            
            return self.get_results()
    
    class StructurePhase(BasePhase):
        """
        Phase d'analyse structurelle des dépendances.
        
        Vérifie la topologie des imports pour assurer une architecture Béton sans cycles.
        """
        
        def execute(self) -> Dict[str, Any]:
            for file_path in self.project_path.rglob("*.py"):
                if self.is_excluded(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        imports = re.findall(r'^import\s+(\w+)|^from\s+(\w+)', content, re.MULTILINE)
                        
                        for imp in imports:
                            module = imp[0] or imp[1]
                            if module and module not in ['os', 'sys', 'json', 'time', 're', 'pathlib']:
                                if (self.project_path / module).exists():
                                    self.add_issue(AuditIssue(
                                        phase="structure",
                                        severity=Severity.MINOR,
                                        category="import_structure",
                                        message=f"Import local détecté: {module}",
                                        file_path=str(file_path),
                                        suggestion="Vérifier l'architecture pour éviter les dépendances cycliques",
                                        priority_score=30,
                                        estimated_fix_time="30 minutes"
                                    ))
                except Exception:
                    continue
            
            return self.get_results()
    
    class QualityPhase(BasePhase):
        """
        Analyse la qualité du code (code smells, mauvaises pratiques).
        
        Utilise le module `ast` de la stdlib pour une détection fiable des fonctions
        sans docstrings, évitant les faux positifs de l'analyse par regex.
        """
        
        def execute(self) -> Dict[str, Any]:
            import ast as ast_module
            
            # Smells détectés par regex (fiables car simples)
            regex_smells = {
                r'print\(': "Print statement en production (utilisez logger)",
                r'(?<!["\'])except:': "Except bare (utilisez except Exception as e:)",
                r'#\s*TODO': "Marqueur TODO non résolu",
                r'#\s*FIXME': "Marqueur FIXME non résolu"
            }
            
            for file_path in self.project_path.rglob("*.py"):
                if self.is_excluded(file_path):
                    continue
                
                try:
                    source = file_path.read_text(encoding='utf-8', errors='ignore')
                    lines = source.split('\n')
                    
                    # --- Détection via regex (patterns simples) ---
                    for pattern, message in regex_smells.items():
                        for match in re.finditer(pattern, source, re.MULTILINE):
                            line_num = source[:match.start()].count('\n') + 1
                            snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                            # Ignorer si c'est une définition de règle
                            if any(kw in snippet for kw in ['code_smells =', 'regex_smells =', "r'"]):
                                continue
                            self.add_issue(AuditIssue(
                                phase="quality",
                                severity=Severity.MINOR,
                                category="code_smell",
                                message=message,
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=snippet.strip(),
                                suggestion="Refactoriser pour améliorer la qualité du code",
                                priority_score=25,
                                estimated_fix_time="15-30 minutes"
                            ))
                    
                    # --- Détection AST : fonctions sans docstrings ---
                    try:
                        tree = ast_module.parse(source)
                        for node in ast_module.walk(tree):
                            if isinstance(node, (ast_module.FunctionDef, ast_module.AsyncFunctionDef)):
                                # Une fonction a une docstring si son premier statement est une constante str
                                has_doc = (
                                    node.body and
                                    isinstance(node.body[0], ast_module.Expr) and
                                    isinstance(node.body[0].value, ast_module.Constant) and
                                    isinstance(node.body[0].value.value, str)
                                )
                                if not has_doc:
                                    snippet = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
                                    self.add_issue(AuditIssue(
                                        phase="quality",
                                        severity=Severity.MINOR,
                                        category="missing_docstring",
                                        message=f"Fonction '{node.name}' sans docstring",
                                        file_path=str(file_path),
                                        line_number=node.lineno,
                                        code_snippet=snippet.strip(),
                                        suggestion="Ajouter une docstring pour documenter le comportement",
                                        priority_score=15,
                                        estimated_fix_time="5-10 minutes"
                                    ))
                    except SyntaxError:
                        pass  # Fichier non parseable, ignoré silencieusement
                        
                except Exception:
                    continue
            
            return self.get_results()
    
    class UnificationPhase(BasePhase):
        """
        Vérifie l'unification du style et le respect des conventions PEP 8.
        """
        
        def execute(self) -> Dict[str, Any]:
            naming_issues = {
                r'class\s+([a-z])': "Nom de classe en minuscule (PascalCase requis)",
                r'def\s+([A-Z])': "Nom de fonction en majuscule (snake_case requis)",
                r'\b([a-z]\w*[A-Z]\w*)\s*=': "Variable en mixedCase (snake_case requis)"
            }
            
            for file_path in self.project_path.rglob("*.py"):
                if self.is_excluded(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for pattern, message in naming_issues.items():
                            for match in re.finditer(pattern, content):
                                line_num = content[:match.start()].count('\n') + 1
                                snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                                
                                # Ignorer si c'est une définition de règle
                                if any(kw in snippet for kw in ['naming_issues =', 'r\'']):
                                    continue
                                    
                                self.add_issue(AuditIssue(
                                    phase="unification",
                                    severity=Severity.MINOR,
                                    category="naming_convention",
                                    message=message,
                                    file_path=str(file_path),
                                    line_number=line_num,
                                    code_snippet=snippet.strip(),
                                    suggestion="Suivre PEP 8 pour les conventions de nommage",
                                    priority_score=20,
                                    estimated_fix_time="10-15 minutes"
                                ))
                except Exception:
                    continue
            
            return self.get_results()
    
    class OptimizationPhase(BasePhase):
        """
        Identifie les opportunités d'optimisation de performance.
        """
        
        def execute(self) -> Dict[str, Any]:
            perf_patterns = {
                r'\.append\(.*\)\s*for\s+.*\s+in\s+.*\]:': "List comprehension inefficace",
                r'for\s+.*\s+in\s+range\(len\(': "Utiliser enumerate() au lieu de range(len())",
                r'global\s+\w+': "Variable globale (éviter pour la performance)"
            }
            
            for file_path in self.project_path.rglob("*.py"):
                if self.is_excluded(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for pattern, message in perf_patterns.items():
                            for match in re.finditer(pattern, content):
                                line_num = content[:match.start()].count('\n') + 1
                                snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                                
                                # Ignorer si c'est une définition de règle
                                if any(kw in snippet for kw in ['perf_patterns =', 'r\'']):
                                    continue
                                    
                                self.add_issue(AuditIssue(
                                    phase="optimization",
                                    severity=Severity.MINOR,
                                    category="performance",
                                    message=message,
                                    file_path=str(file_path),
                                    line_number=line_num,
                                    code_snippet=snippet.strip(),
                                    suggestion="Optimiser pour améliorer les performances",
                                    priority_score=35,
                                    estimated_fix_time="30-60 minutes"
                                ))
                except Exception:
                    continue
            
            return self.get_results()
    
    class SecurityPhase(BasePhase):
        """
        Phase consolidée d'analyse de sécurité.
        """
        
        def execute(self) -> Dict[str, Any]:
            security_patterns = {
                'critical': [
                    r'password\s*=\s*["\']',
                    r'api_key\s*=\s*["\']',
                    r'secret\s*=\s*["\']',
                    r'token\s*=\s*["\']'
                ],
                'major': [
                    r'eval\(',
                    r'exec\(',
                    r'shell\s*=\s*True',
                    r'os\.system\(',
                    r'pickle\.loads\('
                ],
                'minor': [
                    r'%s.*%s',
                    r'\.format\(.*\)',
                    r'request\.form',
                    r'sql\.execute'
                ]
            }
            
            for file_path in self.project_path.rglob("*.py"):
                if self.is_excluded(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for severity, patterns in security_patterns.items():
                            for pattern in patterns:
                                for match in re.finditer(pattern, content, re.IGNORECASE):
                                    line_num = content[:match.start()].count('\n') + 1
                                    snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                                    
                                    # Éviter l'auto-détection des règles (faux positifs d'audit)
                                    if any(kw in snippet for kw in ['security_patterns =', 'dangerous_patterns =', 'r\'']):
                                        continue
                                        
                                    severity_enum = {
                                        'critical': Severity.CRITICAL,
                                        'major': Severity.MAJOR,
                                        'minor': Severity.MINOR
                                    }.get(severity, Severity.MINOR)
                                    
                                    self.add_issue(AuditIssue(
                                        phase="security",
                                        severity=severity_enum,
                                        category="security_pattern",
                                        message=f"Pattern de sécurité détecté: {pattern}",
                                        file_path=str(file_path),
                                        line_number=line_num,
                                        code_snippet=snippet.strip(),
                                        suggestion="Vérifier et sécuriser ce pattern de sécurité",
                                        priority_score=100 if severity == 'critical' else 75 if severity == 'major' else 40,
                                        estimated_fix_time="1-2 heures" if severity == 'critical' else "2-4 heures"
                                    ))
                except Exception:
                    continue
            
            return self.get_results()
    
    class MetricsPhase(BasePhase):
        """
        Phase de calcul des métriques logicielles avancées.
        
        Évalue la complexité, la densité de classes et de fonctions pour mesurer la maintenabilité.
        """
        
        def execute(self) -> Dict[str, Any]:
            total_complexity = 0
            total_functions = 0
            total_classes = 0
            
            for file_path in self.project_path.rglob("*.py"):
                if self.is_excluded(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        total_functions += len(re.findall(r'def\s+\w+', content))
                        total_classes += len(re.findall(r'class\s+\w+', content))
                        total_complexity += len(re.findall(r'\bif\b|\bfor\b|\bwhile\b', content))
                except Exception:
                    continue
            
            return {
                "status": "success",
                "summary": "Métriques avancées calculées",
                "metrics": {
                    "total_functions": total_functions,
                    "total_classes": total_classes,
                    "estimated_complexity": total_complexity,
                    "avg_complexity_per_function": total_complexity / total_functions if total_functions > 0 else 0
                }
            }
