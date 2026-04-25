"""
Afficher les détails d'un audit de manière lisible
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def print_section(title):
    """Afficher une section"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")


def print_subsection(title):
    """Afficher une sous-section"""
    print(f"\n{'─'*60}")
    print(f"{title}")
    print(f"{'─'*60}")


def show_audit_details(report_path: Path):
    """Afficher les détails de l'audit"""
    
    if not report_path.exists():
        print(f"Erreur: Fichier {report_path} introuvable")
        return
    
    with open(report_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Métadonnées
    print_section("MÉTADONNÉES")
    print(f"  Projet: {data['metadata']['project_name']}")
    print(f"  Chemin: {data['metadata']['project_path']}")
    print(f"  Timestamp: {data['metadata']['timestamp']}")
    print(f"  Version moteur: {data['metadata']['engine_version']}")
    print(f"  Durée: {data['metadata']['duration_seconds']:.2f}s")
    
    # Info projet (auto-détecté)
    print_section("INFO PROJET (AUTO-DÉTECTÉ)")
    print(f"  Type: {data['project_info']['project_type']}")
    print(f"  Langages: {', '.join(data['project_info']['languages'])}")
    print(f"  Frameworks: {', '.join(data['project_info']['frameworks'])}")
    print(f"  Bases de données: {', '.join(data['project_info']['databases'])}")
    print(f"  Architecture: {', '.join(data['project_info']['architecture'])}")
    print(f"  Ports: {', '.join(map(str, data['project_info']['ports']))}")
    print(f"  Services: {', '.join(data['project_info']['services'])}")
    print(f"  Docker: {'Oui' if data['project_info']['has_docker'] else 'Non'}")
    print(f"  Tests: {'Oui' if data['project_info']['has_tests'] else 'Non'}")
    print(f"  CI/CD: {'Oui' if data['project_info']['has_ci_cd'] else 'Non'}")
    
    # Scores
    print_section("SCORES")
    scores = data['scores']
    print(f"  Score Global: {scores['global_score']}/100")
    print(f"  Score Sécurité: {scores['security_score']}/100")
    print(f"  Score Qualité: {scores['quality_score']}/100")
    print(f"  Total Issues: {scores['total_issues']}")
    print(f"  Issues Critiques: {scores['critical_issues']}")
    print(f"  Issues Majeures: {scores['major_issues']}")
    print(f"  Issues Mineures: {scores['minor_issues']}")
    
    # Phases
    print_section("PHASES")
    for phase_name, phase_data in data['phases'].items():
        print(f"\n  📋 {phase_name.upper()}")
        print(f"     Status: {phase_data['result']['status']}")
        print(f"     Summary: {phase_data['result'].get('summary', 'N/A')}")
        print(f"     Durée: {phase_data['duration']:.2f}s")
        
        # Issues de cette phase
        if 'issues' in phase_data['result'] and phase_data['result']['issues']:
            print(f"     Issues ({len(phase_data['result']['issues'])}):")
            for issue in phase_data['result']['issues'][:5]:  # Max 5 issues par phase
                severity = issue.get('severity', 'N/A')
                message = issue.get('message', 'N/A')
                print(f"       [{severity}] {message}")
            if len(phase_data['result']['issues']) > 5:
                print(f"       ... et {len(phase_data['result']['issues']) - 5} autres")
    
    # Top 20 issues par sévérité
    print_section("TOP 20 ISSUES PAR SÉVÉRITÉ")
    
    # Trier les issues par sévérité
    all_issues = data.get('issues', [])
    
    # Priorité: CRITICAL > MAJOR > MINOR
    severity_order = {'CRITICAL': 0, 'MAJOR': 1, 'MINOR': 2}
    all_issues_sorted = sorted(all_issues, key=lambda x: severity_order.get(str(x.get('severity', 'MINOR')), 3))
    
    for i, issue in enumerate(all_issues_sorted[:20], 1):
        print(f"\n  #{i} [{issue.get('severity', 'N/A')}]")
        print(f"     Phase: {issue.get('phase', 'N/A')}")
        print(f"     Catégorie: {issue.get('category', 'N/A')}")
        print(f"     Message: {issue.get('message', 'N/A')}")
        print(f"     Fichier: {issue.get('file_path', 'N/A')}")
        if issue.get('line_number'):
            print(f"     Ligne: {issue.get('line_number')}")
        print(f"     Suggestion: {issue.get('suggestion', 'N/A')}")
        print(f"     Priorité: {issue.get('priority_score', 'N/A')}/100")
        print(f"     Temps estimé: {issue.get('estimated_fix_time', 'N/A')}")
    
    # Recommandations
    print_section("RECOMMANDATIONS")
    recommendations = data.get('recommendations', [])
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"\n  {i}. {rec}")
    else:
        print("  Aucune recommandation")


def main():
    """Point d'entrée principal"""
    if len(sys.argv) < 2:
        print("Usage: python show_audit_details.py <chemin_rapport>")
        print("\nExemples:")
        print("  python show_audit_details.py reports/docusense-ai-v2/audit_20260412_082639.json")
        print("  python show_audit_details.py reports/audit/audit_20260412_081820.json")
        return
    
    report_path = Path(sys.argv[1])
    show_audit_details(report_path)


if __name__ == "__main__":
    main()
