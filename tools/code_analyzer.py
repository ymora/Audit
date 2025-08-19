#!/usr/bin/env python3
"""
CODE ANALYZER - AUDIT DOCUSENSE AI
==================================

Analyseur de code intelligent qui respecte les règles configurées.
Différencie les duplications légitimes des vraies duplications.
Analyse la qualité, sécurité et architecture du code.

RÈGLES INTELLIGENTES :
- Respect des patterns d'architecture légitimes
- Détection des wrappers et décorateurs
- Analyse contextuelle des duplications
- Validation de la qualité avant signalement
"""

import os
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict

class CodeAnalyzer:
    def __init__(self, project_dir: Path = None, audit_dir: Path = None):
        self.project_dir = project_dir or Path(__file__).resolve().parent.parent.parent
        self.project_dir = audit_dir or Path(__file__).resolve().parent.parent
        self.rules = self.load_rules()
        self.excluded_patterns = self.load_excluded_patterns()
        self.quality_standards = self.load_quality_standards()
        
        # Cache pour les analyses
        self.function_cache = {}
        self.class_cache = {}
        self.import_cache = {}
        self.duplication_cache = {}
        
    def load_rules(self) -> Dict[str, Any]:
        """Charge les règles d'audit."""
        rules_file = self.project_dir / "rules" / "audit_rules.json"
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erreur chargement règles: {e}")
            return {}
    
    def load_excluded_patterns(self) -> Dict[str, Any]:
        """Charge les patterns à exclure."""
        patterns_file = self.project_dir / "rules" / "excluded_patterns.json"
        try:
            with open(patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erreur chargement patterns exclus: {e}")
            return {}
    
    def load_quality_standards(self) -> Dict[str, Any]:
        """Charge les standards de qualité."""
        standards_file = self.project_dir / "rules" / "quality_standards.json"
        try:
            with open(standards_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erreur chargement standards qualité: {e}")
            return {}
    
    def is_excluded_file(self, file_path: Path) -> bool:
        """Vérifie si un fichier doit être exclu de l'analyse."""
        # Vérifier les répertoires exclus
        excluded_dirs = self.excluded_patterns.get('excluded_patterns', {}).get('directories', [])
        for excluded_dir in excluded_dirs:
            if excluded_dir in str(file_path):
                return True
        
        # Vérifier les patterns de fichiers
        excluded_files = self.excluded_patterns.get('excluded_patterns', {}).get('files', [])
        for pattern in excluded_files:
            if file_path.match(pattern):
                return True
        
        return False
    
    def is_legitimate_duplication(self, func_name: str, context: str) -> bool:
        """Vérifie si une duplication est légitime selon les règles."""
        legitimate_patterns = self.rules.get('audit_rules', {}).get('legitimate_patterns', {})
        
        # Patterns d'héritage
        inheritance_patterns = legitimate_patterns.get('inheritance_patterns', [])
        for pattern in inheritance_patterns:
            if pattern in func_name:
                return True
        
        # Patterns de wrapper
        wrapper_patterns = legitimate_patterns.get('wrapper_patterns', [])
        for pattern in wrapper_patterns:
            if pattern in func_name:
                return True
        
        # Patterns de décorateur
        decorator_patterns = legitimate_patterns.get('decorator_patterns', [])
        for pattern in decorator_patterns:
            if pattern in func_name:
                return True
        
        # Patterns de streaming
        streaming_patterns = legitimate_patterns.get('streaming_patterns', [])
        for pattern in streaming_patterns:
            if pattern in func_name:
                return True
        
        # Patterns légitimes spécifiques
        legitimate_functions = [
            '__init__',  # Constructeurs de classes
            '__repr__',  # Méthodes de représentation
            '__str__',   # Méthodes de conversion en string
            '__eq__',    # Méthodes de comparaison
            '__hash__',  # Méthodes de hachage
            '__len__',   # Méthodes de longueur
            '__getitem__', # Méthodes d'accès
            '__setitem__', # Méthodes de modification
            '__delitem__', # Méthodes de suppression
            '__iter__',  # Méthodes d'itération
            '__next__',  # Méthodes d'itération
            '__enter__', # Méthodes de contexte
            '__exit__',  # Méthodes de contexte
            'main',      # Fonctions main
            'test_',     # Fonctions de test
            'setup_',    # Fonctions de configuration
            'teardown_', # Fonctions de nettoyage
            'get_',      # Getters
            'set_',      # Setters
            'is_',       # Fonctions de validation
            'has_',      # Fonctions de vérification
            'validate_', # Fonctions de validation
            'check_',    # Fonctions de vérification
            'verify_',   # Fonctions de vérification
            'create_',   # Fonctions de création
            'generate_', # Fonctions de génération
            'process_',  # Fonctions de traitement
            'handle_',   # Fonctions de gestion
            'parse_',    # Fonctions de parsing
            'format_',   # Fonctions de formatage
            'convert_',  # Fonctions de conversion
            'transform_', # Fonctions de transformation
            'extract_',  # Fonctions d'extraction
            'load_',     # Fonctions de chargement
            'save_',     # Fonctions de sauvegarde
            'export_',   # Fonctions d'export
            'import_',   # Fonctions d'import
            'sync_',     # Fonctions de synchronisation
            'async_',    # Fonctions asynchrones
            'success_response',  # Réponses API
            'error_response',    # Réponses API
            'cleanup_',  # Fonctions de nettoyage
            'hash_',     # Fonctions de hachage
            'encrypt_',  # Fonctions de chiffrement
            'decrypt_',  # Fonctions de déchiffrement
            'decorator', # Décorateurs
            'wrapper',   # Wrappers
        ]
        
        for pattern in legitimate_functions:
            if func_name.startswith(pattern) or func_name == pattern:
                return True
        
        return False
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyse un fichier Python."""
        if not file_path.suffix == '.py':
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            analysis = {
                'file_path': str(file_path),
                'functions': [],
                'classes': [],
                'imports': [],
                'issues': [],
                'metrics': {}
            }
            
            # Analyser les fonctions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_analysis = self.analyze_function(node, content)
                    if not self.is_excluded_function(func_analysis['name']):
                        analysis['functions'].append(func_analysis)
                
                elif isinstance(node, ast.ClassDef):
                    class_analysis = self.analyze_class(node, content)
                    if not self.is_excluded_class(class_analysis['name']):
                        analysis['classes'].append(class_analysis)
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis['imports'].append(node.module)
            
            # Calculer les métriques
            analysis['metrics'] = self.calculate_metrics(analysis, content)
            
            return analysis
            
        except Exception as e:
            return {
                'file_path': str(file_path),
                'error': str(e),
                'functions': [],
                'classes': [],
                'imports': [],
                'issues': [],
                'metrics': {}
            }
    
    def analyze_function(self, node: ast.FunctionDef, content: str) -> Dict[str, Any]:
        """Analyse une fonction."""
        # Extraire le code de la fonction
        start_line = node.lineno - 1
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
        
        func_lines = content.split('\n')[start_line:end_line]
        func_code = '\n'.join(func_lines)
        
        # Vérifier si la fonction est légitime
        is_legitimate = self.is_legitimate_duplication(node.name, 'function')
        
        analysis = {
            'name': node.name,
            'lineno': node.lineno,
            'end_lineno': getattr(node, 'end_lineno', node.lineno),
            'args': [arg.arg for arg in node.args.args],
            'decorators': [self.get_decorator_name(d) for d in node.decorator_list],
            'lines': len(func_lines),
            'complexity': self.calculate_cyclomatic_complexity(node),
            'nesting_depth': self.calculate_nesting_depth(node),
            'code': func_code,
            'is_legitimate': is_legitimate
        }
        
        # Vérifier les standards de qualité
        quality_issues = self.check_function_quality(analysis)
        analysis['quality_issues'] = quality_issues
        
        return analysis
    
    def analyze_class(self, node: ast.ClassDef, content: str) -> Dict[str, Any]:
        """Analyse une classe."""
        analysis = {
            'name': node.name,
            'lineno': node.lineno,
            'end_lineno': getattr(node, 'end_lineno', node.lineno),
            'bases': [self.get_base_name(base) for base in node.bases],
            'methods': [],
            'is_legitimate': self.is_legitimate_duplication(node.name, 'class')
        }
        
        # Analyser les méthodes
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_analysis = self.analyze_function(item, content)
                analysis['methods'].append(method_analysis)
        
        return analysis
    
    def get_decorator_name(self, decorator: ast.expr) -> str:
        """Extrait le nom d'un décorateur."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{self.get_attribute_name(decorator.value)}.{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return f"{self.get_attribute_name(decorator.func.value)}.{decorator.func.attr}"
        return "unknown"
    
    def get_attribute_name(self, node: ast.expr) -> str:
        """Extrait le nom d'un attribut."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self.get_attribute_name(node.value)}.{node.attr}"
        return "unknown"
    
    def get_base_name(self, base: ast.expr) -> str:
        """Extrait le nom d'une classe de base."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return f"{self.get_attribute_name(base.value)}.{base.attr}"
        return "unknown"
    
    def calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calcule la complexité cyclomatique d'une fonction."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With):
                complexity += 1
            elif isinstance(child, ast.AsyncWith):
                complexity += 1
        
        return complexity
    
    def calculate_nesting_depth(self, node: ast.FunctionDef) -> int:
        """Calcule la profondeur d'imbrication d'une fonction."""
        max_depth = 0
        current_depth = 0
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.AsyncWith)):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif isinstance(child, ast.FunctionDef):
                # Reset depth for nested functions
                current_depth = 0
        
        return max_depth
    
    def is_excluded_function(self, func_name: str) -> bool:
        """Vérifie si une fonction doit être exclue."""
        excluded_functions = self.rules.get('audit_rules', {}).get('excluded_functions', [])
        return func_name in excluded_functions
    
    def is_excluded_class(self, class_name: str) -> bool:
        """Vérifie si une classe doit être exclue."""
        excluded_patterns = self.excluded_patterns.get('excluded_patterns', {}).get('class_patterns', [])
        for pattern in excluded_patterns:
            if pattern.replace('*', '') in class_name:
                return True
        return False
    
    def check_function_quality(self, func_analysis: Dict[str, Any]) -> List[str]:
        """Vérifie la qualité d'une fonction selon les standards."""
        issues = []
        standards = self.quality_standards.get('quality_standards', {}).get('code_metrics', {})
        
        # Vérifier la longueur de fonction
        max_lines = standards.get('function_length', {}).get('max_lines', 50)
        if func_analysis['lines'] > max_lines:
            issues.append(f"Fonction trop longue: {func_analysis['lines']} lignes (max: {max_lines})")
        
        # Vérifier le nombre de paramètres
        max_params = standards.get('parameters', {}).get('max_count', 5)
        if len(func_analysis['args']) > max_params:
            issues.append(f"Trop de paramètres: {len(func_analysis['args'])} (max: {max_params})")
        
        # Vérifier la complexité cyclomatique
        max_complexity = standards.get('cyclomatic_complexity', {}).get('max_value', 10)
        if func_analysis['complexity'] > max_complexity:
            issues.append(f"Complexité cyclomatique élevée: {func_analysis['complexity']} (max: {max_complexity})")
        
        # Vérifier la profondeur d'imbrication
        max_nesting = standards.get('nesting_depth', {}).get('max_levels', 4)
        if func_analysis['nesting_depth'] > max_nesting:
            issues.append(f"Imbrication trop profonde: {func_analysis['nesting_depth']} niveaux (max: {max_nesting})")
        
        return issues
    
    def calculate_metrics(self, analysis: Dict[str, Any], content: str) -> Dict[str, Any]:
        """Calcule les métriques globales du fichier."""
        total_lines = len(content.split('\n'))
        code_lines = len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')])
        comment_lines = len([line for line in content.split('\n') if line.strip().startswith('#')])
        
        return {
            'total_lines': total_lines,
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'comment_ratio': comment_lines / max(code_lines, 1),
            'function_count': len(analysis['functions']),
            'class_count': len(analysis['classes']),
            'import_count': len(analysis['imports'])
        }
    
    def find_duplications(self, all_analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Trouve les duplications de code en respectant les règles."""
        duplications = []
        legitimate_duplications = []
        function_groups = defaultdict(list)
        
        # Grouper toutes les fonctions par nom
        for analysis in all_analyses:
            for func in analysis['functions']:
                function_groups[func['name']].append({
                    'file': analysis['file_path'],
                    'function': func,
                    'is_legitimate': func.get('is_legitimate', False)
                })
        
        # Analyser chaque groupe de fonctions
        for func_name, occurrences in function_groups.items():
            if len(occurrences) > 1:
                # Séparer les occurrences légitimes et non légitimes
                legitimate_occurrences = [occ for occ in occurrences if occ['is_legitimate']]
                non_legitimate_occurrences = [occ for occ in occurrences if not occ['is_legitimate']]
                
                # Traiter les duplications légitimes
                if len(legitimate_occurrences) > 1:
                    similar_groups = self.group_similar_functions(legitimate_occurrences)
                    for group in similar_groups:
                        if len(group) > 1:
                            legitimate_duplications.append({
                                'function_name': func_name,
                                'occurrences': group,
                                'count': len(group),
                                'severity': 'low',
                                'type': 'legitimate',
                                'reason': self.get_legitimate_reason(func_name)
                            })
                
                # Traiter les vraies duplications à corriger
                if len(non_legitimate_occurrences) > 1:
                    similar_groups = self.group_similar_functions(non_legitimate_occurrences)
                    for group in similar_groups:
                        if len(group) > 1:
                            duplications.append({
                                'function_name': func_name,
                                'occurrences': group,
                                'count': len(group),
                                'severity': 'high' if len(group) > 3 else 'medium',
                                'type': 'to_fix',
                                'recommendation': self.get_fix_recommendation(func_name, group)
                            })
        
        # Retourner les vraies duplications à corriger
        return duplications + legitimate_duplications
    
    def get_legitimate_reason(self, func_name: str) -> str:
        """Retourne la raison pour laquelle une duplication est légitime."""
        if func_name == '__init__':
            return "Constructeurs de classes (normal)"
        elif func_name == '__repr__':
            return "Méthodes de représentation (normal)"
        elif func_name.startswith('test_'):
            return "Fonctions de test (normal)"
        elif func_name.startswith('get_'):
            return "Getters (pattern normal)"
        elif func_name.startswith('set_'):
            return "Setters (pattern normal)"
        elif func_name.startswith('is_'):
            return "Fonctions de validation (pattern normal)"
        elif func_name.startswith('validate_'):
            return "Fonctions de validation (pattern normal)"
        elif func_name.startswith('success_response') or func_name.startswith('error_response'):
            return "Réponses API standardisées (normal)"
        elif func_name.startswith('cleanup_'):
            return "Fonctions de nettoyage (pattern normal)"
        else:
            return "Pattern de développement légitime"
    
    def get_fix_recommendation(self, func_name: str, occurrences: List[Dict[str, Any]]) -> str:
        """Retourne une recommandation pour corriger la duplication."""
        files = [occ['file'] for occ in occurrences]
        
        if len(occurrences) > 3:
            return f"CRITIQUE: Refactoriser en service partagé. Fonction '{func_name}' dupliquée dans {len(occurrences)} fichiers"
        elif len(occurrences) > 2:
            return f"IMPORTANT: Créer une fonction utilitaire commune. Fonction '{func_name}' dupliquée dans {len(occurrences)} fichiers"
        else:
            return f"Considérer la création d'une fonction utilitaire pour '{func_name}'"
    
    def group_similar_functions(self, occurrences: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Groupe les fonctions similaires basées sur leur code."""
        groups = []
        processed = set()
        
        for i, occ1 in enumerate(occurrences):
            if i in processed:
                continue
            
            group = [occ1]
            processed.add(i)
            
            for j, occ2 in enumerate(occurrences[i+1:], i+1):
                if j in processed:
                    continue
                
                # Comparer le code des fonctions (vérifier que 'code' existe)
                code1 = occ1['function'].get('code', '')
                code2 = occ2['function'].get('code', '')
                similarity = self.calculate_code_similarity(code1, code2)
                
                if similarity > 0.8:  # 80% de similarité
                    group.append(occ2)
                    processed.add(j)
            
            groups.append(group)
        
        return groups
    
    def calculate_code_similarity(self, code1: str, code2: str) -> float:
        """Calcule la similarité entre deux blocs de code."""
        # Normaliser le code (supprimer espaces, commentaires)
        def normalize_code(code):
            lines = [line.strip() for line in code.split('\n')]
            lines = [line for line in lines if line and not line.startswith('#')]
            return '\n'.join(lines)
        
        norm1 = normalize_code(code1)
        norm2 = normalize_code(code2)
        
        if norm1 == norm2:
            return 1.0
        
        # Calcul simple basé sur les lignes communes
        lines1 = set(norm1.split('\n'))
        lines2 = set(norm2.split('\n'))
        
        if not lines1 or not lines2:
            return 0.0
        
        intersection = lines1.intersection(lines2)
        union = lines1.union(lines2)
        
        return len(intersection) / len(union)
    
    def analyze_project(self) -> Dict[str, Any]:
        """Analyse complète du projet."""
        print("🔍 Début de l'analyse intelligente du projet...")
        
        all_analyses = []
        python_files = []
        
        # Trouver tous les fichiers Python
        for root, dirs, files in os.walk(self.project_dir):
            # Exclure les répertoires
            dirs[:] = [d for d in dirs if not self.is_excluded_file(Path(root) / d)]
            
            for file in files:
                file_path = Path(root) / file
                if file.endswith('.py') and not self.is_excluded_file(file_path):
                    python_files.append(file_path)
        
        print(f"📁 {len(python_files)} fichiers Python à analyser")
        
        # Analyser chaque fichier
        for i, file_path in enumerate(python_files, 1):
            print(f"📄 Analyse {i}/{len(python_files)}: {file_path.name}")
            analysis = self.analyze_file(file_path)
            if analysis:
                all_analyses.append(analysis)
        
        # Trouver les duplications
        print("🔍 Recherche des duplications...")
        duplications = self.find_duplications(all_analyses)
        
        # Générer le rapport
        report = {
            'project_path': str(self.project_dir),
            'analysis_date': str(Path.cwd()),
            'files_analyzed': len(all_analyses),
            'total_functions': sum(len(a['functions']) for a in all_analyses),
            'total_classes': sum(len(a['classes']) for a in all_analyses),
            'duplications_found': len(duplications),
            'duplications': duplications,
            'duplications_summary': {
                'total_duplications': len(duplications),
                'duplications_to_fix': len([d for d in duplications if d.get('type') == 'to_fix']),
                'legitimate_duplications': len([d for d in duplications if d.get('type') == 'legitimate']),
                'critical_duplications': len([d for d in duplications if d.get('severity') == 'high']),
                'medium_duplications': len([d for d in duplications if d.get('severity') == 'medium'])
            },
            'quality_issues': self.aggregate_quality_issues(all_analyses),
            'metrics': self.aggregate_metrics(all_analyses)
        }
        
        print(f"✅ Analyse terminée: {len(duplications)} duplications trouvées")
        return report
    
    def aggregate_quality_issues(self, all_analyses: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Agrège les problèmes de qualité."""
        issues = defaultdict(list)
        
        for analysis in all_analyses:
            for func in analysis['functions']:
                for issue in func.get('quality_issues', []):
                    issues[analysis['file_path']].append(f"{func['name']}: {issue}")
        
        return dict(issues)
    
    def aggregate_metrics(self, all_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Agrège les métriques globales."""
        total_lines = sum(a['metrics']['total_lines'] for a in all_analyses)
        total_functions = sum(a['metrics']['function_count'] for a in all_analyses)
        total_classes = sum(a['metrics']['class_count'] for a in all_analyses)
        
        return {
            'total_lines': total_lines,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'average_function_length': total_lines / max(total_functions, 1)
        }
    

    
    def find_duplicated_functions(self) -> List[Dict[str, Any]]:
        """Détecte les fonctions dupliquées dans le projet."""
        duplicated_functions = []
        
        # Analyser tous les fichiers Python
        python_files = list(self.project_dir.rglob("*.py"))
        function_signatures = {}
        
        for file_path in python_files:
            if self.is_excluded_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Créer une signature simplifiée
                        signature = f"{node.name}_{len(node.args.args)}"
                        
                        if signature in function_signatures:
                            duplicated_functions.append({
                                "function_name": node.name,
                                "file1": str(function_signatures[signature]),
                                "file2": str(file_path),
                                "line": node.lineno
                            })
                        else:
                            function_signatures[signature] = file_path
                            
            except Exception:
                continue
        
        return duplicated_functions
    
    def find_duplicated_classes(self) -> List[Dict[str, Any]]:
        """Détecte les classes dupliquées dans le projet."""
        duplicated_classes = []
        
        # Analyser tous les fichiers Python
        python_files = list(self.project_dir.rglob("*.py"))
        class_names = {}
        
        for file_path in python_files:
            if self.is_excluded_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name
                        
                        if class_name in class_names:
                            duplicated_classes.append({
                                "class_name": class_name,
                                "file1": str(class_names[class_name]),
                                "file2": str(file_path),
                                "line": node.lineno
                            })
                        else:
                            class_names[class_name] = file_path
                            
            except Exception:
                continue
        
        return duplicated_classes
    
    def find_similar_code_blocks(self) -> List[Dict[str, Any]]:
        """Détecte les blocs de code similaires."""
        similar_blocks = []
        
        # Analyser tous les fichiers Python
        python_files = list(self.project_dir.rglob("*.py"))
        
        for i, file1 in enumerate(python_files):
            if self.is_excluded_file(file1):
                continue
                
            try:
                with open(file1, 'r', encoding='utf-8') as f:
                    content1 = f.read()
                
                # Diviser en blocs de 5 lignes
                lines1 = content1.split('\n')
                blocks1 = ['\n'.join(lines1[j:j+5]) for j in range(0, len(lines1), 5)]
                
                for file2 in python_files[i+1:]:
                    if self.is_excluded_file(file2):
                        continue
                        
                    try:
                        with open(file2, 'r', encoding='utf-8') as f:
                            content2 = f.read()
                        
                        lines2 = content2.split('\n')
                        blocks2 = ['\n'.join(lines2[j:j+5]) for j in range(0, len(lines2), 5)]
                        
                        # Comparer les blocs
                        for block1 in blocks1:
                            for block2 in blocks2:
                                if len(block1) > 50 and block1 == block2:
                                    similar_blocks.append({
                                        "file1": str(file1),
                                        "file2": str(file2),
                                        "block": block1[:100] + "..." if len(block1) > 100 else block1
                                    })
                                    
                    except Exception:
                        continue
                        
            except Exception:
                continue
        
        return similar_blocks
    
    def calculate_quality_metrics(self) -> Dict[str, Any]:
        """Calcule les métriques de qualité du projet."""
        metrics = {
            "total_files": 0,
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "average_function_length": 0,
            "average_class_length": 0,
            "complexity_score": 0
        }
        
        # Analyser tous les fichiers Python
        python_files = list(self.project_dir.rglob("*.py"))
        metrics["total_files"] = len(python_files)
        
        total_function_lines = 0
        total_class_lines = 0
        
        for file_path in python_files:
            if self.is_excluded_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                metrics["total_lines"] += len(lines)
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        metrics["total_functions"] += 1
                        # Estimer la longueur de la fonction
                        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                            function_lines = node.end_lineno - node.lineno
                            total_function_lines += function_lines
                        else:
                            total_function_lines += 10  # Estimation par défaut
                            
                    elif isinstance(node, ast.ClassDef):
                        metrics["total_classes"] += 1
                        # Estimer la longueur de la classe
                        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                            class_lines = node.end_lineno - node.lineno
                            total_class_lines += class_lines
                        else:
                            total_class_lines += 20  # Estimation par défaut
                            
            except Exception:
                continue
        
        # Calculer les moyennes
        if metrics["total_functions"] > 0:
            metrics["average_function_length"] = total_function_lines / metrics["total_functions"]
        
        if metrics["total_classes"] > 0:
            metrics["average_class_length"] = total_class_lines / metrics["total_classes"]
        
        # Calculer un score de complexité simple
        metrics["complexity_score"] = min(100, max(0, 
            (metrics["total_lines"] / max(metrics["total_files"], 1)) * 0.1 +
            (metrics["total_functions"] / max(metrics["total_files"], 1)) * 0.3 +
            (metrics["total_classes"] / max(metrics["total_files"], 1)) * 0.2
        ))
        
        return metrics
    
    def calculate_quality_score(self, metrics: Dict[str, Any]) -> int:
        """Calcule un score de qualité global (0-100)."""
        score = 100
        
        # Pénaliser les fichiers trop longs
        avg_lines_per_file = metrics.get("total_lines", 0) / max(metrics.get("total_files", 1), 1)
        if avg_lines_per_file > 500:
            score -= 20
        elif avg_lines_per_file > 300:
            score -= 10
        
        # Pénaliser les fonctions trop longues
        avg_function_length = metrics.get("average_function_length", 0)
        if avg_function_length > 50:
            score -= 15
        elif avg_function_length > 30:
            score -= 8
        
        # Pénaliser les classes trop longues
        avg_class_length = metrics.get("average_class_length", 0)
        if avg_class_length > 200:
            score -= 15
        elif avg_class_length > 100:
            score -= 8
        
        # Bonus pour une bonne structure
        if metrics.get("total_classes", 0) > 0:
            score += 5
        
        return max(0, min(100, score))
    
    def suggest_improvements(self, metrics: Dict[str, Any]) -> List[str]:
        """Suggère des améliorations basées sur les métriques."""
        improvements = []
        
        avg_lines_per_file = metrics.get("total_lines", 0) / max(metrics.get("total_files", 1), 1)
        if avg_lines_per_file > 500:
            improvements.append("Diviser les fichiers trop longs en modules plus petits")
        
        avg_function_length = metrics.get("average_function_length", 0)
        if avg_function_length > 50:
            improvements.append("Refactoriser les fonctions trop longues")
        
        avg_class_length = metrics.get("average_class_length", 0)
        if avg_class_length > 200:
            improvements.append("Diviser les classes trop longues")
        
        if metrics.get("total_classes", 0) == 0:
            improvements.append("Considérer l'utilisation de classes pour organiser le code")
        
        return improvements

def main():
    """Fonction principale."""
    # Le script est dans audit/tools/
    audit_dir = Path(__file__).resolve().parent.parent
    project_dir = audit_dir.parent
    
    analyzer = CodeAnalyzer(project_dir, audit_dir)
    report = analyzer.analyze_project()
    
    # Sauvegarder le rapport
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = audit_dir / "reports" / "latest" / f"{timestamp}_analyse_code_intelligente.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Rapport sauvegardé: {report_file}")

if __name__ == "__main__":
    from datetime import datetime
    main()
