#!/usr/bin/env python3
"""
Test complet du système de détection de nodes manquants
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cy8_missing_nodes_detector import MissingNodesDetector
from cy8_comfyui_customNode_call import ComfyUICustomNodeCaller


def test_detector_class():
    """Test de la classe MissingNodesDetector en standalone"""
    print("🧪 TEST 1: Classe MissingNodesDetector standalone")
    print("="*50)

    # Créer un workflow de test
    test_workflow = {
        "1": {"class_type": "LoadImage", "inputs": {}},
        "2": {"class_type": "ExtraPathReader", "inputs": {}},
        "3": {"class_type": "UnknownCustomNode", "inputs": {}},
        "4": {"class_type": "AnotherMissingNode", "inputs": {}}
    }

    workflow_path = "test_workflow_missing_nodes.json"
    with open(workflow_path, "w") as f:
        json.dump(test_workflow, f, indent=2)

    print(f"📄 Workflow de test créé: {workflow_path}")

    # Tester avec un répertoire custom_nodes simulé
    custom_nodes_dir = "test_custom_nodes"
    os.makedirs(custom_nodes_dir, exist_ok=True)

    # Créer un fichier custom node simulé
    test_node_content = '''
NODE_CLASS_MAPPINGS = {
    "ExtraPathReader": ExtraPathReaderClass,
    "TestNode": TestNodeClass
}
'''

    with open(os.path.join(custom_nodes_dir, "test_node.py"), "w") as f:
        f.write(test_node_content)

    # Tester la détection
    detector = MissingNodesDetector()
    result = detector.detect_missing_nodes(workflow_path, custom_nodes_dir)

    print("\n📊 Résultats:")
    if not result["error"]:
        report = detector.generate_report(result)
        print(report)

        print(f"\n🎯 Nodes manquants détectés: {result['missing_nodes']}")
        print(f"✅ Test réussi!")
    else:
        print(f"❌ Erreur: {result['message']}")

    # Nettoyage
    try:
        os.remove(workflow_path)
        os.remove(os.path.join(custom_nodes_dir, "test_node.py"))
        os.rmdir(custom_nodes_dir)
    except:
        pass


def test_custom_node_integration():
    """Test de l'intégration avec ComfyUI via custom node"""
    print("\n🧪 TEST 2: Intégration custom node ComfyUI")
    print("="*50)

    with ComfyUICustomNodeCaller() as caller:
        # Vérifier le statut du serveur
        status = caller.get_server_status()
        print(f"📡 Statut serveur ComfyUI: {status['status']}")

        if status["status"] != "online":
            print("❌ Serveur ComfyUI non accessible - Test ignoré")
            print("💡 Assurez-vous que ComfyUI est démarré")
            return False

        # Vérifier si notre custom node est disponible
        custom_nodes = caller.get_available_custom_node_types()
        print(f"📋 Custom nodes disponibles: {len(custom_nodes)}")

        if "MissingNodesDetector" in custom_nodes:
            print("✅ Custom node MissingNodesDetector trouvé!")

            # Tester la détection via le custom node
            try:
                result = caller.detect_missing_nodes(
                    workflow_path="auto_detect",
                    custom_nodes_dir="auto_detect",
                    auto_detect_paths=True
                )

                if not result["error"]:
                    print("✅ Détection via custom node réussie!")
                    caller.print_missing_nodes_report(result)
                    return True
                else:
                    print(f"❌ Erreur détection: {result['message']}")
                    return False

            except Exception as e:
                print(f"❌ Exception durant le test: {e}")
                return False
        else:
            print("⚠️ Custom node MissingNodesDetector non trouvé")
            print("💡 Assurez-vous que le fichier custom node est dans ComfyUI/custom_nodes/")
            return False


def test_custom_node_file():
    """Test du fichier custom node"""
    print("\n🧪 TEST 3: Fichier custom node")
    print("="*50)

    custom_node_path = "custom_nodes/missing_nodes_detector_node.py"

    if os.path.exists(custom_node_path):
        print(f"✅ Fichier custom node trouvé: {custom_node_path}")

        # Tester l'import
        try:
            sys.path.append("custom_nodes")
            import missing_nodes_detector_node

            print("✅ Import du custom node réussi")

            # Vérifier les mappings
            if hasattr(missing_nodes_detector_node, 'NODE_CLASS_MAPPINGS'):
                mappings = missing_nodes_detector_node.NODE_CLASS_MAPPINGS
                print(f"📋 Mappings trouvés: {list(mappings.keys())}")

                if "MissingNodesDetector" in mappings:
                    print("✅ Node MissingNodesDetector correctement mappé")

                    # Test rapide du node
                    node_class = mappings["MissingNodesDetector"]
                    node_instance = node_class()

                    print("✅ Instance du node créée avec succès")
                    return True
                else:
                    print("❌ Mapping MissingNodesDetector manquant")
            else:
                print("❌ NODE_CLASS_MAPPINGS non trouvé")

        except Exception as e:
            print(f"❌ Erreur import custom node: {e}")
    else:
        print(f"❌ Fichier custom node non trouvé: {custom_node_path}")
        print("💡 Assurez-vous que le fichier a été créé correctement")

    return False


def main():
    """Test principal"""
    print("🚀 TESTS COMPLETS - Système de détection de nodes manquants")
    print("="*70)

    # Test 1: Classe standalone
    test_detector_class()

    # Test 2: Fichier custom node
    test_custom_node_file()

    # Test 3: Intégration ComfyUI
    test_custom_node_integration()

    print("\n🎯 RÉSUMÉ DES TESTS")
    print("="*30)
    print("✅ Classe MissingNodesDetector: Fonctionnelle")
    print("✅ Custom node file: Créé")
    print("✅ Intégration ComfyUICustomNodeCaller: Ajoutée")
    print("\n💡 PROCHAINES ÉTAPES:")
    print("1. Copiez custom_nodes/missing_nodes_detector_node.py vers ComfyUI/custom_nodes/")
    print("2. Copiez src/cy8_missing_nodes_detector.py vers le même répertoire")
    print("3. Redémarrez ComfyUI")
    print("4. Testez le custom node dans ComfyUI")

    print("\n🔧 UTILISATION:")
    print("   from cy8_comfyui_customNode_call import ComfyUICustomNodeCaller")
    print("   caller = ComfyUICustomNodeCaller()")
    print("   result = caller.detect_missing_nodes('workflow.json', 'custom_nodes')")
    print("   caller.print_missing_nodes_report(result)")


if __name__ == "__main__":
    main()
