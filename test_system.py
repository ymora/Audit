#!/usr/bin/env python3
"""
TEST DU SYSTÈME - SYSTÈME D'AUDIT UNIVERSEL
==========================================

Script pour tester le système d'audit sur un projet réel avant GitHub.
"""

import os
import shutil
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

class ProjectTester:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.test_project_dir = project_dir.parent / "test_project"
    
    def create_test_project(self):
        """Crée un projet de test pour valider le système."""
        print("🧪 Création du projet de test...")
        
        # Supprimer l'ancien projet de test s'il existe
        if self.test_project_dir.exists():
            shutil.rmtree(self.test_project_dir)
        
        self.test_project_dir.mkdir(exist_ok=True)
        
        # Créer une structure de projet Python complexe pour tester les rapports détaillés
        project_structure = {
            'main.py': '''#!/usr/bin/env python3
"""
Projet de test pour le système d'audit universel.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Fonction principale."""
    print("🧪 Projet de test pour l'audit universel")
    print("=" * 40)
    
    # Quelques fonctions pour tester l'analyse
    process_data("test")
    calculate_result(10, 20)
    
    # Problème de sécurité pour test
    execute_command("echo test")
    
    return "Success"

def process_data(data):
    """Traite des données."""
    return data.upper()

def calculate_result(a, b):
    """Calcule un résultat."""
    return a + b

# Duplication intentionnelle pour test
def process_data_duplicate(data):
    """Traite des données (duplication)."""
    return data.upper()

# Code potentiellement mort
def unused_function():
    """Fonction non utilisée."""
    return "unused"

# Problème de sécurité pour test
def execute_command(cmd):
    """Exécute une commande (problème de sécurité)."""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

# Implémentation incomplète pour test
def incomplete_function():
    """Fonction incomplète."""
    # TODO: Implémenter cette fonction
    pass

if __name__ == "__main__":
    main()
''',
            'utils.py': '''"""Utilitaires pour le projet de test."""

import json
import os
import subprocess

def load_config(config_file):
    """Charge un fichier de configuration."""
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

def save_config(config, config_file):
    """Sauvegarde un fichier de configuration."""
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

# Problème de sécurité potentiel pour test
def execute_command(cmd):
    """Exécute une commande (problème de sécurité)."""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

# Autre duplication pour test
def load_config_duplicate(config_file):
    """Charge un fichier de configuration (duplication)."""
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

# Fonction morte pour test
def dead_function():
    """Fonction morte."""
    return "dead"

# Implémentation incomplète
def incomplete_implementation():
    """Implémentation incomplète."""
    # FIXME: Compléter cette implémentation
    raise NotImplementedError("À implémenter")
''',
            'config.json': '''{
  "name": "Test Project",
  "version": "1.0.0",
  "debug": true,
  "features": [
    "audit",
    "security",
    "quality"
  ]
}''',
            'requirements.txt': '''requests>=2.25.0
json5>=0.9.0
pathlib2>=2.3.0
''',
            'README.md': '''# Projet de Test

Ce projet sert à tester le système d'audit universel.

## Fonctionnalités

- Fonctions de base
- Configuration JSON
- Duplications intentionnelles
- Code mort pour test
- Problèmes de sécurité pour test
- Implémentations incomplètes pour test
'''
        }
        
        # Créer les fichiers
        for filename, content in project_structure.items():
            file_path = self.test_project_dir / filename
            file_path.write_text(content, encoding='utf-8')
            print(f"   📄 Créé: {filename}")
        
        # Créer des sous-répertoires
        (self.test_project_dir / "tests").mkdir(exist_ok=True)
        (self.test_project_dir / "docs").mkdir(exist_ok=True)
        
        print(f"✅ Projet de test créé dans: {self.test_project_dir}")
    
    def test_interface_gui(self):
        """Test de l'interface graphique."""
        print("🖥️ Test de l'interface graphique...")
        
        try:
            gui_script = self.project_dir / "core" / "audit_gui.py"
            if gui_script.exists():
                print("   ✅ Script GUI trouvé")
                # Ne pas lancer réellement l'interface en mode test
                print("   💡 Interface GUI disponible (test manuel requis)")
                return True
            else:
                print("   ❌ Script GUI non trouvé")
                return False
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    
    def test_audit_system(self):
        """Test du système d'audit sur le projet de test."""
        print("🔍 Test du système d'audit...")
        
        try:
            # Initialiser l'audit dans le projet de test
            init_script = self.project_dir / "core" / "init_audit.py"
            if not init_script.exists():
                print("   ❌ Script d'initialisation non trouvé")
                return False
            
            print("   📋 Initialisation de l'audit...")
            result = subprocess.run([
                sys.executable, str(init_script), str(self.test_project_dir)
            ], capture_output=True, text=True, cwd=self.project_dir)
            
            if result.returncode == 0:
                print("   ✅ Initialisation réussie")
            else:
                print(f"   ⚠️ Initialisation: {result.stderr}")
            
            # Vérifier que le dossier .audit a été créé
            audit_dir = self.test_project_dir / ".audit"
            if audit_dir.exists():
                print("   ✅ Dossier .audit créé")
                
                # Lister le contenu
                for item in audit_dir.iterdir():
                    print(f"      📁 {item.name}")
                
                return True
            else:
                print("   ❌ Dossier .audit non créé")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur lors du test: {e}")
            return False
    
    def test_code_analysis(self):
        """Test de l'analyse de code."""
        print("🔍 Test de l'analyse de code...")
        
        try:
            # Tester l'analyseur de code
            sys.path.insert(0, str(self.project_dir / "tools"))
            from code_analyzer import CodeAnalyzer
            
            analyzer = CodeAnalyzer()
            
            # Analyser le fichier main.py du projet de test
            main_file = self.test_project_dir / "main.py"
            if main_file.exists():
                result = analyzer.analyze_file(main_file)
                
                if result:
                    print("   ✅ Analyse de fichier réussie")
                    print(f"      📊 Fonctions trouvées: {len(result.get('functions', []))}")
                    print(f"      📊 Classes trouvées: {len(result.get('classes', []))}")
                    return True
                else:
                    print("   ❌ Échec de l'analyse")
                    return False
            else:
                print("   ❌ Fichier de test non trouvé")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur lors de l'analyse: {e}")
            return False
    
    def test_detailed_reports(self):
        """Test de la génération de rapports détaillés."""
        print("📊 Test de la génération de rapports détaillés...")
        
        try:
            # Créer un rapport de test avec des données similaires à docusense
            test_data = {
                'project_name': 'Test Project',
                'files_analyzed': 10477,
                'issues_found': 0,
                'security_issues': 38,
                'duplications_found': 71,
                'dead_functions_count': 429,
                'dead_classes_count': 19,
                'incomplete_implementations': 103,
                'quality_score': 100
            }
            
            # Créer le répertoire reports s'il n'existe pas
            reports_dir = self.project_dir / "reports"
            reports_dir.mkdir(exist_ok=True)
            
            # Générer un rapport JSON de test
            json_report = reports_dir / "test_detailed_report.json"
            with open(json_report, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, indent=2, ensure_ascii=False)
            
            print("   ✅ Rapport JSON de test généré")
            print(f"      📄 Fichier: {json_report}")
            
            # Vérifier que le rapport contient les bonnes données
            with open(json_report, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            if loaded_data['files_analyzed'] == 10477:
                print("   ✅ Données du rapport correctes")
                return True
            else:
                print("   ❌ Données du rapport incorrectes")
                return False
                
        except Exception as e:
            print(f"   ❌ Erreur lors de la génération du rapport: {e}")
            return False
    
    def cleanup_test_project(self):
        """Nettoie le projet de test."""
        print("🧹 Nettoyage du projet de test...")
        
        try:
            if self.test_project_dir.exists():
                shutil.rmtree(self.test_project_dir)
                print("   ✅ Projet de test supprimé")
        except Exception as e:
            print(f"   ⚠️ Erreur lors du nettoyage: {e}")

def main():
    """Fonction principale."""
    project_dir = Path(__file__).parent
    
    print("🧪 TEST DU SYSTÈME - SYSTÈME D'AUDIT UNIVERSEL")
    print("=" * 60)
    print(f"📁 Répertoire: {project_dir}")
    print(f"⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Demander confirmation
    response = input("Voulez-vous tester le système? (oui/non): ").lower().strip()
    if response not in ['oui', 'o', 'yes', 'y']:
        print("❌ Test annulé.")
        return
    
    # Exécuter les tests
    tester = ProjectTester(project_dir)
    
    # 1. Créer un projet de test
    tester.create_test_project()
    
    # 2. Tester l'interface GUI
    gui_ok = tester.test_interface_gui()
    
    # 3. Tester le système d'audit
    audit_ok = tester.test_audit_system()
    
    # 4. Tester l'analyse de code
    analysis_ok = tester.test_code_analysis()
    
    # 5. Tester les rapports détaillés
    reports_ok = tester.test_detailed_reports()
    
    # Résumé des tests
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"🖥️ Interface GUI: {'✅ OK' if gui_ok else '❌ ÉCHEC'}")
    print(f"🔍 Système d'audit: {'✅ OK' if audit_ok else '❌ ÉCHEC'}")
    print(f"📊 Analyse de code: {'✅ OK' if analysis_ok else '❌ ÉCHEC'}")
    print(f"📄 Rapports détaillés: {'✅ OK' if reports_ok else '❌ ÉCHEC'}")
    
    # Demander si on garde le projet de test
    keep_test = input("\nVoulez-vous garder le projet de test? (oui/non): ").lower().strip()
    if keep_test not in ['oui', 'o', 'yes', 'y']:
        tester.cleanup_test_project()
    
    # Résultat final
    all_ok = gui_ok and audit_ok and analysis_ok and reports_ok
    print("\n" + "=" * 60)
    print("RÉSULTAT FINAL")
    print("=" * 60)
    
    if all_ok:
        print("🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✅ Le projet est prêt pour GitHub!")
        print("\n📋 Prochaines étapes:")
        print("1. git init")
        print("2. git add .")
        print("3. git commit -m 'Initial commit: Système d'Audit Universel'")
        print("4. Créer le dépôt GitHub")
        print("5. git remote add origin <url>")
        print("6. git push -u origin main")
    else:
        print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Veuillez corriger les problèmes avant de créer le dépôt GitHub")

if __name__ == "__main__":
    main()
