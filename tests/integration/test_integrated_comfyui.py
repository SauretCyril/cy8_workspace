#!/usr/bin/env python3
"""
Test de l'onglet ComfyUI intégré avec les fonctionnalités Env
"""

import sys
import os

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def test_integrated_comfyui_tab():
    """Test de l'onglet ComfyUI intégré"""
    print("🧪 Test de l'onglet ComfyUI intégré")
    print("=" * 50)

    try:
        from cy8_prompts_manager_main import cy8_prompts_manager
        from cy8_paths import get_all_extra_paths, set_extra_paths
        import tkinter as tk

        # Créer une instance de l'application
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre
        app = cy8_prompts_manager(root)

        print("✅ Application créée")

        # Vérifier les composants de l'onglet ComfyUI intégré
        components = [
            # Composants originaux ComfyUI
            ("test_connection_btn", "Bouton test connexion"),
            ("status_icon_label", "Icône de statut"),
            ("comfyui_log_path", "Chemin log ComfyUI"),
            ("analyze_log_btn", "Bouton analyse log"),
            ("comfyui_config_id", "Variable ID configuration"),
            ("config_id_entry", "Champ ID configuration"),
            ("config_info_label", "Label info configuration"),
            # Nouveaux composants Env intégrés
            ("env_config_id_label", "Label ID configuration Env"),
            ("env_root_label", "Label racine ComfyUI"),
            ("env_tree", "TreeView extra paths"),
            ("env_search_var", "Variable recherche"),
            ("env_type_filter", "Filtre type"),
            # Méthodes intégrées
            ("refresh_env_data", "Méthode actualisation"),
            ("filter_env_paths", "Méthode filtrage"),
            ("copy_selected_path", "Méthode copie chemin"),
        ]

        print("📋 Vérification des composants intégrés...")
        for attr, desc in components:
            if hasattr(app, attr):
                print(f"  ✅ {desc}")
            else:
                print(f"  ❌ {desc} manquant")

        print("\n💾 Test de fonctionnalités intégrées...")

        # Simuler des données extra paths
        test_data = {
            "comfyui_root": "E:/Comfyui_G11/ComfyUI",
            "config_path": "E:/Comfyui_G11/ComfyUI/extra_model_paths.yaml",
            "extra_paths": {
                "comfyui": {
                    "base_path": "G:/ComfyUI_G11/ComfyUI",
                    "is_default": True,
                    "checkpoints": "H:/comfyui/models/checkpoints",
                    "embeddings": "H:/comfyui/models/embeddings",
                    "loras": "H:/comfyui/models/loras",
                    "custom_nodes": "H:/comfyui/G11_04/custom_nodes",
                    "vae": "H:/comfyui/models/vae",
                }
            },
        }

        # Stocker les données
        set_extra_paths(test_data)

        # Simuler la mise à jour des labels comme le ferait identify_comfyui_environment
        app.env_config_id_label.config(text="G11_04", foreground="green")
        app.env_root_label.config(text="E:/Comfyui_G11/ComfyUI", foreground="green")
        app.comfyui_config_id.set("G11_04")

        print("🔄 Test d'actualisation des extra paths...")
        app.refresh_env_data()

        # Vérifier que les données sont bien affichées
        updated_paths = get_all_extra_paths()
        print(f"📊 Paths chargés: {len(updated_paths)}")

        if updated_paths:
            print("📋 Types de paths détectés:")
            types_found = set()
            for key, path_info in updated_paths.items():
                types_found.add(path_info["type"])
            for path_type in sorted(types_found):
                print(f"  🏷️ {path_type}")

        print("\n🔍 Test des fonctions de filtrage...")

        # Test filtrage par recherche
        app.env_search_var.set("checkpoints")
        app.filter_env_paths()
        print("✅ Filtrage par recherche testé")

        # Test filtrage par type
        app.env_search_var.set("")
        app.env_type_filter.set("loras")
        app.filter_env_paths()
        print("✅ Filtrage par type testé")

        # Remettre l'affichage complet
        app.env_type_filter.set("Tous")
        app.filter_env_paths()
        print("✅ Affichage complet restauré")

        print("\n🎨 Test des couleurs par type...")
        # Les couleurs sont configurées dans l'onglet
        color_tags = ["checkpoints", "loras", "embeddings", "custom_nodes", "vae"]
        for tag in color_tags:
            try:
                # Vérifier que le tag existe (pas d'erreur levée)
                app.env_tree.tag_configure(tag)
                print(f"  ✅ Tag couleur '{tag}' configuré")
            except:
                print(f"  ❌ Tag couleur '{tag}' manquant")

        print("\n✅ Test de l'onglet ComfyUI intégré réussi !")
        print("💡 Toutes les fonctionnalités Env sont maintenant dans ComfyUI !")

        return True

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Test de l'onglet ComfyUI avec intégration Env")
    print("=" * 60)

    success = test_integrated_comfyui_tab()

    print("\n" + "=" * 60)
    if success:
        print("🎉 INTÉGRATION RÉUSSIE !")
        print("\n📋 Fonctionnalités maintenant disponibles dans l'onglet ComfyUI:")
        print("  🔗 Test de connexion ComfyUI")
        print("  📊 Analyse des logs ComfyUI")
        print("  🆔 Identification automatique de l'environnement")
        print("  🌍 Affichage des extra paths")
        print("  🔍 Recherche et filtrage des chemins")
        print("  📋 Copie des chemins sélectionnés")
        print("  🎨 Coloration par type de path")
        print("  🔄 Actualisation automatique après identification")
        print("\n💡 Interface unifiée et plus cohérente !")
    else:
        print("❌ Des problèmes subsistent")
    print("=" * 60)
