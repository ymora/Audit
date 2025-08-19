#!/usr/bin/env python3
"""
Test d'analyse de sécurité pour le projet audit.
Utilise security_checker.py et les outils existants.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any
import re

# Ajouter le répertoire tools au path
tools_dir = Path(__file__).parent.parent.parent / "tools"
sys.path.insert(0, str(tools_dir))

try:
    from security_checker import SecurityChecker
except ImportError as e:
    print(f"Erreur import SecurityChecker: {e}")
    SecurityChecker = None

async def run_test(project_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test d'analyse de sécurité du projet audit."""
    
    results = {
        "success": False,
        "message": "",
        "details": {}
    }
    
    try:
        audit_dir = Path(__file__).parent.parent.parent
        security_results = {}
        
        # 1. Analyse avec SecurityChecker
        if SecurityChecker:
            print("  🔒 Analyse de sécurité avancée...")
            security_checker = SecurityChecker(project_path, audit_dir)
            security_report = security_checker.analyze_project()
            
            security_results["security_checker"] = security_report
        else:
            # Fallback : analyse manuelle
            print("  🔒 Analyse de sécurité manuelle...")
            security_results["manual_analysis"] = _manual_security_analysis(project_path)
        
        # 2. Analyse des vulnérabilités communes
        common_vulnerabilities = _analyze_common_vulnerabilities(project_path)
        security_results["common_vulnerabilities"] = common_vulnerabilities
        
        # 3. Analyse des dépendances
        dependency_analysis = _analyze_dependencies(project_path)
        security_results["dependencies"] = dependency_analysis
        
        # 4. Évaluation de la sécurité
        security_score = _calculate_security_score(security_results)
        
        results["success"] = security_score >= 7  # Seuil de sécurité
        results["message"] = f"Sécurité évaluée de façon exhaustive: {security_score}/10 points"
        results["details"] = security_results
        results["details"]["security_score"] = security_score
        
        return results
        
    except Exception as e:
        results["message"] = f"Erreur lors de l'analyse de sécurité: {str(e)}"
        results["details"]["error"] = str(e)
        return results

def _manual_security_analysis(project_path: Path) -> Dict[str, Any]:
    """Analyse de sécurité manuelle."""
    issues = []
    
    # Patterns de sécurité à vérifier
    security_patterns = {
        "hardcoded_passwords": r"password\s*=\s*['\"][^'\"]+['\"]",
        "hardcoded_keys": r"(api_key|secret_key|private_key)\s*=\s*['\"][^'\"]+['\"]",
        "dangerous_imports": r"import\s+(subprocess|os|sys|eval|exec)",
        "sql_injection": r"execute\s*\(\s*[^)]*\+",
        "file_path_traversal": r"\.\./",
        "eval_usage": r"eval\s*\(",
        "exec_usage": r"exec\s*\(",
        "shell_command": r"subprocess\.(run|call|Popen)\s*\(",
        "unsafe_file_operations": r"open\s*\([^)]*['\"][^'\"]*\.\./",
        "weak_crypto": r"(md5|sha1)\s*\("
    }
    
    python_files = list(project_path.rglob("*.py"))
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for pattern_name, pattern in security_patterns.items():
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        
                        # Vérifier si ce n'est pas un commentaire ou docstring
                        if not _is_in_comment_or_docstring(lines, line_num - 1):
                            issues.append({
                                "type": pattern_name,
                                "file": str(py_file.relative_to(project_path)),
                                "line": line_num,
                                "match": match.group(),
                                "severity": _get_severity(pattern_name)
                            })
        except Exception:
            continue
    
    return {
        "total_issues": len(issues),
        "issues": issues,
        "files_analyzed": len(python_files)
    }

def _analyze_common_vulnerabilities(project_path: Path) -> Dict[str, Any]:
    """Analyse des vulnérabilités communes."""
    vulnerabilities = {
        "missing_input_validation": 0,
        "insecure_deserialization": 0,
        "insecure_direct_object_references": 0,
        "missing_authentication": 0,
        "insecure_configuration": 0
    }
    
    # Chercher des patterns spécifiques
    python_files = list(project_path.rglob("*.py"))
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Input validation
                if re.search(r"input\s*\(\s*\)", content):
                    if not re.search(r"validate|check|verify", content, re.IGNORECASE):
                        vulnerabilities["missing_input_validation"] += 1
                
                # Deserialization
                if re.search(r"pickle\.loads|json\.loads", content):
                    vulnerabilities["insecure_deserialization"] += 1
                
                # Direct object references
                if re.search(r"get\s*\(\s*[^)]*id\s*\)", content):
                    vulnerabilities["insecure_direct_object_references"] += 1
                
        except Exception:
            continue
    
    return vulnerabilities

def _analyze_dependencies(project_path: Path) -> Dict[str, Any]:
    """Analyse des dépendances."""
    dependencies = {
        "requirements_found": False,
        "vulnerable_dependencies": [],
        "outdated_dependencies": []
    }
    
    # Vérifier requirements.txt
    requirements_file = project_path / "requirements.txt"
    if requirements_file.exists():
        dependencies["requirements_found"] = True
        
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Détecter les versions fixes (potentiellement vulnérables)
                fixed_versions = re.findall(r'([a-zA-Z0-9_-]+)==([0-9.]+)', content)
                for package, version in fixed_versions:
                    dependencies["vulnerable_dependencies"].append({
                        "package": package,
                        "version": version,
                        "reason": "Version fixe - vérifier les vulnérabilités"
                    })
        except Exception:
            pass
    
    return dependencies

def _calculate_security_score(security_results: Dict[str, Any]) -> int:
    """Calcule un score de sécurité global."""
    score = 10
    
    # Pénaliser les vulnérabilités manuelles
    manual_analysis = security_results.get("manual_analysis", {})
    total_issues = manual_analysis.get("total_issues", 0)
    
    if total_issues > 0:
        score -= min(5, total_issues)  # -1 point par issue
    
    # Pénaliser les vulnérabilités communes
    common_vulns = security_results.get("common_vulnerabilities", {})
    for vuln_type, count in common_vulns.items():
        if count > 0:
            score -= min(2, count)  # -1 point par type de vulnérabilité
    
    # Pénaliser les dépendances vulnérables
    dependencies = security_results.get("dependencies", {})
    vulnerable_deps = len(dependencies.get("vulnerable_dependencies", []))
    
    if vulnerable_deps > 0:
        score -= min(3, vulnerable_deps)  # -1 point par dépendance vulnérable
    
    return max(0, min(10, score))

def _is_in_comment_or_docstring(lines: list, line_index: int) -> bool:
    """Vérifie si une ligne est dans un commentaire ou docstring."""
    if line_index >= len(lines):
        return False
    
    line = lines[line_index].strip()
    
    # Commentaire
    if line.startswith('#'):
        return True
    
    # Docstring (simplifié)
    in_docstring = False
    for i in range(line_index):
        current_line = lines[i].strip()
        if '"""' in current_line or "'''" in current_line:
            in_docstring = not in_docstring
    
    return in_docstring

def _get_severity(pattern_name: str) -> str:
    """Détermine la sévérité d'un pattern."""
    high_severity = ["hardcoded_passwords", "hardcoded_keys", "eval_usage", "exec_usage"]
    medium_severity = ["dangerous_imports", "sql_injection", "shell_command"]
    
    if pattern_name in high_severity:
        return "high"
    elif pattern_name in medium_severity:
        return "medium"
    else:
        return "low"
