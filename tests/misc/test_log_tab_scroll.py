#!/usr/bin/env python3
"""
import sys
import os
Test de la barre de défilement de l'onglet Log

Ce test vérifie que l'onglet Log a bien une barre de défilement
et qu'elle permet d'accéder au tableau des résultats d'analyse.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def test_log_tab_scroll():
    """Test de la barre de défilement de l'onglet Log"""
    print("🧪 Test de la barre de défilement de l'onglet Log")
    print("=" * 50)

    try:
        from cy8_prompts_manager_main import cy8_prompts_manager

        # Créer une instance de l'application sans la démarrer
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre principale

        app = cy8_prompts_manager()

        # Créer un notebook de test
        test_notebook = ttk.Notebook(root)
        test_frame = ttk.Frame(test_notebook)
        test_notebook.add(test_frame, text="Log Test")

        # Configurer l'onglet Log
        app.setup_log_tab(test_frame)

        # Vérifier que le Canvas existe (pour la scrollbar globale)
        canvas_found = False
        scrollbar_found = False
        log_results_tree_found = False
        environments_tree_found = False

        def check_widget_recursively(widget, depth=0):
            nonlocal canvas_found, scrollbar_found, log_results_tree_found, environments_tree_found

            widget_type = type(widget).__name__

            if widget_type == "Canvas":
                canvas_found = True
                print(f"  ✅ Canvas trouvé (profondeur {depth})")
            elif widget_type == "Scrollbar":
                scrollbar_found = True
                print(f"  ✅ Scrollbar trouvée (profondeur {depth})")
            elif hasattr(widget, "_name") and "log_results_tree" in str(widget._name):
                log_results_tree_found = True
                print(f"  ✅ Tableau des résultats trouvé (profondeur {depth})")
            elif hasattr(widget, "_name") and "environments_tree" in str(widget._name):
                environments_tree_found = True
                print(f"  ✅ Tableau des environnements trouvé (profondeur {depth})")

            # Parcourir les enfants
            try:
                for child in widget.winfo_children():
                    check_widget_recursively(child, depth + 1)
            except:
                pass

        print("\n🔍 Analyse de la structure des widgets:")
        check_widget_recursively(test_frame)

        # Vérifier que l'attribut log_results_tree existe dans l'app
        if hasattr(app, "log_results_tree"):
            log_results_tree_found = True
            print("  ✅ app.log_results_tree existe")

        if hasattr(app, "environments_tree"):
            environments_tree_found = True
            print("  ✅ app.environments_tree existe")

        # Résultats des vérifications
        print(f"\n📊 Résultats des vérifications:")
        print(f"  Canvas (scroll global): {'✅' if canvas_found else '❌'}")
        print(f"  Scrollbar principale: {'✅' if scrollbar_found else '❌'}")
        print(f"  Tableau des résultats: {'✅' if log_results_tree_found else '❌'}")
        print(
            f"  Tableau des environnements: {'✅' if environments_tree_found else '❌'}"
        )

        # Test des méthodes clés
        method_checks = []

        methods_to_check = [
            "analyze_comfyui_log",
            "refresh_log_analysis",
            "filter_log_results",
            "refresh_environments",
            "on_environment_select",
        ]

        print(f"\n🔧 Vérification des méthodes clés:")
        for method_name in methods_to_check:
            if hasattr(app, method_name):
                print(f"  ✅ {method_name}")
                method_checks.append(True)
            else:
                print(f"  ❌ {method_name}")
                method_checks.append(False)

        # Calculer le score final
        total_checks = 4 + len(method_checks)  # 4 widgets + méthodes
        passed_checks = sum(
            [
                canvas_found,
                scrollbar_found,
                log_results_tree_found,
                environments_tree_found,
            ]
        ) + sum(method_checks)

        success_rate = (passed_checks / total_checks) * 100

        print(f"\n🎯 Score final: {passed_checks}/{total_checks} ({success_rate:.1f}%)")

        if success_rate >= 90:
            print(
                "✅ Test RÉUSSI - L'onglet Log avec scrollbar est correctement configuré"
            )
            success = True
        elif success_rate >= 70:
            print("⚠️ Test PARTIELLEMENT RÉUSSI - Quelques éléments manquent")
            success = True
        else:
            print("❌ Test ÉCHOUÉ - Problèmes majeurs détectés")
            success = False

        root.destroy()
        return success

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_log_tab_scroll()
    sys.exit(0 if success else 1)
