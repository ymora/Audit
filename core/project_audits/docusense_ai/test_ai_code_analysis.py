#!/usr/bin/env python3
"""
Test d'analyse de code AI pour le projet docusense_ai.
Utilise les outils existants pour analyser le code AI.
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
    from dead_code_detector import DeadCodeDetector
    from code_analyzer import CodeAnalyzer
    from incomplete_implementation_detector import IncompleteImplementationDetector
except ImportError as e:
    print(f"Erreur import outils: {e}")
    DeadCodeDetector = None
    CodeAnalyzer = None
    IncompleteImplementationDetector = None

async def run_test(project_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test d'analyse de code AI du projet docusense_ai."""
    
    results = {
        "success": False,
        "message": "",
        "details": {}
    }
    
    try:
        audit_dir = Path(__file__).parent.parent.parent
        ai_analysis_results = {}
        
        # 1. Analyse du code mort spécifique aux AI
        if DeadCodeDetector:
            print("  🤖 Analyse du code mort AI...")
            dead_code_detector = DeadCodeDetector(project_path, audit_dir)
            dead_code_report = dead_code_detector.analyze_project()
            
            # Filtrer pour les fonctions/classes AI
            ai_dead_functions = _filter_ai_functions(dead_code_report.get("dead_functions", []))
            ai_dead_classes = _filter_ai_classes(dead_code_report.get("dead_classes", []))
            
            ai_analysis_results["ai_dead_code"] = {
                "ai_dead_functions": len(ai_dead_functions),
                "ai_dead_classes": len(ai_dead_classes),
                "ai_dead_functions_list": ai_dead_functions,
                "ai_dead_classes_list": ai_dead_classes
            }
        
        # 2. Analyse des duplications dans le code AI
        if CodeAnalyzer:
            print("  🤖 Analyse des duplications AI...")
            code_analyzer = CodeAnalyzer(project_path, audit_dir)
            duplication_report = code_analyzer.analyze_project()
            
            # Filtrer pour les duplications AI
            ai_duplications = _filter_ai_duplications(duplication_report.get("duplications", []))
            
            ai_analysis_results["ai_duplications"] = {
                "ai_duplications_count": len(ai_duplications),
                "ai_duplications_list": ai_duplications
            }
        
        # 3. Détection d'implémentations incomplètes
        if IncompleteImplementationDetector:
            print("  🤖 Détection d'implémentations incomplètes...")
            incomplete_detector = IncompleteImplementationDetector(project_path, audit_dir)
            incomplete_report = incomplete_detector.analyze_project()
            
            ai_analysis_results["incomplete_implementations"] = incomplete_report
        
        # 4. Analyse spécifique aux AI
        ai_specific_analysis = _analyze_ai_specific_code(project_path)
        ai_analysis_results["ai_specific"] = ai_specific_analysis
        
        # 5. Analyse des modèles et prompts
        model_analysis = _analyze_ai_models_and_prompts(project_path)
        ai_analysis_results["models_and_prompts"] = model_analysis
        
        # 6. Évaluation globale du code AI
        ai_score = _calculate_ai_code_score(ai_analysis_results)
        
        results["success"] = ai_score >= 6  # Seuil pour le code AI
        results["message"] = f"Code AI évalué de façon exhaustive: {ai_score}/10 points"
        results["details"] = ai_analysis_results
        results["details"]["ai_code_score"] = ai_score
        
        return results
        
    except Exception as e:
        results["message"] = f"Erreur lors de l'analyse du code AI: {str(e)}"
        results["details"]["error"] = str(e)
        return results

def _filter_ai_functions(dead_functions: list) -> list:
    """Filtre les fonctions mortes liées aux AI."""
    ai_keywords = [
        "ai", "llm", "model", "prompt", "openai", "anthropic", "gpt", "claude",
        "embedding", "vector", "similarity", "completion", "chat", "assistant",
        "token", "context", "temperature", "max_tokens", "stream"
    ]
    
    ai_functions = []
    for func in dead_functions:
        func_name = func.get("name", "").lower()
        if any(keyword in func_name for keyword in ai_keywords):
            ai_functions.append(func)
    
    return ai_functions

def _filter_ai_classes(dead_classes: list) -> list:
    """Filtre les classes mortes liées aux AI."""
    ai_keywords = [
        "ai", "llm", "model", "prompt", "openai", "anthropic", "gpt", "claude",
        "embedding", "vector", "similarity", "completion", "chat", "assistant",
        "token", "context", "temperature", "max_tokens", "stream"
    ]
    
    ai_classes = []
    for cls in dead_classes:
        class_name = cls.get("name", "").lower()
        if any(keyword in class_name for keyword in ai_keywords):
            ai_classes.append(cls)
    
    return ai_classes

def _filter_ai_duplications(duplications: list) -> list:
    """Filtre les duplications liées aux AI."""
    ai_keywords = [
        "ai", "llm", "model", "prompt", "openai", "anthropic", "gpt", "claude",
        "embedding", "vector", "similarity", "completion", "chat", "assistant",
        "token", "context", "temperature", "max_tokens", "stream"
    ]
    
    ai_duplications = []
    for dup in duplications:
        func_name = dup.get("function_name", "").lower()
        if any(keyword in func_name for keyword in ai_keywords):
            ai_duplications.append(dup)
    
    return ai_duplications

def _analyze_ai_specific_code(project_path: Path) -> Dict[str, Any]:
    """Analyse spécifique du code AI."""
    analysis = {
        "ai_providers": [],
        "model_configurations": [],
        "prompt_templates": [],
        "api_calls": [],
        "error_handling": []
    }
    
    python_files = list(project_path.rglob("*.py"))
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Détecter les fournisseurs AI
                providers = re.findall(r'(openai|anthropic|huggingface|cohere|ai21)', content, re.IGNORECASE)
                analysis["ai_providers"].extend(providers)
                
                # Détecter les configurations de modèles
                model_configs = re.findall(r'(model\s*=\s*["\'][^"\']+["\']|model_name\s*=\s*["\'][^"\']+["\'])', content)
                analysis["model_configurations"].extend(model_configs)
                
                # Détecter les templates de prompts
                prompt_templates = re.findall(r'(prompt\s*=\s*["\'][^"\']+["\']|template\s*=\s*["\'][^"\']+["\'])', content)
                analysis["prompt_templates"].extend(prompt_templates)
                
                # Détecter les appels API
                api_calls = re.findall(r'(\.create\(|\.completion\(|\.chat\(|\.embedding\()', content)
                analysis["api_calls"].extend(api_calls)
                
                # Détecter la gestion d'erreurs
                error_handling = re.findall(r'(try:|except|raise|error|exception)', content, re.IGNORECASE)
                analysis["error_handling"].extend(error_handling)
                
        except Exception:
            continue
    
    # Dédupliquer les listes
    for key in analysis:
        analysis[key] = list(set(analysis[key]))
    
    return analysis

def _analyze_ai_models_and_prompts(project_path: Path) -> Dict[str, Any]:
    """Analyse des modèles et prompts AI."""
    analysis = {
        "models_used": [],
        "prompt_files": [],
        "configuration_files": [],
        "model_parameters": []
    }
    
    # Chercher les fichiers de configuration
    config_files = list(project_path.rglob("*.json")) + list(project_path.rglob("*.yaml")) + list(project_path.rglob("*.yml"))
    
    for config_file in config_files:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Détecter les modèles dans les configs
                models = re.findall(r'("model":\s*"[^"]+"|model_name:\s*[^\n]+)', content)
                analysis["models_used"].extend(models)
                
                # Détecter les paramètres de modèles
                params = re.findall(r'(temperature|max_tokens|top_p|frequency_penalty|presence_penalty)', content)
                analysis["model_parameters"].extend(params)
                
        except Exception:
            continue
    
    # Chercher les fichiers de prompts
    prompt_files = list(project_path.rglob("*prompt*")) + list(project_path.rglob("*template*"))
    analysis["prompt_files"] = [str(f.relative_to(project_path)) for f in prompt_files if f.is_file()]
    
    # Dédupliquer
    for key in analysis:
        if isinstance(analysis[key], list):
            analysis[key] = list(set(analysis[key]))
    
    return analysis

def _calculate_ai_code_score(ai_analysis_results: Dict[str, Any]) -> int:
    """Calcule un score pour le code AI."""
    score = 10
    
    # Pénaliser le code mort AI
    ai_dead_code = ai_analysis_results.get("ai_dead_code", {})
    ai_dead_functions = ai_dead_code.get("ai_dead_functions", 0)
    ai_dead_classes = ai_dead_code.get("ai_dead_classes", 0)
    
    if ai_dead_functions > 0:
        score -= min(3, ai_dead_functions)
    
    if ai_dead_classes > 0:
        score -= min(2, ai_dead_classes)
    
    # Pénaliser les duplications AI
    ai_duplications = ai_analysis_results.get("ai_duplications", {})
    ai_duplications_count = ai_duplications.get("ai_duplications_count", 0)
    
    if ai_duplications_count > 0:
        score -= min(3, ai_duplications_count)
    
    # Bonus pour les bonnes pratiques AI
    ai_specific = ai_analysis_results.get("ai_specific", {})
    error_handling = len(ai_specific.get("error_handling", []))
    
    if error_handling > 0:
        score += min(2, error_handling // 5)  # +1 point par 5 gestionnaires d'erreur
    
    # Bonus pour les configurations de modèles
    models_and_prompts = ai_analysis_results.get("models_and_prompts", {})
    models_used = len(models_and_prompts.get("models_used", []))
    
    if models_used > 0:
        score += min(2, models_used // 2)  # +1 point par 2 modèles configurés
    
    return max(0, min(10, score))
