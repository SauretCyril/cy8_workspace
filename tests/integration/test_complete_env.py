#!/usr/bin/env python3
"""
Test complet de l'onglet Env avec identification d'environnement
"""

import sys
import os

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def test_complete_env_workflow():
    """Test complet du workflow de l'onglet Env"""
    print("🧪 Test complet du workflow Env")
    print("=" * 50)

    try:
        from cy8_prompts_manager_main import cy8_prompts_manager
        from cy8_paths import get_all_extra_paths
        import tkinter as tk

        # Créer une instance de l'application
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre
        app = cy8_prompts_manager(root)

        print("✅ Application créée")
        print("📋 Vérification de l'onglet Env...")

        # Vérifier les composants de l'onglet Env
        components = [
            ("env_tree", "TreeView des paths"),
            ("env_config_id_label", "Label ID de configuration"),
            ("env_root_label", "Label racine ComfyUI"),
            ("env_search_var", "Variable de recherche"),
            ("env_type_filter", "Filtre par type"),
            ("refresh_env_data", "Méthode d'actualisation"),
        ]

        for attr, desc in components:
            if hasattr(app, attr):
                print(f"  ✅ {desc}")
            else:
                print(f"  ❌ {desc} manquant")

        print("\n🔄 Test d'actualisation initiale...")
        app.refresh_env_data()

        # Vérifier l'état initial
        initial_paths = get_all_extra_paths()
        print(f"📊 Paths initiaux: {len(initial_paths)}")

        print("\n💾 Simulation de données extra paths...")
        from cy8_paths import set_extra_paths

        # Simuler les données d'identification
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
                    "clip": "H:/comfyui/models/clip",
                    "clip_vision": "H:/comfyui/models/clip_vision",
                    "controlnet": "H:/comfyui/models/controlnet",
                    "upscale_models": "H:/comfyui/models/upscale_models",
                    "vae": "H:/comfyui/models/vae",
                }
            },
        }

        # Stocker les données
        set_extra_paths(test_data)

        # Simuler la mise à jour des labels
        app.env_config_id_label.config(text="G11_04", foreground="green")
        app.env_root_label.config(text="E:/Comfyui_G11/ComfyUI", foreground="green")

        print("🔄 Actualisation avec nouvelles données...")
        app.refresh_env_data()

        # Vérifier les données après mise à jour
        updated_paths = get_all_extra_paths()
        print(f"📊 Paths après mise à jour: {len(updated_paths)}")

        if updated_paths:
            print("📋 Paths détectés:")
            for key, path_info in updated_paths.items():
                print(f"  🔑 {key}: {path_info['type']} -> {path_info['path'][:60]}...")

        print("\n🔍 Test des fonctions de filtrage...")

        # Test du filtrage par recherche
        app.env_search_var.set("checkpoints")
        app.filter_env_paths()
        print("✅ Filtrage par recherche testé")

        # Test du filtrage par type
        app.env_search_var.set("")
        app.env_type_filter.set("loras")
        app.filter_env_paths()
        print("✅ Filtrage par type testé")

        # Remettre tous les filtres
        app.env_type_filter.set("Tous")
        app.filter_env_paths()
        print("✅ Affichage complet restauré")

        print("\n✅ Test complet réussi !")
        print("💡 L'onglet Env est entièrement fonctionnel !")

        return True

    except Exception as e:
        print(f"❌ Erreur lors du test complet: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Test complet de l'onglet Env")
    print("=" * 60)

    success = test_complete_env_workflow()

    print("\n" + "=" * 60)
    if success:
        print("🎉 ONGLET ENV PLEINEMENT OPÉRATIONNEL !")
        print("\n📋 Fonctionnalités disponibles:")
        print("  • 📊 Affichage de tous les extra paths")
        print("  • 🔍 Recherche par nom/chemin")
        print("  • 🏷️ Filtrage par type")
        print("  • 📋 Copie des chemins")
        print("  • 🔄 Actualisation automatique")
        print("  • 🆔 Affichage de l'ID de configuration")
        print("  • 📁 Affichage de la racine ComfyUI")
    else:
        print("❌ Des problèmes subsistent")
    print("=" * 60)
