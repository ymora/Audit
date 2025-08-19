#!/usr/bin/env python3
"""
SYSTÈME D'AUDIT UNIVERSEL - POINT D'ENTRÉE UNIFIÉ
=================================================

Point d'entrée unique pour le système d'audit universel.
"""

import sys
import subprocess
import argparse
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
        print(f"Erreur: {e}")
        return False

def launch_gui():
    """Lance l'interface graphique."""
    print("Lancement du Systeme d'Audit Universel")
    print("=" * 50)
    
    if not check_dependencies():
        print("Impossible de lancer l'interface graphique.")
        return 1
    
    audit_dir = Path(__file__).parent
    gui_script = audit_dir / "core" / "audit_gui.py"
    
    if not gui_script.exists():
        print(f"Script GUI introuvable: {gui_script}")
        return 1
    
    print(f"Script GUI trouve: {gui_script}")
    print("Lancement de l'interface moderne...")
    
    try:
        subprocess.run([sys.executable, str(gui_script)], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du lancement: {e}")
        return 1
    except KeyboardInterrupt:
        print("Lancement interrompu par l'utilisateur.")
        return 0

def launch_cli(project_path):
    """Lance l'audit en ligne de commande."""
    print(f"Audit en ligne de commande pour: {project_path}")
    print("=" * 50)
    
    audit_dir = Path(__file__).parent
    audit_script = audit_dir / "core" / "audit.py"
    
    if not audit_script.exists():
        print(f"Script d'audit introuvable: {audit_script}")
        return 1
    
    try:
        subprocess.run([sys.executable, str(audit_script), str(project_path)], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'audit: {e}")
        return 1

def show_help():
    """Affiche l'aide."""
    help_text = """
SYSTEME D'AUDIT UNIVERSEL v2.0.0
====================================

USAGE:
    python audit.py                    # Lance l'interface graphique
    python audit.py --gui              # Lance l'interface graphique
    python audit.py --cli <projet>     # Audit en ligne de commande
    python audit.py --help             # Affiche cette aide

EXEMPLES:
    python audit.py                    # Interface graphique moderne
    python audit.py --cli ./mon_projet # Audit du projet ./mon_projet

FONCTIONNALITES:
    Interface graphique moderne avec theme sombre
    Detection automatique des doublons de code
    Identification du code mort
    Verification de securite
    Rapports detailles en HTML, Markdown et JSON
    Support pour tous types de projets

DOCUMENTATION:
    docs/README_PROJET.md          # Documentation detaillee
    docs/RESUME_FINAL.md           # Resume du projet
    CHANGELOG.md                   # Historique des versions

LICENCE: MIT
"""
    print(help_text)

def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Systeme d'Audit Universel v2.0.0",
        add_help=False
    )
    parser.add_argument('--gui', action='store_true', help='Lance l interface graphique')
    parser.add_argument('--cli', metavar='PROJET', help='Audit en ligne de commande du projet specifie')
    parser.add_argument('--help', action='store_true', help='Affiche l aide')
    
    if len(sys.argv) == 1:
        return launch_gui()
    
    args = parser.parse_args()
    
    if args.help:
        show_help()
        return 0
    elif args.gui:
        return launch_gui()
    elif args.cli:
        project_path = Path(args.cli)
        if not project_path.exists():
            print(f"Erreur: Le projet {project_path} n'existe pas")
            return 1
        return launch_cli(project_path)
    else:
        return launch_gui()

if __name__ == "__main__":
    sys.exit(main())
