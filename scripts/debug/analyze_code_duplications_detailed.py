#!/usr/bin/env python3
"""
ANALYSE DÉTAILLÉE DES DUPLICATIONS
===================================

Script pour analyser en détail les duplications détectées
et vérifier qu'elles ne proviennent pas du répertoire codemort.
"""

import json
from pathlib import Path
import sys
from pathlib import Path

# Ajouter le répertoire tools au path
current_dir = Path(__file__).parent
tools_dir = current_dir.parent / "tools"
sys.path.insert(0, str(tools_dir))

try:
    from code_analyzer import CodeAnalyzer
except ImportError:
    print("Erreur: Impossible d'importer CodeAnalyzer")
    print(f"Tools dir: {tools_dir}")
    print(f"Files in tools: {list(tools_dir.glob('*.py'))}")
    sys.exit(1)

def analyze_duplications_detailed():
    """Analyse détaillée des duplications."""
    print("🔍 ANALYSE DÉTAILLÉE DES DUPLICATIONS")
    print("=" * 50)
    
    # Initialiser l'analyseur
    analyzer = CodeAnalyzer()
    
    # Analyser le projet
    print("📊 Analyse du projet en cours...")
    report = analyzer.analyze_project()
    
    # Afficher les statistiques
    print(f"\n📈 STATISTIQUES GÉNÉRALES:")
    print(f"   Fichiers analysés: {report['files_analyzed']}")
    print(f"   Fonctions totales: {report['total_functions']}")
    print(f"   Classes totales: {report['total_classes']}")
    print(f"   Duplications trouvées: {report['duplications_found']}")
    
    # Analyser les duplications
    print(f"\n🔍 ANALYSE DES DUPLICATIONS:")
    print("-" * 30)
    
    if not report['duplications']:
        print("✅ Aucune duplication détectée!")
        return
    
    # Afficher le résumé des duplications
    summary = report.get('duplications_summary', {})
    print(f"\n📊 RÉSUMÉ DES DUPLICATIONS:")
    print(f"   Total duplications: {summary.get('total_duplications', 0)}")
    print(f"   À corriger: {summary.get('duplications_to_fix', 0)}")
    print(f"   Légitimes: {summary.get('legitimate_duplications', 0)}")
    print(f"   Critiques: {summary.get('critical_duplications', 0)}")
    print(f"   Moyennes: {summary.get('medium_duplications', 0)}")
    
    # Grouper par type de duplication
    duplications_to_fix = []
    legitimate_duplications = []
    codemort_duplications = []
    
    for dup in report['duplications']:
        function_name = dup['function_name']
        occurrences = dup['occurrences']
        dup_type = dup.get('type', 'unknown')
        severity = dup.get('severity', 'medium')
        recommendation = dup.get('recommendation', '')
        reason = dup.get('reason', '')
        
        print(f"\n📋 Fonction: {function_name}")
        print(f"   Type: {dup_type.upper()}")
        print(f"   Nombre d'occurrences: {dup['count']}")
        print(f"   Sévérité: {severity}")
        
        if dup_type == 'to_fix':
            print(f"   🔧 RECOMMANDATION: {recommendation}")
        elif dup_type == 'legitimate':
            print(f"   ✅ RAISON: {reason}")
        
        for occ in occurrences:
            file_path = occ['file']
            print(f"   - {file_path}")
            
            # Vérifier si c'est dans codemort
            if 'codemort' in file_path:
                codemort_duplications.append({
                    'function': function_name,
                    'file': file_path,
                    'type': dup_type,
                    'severity': severity
                })
            elif dup_type == 'to_fix':
                duplications_to_fix.append({
                    'function': function_name,
                    'file': file_path,
                    'severity': severity,
                    'recommendation': recommendation
                })
            else:
                legitimate_duplications.append({
                    'function': function_name,
                    'file': file_path,
                    'type': dup_type,
                    'reason': reason
                })
    
    # Résumé final
    print(f"\n📊 RÉSUMÉ FINAL:")
    print("=" * 30)
    print(f"   Total duplications: {len(report['duplications'])}")
    print(f"   À corriger: {len(duplications_to_fix)}")
    print(f"   Légitimes: {len(legitimate_duplications)}")
    print(f"   Dans codemort: {len(codemort_duplications)}")
    
    if codemort_duplications:
        print(f"\n⚠️  DUPLICATIONS DANS CODEMORT (PROBLÈME!):")
        for dup in codemort_duplications:
            print(f"   - {dup['function']} dans {dup['file']}")
    
    if duplications_to_fix:
        print(f"\n🔧 DUPLICATIONS À CORRIGER:")
        for dup in duplications_to_fix:
            print(f"   - {dup['function']} dans {dup['file']} ({dup['severity']})")
            print(f"     💡 {dup['recommendation']}")
    
    if legitimate_duplications:
        print(f"\n✅ DUPLICATIONS LÉGITIMES:")
        for dup in legitimate_duplications:
            print(f"   - {dup['function']} dans {dup['file']} ({dup['reason']})")
    
    # Sauvegarder le rapport détaillé
    detailed_report = {
        'summary': {
            'total_duplications': len(report['duplications']),
            'duplications_to_fix': len(duplications_to_fix),
            'legitimate_duplications': len(legitimate_duplications),
            'codemort_duplications': len(codemort_duplications)
        },
        'duplications_to_fix': duplications_to_fix,
        'legitimate_duplications': legitimate_duplications,
        'codemort_duplications': codemort_duplications,
        'all_duplications': report['duplications']
    }
    
    report_file = Path("reports/latest/detailed_duplications_analysis.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(detailed_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Rapport détaillé sauvegardé: {report_file}")

if __name__ == "__main__":
    analyze_duplications_detailed()
