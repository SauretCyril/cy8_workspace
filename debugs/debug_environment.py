#!/usr/bin/env python3
"""
Test de debug pour vérifier l'état de l'environnement
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_environment_status():
    """Test simple pour vérifier l'état de l'environnement"""
    print("🔍 === DEBUG ENVIRONNEMENT ===")

    # Importer cy8_paths pour voir l'état des extra paths
    try:
        from cy8_paths import get_all_extra_paths

        # Vérifier les extra paths
        all_paths = get_all_extra_paths()
        print(f"📁 Extra paths disponibles: {len(all_paths) if all_paths else 0}")

        if all_paths:
            print("📋 Extra paths trouvés:")
            for key, path_info in list(all_paths.items())[:5]:  # Premiers 5
                print(f"   - {key}: {path_info.get('path', 'N/A')}")

        # Vérifier la racine ComfyUI
        comfyui_info = all_paths.get('comfyui_root') if all_paths else None
        if comfyui_info:
            print(f"🏠 Racine ComfyUI: {comfyui_info}")

    except Exception as e:
        print(f"❌ Erreur import cy8_paths: {e}")

    # Vérifier si le fichier de configuration existe
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"📄 Fichier .env trouvé")
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if 'COMFYUI_CONFIG_ID' in content:
                    for line in content.split('\n'):
                        if 'COMFYUI_CONFIG_ID' in line:
                            print(f"   {line}")
        except Exception as e:
            print(f"❌ Erreur lecture .env: {e}")
    else:
        print("❌ Fichier .env non trouvé")

    print("\n🔧 Recommandations:")
    print("1. Lancez l'application")
    print("2. Allez dans l'onglet ComfyUI")
    print("3. Cliquez sur 'Identifier l'environnement'")
    print("4. Vérifiez que l'ID s'affiche")

if __name__ == "__main__":
    test_environment_status()
