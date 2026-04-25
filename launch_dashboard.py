import os
import sys
from pathlib import Path
import webbrowser

def main():
    """
    Lanceur du dashboard d'audit. 
    Trouve le dernier rapport HTML généré et l'ouvre dans le navigateur.
    """
    reports_dir = Path(__file__).parent / "reports"
    if not reports_dir.exists():
        print("[-] Aucun dossier 'reports' trouvé. Lancez d'abord un audit.")
        return

    # Trouver tous les fichiers dashboard_*.html
    dashboards = list(reports_dir.rglob("dashboard_*.html"))
    if not dashboards:
        print("[-] Aucun dashboard HTML trouvé.")
        return

    # Trier par date de modification (le plus récent en premier)
    dashboards.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest = dashboards[0]

    print(f"[+] Ouverture du dashboard Grâal : {latest.name}")
    webbrowser.open(f"file:///{latest.absolute()}")

if __name__ == "__main__":
    main()
