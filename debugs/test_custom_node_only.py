import sys
import os

# Ajouter le chemin src
sys.path.append('src')

def test_identification_custom_node_only():
    """Test de l'identification uniquement via custom node"""
    print('=== TEST IDENTIFICATION CUSTOM NODE UNIQUEMENT ===')

    try:
        # Import minimal pour test
        from cy8_comfyui_customNode_call import ComfyUICustomNodeCaller

        print('🔧 Test du custom node ExtraPathReader...')

        with ComfyUICustomNodeCaller() as caller:
            # Vérifier le statut
            status = caller.get_server_status()
            print(f'Statut serveur: {status["status"]}')

            if status["status"] != "online":
                print('❌ ComfyUI non accessible')
                return

            # Appeler le custom node
            result = caller.call_custom_node("ExtraPathReader", {})
            print(f'✅ Custom node appelé: {result}')

            if "prompt_id" in result:
                prompt_id = result["prompt_id"]

                # Attendre
                import time
                time.sleep(2)

                # Récupérer la sortie
                output = caller.get_custom_node_output(prompt_id, "1")
                print(f'📋 Sortie du custom node: {output[:200] if output else "None"}...')

                if output:
                    # Parser le JSON
                    import json
                    try:
                        data = json.loads(output)
                        comfyui_root = data.get("comfyui_root", "N/A")
                        print(f'🎯 Racine ComfyUI détectée: {comfyui_root}')

                        # Extraire l'ID
                        if "H12" in comfyui_root:
                            print('✅ SUCCÈS: H12 détecté correctement !')
                        elif "G11" in comfyui_root:
                            print('⚠️ ATTENTION: G11 détecté (non attendu)')
                        else:
                            print(f'❓ AUTRE: {comfyui_root}')

                    except json.JSONDecodeError as e:
                        print(f'❌ Erreur parsing JSON: {e}')
                else:
                    print('❌ Aucune sortie du custom node')
            else:
                print('❌ Pas de prompt_id dans la réponse')

    except Exception as e:
        print(f'❌ Erreur: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_identification_custom_node_only()
