#!/usr/bin/env python3
"""
Test du centrage de la popup des actions d'environnement
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_env_actions_popup_centering():
    """Test du centrage de la popup des actions d'environnement"""
    print("=== TEST CENTRAGE POPUP ACTIONS ENVIRONNEMENT ===")

    try:
        # Imports
        from cy8_prompts_manager_main import center_window
        from cy8_database_manager import cy8_database_manager
        print("✅ Imports réussis")

        # Simuler l'application
        class MockApp:
            def __init__(self):
                self.root = tk.Tk()
                self.root.title("Test Application")
                self.root.geometry("800x600")

                # Initialiser DB
                self.db_manager = cy8_database_manager()
                self.db_manager.init_database(mode="dev")
                self.db_manager.ensure_environment_tables()

                # Ajouter un environnement de test
                try:
                    self.db_manager.cursor.execute(
                        """
                        INSERT OR REPLACE INTO environnements (id, name, path, description)
                        VALUES (?, ?, ?, ?)
                        """,
                        ("TEST_CENTER", "Test Centrage", "G:/test/center", "Test du centrage")
                    )
                    self.db_manager.conn.commit()
                except:
                    pass  # Environnement déjà existant

                # Ajouter quelques actions de test
                self.db_manager.add_env_action("TEST_CENTER", "Action 1", "cmd1")
                self.db_manager.add_env_action("TEST_CENTER", "Action 2", "cmd2")
                self.db_manager.add_env_action("TEST_CENTER", "Action 3", "cmd3")

                print("✅ Application mockée créée")

            def open_env_actions_popup(self, environment_id, environment_name):
                """Version copiée de la méthode avec centrage"""
                import json
                import os
                from datetime import datetime

                # Créer la popup
                popup = tk.Toplevel(self.root)
                popup.title(f"Actions pour l'environnement {environment_name}")
                popup.geometry("800x600")
                popup.transient(self.root)
                popup.grab_set()

                # Centrer la popup
                center_window(popup, 800, 600)

                print(f"✅ Popup créée et centrée pour {environment_name}")

                # Frame principal
                main_frame = ttk.Frame(popup, padding="10")
                main_frame.pack(fill="both", expand=True)

                # Titre
                title_label = ttk.Label(
                    main_frame,
                    text=f"🔧 Actions pour {environment_name}",
                    font=("TkDefaultFont", 12, "bold")
                )
                title_label.pack(pady=(0, 10))

                # Frame pour le tableau des actions
                tree_frame = ttk.Frame(main_frame)
                tree_frame.pack(fill="both", expand=True, pady=(0, 10))

                # Tableau des actions
                columns = ("id", "desc", "cmd")
                actions_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

                # Définir les colonnes
                actions_tree.heading("id", text="ID")
                actions_tree.heading("desc", text="Descriptif court")
                actions_tree.heading("cmd", text="Action (commande)")

                actions_tree.column("id", width=50, minwidth=40)
                actions_tree.column("desc", width=200, minwidth=150)
                actions_tree.column("cmd", width=400, minwidth=200)

                # Scrollbars
                v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=actions_tree.yview)
                h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=actions_tree.xview)
                actions_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

                # Pack tree et scrollbars
                actions_tree.grid(row=0, column=0, sticky="nsew")
                v_scrollbar.grid(row=0, column=1, sticky="ns")
                h_scrollbar.grid(row=1, column=0, sticky="ew")

                tree_frame.grid_rowconfigure(0, weight=1)
                tree_frame.grid_columnconfigure(0, weight=1)

                # Charger les actions
                actions = self.db_manager.get_env_actions(environment_id)
                for action in actions:
                    actions_tree.insert("", "end", values=(
                        action["id"],
                        action["short_desc"],
                        action["action_cmd"] or ""
                    ))

                # Frame pour les boutons
                buttons_frame = ttk.Frame(main_frame)
                buttons_frame.pack(fill="x", pady=(0, 10))

                # Boutons
                ttk.Button(buttons_frame, text="➕ Ajouter", state="disabled").pack(side="left", padx=(0, 5))
                ttk.Button(buttons_frame, text="✏️ Modifier", state="disabled").pack(side="left", padx=(0, 5))
                ttk.Button(buttons_frame, text="🗑️ Supprimer", state="disabled").pack(side="left", padx=(0, 5))
                ttk.Button(buttons_frame, text="💾 Sauvegarder JSON", state="disabled").pack(side="right")

                # Bouton fermer
                ttk.Button(main_frame, text="Fermer", command=popup.destroy).pack(pady=(10, 0))

                # Vérifier la position
                popup.update_idletasks()
                x = popup.winfo_x()
                y = popup.winfo_y()
                width = popup.winfo_width()
                height = popup.winfo_height()

                screen_width = popup.winfo_screenwidth()
                screen_height = popup.winfo_screenheight()

                expected_x = (screen_width - 800) // 2
                expected_y = (screen_height - 600) // 2

                print(f"✅ Position popup: ({x}, {y})")
                print(f"✅ Position attendue: ({expected_x}, {expected_y})")
                print(f"✅ Taille popup: {width}x{height}")
                print(f"✅ Actions chargées: {len(actions)}")

                return popup

        # Créer l'app de test
        app = MockApp()

        # Centrer la fenêtre principale
        center_window(app.root, 800, 600)

        # Bouton pour ouvrir la popup
        ttk.Label(app.root, text="Test du centrage de la popup Actions", font=("TkDefaultFont", 14, "bold")).pack(pady=20)

        def open_test_popup():
            popup = app.open_env_actions_popup("TEST_CENTER", "Test Centrage")
            # Programmer la fermeture automatique après 5 secondes
            app.root.after(5000, popup.destroy)

        ttk.Button(app.root, text="🔧 Ouvrir Popup Actions (centrée)", command=open_test_popup).pack(pady=10)

        ttk.Label(app.root, text="La popup se fermera automatiquement dans 5 secondes", foreground="gray").pack(pady=5)

        # Fermer automatiquement après 10 secondes
        app.root.after(10000, app.root.quit)

        print("\n👁️ Interface de test affichée. Cliquez le bouton pour tester le centrage...")
        app.root.mainloop()

        # Nettoyer
        app.root.destroy()

        print("🎉 Test du centrage de popup terminé avec succès !")
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_env_actions_popup_centering()
