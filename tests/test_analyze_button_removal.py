#!/usr/bin/env python3
"""
Test de suppression du bouton "Analyser environnement sélectionné"

Vérifie que le bouton et la méthode ont été supprimés et que
l'application fonctionne toujours correctement.
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_analyze_button_removal():
    """Test de suppression du bouton d'analyse d'environnement sélectionné"""
    print("🧪 Test de suppression du bouton 'Analyser environnement sélectionné'")
    print("=" * 65)

    try:
        from cy8_prompts_manager_main import cy8_prompts_manager
        import tkinter as tk

        # Créer une instance de l'application (sans interface graphique)
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre

        app = cy8_prompts_manager()
        app.root = root

        print("✅ Application créée avec succès")

        # Test 1: Vérifier que la méthode analyze_selected_environment n'existe plus
        print("\n🔍 Test 1: Vérification suppression de la méthode...")

        if hasattr(app, "analyze_selected_environment"):
            print("❌ La méthode analyze_selected_environment existe encore")
            return False
        else:
            print("✅ La méthode analyze_selected_environment a été supprimée")

        # Test 2: Vérifier que la méthode simulate_log_analysis n'existe plus
        print("\n🔍 Test 2: Vérification suppression de simulate_log_analysis...")

        if hasattr(app, "simulate_log_analysis"):
            print("❌ La méthode simulate_log_analysis existe encore")
            return False
        else:
            print("✅ La méthode simulate_log_analysis a été supprimée")

        # Test 3: Vérifier que les méthodes importantes existent toujours
        print("\n🔍 Test 3: Vérification des méthodes importantes...")

        required_methods = [
            "refresh_environments",
            "on_environment_select",
            "load_environment_analysis_results",
            "analyze_comfyui_log",
            "analyze_complete_log_global",
            "identify_comfyui_environment",
        ]

        all_present = True
        for method_name in required_methods:
            if hasattr(app, method_name):
                print(f"  ✅ {method_name}")
            else:
                print(f"  ❌ {method_name}")
                all_present = False

        if not all_present:
            print("❌ Certaines méthodes importantes manquent")
            return False

        # Test 4: Vérifier que l'onglet Log peut être configuré
        print("\n🔍 Test 4: Test de configuration de l'onglet Log...")

        try:
            test_frame = tk.Frame(root)
            app.setup_log_tab(test_frame)
            print("✅ L'onglet Log se configure correctement")
        except Exception as e:
            print(f"❌ Erreur lors de la configuration de l'onglet Log: {e}")
            return False

        # Test 5: Vérifier que les attributs d'environnement existent
        print("\n🔍 Test 5: Vérification des attributs d'environnement...")

        required_attrs = [
            "current_environment_id",
            "environments_tree",
            "log_results_tree",
        ]

        all_attrs_present = True
        for attr_name in required_attrs:
            if hasattr(app, attr_name):
                print(f"  ✅ {attr_name}")
            else:
                print(f"  ❌ {attr_name}")
                all_attrs_present = False

        if not all_attrs_present:
            print("❌ Certains attributs importants manquent")
            return False

        root.destroy()

        print("\n🏆 TOUS LES TESTS PASSÉS")
        print("✅ Le bouton et les méthodes ont été supprimés avec succès")
        print("✅ L'application reste fonctionnelle")
        return True

    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_file_content():
    """Test du contenu du fichier pour vérifier la suppression"""
    print("\n📄 Test du contenu du fichier...")

    try:
        file_path = os.path.join(
            os.path.dirname(__file__), "..", "src", "cy8_prompts_manager_main.py"
        )

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Vérifier que le texte du bouton n'existe plus
        if "Analyser environnement sélectionné" in content:
            print("❌ Le texte du bouton existe encore dans le fichier")
            return False
        else:
            print("✅ Le texte du bouton a été supprimé du fichier")

        # Vérifier que la méthode n'existe plus
        if "def analyze_selected_environment(" in content:
            print("❌ La méthode analyze_selected_environment existe encore")
            return False
        else:
            print("✅ La méthode analyze_selected_environment a été supprimée")

        # Vérifier que simulate_log_analysis n'existe plus
        if "def simulate_log_analysis(" in content:
            print("❌ La méthode simulate_log_analysis existe encore")
            return False
        else:
            print("✅ La méthode simulate_log_analysis a été supprimée")

        print("✅ Contenu du fichier correct")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier: {e}")
        return False


def main():
    """Fonction principale de test"""
    print("🚀 Test de suppression du bouton d'analyse d'environnement")
    print("=" * 60)

    success_count = 0
    total_tests = 2

    # Test 1: Vérification application
    if test_analyze_button_removal():
        success_count += 1
        print("\n✅ Test 1 RÉUSSI - Application fonctionnelle")
    else:
        print("\n❌ Test 1 ÉCHOUÉ")

    # Test 2: Vérification fichier
    if test_file_content():
        success_count += 1
        print("\n✅ Test 2 RÉUSSI - Fichier correct")
    else:
        print("\n❌ Test 2 ÉCHOUÉ")

    # Résumé final
    print(f"\n🎯 RÉSUMÉ FINAL:")
    print(f"   Tests réussis: {success_count}/{total_tests}")
    print(f"   Taux de réussite: {(success_count/total_tests)*100:.1f}%")

    if success_count == total_tests:
        print("\n🏆 SUPPRESSION RÉUSSIE !")
        print("✅ Le bouton 'Analyser environnement sélectionné' a été supprimé")
        print("✅ Les méthodes associées ont été supprimées")
        print("✅ L'application reste fonctionnelle")
        print("\n💡 Maintenant, seul l'environnement identifié peut être analysé")
        return True
    else:
        print("\n❌ PROBLÈMES DÉTECTÉS")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
