#!/usr/bin/env python3
"""
Test simple de get_extra_paths
"""

import sys
import json
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cy8_comfyui_customNode_call import ComfyUICustomNodeCaller


def test_get_extra_paths():
    """Test de la méthode get_extra_paths"""

    print("🗂️  Test de get_extra_paths...")

    try:
        caller = ComfyUICustomNodeCaller()

        result = caller.get_extra_paths()

        if result["error"]:
            print(f"❌ Erreur: {result}")
        else:
            print("✅ Chemins récupérés:")
            data = result["data"]

            print(f"📁 Racine ComfyUI: {data.get('comfyui_root', 'N/A')}")
            print(f"⚙️  Config: {data.get('config_path', 'N/A')}")

            if "extra_paths" in data:
                extra = data["extra_paths"]
                if "comfyui" in extra:
                    comfyui_paths = extra["comfyui"]
                    print("📂 Chemins de modèles:")
                    for key, path in comfyui_paths.items():
                        if key not in ["base_path", "is_default"]:
                            print(f"  • {key}: {path}")

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_get_extra_paths()
