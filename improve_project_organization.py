#!/usr/bin/env python3
"""
AMÉLIORATION DE L'ORGANISATION DES PROJETS - SYSTÈME D'AUDIT UNIVERSEL
=====================================================================

Script pour améliorer l'organisation des projets et clarifier la distinction
entre les logs/rapports du programme et ceux de l'audit.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class ProjectOrganizationImprover:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        
    def analyze_current_confusion(self):
        """Analyse la confusion actuelle dans l'organisation des projets."""
        print("🔍 Analyse de la confusion actuelle...")
        
        issues = []
        projects_dir = self.project_dir / "projects"
        
        if projects_dir.exists():
            for project_path in projects_dir.iterdir():
                if project_path.is_dir():
                    project_name = project_path.name
                    
                    # Vérifier la confusion logs
                    project_logs = project_path / "logs"
                    audit_logs = project_path / ".project" / "logs"
                    
                    if project_logs.exists() and audit_logs.exists():
                        issues.append(f"⚠️ {project_name}: Confusion entre logs du programme et logs d'audit")
                    
                    # Vérifier la confusion reports
                    project_reports = project_path / "reports"
                    audit_reports = project_path / ".project" / "reports"
                    
                    if project_reports.exists() and audit_reports.exists():
                        issues.append(f"⚠️ {project_name}: Confusion entre rapports du programme et rapports d'audit")
                    
                    # Vérifier la confusion tests
                    project_tests = project_path / "tests"
                    audit_tests = project_path / ".project" / "tests"
                    
                    if project_tests.exists() and audit_tests.exists():
                        issues.append(f"⚠️ {project_name}: Confusion entre tests du programme et tests d'audit")
        
        if issues:
            print("   Problèmes identifiés:")
            for issue in issues:
                print(f"      {issue}")
        else:
            print("   ✅ Organisation actuelle claire")
        
        return issues
    
    def propose_clear_organization(self):
        """Propose une organisation claire et simple."""
        print("\n🎯 Organisation claire proposée:")
        print("""
PROJET TYPIQUE (ex: docusense_ai)
=================================

docusense_ai/
├── config.json              # Configuration du projet
├── src/                     # Code source du projet
├── tests/                   # Tests du projet (fonctionnels, unitaires)
├── logs/                    # Logs du programme en cours d'exécution
├── reports/                 # Rapports générés par le programme
├── docs/                    # Documentation du projet
└── .project/                  # Dossier d'audit (caché)
    ├── config/              # Configuration spécifique à l'audit
    │   └── project_config.json
    ├── logs/                # Logs des sessions d'audit
    ├── reports/             # Rapports d'audit générés
    └── tests/               # Tests spécifiques à l'audit (optionnel)

AVANTAGES DE CETTE ORGANISATION:
===============================

1. 📁 SÉPARATION CLAIRE :
   - logs/ = Logs du programme en cours d'exécution
   - .project/logs/ = Logs des sessions d'audit

2. 📋 DISTINCTION ÉVIDENTE :
   - reports/ = Rapports générés par le programme
   - .project/reports/ = Rapports d'audit

3. 🧪 TESTS ORGANISÉS :
   - tests/ = Tests du projet (fonctionnels, unitaires)
   - .project/tests/ = Tests spécifiques à l'audit (optionnel)

4. 🎯 SIMPLICITÉ :
   - Structure prévisible
   - Pas de confusion possible
   - Facile à comprendre
        """)
    
    def reorganize_projects(self):
        """Réorganise les projets pour clarifier la structure."""
        print("\n🔄 Réorganisation des projets...")
        
        projects_dir = self.project_dir / "projects"
        
        if projects_dir.exists():
            for project_path in projects_dir.iterdir():
                if project_path.is_dir():
                    project_name = project_path.name
                    print(f"   📁 Réorganisation de {project_name}...")
                    
                    # 1. Clarifier les logs
                    self._clarify_logs(project_path, project_name)
                    
                    # 2. Clarifier les rapports
                    self._clarify_reports(project_path, project_name)
                    
                    # 3. Clarifier les tests
                    self._clarify_tests(project_path, project_name)
                    
                    # 4. Créer la structure claire
                    self._create_clear_structure(project_path, project_name)
    
    def _clarify_logs(self, project_path: Path, project_name: str):
        """Clarifie l'organisation des logs."""
        project_logs = project_path / "logs"
        audit_logs = project_path / ".project" / "logs"
        
        if project_logs.exists() and audit_logs.exists():
            print(f"      📝 Clarification des logs pour {project_name}")
            
            # Créer un dossier temporaire pour trier
            temp_logs = project_path / "temp_logs"
            temp_logs.mkdir(exist_ok=True)
            
            # Déplacer tous les logs dans le temporaire
            for log_file in project_logs.glob("*"):
                if log_file.is_file():
                    shutil.move(str(log_file), str(temp_logs / log_file.name))
            
            for log_file in audit_logs.glob("*"):
                if log_file.is_file():
                    shutil.move(str(log_file), str(temp_logs / log_file.name))
            
            # Supprimer les dossiers vides
            if not any(project_logs.iterdir()):
                project_logs.rmdir()
            if not any(audit_logs.iterdir()):
                audit_logs.rmdir()
            
            # Recréer les dossiers
            project_logs.mkdir(exist_ok=True)
            audit_logs.mkdir(parents=True, exist_ok=True)
            
            # Trier les logs par nom de fichier
            for log_file in temp_logs.glob("*"):
                if log_file.is_file():
                    filename = log_file.name.lower()
                    
                    # Logs d'audit contiennent "audit" dans le nom
                    if "audit" in filename or "session" in filename:
                        shutil.move(str(log_file), str(audit_logs / log_file.name))
                    else:
                        # Logs du programme
                        shutil.move(str(log_file), str(project_logs / log_file.name))
            
            # Supprimer le dossier temporaire
            if temp_logs.exists():
                temp_logs.rmdir()
    
    def _clarify_reports(self, project_path: Path, project_name: str):
        """Clarifie l'organisation des rapports."""
        project_reports = project_path / "reports"
        audit_reports = project_path / ".project" / "reports"
        
        if project_reports.exists() and audit_reports.exists():
            print(f"      📋 Clarification des rapports pour {project_name}")
            
            # Créer un dossier temporaire pour trier
            temp_reports = project_path / "temp_reports"
            temp_reports.mkdir(exist_ok=True)
            
            # Déplacer tous les rapports dans le temporaire
            for report_file in project_reports.glob("*"):
                if report_file.is_file():
                    shutil.move(str(report_file), str(temp_reports / report_file.name))
            
            for report_file in audit_reports.glob("*"):
                if report_file.is_file():
                    shutil.move(str(report_file), str(temp_reports / report_file.name))
            
            # Supprimer les dossiers vides
            if not any(project_reports.iterdir()):
                project_reports.rmdir()
            if not any(audit_reports.iterdir()):
                audit_reports.rmdir()
            
            # Recréer les dossiers
            project_reports.mkdir(exist_ok=True)
            audit_reports.mkdir(parents=True, exist_ok=True)
            
            # Trier les rapports par nom de fichier
            for report_file in temp_reports.glob("*"):
                if report_file.is_file():
                    filename = report_file.name.lower()
                    
                    # Rapports d'audit contiennent "audit" dans le nom
                    if "audit" in filename or "report" in filename:
                        shutil.move(str(report_file), str(audit_reports / report_file.name))
                    else:
                        # Rapports du programme
                        shutil.move(str(report_file), str(project_reports / report_file.name))
            
            # Supprimer le dossier temporaire
            if temp_reports.exists():
                temp_reports.rmdir()
    
    def _clarify_tests(self, project_path: Path, project_name: str):
        """Clarifie l'organisation des tests."""
        project_tests = project_path / "tests"
        audit_tests = project_path / ".project" / "tests"
        
        if project_tests.exists() and audit_tests.exists():
            print(f"      🧪 Clarification des tests pour {project_name}")
            
            # Créer un dossier temporaire pour trier
            temp_tests = project_path / "temp_tests"
            temp_tests.mkdir(exist_ok=True)
            
            # Déplacer tous les tests dans le temporaire
            for test_file in project_tests.glob("*"):
                if test_file.is_file():
                    shutil.move(str(test_file), str(temp_tests / test_file.name))
            
            for test_file in audit_tests.glob("*"):
                if test_file.is_file():
                    shutil.move(str(test_file), str(temp_tests / test_file.name))
            
            # Supprimer les dossiers vides
            if not any(project_tests.iterdir()):
                project_tests.rmdir()
            if not any(audit_tests.iterdir()):
                audit_tests.rmdir()
            
            # Recréer les dossiers
            project_tests.mkdir(exist_ok=True)
            audit_tests.mkdir(parents=True, exist_ok=True)
            
            # Trier les tests par nom de fichier
            for test_file in temp_tests.glob("*"):
                if test_file.is_file():
                    filename = test_file.name.lower()
                    
                    # Tests d'audit contiennent "audit" dans le nom
                    if "audit" in filename or "security" in filename:
                        shutil.move(str(test_file), str(audit_tests / test_file.name))
                    else:
                        # Tests du programme
                        shutil.move(str(test_file), str(project_tests / test_file.name))
            
            # Supprimer le dossier temporaire
            if temp_tests.exists():
                temp_tests.rmdir()
    
    def _create_clear_structure(self, project_path: Path, project_name: str):
        """Crée une structure claire avec des fichiers README explicatifs."""
        print(f"      📄 Création de la documentation pour {project_name}")
        
        # Créer README pour les logs du programme
        project_logs = project_path / "logs"
        if project_logs.exists():
            logs_readme = project_logs / "README.md"
            logs_content = f"""# Logs du Programme - {project_name}

Ce dossier contient les logs générés par le programme {project_name} en cours d'exécution.

## Contenu typique :
- Logs d'application
- Logs d'erreurs
- Logs de performance
- Logs de débogage

## Utilisation :
Ces logs sont générés automatiquement par le programme lors de son exécution.
"""
            with open(logs_readme, 'w', encoding='utf-8') as f:
                f.write(logs_content)
        
        # Créer README pour les rapports du programme
        project_reports = project_path / "reports"
        if project_reports.exists():
            reports_readme = project_reports / "README.md"
            reports_content = f"""# Rapports du Programme - {project_name}

Ce dossier contient les rapports générés par le programme {project_name}.

## Contenu typique :
- Rapports de performance
- Rapports d'utilisation
- Rapports d'erreurs
- Statistiques du programme

## Utilisation :
Ces rapports sont générés par le programme lui-même, pas par l'audit.
"""
            with open(reports_readme, 'w', encoding='utf-8') as f:
                f.write(reports_content)
        
        # Créer README pour les tests du programme
        project_tests = project_path / "tests"
        if project_tests.exists():
            tests_readme = project_tests / "README.md"
            tests_content = f"""# Tests du Programme - {project_name}

Ce dossier contient les tests du programme {project_name}.

## Contenu typique :
- Tests unitaires
- Tests d'intégration
- Tests fonctionnels
- Tests de performance

## Utilisation :
Ces tests vérifient le bon fonctionnement du programme.
"""
            with open(tests_readme, 'w', encoding='utf-8') as f:
                f.write(tests_content)
        
        # Créer README pour le dossier .project
        audit_dir = project_path / ".project"
        if audit_dir.exists():
            audit_readme = audit_dir / "README.md"
            audit_content = f"""# Dossier d'Audit - {project_name}

Ce dossier contient tous les éléments spécifiques à l'audit du projet {project_name}.

## Structure :
- `config/` : Configuration spécifique à l'audit
- `logs/` : Logs des sessions d'audit
- `reports/` : Rapports d'audit générés
- `tests/` : Tests spécifiques à l'audit (optionnel)

## Distinction importante :
- Les logs/rapports du PROGRAMME sont dans les dossiers à la racine
- Les logs/rapports d'AUDIT sont dans ce dossier .project/

## Utilisation :
Ce dossier est géré automatiquement par le système d'audit.
"""
            with open(audit_readme, 'w', encoding='utf-8') as f:
                f.write(audit_content)
    
    def verify_improvement(self):
        """Vérifie que l'amélioration s'est bien passée."""
        print("\n✅ Vérification de l'amélioration...")
        
        projects_dir = self.project_dir / "projects"
        
        if projects_dir.exists():
            for project_path in projects_dir.iterdir():
                if project_path.is_dir():
                    project_name = project_path.name
                    
                    # Vérifier la structure claire
                    project_logs = project_path / "logs"
                    audit_logs = project_path / ".project" / "logs"
                    project_reports = project_path / "reports"
                    audit_reports = project_path / ".project" / "reports"
                    
                    if project_logs.exists() and audit_logs.exists():
                        print(f"   ✅ {project_name}: Logs séparés (programme vs audit)")
                    
                    if project_reports.exists() and audit_reports.exists():
                        print(f"   ✅ {project_name}: Rapports séparés (programme vs audit)")
                    
                    # Vérifier les README
                    if (project_logs / "README.md").exists():
                        print(f"   ✅ {project_name}: Documentation des logs créée")
                    
                    if (project_reports / "README.md").exists():
                        print(f"   ✅ {project_name}: Documentation des rapports créée")
    
    def generate_organization_guide(self):
        """Génère un guide d'organisation pour les projets."""
        print("\n📋 Génération du guide d'organisation...")
        
        guide_content = f"""# GUIDE D'ORGANISATION DES PROJETS
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Structure claire recommandée pour chaque projet

```
projet_exemple/
├── config.json              # Configuration du projet
├── src/                     # Code source du projet
├── tests/                   # Tests du projet (fonctionnels, unitaires)
│   └── README.md           # Documentation des tests
├── logs/                    # Logs du programme en cours d'exécution
│   └── README.md           # Documentation des logs
├── reports/                 # Rapports générés par le programme
│   └── README.md           # Documentation des rapports
├── docs/                    # Documentation du projet
└── .project/                  # Dossier d'audit (caché)
    ├── README.md           # Documentation de l'audit
    ├── config/              # Configuration spécifique à l'audit
    ├── logs/                # Logs des sessions d'audit
    ├── reports/             # Rapports d'audit générés
    └── tests/               # Tests spécifiques à l'audit (optionnel)
```

## Distinctions importantes

### 📝 Logs
- **logs/** : Logs du programme en cours d'exécution
- **.project/logs/** : Logs des sessions d'audit

### 📋 Rapports
- **reports/** : Rapports générés par le programme
- **.project/reports/** : Rapports d'audit générés

### 🧪 Tests
- **tests/** : Tests du projet (fonctionnels, unitaires)
- **.project/tests/** : Tests spécifiques à l'audit (optionnel)

## Avantages

1. **Clarté** : Pas de confusion possible
2. **Simplicité** : Structure prévisible
3. **Documentation** : README explicatifs dans chaque dossier
4. **Séparation** : Programme et audit bien distincts
5. **Maintenabilité** : Organisation logique et cohérente

## Utilisation

- **Développement** : Utiliser les dossiers à la racine
- **Audit** : Utiliser le dossier .project/
- **Documentation** : Consulter les README.md dans chaque dossier
"""
        
        guide_file = self.project_dir / "docs" / "PROJECT_ORGANIZATION_GUIDE.md"
        guide_file.parent.mkdir(exist_ok=True)
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"   📄 Guide généré: {guide_file}")

def main():
    """Fonction principale."""
    project_dir = Path(__file__).parent
    
    print("🎯 AMÉLIORATION DE L'ORGANISATION DES PROJETS")
    print("=" * 60)
    print(f"📁 Répertoire: {project_dir}")
    print(f"⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    improver = ProjectOrganizationImprover(project_dir)
    
    # 1. Analyser la confusion actuelle
    issues = improver.analyze_current_confusion()
    
    # 2. Proposer une organisation claire
    improver.propose_clear_organization()
    
    # 3. Réorganiser les projets
    if issues:
        improver.reorganize_projects()
        
        # 4. Vérifier l'amélioration
        improver.verify_improvement()
        
        # 5. Générer un guide
        improver.generate_organization_guide()
        
        print("\n🎉 AMÉLIORATION TERMINÉE")
        print("=" * 60)
        print("✅ Organisation des projets améliorée!")
        print("📋 Guide généré dans docs/PROJECT_ORGANIZATION_GUIDE.md")
    else:
        print("\n✅ Organisation déjà claire")
        print("Aucune amélioration nécessaire")

if __name__ == "__main__":
    main()
