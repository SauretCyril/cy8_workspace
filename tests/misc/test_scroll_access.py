#!/usr/bin/env python3
"""
Test d'usage pour vérifier l'accessibilité du tableau des résultats
via la barre de défilement de l'onglet Log.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def test_scroll_to_results():
    """Test pour vérifier qu'on peut accéder au tableau des résultats"""
    print("🎯 Test d'accessibilité du tableau des résultats d'analyse")
    print("=" * 55)

    try:
        from cy8_prompts_manager_main import cy8_prompts_manager

        # Créer l'application de test
        root = tk.Tk()
        root.title("Test Scroll - Onglet Log")
        root.geometry("1200x800")

        # Créer l'application
        app = cy8_prompts_manager()
        app.root = root  # Remplacer la racine

        # Créer un notebook pour simuler l'onglet Log
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        log_tab = ttk.Frame(notebook)
        notebook.add(log_tab, text="📊 Log ComfyUI (Test)")

        # Configurer l'onglet Log
        app.setup_log_tab(log_tab)

        # Ajouter des données de test dans les environnements
        try:
            app.refresh_environments()
            print("✅ Environnements chargés")
        except:
            print("⚠️ Impossible de charger les environnements (normal en test)")

        # Simuler des données de test dans le tableau des résultats
        test_data = [
            (
                "2024-10-03 14:30:15",
                "ERREUR",
                "Custom Node",
                "node_missing.py",
                "Module non trouvé",
                "127",
            ),
            (
                "2024-10-03 14:30:16",
                "ATTENTION",
                "Model",
                "checkpoint.safetensors",
                "Fichier manquant",
                "203",
            ),
            ("2024-10-03 14:30:17", "OK", "Init", "ComfyUI", "Démarrage réussi", "45"),
            (
                "2024-10-03 14:30:18",
                "INFO",
                "API",
                "server.py",
                "Serveur démarré",
                "89",
            ),
            (
                "2024-10-03 14:30:19",
                "ERREUR",
                "Memory",
                "CUDA",
                "Mémoire insuffisante",
                "156",
            ),
        ]

        # Remplir le tableau avec des données de test
        for i, data in enumerate(test_data * 5):  # Multiplier pour avoir plus de lignes
            app.log_results_tree.insert("", "end", values=data, tags=(data[1],))

        print(
            f"✅ {len(test_data) * 5} lignes de test ajoutées au tableau des résultats"
        )

        # Mettre à jour le compteur
        app.log_results_count_label.config(
            text=f"{len(test_data) * 5} résultats de test"
        )

        # Instructions pour l'utilisateur
        instructions = """
🎮 INSTRUCTIONS DE TEST:

1. ✅ Vérifiez que l'onglet Log s'affiche correctement
2. 🖱️ Utilisez la molette de la souris pour faire défiler l'onglet
3. 📊 Vérifiez que vous pouvez voir toutes les sections:
   - Configuration du fichier log (en haut)
   - Actions d'analyse
   - Environnements ComfyUI
   - Résultats de l'analyse (en bas avec données de test)
4. 🔍 Double-cliquez sur une ligne du tableau pour voir les détails
5. ❌ Fermez cette fenêtre pour terminer le test

💡 Si vous pouvez voir le tableau des résultats en bas,
   la barre de défilement fonctionne correctement !
"""

        # Créer une fenêtre d'instructions
        instructions_window = tk.Toplevel(root)
        instructions_window.title("Instructions de test")
        instructions_window.geometry("500x400")
        instructions_window.transient(root)

        text_widget = tk.Text(
            instructions_window, wrap="word", font=("TkDefaultFont", 10)
        )
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", instructions)
        text_widget.config(state="disabled")

        # Bouton pour fermer les instructions
        ttk.Button(
            instructions_window,
            text="✅ J'ai compris",
            command=instructions_window.destroy,
        ).pack(pady=10)

        print("📋 Fenêtre de test ouverte avec instructions")
        print("🎯 Testez la barre de défilement et l'accès au tableau des résultats")

        # Démarrer l'interface de test
        root.mainloop()

        return True

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_scroll_to_results()
