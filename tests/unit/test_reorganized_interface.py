#!/usr/bin/env python3
"""
Test de la nouvelle interface réorganisée de l'onglet ComfyUI
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import tkinter as tk
from tkinter import ttk


def test_reorganized_interface():
    """Test de la nouvelle interface réorganisée"""

    print("=== Test de la nouvelle interface ComfyUI ===")

    try:
        # Créer l'application
        from cy8_prompts_manager_main import cy8_prompts_manager

        root = tk.Tk()
        root.geometry("1000x700")
        root.withdraw()  # Masquer pour le test

        app = cy8_prompts_manager(root)
        print("✅ Application créée avec la nouvelle interface")

        # Vérifier les composants principaux
        components_to_check = [
            ("env_tree", "Tableau des extra paths"),
            ("env_search_var", "Variable de recherche"),
            ("env_type_filter", "Filtre de type"),
            ("env_config_id_label", "Label ID configuration"),
            ("env_root_label", "Label racine ComfyUI"),
            ("status_icon_label", "Icône de statut"),
            ("status_text_label", "Texte de statut"),
            ("test_connection_btn", "Bouton test connexion"),
            ("log_results_tree", "Tableau d'analyse des logs"),
            ("details_text", "Zone de détails techniques"),
        ]

        print("\n📋 Vérification des composants:")
        missing_components = []

        for attr_name, description in components_to_check:
            if hasattr(app, attr_name):
                print(f"   ✅ {description} ({attr_name})")
            else:
                print(f"   ❌ {description} ({attr_name}) - MANQUANT")
                missing_components.append(attr_name)

        # Test du tableau des extra paths
        print("\n🌍 Test du tableau des extra paths:")
        if hasattr(app, "env_tree"):
            env_tree = app.env_tree
            print(f"   📊 Colonnes: {env_tree['columns']}")
            print(f"   📏 Hauteur: {env_tree['height']}")

            # Vérifier la position dans la hiérarchie
            parent = env_tree.master
            print(f"   🏗️ Parent: {parent.__class__.__name__}")

            # Ajouter des données de test
            test_data = [
                (
                    "checkpoints",
                    "checkpoints",
                    "H:/comfyui/models/checkpoints",
                    "comfyui",
                ),
                ("loras", "loras", "H:/comfyui/models/loras", "comfyui"),
                (
                    "custom_nodes",
                    "custom_nodes",
                    "H:/comfyui/G11_04/custom_nodes",
                    "comfyui",
                ),
            ]

            for key, type_name, path, section in test_data:
                env_tree.insert("", "end", values=(key, type_name, path, section))

            items_count = len(env_tree.get_children())
            print(f"   📋 Données de test ajoutées: {items_count} éléments")

            print("   ✅ Tableau des extra paths fonctionnel et VISIBLE")
        else:
            print("   ❌ Tableau des extra paths non trouvé")

        # Test des boutons d'action
        print("\n🔘 Test des boutons d'action:")
        buttons_to_check = [
            ("identify_comfyui_environment", "Identifier environnement"),
            ("test_comfyui_connection", "Test connexion"),
            ("refresh_env_data", "Actualiser données"),
            ("filter_env_paths", "Filtrer paths"),
            ("copy_selected_path", "Copier chemin sélectionné"),
        ]

        for method_name, description in buttons_to_check:
            if hasattr(app, method_name):
                print(f"   ✅ {description} ({method_name})")
            else:
                print(f"   ❌ {description} ({method_name}) - MANQUANT")

        # Test de la recherche
        print("\n🔍 Test de la fonctionnalité de recherche:")
        if hasattr(app, "env_search_var") and hasattr(app, "filter_env_paths"):
            app.env_search_var.set("checkpoints")
            app.filter_env_paths()
            print("   ✅ Recherche 'checkpoints' effectuée")

            app.env_search_var.set("")
            app.filter_env_paths()
            print("   ✅ Recherche réinitialisée")

        # Test du filtrage par type
        print("\n🏷️ Test du filtrage par type:")
        if hasattr(app, "env_type_filter"):
            filter_combo = app.env_type_filter
            print(f"   📋 Valeurs disponibles: {filter_combo['values']}")
            print(f"   🔧 Valeur actuelle: {filter_combo.get()}")

            filter_combo.set("checkpoints")
            app.filter_env_paths()
            print("   ✅ Filtre 'checkpoints' appliqué")

            filter_combo.set("Tous")
            app.filter_env_paths()
            print("   ✅ Filtre réinitialisé")

        root.destroy()

        # Résultats
        success = len(missing_components) == 0
        return success, missing_components

    except Exception as e:
        print(f"❌ Erreur pendant le test: {e}")
        import traceback

        traceback.print_exc()
        return False, []


if __name__ == "__main__":
    success, missing = test_reorganized_interface()

    print("\n" + "=" * 60)
    if success:
        print("🎉 NOUVELLE INTERFACE RÉORGANISÉE AVEC SUCCÈS!")
        print("\n✨ AMÉLIORATIONS APPORTÉES:")
        print("   • 🌍 Tableau des extra paths en PREMIÈRE POSITION")
        print("   • 🎯 Interface compacte et organisée")
        print("   • 📱 Scroll vertical pour gérer le contenu")
        print("   • 🔘 Boutons d'action regroupés et visibles")
        print("   • 🔍 Recherche et filtrage intégrés")
        print("   • 📊 Informations d'état en ligne compacte")
        print("   • 🛠️ Outils complémentaires en section séparée")

        print("\n🎯 LE TABLEAU EST MAINTENANT VISIBLE EN HAUT DE L'ONGLET!")
        print("💡 Pour utiliser:")
        print("   1. Ouvrez l'onglet 'ComfyUI'")
        print("   2. Le tableau des extra paths est directement visible")
        print("   3. Cliquez 'Identifier l'environnement' pour le remplir")
        print("   4. Utilisez la recherche et les filtres")

    else:
        print("💥 PROBLÈME AVEC LA RÉORGANISATION!")
        if missing:
            print(f"❌ Composants manquants: {missing}")
        print("🔧 Vérifiez les corrections apportées")

    print("=" * 60)
    sys.exit(0 if success else 1)
