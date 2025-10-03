#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test final de validation de la barre de défilement de l'onglet Log

Vérifie que toutes les fonctionnalités sont opérationnelles après l'ajout
de la barre de défilement globale.
"""

import unittest
import sys
import os

# Configuration de l'encodage pour Windows
if os.name == "nt":  # Windows
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestLogTabScrollbar(unittest.TestCase):
    """Tests pour la barre de défilement de l'onglet Log"""

    @classmethod
    def setUpClass(cls):
        """Configuration une seule fois pour tous les tests"""
        print("🧪 Tests de validation de la barre de défilement - Onglet Log")
        print("=" * 60)

    def setUp(self):
        """Configuration avant chaque test"""
        # Éviter l'affichage de l'interface
        import tkinter as tk

        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """Nettoyage après chaque test"""
        try:
            self.root.destroy()
        except:
            pass

    def test_application_import(self):
        """Test 1: Vérifier que l'application peut être importée"""
        print("📦 Test 1: Import de l'application...")
        try:
            from cy8_prompts_manager_main import cy8_prompts_manager

            print("  ✅ Import réussi")
            self.assertTrue(True)
        except ImportError as e:
            print(f"  ❌ Erreur d'import: {e}")
            self.fail(f"Impossible d'importer l'application: {e}")

    def test_log_tab_creation(self):
        """Test 2: Vérifier que l'onglet Log peut être créé"""
        print("🏗️ Test 2: Création de l'onglet Log...")
        try:
            from cy8_prompts_manager_main import cy8_prompts_manager
            import tkinter as tk
            from tkinter import ttk

            app = cy8_prompts_manager()
            test_frame = ttk.Frame(self.root)

            # Créer l'onglet Log
            app.setup_log_tab(test_frame)

            print("  ✅ Onglet Log créé avec succès")
            self.assertTrue(hasattr(app, "log_results_tree"))
            self.assertTrue(hasattr(app, "environments_tree"))

        except Exception as e:
            print(f"  ❌ Erreur lors de la création: {e}")
            self.fail(f"Impossible de créer l'onglet Log: {e}")

    def test_canvas_and_scrollbar(self):
        """Test 3: Vérifier la présence du Canvas et de la scrollbar"""
        print("🖼️ Test 3: Vérification Canvas et Scrollbar...")
        try:
            from cy8_prompts_manager_main import cy8_prompts_manager
            import tkinter as tk
            from tkinter import ttk

            app = cy8_prompts_manager()
            test_frame = ttk.Frame(self.root)

            # Créer l'onglet Log
            app.setup_log_tab(test_frame)

            # Vérifier la présence d'un Canvas (pour la scrollbar)
            canvas_found = False
            scrollbar_found = False

            def find_widgets(widget):
                nonlocal canvas_found, scrollbar_found

                if isinstance(widget, tk.Canvas):
                    canvas_found = True
                elif isinstance(widget, ttk.Scrollbar):
                    scrollbar_found = True

                try:
                    for child in widget.winfo_children():
                        find_widgets(child)
                except:
                    pass

            find_widgets(test_frame)

            print(f"  Canvas trouvé: {'✅' if canvas_found else '❌'}")
            print(f"  Scrollbar trouvée: {'✅' if scrollbar_found else '❌'}")

            self.assertTrue(canvas_found, "Canvas pour scrollbar non trouvé")
            self.assertTrue(scrollbar_found, "Scrollbar non trouvée")

        except Exception as e:
            print(f"  ❌ Erreur lors de la vérification: {e}")
            self.fail(f"Erreur Canvas/Scrollbar: {e}")

    def test_key_methods_exist(self):
        """Test 4: Vérifier que les méthodes clés existent"""
        print("🔧 Test 4: Vérification des méthodes clés...")
        try:
            from cy8_prompts_manager_main import cy8_prompts_manager

            app = cy8_prompts_manager()

            required_methods = [
                "setup_log_tab",
                "analyze_comfyui_log",
                "refresh_log_analysis",
                "filter_log_results",
                "refresh_environments",
                "on_environment_select",
                "check_log_file_status",
                "update_analysis_buttons_state",
            ]

            missing_methods = []
            for method_name in required_methods:
                if hasattr(app, method_name):
                    print(f"  ✅ {method_name}")
                else:
                    print(f"  ❌ {method_name}")
                    missing_methods.append(method_name)

            if missing_methods:
                self.fail(f"Méthodes manquantes: {missing_methods}")

        except Exception as e:
            print(f"  ❌ Erreur lors de la vérification des méthodes: {e}")
            self.fail(f"Erreur méthodes: {e}")

    def test_environment_integration(self):
        """Test 5: Vérifier l'intégration avec les environnements"""
        print("🌍 Test 5: Intégration environnements...")
        try:
            from cy8_prompts_manager_main import cy8_prompts_manager

            app = cy8_prompts_manager()

            # Vérifier les attributs d'environnement
            self.assertTrue(hasattr(app, "current_environment_id"))
            self.assertTrue(hasattr(app, "set_current_environment"))
            self.assertTrue(hasattr(app, "update_analysis_buttons_state"))

            print("  ✅ Attributs d'environnement présents")
            print("  ✅ Méthodes d'environnement présentes")

        except Exception as e:
            print(f"  ❌ Erreur environnements: {e}")
            self.fail(f"Erreur environnements: {e}")


def run_tests():
    """Exécuter tous les tests"""
    # Configuration de unittest pour être plus verbeux
    unittest.main(argv=[""], exit=False, verbosity=0)


if __name__ == "__main__":
    try:
        # Créer une suite de tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestLogTabScrollbar)

        # Exécuter les tests
        runner = unittest.TextTestRunner(verbosity=0, stream=sys.stdout)
        result = runner.run(suite)

        # Résumé final
        print(f"\n🎯 RÉSUMÉ FINAL:")
        print(f"   Tests exécutés: {result.testsRun}")
        print(
            f"   ✅ Réussites: {result.testsRun - len(result.failures) - len(result.errors)}"
        )
        print(f"   ❌ Échecs: {len(result.failures)}")
        print(f"   💥 Erreurs: {len(result.errors)}")

        if result.wasSuccessful():
            print(
                f"\n🏆 TOUS LES TESTS PASSÉS - La barre de défilement fonctionne correctement!"
            )
            sys.exit(0)
        else:
            print(f"\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Erreur lors de l'exécution des tests: {e}")
        sys.exit(1)
