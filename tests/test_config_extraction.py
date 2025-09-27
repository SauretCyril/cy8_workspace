#!/usr/bin/env python3
"""
Test de l'extraction de l'ID de configuration ComfyUI
"""

import os
import sys
sys.path.append('../src')

from cy8_log_analyzer import cy8_log_analyzer


def create_config_test_log():
    """Créer un fichier de log de test avec l'ID de configuration"""
    test_content = """2025-09-26 10:00:01,123 - INFO - Starting ComfyUI
2025-09-26 10:00:02,456 - INFO - Total VRAM: 8192 MB
2025-09-26 10:00:03,789 - INFO - CUDA Available: True
2025-09-26 10:00:04,012 - Adding extra search path E:/Comfyui_G11/ComfyUI/custom_nodes
2025-09-26 10:00:05,234 - Adding extra search path E:/ComfyUI/MyConfig/ComfyUI/custom_nodes

Import times for custom nodes:
   0.1 seconds: E:\\ComfyUI\\custom_nodes\\ComfyUI-Manager
   0.2 seconds: E:\\ComfyUI\\custom_nodes\\comfyui_controlnet_aux
   0.0 seconds: E:\\ComfyUI\\custom_nodes\\sd-webui-controlnet (IMPORT FAILED)
   0.3 seconds: E:\\ComfyUI\\custom_nodes\\ComfyUI_InstantID

2025-09-26 10:00:15,123 - INFO - Server started on 127.0.0.1:8188
"""

    with open('test_config_comfyui.log', 'w', encoding='utf-8') as f:
        f.write(test_content)

    return 'test_config_comfyui.log'


def test_config_id_extraction():
    """Tester l'extraction de l'ID de configuration"""
    print("🧪 Test de l'extraction de l'ID de configuration ComfyUI")
    print("=" * 58)

    # Créer le fichier de test
    log_file = create_config_test_log()
    print(f"✅ Fichier de test créé: {log_file}")

    # Analyser le log
    analyzer = cy8_log_analyzer()
    result = analyzer.analyze_log_file(log_file)

    if result["success"]:
        print("✅ Analyse réussie !")
        print()

        # Afficher l'ID de configuration
        config_id = result.get("config_id")
        if config_id:
            print(f"🆔 ID de Configuration détecté: '{config_id}'")
            print("✅ Extraction de l'ID réussie !")
        else:
            print("❌ Aucun ID de configuration détecté")

        print()

        # Afficher le résumé
        summary = result["summary"]
        print("📊 Résumé:")
        print(f"  • Custom nodes OK: {summary['custom_nodes_ok']}")
        print(f"  • Custom nodes échoués: {summary['custom_nodes_failed']}")
        print(f"  • Erreurs: {summary['errors']}")
        print(f"  • Warnings: {summary['warnings']}")
        print(f"  • Informations: {summary['info_messages']}")

        print()

        # Test de patterns spécifiques
        test_patterns = [
            "E:/Comfyui_G11/ComfyUI/custom_nodes",
            "E:/ComfyUI/MyConfig/ComfyUI/custom_nodes",
            "C:/ComfyUI/Production/ComfyUI/custom_nodes",
            "D:/AI/comfyui/TestEnv/ComfyUI/custom_nodes"
        ]

        print("🔍 Test des patterns d'extraction:")
        for pattern in test_patterns:
            test_line = f"2025-09-26 10:00:05,234 - Adding extra search path {pattern}"
            extracted_id = analyzer._extract_config_id(test_line)
            expected_parts = pattern.split('/')
            expected_id = None

            # Trouver l'index de 'ComfyUI' et prendre l'élément précédent
            for i, part in enumerate(expected_parts):
                if part.lower() == 'comfyui' and i > 0:
                    expected_id = expected_parts[i-1]
                    break

            status = "✅" if extracted_id == expected_id else "❌"
            print(f"  {status} '{pattern}' → ID: '{extracted_id}' (attendu: '{expected_id}')")

    else:
        print(f"❌ Erreur: {result['error']}")

    # Nettoyer
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f"\n🧹 Fichier de test supprimé")


if __name__ == "__main__":
    test_config_id_extraction()
