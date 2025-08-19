#!/usr/bin/env python3
"""
DÉMONSTRATION - SYSTÈME D'AUDIT UNIVERSEL
========================================

Script de démonstration pour présenter les fonctionnalités du système d'audit universel.
"""

import subprocess
import sys
import time
from pathlib import Path

def print_header(title):
    """Affiche un en-tête stylisé."""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)

def print_step(step, description):
    """Affiche une étape de la démonstration."""
    print(f"\n📋 Étape {step}: {description}")
    print("-" * 40)

def run_command(command, description=""):
    """Exécute une commande et affiche le résultat."""
    print(f"⚡ {description}")
    print(f"Commande: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Succès")
            if result.stdout.strip():
                print("Sortie:")
                print(result.stdout.strip())
        else:
            print("❌ Erreur")
            if result.stderr.strip():
                print("Erreur:")
                print(result.stderr.strip())
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def demo_interface_graphique():
    """Démonstration de l'interface graphique."""
    print_header("Interface Graphique")
    
    print("🎯 Fonctionnalités de l'interface graphique:")
    print("• Sélection de projet via dialogue de fichiers")
    print("• Lancement d'audit en un clic")
    print("• Ouverture automatique des rapports HTML")
    print("• Gestion des projets récents")
    print("• Logs en temps réel")
    print("• Barre de progression")
    
    print("\n🚀 Lancement de l'interface...")
    print("💡 L'interface va s'ouvrir dans une nouvelle fenêtre.")
    print("   Vous pourrez tester toutes les fonctionnalités.")
    
    response = input("\nVoulez-vous lancer l'interface graphique? (oui/non): ").lower().strip()
    if response in ['oui', 'yes', 'o', 'y']:
        return run_command("python audit_gui.py", "Lancement de l'interface graphique")
    else:
        print("⏭️ Interface graphique ignorée.")
        return True

def demo_audit_ligne_commande():
    """Démonstration de l'audit en ligne de commande."""
    print_header("Audit en Ligne de Commande")
    
    # Utiliser le projet actuel comme exemple
    current_project = Path.cwd().parent  # Remonter d'un niveau depuis audit/
    
    print(f"📁 Projet de démonstration: {current_project}")
    
    print_step(1, "Initialisation de l'audit dans le projet")
    success = run_command(
        f"python init_audit.py \"{current_project}\"",
        "Initialisation de l'audit dans le projet de démonstration"
    )
    
    if success:
        print_step(2, "Exécution de l'audit")
        success = run_command(
            f"python universal_auditor.py \"{current_project}\"",
            "Exécution de l'audit complet"
        )
        
        if success:
            print_step(3, "Vérification des rapports")
            audit_dir = current_project / ".audit"
            if audit_dir.exists():
                reports_dir = audit_dir / "reports"
                if reports_dir.exists():
                    html_reports = list(reports_dir.glob("*.html"))
                    json_reports = list(reports_dir.glob("*.json"))
                    
                    print(f"✅ Rapports générés:")
                    print(f"   • HTML: {len(html_reports)} fichier(s)")
                    print(f"   • JSON: {len(json_reports)} fichier(s)")
                    
                    if html_reports:
                        latest_html = reports_dir / "latest_report.html"
                        if latest_html.exists():
                            print(f"   • Dernier rapport: {latest_html}")
                            
                            response = input("\nVoulez-vous ouvrir le rapport HTML? (oui/non): ").lower().strip()
                            if response in ['oui', 'yes', 'o', 'y']:
                                run_command(f"start {latest_html}", "Ouverture du rapport HTML")
                else:
                    print("❌ Aucun rapport trouvé")
            else:
                print("❌ Dossier d'audit non trouvé")

def demo_migration():
    """Démonstration de la migration."""
    print_header("Migration des Anciens Rapports")
    
    print("🔄 Fonctionnalités de migration:")
    print("• Migration automatique des anciens rapports")
    print("• Préservation de l'historique")
    print("• Organisation dans le nouveau système")
    print("• Rapport de migration détaillé")
    
    current_project = Path.cwd().parent
    
    print(f"\n📁 Migration vers: {current_project}")
    
    success = run_command(
        f"python migrate_old_reports.py \"{current_project}\"",
        "Migration des anciens rapports"
    )
    
    if success:
        print("✅ Migration terminée avec succès!")
        print("📊 Vérifiez le dossier .audit/ pour voir les fichiers migrés.")

def demo_types_projets():
    """Démonstration des types de projets supportés."""
    print_header("Types de Projets Supportés")
    
    projects_dir = Path("projects")
    if projects_dir.exists():
        project_types = [d.name for d in projects_dir.iterdir() if d.is_dir()]
        
        print("🎯 Types de projets configurés:")
        for project_type in project_types:
            config_file = projects_dir / project_type / "config.json"
            if config_file.exists():
                print(f"   • {project_type} ✅")
            else:
                print(f"   • {project_type} ⚠️ (config manquante)")
        
        print(f"\n📊 Total: {len(project_types)} type(s) de projet")
        
        if project_types:
            print("\n🔧 Pour ajouter un nouveau type:")
            print("1. Créer le dossier: projects/nouveau_type/")
            print("2. Ajouter config.json")
            print("3. Créer les tests dans tests/")
            print("4. Documenter dans le README")
    else:
        print("❌ Dossier projects/ non trouvé")

def demo_fonctionnalites_avancees():
    """Démonstration des fonctionnalités avancées."""
    print_header("Fonctionnalités Avancées")
    
    print("🚀 Fonctionnalités avancées disponibles:")
    print("• Tests personnalisables par type de projet")
    print("• Configuration flexible via JSON")
    print("• Rapports HTML avec graphiques")
    print("• Logs détaillés avec horodatage")
    print("• Migration automatique des anciens systèmes")
    print("• Interface graphique intuitive")
    print("• Support multi-projets")
    print("• Architecture modulaire et extensible")
    
    print("\n📈 Avantages du système:")
    print("• Gain de temps significatif")
    print("• Standardisation des audits")
    print("• Historique complet préservé")
    print("• Facilité d'utilisation")
    print("• Extensibilité maximale")

def main():
    """Fonction principale de démonstration."""
    print_header("Démonstration - Système d'Audit Universel")
    
    print("🎯 Cette démonstration présente les principales fonctionnalités")
    print("   du Système d'Audit Universel.")
    
    print("\n📋 Menu de démonstration:")
    print("1. Interface graphique")
    print("2. Audit en ligne de commande")
    print("3. Migration des anciens rapports")
    print("4. Types de projets supportés")
    print("5. Fonctionnalités avancées")
    print("6. Démonstration complète")
    print("0. Quitter")
    
    while True:
        choice = input("\nChoisissez une option (0-6): ").strip()
        
        if choice == "0":
            print("\n👋 Merci d'avoir testé le Système d'Audit Universel!")
            break
        elif choice == "1":
            demo_interface_graphique()
        elif choice == "2":
            demo_audit_ligne_commande()
        elif choice == "3":
            demo_migration()
        elif choice == "4":
            demo_types_projets()
        elif choice == "5":
            demo_fonctionnalites_avancees()
        elif choice == "6":
            print_header("Démonstration Complète")
            demo_interface_graphique()
            time.sleep(1)
            demo_audit_ligne_commande()
            time.sleep(1)
            demo_migration()
            time.sleep(1)
            demo_types_projets()
            time.sleep(1)
            demo_fonctionnalites_avancees()
            print("\n🎉 Démonstration complète terminée!")
        else:
            print("❌ Option invalide. Veuillez choisir 0-6.")
    
    print_header("Fin de la Démonstration")
    print("💡 Pour plus d'informations, consultez:")
    print("   • README.md - Documentation principale")
    print("   • README_PROJET.md - Documentation du projet")
    print("   • audit/README.md - Documentation technique")

if __name__ == "__main__":
    main()
