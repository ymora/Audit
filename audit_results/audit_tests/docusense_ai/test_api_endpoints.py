#!/usr/bin/env python3
"""
Test des endpoints API pour le projet docusense_ai.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any
import re

async def run_test(project_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test des endpoints API du projet docusense_ai."""
    
    results = {
        "success": False,
        "message": "",
        "details": {}
    }
    
    try:
        # Chercher les fichiers d'API
        api_files = []
        for pattern in ["*.py", "*.js", "*.ts"]:
            api_files.extend(project_path.rglob(pattern))
        
        # Filtrer les fichiers d'API
        api_patterns = [
            r"@app\.route",
            r"@api\.route",
            r"@router\.",
            r"app\.get\(",
            r"app\.post\(",
            r"app\.put\(",
            r"app\.delete\(",
            r"router\.get\(",
            r"router\.post\(",
            r"router\.put\(",
            r"router\.delete\("
        ]
        
        found_endpoints = []
        api_files_analyzed = 0
        
        for api_file in api_files[:20]:  # Limiter l'analyse
            try:
                with open(api_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    api_files_analyzed += 1
                    
                    for pattern in api_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            found_endpoints.append({
                                "file": str(api_file.relative_to(project_path)),
                                "line": line_num,
                                "pattern": pattern,
                                "match": match.group()
                            })
            except Exception:
                continue
        
        # Vérifier la documentation des API
        doc_files = []
        for doc_pattern in ["README.md", "API.md", "docs/*.md", "swagger.json", "openapi.yaml"]:
            doc_files.extend(project_path.glob(doc_pattern))
        
        # Vérifier les tests d'API
        test_files = []
        for test_pattern in ["test_*.py", "*_test.py", "tests/*.py"]:
            test_files.extend(project_path.rglob(test_pattern))
        
        # Évaluer la qualité de l'API
        score = 0
        max_score = 10
        
        if found_endpoints:
            score += 4
        if doc_files:
            score += 2
        if test_files:
            score += 3
        if (project_path / "requirements.txt").exists():
            score += 1
        
        results["success"] = score >= 4
        results["message"] = f"API évaluée: {score}/{max_score} points - {len(found_endpoints)} endpoints trouvés"
        results["details"] = {
            "score": score,
            "max_score": max_score,
            "endpoints_found": len(found_endpoints),
            "api_files_analyzed": api_files_analyzed,
            "documentation_files": [str(f.relative_to(project_path)) for f in doc_files],
            "test_files": [str(f.relative_to(project_path)) for f in test_files],
            "endpoints": found_endpoints[:10]  # Limiter l'affichage
        }
        
        return results
        
    except Exception as e:
        results["message"] = f"Erreur lors du test des API: {str(e)}"
        results["details"]["error"] = str(e)
        return results
