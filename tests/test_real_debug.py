#!/usr/bin/env python3
"""
Test avec un vrai log ComfyUI pour voir si l'ID est détecté
"""

import os
import sys
sys.path.append('../src')

from cy8_log_analyzer import cy8_log_analyzer


def create_real_comfyui_log():
    """Créer un log qui ressemble vraiment à un log ComfyUI"""
    content = """2025-09-26 10:00:01,123 - Starting ComfyUI
2025-09-26 10:00:02,456 - Total VRAM: 8192 MB
2025-09-26 10:00:03,789 - CUDA Available: True
Adding extra search path custom_nodes H:\\comfyui\\G11_04\\custom_nodes

Import times for custom nodes:
   0.1 seconds: H:\\comfyui\\G11_04\\custom_nodes\\ComfyUI-Manager
   0.2 seconds: H:\\comfyui\\G11_04\\custom_nodes\\comfyui_controlnet_aux
   0.0 seconds: H:\\comfyui\\G11_04\\custom_nodes\\sd-webui-controlnet (IMPORT FAILED)
   0.3 seconds: H:\\comfyui\\G11_04\\custom_nodes\\ComfyUI_InstantID

2025-09-26 10:00:15,123 - Server started on 127.0.0.1:8188
2025-09-26 10:00:16,456 - Loading model: checkpoints/sd_xl_base_1.0.safetensors"""

    with open('real_comfyui_test.log', 'w', encoding='utf-8') as f:
        f.write(content)

    return 'real_comfyui_test.log'


def test_with_debug():
    """Test avec debug activé"""
    print("🔍 TEST avec log ComfyUI réaliste")
    print("=" * 40)

    log_file = create_real_comfyui_log()
    print(f"✅ Fichier créé: {log_file}")

    # Lire le contenu pour vérification
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print("📋 Contenu du log:")
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if line.strip():
            print(f"  {i:2d}: {line}")
    print()

    # Analyser le log
    analyzer = cy8_log_analyzer()

    print("🔍 Analyse ligne par ligne:")
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue

        if "Adding extra search path" in line and "custom_nodes" in line:
            print(f"  Ligne {i}: TROUVÉE - {line}")
            config_id = analyzer._extract_config_id(line)
            print(f"    → ID extrait: '{config_id}'")

    print()

    # Analyse complète
    result = analyzer.analyze_log_file(log_file)

    if result["success"]:
        config_id = result.get("config_id")
        print(f"🆔 ID final dans result: '{config_id}'")

        if config_id == "G11_04":
            print("✅ SUCCESS - ID correctement trouvé!")
        else:
            print(f"❌ PROBLEM - ID attendu 'G11_04', trouvé '{config_id}'")

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
        print(f"\n🧹 Fichier supprimé")


if __name__ == "__main__":
    test_with_debug()
