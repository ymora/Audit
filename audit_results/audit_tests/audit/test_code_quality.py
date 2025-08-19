#!/usr/bin/env python3
"""
Test de qualité du code pour le projet audit.
Utilise les outils existants : dead_code_detector, code_analyzer, etc.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# Ajouter le répertoire tools au path
tools_dir = Path(__file__).parent.parent.parent.parent / "tools"
sys.path.insert(0, str(tools_dir))

try:
    from dead_code_detector import DeadCodeDetector
    from code_analyzer import CodeAnalyzer
    from generic_auditor import GenericAuditor
    from security_checker import SecurityChecker
    from incomplete_implementation_detector import IncompleteImplementationDetector
except ImportError as e:
    print(f"Erreur import outils: {e}")
    # Fallback si les imports échouent
    DeadCodeDetector = None
    CodeAnalyzer = None
    GenericAuditor = None
    SecurityChecker = None
    IncompleteImplementationDetector = None

async def run_test(project_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test de qualité du code du projet audit."""
    
    results = {
        "success": False,
        "message": "",
        "details": {}
    }
    
    try:
        audit_dir = Path(__file__).parent.parent.parent
        quality_results = {}
        
        # 1. Détection du code mort
        if DeadCodeDetector:
            print("  🔍 Analyse du code mort...")
            dead_code_detector = DeadCodeDetector(project_path, audit_dir)
            dead_code_report = dead_code_detector.analyze_project()
            
            quality_results["dead_code"] = {
                "dead_functions": dead_code_report.get("dead_functions_count", 0),
                "dead_classes": dead_code_report.get("dead_classes_count", 0),
                "total_functions": dead_code_report.get("total_functions", 0),
                "total_classes": dead_code_report.get("total_classes", 0),
                "dead_functions_list": dead_code_report.get("dead_functions", []),
                "dead_classes_list": dead_code_report.get("dead_classes", [])
            }
        
        # 2. Analyse des duplications
        if CodeAnalyzer:
            print("  🔍 Analyse des duplications...")
            code_analyzer = CodeAnalyzer(project_path, audit_dir)
            duplication_report = code_analyzer.analyze_project()
            
            quality_results["duplications"] = {
                "total_duplications": duplication_report.get("duplications_found", 0),
                "files_analyzed": duplication_report.get("files_analyzed", 0),
                "duplications_list": duplication_report.get("duplications", []),
                "duplications_summary": duplication_report.get("duplications_summary", {})
            }
        
        # 3. Audit de sécurité
        if SecurityChecker:
            print("  🔒 Audit de sécurité...")
            security_checker = SecurityChecker(project_path, audit_dir)
            vulnerabilities = security_checker.scan_vulnerabilities()
            security_report = security_checker.generate_security_report(vulnerabilities)
            
            quality_results["security"] = security_report
        
        # 4. Détection d'implémentations incomplètes
        if IncompleteImplementationDetector:
            print("  🔍 Détection d'implémentations incomplètes...")
            incomplete_detector = IncompleteImplementationDetector(project_path, audit_dir)
            incomplete_report = incomplete_detector.analyze_project()
            
            quality_results["incomplete_implementations"] = incomplete_report
        
        # 5. Audit générique
        if GenericAuditor:
            print("  🔍 Audit générique...")
            generic_auditor = GenericAuditor(project_path, config)
            generic_report = await generic_auditor.run_generic_audit()
            
            quality_results["generic_audit"] = generic_report.get("generic_audit", {})
        
        # 6. Analyse de la structure
        structure_analysis = _analyze_project_structure(project_path)
        quality_results["structure"] = structure_analysis
        
        # 7. Évaluation globale
        score = _calculate_quality_score(quality_results)
        
        results["success"] = score >= 6  # Seuil de qualité
        results["message"] = f"Audit exhaustif terminé: {score}/10 points (code mort, duplications, sécurité, implémentations incomplètes)"
        results["details"] = quality_results
        results["details"]["quality_score"] = score
        
        return results
        
    except Exception as e:
        results["message"] = f"Erreur lors de l'analyse de qualité: {str(e)}"
        results["details"]["error"] = str(e)
        return results

def _analyze_project_structure(project_path: Path) -> Dict[str, Any]:
    """Analyse la structure du projet."""
    structure = {
        "total_files": 0,
        "python_files": 0,
        "test_files": 0,
        "doc_files": 0,
        "missing_essential": []
    }
    
    # Compter les fichiers
    for file_path in project_path.rglob("*"):
        if file_path.is_file():
            structure["total_files"] += 1
            
            if file_path.suffix == ".py":
                structure["python_files"] += 1
                
                if "test" in file_path.name.lower():
                    structure["test_files"] += 1
            
            elif file_path.suffix in [".md", ".txt", ".rst"]:
                structure["doc_files"] += 1
    
    # Vérifier les fichiers essentiels
    essential_files = ["README.md", "requirements.txt", "audit.py"]
    for file_name in essential_files:
        if not (project_path / file_name).exists():
            structure["missing_essential"].append(file_name)
    
    return structure

def _calculate_quality_score(quality_results: Dict[str, Any]) -> int:
    """Calcule un score de qualité global exhaustif."""
    score = 10
    
    # Pénaliser le code mort
    dead_code = quality_results.get("dead_code", {})
    dead_functions = dead_code.get("dead_functions", 0)
    dead_classes = dead_code.get("dead_classes", 0)
    
    if dead_functions > 0:
        score -= min(3, dead_functions // 5)  # -1 point par 5 fonctions mortes
    
    if dead_classes > 0:
        score -= min(2, dead_classes // 3)  # -1 point par 3 classes mortes
    
    # Pénaliser les duplications
    duplications = quality_results.get("duplications", {})
    total_duplications = duplications.get("total_duplications", 0)
    
    if total_duplications > 0:
        score -= min(3, total_duplications // 10)  # -1 point par 10 duplications
    
    # Pénaliser les problèmes de sécurité
    security = quality_results.get("security", {})
    if isinstance(security, dict) and "summary" in security:
        security_issues = security["summary"].get("total_vulnerabilities", 0)
        if security_issues > 0:
            score -= min(3, security_issues // 2)  # -1 point par 2 vulnérabilités
    
    # Pénaliser les implémentations incomplètes
    incomplete = quality_results.get("incomplete_implementations", {})
    incomplete_count = incomplete.get("incomplete_count", 0)
    
    if incomplete_count > 0:
        score -= min(2, incomplete_count)  # -1 point par implémentation incomplète
    
    # Pénaliser les fichiers manquants
    structure = quality_results.get("structure", {})
    missing_essential = len(structure.get("missing_essential", []))
    
    if missing_essential > 0:
        score -= missing_essential  # -1 point par fichier essentiel manquant
    
    # Bonus pour les tests
    test_files = structure.get("test_files", 0)
    if test_files > 0:
        score += min(2, test_files // 5)  # +1 point par 5 fichiers de test
    
    # Bonus pour la documentation
    doc_files = structure.get("doc_files", 0)
    if doc_files > 0:
        score += min(1, doc_files // 3)  # +1 point par 3 fichiers de doc
    
    return max(0, min(10, score))
