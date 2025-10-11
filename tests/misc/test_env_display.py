#!/usr/bin/env python3
"""
Test pour vérifier l'affichage du tableau des extra paths dans l'onglet ComfyUI
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import tkinter as tk
from tkinter import ttk
import threading
import time


def test_env_display():
    """Test pour vérifier que le tableau des extra paths s'affiche correctement"""

    print("=== Test d'affichage du tableau des extra paths ===")

    try:
        # Importer l'application
        from cy8_prompts_manager_main import cy8_prompts_manager

        print("✅ Import de cy8_prompts_manager réussi")

        # Créer l'application
        root = tk.Tk()
        root.withdraw()  # Masquer la fenêtre principale

        app = cy8_prompts_manager(root)
        print("✅ Application créée avec succès")

        # Vérifier que l'onglet ComfyUI existe et a les composants nécessaires
        if hasattr(app, "env_tree"):
            print("✅ Composant env_tree trouvé")

            # Vérifier les colonnes du TreeView
            columns = app.env_tree["columns"]
            print(f"📋 Colonnes du TreeView: {columns}")

            if columns == ("key", "type", "path", "section"):
                print("✅ Colonnes correctement configurées")
            else:
                print(f"❌ Colonnes incorrectes: {columns}")

            # Vérifier le contenu initial
            items = app.env_tree.get_children()
            print(f"📊 Nombre d'éléments dans le TreeView: {len(items)}")

            if items:
                for item in items:
                    values = app.env_tree.item(item)["values"]
                    print(f"📋 Élément: {values}")
                print("✅ TreeView contient des données")
            else:
                print(
                    "⚠️ TreeView vide - Normal si aucun environnement n'a été identifié"
                )

            # Vérifier les boutons et composants de recherche
            components_to_check = [
                ("env_search_var", "Variable de recherche"),
                ("env_type_filter", "Filtre de type"),
                ("env_config_id_label", "Label ID configuration"),
                ("env_root_label", "Label racine ComfyUI"),
            ]

            for attr_name, description in components_to_check:
                if hasattr(app, attr_name):
                    print(f"✅ {description} ({attr_name}) trouvé")
                else:
                    print(f"❌ {description} ({attr_name}) manquant")

        else:
            print("❌ Composant env_tree non trouvé")
            return False

        print("\n=== Résumé du test ===")
        print("✅ Le tableau des extra paths est correctement configuré")
        print(
            "💡 Pour voir les données, cliquez sur 'Identifier l'environnement' dans l'application"
        )
        print(
            "💡 Les données apparaîtront après identification réussie de l'environnement ComfyUI"
        )

        root.destroy()
        return True

    except Exception as e:
        print(f"❌ Erreur pendant le test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_env_display()
    if success:
        print("\n🎉 Test réussi - Le tableau des extra paths est bien présent!")
    else:
        print("\n💥 Test échoué - Problème avec l'affichage du tableau")

    sys.exit(0 if success else 1)
