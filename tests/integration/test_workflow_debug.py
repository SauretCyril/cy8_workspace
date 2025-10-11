#!/usr/bin/env python3
"""
Test de debug du workflow généré pour ExtraPathReader
"""

import sys
import os
import json

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def test_workflow_generation():
    """Tester la génération du workflow pour ExtraPathReader"""
    print("🔧 Test de génération de workflow")
    print("=" * 40)

    try:
        from cy8_comfyui_customNode_call import ComfyUICustomNodeCaller

        with ComfyUICustomNodeCaller() as caller:
            print("✅ ComfyUICustomNodeCaller initialisé")

            # Générer le workflow pour ExtraPathReader
            workflow = caller.create_custom_node_workflow(
                node_type="ExtraPathReader", node_inputs={}
            )

            print("📋 Workflow généré:")
            print(json.dumps(workflow, indent=2))

            # Vérifier si ExtraPathReader est disponible dans ComfyUI
            print("\n🔍 Vérification de la disponibilité du node...")
            nodes_info = caller.get_custom_nodes_info()

            if "ExtraPathReader" in nodes_info:
                print("✅ ExtraPathReader trouvé dans ComfyUI")
                schema = nodes_info["ExtraPathReader"]
                print(f"📝 Schema du node:")
                print(json.dumps(schema, indent=2))
            else:
                print("❌ ExtraPathReader non trouvé dans ComfyUI")
                print("💡 Nodes disponibles:")
                for node_name in list(nodes_info.keys())[
                    :10
                ]:  # Limiter à 10 pour la lisibilité
                    print(f"   - {node_name}")
                if len(nodes_info) > 10:
                    print(f"   ... et {len(nodes_info) - 10} autres")

            # Test manuel avec un workflow valide connu
            print("\n🧪 Test avec un workflow minimal valide...")
            minimal_workflow = {
                "1": {
                    "inputs": {},
                    "class_type": "ExtraPathReader",
                    "_meta": {"title": "Extra Path Reader"},
                }
            }

            print("📋 Workflow minimal:")
            print(json.dumps(minimal_workflow, indent=2))

            # Essayer de l'envoyer manuellement
            import requests

            payload = {"prompt": minimal_workflow}

            print("\n📤 Test d'envoi du workflow minimal...")
            try:
                response = requests.post(
                    "http://127.0.0.1:8188/prompt", json=payload, timeout=10
                )
                print(f"📨 Status: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Succès: {json.dumps(result, indent=2)}")
                else:
                    print(f"❌ Erreur {response.status_code}: {response.text}")

            except Exception as e:
                print(f"❌ Erreur lors de l'envoi: {e}")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_workflow_generation()
