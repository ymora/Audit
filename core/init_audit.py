#!/usr/bin/env python3
"""
INITIALISATION AUDIT - SYSTÈME D'AUDIT UNIVERSEL
================================================

Script pour initialiser le système d'audit dans un projet.
Copie la configuration et les tests spécifiques au projet.

USAGE:
    python init_audit.py [chemin_du_projet]
"""

import sys
import json
import shutil
from pathlib import Path
from typing import Optional

def detect_project_type(project_path: Path) -> str:
    """Détecte le type de projet."""
    project_files = [f.name.lower() for f in project_path.iterdir() if f.is_file()]
    
    # Détection Python/Django/Flask
    if any(f in project_files for f in ['requirements.txt', 'pyproject.toml', 'setup.py']):
        if 'manage.py' in project_files:
            return 'django'
        elif any(f.startswith('app.py') or f.startswith('main.py') for f in project_files):
            return 'flask'
        else:
            return 'python'
    
    # Détection Node.js/React/Vue
    if 'package.json' in project_files:
        if any(f in project_files for f in ['next.config.js', 'nuxt.config.js']):
            return 'nextjs' if 'next.config.js' in project_files else 'nuxtjs'
        elif any(f in project_files for f in ['vite.config.js', 'vite.config.ts']):
            return 'vite'
        else:
            return 'nodejs'
    
    # Détection Java/Maven/Gradle
    if any(f in project_files for f in ['pom.xml', 'build.gradle']):
        return 'java'
    
    # Détection PHP
    if any(f in project_files for f in ['composer.json', 'index.php']):
        return 'php'
    
    # Détection Go
    if 'go.mod' in project_files:
        return 'go'
    
    # Détection Rust
    if 'Cargo.toml' in project_files:
        return 'rust'
    
    # Par défaut
    return 'generic'

def create_default_config(project_name: str, project_type: str) -> dict:
    """Crée une configuration par défaut pour le projet."""
    configs = {
        'python': {
            'name': project_name,
            'description': f'Projet Python {project_name}',
            'type': 'python',
            'version': '1.0.0',
            'test_patterns': ['test_*.py', '*_test.py', 'tests/'],
            'ignore_patterns': ['__pycache__/', '*.pyc', 'venv/', '.venv/'],
            'quality_tools': ['pylint', 'flake8', 'black'],
            'security_tools': ['bandit', 'safety'],
            'coverage_tool': 'coverage'
        },
        'django': {
            'name': project_name,
            'description': f'Projet Django {project_name}',
            'type': 'django',
            'version': '1.0.0',
            'test_patterns': ['test_*.py', '*_test.py', 'tests/', 'test.py'],
            'ignore_patterns': ['__pycache__/', '*.pyc', 'venv/', '.venv/', 'migrations/'],
            'quality_tools': ['pylint', 'flake8', 'black'],
            'security_tools': ['bandit', 'safety', 'django-check'],
            'coverage_tool': 'coverage',
            'django_specific': True
        },
        'flask': {
            'name': project_name,
            'description': f'Projet Flask {project_name}',
            'type': 'flask',
            'version': '1.0.0',
            'test_patterns': ['test_*.py', '*_test.py', 'tests/'],
            'ignore_patterns': ['__pycache__/', '*.pyc', 'venv/', '.venv/'],
            'quality_tools': ['pylint', 'flake8', 'black'],
            'security_tools': ['bandit', 'safety'],
            'coverage_tool': 'coverage'
        },
        'nodejs': {
            'name': project_name,
            'description': f'Projet Node.js {project_name}',
            'type': 'nodejs',
            'version': '1.0.0',
            'test_patterns': ['test/', '__tests__/', '*.test.js', '*.spec.js'],
            'ignore_patterns': ['node_modules/', 'dist/', 'build/'],
            'quality_tools': ['eslint', 'prettier'],
            'security_tools': ['npm audit', 'snyk'],
            'coverage_tool': 'nyc'
        },
        'vite': {
            'name': project_name,
            'description': f'Projet Vite {project_name}',
            'type': 'vite',
            'version': '1.0.0',
            'test_patterns': ['test/', '__tests__/', '*.test.js', '*.spec.js'],
            'ignore_patterns': ['node_modules/', 'dist/', 'build/'],
            'quality_tools': ['eslint', 'prettier'],
            'security_tools': ['npm audit', 'snyk'],
            'coverage_tool': 'vitest'
        },
        'generic': {
            'name': project_name,
            'description': f'Projet générique {project_name}',
            'type': 'generic',
            'version': '1.0.0',
            'test_patterns': ['test/', 'tests/', '*test*'],
            'ignore_patterns': ['node_modules/', '__pycache__/', 'dist/', 'build/'],
            'quality_tools': [],
            'security_tools': [],
            'coverage_tool': None
        }
    }
    
    return configs.get(project_type, configs['generic'])

def init_audit_in_project(project_path: Path, audit_dir: Path) -> bool:
    """Initialise l'audit dans un projet."""
    try:
        project_name = project_path.name.lower().replace(' ', '_').replace('-', '_')
        project_type = detect_project_type(project_path)
        
        print(f"[TARGET] Initialisation de l'audit pour {project_name}")
        print(f"[FOLDER] Projet: {project_path}")
        print(f"[TAG] Type detecte: {project_type}")
        print()
        
        # Créer la structure d'audit dans le projet
        project_audit_dir = project_path / ".project"
        
        directories = [
            project_audit_dir,
            project_audit_dir / "reports",
            project_audit_dir / "logs",
            project_audit_dir / "config",
            project_audit_dir / "tests"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"[OK] Cree: {directory}")
        
        # Créer la configuration du projet
        config = create_default_config(project_name, project_type)
        config_file = project_audit_dir / "config" / "project_config.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Configuration creee: {config_file}")
        
        # Copier le template .gitignore
        gitignore_template = audit_dir / ".gitignore_template"
        gitignore_file = project_audit_dir / ".gitignore"
        
        if gitignore_template.exists():
            shutil.copy2(gitignore_template, gitignore_file)
            print(f"[OK] .gitignore cree: {gitignore_file}")
        
        # Copier les tests spécifiques au projet s'ils existent
        source_tests_dir = audit_dir / "projects" / project_name / "tests"
        target_tests_dir = project_audit_dir / "tests"
        
        if source_tests_dir.exists():
            for test_file in source_tests_dir.glob("*.py"):
                shutil.copy2(test_file, target_tests_dir / test_file.name)
                print(f"[OK] Test copie: {test_file.name}")
        
        # Créer un script d'audit local
        audit_script = project_audit_dir / "run_audit.py"
        script_content = f'''#!/usr/bin/env python3
"""
Script d'audit local pour {project_name}
========================================

Exécute l'audit spécifique à ce projet.
"""

import sys
import asyncio
from pathlib import Path

# Ajouter le répertoire audit au path
audit_dir = Path(__file__).parent.parent / "audit"
sys.path.insert(0, str(audit_dir))

from audit import UniversalAuditor

async def main():
    """Exécute l'audit du projet."""
    project_path = Path(__file__).parent.parent
    auditor = UniversalAuditor(project_path)
    await auditor.run_full_audit()

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        with open(audit_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"[OK] Script d'audit cree: {audit_script}")
        
        # Créer un README pour l'audit
        readme_file = project_audit_dir / "README.md"
        readme_content = f'''# Audit - {project_name}

Ce dossier contient la configuration et les rapports d'audit pour le projet {project_name}.

## Structure

- `config/` - Configuration d'audit du projet
- `tests/` - Tests spécifiques au projet
- `reports/` - Rapports d'audit générés
- `logs/` - Logs d'exécution des audits

## Utilisation

### Exécuter l'audit depuis le projet
```bash
python .project/run_audit.py
```

### Exécuter l'audit depuis le système central
```bash
cd audit
python audit.py
```

## Configuration

La configuration se trouve dans `config/project_config.json`.
Vous pouvez la modifier selon vos besoins.

## Rapports

Les rapports sont générés dans `reports/` :
- `latest_report.json` - Dernier rapport JSON
- `latest_report.html` - Dernier rapport HTML
- `audit_report_YYYYMMDD_HHMMSS.*` - Rapports horodatés

## Logs

Les logs d'exécution se trouvent dans `logs/audit_YYYYMMDD_HHMMSS.log`
'''
        
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"[OK] README cree: {readme_file}")
        
        print(f"\n[SUCCESS] Initialisation terminee avec succes!")
        print(f"[FOLDER] Dossier d'audit: {project_audit_dir}")
        print(f"[TOOL] Pour executer l'audit: python {audit_script}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'initialisation: {e}")
        return False

def main():
    """Fonction principale."""
    # Obtenir le chemin du projet
    if len(sys.argv) > 1:
        project_path = Path(sys.argv[1])
    else:
        # Utiliser le répertoire courant
        project_path = Path.cwd()
    
    # Vérifier que le projet existe
    if not project_path.exists():
        print(f"❌ Erreur: Le projet {project_path} n'existe pas")
        sys.exit(1)
    
    # Obtenir le chemin du dossier audit
    audit_dir = Path(__file__).parent
    
    # Initialiser l'audit
    success = init_audit_in_project(project_path, audit_dir)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
