import os
import sys

def debug_custom_node_location():
    """Débugger l'emplacement du custom node pour comprendre le problème"""
    print('=== DEBUG CUSTOM NODE LOCATION ===')

    # Simuler le comportement du custom node
    current_file = r"g:\G_WCS\cy8_workspace\custom_nodes\extra_path_reader.py"
    print(f'📍 Fichier custom node: {current_file}')

    current_path = os.path.dirname(current_file)
    print(f'📂 Dossier custom_nodes: {current_path}')

    # Simuler la logique _find_comfyui_root()
    print('\n🔍 SIMULATION _find_comfyui_root():')
    search_path = current_path
    step = 0

    while search_path and search_path != os.path.dirname(search_path):
        step += 1
        print(f'Étape {step}: {search_path}')

        # Vérifier la présence de fichiers/dossiers typiques de ComfyUI
        main_py = os.path.join(search_path, "main.py")
        custom_nodes = os.path.join(search_path, "custom_nodes")
        models = os.path.join(search_path, "models")

        print(f'  main.py: {"✅" if os.path.exists(main_py) else "❌"} {main_py}')
        print(f'  custom_nodes/: {"✅" if os.path.exists(custom_nodes) else "❌"} {custom_nodes}')
        print(f'  models/: {"✅" if os.path.exists(models) else "❌"} {models}')

        if (os.path.exists(main_py) and
            os.path.exists(custom_nodes) and
            os.path.exists(models)):
            print(f'🎯 RACINE COMFYUI TROUVÉE: {search_path}')

            # Vérifier le fichier de config
            config_path = os.path.join(search_path, "extra_model_paths.yaml")
            print(f'⚙️ Config attendu: {config_path}')
            print(f'⚙️ Config existe: {"✅" if os.path.exists(config_path) else "❌"}')

            return search_path

        search_path = os.path.dirname(search_path)

        if step > 10:  # Sécurité
            break

    print('❌ Aucune racine ComfyUI trouvée')
    return None

def check_actual_comfyui_roots():
    """Vérifier où sont les vraies installations ComfyUI"""
    print('\n=== VRAIES INSTALLATIONS COMFYUI ===')

    comfyui_locations = [
        'E:/Comfyui_G11/ComfyUI',
        'E:/Comfyui_H12/ComfyUI',
        'H:/ComfyUI'
    ]

    for location in comfyui_locations:
        if os.path.exists(location):
            print(f'\n📂 {location}:')

            main_py = os.path.join(location, "main.py")
            custom_nodes = os.path.join(location, "custom_nodes")
            models = os.path.join(location, "models")
            config = os.path.join(location, "extra_model_paths.yaml")

            print(f'  main.py: {"✅" if os.path.exists(main_py) else "❌"}')
            print(f'  custom_nodes/: {"✅" if os.path.exists(custom_nodes) else "❌"}')
            print(f'  models/: {"✅" if os.path.exists(models) else "❌"}')
            print(f'  config: {"✅" if os.path.exists(config) else "❌"}')

            # Vérifier si notre custom node est présent
            our_custom_node = os.path.join(custom_nodes, "extra_path_reader.py")
            print(f'  notre custom node: {"✅" if os.path.exists(our_custom_node) else "❌"}')

if __name__ == "__main__":
    debug_custom_node_location()
    check_actual_comfyui_roots()
