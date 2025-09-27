#!/usr/bin/env python3
"""
Test de l'analyseur de logs avec un exemple réaliste de log ComfyUI
"""

import os
import sys
sys.path.append('../src')

from cy8_log_analyzer import cy8_log_analyzer


def create_realistic_test_log():
    """Créer un fichier de log de test réaliste"""
    test_content = """2025-09-26 10:00:01,123 - INFO - Starting ComfyUI
2025-09-26 10:00:02,456 - INFO - Total VRAM: 8192 MB
2025-09-26 10:00:03,789 - INFO - CUDA Available: True
2025-09-26 10:00:04,012 - INFO - Torch version: 2.0.1

Import times for custom nodes:
   0.1 seconds: E:\\ComfyUI\\custom_nodes\\ComfyUI-Manager
   0.2 seconds: E:\\ComfyUI\\custom_nodes\\comfyui_controlnet_aux
   0.0 seconds: E:\\ComfyUI\\custom_nodes\\sd-webui-controlnet (IMPORT FAILED)
   0.3 seconds: E:\\ComfyUI\\custom_nodes\\ComfyUI_InstantID
   0.0 seconds: E:\\ComfyUI\\custom_nodes\\broken_extension (IMPORT FAILED)
   0.5 seconds: E:\\ComfyUI\\custom_nodes\\ComfyUI-AnimateDiff-Evolved

2025-09-26 10:00:15,123 - INFO - Server started on 127.0.0.1:8188
2025-09-26 10:00:16,456 - INFO - Loading model: checkpoints/sd_xl_base_1.0.safetensors
2025-09-26 10:00:17,789 - WARNING - Deprecated function used in workflow
2025-09-26 10:00:18,012 - ERROR - CUDA out of memory error occurred
2025-09-26 10:00:19,345 - INFO - Workflow execution completed
"""

    with open('test_realistic_comfyui.log', 'w', encoding='utf-8') as f:
        f.write(test_content)

    return 'test_realistic_comfyui.log'


def test_realistic_log_analysis():
    """Tester l'analyse avec un log réaliste"""
    print("🧪 Test de l'analyseur avec un log ComfyUI réaliste")
    print("=" * 55)

    # Créer le fichier de test
    log_file = create_realistic_test_log()
    print(f"✅ Fichier de test créé: {log_file}")

    # Analyser le log
    analyzer = cy8_log_analyzer()
    result = analyzer.analyze_log_file(log_file)

    if result["success"]:
        print("✅ Analyse réussie !")
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

        # Afficher les détails
        entries = result["entries"]
        print(f"📋 Détails des entrées ({len(entries)} éléments):")

        custom_nodes_ok = [e for e in entries if e["type"] == "OK" and e["category"] == "Custom Node"]
        custom_nodes_failed = [e for e in entries if e["type"] == "ERREUR" and e["category"] == "Custom Node"]

        print("\n🟢 Custom Nodes chargés avec succès:")
        for i, entry in enumerate(custom_nodes_ok, 1):
            print(f"   {i}. ✅ {entry['element']} (ligne {entry['line']})")

        print("\n🔴 Custom Nodes en échec:")
        for i, entry in enumerate(custom_nodes_failed, 1):
            print(f"   {i}. ❌ {entry['element']} (ligne {entry['line']}) - {entry['message']}")

        # Autres entrées
        other_entries = [e for e in entries if not (e["type"] == "OK" or e["type"] == "ERREUR") or e["category"] != "Custom Node"]
        if other_entries:
            print(f"\n📝 Autres entrées ({len(other_entries)}):")
            for i, entry in enumerate(other_entries[:5], 1):  # Limiter l'affichage
                icon = "🔴" if entry["type"] == "ERREUR" else "⚠️" if entry["type"] == "ATTENTION" else "ℹ️"
                print(f"   {i}. {icon} {entry['type']} | {entry['element']} | Ligne {entry['line']}")
                print(f"      {entry['message'][:80]}{'...' if len(entry['message']) > 80 else ''}")

            if len(other_entries) > 5:
                print(f"      ... et {len(other_entries) - 5} autres éléments")

    else:
        print(f"❌ Erreur: {result['error']}")

    # Nettoyer
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f"\n🧹 Fichier de test supprimé")

    print(f"\n{analyzer.get_summary_text()}")


if __name__ == "__main__":
    test_realistic_log_analysis()
