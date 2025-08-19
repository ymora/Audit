#!/usr/bin/env python3
"""
Test de détection des subprocess pour comprendre les faux positifs
"""

import re

# Exemple de code sécurisé (bonne pratique)
secure_code = '''
subprocess.run([
    str(self.backend_path / "venv" / "Scripts" / "python.exe"), "main.py"
], cwd=self.backend_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

subprocess.run(["npm", "run", "dev"], cwd=self.frontend_path)

subprocess.run(["explorer", str(path)], check=True)

subprocess.run(["wmic", "logicaldisk", "where", f"DeviceID='{drive_letter}:'"])
'''

# Patterns de détection
patterns = [
    r'subprocess\.run\s*\(\s*[^)]*\+\s*[^)]*\)',
    r'subprocess\.Popen\s*\(\s*[^)]*\+\s*[^)]*\)',
]

# Patterns d'exclusion
exclusions = [
    r'subprocess\.run\s*\(\s*\[[^\]]+\]',
    r'subprocess\.Popen\s*\(\s*\[[^\]]+\]',
    r'subprocess\.run\s*\(\s*\[[^\]]+\],\s*cwd=',
    r'subprocess\.Popen\s*\(\s*\[[^\]]+\],\s*cwd=',
    r'subprocess\.run\s*\(\s*\[["\'](?:npm|pip|python|wmic|explorer|open|xdg-open)["\']',
    r'subprocess\.Popen\s*\(\s*\[["\'](?:npm|pip|python|wmic|explorer|open|xdg-open)["\']',
]

print("🔍 TEST DE DÉTECTION SUBPROCESS")
print("=" * 50)

print("\n📋 Code sécurisé à tester:")
print(secure_code)

print("\n🔍 Détection avec patterns:")
for i, pattern in enumerate(patterns, 1):
    matches = re.findall(pattern, secure_code)
    print(f"Pattern {i}: {pattern}")
    print(f"  Matches: {matches}")
    print()

print("\n🚫 Vérification des exclusions:")
for i, exclusion in enumerate(exclusions, 1):
    matches = re.findall(exclusion, secure_code)
    print(f"Exclusion {i}: {exclusion}")
    print(f"  Matches: {matches}")
    print()

# Test de logique combinée
print("\n🎯 LOGIQUE COMBINÉE:")
for line in secure_code.split('\n'):
    if 'subprocess' in line:
        print(f"\nLigne: {line.strip()}")
        
        # Vérifier si c'est détecté comme vulnérabilité
        is_vulnerable = False
        for pattern in patterns:
            if re.search(pattern, line):
                is_vulnerable = True
                print(f"  ❌ Détecté comme vulnérabilité par: {pattern}")
                break
        
        # Vérifier si c'est exclu
        is_excluded = False
        for exclusion in exclusions:
            if re.search(exclusion, line):
                is_excluded = True
                print(f"  ✅ Exclu par: {exclusion}")
                break
        
        if not is_vulnerable:
            print(f"  ✅ Pas détecté comme vulnérabilité")
        elif is_excluded:
            print(f"  ✅ Vulnérabilité exclue (faux positif)")
        else:
            print(f"  ❌ Vraie vulnérabilité détectée")

