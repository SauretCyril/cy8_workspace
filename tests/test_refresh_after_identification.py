#!/usr/bin/env python3
"""
Test pour vérifier que le tableau se remplit après identification
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import tkinter as tk
from tkinter import ttk
import threading
import time

def test_identification_and_refresh():
    """Test complet d'identification et rafraîchissement du tableau"""

    print("=== Test Identification et Rafraîchissement ===")

    try:
        # Créer l'application
        from cy8_prompts_manager_main import cy8_prompts_manager

        root = tk.Tk()
        root.withdraw()  # Masquer la fenêtre

        app = cy8_prompts_manager(root)
        print("✅ Application créée")

        # Vérifier l'état initial du tableau
        initial_items = app.env_tree.get_children()
        print(f"📊 État initial: {len(initial_items)} éléments")

        if initial_items:
            for item in initial_items:
                values = app.env_tree.item(item)['values']
                print(f"   Initial: {values}")

        # Simuler le stockage de données comme le ferait identify_comfyui_environment
        print("\n🔧 Simulation du stockage des extra paths...")

        from cy8_paths import set_extra_paths

        # Données de test (similaires à celles récupérées depuis ComfyUI)
        test_data = {
            'comfyui_root': 'E:/Comfyui_G11/ComfyUI',
            'config_path': 'E:/Comfyui_G11/ComfyUI/extra_model_paths.yaml',
            'extra_paths': {
                'comfyui': {
                    'base_path': 'G:/ComfyUI_G11/ComfyUI',
                    'checkpoints': 'H:/comfyui/models/checkpoints',
                    'embeddings': 'H:/comfyui/models/embeddings',
                    'loras': 'H:/comfyui/models/loras',
                    'custom_nodes': 'H:/comfyui/G11_04/custom_nodes',
                    'vae': 'H:/comfyui/models/vae'
                }
            }
        }

        # Stocker les données
        set_extra_paths(test_data)
        print("✅ Données stockées")

        # Appeler refresh_env_data directement
        print("🔄 Appel de refresh_env_data...")
        app.refresh_env_data()

        # Vérifier le résultat
        final_items = app.env_tree.get_children()
        print(f"📊 État final: {len(final_items)} éléments")

        if final_items:
            print("✅ Contenu du tableau après refresh:")
            for item in final_items:
                values = app.env_tree.item(item)['values']
                print(f"   {values[0]} | {values[1]} | {values[2]} | {values[3]}")
        else:
            print("❌ Tableau encore vide après refresh")

        # Vérifier les labels d'information
        if hasattr(app, 'env_config_id_label'):
            config_text = app.env_config_id_label.cget('text')
            print(f"🆔 Label ID Configuration: '{config_text}'")

        if hasattr(app, 'env_root_label'):
            root_text = app.env_root_label.cget('text')
            print(f"📁 Label Racine ComfyUI: '{root_text}'")

        root.destroy()

        # Résultats
        success = len(final_items) > 1  # Plus que juste le message par défaut
        return success

    except Exception as e:
        print(f"❌ Erreur pendant le test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_identification_and_refresh()
    if success:
        print("\n🎉 Test réussi - Le tableau se remplit correctement!")
    else:
        print("\n💥 Test échoué - Le tableau ne se remplit pas")

    sys.exit(0 if success else 1)
