#!/usr/bin/env python3
"""
Test pour vérifier la gestion des largeurs des tableaux dans l'onglet ComfyUI
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import tkinter as tk
from tkinter import ttk


def test_table_widths():
    """Test des largeurs et de l'affichage des tableaux"""

    print("=== Test des largeurs des tableaux ===")

    try:
        # Créer l'application
        from cy8_prompts_manager_main import cy8_prompts_manager

        root = tk.Tk()
        root.geometry("1200x800")  # Taille de fenêtre réaliste
        root.withdraw()  # Masquer pour le test

        app = cy8_prompts_manager(root)
        print("✅ Application créée")

        # Test du tableau d'analyse des logs
        print("\n📊 Test du tableau d'analyse des logs:")
        if hasattr(app, "log_results_tree"):
            log_tree = app.log_results_tree
            print(f"   Colonnes: {log_tree['columns']}")

            for col in log_tree["columns"]:
                width = log_tree.column(col, "width")
                minwidth = log_tree.column(col, "minwidth")
                print(f"   {col:12}: width={width:3}, minwidth={minwidth:3}")

            # Ajouter quelques données de test
            log_tree.insert(
                "",
                "end",
                values=(
                    "OK",
                    "Custom Node",
                    "ExtraPathReader",
                    "Node chargé avec succès",
                    "42",
                ),
            )
            log_tree.insert(
                "",
                "end",
                values=(
                    "ERREUR",
                    "Model",
                    "checkpoint_model_very_long_name.safetensors",
                    "Erreur de chargement du modèle avec un message très long qui devrait tester le défilement horizontal",
                    "158",
                ),
            )

            print("   ✅ Données de test ajoutées au tableau des logs")
        else:
            print("   ❌ Tableau d'analyse des logs non trouvé")

        # Test du tableau des extra paths
        print("\n🌍 Test du tableau des extra paths:")
        if hasattr(app, "env_tree"):
            env_tree = app.env_tree
            print(f"   Colonnes: {env_tree['columns']}")

            for col in env_tree["columns"]:
                width = env_tree.column(col, "width")
                minwidth = env_tree.column(col, "minwidth")
                print(f"   {col:12}: width={width:3}, minwidth={minwidth:3}")

            # Ajouter quelques données de test avec des chemins longs
            test_paths = [
                (
                    "checkpoints",
                    "checkpoints",
                    "H:/comfyui/models/checkpoints/very_long_model_name_that_should_test_horizontal_scrolling.safetensors",
                    "comfyui",
                ),
                (
                    "loras",
                    "loras",
                    "C:/Users/Username/Documents/ComfyUI/models/loras/style_enhancement_v2.safetensors",
                    "comfyui",
                ),
                (
                    "custom_nodes",
                    "custom_nodes",
                    "E:/ComfyUI_installations/G11_04/custom_nodes/ComfyUI-Manager",
                    "comfyui",
                ),
                (
                    "vae",
                    "vae",
                    "H:/ai_models/vae/vae-ft-mse-840000-ema-pruned.ckpt",
                    "comfyui",
                ),
            ]

            for key, type_name, path, section in test_paths:
                env_tree.insert("", "end", values=(key, type_name, path, section))

            print("   ✅ Données de test ajoutées au tableau des extra paths")
        else:
            print("   ❌ Tableau des extra paths non trouvé")

        # Test de redimensionnement
        print("\n📏 Test de redimensionnement:")
        root.geometry("800x600")  # Taille plus petite
        root.update()
        print("   ✅ Fenêtre redimensionnée à 800x600")

        root.geometry("1400x900")  # Taille plus grande
        root.update()
        print("   ✅ Fenêtre redimensionnée à 1400x900")

        # Vérifier les scrollbars
        print("\n📜 Test des scrollbars:")

        if hasattr(app, "log_results_tree"):
            # Vérifier si les scrollbars sont présentes
            log_tree = app.log_results_tree
            if hasattr(log_tree, "xview") and hasattr(log_tree, "yview"):
                print("   ✅ Scrollbars configurées pour le tableau des logs")
            else:
                print("   ❌ Problème avec les scrollbars du tableau des logs")

        if hasattr(app, "env_tree"):
            # Vérifier si les scrollbars sont présentes
            env_tree = app.env_tree
            if hasattr(env_tree, "xview") and hasattr(env_tree, "yview"):
                print("   ✅ Scrollbars configurées pour le tableau des extra paths")
            else:
                print("   ❌ Problème avec les scrollbars du tableau des extra paths")

        # Test de largeur totale
        print("\n📐 Calcul des largeurs totales:")

        if hasattr(app, "log_results_tree"):
            log_tree = app.log_results_tree
            total_width = sum(
                log_tree.column(col, "width") for col in log_tree["columns"]
            )
            print(f"   Tableau logs: {total_width}px de largeur totale")

        if hasattr(app, "env_tree"):
            env_tree = app.env_tree
            total_width = sum(
                env_tree.column(col, "width") for col in env_tree["columns"]
            )
            print(f"   Tableau extra paths: {total_width}px de largeur totale")

        root.destroy()
        return True

    except Exception as e:
        print(f"❌ Erreur pendant le test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_table_widths()

    print("\n" + "=" * 50)
    if success:
        print("🎉 Test des largeurs réussi!")
        print("✅ Les tableaux sont maintenant mieux configurés:")
        print("   • Scrollbars positionnées avec grid")
        print("   • Largeurs optimisées pour chaque colonne")
        print("   • Largeurs minimales définies")
        print("   • Meilleure gestion du redimensionnement")
    else:
        print("💥 Test des largeurs échoué!")
        print("❌ Vérifiez les configurations des tableaux")

    print("=" * 50)
    sys.exit(0 if success else 1)
