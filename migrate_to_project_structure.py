#!/usr/bin/env python3
"""
MIGRATION VERS .PROJECT - SYSTÈME D'AUDIT UNIVERSEL
==================================================

Script pour migrer de .project vers .project pour une structure plus claire.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class ProjectMigrationManager:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        
    def analyze_migration_needs(self):
        """Analyse les besoins de migration."""
        print("🔍 Analyse des besoins de migration...")
        
        migration_targets = []
        projects_dir = self.project_dir / "projects"
        
        if projects_dir.exists():
            for project_path in projects_dir.iterdir():
                if project_path.is_dir():
                    project_name = project_path.name
                    audit_dir = project_path / ".project"
                    
                    if audit_dir.exists():
                        migration_targets.append({
                            'project_name': project_name,
                            'project_path': project_path,
                            'audit_dir': audit_dir,
                            'project_dir': project_path / ".project"
                        })
                        print(f"   📁 {project_name}: Migration .project → .project nécessaire")
        
        if not migration_targets:
            print("   ✅ Aucune migration nécessaire")
        
        return migration_targets
    
    def backup_existing_structure(self, migration_targets):
        """Sauvegarde la structure existante."""
        print("\n💾 Sauvegarde de la structure existante...")
        
        backup_dir = self.project_dir / "backup_migration"
        backup_dir.mkdir(exist_ok=True)
        
        for target in migration_targets:
            project_name = target['project_name']
            audit_dir = target['audit_dir']
            
            if audit_dir.exists():
                backup_path = backup_dir / f"{project_name}_audit_backup"
                print(f"   📦 Sauvegarde de {project_name}/.project vers {backup_path}")
                shutil.copytree(audit_dir, backup_path, dirs_exist_ok=True)
        
        print(f"   ✅ Sauvegarde créée dans: {backup_dir}")
        return backup_dir
    
    def migrate_to_project_structure(self, migration_targets):
        """Migre de .project vers .project."""
        print("\n🔄 Migration vers la structure .project...")
        
        for target in migration_targets:
            project_name = target['project_name']
            audit_dir = target['audit_dir']
            project_dir = target['project_dir']
            
            print(f"   📁 Migration de {project_name}...")
            
            if audit_dir.exists():
                # Renommer .project en .project
                print(f"      🔄 Renommage .project → .project")
                shutil.move(str(audit_dir), str(project_dir))
                
                # Mettre à jour les README
                self._update_project_readme(project_dir, project_name)
                
                # Créer la structure claire
                self._create_clear_project_structure(project_dir, project_name)
                
                print(f"      ✅ Migration terminée pour {project_name}")
    
    def _update_project_readme(self, project_dir: Path, project_name: str):
        """Met à jour le README du dossier .project."""
        readme_file = project_dir / "README.md"
        
        readme_content = f"""# Dossier du Projet - {project_name}

Ce dossier contient tous les éléments spécifiques au projet {project_name}.

## Structure :
- `config/` : Configuration du projet
- `logs/` : Logs du projet (historique, sessions, etc.)
- `reports/` : Rapports du projet (analyses, métriques, etc.)
- `tests/` : Tests du projet (intégration, performance, etc.)

## Distinction importante :
- Les logs/rapports du PROGRAMME sont dans les dossiers à la racine
- Les logs/rapports du PROJET sont dans ce dossier .project/

## Utilisation :
Ce dossier est géré automatiquement par le système d'audit.
"""
        
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"      📄 README mis à jour pour {project_name}")
    
    def _create_clear_project_structure(self, project_dir: Path, project_name: str):
        """Crée une structure claire dans le dossier .project."""
        # Créer les sous-dossiers s'ils n'existent pas
        for subdir in ["config", "logs", "reports", "tests"]:
            subdir_path = project_dir / subdir
            subdir_path.mkdir(exist_ok=True)
            
            # Créer un README pour chaque sous-dossier
            readme_file = subdir_path / "README.md"
            
            if subdir == "config":
                content = f"""# Configuration du Projet - {project_name}

Ce dossier contient la configuration spécifique au projet {project_name}.

## Contenu typique :
- project_config.json
- Paramètres spécifiques
- Configuration d'environnement
"""
            elif subdir == "logs":
                content = f"""# Logs du Projet - {project_name}

Ce dossier contient les logs du projet {project_name}.

## Contenu typique :
- Logs d'historique
- Logs de sessions
- Logs d'analyses
- Logs de métriques
"""
            elif subdir == "reports":
                content = f"""# Rapports du Projet - {project_name}

Ce dossier contient les rapports du projet {project_name}.

## Contenu typique :
- Rapports d'analyses
- Rapports de métriques
- Rapports de performance
- Rapports d'historique
"""
            elif subdir == "tests":
                content = f"""# Tests du Projet - {project_name}

Ce dossier contient les tests spécifiques au projet {project_name}.

## Contenu typique :
- Tests d'intégration
- Tests de performance
- Tests spécifiques au projet
- Tests d'analyse
"""
            
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def update_system_configuration(self):
        """Met à jour la configuration du système pour utiliser .project."""
        print("\n⚙️ Mise à jour de la configuration du système...")
        
        # Mettre à jour les scripts qui référencent .project
        self._update_audit_scripts()
        
        # Mettre à jour la documentation
        self._update_documentation()
        
        print("   ✅ Configuration du système mise à jour")
    
    def _update_audit_scripts(self):
        """Met à jour les scripts qui référencent .project."""
        print("      🔧 Mise à jour des scripts...")
        
        # Chercher les fichiers qui contiennent ".project"
        for file_path in self.project_dir.rglob("*.py"):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if ".project" in content:
                        # Remplacer .project par .project
                        new_content = content.replace(".project", ".project")
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        print(f"         📝 Mis à jour: {file_path.relative_to(self.project_dir)}")
                except Exception as e:
                    print(f"         ⚠️ Erreur lors de la mise à jour de {file_path}: {e}")
    
    def _update_documentation(self):
        """Met à jour la documentation."""
        print("      📄 Mise à jour de la documentation...")
        
        # Mettre à jour le README principal
        readme_file = self.project_dir / "README.md"
        if readme_file.exists():
            try:
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remplacer les références à .project
                new_content = content.replace(".project", ".project")
                
                with open(readme_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print("         📝 README.md mis à jour")
            except Exception as e:
                print(f"         ⚠️ Erreur lors de la mise à jour du README: {e}")
    
    def verify_migration(self, migration_targets):
        """Vérifie que la migration s'est bien passée."""
        print("\n✅ Vérification de la migration...")
        
        success_count = 0
        
        for target in migration_targets:
            project_name = target['project_name']
            project_dir = target['project_dir']
            old_audit_dir = target['audit_dir']
            
            # Vérifier que .project existe
            if project_dir.exists():
                print(f"   ✅ {project_name}: Dossier .project créé")
                
                # Vérifier que .project n'existe plus
                if not old_audit_dir.exists():
                    print(f"   ✅ {project_name}: Ancien dossier .project supprimé")
                    
                    # Vérifier la structure
                    for subdir in ["config", "logs", "reports", "tests"]:
                        subdir_path = project_dir / subdir
                        if subdir_path.exists():
                            print(f"   ✅ {project_name}: Sous-dossier {subdir}/ créé")
                    
                    success_count += 1
                else:
                    print(f"   ⚠️ {project_name}: Ancien dossier .project toujours présent")
            else:
                print(f"   ❌ {project_name}: Dossier .project manquant")
        
        print(f"\n📊 Résultat: {success_count}/{len(migration_targets)} projets migrés avec succès")
        return success_count == len(migration_targets)
    
    def generate_migration_report(self, migration_targets, backup_dir, success):
        """Génère un rapport de migration."""
        print("\n📋 Génération du rapport de migration...")
        
        report_content = f"""# RAPPORT DE MIGRATION .AUDIT → .PROJECT
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Résumé de la migration

**Statut:** {'✅ Succès' if success else '❌ Échec'}
**Projets migrés:** {len(migration_targets)}

## Projets traités

"""
        
        for target in migration_targets:
            project_name = target['project_name']
            project_dir = target['project_dir']
            
            report_content += f"""### {project_name}
- **Ancien dossier:** .project
- **Nouveau dossier:** .project
- **Statut:** {'✅ Migré' if project_dir.exists() else '❌ Échec'}
- **Chemin:** {project_dir.relative_to(self.project_dir)}

"""
        
        report_content += f"""
## Sauvegarde

Une sauvegarde de l'ancienne structure a été créée dans:
`{backup_dir.relative_to(self.project_dir)}`

## Nouvelle structure

```
projet_exemple/
├── config.json              # Configuration du projet
├── src/                     # Code source du projet
├── tests/                   # Tests du projet (fonctionnels, unitaires)
├── logs/                    # Logs du programme en cours d'exécution
├── reports/                 # Rapports générés par le programme
├── docs/                    # Documentation du projet
└── .project/                # Dossier du projet (caché)
    ├── README.md           # Documentation du projet
    ├── config/              # Configuration du projet
    ├── logs/                # Logs du projet (historique, sessions)
    ├── reports/             # Rapports du projet (analyses, métriques)
    └── tests/               # Tests du projet (intégration, performance)
```

## Avantages de la nouvelle structure

1. **Clarté** : Plus de confusion entre programme et projet
2. **Intuitivité** : .project = tout ce qui concerne le projet
3. **Standard** : Conforme aux pratiques de l'industrie
4. **Maintenabilité** : Structure plus logique et cohérente

## Utilisation

- **Développement** : Utiliser les dossiers à la racine
- **Projet** : Utiliser le dossier .project/
- **Documentation** : Consulter les README.md dans chaque dossier
"""
        
        report_file = self.project_dir / "docs" / "MIGRATION_REPORT.md"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"   📄 Rapport généré: {report_file}")

def main():
    """Fonction principale."""
    project_dir = Path(__file__).parent
    
    print("🎯 MIGRATION VERS .PROJECT - SYSTÈME D'AUDIT UNIVERSEL")
    print("=" * 60)
    print(f"📁 Répertoire: {project_dir}")
    print(f"⏰ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    migrator = ProjectMigrationManager(project_dir)
    
    # 1. Analyser les besoins de migration
    migration_targets = migrator.analyze_migration_needs()
    
    if not migration_targets:
        print("✅ Aucune migration nécessaire")
        return
    
    # 2. Sauvegarder la structure existante
    backup_dir = migrator.backup_existing_structure(migration_targets)
    
    # 3. Migrer vers la structure .project
    migrator.migrate_to_project_structure(migration_targets)
    
    # 4. Mettre à jour la configuration du système
    migrator.update_system_configuration()
    
    # 5. Vérifier la migration
    success = migrator.verify_migration(migration_targets)
    
    # 6. Générer un rapport
    migrator.generate_migration_report(migration_targets, backup_dir, success)
    
    print("\n🎉 MIGRATION TERMINÉE")
    print("=" * 60)
    if success:
        print("✅ Migration vers .project réussie!")
        print("📋 Rapport généré dans docs/MIGRATION_REPORT.md")
        print("💾 Sauvegarde créée dans backup_migration/")
    else:
        print("❌ Migration partiellement échouée")
        print("📋 Consultez le rapport pour plus de détails")

if __name__ == "__main__":
    main()
