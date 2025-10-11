#!/usr/bin/env python3
"""
Test de diagnostic pour comprendre pourquoi le tableau des extra paths ne se remplit pas
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def test_extra_paths_workflow():
    """Test complet du workflow de récupération des extra paths"""

    print("=== DIAGNOSTIC - Workflow Extra Paths ===")

    try:
        # 1. Tester la récupération des données
        print("\n1. Test de récupération des données depuis YAML...")

        import yaml

        config_path = "E:/Comfyui_G11/ComfyUI/extra_model_paths.yaml"

        if os.path.exists(config_path):
            print(f"✅ Fichier trouvé: {config_path}")

            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            print(f"📊 Contenu du fichier YAML:")
            print(f"   Type: {type(config)}")
            print(
                f"   Clés principales: {list(config.keys()) if isinstance(config, dict) else 'Non-dict'}"
            )

            if isinstance(config, dict):
                for key, value in config.items():
                    print(
                        f"   {key}: {type(value)} - {len(value) if isinstance(value, dict) else 'N/A'} entrées"
                    )
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            print(f"     {subkey}: {subvalue}")
        else:
            print(f"❌ Fichier non trouvé: {config_path}")
            return False

        # 2. Test du format attendu par set_extra_paths
        print("\n2. Test du format de données pour set_extra_paths...")

        extra_paths_data = {
            "comfyui_root": "E:/Comfyui_G11/ComfyUI",
            "config_path": config_path,
            "extra_paths": config,
        }

        print(f"📋 Format des données préparées:")
        print(f"   comfyui_root: {extra_paths_data['comfyui_root']}")
        print(f"   config_path: {extra_paths_data['config_path']}")
        print(f"   extra_paths: {type(extra_paths_data['extra_paths'])}")

        # 3. Test de stockage
        print("\n3. Test de stockage dans cy8_paths_manager...")

        from cy8_paths import set_extra_paths, get_all_extra_paths

        # Vider d'abord
        from cy8_paths import cy8_paths_manager

        cy8_paths_manager._extra_paths.clear()

        print("📤 Stockage des données...")
        set_extra_paths(extra_paths_data)

        # 4. Test de récupération
        print("\n4. Test de récupération des données stockées...")

        stored_paths = get_all_extra_paths()
        print(f"📥 Données récupérées:")
        print(f"   Type: {type(stored_paths)}")
        print(f"   Nombre d'entrées: {len(stored_paths)}")

        if stored_paths:
            for key, path_info in stored_paths.items():
                print(f"   {key}: {path_info}")
        else:
            print("   ❌ Aucune donnée récupérée")

        # 5. Test de la méthode refresh_env_data
        print("\n5. Test simulation de refresh_env_data...")

        if stored_paths:
            print("✅ Données disponibles pour l'affichage")
            for key, path_info in stored_paths.items():
                print(
                    f"   Ligne tableau: {key} | {path_info.get('type', 'N/A')} | {path_info.get('path', 'N/A')} | {path_info.get('section', 'N/A')}"
                )
            return True
        else:
            print("❌ Aucune donnée pour l'affichage")
            return False

    except Exception as e:
        print(f"❌ Erreur pendant le diagnostic: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_extra_paths_workflow()
    if success:
        print("\n🎉 Diagnostic réussi - Les données devraient s'afficher!")
    else:
        print("\n💥 Diagnostic échoué - Problème identifié")

    sys.exit(0 if success else 1)
