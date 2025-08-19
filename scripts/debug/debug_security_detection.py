#!/usr/bin/env python3
"""
Debug de la détection de sécurité pour comprendre les faux positifs
"""

import re
from pathlib import Path

# Patterns de détection actuels
patterns = [
    r'os\.system\s*\(\s*[^)]*\+\s*[^)]*\)',
    r'subprocess\.run\s*\(\s*[^)]*\+\s*[^)]*\+\s*[^)]*\)',
    r'subprocess\.Popen\s*\(\s*[^)]*\+\s*[^)]*\+\s*[^)]*\)',
    r'eval\s*\(\s*[^)]*\+\s*[^)]*\)',
    r'exec\s*\(\s*[^)]*\+\s*[^)]*\)',
]

# Fichiers à analyser
files_to_check = [
    "error_monitor.py",
    "backend/app/api/files.py",
    "backend/app/services/document_extractor_service.py",
    "backend/app/services/multimedia_service.py",
    "backend/app/services/streaming_service.py",
    "backend/app/services/video_converter_service.py",
]

print("🔍 DEBUG DE LA DÉTECTION DE SÉCURITÉ")
print("=" * 50)

for file_path in files_to_check:
    full_path = Path("..") / file_path
    if not full_path.exists():
        print(f"❌ Fichier non trouvé: {file_path}")
        continue
    
    print(f"\n📁 Analyse de: {file_path}")
    print("-" * 30)
    
    try:
        content = full_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for i, pattern in enumerate(patterns, 1):
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                
                print(f"Pattern {i}: {pattern}")
                print(f"  Ligne {line_num}: {line_content.strip()}")
                print(f"  Match: {match.group()}")
                print(f"  Position: {match.start()}-{match.end()}")
                print()
                
    except Exception as e:
        print(f"❌ Erreur lecture {file_path}: {e}")

