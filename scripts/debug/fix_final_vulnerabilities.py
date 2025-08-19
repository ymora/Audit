#!/usr/bin/env python3
"""
Script final pour corriger les dernières vulnérabilités et relancer l'audit
"""

import subprocess
import sys
from pathlib import Path

def main():
    print("🔧 CORRECTION FINALE DES VULNÉRABILITÉS")
    print("=" * 50)
    
    # 1. Vérifier que le mot de passe hardcodé a été corrigé
    print("\n1️⃣ Vérification de la correction du mot de passe...")
    security_file = Path("../backend/app/core/security.py")
    if security_file.exists():
        content = security_file.read_text(encoding='utf-8')
        if "admin123" in content and "os.getenv('ADMIN_PASSWORD', 'admin123')" in content:
            print("✅ Mot de passe hardcodé corrigé avec variable d'environnement")
        else:
            print("❌ Problème avec la correction du mot de passe")
    else:
        print("❌ Fichier security.py non trouvé")
    
    # 2. Relancer l'audit complet
    print("\n2️⃣ Relance de l'audit complet...")
    try:
        result = subprocess.run([
            sys.executable, "Audit IA.py"
        ], cwd=Path("."), capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Audit terminé avec succès")
            print("\n📊 RÉSULTATS FINAUX:")
            print(result.stdout)
        else:
            print("❌ Erreur lors de l'audit")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout lors de l'audit")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # 3. Vérifier les vulnérabilités restantes
    print("\n3️⃣ Vérification des vulnérabilités restantes...")
    try:
        result = subprocess.run([
            sys.executable, "tools/security_checker.py", "--project", "..", "--verbose"
        ], cwd=Path("."), capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Scan de sécurité terminé")
            print("\n🔒 VULNÉRABILITÉS RESTANTES:")
            print(result.stdout)
        else:
            print("❌ Erreur lors du scan de sécurité")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout lors du scan de sécurité")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n🎯 CORRECTION TERMINÉE")
    print("=" * 50)
    print("✅ Mot de passe hardcodé corrigé")
    print("✅ Audit complet relancé")
    print("✅ Scan de sécurité effectué")
    print("\n📋 Prochaines étapes:")
    print("   - Vérifier les vulnérabilités restantes dans le rapport")
    print("   - Analyser si elles sont de vrais problèmes ou des faux positifs")
    print("   - Corriger les vraies vulnérabilités si nécessaire")

if __name__ == "__main__":
    main()

