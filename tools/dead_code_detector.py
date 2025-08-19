#!/usr/bin/env python3
"""
DEAD CODE DETECTOR - AUDIT DOCUSENSE AI
=======================================

Détecte le code mort (fonctions/classes non utilisées) en analysant les imports
et références AST dans le projet.
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict

class DeadCodeDetector:
    """Détecteur de code mort basé sur l'analyse AST et des imports."""
    
    def __init__(self, project_dir: Path, audit_dir: Path):
        self.project_dir = project_dir
        self.project_dir = audit_dir
        self.excluded_patterns = [
            r'__pycache__',
            r'\.git',
            r'\.venv',
            r'venv',
            r'node_modules',
            r'\.pytest_cache',
            r'codemort',
            r'audit',
            r'\.backup',
            r'\.log',
            r'tests?/',
            r'test_',
            r'_test\.py$'
        ]
        
        # Cache pour les analyses
        self._import_graph = {}
        self._defined_functions = {}
        self._defined_classes = {}
        self._used_functions = set()
        self._used_classes = set()
    
    def is_excluded_file(self, file_path: Path) -> bool:
        """Vérifie si un fichier doit être exclu de l'analyse."""
        file_str = str(file_path)
        
        for pattern in self.excluded_patterns:
            if re.search(pattern, file_str, re.IGNORECASE):
                return True
        
        return False
    
    def analyze_project(self) -> Dict[str, Any]:
        """Analyse complète du projet pour détecter le code mort."""
        print("🔍 Analyse du code mort en cours...")
        
        # 1. Collecter tous les fichiers Python
        python_files = []
        for root, dirs, files in os.walk(self.project_dir):
            # Filtrer les dossiers exclus
            dirs[:] = [d for d in dirs if not self.is_excluded_file(Path(root) / d)]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    if not self.is_excluded_file(file_path):
                        python_files.append(file_path)
        
        print(f"  📁 {len(python_files)} fichiers Python analysés")
        
        # 2. Analyser chaque fichier
        for file_path in python_files:
            try:
                self._analyze_file(file_path)
            except Exception as e:
                print(f"  ⚠️ Erreur analyse {file_path}: {e}")
        
        # 3. Détecter le code mort
        dead_functions = self._find_dead_functions()
        dead_classes = self._find_dead_classes()
        
        # 4. Générer le rapport
        results = {
            'total_files': len(python_files),
            'total_functions': sum(len(funcs) for funcs in self._defined_functions.values()),
            'total_classes': sum(len(classes) for classes in self._defined_classes.values()),
            'dead_functions': dead_functions,
            'dead_classes': dead_classes,
            'dead_functions_count': len(dead_functions),
            'dead_classes_count': len(dead_classes),
            'import_graph': self._import_graph,
            'defined_functions': self._defined_functions,
            'defined_classes': self._defined_classes
        }
        
        print(f"  ⚰️ {len(dead_functions)} fonctions mortes détectées")
        print(f"  ⚰️ {len(dead_classes)} classes mortes détectées")
        
        return results
    
    def _analyze_file(self, file_path: Path):
        """Analyse un fichier Python pour extraire les définitions et usages."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            relative_path = file_path.relative_to(self.project_dir)
            
            # Analyser les imports
            self._analyze_imports(tree, relative_path)
            
            # Analyser les définitions
            self._analyze_definitions(tree, relative_path)
            
            # Analyser les usages
            self._analyze_usages(tree, relative_path)
            
        except Exception as e:
            print(f"  ⚠️ Erreur parsing {file_path}: {e}")
    
    def _analyze_imports(self, tree: ast.AST, file_path: Path):
        """Analyse les imports d'un fichier."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._import_graph[str(file_path)] = self._import_graph.get(str(file_path), set())
                    self._import_graph[str(file_path)].add(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    full_name = f"{module}.{alias.name}" if module else alias.name
                    self._import_graph[str(file_path)] = self._import_graph.get(str(file_path), set())
                    self._import_graph[str(file_path)].add(full_name)
    
    def _analyze_definitions(self, tree: ast.AST, file_path: Path):
        """Analyse les définitions de fonctions et classes."""
        file_str = str(file_path)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Ignorer les méthodes de classe
                if not self._is_class_method(node):
                    func_name = node.name
                    if file_str not in self._defined_functions:
                        self._defined_functions[file_str] = {}
                    
                    self._defined_functions[file_str][func_name] = {
                        'line': node.lineno,
                        'end_line': node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                        'is_async': isinstance(node, ast.AsyncFunctionDef),
                        'decorators': [self._get_decorator_name(d) for d in node.decorator_list]
                    }
            
            elif isinstance(node, ast.ClassDef):
                class_name = node.name
                if file_str not in self._defined_classes:
                    self._defined_classes[file_str] = {}
                
                self._defined_classes[file_str][class_name] = {
                    'line': node.lineno,
                    'end_line': node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                    'bases': [self._get_base_name(base) for base in node.bases],
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                }
    
    def _analyze_usages(self, tree: ast.AST, file_path: Path):
        """Analyse les usages de fonctions et classes."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                if func_name:
                    self._used_functions.add(func_name)
            
            elif isinstance(node, ast.Name):
                # Usage direct d'une classe ou fonction
                self._used_functions.add(node.id)
                self._used_classes.add(node.id)
            
            elif isinstance(node, ast.Attribute):
                # Usage via attribut (ex: module.function)
                attr_name = self._get_attribute_name(node)
                if attr_name:
                    self._used_functions.add(attr_name)
                    self._used_classes.add(attr_name)
    
    def _is_class_method(self, node: ast.FunctionDef) -> bool:
        """Vérifie si une fonction est une méthode de classe."""
        parent = getattr(node, 'parent', None)
        return parent and isinstance(parent, ast.ClassDef)
    
    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Extrait le nom d'un décorateur."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return self._get_attribute_name(decorator)
        return "unknown"
    
    def _get_base_name(self, base: ast.expr) -> str:
        """Extrait le nom d'une classe de base."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return self._get_attribute_name(base)
        return "unknown"
    
    def _get_call_name(self, node: ast.Call) -> str:
        """Extrait le nom d'un appel de fonction."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return self._get_attribute_name(node.func)
        return None
    
    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Extrait le nom complet d'un attribut."""
        parts = []
        current = node
        
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        
        if isinstance(current, ast.Name):
            parts.append(current.id)
        
        return '.'.join(reversed(parts))
    
    def _find_dead_functions(self) -> List[Dict[str, Any]]:
        """Trouve les fonctions mortes."""
        dead_functions = []
        
        for file_path, functions in self._defined_functions.items():
            for func_name, func_info in functions.items():
                # Vérifier si la fonction est utilisée
                if not self._is_function_used(func_name, file_path):
                    dead_functions.append({
                        'file': file_path,
                        'name': func_name,
                        'line': func_info['line'],
                        'end_line': func_info['end_line'],
                        'is_async': func_info['is_async'],
                        'decorators': func_info['decorators'],
                        'type': 'function'
                    })
        
        return dead_functions
    
    def _find_dead_classes(self) -> List[Dict[str, Any]]:
        """Trouve les classes mortes."""
        dead_classes = []
        
        for file_path, classes in self._defined_classes.items():
            for class_name, class_info in classes.items():
                # Vérifier si la classe est utilisée
                if not self._is_class_used(class_name, file_path):
                    dead_classes.append({
                        'file': file_path,
                        'name': class_name,
                        'line': class_info['line'],
                        'end_line': class_info['end_line'],
                        'bases': class_info['bases'],
                        'methods': class_info['methods'],
                        'type': 'class'
                    })
        
        return dead_classes
    
    def _is_function_used(self, func_name: str, file_path: str) -> bool:
        """Vérifie si une fonction est utilisée."""
        # Vérifier les usages directs
        if func_name in self._used_functions:
            return True
        
        # Vérifier les imports
        for imports in self._import_graph.values():
            for imported in imports:
                if imported.endswith(f'.{func_name}') or imported == func_name:
                    return True
        
        # Vérifier les patterns spéciaux
        if self._is_special_function(func_name):
            return True
        
        return False
    
    def _is_class_used(self, class_name: str, file_path: str) -> bool:
        """Vérifie si une classe est utilisée."""
        # Vérifier les usages directs
        if class_name in self._used_classes:
            return True
        
        # Vérifier les imports
        for imports in self._import_graph.values():
            for imported in imports:
                if imported.endswith(f'.{class_name}') or imported == class_name:
                    return True
        
        # Vérifier les patterns spéciaux
        if self._is_special_class(class_name):
            return True
        
        return False
    
    def _is_special_function(self, func_name: str) -> bool:
        """Vérifie si une fonction est spéciale (toujours considérée comme utilisée)."""
        special_patterns = [
            r'^__[a-z_]+__$',  # Méthodes magiques
            r'^main$',         # Point d'entrée
            r'^setup$',        # Setup scripts
            r'^run$',          # Fonctions de lancement
            r'^start$',        # Fonctions de démarrage
            r'^init$',         # Initialisation
            r'^create_app$',   # Factory Flask
            r'^get_app$',      # Factory FastAPI
        ]
        
        for pattern in special_patterns:
            if re.match(pattern, func_name, re.IGNORECASE):
                return True
        
        return False
    
    def _is_special_class(self, class_name: str) -> bool:
        """Vérifie si une classe est spéciale (toujours considérée comme utilisée)."""
        special_patterns = [
            r'^[A-Z][a-zA-Z]*Config$',  # Classes de configuration
            r'^[A-Z][a-zA-Z]*Manager$', # Classes de gestion
            r'^[A-Z][a-zA-Z]*Service$', # Classes de service
            r'^[A-Z][a-zA-Z]*Model$',   # Classes de modèle
            r'^[A-Z][a-zA-Z]*View$',    # Classes de vue
            r'^[A-Z][a-zA-Z]*Controller$', # Classes de contrôleur
        ]
        
        for pattern in special_patterns:
            if re.match(pattern, class_name, re.IGNORECASE):
                return True
        
        return False
    
    def generate_dead_code_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un rapport détaillé du code mort."""
        return {
            'summary': {
                'total_files': results['total_files'],
                'total_functions': results['total_functions'],
                'total_classes': results['total_classes'],
                'dead_functions_count': results['dead_functions_count'],
                'dead_classes_count': results['dead_classes_count'],
                'dead_code_percentage': self._calculate_dead_code_percentage(results)
            },
            'dead_functions': results['dead_functions'],
            'dead_classes': results['dead_classes'],
            'recommendations': self._generate_dead_code_recommendations(results)
        }
    
    def _calculate_dead_code_percentage(self, results: Dict[str, Any]) -> float:
        """Calcule le pourcentage de code mort."""
        total_code = results['total_functions'] + results['total_classes']
        dead_code = results['dead_functions_count'] + results['dead_classes_count']
        
        if total_code == 0:
            return 0.0
        
        return round((dead_code / total_code) * 100, 2)
    
    def _generate_dead_code_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Génère des recommandations pour le code mort."""
        recommendations = []
        
        dead_count = results['dead_functions_count'] + results['dead_classes_count']
        
        if dead_count == 0:
            recommendations.append("✅ Aucun code mort détecté - excellent travail de maintenance !")
        elif dead_count <= 5:
            recommendations.append("⚠️ Quelques éléments de code mort détectés - considérer leur suppression")
        elif dead_count <= 15:
            recommendations.append("🔧 Code mort modéré détecté - planifier un nettoyage")
        else:
            recommendations.append("🚨 Code mort important détecté - nettoyage prioritaire recommandé")
        
        if results['dead_functions_count'] > 0:
            recommendations.append(f"Supprimer ou documenter les {results['dead_functions_count']} fonctions non utilisées")
        
        if results['dead_classes_count'] > 0:
            recommendations.append(f"Supprimer ou documenter les {results['dead_classes_count']} classes non utilisées")
        
        recommendations.append("Maintenir une analyse régulière du code mort pour optimiser la base de code")
        
        return recommendations

