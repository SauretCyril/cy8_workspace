import requests
import json

def debug_comfyui_custom_node():
    """Débugger directement le custom node ExtraPathReader via l'API ComfyUI"""
    print('=== DEBUG CUSTOM NODE VIA API ===')

    # Workflow de test avec debug et sortie
    workflow = {
        "1": {
            "class_type": "ExtraPathReader",
            "inputs": {}
        },
        "2": {
            "class_type": "PythonPathNode",
            "inputs": {}
        },
        "3": {
            "class_type": "PreviewAny",
            "inputs": {
                "source": ["1", 0]
            }
        },
        "4": {
            "class_type": "PreviewAny",
            "inputs": {
                "source": ["2", 0]
            }
        }
    }

    try:
        # Appeler ComfyUI
        response = requests.post(
            "http://127.0.0.1:8188/prompt",
            json={"prompt": workflow},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            prompt_id = result.get("prompt_id")
            print(f'✅ Workflow envoyé, prompt_id: {prompt_id}')

            # Attendre et récupérer les résultats
            import time
            time.sleep(3)

            # Récupérer l'historique
            history_response = requests.get(f"http://127.0.0.1:8188/history/{prompt_id}")
            if history_response.status_code == 200:
                history = history_response.json()
                print('\n📋 RÉSULTATS:')

                for node_id, node_result in history.items():
                    if 'outputs' in node_result:
                        outputs = node_result['outputs']
                        print(f'\nNode {node_id}:')
                        for output_key, output_data in outputs.items():
                            if isinstance(output_data, list) and len(output_data) > 0:
                                print(f'  {output_key}: {output_data[0][:200]}...')
            else:
                print(f'❌ Erreur récupération historique: {history_response.status_code}')

        else:
            print(f'❌ Erreur API: {response.status_code}')
            print(f'Response: {response.text}')

    except Exception as e:
        print(f'❌ Erreur: {e}')

if __name__ == "__main__":
    debug_comfyui_custom_node()
