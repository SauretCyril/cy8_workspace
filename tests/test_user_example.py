#!/usr/bin/env python3
"""
Test spécifique pour l'exemple fourni par l'utilisateur
"""

import os
import sys
sys.path.append('../src')

from cy8_log_analyzer import cy8_log_analyzer


def test_user_example():
    """Tester avec l'exemple exact fourni par l'utilisateur"""
    print("🧪 Test avec l'exemple utilisateur spécifique")
    print("=" * 50)

    # Ligne exacte fournie par l'utilisateur
    test_line = "Adding extra search path custom_nodes H:\\comfyui\\G11_04\\custom_nodes"
    print(f"📝 Ligne à analyser: {test_line}")

    # Tester l'extraction
    analyzer = cy8_log_analyzer()
    config_id = analyzer._extract_config_id(test_line)

    print(f"🆔 ID extrait: '{config_id}'")
    print(f"✅ Attendu: 'G11_04'")

    if config_id == "G11_04":
        print("🎉 SUCCESS - L'extraction fonctionne parfaitement !")
    else:
        print("❌ FAILED - L'extraction ne fonctionne pas correctement")

    print()

    # Test avec variations possibles
    test_variations = [
        "Adding extra search path custom_nodes H:\\comfyui\\G11_04\\custom_nodes",
        "Adding extra search path custom_nodes H:/comfyui/G11_04/custom_nodes",
        "Adding extra search path custom_nodes C:\\comfyui\\Production_v2\\custom_nodes",
        "Adding extra search path custom_nodes D:/comfyui/TestEnv/custom_nodes",
    ]

    print("🔍 Test des variations:")
    for line in test_variations:
        extracted = analyzer._extract_config_id(line)
        print(f"  📄 {line}")
        print(f"    → ID: '{extracted}'")
        print()


def create_complete_test_log():
    """Créer un log complet avec l'exemple utilisateur"""
    test_content = f"""2025-09-26 10:00:01,123 - INFO - Starting ComfyUI
2025-09-26 10:00:02,456 - INFO - Total VRAM: 8192 MB
2025-09-26 10:00:03,789 - INFO - CUDA Available: True
Adding extra search path custom_nodes H:\\comfyui\\G11_04\\custom_nodes

Import times for custom nodes:
   0.1 seconds: H:\\comfyui\\G11_04\\custom_nodes\\ComfyUI-Manager
   0.2 seconds: H:\\comfyui\\G11_04\\custom_nodes\\comfyui_controlnet_aux
   0.0 seconds: H:\\comfyui\\G11_04\\custom_nodes\\sd-webui-controlnet (IMPORT FAILED)
   0.3 seconds: H:\\comfyui\\G11_04\\custom_nodes\\ComfyUI_InstantID

2025-09-26 10:00:15,123 - INFO - Server started on 127.0.0.1:8188
"""

    with open('test_user_example.log', 'w', encoding='utf-8') as f:
        f.write(test_content)

    return 'test_user_example.log'


def test_complete_analysis():
    """Test complet avec le log utilisateur"""
    print("🧪 Test d'analyse complète avec l'exemple utilisateur")
    print("=" * 55)

    # Créer le fichier de test
    log_file = create_complete_test_log()
    print(f"✅ Fichier de test créé: {log_file}")

    # Analyser le log
    analyzer = cy8_log_analyzer()
    result = analyzer.analyze_log_file(log_file)

    if result["success"]:
        print("✅ Analyse réussie !")

        # Vérifier l'ID de configuration
        config_id = result.get("config_id")
        print(f"🆔 ID de Configuration: '{config_id}'")

        if config_id == "G11_04":
            print("🎉 SUCCESS - ID correctement extrait !")
        else:
            print(f"❌ FAILED - ID incorrect, attendu 'G11_04', obtenu '{config_id}'")

        # Afficher le résumé
        summary = result["summary"]
        print(f"\n📊 Résumé:")
        print(f"  • Custom nodes OK: {summary['custom_nodes_ok']}")
        print(f"  • Custom nodes échoués: {summary['custom_nodes_failed']}")

    else:
        print(f"❌ Erreur: {result['error']}")

    # Nettoyer
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f"\n🧹 Fichier de test supprimé")


if __name__ == "__main__":
    test_user_example()
    print()
    test_complete_analysis()
