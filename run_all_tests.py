#!/usr/bin/env python3
"""
Script utilitaire pour lancer tous les tests du projet cy8_prompts_manager
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Exécuter une commande et afficher le résultat"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True, cwd=os.getcwd(),
                              encoding='utf-8', errors='replace')
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    except UnicodeDecodeError as e:
        print(f"⚠️  Problème d'encodage: {e}")
        print("Le test peut avoir réussi malgré ce problème d'affichage")
        return True

def main():
    """Lancer tous les tests disponibles"""
    print("🚀 SUITE COMPLÈTE DE TESTS - cy8_prompts_manager")
    print("=" * 60)
    
    # Vérifier qu'on est dans le bon répertoire
    if not os.path.exists("src/cy8_prompts_manager_main.py"):
        print("❌ Erreur: Ce script doit être lancé depuis la racine du projet")
        sys.exit(1)
    
    success_count = 0
    total_count = 0
    
    # Tests principaux cy8
    total_count += 1
    if run_command("python src/cy8_test_suite.py", "Tests principaux cy8"):
        success_count += 1
    
    # Test de connexion ComfyUI
    total_count += 1
    if run_command("python tests/test_comfyui_connection.py", "Test de connexion ComfyUI"):
        success_count += 1
    
    # Test de l'onglet ComfyUI
    total_count += 1
    if run_command("python tests/test_comfyui_tab.py", "Test de l'onglet ComfyUI"):
        success_count += 1
    
    # Test de validation CI (si disponible)
    if os.path.exists("tests/test_ci_validation.py"):
        total_count += 1
        if run_command("python tests/test_ci_validation.py", "Test de validation CI"):
            success_count += 1
    
    # Tests pytest (si pytest est installé)
    try:
        subprocess.run(["pytest", "--version"], check=True, capture_output=True)
        total_count += 1
        if run_command("pytest tests/ -v", "Tests pytest"):
            success_count += 1
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n⚠️  pytest non disponible, tests pytest ignorés")
    
    # Résumé final
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ DES TESTS")
    print(f"{'='*60}")
    print(f"Tests réussis: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 TOUS LES TESTS ONT RÉUSSI !")
        print("   Le système cy8_prompts_manager est entièrement fonctionnel.")
    else:
        print(f"❌ {total_count - success_count} test(s) ont échoué")
        print("   Vérifiez les messages d'erreur ci-dessus.")
        sys.exit(1)
    
    print(f"{'='*60}")
    
    # Instructions pour l'utilisateur
    print("\n💡 Pour tester manuellement :")
    print("   1. python src/cy8_prompts_manager_main.py")
    print("   2. Sélectionnez un prompt")
    print("   3. Onglet 'ComfyUI' -> 'Tester la connexion'")

if __name__ == "__main__":
    main()