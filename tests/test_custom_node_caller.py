#!/usr/bin/env python3
"""
Test de la classe ComfyUICustomNodeCaller
"""

import sys
import os
sys.path.append('../src')

from cy8_comfyui_customNode_call import ComfyUICustomNodeCaller


def test_comfyui_custom_node_caller():
    """Tester la classe ComfyUICustomNodeCaller"""
    print("🧪 Test de la classe ComfyUICustomNodeCaller")
    print("=" * 50)

    # Test de l'initialisation
    print("1. Test d'initialisation...")
    caller = ComfyUICustomNodeCaller()
    print(f"   ✅ URL du serveur: {caller.server_url}")
    print(f"   ✅ API Key: {'Configurée' if caller.api_key else 'Non configurée'}")
    print()

    # Test du statut du serveur
    print("2. Test du statut du serveur...")
    status = caller.get_server_status()
    print(f"   📡 Statut: {status['status']}")

    if status['status'] == 'online':
        print(f"   ⏱️ Temps de réponse: {status['response_time']:.3f}s")
        print("   ✅ Serveur ComfyUI accessible")

        # Test des custom nodes
        print("\n3. Test de récupération des custom nodes...")
        try:
            custom_nodes = caller.get_available_custom_node_types()
            print(f"   📦 Nombre de custom nodes détectés: {len(custom_nodes)}")

            if custom_nodes:
                print("   🔍 Premiers custom nodes détectés:")
                for i, node in enumerate(custom_nodes[:5], 1):
                    print(f"      {i}. {node}")

                if len(custom_nodes) > 5:
                    print(f"      ... et {len(custom_nodes) - 5} autres")

                # Test du schéma d'un custom node
                print(f"\n4. Test du schéma pour '{custom_nodes[0]}'...")
                schema = caller.get_custom_node_schema(custom_nodes[0])
                if schema:
                    print("   ✅ Schéma récupéré avec succès")
                    if 'input' in schema:
                        inputs = schema.get('input', {})
                        required = inputs.get('required', {})
                        optional = inputs.get('optional', {})
                        print(f"   📋 Inputs requis: {len(required)}")
                        print(f"   📋 Inputs optionnels: {len(optional)}")
                else:
                    print("   ⚠️ Aucun schéma trouvé")

        except Exception as e:
            print(f"   ❌ Erreur lors de la récupération des custom nodes: {e}")

    else:
        print(f"   ❌ Serveur inaccessible: {status.get('error', 'Erreur inconnue')}")
        print("   💡 Assurez-vous que ComfyUI est démarré sur http://127.0.0.1:8188")

    # Test de création de workflow
    print("\n5. Test de création de workflow...")
    workflow = caller.create_custom_node_workflow(
        node_type="ExtraPathReader",
        node_inputs={}
    )
    print("   ✅ Workflow créé:")
    print(f"   📄 Structure: {workflow}")

    # Fermer la connexion
    caller.close()
    print("\n✅ Tests terminés")


def test_context_manager():
    """Tester l'utilisation avec context manager"""
    print("\n🧪 Test du context manager")
    print("=" * 30)

    try:
        with ComfyUICustomNodeCaller() as caller:
            status = caller.get_server_status()
            print(f"✅ Context manager fonctionne - Statut: {status['status']}")
    except Exception as e:
        print(f"❌ Erreur avec context manager: {e}")


if __name__ == "__main__":
    test_comfyui_custom_node_caller()
    test_context_manager()

    print("\n" + "="*60)
    print("💡 Pour utiliser cette classe dans votre code:")
    print()
    print("from cy8_comfyui_customNode_call import ComfyUICustomNodeCaller")
    print()
    print("# Utilisation basique")
    print("caller = ComfyUICustomNodeCaller()")
    print("custom_nodes = caller.get_available_custom_node_types()")
    print()
    print("# Utilisation avec context manager (recommandé)")
    print("with ComfyUICustomNodeCaller() as caller:")
    print("    result = caller.call_custom_node('NodeType', {'input': 'value'})")
    print("="*60)
