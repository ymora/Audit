import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from core.engine import AuditEngine


def clear_screen():
    """Efface l'écran de la console de manière sécurisée sans utiliser os.system."""
    # Séquence ANSI pour effacer l'écran : \033[H (home) \033[J (clear screen)
    sys.stdout.write("\033[H\033[2J")
    sys.stdout.flush()


def print_menu():
    """
    Affiche le menu principal interactif du système d'audit.
    
    Cette fonction liste dynamiquement tous les répertoires de projets 
    détectés dans le dossier racine de travail (d:/Windsurf).
    """
    clear_screen()
    print("=" * 80)
    print("  SYSTÈME D'AUDIT MODULAIRE — ARCHITECTURE GRAAL v4.0")
    print("=" * 80)
    print("\n  PROJETS DISPONIBLES:\n")
    
    # Lister les projets dans d:\Windsurf\
    windsurf_path = Path("d:/Windsurf")
    projects = []
    if windsurf_path.exists():
        projects = [p for p in windsurf_path.iterdir() if p.is_dir() and not p.name.startswith('.')]
        for i, project in enumerate(projects, 1):
            print(f"  {i:2d}. {project.name:<30}")
    else:
        print("  [!] Erreur: d:/Windsurf introuvable")
    
    print("\n  00. Quitter")
    print("\n" + "=" * 80)
    return projects


def run_audit_interactive(project_path: Path, project_name: str = None):
    """
    Exécute l'audit complet d'un projet spécifique en mode interactif.

    Args:
        project_path (Path): Chemin racine du projet à auditer.
        project_name (str, optional): Nom d'affichage du projet.
    """
    if not project_name:
        project_name = project_path.name
    
    print(f"\n{'='*80}")
    print(f"DÉMARRAGE AUDIT - {project_name.upper()}")
    print(f"{'='*80}")
    print(f"Cible: {project_path}")
    
    # Créer le moteur d'audit
    engine = AuditEngine(project_path)
    
    # Exécuter l'audit
    engine.run_audit()
    
    # Sauvegarder le rapport
    report_file = engine.save_report()
    
    # Afficher la synthèse IA
    print(f"\n{'-'*80}")
    print("SYNTHÈSE IA:")
    print(f"{engine.results.get('executive_summary', 'Aucune synthèse générée.')}")
    print(f"{'-'*80}")
    
    print(f"\n[OK] Audit terminé avec succès.")
    print(f"[DOC] Rapport complet généré: {report_file}")
    print("=" * 80)


def main():
    """
    Point d'entrée principal de l'application d'audit.
    
    Gère la bascule entre le mode ligne de commande (CLI) et le mode interactif.
    """
    # Mode ligne de commande
    if len(sys.argv) > 1 and sys.argv[1] != "--interactive":
        project_path = Path(sys.argv[1])
        if not project_path.exists():
            print(f"Erreur: Le chemin {project_path} n'existe pas.")
            return 1
            
        engine = AuditEngine(project_path)
        engine.run_audit()
        report_file = engine.save_report()
        
        # Afficher la synthèse IA
        print(f"\n{'-'*80}")
        print("SYNTHÈSE IA:")
        print(f"{engine.results.get('executive_summary', 'Aucune synthèse générée.')}")
        print(f"{'-'*80}")
        
        print(f"\n[OK] Audit terminé avec succès.")
        print(f"[DOC] Rapports générés dans: {report_file.parent}")
        return 0
    
    # Mode interactif
    while True:
        projects = print_menu()
        
        try:
            choice = input("\nEntrez le numéro du projet (0 pour quitter): ").strip()
            
            if choice in ("0", "00"):
                print("\n[INFO] Fermeture de l'audit. Au revoir!")
                break
            
            index = int(choice) - 1
            if 0 <= index < len(projects):
                run_audit_interactive(projects[index])
                input("\nAppuyez sur Entrée pour revenir au menu...")
            else:
                print(f"\n[!] Erreur: Choix invalide (1-{len(projects)})")
                input("\nAppuyez sur Entrée...")
        except ValueError:
            print("\n[!] Erreur: Veuillez entrer un nombre valide.")
            input("\nAppuyez sur Entrée...")
        except KeyboardInterrupt:
            print("\n\n[INFO] Interruption utilisateur. Au revoir!")
            break
            
    return 0


if __name__ == "__main__":
    # Assurer que le terminal supporte ANSI sur Windows
    if os.name == 'nt':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004 | DISABLE_NEWLINE_AUTO_RETURN = 0x0008
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        
    sys.exit(main())
