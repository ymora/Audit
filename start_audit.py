#!/usr/bin/env python3
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
        print("\n❌ Impossible de lancer l'interface graphique.")
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
        print("\n⏹️ Lancement interrompu par l'utilisateur.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
