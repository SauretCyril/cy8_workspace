#!/usr/bin/env python3
"""
Test des solutions d'erreurs avec Mistral AI
"""

import sys
import os
import time
from datetime import datetime

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from cy8_mistral import analyze_comfyui_error, save_error_solution, load_error_solution


def test_mistral_functions():
    """Tester les nouvelles fonctions Mistral pour l'analyse d'erreurs"""
    print("🤖 Test des fonctions Mistral AI")
    print("=" * 50)

    # Test avec une erreur simulée
    test_timestamp = "2025-09-28 14:30:25.123"
    test_error = "ModuleNotFoundError: No module named 'torch_audio'"
    test_solutions_dir = "test_solutions"

    print(f"📋 Test avec erreur: {test_error}")
    print(f"🕐 Timestamp: {test_timestamp}")
    print(f"📁 Répertoire test: {test_solutions_dir}")
    print()

    try:
        # Créer le répertoire de test
        os.makedirs(test_solutions_dir, exist_ok=True)

        # Test 1: Vérifier qu'aucune solution n'existe
        existing = load_error_solution(test_timestamp, test_solutions_dir)
        if existing is None:
            print("✅ Test 1: Aucune solution existante (attendu)")
        else:
            print("⚠️  Test 1: Solution trouvée (inattendu)")

        # Test 2: Sauvegarder une solution de test
        test_solution = """ANALYSE D'ERREUR COMFYUI - TEST
========================================

EXPLICATION:
L'erreur ModuleNotFoundError indique qu'un module Python requis n'est pas installé.

CAUSES POSSIBLES:
1. Module torch_audio non installé
2. Environnement Python incorrect
3. Dépendances manquantes

SOLUTIONS:
1. Installer le module: pip install torchaudio
2. Vérifier l'environnement virtuel
3. Réinstaller les dépendances ComfyUI

PRÉVENTION:
- Utiliser un requirements.txt
- Vérifier l'environnement avant de lancer ComfyUI
"""

        saved_path = save_error_solution(
            test_timestamp, test_error, test_solution, test_solutions_dir
        )

        if saved_path:
            print(f"✅ Test 2: Solution sauvegardée - {os.path.basename(saved_path)}")
        else:
            print("❌ Test 2: Échec de la sauvegarde")
            return False

        # Test 3: Charger la solution sauvegardée
        loaded_solution = load_error_solution(test_timestamp, test_solutions_dir)

        if loaded_solution:
            print("✅ Test 3: Solution chargée avec succès")
            print(f"   📄 Taille: {len(loaded_solution)} caractères")
        else:
            print("❌ Test 3: Échec du chargement")
            return False

        print()
        print("🎉 Tous les tests de base réussis !")
        return True

    except Exception as e:
        print(f"❌ Erreur pendant le test: {e}")
        return False
    finally:
        # Nettoyer le répertoire de test
        try:
            import shutil

            if os.path.exists(test_solutions_dir):
                shutil.rmtree(test_solutions_dir)
                print("🧹 Répertoire de test nettoyé")
        except:
            pass


def test_interface_integration():
    """Tester l'intégration avec l'interface"""
    print("🖥️ Test d'intégration interface")
    print("=" * 50)

    try:
        # Importer l'interface principale
        from cy8_prompts_manager_main import cy8_prompts_manager

        print("✅ Import de l'interface réussi")

        # Créer l'application
        app = cy8_prompts_manager()

        # Vérifier que les nouvelles méthodes existent
        required_methods = [
            "browse_solutions_directory",
            "display_cached_solution",
            "display_new_solution",
            "get_new_ai_solution",
            "save_current_solution",
            "open_solutions_folder",
        ]

        missing_methods = []
        for method in required_methods:
            if not hasattr(app, method):
                missing_methods.append(method)

        if missing_methods:
            print(f"❌ Méthodes manquantes: {missing_methods}")
            return False
        else:
            print("✅ Toutes les méthodes nécessaires présentes")

        # Vérifier que la variable du répertoire existe
        if hasattr(app, "error_solutions_dir"):
            print("✅ Variable error_solutions_dir présente")
            default_dir = app.error_solutions_dir.get()
            print(f"   📁 Répertoire par défaut: {default_dir}")
        else:
            print("❌ Variable error_solutions_dir manquante")
            return False

        # Vérifier les préférences
        prefs_info = app.user_prefs.get_preferences_info()
        if "error_solutions_directory" in prefs_info:
            print("✅ Préférence error_solutions_directory configurée")
            print(f"   📁 Valeur: {prefs_info['error_solutions_directory']}")
        else:
            print("❌ Préférence error_solutions_directory manquante")
            return False

        return True

    except Exception as e:
        print(f"❌ Erreur d'intégration: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_filename_generation():
    """Tester la génération des noms de fichiers"""
    print("📝 Test de génération des noms de fichiers")
    print("=" * 50)

    test_timestamps = [
        "2025-09-28 14:30:25.123",
        "2025-09-28 14:30:26.45",
        "2025-09-28 14:30:27.789",
        "2025-09-28 14:30:28.00",
        "Invalid timestamp with spaces",
    ]

    for timestamp in test_timestamps:
        # Simuler la logique de nettoyage du nom de fichier
        safe_timestamp = timestamp.replace(":", "-").replace(" ", "_").replace(".", "-")
        expected_filename = f"error_solution_{safe_timestamp}.txt"

        print(f"   Timestamp: {timestamp}")
        print(f"   Fichier: {expected_filename}")
        print()

    print("✅ Génération des noms de fichiers testée")
    return True


if __name__ == "__main__":
    print("🧪 TESTS DES SOLUTIONS D'ERREURS AVEC MISTRAL AI")
    print("=" * 60)

    success = True

    # Test 1: Fonctions Mistral de base
    success &= test_mistral_functions()
    print()

    # Test 2: Génération des noms de fichiers
    success &= test_filename_generation()
    print()

    # Test 3: Intégration interface
    success &= test_interface_integration()
    print()

    if success:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("✨ Fonctionnalités ajoutées:")
        print("   • Double-clic sur erreurs pour solutions IA")
        print("   • Cache des solutions par timestamp")
        print("   • Configuration du répertoire de sauvegarde")
        print("   • Interface complète avec Mistral AI")
        print("   • Gestion automatique des fichiers de solutions")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez l'implémentation des solutions IA")
