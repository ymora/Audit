#!/usr/bin/env python3
"""
AUDITEUR GÉNÉRIQUE - ANALYSE DE CODE UNIVERSEL
==============================================

Auditeur générique qui peut analyser n'importe quel type de projet.
Effectue des analyses de base : structure, fichiers, qualité, sécurité.
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import ast
import re

class GenericAuditor:
    """Auditeur générique pour tous les types de projets."""
    
    def __init__(self, project_path: Path, config: Dict[str, Any]):
        self.project_path = project_path
        self.config = config
        self.results = {
            "analysis_type": "generic",
            "timestamp": datetime.now().isoformat(),
            "project_path": str(project_path),
            "findings": [],
            "metrics": {},
            "recommendations": []
        }
    
    async def run_generic_audit(self) -> Dict[str, Any]:
        """Exécute l'audit générique complet."""
        print(f"[ANALYSIS] Démarrage de l'audit générique...")
        
        # Analyser la structure du projet
        await self._analyze_project_structure()
        
        # Analyser les fichiers de code
        await self._analyze_code_files()
        
        # Analyser la sécurité
        await self._analyze_security()
        
        # Analyser la qualité
        await self._analyze_quality()
        
        # Générer les recommandations
        self._generate_recommendations()
        
        print(f"[ANALYSIS] Audit générique terminé - {len(self.results['findings'])} problèmes trouvés")
        
        return {
            "generic_audit": {
                "success": True,
                "message": "Audit générique terminé avec succès",
                "details": self.results
            }
        }
    
    async def _analyze_project_structure(self):
        """Analyse la structure générale du projet."""
        print(f"  [STRUCTURE] Analyse de la structure...")
        
        # Compter les fichiers par type
        file_counts = {}
        total_files = 0
        
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file():
                total_files += 1
                ext = file_path.suffix.lower()
                file_counts[ext] = file_counts.get(ext, 0) + 1
        
        self.results["metrics"]["total_files"] = total_files
        self.results["metrics"]["file_types"] = file_counts
        
        # Vérifier les dossiers importants
        important_dirs = ["src", "lib", "app", "main", "core", "utils", "tests", "docs"]
        missing_dirs = []
        
        for dir_name in important_dirs:
            if not (self.project_path / dir_name).exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            self.results["findings"].append({
                "type": "structure",
                "severity": "info",
                "message": f"Dossiers recommandés manquants: {', '.join(missing_dirs)}",
                "recommendation": "Créer une structure de projet standardisée"
            })
    
    async def _analyze_code_files(self):
        """Analyse les fichiers de code."""
        print(f"  [CODE] Analyse des fichiers de code...")
        
        code_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.php', '.go', '.rs']
        code_files = []
        
        for ext in code_extensions:
            code_files.extend(self.project_path.rglob(f"*{ext}"))
        
        self.results["metrics"]["code_files"] = len(code_files)
        
        # Analyser les fichiers Python
        python_files = list(self.project_path.rglob("*.py"))
        if python_files:
            await self._analyze_python_files(python_files)
    
    async def _analyze_python_files(self, python_files: List[Path]):
        """Analyse spécifique des fichiers Python."""
        print(f"    [PYTHON] Analyse de {len(python_files)} fichiers Python...")
        
        total_lines = 0
        total_functions = 0
        total_classes = 0
        issues = []
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    lines = content.split('\n')
                    total_lines += len(lines)
                
                # Analyse AST basique
                try:
                    tree = ast.parse(content)
                    functions = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
                    classes = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
                    total_functions += functions
                    total_classes += classes
                    
                    # Vérifier les fonctions trop longues
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            if len(node.body) > 20:  # Plus de 20 lignes
                                issues.append({
                                    "file": str(py_file.relative_to(self.project_path)),
                                    "line": node.lineno,
                                    "type": "long_function",
                                    "message": f"Fonction '{node.name}' très longue ({len(node.body)} lignes)"
                                })
                
                except SyntaxError:
                    issues.append({
                        "file": str(py_file.relative_to(self.project_path)),
                        "type": "syntax_error",
                        "message": "Erreur de syntaxe Python"
                    })
                    
            except Exception as e:
                issues.append({
                    "file": str(py_file.relative_to(self.project_path)),
                    "type": "read_error",
                    "message": f"Impossible de lire le fichier: {e}"
                })
        
        self.results["metrics"]["python"] = {
            "total_files": len(python_files),
            "total_lines": total_lines,
            "total_functions": total_functions,
            "total_classes": total_classes,
            "avg_lines_per_file": total_lines / len(python_files) if python_files else 0
        }
        
        # Ajouter les problèmes trouvés
        for issue in issues:
            self.results["findings"].append({
                "type": "code_quality",
                "severity": "warning",
                "file": issue.get("file", ""),
                "line": issue.get("line", 0),
                "message": issue["message"]
            })
    
    async def _analyze_security(self):
        """Analyse de sécurité basique."""
        print(f"  [SECURITY] Analyse de sécurité...")
        
        security_patterns = {
            "password": r"password\s*=\s*['\"][^'\"]+['\"]",
            "api_key": r"api_key\s*=\s*['\"][^'\"]+['\"]",
            "secret": r"secret\s*=\s*['\"][^'\"]+['\"]",
            "token": r"token\s*=\s*['\"][^'\"]+['\"]",
            "eval": r"eval\s*\(",
            "exec": r"exec\s*\(",
            "sql_injection": r"execute\s*\(\s*['\"].*%s.*['\"]",
        }
        
        code_files = []
        for ext in ['.py', '.js', '.php', '.java']:
            code_files.extend(self.project_path.rglob(f"*{ext}"))
        
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                for pattern_name, pattern in security_patterns.items():
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        self.results["findings"].append({
                            "type": "security",
                            "severity": "high",
                            "file": str(file_path.relative_to(self.project_path)),
                            "message": f"Pattern de sécurité détecté: {pattern_name}",
                            "recommendation": "Vérifier et sécuriser les données sensibles"
                        })
                        
            except Exception:
                continue
    
    async def _analyze_quality(self):
        """Analyse de qualité du code."""
        print(f"  [QUALITY] Analyse de qualité...")
        
        # Vérifier la présence de documentation
        doc_files = list(self.project_path.rglob("README*"))
        if not doc_files:
            self.results["findings"].append({
                "type": "documentation",
                "severity": "medium",
                "message": "Aucun fichier README trouvé",
                "recommendation": "Créer un README.md avec la documentation du projet"
            })
        
        # Vérifier la présence de tests
        test_files = []
        for pattern in ["test_*.py", "*_test.py", "tests/", "__tests__/"]:
            test_files.extend(self.project_path.rglob(pattern))
        
        if not test_files:
            self.results["findings"].append({
                "type": "testing",
                "severity": "medium",
                "message": "Aucun fichier de test trouvé",
                "recommendation": "Ajouter des tests unitaires et d'intégration"
            })
    
    def _generate_recommendations(self):
        """Génère des recommandations basées sur l'analyse."""
        print(f"  [RECOMMENDATIONS] Génération des recommandations...")
        
        recommendations = []
        
        # Recommandations basées sur les métriques
        if self.results["metrics"].get("total_files", 0) > 100:
            recommendations.append("Projet de grande taille - Considérer une architecture modulaire")
        
        if self.results["metrics"].get("python", {}).get("avg_lines_per_file", 0) > 200:
            recommendations.append("Fichiers très longs - Diviser en modules plus petits")
        
        # Recommandations basées sur les problèmes trouvés
        security_issues = [f for f in self.results["findings"] if f["type"] == "security"]
        if security_issues:
            recommendations.append("Problèmes de sécurité détectés - Audit de sécurité recommandé")
        
        quality_issues = [f for f in self.results["findings"] if f["type"] == "code_quality"]
        if quality_issues:
            recommendations.append("Problèmes de qualité détectés - Refactoring recommandé")
        
        self.results["recommendations"] = recommendations

async def run_generic_audit(project_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    """Fonction principale pour l'audit générique."""
    auditor = GenericAuditor(project_path, config)
    return await auditor.run_generic_audit()
