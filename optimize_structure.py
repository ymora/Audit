#!/usr/bin/env python3
"""
OPTIMISATION DE LA STRUCTURE - SYSTÈME D'AUDIT UNIVERSEL
=======================================================

Script pour optimiser la structure du projet audit et le rendre plus clair.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class StructureOptimizer:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        
    def analyze_current_structure(self):
        """Analyse la structure actuelle et identifie les problèmes."""
        print("🔍 Analyse de la structure actuelle...")
        
        issues = []
        
        # Vérifier le dossier .project à la racine
        root_audit_dir = self.project_dir / ".project"
        if root_audit_dir.exists():
            issues.append("⚠️ Dossier .project à la racine (devrait être dans projects/audit-universel/)")
        
        # Vérifier le dossier reports à la racine
        root_reports_dir = self.project_dir / "reports"
        if root_reports_dir.exists():
            issues.append("⚠️ Dossier reports à la racine (devrait être organisé différemment)")
        
        # Vérifier la structure des projets
        projects_dir = self.project_dir / "projects"
        if projects_dir.exists():
            for project_path in projects_dir.iterdir():
                if project_path.is_dir():
                    project_audit_dir = project_path / ".project"
                    if not project_audit_dir.exists():
                        issues.append(f"⚠️ Projet {project_path.name} n'a pas de dossier .project")
        
        if issues:
            print("   Problèmes identifiés:")
            for issue in issues:
                print(f"      {issue}")
        else:
            print("   ✅ Structure actuelle correcte")
        
        return issues
    
    def propose_optimal_structure(self):
        """Propose une structure optimale."""
        print("\n🎯 Structure optimale proposée:")
        print("""
audit-universel/
├── audit.py                    # Point d'entrée unifié
├── README.md                   # Documentation principale
├── CHANGELOG.md               # Historique des versions
├── LICENSE                    # Licence
├── requirements.txt           # Dépendances
├── .gitignore                # Fichiers à ignorer
├── core/                     # Cœur du système d'audit
│   ├── audit_gui.py          # Interface graphique
│   ├── audit.py              # Moteur d'audit
│   └── init_audit.py         # Initialisation
├── tools/                    # Outils d'analyse
│   ├── code_analyzer.py
│   ├── security_checker.py
│   └── dead_code_detector.py
├── tests/                    # Tests du système d'audit
│   ├── generic/              # Framework de tests
│   └── run_tests.py          # Lanceur de tests
├── scripts/                  # Scripts utilitaires
│   └── debug/                # Outils de debug
├── docs/                     # Documentation
│   ├── README_PROJET.md
│   ├── RESUME_FINAL.md
│   └── TESTS_ARCHITECTURE.md
├── rules/                    # Règles d'audit
│   ├── audit_rules.json
│   ├── excluded_patterns.json
│   └── quality_standards.json
└── projects/                 # Projets audités
    ├── audit-universel/      # Le projet audit lui-même
    │   ├── .project/           # Configuration d'audit
    │   ├── tests/            # Tests spécifiques
    │   ├── logs/             # Logs du projet
    │   ├── reports/          # Rapports du projet
    │   └── config.json       # Configuration
    └── docusense_ai/         # Autres projets
        ├── .project/           # Configuration d'audit
        ├── tests/            # Tests spécifiques
        ├── logs/             # Logs du projet
        ├── reports/          # Rapports du projet
        └── config.json       # Configuration
        """)
    
    def optimize_structure(self):
        """Optimise la structure actuelle."""
        print("\n🔄 Optimisation de la structure...")
        
        # 1. Déplacer le dossier .project de la racine vers projects/audit-universel/
        root_audit_dir = self.project_dir / ".project"
        target_audit_dir = self.project_dir / "projects" / "audit-universel" / ".project"
        
        if root_audit_dir.exists() and not target_audit_dir.exists():
            print("   📁 Déplacement du dossier .project de la racine vers projects/audit-universel/")
            shutil.move(str(root_audit_dir), str(target_audit_dir))
        
        # 2. Organiser les rapports à la racine
        root_reports_dir = self.project_dir / "reports"
        if root_reports_dir.exists():
            print("   📋 Organisation des rapports à la racine...")
            
            # Créer un dossier pour les rapports du système d'audit
            system_reports_dir = self.project_dir / "docs" / "reports"
            system_reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Déplacer les rapports système
            for report_file in root_reports_dir.glob("*"):
                if report_file.is_file():
                    shutil.move(str(report_file), str(system_reports_dir / report_file.name))
            
            # Supprimer le dossier reports vide
            if not any(root_reports_dir.iterdir()):
                root_reports_dir.rmdir()
                print("   ✅ Dossier reports à la racine supprimé")
        
        # 3. Vérifier que tous les projets ont leur structure .project
        projects_dir = self.project_dir / "projects"
        if projects_dir.exists():
            for project_path in projects_dir.iterdir():
                if project_path.is_dir():
                    project_audit_dir = project_path / ".project"
                    if not project_audit_dir.exists():
                        print(f"   📁 Création de .project pour {project_path.name}")
                        project_audit_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Créer les sous-dossiers
                        for subdir in ["config", "reports", "logs"]:
                            (project_audit_dir / subdir).mkdir(exist_ok=True)
    
    def verify_optimization(self):
        """Vérifie que l'optimisation s'est bien passée."""
        print("\n✅ Vérification de l'optimisation...")
        
        # Vérifier que .project n'est plus à la racine
        root_audit_dir = self.project_dir / ".project"
        if not root_audit_dir.exists():
            print("   ✅ Dossier .project supprimé de la racine")
        else:
            print("   ⚠️ Dossier .project toujours présent à la racine")
        
        # Vérifier que .project est dans projects/audit-universel/
        target_audit_dir = self.project_dir / "projects" / "audit-universel" / ".project"
        if target_audit_dir.exists():
            print("   ✅ Dossier .project présent dans projects/audit-universel/")
        else:
            print("   ⚠️ Dossier .project manquant dans projects/audit-universel/")
        
        # Vérifier que tous les projets ont leur .project
        projects_dir = self.project_dir / "projects"
        if projects_dir.exists():
            for project_path in projects_dir.iterdir():
                if project_path.is_dir():
                    project_audit_dir = project_path / ".project"
                    if project_audit_dir.exists():
                        print(f"   ✅ Projet {project_path.name} a son dossier .project")
                    else:
                        print(f"   ⚠️ Projet {project_path.name} n'a pas de dossier .project")
    
    def generate_structure_report(self):
        """Génère un rapport de la structure finale."""
        print("\n📋 Génération du rapport de structure...")
        
        report_content = f"""# RAPPORT DE STRUCTURE OPTIMISÉE
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Structure finale optimale

```
audit-universel/
├── audit.py                    # Point d'entrée unifié
├── README.md                   # Documentation principale
├── CHANGELOG.md               # Historique des versions
├── LICENSE                    # Licence
├── requirements.txt           # Dépendances
├── .gitignore                # Fichiers à ignorer
├── core/                     # Cœur du système d'audit
├── tools/                    # Outils d'analyse
├── tests/                    # Tests du système d'audit
├── scripts/                  # Scripts utilitaires
├── docs/                     # Documentation
├── rules/                    # Règles d'audit
└── projects/                 # Projets audités
    ├── audit-universel/      # Le projet audit lui-même
    │   └── .project/           # Configuration d'audit
    └── docusense_ai/         # Autres projets
        └── .project/           # Configuration d'audit
```

## Avantages de cette structure

1. **Séparation claire** : Le système d'audit et les projets audités sont séparés
2. **Organisation logique** : Chaque élément a sa place définie
3. **Extensibilité** : Facile d'ajouter de nouveaux projets
4. **Maintenabilité** : Structure prévisible et organisée
5. **Pas de confusion** : Le projet audit lui-même est traité comme les autres projets

## Utilisation

- **Point d'entrée** : `python audit.py`
- **Audit du système** : `python audit.py --cli projects/audit-universel`
- **Audit d'autres projets** : `python audit.py --cli projects/docusense_ai`
- **Tests** : `python tests/run_tests.py --all`
"""
        
        report_file = self.project_dir / "docs" / "STRUCTURE_REPORT.md"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"   📄 Rapport généré: {report_file}")

def main():
    """Fonction principale."""
    project_dir = Path(__file__).parent
    
    print("🎯 OPTIMISATION DE LA STRUCTURE - SYSTÈME D'AUDIT UNIVERSEL")
    print("=" * 60)
    print(f"📁 Répertoire: {project_dir}")
    print(f"⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    optimizer = StructureOptimizer(project_dir)
    
    # 1. Analyser la structure actuelle
    issues = optimizer.analyze_current_structure()
    
    # 2. Proposer une structure optimale
    optimizer.propose_optimal_structure()
    
    # 3. Optimiser la structure
    if issues:
        optimizer.optimize_structure()
        
        # 4. Vérifier l'optimisation
        optimizer.verify_optimization()
        
        # 5. Générer un rapport
        optimizer.generate_structure_report()
        
        print("\n🎉 OPTIMISATION TERMINÉE")
        print("=" * 60)
        print("✅ Structure optimisée avec succès!")
        print("📋 Rapport généré dans docs/STRUCTURE_REPORT.md")
    else:
        print("\n✅ Structure déjà optimale")
        print("Aucune modification nécessaire")

if __name__ == "__main__":
    main()
