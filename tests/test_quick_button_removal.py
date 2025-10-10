#!/usr/bin/env python3
"""
Test rapide de suppression du bouton "Analyser environnement sélectionné"

Vérifie uniquement le contenu du fichier sans lancer l'application graphique.
"""

import sys
import os


def test_button_removal_in_file():
    """Test de suppression du bouton dans le fichier"""
    print("🧪 Test de suppression du bouton 'Analyser environnement sélectionné'")
    print("=" * 65)

    try:
        file_path = os.path.join(
            os.path.dirname(__file__), "..", "src", "cy8_prompts_manager_main.py"
        )

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tests_passed = 0
        total_tests = 4

        # Test 1: Vérifier que le texte du bouton n'existe plus
        print("\n🔍 Test 1: Vérification suppression du bouton...")
        if "Analyser environnement sélectionné" in content:
            print("❌ Le texte du bouton existe encore dans le fichier")
        else:
            print("✅ Le texte du bouton a été supprimé du fichier")
            tests_passed += 1

        # Test 2: Vérifier que la méthode analyze_selected_environment n'existe plus
        print(
            "\n🔍 Test 2: Vérification suppression de analyze_selected_environment..."
        )
        if "def analyze_selected_environment(" in content:
            print("❌ La méthode analyze_selected_environment existe encore")
        else:
            print("✅ La méthode analyze_selected_environment a été supprimée")
            tests_passed += 1

        # Test 3: Vérifier que simulate_log_analysis n'existe plus
        print("\n🔍 Test 3: Vérification suppression de simulate_log_analysis...")
        if "def simulate_log_analysis(" in content:
            print("❌ La méthode simulate_log_analysis existe encore")
        else:
            print("✅ La méthode simulate_log_analysis a été supprimée")
            tests_passed += 1

        # Test 4: Vérifier que les méthodes importantes existent toujours
        print("\n🔍 Test 4: Vérification des méthodes importantes...")

        required_methods = [
            "def refresh_environments(",
            "def on_environment_select(",
            "def load_environment_analysis_results(",
            "def analyze_comfyui_log(",
            "def identify_comfyui_environment(",
        ]

        all_present = True
        for method_signature in required_methods:
            if method_signature in content:
                method_name = method_signature.split("(")[0].replace("def ", "")
                print(f"  ✅ {method_name}")
            else:
                method_name = method_signature.split("(")[0].replace("def ", "")
                print(f"  ❌ {method_name}")
                all_present = False

        if all_present:
            tests_passed += 1
            print("✅ Toutes les méthodes importantes sont présentes")
        else:
            print("❌ Certaines méthodes importantes manquent")

        # Résumé
        print(f"\n🎯 RÉSUMÉ:")
        print(f"   Tests réussis: {tests_passed}/{total_tests}")
        print(f"   Taux de réussite: {(tests_passed/total_tests)*100:.1f}%")

        if tests_passed == total_tests:
            print("\n🏆 SUPPRESSION RÉUSSIE !")
            print("✅ Le bouton 'Analyser environnement sélectionné' a été supprimé")
            print("✅ Les méthodes associées ont été supprimées")
            print("✅ Les méthodes importantes sont conservées")
            print("\n💡 Maintenant, seul l'environnement identifié peut être analysé")
            return True
        else:
            print("\n❌ PROBLÈMES DÉTECTÉS")
            return False

    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_code_consistency():
    """Test de cohérence du code après suppression"""
    print("\n📋 Test de cohérence du code...")

    try:
        file_path = os.path.join(
            os.path.dirname(__file__), "..", "src", "cy8_prompts_manager_main.py"
        )

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Vérifier qu'il n'y a pas de références orphelines
        orphan_checks = [
            (
                "self.analyze_selected_environment",
                "Référence orpheline à analyze_selected_environment",
            ),
            (
                "self.simulate_log_analysis",
                "Référence orpheline à simulate_log_analysis",
            ),
        ]

        all_clean = True
        for check, description in orphan_checks:
            if check in content:
                print(f"❌ {description}")
                all_clean = False
            else:
                print(f"✅ Pas de {description.lower()}")

        # Vérifier que la structure setup_log_tab est cohérente
        if "def setup_log_tab(" in content:
            print("✅ La méthode setup_log_tab existe")

            # Extraire la méthode setup_log_tab
            start_marker = "def setup_log_tab("
            start_pos = content.find(start_marker)
            if start_pos != -1:
                # Trouver la fin de la méthode (prochaine def au même niveau d'indentation)
                method_content = content[start_pos:]
                lines = method_content.split("\n")
                method_lines = [lines[0]]  # La ligne de définition

                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == "":
                        method_lines.append(line)
                    elif line.startswith("    "):  # Contenu de la méthode (indentation)
                        method_lines.append(line)
                    elif line.startswith("def ") and not line.startswith(
                        "        "
                    ):  # Nouvelle méthode
                        break
                    else:
                        method_lines.append(line)

                method_text = "\n".join(method_lines)

                # Vérifier que Canvas est bien utilisé
                if "Canvas(" in method_text and "Scrollbar(" in method_text:
                    print("✅ Canvas et Scrollbar sont présents dans setup_log_tab")
                else:
                    print("⚠️ Canvas ou Scrollbar pourrait manquer dans setup_log_tab")
                    all_clean = False
        else:
            print("❌ La méthode setup_log_tab manque")
            all_clean = False

        return all_clean

    except Exception as e:
        print(f"❌ Erreur lors du test de cohérence: {e}")
        return False


def main():
    """Fonction principale de test rapide"""
    print("🚀 Test rapide de suppression du bouton d'analyse d'environnement")
    print("=" * 60)

    success1 = test_button_removal_in_file()
    success2 = test_code_consistency()

    if success1 and success2:
        print("\n🎉 TOUS LES TESTS RÉUSSIS !")
        print("✅ La suppression a été effectuée correctement")
        print("✅ Le code reste cohérent")
        print("\n📝 RÉSUMÉ DES MODIFICATIONS:")
        print("   • Bouton 'Analyser environnement sélectionné' supprimé")
        print("   • Méthode analyze_selected_environment() supprimée")
        print("   • Méthode simulate_log_analysis() supprimée")
        print("   • Méthodes importantes conservées")
        print("   • Interface Log avec Canvas/Scrollbar maintenue")
        return True
    else:
        print("\n❌ ÉCHEC DES TESTS")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
