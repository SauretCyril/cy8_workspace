#!/usr/bin/env python3
"""
Test de la classe cy8_paths_manager et de l'onglet Env
"""

import sys
import os

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def test_paths_manager():
    """Tester la classe cy8_paths_manager"""
    print("🧪 Test de cy8_paths_manager")
    print("=" * 40)

    try:
        from cy8_paths import (
            cy8_paths_manager,
            set_extra_paths,
            get_all_extra_paths,
            get_extra_path,
        )

        # Données de test simulant les extra paths ComfyUI
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
                    "vae": "H:/comfyui/models/vae",
                }
            },
        }

        print("📋 Données de test:")
        for key, value in test_data["extra_paths"]["comfyui"].items():
            if isinstance(value, str):
                print(f"  {key}: {value}")

        print("\n💾 Test de stockage des extra paths...")
        set_extra_paths(test_data)

        print("📂 Récupération de tous les paths...")
        all_paths = get_all_extra_paths()

        if all_paths:
            print(f"✅ {len(all_paths)} paths stockés:")
            for key, path_info in all_paths.items():
                print(f"  🔑 {key}: {path_info['type']} -> {path_info['path']}")
        else:
            print("❌ Aucun path stocké")
            return False

        print("\n🔍 Test de récupération par clé...")
        # Tester quelques clés
        test_keys = ["checkpoints", "G11_04", "models"]
        for key in test_keys:
            path_info = get_extra_path(key)
            if path_info:
                print(f"  ✅ {key}: {path_info['path']}")
            else:
                print(f"  ❌ {key}: non trouvé")

        print("\n🏷️ Test de filtrage par type...")
        checkpoints_paths = cy8_paths_manager.get_paths_by_type("checkpoints")
        print(f"  Paths de type 'checkpoints': {len(checkpoints_paths)}")

        loras_paths = cy8_paths_manager.get_paths_by_type("loras")
        print(f"  Paths de type 'loras': {len(loras_paths)}")

        print("\n🔍 Test de recherche...")
        search_results = cy8_paths_manager.find_paths_containing("H:/comfyui")
        print(f"  Paths contenant 'H:/comfyui': {len(search_results)}")

        print("\n✅ Test de cy8_paths_manager réussi !")
        return True

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_env_tab_integration():
    """Tester l'intégration avec l'onglet Env"""
    print("\n🧪 Test d'intégration onglet Env")
    print("=" * 40)

    try:
        from cy8_prompts_manager_main import cy8_prompts_manager
        import tkinter as tk

        # Créer une instance de l'application
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre
        app = cy8_prompts_manager(root)

        # Vérifier que l'onglet Env est créé
        if hasattr(app, "env_tree"):
            print("✅ Onglet Env créé avec succès")
            print("✅ TreeView env_tree disponible")
        else:
            print("❌ Onglet Env non créé")
            return False

        if hasattr(app, "refresh_env_data"):
            print("✅ Méthode refresh_env_data disponible")
        else:
            print("❌ Méthode refresh_env_data manquante")
            return False

        # Tester la méthode refresh_env_data
        print("🔄 Test de actualisation des données...")
        app.refresh_env_data()
        print("✅ Actualisation terminée")

        print("\n✅ Test d'intégration réussi !")
        return True

    except Exception as e:
        print(f"❌ Erreur lors du test d'intégration: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Tests de l'onglet Env et cy8_paths_manager")
    print("=" * 60)

    # Test 1: Classe cy8_paths_manager
    success1 = test_paths_manager()

    # Test 2: Intégration avec l'onglet Env
    success2 = test_env_tab_integration()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("💡 L'onglet Env est prêt à l'emploi")
    else:
        print("❌ Certains tests ont échoué")
    print("=" * 60)
