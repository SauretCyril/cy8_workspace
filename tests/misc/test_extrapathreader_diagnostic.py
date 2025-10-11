#!/usr/bin/env python3
"""
Test de diagnostic pour le custom node ExtraPathReader
"""

import os
import sys
import json
import requests
from urllib.parse import urljoin

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def test_comfyui_connection(server_url="http://127.0.0.1:8188"):
    """Tester la connexion de base à ComfyUI"""
    try:
        print(f"🔌 Test de connexion à {server_url}...")
        response = requests.get(f"{server_url}/system_stats", timeout=5)
        if response.status_code == 200:
            print("✅ ComfyUI accessible")
            return True
        else:
            print(f"❌ ComfyUI non accessible - Statut: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False


def test_object_info(server_url="http://127.0.0.1:8188"):
    """Récupérer les informations sur les nœuds disponibles"""
    try:
        print("📋 Récupération des informations sur les nœuds...")
        response = requests.get(f"{server_url}/object_info", timeout=10)
        if response.status_code == 200:
            object_info = response.json()

            # Vérifier si ExtraPathReader est disponible
            if "ExtraPathReader" in object_info:
                print("✅ ExtraPathReader trouvé dans object_info")
                node_info = object_info["ExtraPathReader"]
                print(f"📋 Info ExtraPathReader: {json.dumps(node_info, indent=2)}")
                return True, node_info
            else:
                print("❌ ExtraPathReader NON trouvé dans object_info")
                print("🔍 Nœuds disponibles contenant 'Extra':")
                for node_name in object_info.keys():
                    if "Extra" in node_name or "Path" in node_name:
                        print(f"   - {node_name}")
                return False, None
        else:
            print(f"❌ Erreur récupération object_info: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Exception object_info: {e}")
        return False, None


def test_extra_path_reader_workflow(server_url="http://127.0.0.1:8188"):
    """Tester ExtraPathReader avec différents workflows"""

    # Test 1: Workflow minimal
    print("\n🧪 Test 1: Workflow minimal")
    workflow1 = {"1": {"class_type": "ExtraPathReader", "inputs": {}}}

    result1 = send_workflow(server_url, workflow1, "Test 1")

    # Test 2: Workflow avec client_id
    print("\n🧪 Test 2: Workflow avec client_id")
    result2 = send_workflow(server_url, workflow1, "Test 2", client_id="test_client")

    # Test 3: Workflow avec extra_data vide
    print("\n🧪 Test 3: Workflow avec extra_data")
    result3 = send_workflow(server_url, workflow1, "Test 3", extra_data={})

    return result1 or result2 or result3


def send_workflow(server_url, workflow, test_name, client_id=None, extra_data=None):
    """Envoyer un workflow à ComfyUI et analyser la réponse"""
    try:
        # Préparer le payload
        payload = {"prompt": workflow}

        if client_id:
            payload["client_id"] = client_id

        if extra_data is not None:
            payload["extra_data"] = extra_data

        print(f"📤 {test_name} - Envoi du payload:")
        print(json.dumps(payload, indent=2))

        # Envoyer la requête
        url = urljoin(server_url, "/prompt")
        response = requests.post(url, json=payload, timeout=30)

        print(f"📡 {test_name} - Statut: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ {test_name} - Succès!")
            print(f"📋 Réponse: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ {test_name} - Échec HTTP {response.status_code}")
            try:
                error_details = response.json()
                print(f"❌ Détails erreur: {json.dumps(error_details, indent=2)}")
            except:
                print(f"❌ Réponse brute: {response.text}")
            return False

    except Exception as e:
        print(f"❌ {test_name} - Exception: {e}")
        return False


def test_custom_node_caller():
    """Tester avec notre classe CustomNodeCaller"""
    try:
        print("\n🧪 Test avec CustomNodeCaller...")
        from cy8_comfyui_customNode_call import CustomNodeCaller

        caller = CustomNodeCaller()

        # Test de connexion
        if not caller.is_server_online():
            print("❌ Serveur non accessible via CustomNodeCaller")
            return False

        print("✅ Serveur accessible via CustomNodeCaller")

        # Test direct
        print("🔍 Test direct ExtraPathReader...")
        result = caller.test_extra_path_reader_direct()

        if result.get("error", True):
            print("❌ Test direct échoué")
            print(f"Détails: {result}")
        else:
            print("✅ Test direct réussi!")
            print(f"Résultat: {result}")

        return not result.get("error", True)

    except Exception as e:
        print(f"❌ Erreur CustomNodeCaller: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Fonction principale de diagnostic"""
    print("🔍 DIAGNOSTIC EXTRAPATHREADER")
    print("=" * 50)

    server_url = "http://127.0.0.1:8188"

    # Test 1: Connexion de base
    if not test_comfyui_connection(server_url):
        print("\n❌ ARRÊT: ComfyUI non accessible")
        return False

    # Test 2: Vérification object_info
    found, node_info = test_object_info(server_url)
    if not found:
        print("\n❌ ARRÊT: ExtraPathReader non trouvé dans ComfyUI")
        print("💡 Suggestions:")
        print("   1. Vérifier que le custom node est bien installé")
        print("   2. Redémarrer ComfyUI")
        print("   3. Vérifier les logs de ComfyUI")
        return False

    # Test 3: Tests de workflow
    if not test_extra_path_reader_workflow(server_url):
        print("\n❌ Tous les tests de workflow ont échoué")

    # Test 4: Test avec notre classe
    test_custom_node_caller()

    print("\n🎯 DIAGNOSTIC TERMINÉ")
    return True


if __name__ == "__main__":
    main()
