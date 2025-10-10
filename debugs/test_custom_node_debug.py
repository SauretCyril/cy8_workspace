import sys
import os
import time
import requests
import json

# Ajouter le chemin src
sys.path.append('src')

def test_custom_node_debug():
    """Test debug du custom node"""
    print('=== DEBUG CUSTOM NODE ===')

    try:
        from cy8_comfyui_customNode_call import ComfyUICustomNodeCaller

        with ComfyUICustomNodeCaller() as caller:
            result = caller.call_custom_node("ExtraPathReader", {})
            print(f'Custom node result: {result}')

            if "prompt_id" in result:
                prompt_id = result["prompt_id"]
                print(f'Prompt ID: {prompt_id}')

                # Attendre l'exécution
                print('Attente 5 secondes...')
                time.sleep(5)

                # Récupérer l'historique directement
                try:
                    response = requests.get(f"http://127.0.0.1:8188/history/{prompt_id}")
                    if response.status_code == 200:
                        history = response.json()
                        print(f'Historique: {json.dumps(history, indent=2)}')
                    else:
                        print(f'Erreur historique: {response.status_code}')
                except Exception as e:
                    print(f'Erreur: {e}')

    except Exception as e:
        print(f'Erreur: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_custom_node_debug()
