#!/usr/bin/env python3
"""
Test rapide du ComfyUICustomNodeCaller pour diagnostiquer l'erreur 400
"""

import sys
import os

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def test_custom_node_caller():
    """Test rapide de la classe ComfyUICustomNodeCaller"""
    print("🔧 Test de ComfyUICustomNodeCaller")
    print("=" * 40)

    try:
        from cy8_comfyui_customNode_call import ComfyUICustomNodeCaller

        with ComfyUICustomNodeCaller() as caller:
            print("✅ ComfyUICustomNodeCaller initialisé")

            # Test du statut du serveur
            status = caller.get_server_status()
            print(f"📡 Statut du serveur: {status}")

            if status['status'] == 'online':
                print("🟢 Serveur ComfyUI en ligne")

                # Test d'appel du custom node
                try:
                    print("🚀 Tentative d'appel du custom node ExtraPathReader...")
                    result = caller.call_custom_node(
                        node_type="ExtraPathReader",
                        inputs={}
                    )
                    print(f"✅ Appel du custom node réussi: {result}")

                except Exception as e:
                    print(f"❌ Erreur lors de l'appel du custom node: {e}")
                    print(f"🔍 Type d'erreur: {type(e).__name__}")
                    import traceback
                    traceback.print_exc()

            else:
                print(f"🔴 Serveur ComfyUI hors ligne: {status.get('error', 'Raison inconnue')}")

    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_custom_node_caller()
