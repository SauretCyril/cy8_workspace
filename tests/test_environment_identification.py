#!/usr/bin/env python3
"""
Test de la nouvelle fonctionnalité d'identification d'environnement ComfyUI
"""

import sys
import os

sys.path.append("../src")

from cy8_comfyui_customNode_call import ComfyUICustomNodeCaller


def test_environment_identification():
    """Tester l'identification d'environnement ComfyUI"""
    print("🧪 Test d'identification d'environnement ComfyUI")
    print("=" * 50)

    try:
        # Test de connexion à ComfyUI
        print("1. Test de connexion à ComfyUI...")
        with ComfyUICustomNodeCaller() as caller:
            status = caller.get_server_status()
            print(f"   📡 Statut: {status['status']}")

            if status["status"] == "online":
                print("   ✅ ComfyUI accessible")

                # Test des custom nodes disponibles
                print("\n2. Vérification du custom node ExtraPathReader...")
                try:
                    custom_nodes = caller.get_available_custom_node_types()
                    if "ExtraPathReader" in custom_nodes:
                        print("   ✅ ExtraPathReader trouvé dans les custom nodes")

                        # Test d'appel du custom node
                        print("\n3. Test d'appel du custom node...")
                        result = caller.call_custom_node(
                            node_type="ExtraPathReader", inputs={}
                        )
                        print(f"   📄 Résultat: {result}")

                        if "prompt_id" in result:
                            print("   ✅ Custom node exécuté avec succès")
                        else:
                            print("   ⚠️ Résultat inattendu du custom node")

                    else:
                        print("   ❌ ExtraPathReader non trouvé dans les custom nodes")
                        print(f"   📋 Custom nodes disponibles: {len(custom_nodes)}")

                except Exception as e:
                    print(f"   ❌ Erreur lors de la vérification: {e}")
            else:
                print(
                    f"   ❌ ComfyUI inaccessible: {status.get('error', 'Erreur inconnue')}"
                )

    except Exception as e:
        print(f"❌ Erreur de test: {e}")


def test_extra_paths_detection():
    """Tester la détection des extra paths"""
    print("\n🔍 Test de détection des extra paths")
    print("=" * 40)

    # Test de lecture directe du fichier de configuration
    import yaml

    possible_paths = [
        os.path.expanduser("~/.config/ComfyUI/extra_model_paths.yaml"),
        os.path.expanduser("~/ComfyUI/extra_model_paths.yaml"),
        "E:/Comfyui_G11/ComfyUI/extra_model_paths.yaml",
        "C:/ComfyUI/extra_model_paths.yaml",
    ]

    for i, config_path in enumerate(possible_paths, 1):
        print(f"{i}. Test du chemin: {config_path}")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                print(f"   ✅ Fichier trouvé et lu")
                print(
                    f"   📋 Contenu: {list(config.keys()) if isinstance(config, dict) else 'Format inattendu'}"
                )

                # Test d'extraction d'ID
                config_id = extract_config_id_from_extra_paths(config)
                if config_id:
                    print(f"   🆔 ID extrait: '{config_id}'")
                else:
                    print("   ⚠️ Aucun ID extrait")
                break
            except Exception as e:
                print(f"   ❌ Erreur de lecture: {e}")
        else:
            print("   ❌ Fichier non trouvé")
    else:
        print("\n⚠️ Aucun fichier de configuration trouvé")


def extract_config_id_from_extra_paths(extra_paths_config):
    """Fonction utilitaire pour extraire l'ID"""
    if not extra_paths_config or not isinstance(extra_paths_config, dict):
        return None

    import re

    # Chercher dans toutes les valeurs de configuration
    for key, paths in extra_paths_config.items():
        if isinstance(paths, dict):
            for path_key, path_value in paths.items():
                if isinstance(path_value, str) and "custom_nodes" in path_value:
                    pattern = r".*[/\\]([^/\\]+)[/\\]ComfyUI[/\\]custom_nodes"
                    match = re.search(pattern, path_value, re.IGNORECASE)
                    if match:
                        return match.group(1)
        elif isinstance(paths, str) and "custom_nodes" in paths:
            pattern = r".*[/\\]([^/\\]+)[/\\]ComfyUI[/\\]custom_nodes"
            match = re.search(pattern, paths, re.IGNORECASE)
            if match:
                return match.group(1)

    return None


if __name__ == "__main__":
    test_environment_identification()
    test_extra_paths_detection()

    print("\n" + "=" * 50)
    print("💡 Pour tester dans l'application:")
    print("1. Lancez python main.py")
    print("2. Allez dans l'onglet ComfyUI")
    print("3. Cliquez sur 'Identifier l'environnement'")
    print("4. L'ID devrait s'afficher automatiquement")
    print("=" * 50)
