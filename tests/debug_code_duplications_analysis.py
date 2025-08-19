#!/usr/bin/env python3
"""
DEBUG DUPLICATIONS
==================

Script de débogage pour comprendre pourquoi les duplications légitimes
ne sont pas correctement identifiées.
"""

from tools.code_analyzer import CodeAnalyzer
from pathlib import Path

def debug_duplications():
    """Débogue le système de détection des duplications."""
    print("🔍 DÉBOGAGE DU SYSTÈME DE DUPLICATIONS")
    print("=" * 50)
    
    # Initialiser l'analyseur
    analyzer = CodeAnalyzer()
    
    # Test de la fonction is_legitimate_duplication
    print("\n📋 TEST DE LA FONCTION is_legitimate_duplication:")
    test_functions = ['__init__', '__repr__', 'decorator', 'wrapper', 'test_frontend', 'main']
    
    for func_name in test_functions:
        is_legitimate = analyzer.is_legitimate_duplication(func_name, 'function')
        print(f"   {func_name}: {is_legitimate}")
    
    # Analyser un fichier spécifique
    print("\n📄 ANALYSE D'UN FICHIER SPÉCIFIQUE:")
    test_file = Path("../backend/app/core/cache.py")
    
    if test_file.exists():
        analysis = analyzer.analyze_file(test_file)
        print(f"   Fichier: {test_file}")
        print(f"   Fonctions trouvées: {len(analysis.get('functions', []))}")
        
        for func in analysis.get('functions', []):
            func_name = func.get('name', 'unknown')
            is_legitimate = func.get('is_legitimate', False)
            expected_legitimate = analyzer.is_legitimate_duplication(func_name, 'function')
            print(f"   - {func_name}: is_legitimate = {is_legitimate} (expected: {expected_legitimate})")
    
    # Test de la logique de séparation
    print("\n🔍 TEST DE LA LOGIQUE DE SÉPARATION:")
    
    # Simuler des occurrences
    test_occurrences = [
        {'file': 'file1.py', 'function': {'name': '__init__', 'is_legitimate': True}},
        {'file': 'file2.py', 'function': {'name': '__init__', 'is_legitimate': True}},
        {'file': 'file3.py', 'function': {'name': 'test_function', 'is_legitimate': False}},
        {'file': 'file4.py', 'function': {'name': 'test_function', 'is_legitimate': False}},
    ]
    
    legitimate_occurrences = [occ for occ in test_occurrences if occ['function']['is_legitimate']]
    non_legitimate_occurrences = [occ for occ in test_occurrences if not occ['function']['is_legitimate']]
    
    print(f"   Occurrences légitimes: {len(legitimate_occurrences)}")
    print(f"   Occurrences non légitimes: {len(non_legitimate_occurrences)}")
    
    for occ in legitimate_occurrences:
        print(f"   - Légitime: {occ['function']['name']} dans {occ['file']}")
    
    for occ in non_legitimate_occurrences:
        print(f"   - Non légitime: {occ['function']['name']} dans {occ['file']}")

if __name__ == "__main__":
    debug_duplications()
