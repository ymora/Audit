#!/usr/bin/env python3
"""
MIGRATION DES ANCIENS RAPPORTS - SYSTÈME D'AUDIT UNIVERSEL
========================================================

Script pour migrer les anciens rapports et logs vers le nouveau système
qui stocke tout dans chaque projet.
"""

import shutil
import json
from pathlib import Path
from datetime import datetime

def migrate_old_reports(audit_dir: Path, project_path: Path):
    """Migre les anciens rapports vers le nouveau système."""
    
    print(f"🔄 Migration des anciens rapports...")
    print(f"📁 Audit: {audit_dir}")
    print(f"📁 Projet: {project_path}")
    print()
    
    # Créer le dossier d'audit dans le projet s'il n'existe pas
    project_audit_dir = project_path / ".audit"
    project_audit_dir.mkdir(parents=True, exist_ok=True)
    
    # Migrer les rapports
    old_reports_dir = audit_dir / "reports"
    new_reports_dir = project_audit_dir / "reports"
    new_reports_dir.mkdir(parents=True, exist_ok=True)
    
    if old_reports_dir.exists():
        print("📄 Migration des rapports...")
        
        # Migrer les rapports du projet spécifique
        project_name = project_path.name.lower().replace(' ', '_').replace('-', '_')
        old_project_reports = old_reports_dir / project_name
        
        if old_project_reports.exists():
            for report_file in old_project_reports.glob("*"):
                if report_file.is_file():
                    new_file = new_reports_dir / report_file.name
                    shutil.copy2(report_file, new_file)
                    print(f"  ✅ Rapport migré: {report_file.name}")
        
        # Migrer les rapports généraux (latest)
        latest_reports = old_reports_dir / "latest"
        if latest_reports.exists():
            for report_file in latest_reports.glob("*"):
                if report_file.is_file():
                    new_file = new_reports_dir / f"migrated_latest_{report_file.name}"
                    shutil.copy2(report_file, new_file)
                    print(f"  ✅ Rapport latest migré: {report_file.name}")
        
        # Migrer les rapports d'archive
        archive_reports = old_reports_dir / "archive"
        if archive_reports.exists():
            for report_file in archive_reports.glob("*"):
                if report_file.is_file():
                    new_file = new_reports_dir / f"migrated_archive_{report_file.name}"
                    shutil.copy2(report_file, new_file)
                    print(f"  ✅ Rapport d'archive migré: {report_file.name}")
        
        # Migrer les rapports généraux dans le dossier reports
        for report_file in old_reports_dir.glob("*"):
            if report_file.is_file() and report_file.suffix in ['.json', '.html', '.md']:
                new_file = new_reports_dir / f"migrated_{report_file.name}"
                shutil.copy2(report_file, new_file)
                print(f"  ✅ Rapport général migré: {report_file.name}")
    
    # Migrer les logs
    old_logs_dir = audit_dir / "logs"
    new_logs_dir = project_audit_dir / "logs"
    new_logs_dir.mkdir(parents=True, exist_ok=True)
    
    if old_logs_dir.exists():
        print("📝 Migration des logs...")
        
        # Migrer les logs actuels
        current_logs = old_logs_dir / "current"
        if current_logs.exists():
            for log_file in current_logs.glob("*"):
                if log_file.is_file():
                    new_file = new_logs_dir / f"migrated_{log_file.name}"
                    shutil.copy2(log_file, new_file)
                    print(f"  ✅ Log migré: {log_file.name}")
        
        # Migrer les logs d'archive
        archive_logs = old_logs_dir / "archive"
        if archive_logs.exists():
            for log_file in archive_logs.glob("*"):
                if log_file.is_file():
                    new_file = new_logs_dir / f"archived_{log_file.name}"
                    shutil.copy2(log_file, new_file)
                    print(f"  ✅ Log d'archive migré: {log_file.name}")
    
    # Créer un rapport de migration
    migration_report = {
        "migration_info": {
            "timestamp": datetime.now().isoformat(),
            "audit_dir": str(audit_dir),
            "project_path": str(project_path),
            "project_audit_dir": str(project_audit_dir)
        },
        "migrated_files": {
            "reports": [],
            "logs": []
        }
    }
    
    # Compter les fichiers migrés
    for report_file in new_reports_dir.glob("*"):
        if report_file.is_file():
            migration_report["migrated_files"]["reports"].append(report_file.name)
    
    for log_file in new_logs_dir.glob("*"):
        if log_file.is_file():
            migration_report["migrated_files"]["logs"].append(log_file.name)
    
    # Sauvegarder le rapport de migration
    migration_file = new_reports_dir / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(migration_file, 'w', encoding='utf-8') as f:
        json.dump(migration_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Migration terminée!")
    print(f"📊 Fichiers migrés:")
    print(f"   - Rapports: {len(migration_report['migrated_files']['reports'])}")
    print(f"   - Logs: {len(migration_report['migrated_files']['logs'])}")
    print(f"📄 Rapport de migration: {migration_file}")
    print(f"📂 Nouveau dossier d'audit: {project_audit_dir}")

def main():
    """Fonction principale."""
    import sys
    
    # Obtenir les chemins
    if len(sys.argv) > 1:
        project_path = Path(sys.argv[1])
    else:
        project_path = Path.cwd()
    
    audit_dir = Path(__file__).parent
    
    # Vérifier que le projet existe
    if not project_path.exists():
        print(f"❌ Erreur: Le projet {project_path} n'existe pas")
        sys.exit(1)
    
    # Vérifier que le dossier audit existe
    if not audit_dir.exists():
        print(f"❌ Erreur: Le dossier audit {audit_dir} n'existe pas")
        sys.exit(1)
    
    # Effectuer la migration
    try:
        migrate_old_reports(audit_dir, project_path)
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
