#!/usr/bin/env python3
"""
TEST CONFIGURATION AUDIT - DOCUSENSE AI
======================================

Script de test pour vérifier l'intégrité de la configuration du système d'audit.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def test_structure():
    """Test de la structure des dossiers"""
    print("🔍 Test de la structure...")
    
    required_dirs = [
        "rules",
        "reports/latest", 
        "reports/archive",
        "logs/current",
        "logs/archive",
        "tools",
        "scripts"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
        else:
            print(f"  ✅ {dir_path}")
    
    if missing_dirs:
        print(f"  ❌ Dossiers manquants: {missing_dirs}")
        return False
    
    return True

def test_configuration_files():
    """Test des fichiers de configuration"""
    print("\n🔍 Test des fichiers de configuration...")
    
    config_files = [
        "rules/audit_rules.json",
        "rules/excluded_patterns.json", 
        "rules/quality_standards.json"
    ]
    
    missing_files = []
    for file_path in config_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"  ❌ Fichiers manquants: {missing_files}")
        return False
    
    return True

def test_scripts_directory():
    """Test du répertoire scripts"""
    print("\n🔍 Test du répertoire scripts...")
    
    scripts_dir = "scripts"
    if not Path(scripts_dir).exists():
        print(f"  ❌ {scripts_dir} manquant")
        return False
    
    scripts_files = list(Path(scripts_dir).glob("*.py"))
    if len(scripts_files) == 0:
        print(f"  ⚠️ {scripts_dir} vide")
        return False
    
    print(f"  ✅ {scripts_dir} avec {len(scripts_files)} scripts")
    return True

def test_analysis_tools():
    """Test des outils d'analyse"""
    print("\n🔍 Test des outils d'analyse...")
    
    tools = [
    "tools/code_analyzer.py",
    "tools/security_checker.py"
]
    
    missing_tools = []
    for tool in tools:
        if not Path(tool).exists():
            missing_tools.append(tool)
        else:
            print(f"  ✅ {tool}")
    
    if missing_tools:
        print(f"  ❌ Outils manquants: {missing_tools}")
        return False
    
    return True

def test_main_audit_script():
    """Test du script principal d'audit"""
    print("\n🔍 Test du script principal d'audit...")
    
    main_script = "Audit IA.py"
    if not Path(main_script).exists():
        print(f"  ❌ {main_script} manquant")
        return False
    
    print(f"  ✅ {main_script}")
    return True

def test_organization_rules():
    """Test des règles d'organisation"""
    print("\n🔍 Test des règles d'organisation...")
    
    # Vérifier qu'il n'y a pas de fichiers orphelins dans tools/
    tools_dir = Path("tools")
    if tools_dir.exists():
        files = list(tools_dir.glob("*.py"))
        if len(files) > 4:  # Plus que les 4 fichiers essentiels
            print(f"  ⚠️ {len(files)} fichiers dans tools/ (peut-être des fichiers obsolètes)")
        else:
            print(f"  ✅ {len(files)} fichiers dans tools/")
    
    return True

def generate_test_report(results):
    """Génère un rapport de test"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Créer le répertoire reports/latest s'il n'existe pas
    reports_dir = Path("reports/latest")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = reports_dir / f"{timestamp}_test_system.json"
    
    report = {
        "timestamp": timestamp,
        "tests": results,
        "overall_status": "PASS" if all(results.values()) else "FAIL",
        "recommendations": []
    }
    
    if not results["structure"]:
        report["recommendations"].append("Créer la structure de dossiers manquante")
    
    if not results["configuration"]:
        report["recommendations"].append("Créer les fichiers de configuration manquants")
    
    if not results["scripts"]:
        report["recommendations"].append("Créer le répertoire scripts")
    
    if not results["tools"]:
        report["recommendations"].append("Créer les outils d'analyse")
    
    if not results["main_script"]:
        report["recommendations"].append("Créer le script principal d'audit")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report_file

def main():
    """Fonction principale de test"""
    print("🚀 TEST DE LA CONFIGURATION D'AUDIT")
    print("=" * 50)
    
    results = {
        "structure": test_structure(),
        "configuration": test_configuration_files(),
        "scripts": test_scripts_directory(),
        "tools": test_analysis_tools(),
        "main_script": test_main_audit_script(),
        "organization": test_organization_rules()
    }
    
    # Résumé
    print("\n📊 RÉSUMÉ DES TESTS:")
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés! Le système d'audit est prêt.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les recommandations.")
    
    # Générer le rapport
    report_file = generate_test_report(results)
    print(f"\n📋 Rapport généré: {report_file}")
    
    # Code de sortie pour CI/CD
    if passed < total:
        print(f"\n❌ {total - passed} test(s) échoué(s) - Sortie avec code d'erreur")
        sys.exit(1)
    else:
        print(f"\n✅ Tous les tests réussis - Sortie avec succès")
        sys.exit(0)

if __name__ == "__main__":
    main()
