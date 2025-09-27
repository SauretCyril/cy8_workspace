#!/usr/bin/env python3
"""
Script pour exécuter tous les tests du projet cy8_workspace
"""

import os
import sys
import subprocess
from pathlib import Path

# Se placer dans le répertoire du script
script_dir = Path(__file__).parent
os.chdir(script_dir.parent)  # Retour au répertoire racine

def run_all_tests():
    """Exécuter tous les fichiers de test"""
    tests_dir = Path("tests")
    
    print("🧪 Exécution des tests cy8_workspace")
    print("=" * 40)
    
    test_files = list(tests_dir.glob("test_*.py"))
    
    if not test_files:
        print("❌ Aucun fichier de test trouvé")
        return
    
    print(f"📋 {len(test_files)} fichiers de test trouvés\n")
    
    results = []
    
    for test_file in sorted(test_files):
        print(f"▶️ Exécution de {test_file.name}...")
        
        try:
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"   ✅ {test_file.name} - RÉUSSI")
                results.append((test_file.name, "RÉUSSI", ""))
            else:
                print(f"   ❌ {test_file.name} - ÉCHEC")
                results.append((test_file.name, "ÉCHEC", result.stderr))
        
        except subprocess.TimeoutExpired:
            print(f"   ⏰ {test_file.name} - TIMEOUT")
            results.append((test_file.name, "TIMEOUT", ""))
        except Exception as e:
            print(f"   💥 {test_file.name} - ERREUR: {e}")
            results.append((test_file.name, "ERREUR", str(e)))
        
        print()
    
    # Résumé
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 20)
    
    success_count = sum(1 for _, status, _ in results if status == "RÉUSSI")
    
    for name, status, error in results:
        status_icon = "✅" if status == "RÉUSSI" else "❌"
        print(f"{status_icon} {name}: {status}")
        if error and status == "ÉCHEC":
            print(f"   └─ {error[:100]}...")
    
    print(f"\n🎯 Résultat global: {success_count}/{len(results)} tests réussis")
    
    return success_count == len(results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
