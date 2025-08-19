#!/usr/bin/env python3
"""
NETTOYAGE ANCIEN SYSTÈME AUDIT - SYSTÈME D'AUDIT UNIVERSEL
=========================================================

Script pour nettoyer l'ancien système d'audit après migration vers le nouveau système.
ATTENTION: Ce script supprime définitivement les anciens rapports et logs.
"""

import shutil
import json
from pathlib import Path
from datetime import datetime

def cleanup_old_audit(audit_dir: Path, backup_dir: Path = None):
    """Nettoie l'ancien système d'audit."""
    
    print(f"🧹 Nettoyage de l'ancien système d'audit...")
    print(f"📁 Audit: {audit_dir}")
    
    if backup_dir:
        print(f"📁 Sauvegarde: {backup_dir}")
    else:
        print(f"⚠️  ATTENTION: Aucune sauvegarde - suppression définitive!")
    
    print()
    
    # Créer une sauvegarde si demandée
    if backup_dir:
        backup_dir.mkdir(parents=True, exist_ok=True)
        print("📦 Création de la sauvegarde...")
        
        # Sauvegarder les rapports
        old_reports = audit_dir / "reports"
        if old_reports.exists():
            backup_reports = backup_dir / "reports"
            shutil.copytree(old_reports, backup_reports, dirs_exist_ok=True)
            print(f"  ✅ Rapports sauvegardés: {backup_reports}")
        
        # Sauvegarder les logs
        old_logs = audit_dir / "logs"
        if old_logs.exists():
            backup_logs = backup_dir / "logs"
            shutil.copytree(old_logs, backup_logs, dirs_exist_ok=True)
            print(f"  ✅ Logs sauvegardés: {backup_logs}")
        
        # Sauvegarder les règles
        old_rules = audit_dir / "rules"
        if old_rules.exists():
            backup_rules = backup_dir / "rules"
            shutil.copytree(old_rules, backup_rules, dirs_exist_ok=True)
            print(f"  ✅ Règles sauvegardées: {backup_rules}")
        
        # Sauvegarder les scripts
        old_scripts = audit_dir / "scripts"
        if old_scripts.exists():
            backup_scripts = backup_dir / "scripts"
            shutil.copytree(old_scripts, backup_scripts, dirs_exist_ok=True)
            print(f"  ✅ Scripts sauvegardés: {backup_scripts}")
    
    # Supprimer les anciens dossiers
    print("🗑️  Suppression des anciens dossiers...")
    
    directories_to_remove = [
        audit_dir / "reports",
        audit_dir / "logs",
        audit_dir / "rules",
        audit_dir / "scripts"
    ]
    
    for directory in directories_to_remove:
        if directory.exists():
            shutil.rmtree(directory)
            print(f"  ✅ Supprimé: {directory}")
        else:
            print(f"  ℹ️  Non trouvé: {directory}")
    
    # Supprimer l'ancien script principal
    old_script = audit_dir / "Audit IA.py"
    if old_script.exists():
        old_script.unlink()
        print(f"  ✅ Supprimé: {old_script}")
    
    # Créer un rapport de nettoyage
    cleanup_report = {
        "cleanup_info": {
            "timestamp": datetime.now().isoformat(),
            "audit_dir": str(audit_dir),
            "backup_dir": str(backup_dir) if backup_dir else None,
            "cleanup_type": "backup_and_clean" if backup_dir else "clean_only"
        },
        "removed_directories": [
            str(d) for d in directories_to_remove if d.exists()
        ],
        "removed_files": [
            str(old_script) if old_script.exists() else None
        ]
    }
    
    # Sauvegarder le rapport de nettoyage
    cleanup_file = audit_dir / f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(cleanup_file, 'w', encoding='utf-8') as f:
        json.dump(cleanup_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Nettoyage terminé!")
    print(f"📄 Rapport de nettoyage: {cleanup_file}")
    
    if backup_dir:
        print(f"📦 Sauvegarde créée: {backup_dir}")
        print(f"💡 Pour restaurer: copiez le contenu de {backup_dir} vers {audit_dir}")

def main():
    """Fonction principale."""
    import sys
    
    audit_dir = Path(__file__).parent
    
    # Vérifier les arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--backup":
            # Créer une sauvegarde avant nettoyage
            backup_dir = audit_dir.parent / f"audit_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"🔄 Mode sauvegarde activé")
        elif sys.argv[1] == "--force":
            # Nettoyage sans sauvegarde
            backup_dir = None
            print(f"⚠️  Mode force activé - pas de sauvegarde")
        else:
            print(f"❌ Argument invalide: {sys.argv[1]}")
            print(f"Usage: python cleanup_old_audit.py [--backup|--force]")
            sys.exit(1)
    else:
        # Demander confirmation
        print(f"⚠️  ATTENTION: Ce script va supprimer l'ancien système d'audit!")
        print(f"Options:")
        print(f"  --backup: Créer une sauvegarde avant nettoyage")
        print(f"  --force: Nettoyer sans sauvegarde")
        print(f"  (aucun argument): Demander confirmation")
        
        response = input(f"\nVoulez-vous continuer? (oui/non): ").lower().strip()
        if response not in ['oui', 'yes', 'o', 'y']:
            print(f"❌ Nettoyage annulé")
            sys.exit(0)
        
        backup_dir = None
    
    # Vérifier que le dossier audit existe
    if not audit_dir.exists():
        print(f"❌ Erreur: Le dossier audit {audit_dir} n'existe pas")
        sys.exit(1)
    
    # Effectuer le nettoyage
    try:
        cleanup_old_audit(audit_dir, backup_dir)
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
