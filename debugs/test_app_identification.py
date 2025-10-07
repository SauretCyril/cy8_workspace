import sys
import os

# Ajouter le chemin src
sys.path.append('src')

def test_app_identification():
    """Test de l'identification dans l'application complète"""
    print('=== TEST APPLICATION IDENTIFICATION ===')

    try:
        # Simulation de l'environnement de l'application
        from cy8_prompts_manager_main import cy8_prompts_manager

        print('🔧 Création d\'une instance temporaire...')

        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Cacher

        # Créer instance minimale
        app = cy8_prompts_manager()
        app.root = root
        app.comfyui_config_id = tk.StringVar()
        app.current_environment_id = None

        # Label temporaire
        import tkinter.ttk as ttk
        app.config_info_label = ttk.Label(root, text="Test")

        print('✅ Instance créée')

        # Test de l'identification
        print('\n🔍 Test identification custom node uniquement...')
        try:
            app.identify_comfyui_environment()
            print(f'✅ Identification réussie !')
            print(f'Environment ID: {app.comfyui_config_id.get()}')

            if "H12" in app.comfyui_config_id.get():
                print('🎯 SUCCÈS: H12 détecté !')
            else:
                print(f'⚠️ Autre: {app.comfyui_config_id.get()}')

        except Exception as e:
            print(f'❌ Erreur identification: {e}')

        root.destroy()

    except Exception as e:
        print(f'❌ Erreur: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_app_identification()
