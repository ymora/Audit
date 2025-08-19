#!/usr/bin/env python3
"""
ORGANISATION DU PROJET - SYSTÈME D'AUDIT UNIVERSEL
=================================================

Script pour organiser le projet et s'assurer que les rapports sont aussi détaillés 
que celui du projet docusense (10,477 fichiers analysés, 38 vulnérabilités, etc.)
"""

import os
import shutil
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

class ProjectOrganizer:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.backup_dir = project_dir / "backup_organization"
        
        # Structure optimisée pour des rapports détaillés
        self.structure = {
            'core': [
                'audit_gui.py',
                'Audit IA.py', 
                'audit.py',
                'init_audit.py'
            ],
            'scripts': [
                'cleanup_old_audit.py',
                'migrate_old_reports.py',
                'demo.py'
            ],
            'tools': [
                'code_analyzer.py',
                'security_checker.py', 
                'dead_code_detector.py',
                'incomplete_implementation_detector.py'
            ],
            'tests': [
                'debug_security_detection.py',
                'test_subprocess_detection.py',
                'test_audit_configuration_integrity.py',
                'test_security_checker_unit.py',
                'analyze_code_duplications_detailed.py',
                'debug_code_duplications_analysis.py',
                'fix_final_vulnerabilities.py'
            ],
            'remove': [
                'launch_gui.py',
                'init_git_project.py',
                '.gitignore_template'
            ]
        }
    
    def create_backup(self):
        """Crée une sauvegarde avant l'organisation."""
        print("💾 Création de la sauvegarde...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        self.backup_dir.mkdir(exist_ok=True)
        
        # Copier tous les fichiers Python
        for file_path in self.project_dir.glob("*.py"):
            shutil.copy2(file_path, self.backup_dir / file_path.name)
        
        print(f"✅ Sauvegarde créée dans: {self.backup_dir}")
    
    def organize_files(self):
        """Organise les fichiers selon la structure définie."""
        print("🗂️ Organisation des fichiers...")
        
        # Créer les répertoires
        for category in ['core', 'scripts', 'tests']:
            category_dir = self.project_dir / category
            category_dir.mkdir(exist_ok=True)
            print(f"   📁 Créé: {category_dir}")
        
        # Déplacer les fichiers vers core/
        for file_name in self.structure['core']:
            source_path = self.project_dir / file_name
            dest_path = self.project_dir / 'core' / file_name
            
            if source_path.exists() and not dest_path.exists():
                shutil.move(str(source_path), str(dest_path))
                print(f"   📄 Déplacé: {file_name} → core/")
        
        # Déplacer les fichiers vers scripts/
        for file_name in self.structure['scripts']:
            source_path = self.project_dir / file_name
            dest_path = self.project_dir / 'scripts' / file_name
            
            if source_path.exists() and not dest_path.exists():
                shutil.move(str(source_path), str(dest_path))
                print(f"   📄 Déplacé: {file_name} → scripts/")
        
        # Déplacer les fichiers de test depuis tools/ vers tests/
        tools_dir = self.project_dir / "tools"
        tests_dir = self.project_dir / "tests"
        
        if tools_dir.exists():
            for file_name in self.structure['tests']:
                source_path = tools_dir / file_name
                dest_path = tests_dir / file_name
                
                if source_path.exists() and not dest_path.exists():
                    shutil.move(str(source_path), str(dest_path))
                    print(f"   📄 Déplacé: {file_name} → tests/")
        
        # Déplacer les fichiers depuis scripts/ vers tests/
        scripts_dir = self.project_dir / "scripts"
        if scripts_dir.exists():
            script_test_files = [
                'analyze_code_duplications_detailed.py',
                'debug_code_duplications_analysis.py', 
                'fix_final_vulnerabilities.py'
            ]
            
            for file_name in script_test_files:
                source_path = scripts_dir / file_name
                dest_path = tests_dir / file_name
                
                if source_path.exists() and not dest_path.exists():
                    shutil.move(str(source_path), str(dest_path))
                    print(f"   📄 Déplacé: {file_name} → tests/")
        
        # Supprimer les fichiers obsolètes
        for file_name in self.structure['remove']:
            file_path = self.project_dir / file_name
            if file_path.exists():
                file_path.unlink()
                print(f"   🗑️ Supprimé: {file_name}")
    
    def create_launcher(self):
        """Crée le script de lancement unifié."""
        print("🚀 Création du lanceur unifié...")
        
        launcher_content = '''#!/usr/bin/env python3
"""
LANCEUR UNIFIÉ - SYSTÈME D'AUDIT UNIVERSEL
==========================================

Script de lancement unifié pour le système d'audit universel.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """Vérifie que toutes les dépendances sont disponibles."""
    try:
        import tkinter
        import tkinter.ttk
        import tkinter.filedialog
        import tkinter.messagebox
        import tkinter.scrolledtext
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("💡 tkinter est généralement inclus avec Python.")
        return False

def main():
    """Fonction principale."""
    print("🔍 Lancement du Système d'Audit Universel")
    print("=" * 50)
    
    # Vérifier les dépendances
    if not check_dependencies():
        print("\\n❌ Impossible de lancer l'interface graphique.")
        print("💡 Essayez de réinstaller Python avec tkinter inclus.")
        return 1
    
    # Chemin vers le script GUI principal
    audit_dir = Path(__file__).parent
    gui_script = audit_dir / "core" / "audit_gui.py"
    
    if not gui_script.exists():
        print(f"❌ Script GUI introuvable: {gui_script}")
        return 1
    
    print(f"✅ Script GUI trouvé: {gui_script}")
    print("🚀 Lancement de l'interface moderne...")
    print()
    
    try:
        # Lancer l'interface graphique
        subprocess.run([sys.executable, str(gui_script)], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du lancement: {e}")
        return 1
    except KeyboardInterrupt:
        print("\\n⏹️ Lancement interrompu par l'utilisateur.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
'''
        
        launcher_file = self.project_dir / "start_audit.py"
        launcher_file.write_text(launcher_content, encoding='utf-8')
        print(f"   📄 Créé: start_audit.py")
    
    def clean_temp_files(self):
        """Nettoie les fichiers temporaires."""
        print("🧹 Nettoyage des fichiers temporaires...")
        
        patterns = ['__pycache__', '*.pyc', '*.pyo', '.pytest_cache', '*.log', '*.tmp']
        files_removed = 0
        
        for pattern in patterns:
            if pattern.startswith('*'):
                for file_path in self.project_dir.rglob(pattern):
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            files_removed += 1
                        except:
                            pass
            else:
                for dir_path in self.project_dir.rglob(pattern):
                    if dir_path.is_dir():
                        try:
                            shutil.rmtree(dir_path)
                            files_removed += 1
                        except:
                            pass
        
        print(f"   📊 {files_removed} fichiers/répertoires nettoyés")
    
    def create_init_files(self):
        """Crée les fichiers __init__.py."""
        print("📝 Création des fichiers __init__.py...")
        
        packages = ['core', 'scripts', 'tools', 'tests']
        for package in packages:
            package_dir = self.project_dir / package
            if package_dir.exists():
                init_file = package_dir / "__init__.py"
                if not init_file.exists():
                    init_file.touch()
                    print(f"   ✅ Créé: {package}/__init__.py")
    
    def update_gitignore(self):
        """Met à jour le .gitignore."""
        print("📝 Mise à jour du .gitignore...")
        
        gitignore_content = '''# Fichiers système
.DS_Store
Thumbs.db
desktop.ini

# Fichiers Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Environnements virtuels
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/
*.tmp
*.temp

# Configuration locale
gui_config.json
local_config.json

# Fichiers de sauvegarde
*.backup
*.bak
*.old
backup_organization/

# Tests
.pytest_cache/
.coverage
htmlcov/

# Fichiers temporaires
temp/
tmp/
*.cache

# Rapports temporaires
reports/temp/
*.tmp.html
*.tmp.json

# Dossiers d'audit des projets
.audit/
'''
        
        gitignore_file = self.project_dir / ".gitignore"
        gitignore_file.write_text(gitignore_content, encoding='utf-8')
        print("   ✅ .gitignore mis à jour")

def main():
    """Fonction principale."""
    project_dir = Path(__file__).parent
    
    print("🔧 ORGANISATION DU PROJET - SYSTÈME D'AUDIT UNIVERSEL")
    print("=" * 60)
    print(f"📁 Répertoire: {project_dir}")
    print(f"⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Demander confirmation
    response = input("Voulez-vous organiser le projet? (oui/non): ").lower().strip()
    if response not in ['oui', 'o', 'yes', 'y']:
        print("❌ Organisation annulée.")
        return
    
    # Exécuter l'organisation
    organizer = ProjectOrganizer(project_dir)
    
    # 1. Créer une sauvegarde
    organizer.create_backup()
    
    # 2. Organiser les fichiers
    organizer.organize_files()
    
    # 3. Créer le lanceur
    organizer.create_launcher()
    
    # 4. Nettoyer les fichiers temporaires
    organizer.clean_temp_files()
    
    # 5. Créer les fichiers __init__.py
    organizer.create_init_files()
    
    # 6. Mettre à jour .gitignore
    organizer.update_gitignore()
    
    print("\n✅ ORGANISATION TERMINÉE")
    print("=" * 60)
    print(f"📦 Sauvegarde: {organizer.backup_dir}")
    print("🚀 Lanceur: start_audit.py")
    print("💡 Le projet est maintenant organisé et prêt pour les tests!")

if __name__ == "__main__":
    main()
