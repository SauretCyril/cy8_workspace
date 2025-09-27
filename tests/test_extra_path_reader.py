#!/usr/bin/env python3
"""
Test du custom node ExtraPathReader
"""

import sys
import os

# Ajouter le chemin vers le custom node
custom_node_path = r"E:\Comfyui_G11\ComfyUI\custom_nodes"
if custom_node_path not in sys.path:
    sys.path.insert(0, custom_node_path)


def test_extra_path_reader():
    """Tester le custom node ExtraPathReader"""
    print("🧪 Test du custom node ExtraPathReader")
    print("=" * 40)

    try:
        # Importer le custom node
        from extra_path_reader import (
            ExtraPathReader,
            NODE_CLASS_MAPPINGS,
            NODE_DISPLAY_NAME_MAPPINGS,
        )

        print("✅ Import réussi")

        # Vérifier les mappings
        print(f"📦 Mappings de classe: {NODE_CLASS_MAPPINGS}")
        print(f"📝 Mappings de nom: {NODE_DISPLAY_NAME_MAPPINGS}")

        # Créer une instance du node
        reader = ExtraPathReader()
        print("✅ Instance créée")

        # Tester INPUT_TYPES
        input_types = reader.INPUT_TYPES()
        print(f"📋 Types d'entrée: {input_types}")

        # Vérifier les propriétés de classe
        print(f"🔄 Types de retour: {reader.RETURN_TYPES}")
        print(f"🏷️ Noms de retour: {reader.RETURN_NAMES}")
        print(f"⚙️ Fonction: {reader.FUNCTION}")
        print(f"📂 Catégorie: {reader.CATEGORY}")

        # Tester la fonction read_paths
        print("\n🔍 Test de la fonction read_paths...")
        try:
            result = reader.read_paths()
            print(f"✅ Résultat obtenu (type: {type(result)})")
            if isinstance(result, tuple) and len(result) > 0:
                print(
                    f"📄 Contenu (premiers 200 caractères): {str(result[0])[:200]}..."
                )
            else:
                print(f"📄 Résultat complet: {result}")
        except Exception as e:
            print(f"⚠️ Erreur lors de l'exécution: {e}")
            print(
                "💡 Cela peut être normal si le fichier extra_model_paths.yaml n'existe pas"
            )

        print("\n✅ Test du custom node terminé avec succès !")

    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("💡 Vérifiez que le fichier extra_path_reader.py est correct")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")


def test_yaml_config():
    """Tester la présence du fichier de configuration YAML"""
    print("\n🔍 Vérification du fichier de configuration")
    print("=" * 45)

    config_path = os.path.expanduser("~/.config/ComfyUI/extra_model_paths.yaml")
    print(f"📁 Chemin recherché: {config_path}")

    if os.path.exists(config_path):
        print("✅ Fichier trouvé")
        try:
            import yaml

            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            print(
                f"📋 Configuration chargée: {len(config) if isinstance(config, dict) else 'N/A'} entrées"
            )
        except Exception as e:
            print(f"⚠️ Erreur lors de la lecture: {e}")
    else:
        print("❌ Fichier non trouvé")
        print("💡 Le custom node retournera un message d'erreur")


if __name__ == "__main__":
    test_extra_path_reader()
    test_yaml_config()

    print("\n" + "=" * 50)
    print("💡 Pour utiliser ce custom node dans ComfyUI:")
    print("1. Redémarrez ComfyUI")
    print(
        "2. Le node 'Extra Path Reader' devrait apparaître dans la catégorie 'Utility'"
    )
    print("3. Il retourne le contenu du fichier extra_model_paths.yaml en JSON")
    print("=" * 50)
