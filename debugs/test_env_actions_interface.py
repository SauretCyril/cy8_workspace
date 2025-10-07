#!/usr/bin/env python3
"""
Test complet de la fonctionnalité Actions d'environnement avec interface
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_env_actions_interface():
    """Test de l'interface des actions d'environnement"""
    print("=== TEST INTERFACE ACTIONS D'ENVIRONNEMENT ===")

    try:
        # Import des modules
        from cy8_database_manager import cy8_database_manager
        from cy8_prompts_manager_main import cy8_prompts_manager
        print("✅ Imports réussis")

        # Créer une instance simplifiée pour tester les méthodes
        class TestApp:
            def __init__(self):
                self.db_manager = cy8_database_manager()
                self.db_manager.init_database(mode="dev")
                self.db_manager.ensure_environment_tables()
                self.root = tk.Tk()
                self.root.withdraw()  # Cacher la fenêtre principale

                # Créer un environnement de test s'il n'existe pas
                existing_envs = self.db_manager.get_all_environments()
                test_env_exists = any(env[0] == "TEST_H12" for env in existing_envs)

                if not test_env_exists:
                    # Ajouter l'environnement de test
                    try:
                        self.db_manager.cursor.execute(
                            """
                            INSERT INTO environnements (id, name, path, description)
                            VALUES (?, ?, ?, ?)
                            """,
                            ("TEST_H12", "Test H12", "G:/test/h12", "Environnement de test")
                        )
                        self.db_manager.conn.commit()
                        print("✅ Environnement de test créé")
                    except Exception as e:
                        print(f"⚠️ Environnement de test déjà existant ou erreur: {e}")

        app = TestApp()

        # Test 1: Ajouter une action
        print("\n--- Test 1: Ajout d'action ---")
        action_id = app.db_manager.add_env_action("TEST_H12", "Démarrer ComfyUI", "python main.py --port 8188")
        print(f"✅ Action ajoutée: {action_id}")

        # Test 2: Récupérer les actions
        print("\n--- Test 2: Récupération des actions ---")
        actions = app.db_manager.get_env_actions("TEST_H12")
        print(f"✅ Actions trouvées: {len(actions)}")
        for action in actions:
            print(f"  - ID: {action['id']}, Desc: {action['short_desc']}, Cmd: {action['action_cmd']}")

        # Test 3: Tester la méthode get_environment_analyses_directory
        print("\n--- Test 3: Répertoire d'analyses ---")
        analyses_dir = app.db_manager.get_environment_analyses_directory("TEST_H12")
        print(f"✅ Répertoire d'analyses: {analyses_dir}")

        # Test 4: Test des méthodes de l'interface (si elles existent)
        print("\n--- Test 4: Méthodes d'interface ---")
        # Simuler l'ajout des méthodes d'interface à notre objet test
        from cy8_prompts_manager_main import cy8_prompts_manager

        # Vérifier que les méthodes existent
        methods_to_check = [
            'add_env_action_dialog',
            'edit_env_action_dialog',
            'delete_env_action_dialog',
            'save_env_actions_json',
            'open_env_actions_popup'
        ]

        for method_name in methods_to_check:
            if hasattr(cy8_prompts_manager, method_name):
                print(f"✅ Méthode trouvée: {method_name}")
            else:
                print(f"❌ Méthode manquante: {method_name}")

        # Test 5: Nettoyage
        print("\n--- Test 5: Nettoyage ---")
        for action in actions:
            app.db_manager.delete_env_action(action['id'])
        print("✅ Actions supprimées")

        # Fermer proprement
        app.root.destroy()
        print("\n🎉 Tests terminés avec succès !")
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_env_actions_interface()
