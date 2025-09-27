#!/usr/bin/env python3
"""
Debug du fichier extra_model_paths.yaml
"""

import yaml
import os

def debug_extra_paths():
    """Debug du contenu des extra paths"""
    print("🔍 Debug du fichier extra_model_paths.yaml")
    print("=" * 45)

    config_path = "E:/Comfyui_G11/ComfyUI/extra_model_paths.yaml"

    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()

        print("📄 Contenu brut du fichier:")
        print(content)
        print("\n" + "="*30)

        try:
            config = yaml.safe_load(content)
            print("📋 Structure analysée:")
            print(f"Type: {type(config)}")

            if isinstance(config, dict):
                for key, value in config.items():
                    print(f"Clé: '{key}' -> Type: {type(value)}")
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            print(f"  └─ '{sub_key}': {sub_value}")
                            if "custom_nodes" in str(sub_value):
                                print(f"     🎯 TROUVÉ custom_nodes dans: {sub_value}")
                    else:
                        print(f"  └─ Valeur: {value}")
                        if "custom_nodes" in str(value):
                            print(f"     🎯 TROUVÉ custom_nodes dans: {value}")
        except Exception as e:
            print(f"❌ Erreur de parsing: {e}")
    else:
        print("❌ Fichier non trouvé")

if __name__ == "__main__":
    debug_extra_paths()
