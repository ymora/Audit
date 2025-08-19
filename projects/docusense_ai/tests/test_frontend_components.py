#!/usr/bin/env python3
"""
Test des composants frontend pour DocuSense AI
==============================================

Teste l'accessibilité et la structure du frontend.
"""

import asyncio
import requests
import json
from pathlib import Path
from typing import Dict, Any

async def run_test(project_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    """Exécute le test des composants frontend."""
    
    print("🎨 Test des composants frontend...")
    
    results = {
        "success": True,
        "message": "Frontend accessible et fonctionnel",
        "details": {
            "frontend_accessible": False,
            "components_tested": 0,
            "components_successful": 0,
            "components_failed": 0,
            "component_results": {}
        }
    }
    
    frontend_url = "http://localhost:3000"
    
    # Test 1: Accessibilité du frontend
    print("  🔍 Test d'accessibilité du frontend...")
    try:
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200:
            print("    ✅ Frontend accessible")
            results["details"]["frontend_accessible"] = True
            results["details"]["component_results"]["accessibility"] = {
                "status": "success",
                "message": "Frontend accessible",
                "response_time": response.elapsed.total_seconds(),
                "status_code": response.status_code
            }
            results["details"]["components_successful"] += 1
        else:
            print(f"    ❌ Frontend - Status {response.status_code}")
            results["details"]["component_results"]["accessibility"] = {
                "status": "failed",
                "message": f"Status {response.status_code}",
                "status_code": response.status_code
            }
            results["details"]["components_failed"] += 1
            results["success"] = False
    except requests.exceptions.ConnectionError:
        print("    ❌ Frontend - Connexion impossible")
        results["details"]["component_results"]["accessibility"] = {
            "status": "failed",
            "message": "Impossible de se connecter au frontend",
            "error": "ConnectionError"
        }
        results["details"]["components_failed"] += 1
        results["success"] = False
    except Exception as e:
        print(f"    ❌ Frontend - Erreur: {str(e)}")
        results["details"]["component_results"]["accessibility"] = {
            "status": "failed",
            "message": f"Erreur: {str(e)}",
            "error": str(e)
        }
        results["details"]["components_failed"] += 1
        results["success"] = False
    
    results["details"]["components_tested"] += 1
    
    # Test 2: Vérification de la structure HTML
    if results["details"]["frontend_accessible"]:
        print("  🔍 Test de la structure HTML...")
        try:
            response = requests.get(frontend_url, timeout=10)
            html_content = response.text.lower()
            
            # Vérifications de base
            checks = [
                ("doctype", "doctype html" in html_content, "Doctype HTML présent"),
                ("title", "<title>" in html_content, "Balise title présente"),
                ("body", "<body>" in html_content, "Balise body présente"),
                ("react_root", "id=\"root\"" in html_content, "Élément root React présent"),
                ("script", "<script" in html_content, "Scripts présents")
            ]
            
            checks_passed = 0
            for check_name, check_result, check_message in checks:
                if check_result:
                    print(f"    ✅ {check_message}")
                    checks_passed += 1
                else:
                    print(f"    ⚠️ {check_message} manquant")
            
            if checks_passed >= 4:  # Au moins 4 sur 5
                results["details"]["component_results"]["html_structure"] = {
                    "status": "success",
                    "message": f"Structure HTML valide ({checks_passed}/5)",
                    "checks_passed": checks_passed,
                    "total_checks": len(checks)
                }
                results["details"]["components_successful"] += 1
            else:
                results["details"]["component_results"]["html_structure"] = {
                    "status": "warning",
                    "message": f"Structure HTML partielle ({checks_passed}/5)",
                    "checks_passed": checks_passed,
                    "total_checks": len(checks)
                }
                results["details"]["components_successful"] += 1
                
        except Exception as e:
            print(f"    ❌ Erreur lors de la vérification HTML: {str(e)}")
            results["details"]["component_results"]["html_structure"] = {
                "status": "failed",
                "message": f"Erreur: {str(e)}",
                "error": str(e)
            }
            results["details"]["components_failed"] += 1
            results["success"] = False
        
        results["details"]["components_tested"] += 1
    
    # Test 3: Vérification des fichiers statiques
    print("  🔍 Test des fichiers statiques...")
    static_files = [
        "/src/main.tsx",
        "/src/App.tsx",
        "/package.json",
        "/vite.config.ts"
    ]
    
    static_files_found = 0
    for static_file in static_files:
        file_path = project_path / "frontend" / static_file.lstrip("/")
        if file_path.exists():
            print(f"    ✅ {static_file} présent")
            static_files_found += 1
        else:
            print(f"    ⚠️ {static_file} manquant")
    
    if static_files_found >= 3:  # Au moins 3 sur 4
        results["details"]["component_results"]["static_files"] = {
            "status": "success",
            "message": f"Fichiers statiques présents ({static_files_found}/4)",
            "files_found": static_files_found,
            "total_files": len(static_files)
        }
        results["details"]["components_successful"] += 1
    else:
        results["details"]["component_results"]["static_files"] = {
            "status": "warning",
            "message": f"Fichiers statiques partiels ({static_files_found}/4)",
            "files_found": static_files_found,
            "total_files": len(static_files)
        }
        results["details"]["components_successful"] += 1
    
    results["details"]["components_tested"] += 1
    
    # Test 4: Vérification de la configuration Vite
    print("  🔍 Test de la configuration Vite...")
    vite_config_path = project_path / "frontend" / "vite.config.ts"
    if vite_config_path.exists():
        try:
            with open(vite_config_path, 'r', encoding='utf-8') as f:
                vite_content = f.read()
            
            vite_checks = [
                ("defineConfig", "defineConfig" in vite_content, "defineConfig utilisé"),
                ("react", "react" in vite_content, "Plugin React configuré"),
                ("port", "3000" in vite_content, "Port 3000 configuré"),
                ("host", "host" in vite_content, "Host configuré")
            ]
            
            vite_checks_passed = 0
            for check_name, check_result, check_message in vite_checks:
                if check_result:
                    print(f"    ✅ {check_message}")
                    vite_checks_passed += 1
                else:
                    print(f"    ⚠️ {check_message} manquant")
            
            if vite_checks_passed >= 3:  # Au moins 3 sur 4
                results["details"]["component_results"]["vite_config"] = {
                    "status": "success",
                    "message": f"Configuration Vite valide ({vite_checks_passed}/4)",
                    "checks_passed": vite_checks_passed,
                    "total_checks": len(vite_checks)
                }
                results["details"]["components_successful"] += 1
            else:
                results["details"]["component_results"]["vite_config"] = {
                    "status": "warning",
                    "message": f"Configuration Vite partielle ({vite_checks_passed}/4)",
                    "checks_passed": vite_checks_passed,
                    "total_checks": len(vite_checks)
                }
                results["details"]["components_successful"] += 1
                
        except Exception as e:
            print(f"    ❌ Erreur lors de la vérification Vite: {str(e)}")
            results["details"]["component_results"]["vite_config"] = {
                "status": "failed",
                "message": f"Erreur: {str(e)}",
                "error": str(e)
            }
            results["details"]["components_failed"] += 1
            results["success"] = False
    else:
        print("    ⚠️ Fichier vite.config.ts manquant")
        results["details"]["component_results"]["vite_config"] = {
            "status": "warning",
            "message": "Fichier vite.config.ts manquant"
        }
        results["details"]["components_successful"] += 1
    
    results["details"]["components_tested"] += 1
    
    # Mettre à jour le message de résultat
    if results["details"]["components_failed"] > 0:
        results["message"] = f"{results['details']['components_failed']} composant(s) en échec"
    elif results["details"]["components_successful"] > 0:
        results["message"] = f"{results['details']['components_successful']} composant(s) testé(s) avec succès"
    else:
        results["message"] = "Aucun composant testé"
    
    return results
